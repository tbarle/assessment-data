# Embedding Strategy — Knowledge Base per RAG

## Modello scelto

**`text-embedding-3-small`** (OpenAI) — 1536 dimensioni

| Criterio | Motivazione |
|---|---|
| Qualità semantica | Ottima comprensione dell'italiano e del gergo di settore (CAWI, CATI, panel, ecc.) |
| Dimensioni | 1536 dim è il default del modello; si può ridurre a 256/512 con il parametro `dimensions` senza degradazione severa |
| Costo | ~0.02$/M token — adeguato per il volume (~111 chunk) |
| Semplicità | Nessuna infrastruttura locale, API stateless |

**Alternativa valutata**: `BAAI/bge-m3` (sentence-transformers, 1024 dim). Stato dell'arte per embedding multilingua locali, con supporto nativo dell'italiano e buona comprensione del gergo tecnico di settore. Da preferire se la privacy dei dati impone che il testo non lasci l'infrastruttura aziendale — la qualità semantica è superiore a modelli locali più datati (es. MiniLM) e comparabile a `text-embedding-3-small` sul dominio specifico.

---

## Strategia di chunking

Il dataset contiene tre sorgenti con struttura e granularità molto diverse — è stata scelta una strategia **per-sorgente** invece di un chunking a finestra fissa.

### FAQ (24 chunk)

**Unità**: 1 chunk = 1 coppia Q+A

```
Q: Cosa significa CAWI?
A: CAWI sta per Computer Assisted Web Interviewing...
```

**Motivazione**: ogni Q+A è già un'unità semantica coesa e autocontenuta. Spezzarla introdurrebbe chunk orfani (domanda senza risposta o viceversa) che degradano il retrieval. La lunghezza media (~80 token) è ben dentro il limite del modello.

### Progetti (50 chunk)

**Unità**: 1 chunk = 1 progetto, rappresentato come prosa denormalizzata

```
Progetto PRJ-001: Megaditta Consumer Sentiment Q4
Cliente: Megaditta SpA | Workspace: WS-001
Topic: Brand Awareness | Metodologia: CAWI
Paese: IT | Campione: 1500 rispondenti | Budget: €15.000
Periodo: 2024-01-15 → 2024-02-28
Stato: Completed
```

**Motivazione**: I dati strutturati vengono "denormalizzati" in testo leggibile perché gli embeddings catturano meglio la semantica su prosa naturale che su JSON o colonne separate. Unire client, metodologia e workspace nello stesso chunk permette di rispondere a query trasversali ("progetti CAWI di Megaditta SpA completati in Q1") con un singolo vettore.

### Interazioni (37 chunk)

**Unità**: 1 chunk = 1 caso di supporto completo (problema + risoluzione)

```
Interazione INT-20240115-001 — Technical Support via Email
Progetto: PRJ-001 | Workspace: WS-001
Data: 2024-01-15T09:23:45+00:00
Problema: Candidato non riesce ad accedere al sondaggio, riceve errore 404
Risoluzione: Reset password e invio nuovo link. Issue risolta.
Esito: Risolto in 2.5h | Soddisfazione: 5/5
```

**Motivazione**: Tenere problema e risoluzione nello stesso chunk è fondamentale per il caso d'uso dell'agente AI di supporto: quando un panelista presenta un problema simile, il retrieval porta direttamente anche la soluzione già adottata.

---

## Struttura dei metadata

Ogni record JSONL ha un campo `metadata` pensato per **pre-filtering** sul vector store (es. filtrare per workspace prima della ricerca vettoriale).

| Campo | Sorgenti | Uso |
|---|---|---|
| `source` | tutte | routing della query alla sorgente corretta |
| `workspace_id` | projects, interactions | isolamento multi-tenant |
| `project_id` | projects, interactions | join con altri dati |
| `category` / `category_id` | faq | filtering per dominio tematico |
| `status` | projects | escludere progetti cancellati |
| `country_code` | projects | filtering geografico |
| `methodology_code` | projects | filtering metodologico |
| `resolved` | interactions | separare casi risolti/aperti |
| `issue_type` / `channel` | interactions | routing per tipo di problema |
| `language` | faq | futuro supporto multilingua |
| `created_at` | tutte | filtering temporale / decay |

---

## Multi-tenancy

Il campo `workspace_id` nei metadata è la chiave per garantire l'isolamento tra tenant in un contesto RAG:

1. **Pre-filter al retrieval**: ogni query viene eseguita con un filtro `workspace_id = <tenant>` prima della ricerca vettoriale. Questo garantisce che i risultati di WS-001 non vengano mai restituiti a WS-002, indipendentemente dalla similarità semantica.
2. **Zero leakage by design**: il filtro è applicato a livello di vector store (es. Pinecone namespace, Qdrant filter, pgvector WHERE), non a livello applicativo — non dipende da logica nel prompt.
3. **FAQ condivise**: le FAQ non hanno `workspace_id` (sono conoscenza comune di dominio) e vengono incluse in tutte le query senza filtro di workspace.

Schema di query tipico:
```python
results = vector_store.query(
    vector=query_embedding,
    filter={"$or": [
        {"workspace_id": {"$eq": current_workspace}},
        {"source": {"$eq": "faq"}},  # FAQ sono cross-tenant
    ]},
    top_k=5,
)
```

---

## Output

| File | Formato | Dimensioni attese |
|---|---|---|
| `knowledge_base.jsonl` | JSONL (1 record per riga) | 111 record, ~2.5 MB |

Struttura di ogni record:
```json
{
  "id": "faq-001",
  "content": "Q: ...\nA: ...",
  "embedding": [0.023, -0.041, ...],
  "metadata": {
    "source": "faq",
    "category": "Metodologie Di Ricerca",
    "language": "it",
    "created_at": "1975-03-01T00:00:00"
  }
}
```

---

## Utilizzo

```bash
pip install openai
OPENAI_API_KEY=sk-... python prepare_knowledge_base.py
```
