# Come eseguire la pipeline

Documentazione per eseguire la pipeline ETL e la generazione della Knowledge Base.

---

## Struttura

```
expected_output/
├── task1/
│   ├── schema.sql              # DDL dello schema normalizzato
│   ├── schema.dbml             # Schema in formato DBML (leggibile su dbdiagram.io)
│   ├── schema.png              # Diagramma ER
│   └── DESGIN_CHOICES.md       # Motivazioni delle scelte progettuali
├── task2/
│   ├── etl_pipeline.py         # Pipeline ETL
│   ├── data_quality_report.md  # Report anomalie e statistiche
│   └── cleaned_data/           # Output dati puliti (CSV + JSON)
│       ├── interactions.*
│       ├── projects.*
│       ├── panelists.*
│       ├── agents.*
│       ├── clients.*
│       ├── methodologies.*
│       ├── workspaces.*
│       ├── faq.*
│       └── faq_categories.*
└── task3/
    ├── prepare_knowledge_base.py   # Script generazione embeddings
    ├── knowledge_base.jsonl        # Output Knowledge Base (generato a runtime)
    └── EMBEDDING_STRATEGY.md       # Strategia chunking, modello, metadata
```

---

## Prerequisiti

| Tool | Versione minima | Note |
|---|---|---|
| Python | 3.11 | Richiesto per il supporto corretto di `%z` nel parsing dei datetime |
| pip | qualsiasi | Solo per esecuzione locale |
| Docker | 20+ | Solo per esecuzione containerizzata |
| OpenAI API key | — | Necessaria per il Task 3 |

---

## Esecuzione con Docker (pipeline completa)

Esegue in sequenza ETL → generazione embeddings in un ambiente isolato e riproducibile.

**1. Build dell'immagine** (dalla root del progetto):

```bash
docker build -t etl-pipeline .
```

**2. Esecuzione con output montato sul filesystem locale:**

```bash
docker run \
  --env-file .env \
  -v $(pwd)/output/task2:/app/expected_output/task2/cleaned_data \
  -v $(pwd)/output/task3:/app/expected_output/task3 \
  etl-pipeline
```

Il flag `--env-file .env` inietta l'`OPENAI_API_KEY` dal file `.env` nella root del progetto.
I file prodotti saranno disponibili in `./output/` una volta terminata l'esecuzione.

---

## Esecuzione locale — singoli step

### Installazione dipendenze

```bash
pip install -r requirements.txt
```

### Task 2 — ETL Pipeline

Legge i dati grezzi da `data/` e scrive i dati puliti in `expected_output/task2/cleaned_data/`.

```bash
python expected_output/task2/etl_pipeline.py
```

Output prodotto:
- `cleaned_data/*.json` e `cleaned_data/*.csv` — dati puliti e normalizzati
- `data_quality_report.md` — report anomalie (aggiornato ad ogni esecuzione)

> La pipeline è idempotente: può essere rieseguita più volte senza effetti collaterali.

### Task 3 — Knowledge Base

Legge i dati puliti da `task2/cleaned_data/`, genera gli embeddings e scrive `knowledge_base.jsonl`.

> **Dipende dal Task 2**: eseguire prima `etl_pipeline.py`.

```bash
python expected_output/task3/prepare_knowledge_base.py
```

L'API key viene letta dalla variabile d'ambiente `OPENAI_API_KEY` oppure, se assente, dal file `.env` nella root del progetto.

Output prodotto:
- `task3/knowledge_base.jsonl` — 111 record in formato JSONL, ognuno con `id`, `content`, `embedding` (1536 dim) e `metadata`

### Pipeline completa (senza Docker)

```bash
python expected_output/task2/etl_pipeline.py && \
python expected_output/task3/prepare_knowledge_base.py
```

---

## Variabili d'ambiente

| Variabile | Obbligatoria | Descrizione |
|---|---|---|
| `OPENAI_API_KEY` | Sì (solo Task 3) | API key per generare gli embeddings con `text-embedding-3-small` |

---

## Approfondimenti

- **Scelte ETL**: [task2/data_quality_report.md](task2/data_quality_report.md)
- **Strategia embedding e chunking**: [task3/EMBEDDING_STRATEGY.md](task3/EMBEDDING_STRATEGY.md)
- **Schema DB e motivazioni**: [task1/DESGIN_CHOICES.md](task1/DESGIN_CHOICES.md)
