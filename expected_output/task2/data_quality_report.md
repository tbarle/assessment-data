# Report Qualità dei Dati

_Generato il: 2026-06-09 23:15:52_

---

## Statistiche di Riepilogo

| Metrica | Valore |
|---------|--------|
| `faq.categories` | 11 |
| `faq.parsed` | 24 |
| `interactions.cleaned` | 37 |
| `interactions.format_normalised` | 36 |
| `interactions.multiple_emails_for_panelist` | 2 |
| `interactions.out_of_range` | 1 |
| `interactions.raw` | 37 |
| `interactions.type_coerced` | 23 |
| `interactions.unique_agents` | 3 |
| `interactions.unique_panelists` | 19 |
| `projects.cleaned` | 50 |
| `projects.duplicate` | 3 |
| `projects.end_before_start` | 2 |
| `projects.missing` | 1 |
| `projects.negative_value` | 1 |
| `projects.raw` | 54 |
| `projects.unique_clients` | 50 |
| `projects.unique_methodologies` | 7 |

---

## Log delle Anomalie

| Sorgente | ID Record | Campo | Anomalia | Valore Originale | Risoluzione |
|----------|-----------|-------|----------|------------------|-------------|
| interactions | `INT-20240115-001` | `interaction_date` | format_normalised | `2024-01-15T09:23:45` | 2024-01-15T09:23:45+00:00 |
| interactions | `INT-20240118-002` | `interaction_date` | format_normalised | `18/01/2024 14:30:00` | 2024-01-18T14:30:00+00:00 |
| interactions | `INT-20240120-003` | `interaction_date` | format_normalised | `2024-01-20T16:45:12` | 2024-01-20T16:45:12+00:00 |
| interactions | `INT-20240125-004` | `interaction_date` | format_normalised | `2024-01-25T10:15:33` | 2024-01-25T10:15:33+00:00 |
| interactions | `INT-20240128-005` | `interaction_date` | format_normalised | `Jan 28, 2024 11:20 AM` | 2024-01-28T11:20:00+00:00 |
| interactions | `INT-20240128-005` | `resolved` | type_coerced | `true` | True |
| interactions | `INT-20240128-005` | `resolution_time_hours` | type_coerced | `1` | 1.0 |
| interactions | `INT-20240201-006` | `interaction_date` | format_normalised | `2024-02-01T15:00:00` | 2024-02-01T15:00:00+00:00 |
| interactions | `INT-20240205-007` | `interaction_date` | format_normalised | `2024-02-05T09:30:22` | 2024-02-05T09:30:22+00:00 |
| interactions | `INT-20240208-008` | `interaction_date` | format_normalised | `08-02-2024 13:45:00` | 2024-02-08T13:45:00+00:00 |
| interactions | `INT-20240208-008` | `resolved` | type_coerced | `1` | True |
| interactions | `INT-20240208-008` | `satisfaction_score` | type_coerced | `4` | 4 |
| interactions | `INT-20240212-009` | `interaction_date` | format_normalised | `2024-02-12T10:00:00Z` | 2024-02-12T10:00:00+00:00 |
| interactions | `INT-20240215-010` | `interaction_date` | format_normalised | `2024-02-15T14:20:11` | 2024-02-15T14:20:11+00:00 |
| interactions | `INT-20240220-011` | `interaction_date` | format_normalised | `20/02/2024 16:30` | 2024-02-20T16:30:00+00:00 |
| interactions | `INT-20240220-011` | `resolved` | type_coerced | `yes` | True |
| interactions | `INT-20240225-012` | `interaction_date` | format_normalised | `2024-02-25T11:15:00` | 2024-02-25T11:15:00+00:00 |
| interactions | `INT-20240228-013` | `interaction_date` | format_normalised | `Feb 28, 2024 09:00:00` | 2024-02-28T09:00:00+00:00 |
| interactions | `INT-20240303-014` | `interaction_date` | format_normalised | `2024-03-03T13:45:30` | 2024-03-03T13:45:30+00:00 |
| interactions | `INT-20240303-014` | `resolved` | type_coerced | `1` | True |
| interactions | `INT-20240308-015` | `interaction_date` | format_normalised | `08/03/2024 10:20` | 2024-03-08T10:20:00+00:00 |
| interactions | `INT-20240308-015` | `resolved` | type_coerced | `True` | True |
| interactions | `INT-20240308-015` | `resolution_time_hours` | type_coerced | `3.5` | 3.5 |
| interactions | `INT-20240315-017` | `interaction_date` | format_normalised | `March 15, 2024 11:00 AM` | 2024-03-15T11:00:00+00:00 |
| interactions | `INT-20240315-017` | `satisfaction_score` | type_coerced | `5` | 5 |
| interactions | `INT-20240320-018` | `interaction_date` | format_normalised | `2024-03-20T09:15:44` | 2024-03-20T09:15:44+00:00 |
| interactions | `INT-20240320-018` | `resolved` | type_coerced | `1` | True |
| interactions | `INT-20240325-019` | `interaction_date` | format_normalised | `25-03-2024 14:00:00` | 2024-03-25T14:00:00+00:00 |
| interactions | `INT-20240328-020` | `interaction_date` | format_normalised | `2024-03-28T16:45:00` | 2024-03-28T16:45:00+00:00 |
| interactions | `INT-20240328-020` | `resolved` | type_coerced | `yes` | True |
| interactions | `INT-20250815-021` | `interaction_date` | format_normalised | `2025-08-15T10:30:00` | 2025-08-15T10:30:00+00:00 |
| interactions | `INT-20250815-021` | `satisfaction_score` | out_of_range | `8` | clamped_to_5 |
| interactions | `11204` | `panelist_email` | multiple_emails_for_panelist | `['roberto.verdi.alt@email.com', 'roberto.verdi@email.com']` | tutti gli hash in panelist_emails; primo marcato is_primary |
| interactions | `INT-20240401-022` | `interaction_date` | format_normalised | `April 1, 2024` | 2024-04-01T00:00:00+00:00 |
| interactions | `INT-20240401-022` | `resolved` | type_coerced | `TRUE` | True |
| interactions | `INT-20240401-022` | `resolution_time_hours` | type_coerced | `2` | 2.0 |
| interactions | `INT-20240401-022` | `satisfaction_score` | type_coerced | `4` | 4 |
| interactions | `10847` | `panelist_email` | multiple_emails_for_panelist | `['giuseppe.bianchi1965@email.it', 'mario.bianchi.nuovo@gmail.com']` | tutti gli hash in panelist_emails; primo marcato is_primary |
| interactions | `INT-20240405-023` | `interaction_date` | format_normalised | `2024-04-05T10:30:00` | 2024-04-05T10:30:00+00:00 |
| interactions | `INT-20240408-024` | `interaction_date` | format_normalised | `08/04/2024 09:15` | 2024-04-08T09:15:00+00:00 |
| interactions | `INT-20240410-025` | `interaction_date` | format_normalised | `2024-04-10T14:45:22` | 2024-04-10T14:45:22+00:00 |
| interactions | `INT-20240412-026` | `interaction_date` | format_normalised | `April 12, 2024 16:00` | 2024-04-12T16:00:00+00:00 |
| interactions | `INT-20240415-027` | `interaction_date` | format_normalised | `15-04-2024 11:30:00` | 2024-04-15T11:30:00+00:00 |
| interactions | `INT-20240415-027` | `resolved` | type_coerced | `1` | True |
| interactions | `INT-20240415-027` | `satisfaction_score` | type_coerced | `5` | 5 |
| interactions | `INT-20240418-028` | `interaction_date` | format_normalised | `2024-04-18T08:45:00+02:00` | 2024-04-18T06:45:00+00:00 |
| interactions | `INT-20240420-029` | `interaction_date` | format_normalised | `2024-04-20T13:20:00` | 2024-04-20T13:20:00+00:00 |
| interactions | `INT-20240422-030` | `interaction_date` | format_normalised | `22/04/2024 10:00` | 2024-04-22T10:00:00+00:00 |
| interactions | `INT-20240422-030` | `resolved` | type_coerced | `true` | True |
| interactions | `INT-20240422-030` | `resolution_time_hours` | type_coerced | `3` | 3.0 |
| interactions | `INT-20240425-031` | `interaction_date` | format_normalised | `2024-04-25T15:00:00Z` | 2024-04-25T15:00:00+00:00 |
| interactions | `INT-20240428-032` | `interaction_date` | format_normalised | `Apr 28, 2024 14:30:00` | 2024-04-28T14:30:00+00:00 |
| interactions | `INT-20240502-033` | `interaction_date` | format_normalised | `2024-05-02T09:00:00` | 2024-05-02T09:00:00+00:00 |
| interactions | `INT-20240502-033` | `resolved` | type_coerced | `1` | True |
| interactions | `INT-20240505-034` | `interaction_date` | format_normalised | `05/05/2024 16:45` | 2024-05-05T16:45:00+00:00 |
| interactions | `INT-20240505-034` | `resolved` | type_coerced | `yes` | True |
| interactions | `INT-20240508-035` | `interaction_date` | format_normalised | `2024-05-08T11:30:15` | 2024-05-08T11:30:15+00:00 |
| interactions | `INT-20240510-036` | `interaction_date` | format_normalised | `May 10, 2024` | 2024-05-10T00:00:00+00:00 |
| interactions | `INT-20240510-036` | `resolved` | type_coerced | `True` | True |
| interactions | `INT-20240510-036` | `resolution_time_hours` | type_coerced | `0.5` | 0.5 |
| interactions | `INT-20240510-036` | `satisfaction_score` | type_coerced | `4` | 4 |
| interactions | `INT-20240512-037` | `interaction_date` | format_normalised | `2024-05-12T14:00:00` | 2024-05-12T14:00:00+00:00 |
| projects | `PRJ-001` | `project_id` | duplicate | `3 records` | keeping most complete |
| projects | `PRJ-002` | `project_id` | duplicate | `2 records` | keeping most complete |
| projects | `PRJ-030` | `workspace_id` | missing | `` | null |
| projects | `PRJ-031` | `end_date` | end_before_start | `start=2024-05-10 end=2024-03-15` | end_date_set_null |
| projects | `PRJ-031` | `budget` | negative_value | `-5000.0` | set_null |
| projects | `PRJ-032` | `end_date` | end_before_start | `start=2024-06-01 end=2024-04-20` | end_date_set_null |
| projects | `PRJ-042` | `project_id` | duplicate | `2 records` | keeping most complete |

