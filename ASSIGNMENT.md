# Assignment

## Obiettivo

Creare una Knowledge Base ottimizzata per un agente AI che supporta il team della Megaditta nel rispondere a domande su progetti, panelisti e metodologie di ricerca.

## Task

### Task 1: Database Design & Normalizzazione (30%)

Progetta uno schema di database normalizzato (almeno 3NF) che:

1. Elimini ridondanze e anomalie
2. Gestisca correttamente le relazioni tra entità
3. Sia ottimizzato per query frequenti dell'agente AI

**Deliverable**: 
- File `schema.sql` o `schema_diagram.png/pdf`
- Breve documento `DESIGN_CHOICES.md` che spiega le tue decisioni

### Task 2: Pipeline ETL (40%)

Implementa una pipeline di estrazione, trasformazione e caricamento che:

1. Pulisca e normalizzi i dati grezzi
2. Gestisca duplicati, inconsistenze e dati mancanti
3. Anonimizzi eventuali dati sensibili (GDPR compliance)
4. Validi la qualità dei dati processati

**Deliverable**:
- Script (es. `etl_pipeline.py`)
- Dati puliti in formato strutturato (CSV, JSON, Parquet, o database SQLite)
- File `data_quality_report.md` con statistiche e issue trovati

### Task 3: Knowledge Base per RAG (30%)

Prepara i dati per retrieval semantico:

1. Genera embeddings per i contenuti testuali
2. Scegli strategia di chunking appropriata
3. Crea metadata utili per filtering/routing
4. Prepara output in formato ottimale per vector database

**Deliverable**:
- Script (es.`prepare_knowledge_base.py`)
- Output in formato JSONL con struttura:
```json
  {
    "id": "unique_id",
    "content": "text chunk",
    "embedding": [0.1, 0.2, ...],
    "metadata": {
      "source": "projects|interactions|faq",
      "category": "...",
      "created_at": "ISO timestamp",
      ...
    }
  }
```
- Documento `EMBEDDING_STRATEGY.md` che spiega le tue scelte

## Bonus (Opzionale)

- Implementa un semplice retrieval test
- Aggiungi monitoring/logging alla pipeline
- Aggiungi unit tests

## Note Importanti

⚠️ **I dati contengono inconsistenze intenzionali** - parte dell'assessment è identificarle e gestirle correttamente.

## Domande?

Se qualcosa non è chiaro, fai assunzioni ragionevoli e documentale nel README.