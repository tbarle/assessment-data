# AI Engineer Assessment

Benvenuto! Questo assessment è progettato per valutare le tue competenze in:
- Normalizzazione e design di database
- Pipeline ETL e data transformation
- Preparazione dati per sistemi RAG/Knowledge Base
- Integrazione con agenti AI

## Scenario

Lavori per la **Megaditta (ItalPetrolCemenTermoTessilFarmoMetalChimica)**, una piattaforma di ricerche di mercato. Hai ricevuto dati grezzi da tre fonti diverse che devono essere normalizzati e preparati per alimentare un agente AI che risponde a domande su:
- Progetti di ricerca attivi
- Risultati di sondaggi
- Interazioni con i panelisti

## Struttura Repository
```
├── data/                          # Dataset grezzi (NON MODIFICARE)
│   ├── projects_raw.csv          # Progetti di ricerca
│   ├── panelist_interactions.json # Interazioni customer support
│   └── research_faq.txt          # FAQ metodologie di ricerca
├── expected_output/               # Metti qui i tuoi output
├── instructions/
│   └── ASSIGNMENT.md             # Istruzioni
```

## Come procedere

1. Leggi attentamente `ASSIGNMENT.md`
2. Analizza i dati in `data/`
3. Completa i task richiesti
4. Salva i tuoi output in `expected_output/`
5. Preparati per una breve presentazione delle tue scelte

## Regole

- **Linguaggio**: Libera scelta
- **Librerie**: Libera scelta
- **Embeddings**: Scegli il modello che preferisci (OpenAI, open-source, etc.)
- **Documentazione**: Spiega le tue scelte tecniche

## Consegna

Crea un fork di questa repo e condividi il link quando hai completato l'assessment.

Buon lavoro! 🚀