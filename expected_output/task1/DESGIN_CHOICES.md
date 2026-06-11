# Entità identificate

## Workspaces

Rappresentano le aziende clienti che utilizzano la piattaforma.

Tramite l'inserimento del campo `workspace_id` nelle entità operative è possibile isolare i dati e si garantisce un corretto funzionamento in un ambiente multi-tenant, a scapito dell'introduzione di dipendenza transitiva (3NF ok a livello tabella) ma accettabile per query performanti e scalabilità. 

Vedi il caso di `projects` che contiene `workspace_id` per filtrare i progetti attivi di ogni cliente, senza dover passare da una tabella di join con `clients` che a sua volta è collegata a `workspaces`.

---

## Clients

Entità che rappresenta i clienti che commissionano uno o più progetti di ricerca tramite le aziende clienti (workspaces).

Motivazioni:
* La separazione dei clienti dalla tabella Projects evita la duplicazione del nome cliente su ogni progetto.

Relazioni:

```text
Workspace 1 → N Clients
Client 1 → N Projects
```
---

## Projects

Entità che rappresenta le singole ricerche di mercato.

Contengono informazioni relative a:

* nome del progetto
* date di inizio e fine
* stato del progetto
* budget
* dimensione campione
* argomento della ricerca

Relazioni:

```text
Client 1 → N Projects
Methodology 1 → N Projects
```

---

## Methodologies

Entità per normalizzare le metodologie in una tabella dedicata.

Motivazioni:

* eliminazione di duplicazioni
* possibilità di arricchire le descrizioni

Relazioni:

```text
Methodology 1 → N Projects
```

---

## Panelists

Entità che rappresenta i partecipanti alle ricerche di mercato.
Nel file panelists_interactions.json si vede che le informazioni di email e telefono del panelista sono ripetute in ogni interazione, questo rende necessario la normalizzazione per evitare ridondanza e anomalie di aggiornamento.

Motivazioni:

* Eliminazione della ridondanza
* Miglioramento della coerenza dei dati
* Facilità di aggiornamento delle informazioni

Relazioni:

```text
Panelist 1 → N Interactions
Panelist 1 → N PanalistEmails
```

---

## Panelist Emails

Tabella separata per gestire la relazione 1:N tra panelista e indirizzi email. La necessità è emersa durante l'analisi dei dati sorgente, dove lo stesso `panelist_id` compariva con email distinte in record diversi.

Mantenere le email in una tabella dedicata permette di:

* Preservare tutti gli indirizzi noti senza perdita di informazione
* Identificare l'indirizzo canonico tramite il flag `is_primary`
* Garantire l'integrità referenziale verso `panelists`

L'email è memorizzata come hash pseudonimizzato (`email_hash`) in conformità ai requisiti GDPR. Il flag `is_primary = true` identifica il primo indirizzo in ordine lessicografico, scelto come riferimento deterministico e riproducibile.

Relazione:

```text
Panelist 1 → N PanalistEmails
```

---

## Agents

Entità che rappresenta gli operatori che gestiscono le richieste dei panelisti.

Relazione:

```text
Agent 1 → N Interactions
```

---

## Issue Types

Entità che rappresenta i tipi di richiesta, i quali vengono normalizzati.

Motivazioni:

* riduzione degli errori di inserimento
* migliore aggregazione statistica
* reporting più efficiente

Relazione:

```text
IssueType 1 → N Interactions
```

---

## Interactions

Entità che serve a modellare il principale fatto operativo del sistema, ovvero le interazioni tra panelisti e agenti all'interno di un progetto.

Una interazione collega:

* un panelista
* un progetto
* un agente
* una categoria di problema

Contiene inoltre:

* descrizione del problema
* informazioni di risoluzione
* soddisfazione dell'utente

Questa tabella costituisce il principale storico operativo interrogato dall'agente AI.

**Assunzione: range di `satisfaction_score`**

Il campo `satisfaction_score` accetta valori interi compresi tra 1 e 5 (vincolo `CHECK` in schema). Questo range non è esplicitamente specificato nell'assignment ma è stato inferito dall'osservazione dei dati sorgente, dove tutti i valori validi rientrano in questo intervallo e l'unico outlier (8) è chiaramente anomalo rispetto alla scala standard Likert. In fase ETL i valori fuori range vengono clamped al limite più vicino (es. 8 → 5).

---

## Knowledge Base

Il file FAQ fornito rappresenta conoscenza strutturata che può essere interrogata dall'agente AI.

È stata modellata tramite 2 entità:

* FAQ Categories
* FAQ

Ogni FAQ contiene:

* domanda
* risposta

Esempio:

```text
Q: Cosa significa CAWI?
A: Computer Assisted Web Interviewing...
```

Questa scelta permette una futura integrazione con sistemi RAG (Retrieval Augmented Generation).

---

# Verifica della Terza Forma Normale (3NF)

## Prima Forma Normale (1NF)

Tutti gli attributi sono atomici.

Non esistono:

* liste
* array
* campi multivalore

---

## Seconda Forma Normale (2NF)

Tutti gli attributi non chiave dipendono interamente dalla chiave primaria.

Esempio:

Il telefono del panelista dipende dal panelista e non dall'interazione, per cui è stato estratto in `panelists`.

Le email sono state ulteriormente normalizzate in una tabella separata `panelist_emails` (relazione 1:N), in quanto uno stesso panelista può avere più indirizzi email distinti. Ogni riga riporta l'hash dell'email e il flag `is_primary` che indica l'indirizzo canonico.

---

## Terza Forma Normale (3NF)

Sono state eliminate le dipendenze transitive per cui attributi non chiave dipendono da altri attributi non chiave.

Esempio:

```text
project
 → methodology_code
 → methodology_description
```

La descrizione della metodologia è stata spostata nella tabella:

```text
methodologies
```

Analogo approccio è stato utilizzato per:

```text
issue_types
faq_categories
```

---

# Ottimizzazioni per l'Agente AI

Facendo delle supposizioni, le query più frequenti previste potrebbero essere:

* progetti attivi per workspace
* interazioni associate ad un progetto
* storico di un panelista
* performance degli agenti
* ricerca di definizioni metodologiche

Per supportare questi casi d'uso sono stati introdotti indici su:

```text
projects(workspace_id, status)

interactions(project_id)

interactions(panelist_id)

interactions(agent_id)

interactions(interaction_date)

faq(category_id)
```

---