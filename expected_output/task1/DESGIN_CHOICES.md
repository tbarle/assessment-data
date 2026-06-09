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

Relazione:

```text
Panelist 1 → N Interactions
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

Email e telefono del panelista dipendono dal panelista e non dall'interazione.

Per questo motivo sono stati estratti nella tabella:

```text
panelists
```

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