---

## Anonimizzazione GDPR

| Entità | Campi Pseudonimizzati | Algoritmo |
|--------|-----------------------|-----------|
| Panelist | `email`, `phone` | SHA-256(salt + value), prefisso `em_` / `ph_` |
| Agent | `agent_name` | SHA-256(salt + value), prefisso `ag_` |

L'hashing è **deterministico** — lo stesso input produce sempre lo stesso token,
preservando l'integrità referenziale tra le tabelle.
Il salt **non viene salvato** in nessun file di output.

---

## Strategia di Deduplicazione

### Interazioni
Chiave: `interaction_id` in maiuscolo + senza spazi.  
Strategia: **mantieni la prima occorrenza**, scarta le successive.

### Progetti
Chiave: `project_id` in maiuscolo + senza spazi.  
Strategia: **mantieni il record più completo** (maggior numero di campi non vuoti).

Duplicati confermati nei dati sorgente:
- `PRJ-001` — 3 record (`PRJ-001`, `prj-001`, `PRJ-001 ` con spazio finale)
- `PRJ-002` — 2 record (`PRJ-002`, `prj-002`)
- `PRJ-042` — 2 record (`PRJ-042`, `prj-042`)

---

## Anomalie Note per Sorgente

### `panelist_interactions.json`

| # | Anomalia | Record Coinvolti | Correzione Applicata |
|---|----------|-----------------|----------------------|
| 1 | **Formati data** — 12+ varianti (`ISO`, `dd/mm/yyyy`, `Jan 28, 2024 11:20 AM`, `08-02-2024`, …) | tutti | Normalizzati a ISO 8601 (`YYYY-MM-DDTHH:MM:SS`) |
| 2 | **Tipi misti** — `panelist_id`, `resolved`, `satisfaction_score`, `resolution_time_hours` salvati come stringhe | multipli | Convertiti ai tipi corretti |
| 3 | **Rappresentazioni null** — `""`, `"N/A"`, `"0"`, `null` per phone/email/project_ref | multipli | Unificati a SQL NULL |
| 4 | **Punteggio fuori range** — `INT-20250815-021` ha `satisfaction_score = 8` (valido: 1–5) | 1 | Clamped al limite del range (8 → 5) |
| 5 | **Email multiple per lo stesso panelista** — panelista `10847` ha 2 email distinte | 1 panelista | Tutti gli hash salvati in `panelist_emails`; il primo in ordine lessicografico marcato come `is_primary` |
| 6 | **Capitalizzazione workspace_id** — `ws-001`, `WS001`, `WS-001` | multipli | Normalizzati alla forma canonica `WS-001` |
| 7 | **Capitalizzazione project_ref** — `prj-001`, `N/A`, vuoto | multipli | Normalizzati a `PRJ-001`; marcatori non validi → NULL |
| 8 | **Capitalizzazione channel** — `email`, `PHONE`, `CHAT` | multipli | Normalizzati tramite `.capitalize()` |

### `projects_raw.csv`

| # | Anomalia | Record Coinvolti | Correzione Applicata |
|---|----------|-----------------|----------------------|
| 1 | **Record duplicati** (3× per PRJ-001, 2× per PRJ-002, 2× per PRJ-042) | 7 righe → 3 uniche | Mantenuto il più completo |
| 2 | **Spazio finale in project_id** (`PRJ-001 `) | 1 | Rimosso durante il raggruppamento |
| 3 | **Formati data** — `March 10 2024`, `01-Mar-2024`, `15/01/2024`, stringa `null` | multipli | Normalizzati a ISO 8601 |
| 4 | **Budget** — simboli di valuta (`€15000`, `22000 EUR`), valore negativo (`-5000`) | multipli | Simboli rimossi; negativi → NULL |
| 5 | **PRJ-032** — `end_date` (2024-04-20) precedente a `start_date` (2024-06-01) | 1 | `end_date` impostata a NULL |
| 6 | **Alias di stato** — `active` → `In Progress`, `completed` → `Completed` | multipli | Mappati ai valori canonici |
| 7 | **Nomi di paese estesi** — `Italy` → `IT`, `Germany` → `DE`, `UK` → `GB` | multipli | Mappati a codici ISO-2 |
| 8 | **Alias di metodologia** — `Online Survey` → `CAWI`, `Telephone Survey` → `CATI` | multipli | Mappati ai nomi canonici |
| 9 | **PRJ-030** — `workspace_id` mancante | 1 | NULL (segnalato) |
| 10 | **Colonna `project_manager`** — contiene dati personali, assente dallo schema target | tutti | Rimossa silenziosamente |
| 11 | **Stringhe NULL** in `project_manager` / `end_date` (`"null"`, `"NULL"`, `"N/A"`) | multipli | Unificate a SQL NULL |

### `research_faq.txt`

| # | Anomalia | Correzione |
|---|----------|------------|
| 1 | **Codifica** — `â‚¬` invece di `€` (mojibake, latin-1 letto come UTF-8) | Sostituiti con glifi UTF-8 corretti |
