#!/usr/bin/env python3
import csv
import hashlib
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


# ─── Paths ───────────────────────────────────────────────────────────────────────

ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = ROOT / "data"
OUT_DIR = Path(__file__).resolve().parent
CLEANED_DIR = OUT_DIR / "cleaned_data"


# ─── GDPR Pseudonymisation ───────────────────────────────────────────────────────

_SALT = "mgdt-gdpr-2024"  # in production: load from env / secrets manager


def _pseudonymise(prefix: str, value: str) -> str:
    h = hashlib.sha256(f"{_SALT}:{prefix}:{value}".encode()).hexdigest()
    return f"{prefix}_{h}"


class Anonymiser:

    def __init__(self) -> None:
        self._emails: dict[str, str] = {}
        self._phones: dict[str, str] = {}
        self._names: dict[str, str] = {}

    def email(self, v: Optional[str]) -> Optional[str]:
        if not v:
            return None
        key = v.lower().strip()
        if key not in self._emails:
            self._emails[key] = _pseudonymise("em", key)
        return self._emails[key]

    def phone(self, v: Optional[str]) -> Optional[str]:
        if not v:
            return None
        if v not in self._phones:
            self._phones[v] = _pseudonymise("ph", v)
        return self._phones[v]

    def name(self, v: Optional[str]) -> Optional[str]:
        if not v:
            return None
        key = v.strip()
        if key not in self._names:
            self._names[key] = _pseudonymise("ag", key)
        return self._names[key]


# ─── Date Parsing ────────────────────────────────────────────────────────────────

_DATE_FORMATS = [
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%dT%H:%M:%SZ",
    "%Y-%m-%dT%H:%M:%S%z",
    "%Y-%m-%d",
    "%d/%m/%Y %H:%M:%S",
    "%d/%m/%Y %H:%M",
    "%d/%m/%Y",
    "%m/%d/%Y",
    "%d-%m-%Y %H:%M:%S",
    "%d-%m-%Y %H:%M",
    "%d-%m-%Y",
    "%d-%b-%Y",             # 01-Mar-2024
    "%B %d, %Y %I:%M %p",   # January 28, 2024 11:20 AM
    "%b %d, %Y %I:%M %p",   # Jan 28, 2024 11:20 AM
    "%B %d, %Y %H:%M:%S",   # March 15, 2024 11:00:00
    "%b %d, %Y %H:%M:%S",   # Mar 15, 2024 11:00:00
    "%B %d, %Y %H:%M",      # April 12, 2024 16:00
    "%b %d, %Y %H:%M",      # Apr 28, 2024 14:30
    "%B %d, %Y",            # April 1, 2024
    "%b %d, %Y",            # Apr 28, 2024
    "%B %d %Y",             # March 10 2024
    "%b %d %Y",
    "%d %b %Y",
    "%d %B %Y",
    "%Y/%m/%d",
]

_NULL_MARKERS = frozenset({"", "null", "n/a", "na", "none", "-"})


def _clean_str(v: Any) -> Optional[str]:
    if v is None:
        return None
    s = str(v).strip()
    return None if s.lower() in _NULL_MARKERS else s


def parse_datetime(v: Any) -> Optional[str]:
    """Parse any supported datetime format and return an ISO 8601 string normalised to UTC (+00:00)."""
    try:
        s = _clean_str(v)
        if s is None:
            return None
        # Normalise Z suffix so %z can parse it
        s_normalized = re.sub(r'Z$', '+00:00', s.strip())  # "Z" finale → "+00:00" per compatibilità con %z
        for src in (s_normalized, s):
            for fmt in _DATE_FORMATS:
                try:
                    dt = datetime.strptime(src, fmt)
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                    else:
                        dt = dt.astimezone(timezone.utc)
                    return dt.strftime("%Y-%m-%dT%H:%M:%S+00:00")
                except ValueError:
                    pass
        print(f"[WARN] parse_datetime: unrecognised format for value {v!r}")
        return None
    except Exception as e:
        print(f"[ERROR] parse_datetime: unexpected error on value {v!r}: {type(e).__name__}: {e}")
        return None


def parse_date_only(v: Any) -> Optional[str]:
    dt = parse_datetime(v)
    return dt[:10] if dt else None


# ─── Field Coercions ─────────────────────────────────────────────────────────────

def coerce_bool(v: Any) -> Optional[bool]:
    if v is None:
        return None
    if isinstance(v, bool):
        return v
    if isinstance(v, int):
        return bool(v)
    s = str(v).strip().lower()
    if s in ("true", "1", "yes", "t"):
        return True
    if s in ("false", "0", "no", "f"):
        return False
    return None


def coerce_float(v: Any) -> Optional[float]:
    s = _clean_str(v)
    if s is None:
        return None
    s = re.sub(r'[€$£]|\s*eur\s*', '', s, flags=re.IGNORECASE).strip()  # rimuove simboli valuta (€, $, £) e "eur" con spazi opzionali
    try:
        return float(s)
    except ValueError:
        return None


def coerce_int(v: Any) -> Optional[int]:
    f = coerce_float(v)
    return int(f) if f is not None else None


def normalise_workspace(v: Any) -> Optional[str]:
    s = _clean_str(v)
    if s is None:
        return None
    s = s.strip().upper().replace(" ", "")
    m = re.match(r'^WS-?(\d+)$', s)  # accetta "WS001" o "WS-001", cattura la parte numerica
    return f"WS-{m.group(1).zfill(3)}" if m else s


def normalise_project_id(v: Any) -> Optional[str]:
    s = _clean_str(v)
    if s is None:
        return None
    s = s.strip().upper().replace(" ", "")
    m = re.match(r'^PRJ-?(\d+)$', s)  # accetta "PRJ001" o "PRJ-001", cattura la parte numerica
    return f"PRJ-{m.group(1).zfill(3)}" if m else None


def normalise_channel(v: Any) -> Optional[str]:
    s = _clean_str(v)
    return s.capitalize() if s else None


def normalise_status(v: Any) -> Optional[str]:
    s = _clean_str(v)
    if s is None:
        return None
    _MAP = {
        "completed": "Completed",
        "in progress": "In Progress",
        "active": "In Progress",
        "on hold": "On Hold",
        "cancelled": "Cancelled",
        "canceled": "Cancelled",
    }
    return _MAP.get(s.lower(), s.title())


def normalise_country(v: Any) -> Optional[str]:
    s = _clean_str(v)
    if s is None:
        return None
    _MAP = {
        "italy": "IT", "italia": "IT",
        "germany": "DE", "germania": "DE",
        "france": "FR", "francia": "FR",
        "uk": "GB", "united kingdom": "GB",
        "us": "US", "usa": "US", "united states": "US",
        "spain": "ES", "spagna": "ES",
    }
    return _MAP.get(s.lower(), s.upper()[:2])


def normalise_methodology(v: Any) -> str:
    s = _clean_str(v) or "UNKNOWN"
    _MAP = {
        "online survey": "CAWI",
        "telephone survey": "CATI",
        "online panel": "Online Panel",
        "online community": "Online Community",
        "face to face": "Face to Face",
        "face-to-face": "Face to Face",
        "mixed methods": "Mixed Methods",
        "mixed": "Mixed Methods",
    }
    return _MAP.get(s.lower(), s)


def normalise_phone(v: Any) -> Optional[str]:
    """Return None for clearly invalid phone values."""
    s = _clean_str(v)
    if s is None:
        return None
    # single digit or obviously placeholder
    if re.match(r'^\d{1,2}$', s):  # 1-2 cifre sole → valore placeholder, non un numero di telefono valido
        return None
    return s


# ─── Quality Log ─────────────────────────────────────────────────────────────────

class QualityLog:
    """Registro centralizzato della qualità dei dati prodotto durante l'ETL.

    Raccoglie due tipi di informazioni:
    - ``issues``: lista di anomalie per singolo record (campo mancante, valore
      fuori range, tipo errato, ecc.), ognuna con sorgente, ID record, campo
      coinvolto, descrizione del problema, valore originale e azione intrapresa.
    - ``counters``: contatori aggregati (record grezzi, puliti, rifiutati, …)
      usati nel report di riepilogo.

    L'istanza viene passata a tutte le funzioni ETL e alla fine serializzata in
    ``data_quality_report.md`` tramite ``write_report()``.
    """

    def __init__(self) -> None:
        self.issues: list[dict] = []
        self.counters: dict[str, int] = defaultdict(int)

    def log(self, source: str, rid: str, field: str, issue: str,
            original: Any = None, resolution: str = "") -> None:
        self.issues.append({
            "source": source,
            "record_id": str(rid),
            "field": field,
            "issue": issue,
            "original_value": str(original)[:120] if original is not None else "",
            "resolution": resolution,
        })
        self.counters[f"{source}.{issue}"] += 1

    def count(self, key: str, n: int = 1) -> None:
        self.counters[key] += n


# ─── Workspaces ──────────────────────────────────────────────────────────────────

def extract_workspaces(
    interactions: list[dict],
    projects: list[dict],
) -> list[dict]:
    ws_ids: set[str] = set()
    for rec in interactions:
        if rec.get("workspace_id"):
            ws_ids.add(rec["workspace_id"])
    for rec in projects:
        if rec.get("workspace_id"):
            ws_ids.add(rec["workspace_id"])
    return [
        {
            "workspace_id": wid,
            "workspace_name": f"Workspace {wid}",
            "created_at": "2024-01-01T00:00:00",
        }
        for wid in sorted(ws_ids)
    ]


# ─── Interactions ETL ─────────────────────────────────────────────────────────────

def etl_interactions(
    path: Path, anon: Anonymiser, log: QualityLog
) -> tuple[list[dict], list[dict], list[dict], list[dict]]:
    """Returns (interactions, panelists, panelist_emails, agents) — all PII removed from interactions."""
    with open(path, encoding="utf-8") as f:
        raw: list[dict] = json.load(f)

    log.count("interactions.raw", len(raw))

    panelists: dict[int, dict] = {}
    agents: dict[str, str] = {}     # raw_name → hash
    cleaned: list[dict] = []
    seen_ids: set[str] = set()

    for rec in raw:
        rid = str(rec.get("interaction_id", "")).strip()
        norm_id = rid.upper()

        # ── duplicate id ─────────────────────────────────────────────────────
        if norm_id in seen_ids:
            log.log("interactions", rid, "interaction_id", "duplicate", rid, "skipped")
            continue
        seen_ids.add(norm_id)

        try:
            # ── panelist_id ───────────────────────────────────────────────────────
            pid = coerce_int(rec.get("panelist_id"))
            if pid is None:
                log.log("interactions", rid, "panelist_id", "missing_or_invalid",
                        rec.get("panelist_id"), "record_rejected")
                log.count("interactions.rejected")
                continue

            # ── workspace_id ──────────────────────────────────────────────────────
            ws = normalise_workspace(rec.get("workspace_id"))
            if ws is None:
                log.log("interactions", rid, "workspace_id", "missing", None, "null")

            # ── date ──────────────────────────────────────────────────────────────
            raw_date = rec.get("interaction_date")
            date_parsed = parse_datetime(raw_date)
            if date_parsed is None:
                log.log("interactions", rid, "interaction_date", "unparseable",
                        raw_date, "null")
            elif str(raw_date).strip() != date_parsed:
                log.log("interactions", rid, "interaction_date", "format_normalised",
                        raw_date, date_parsed)

            # ── project_id ────────────────────────────────────────────────────────
            proj = normalise_project_id(rec.get("project_ref"))

            # ── resolved ─────────────────────────────────────────────────────────
            raw_resolved = rec.get("resolved")
            resolved = coerce_bool(raw_resolved)
            if resolved is None:
                log.log("interactions", rid, "resolved", "unparseable", raw_resolved, "null")
            elif not isinstance(raw_resolved, bool):
                log.log("interactions", rid, "resolved", "type_coerced",
                        raw_resolved, str(resolved))

            # ── resolution_time_hours ─────────────────────────────────────────────
            rth_raw = rec.get("resolution_time_hours")
            rth = coerce_float(rth_raw)
            if rth_raw is not None and not isinstance(rth_raw, (int, float)):
                log.log("interactions", rid, "resolution_time_hours", "type_coerced",
                        rth_raw, str(rth))

            # ── satisfaction_score ────────────────────────────────────────────────
            score_raw = rec.get("satisfaction_score")
            score = coerce_int(score_raw)
            if score is not None and not isinstance(score_raw, int):
                log.log("interactions", rid, "satisfaction_score", "type_coerced",
                        score_raw, str(score))
            if score is not None and not (1 <= score <= 5):
                clamped = max(1, min(5, score))
                log.log("interactions", rid, "satisfaction_score", "out_of_range",
                        score, f"clamped_to_{clamped}")
                score = clamped

            # ── collect PII (track latest contact info per panelist) ──────────────
            raw_email = _clean_str(rec.get("panelist_email"))
            raw_phone = normalise_phone(rec.get("panelist_phone"))

            if pid not in panelists:
                panelists[pid] = {"workspace_id": ws, "emails": set(), "phones": set()}
            p = panelists[pid]
            if raw_email:
                p["emails"].add(raw_email.lower())
            if raw_phone:
                p["phones"].add(raw_phone)
            if ws and p["workspace_id"] is None:
                p["workspace_id"] = ws

            if len(p["emails"]) > 1:
                log.log("interactions", str(pid), "panelist_email",
                        "multiple_emails_for_panelist",
                        sorted(p["emails"]), "tutti gli hash in panelist_emails; primo marcato is_primary")

            # ── agent ─────────────────────────────────────────────────────────────
            agent_raw = (rec.get("agent_name") or "").strip()
            if agent_raw and agent_raw not in agents:
                agents[agent_raw] = anon.name(agent_raw)
            agent_hash = agents.get(agent_raw)

            cleaned.append({
                "interaction_id": norm_id,
                "workspace_id": ws,
                "panelist_id": pid,
                "project_id": proj,
                "agent_id_hash": agent_hash,
                "issue_type": _clean_str(rec.get("issue_type")),
                "interaction_date": date_parsed,
                "channel": normalise_channel(rec.get("channel")),
                "issue_description": _clean_str(rec.get("issue_description")),
                "resolution": _clean_str(rec.get("resolution")),
                "resolved": resolved,
                "resolution_time_hours": rth,
                "satisfaction_score": score,
            })
            log.count("interactions.cleaned")
        except Exception as e:
            print(f"[ERROR] interactions: unexpected error on record '{rid}': {type(e).__name__}: {e}")
            log.log("interactions", rid, "*", "unexpected_error", str(e), "record_skipped")
            log.count("interactions.error")

    # ── panelists table (anonymised) ──────────────────────────────────────────
    panelists_out = []
    panelist_emails_out = []
    for pid, p in sorted(panelists.items()):
        emails = sorted(p["emails"])
        phones = sorted(p["phones"])
        panelists_out.append({
            "panelist_id": pid,
            "workspace_id": p["workspace_id"],
            "phone_hash": anon.phone(phones[0]) if phones else None,
        })
        for i, email in enumerate(emails):
            panelist_emails_out.append({
                "panelist_id": pid,
                "email_hash": anon.email(email),
                "is_primary": i == 0,
            })

    agents_out = [
        {"agent_id_hash": h}
        for h in sorted(set(agents.values()))
    ]

    log.count("interactions.unique_panelists", len(panelists_out))
    log.count("interactions.unique_agents", len(agents_out))
    return cleaned, panelists_out, panelist_emails_out, agents_out


# ─── Projects ETL ─────────────────────────────────────────────────────────────────

def etl_projects(
    path: Path, log: QualityLog
) -> tuple[list[dict], list[dict], list[dict]]:
    """Returns (projects, clients, methodologies)."""
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    log.count("projects.raw", len(rows))

    # ── group by normalised project_id for deduplication ─────────────────────
    groups: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        key = re.sub(r'\s+', '', row.get("project_id", "").strip()).upper()  # elimina tutti gli spazi interni per normalizzare la chiave di deduplicazione
        groups[key].append(row)

    clients: dict[tuple, int] = {}
    methodologies: dict[str, int] = {}
    c_seq = m_seq = 1
    clients_out: list[dict] = []
    methodologies_out: list[dict] = []
    projects_out: list[dict] = []

    for canonical, group in groups.items():
        try:
            if len(group) > 1:
                log.log("projects", canonical, "project_id", "duplicate",
                        f"{len(group)} records", "keeping most complete")
                # projects.duplicate è già auto-incrementato da log.log() — nessun contatore separato necessario
                # keep the record with most non-empty fields
                group.sort(
                    key=lambda r: sum(1 for v in r.values() if v and v.strip()),
                    reverse=True,
                )
            row = group[0]

            pid = normalise_project_id(canonical)
            if pid is None:
                log.log("projects", canonical, "project_id", "invalid", canonical, "rejected")
                log.count("projects.rejected")
                continue

            ws = normalise_workspace(row.get("workspace_id"))
            if ws is None:
                log.log("projects", pid, "workspace_id", "missing", None, "null")

            # ── client ────────────────────────────────────────────────────────────
            client_name = _clean_str(row.get("client_name"))
            ck = (ws or "", client_name or "")
            if ck not in clients:
                clients[ck] = c_seq
                clients_out.append({
                    "client_id": c_seq,
                    "workspace_id": ws,
                    "client_name": client_name,
                })
                c_seq += 1
            client_id = clients[ck]

            # ── methodology ───────────────────────────────────────────────────────
            meth_name = normalise_methodology(row.get("methodology", ""))
            meth_code = re.sub(r'[\s\-]+', '_', meth_name).upper()  # spazi e trattini → underscore per ottenere un codice tipo "ONLINE_PANEL"
            if meth_code not in methodologies:
                methodologies[meth_code] = m_seq
                methodologies_out.append({
                    "methodology_id": m_seq,
                    "methodology_code": meth_code,
                    "methodology_name": meth_name,
                })
                m_seq += 1
            meth_id = methodologies[meth_code]

            # ── dates ─────────────────────────────────────────────────────────────
            start = parse_date_only(row.get("start_date"))
            if start is None:
                log.log("projects", pid, "start_date", "missing_or_invalid",
                        row.get("start_date"), "null")

            end = parse_date_only(_clean_str(row.get("end_date")))
            if start and end and end < start:
                log.log("projects", pid, "end_date", "end_before_start",
                        f"start={start} end={end}", "end_date_set_null")
                end = None

            # ── budget ────────────────────────────────────────────────────────────
            budget = coerce_float(row.get("budget"))
            if budget is not None and budget < 0:
                log.log("projects", pid, "budget", "negative_value", budget, "set_null")
                budget = None

            # project_manager is dropped: not in target schema + contains PII
            projects_out.append({
                "project_id": pid,
                "workspace_id": ws,
                "client_id": client_id,
                "methodology_id": meth_id,
                "project_name": _clean_str(row.get("project_name")),
                "research_topic": _clean_str(row.get("research_topic")),
                "start_date": start,
                "end_date": end,
                "sample_size": coerce_int(row.get("sample_size")),
                "budget": budget,
                "country_code": normalise_country(row.get("country")),
                "status": normalise_status(row.get("status")),
                "notes": _clean_str(row.get("notes")),
            })
            log.count("projects.cleaned")
        except Exception as e:
            print(f"[ERROR] projects: unexpected error on project '{canonical}': {type(e).__name__}: {e}")
            log.log("projects", canonical, "*", "unexpected_error", str(e), "record_skipped")
            log.count("projects.error")

    log.count("projects.unique_clients", len(clients_out))
    log.count("projects.unique_methodologies", len(methodologies_out))
    return projects_out, clients_out, methodologies_out


# ─── FAQ ETL ──────────────────────────────────────────────────────────────────────

def etl_faq(
    path: Path, log: QualityLog
) -> tuple[list[dict], list[dict]]:
    text = path.read_text(encoding="utf-8", errors="replace")
    # Fix mojibake (latin-1 read as utf-8)
    text = (text
            .replace("â‚¬", "€")
            .replace("â€™", "'")
            .replace("â€œ", '"')
            .replace("â€", '"'))

    categories: dict[str, int] = {}
    cats_out: list[dict] = []
    faqs_out: list[dict] = []
    c_seq = faq_seq = 1
    current_cat: Optional[str] = None

    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # --- CATEGORY HEADER ---
        m = re.match(r'^---\s+(.+?)\s+---$', line)  # header di categoria: "--- Nome Categoria ---"
        if m:
            current_cat = m.group(1).strip().title()
            if current_cat not in categories:
                categories[current_cat] = c_seq
                cats_out.append({"category_id": c_seq, "category_name": current_cat})
                c_seq += 1
            i += 1
            continue

        # Q: question
        q_m = re.match(r'^Q:\s*(.+)$', line)  # riga domanda: "Q: testo della domanda"
        if q_m:
            question = q_m.group(1).strip()
            answer_parts: list[str] = []
            j = i + 1
            while j < len(lines):
                a_m = re.match(r'^A:\s*(.+)$', lines[j].strip())  # riga risposta: "A: testo della risposta"
                if a_m:
                    answer_parts.append(a_m.group(1).strip())
                    j += 1
                    while j < len(lines):
                        nx = lines[j].strip()
                        if not nx or nx.startswith("Q:") or re.match(r'^[-=]{3}', nx):  # fine risposta: riga vuota, nuova domanda, o separatore "---"/"==="
                            break
                        answer_parts.append(nx)
                        j += 1
                    break
                j += 1

            cat_id = categories.get(current_cat, 1) if current_cat else 1
            faqs_out.append({
                "id": faq_seq,
                "category_id": cat_id,
                "question": question,
                "answer": " ".join(filter(None, answer_parts)),
                "created_at": "1975-03-01T00:00:00",
            })
            faq_seq += 1
            i = j
            continue

        i += 1

    log.count("faq.parsed", len(faqs_out))
    log.count("faq.categories", len(cats_out))
    return faqs_out, cats_out


# ─── I/O ─────────────────────────────────────────────────────────────────────────

def write_json(records: list[dict], p: Path) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        json.dumps(records, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )


def write_csv(records: list[dict], p: Path) -> None:
    if not records:
        return
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(records[0]))
        w.writeheader()
        w.writerows(records)


# ─── Quality Report ───────────────────────────────────────────────────────────────

def write_report(log: QualityLog, path: Path) -> None:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    md: list[str] = [
        "# Report Qualità dei Dati",
        "",
        f"_Generato il: {now}_",
        "",
        "---",
        "",
        "## Statistiche di Riepilogo",
        "",
        "| Metrica | Valore |",
        "|---------|--------|",
        *[f"| `{k}` | {v} |" for k, v in sorted(log.counters.items())],
        "",
        "---",
        "",
        "## Log delle Anomalie",
        "",
        "| Sorgente | ID Record | Campo | Anomalia | Valore Originale | Risoluzione |",
        "|----------|-----------|-------|----------|------------------|-------------|",
        *[
            f"| {i['source']} | `{i['record_id']}` | `{i['field']}` "
            f"| {i['issue']} | `{i['original_value']}` | {i['resolution']} |"
            for i in log.issues
        ],
        "",
        "---",
        "",
        "## Anonimizzazione GDPR",
        "",
        "| Entità | Campi Pseudonimizzati | Algoritmo |",
        "|--------|-----------------------|-----------|",
        "| Panelist | `email`, `phone` | SHA-256(salt + value), prefisso `em_` / `ph_` |",
        "| Agent | `agent_name` | SHA-256(salt + value), prefisso `ag_` |",
        "",
        "L'hashing è **deterministico** — lo stesso input produce sempre lo stesso token,",
        "preservando l'integrità referenziale tra le tabelle.",
        "Il salt **non viene salvato** in nessun file di output.",
        "",
        "---",
        "",
        "## Strategia di Deduplicazione",
        "",
        "### Interazioni",
        "Chiave: `interaction_id` in maiuscolo + senza spazi.  ",
        "Strategia: **mantieni la prima occorrenza**, scarta le successive.",
        "",
        "### Progetti",
        "Chiave: `project_id` in maiuscolo + senza spazi.  ",
        "Strategia: **mantieni il record più completo** (maggior numero di campi non vuoti).",
        "",
        "Duplicati confermati nei dati sorgente:",
        "- `PRJ-001` — 3 record (`PRJ-001`, `prj-001`, `PRJ-001 ` con spazio finale)",
        "- `PRJ-002` — 2 record (`PRJ-002`, `prj-002`)",
        "- `PRJ-042` — 2 record (`PRJ-042`, `prj-042`)",
        "",
        "---",
        "",
        "## Anomalie Note per Sorgente",
        "",
        "### `panelist_interactions.json`",
        "",
        "| # | Anomalia | Record Coinvolti | Correzione Applicata |",
        "|---|----------|-----------------|----------------------|",
        "| 1 | **Formati data** — 12+ varianti (`ISO`, `dd/mm/yyyy`, `Jan 28, 2024 11:20 AM`, `08-02-2024`, …) | tutti | Normalizzati a ISO 8601 (`YYYY-MM-DDTHH:MM:SS`) |",
        "| 2 | **Tipi misti** — `panelist_id`, `resolved`, `satisfaction_score`, `resolution_time_hours` salvati come stringhe | multipli | Convertiti ai tipi corretti |",
        "| 3 | **Rappresentazioni null** — `\"\"`, `\"N/A\"`, `\"0\"`, `null` per phone/email/project_ref | multipli | Unificati a SQL NULL |",
        "| 4 | **Punteggio fuori range** — `INT-20250815-021` ha `satisfaction_score = 8` (valido: 1–5) | 1 | Clamped al limite del range (8 → 5) |",
        "| 5 | **Email multiple per lo stesso panelista** — panelista `10847` ha 2 email distinte | 1 panelista | Tutti gli hash salvati in `panelist_emails`; il primo in ordine lessicografico marcato come `is_primary` |",
        "| 6 | **Capitalizzazione workspace_id** — `ws-001`, `WS001`, `WS-001` | multipli | Normalizzati alla forma canonica `WS-001` |",
        "| 7 | **Capitalizzazione project_ref** — `prj-001`, `N/A`, vuoto | multipli | Normalizzati a `PRJ-001`; marcatori non validi → NULL |",
        "| 8 | **Capitalizzazione channel** — `email`, `PHONE`, `CHAT` | multipli | Normalizzati tramite `.capitalize()` |",
        "",
        "### `projects_raw.csv`",
        "",
        "| # | Anomalia | Record Coinvolti | Correzione Applicata |",
        "|---|----------|-----------------|----------------------|",
        "| 1 | **Record duplicati** (3× per PRJ-001, 2× per PRJ-002, 2× per PRJ-042) | 7 righe → 3 uniche | Mantenuto il più completo |",
        "| 2 | **Spazio finale in project_id** (`PRJ-001 `) | 1 | Rimosso durante il raggruppamento |",
        "| 3 | **Formati data** — `March 10 2024`, `01-Mar-2024`, `15/01/2024`, stringa `null` | multipli | Normalizzati a ISO 8601 |",
        "| 4 | **Budget** — simboli di valuta (`€15000`, `22000 EUR`), valore negativo (`-5000`) | multipli | Simboli rimossi; negativi → NULL |",
        "| 5 | **PRJ-032** — `end_date` (2024-04-20) precedente a `start_date` (2024-06-01) | 1 | `end_date` impostata a NULL |",
        "| 6 | **Alias di stato** — `active` → `In Progress`, `completed` → `Completed` | multipli | Mappati ai valori canonici |",
        "| 7 | **Nomi di paese estesi** — `Italy` → `IT`, `Germany` → `DE`, `UK` → `GB` | multipli | Mappati a codici ISO-2 |",
        "| 8 | **Alias di metodologia** — `Online Survey` → `CAWI`, `Telephone Survey` → `CATI` | multipli | Mappati ai nomi canonici |",
        "| 9 | **PRJ-030** — `workspace_id` mancante | 1 | NULL (segnalato) |",
        "| 10 | **Colonna `project_manager`** — contiene dati personali, assente dallo schema target | tutti | Rimossa silenziosamente |",
        "| 11 | **Stringhe NULL** in `project_manager` / `end_date` (`\"null\"`, `\"NULL\"`, `\"N/A\"`) | multipli | Unificate a SQL NULL |",
        "",
        "### `research_faq.txt`",
        "",
        "| # | Anomalia | Correzione |",
        "|---|----------|------------|",
        "| 1 | **Codifica** — `â‚¬` invece di `€` (mojibake, latin-1 letto come UTF-8) | Sostituiti con glifi UTF-8 corretti |",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(md), encoding="utf-8")
    print(f"  ✓ report → {path.relative_to(ROOT)}")


# ─── Main ─────────────────────────────────────────────────────────────────────────

def main() -> None:
    print("=" * 52)
    print("  MegaDitta ETL Pipeline")
    print("=" * 52)

    anon = Anonymiser()
    log = QualityLog()

    # 1. Interactions ─────────────────────────────────────────────────────────
    print("\n[1/4] interactions...")
    interactions, panelists, panelist_emails, agents = etl_interactions(
        DATA_DIR / "panelist_interactions.json", anon, log
    )
    for name, records in [
        ("interactions", interactions),
        ("panelists", panelists),
        ("panelist_emails", panelist_emails),
        ("agents", agents),
    ]:
        write_json(records, CLEANED_DIR / f"{name}.json")
        write_csv(records, CLEANED_DIR / f"{name}.csv")
    print(f"       {len(interactions)} interactions | {len(panelists)} panelists | {len(panelist_emails)} email hashes | {len(agents)} agents")

    # 2. Projects ─────────────────────────────────────────────────────────────
    print("\n[2/4] projects...")
    projects, clients, methodologies = etl_projects(DATA_DIR / "projects_raw.csv", log)
    for name, records in [
        ("projects", projects),
        ("clients", clients),
        ("methodologies", methodologies),
    ]:
        write_json(records, CLEANED_DIR / f"{name}.json")
        write_csv(records, CLEANED_DIR / f"{name}.csv")
    print(f"       {len(projects)} projects | {len(clients)} clients | {len(methodologies)} methodologies")

    # 3. Workspaces ───────────────────────────────────────────────────────────
    print("\n[3/4] workspaces...")
    workspaces = extract_workspaces(interactions, projects)
    write_json(workspaces, CLEANED_DIR / "workspaces.json")
    write_csv(workspaces, CLEANED_DIR / "workspaces.csv")
    print(f"       {len(workspaces)} workspaces")

    # 4. FAQ ──────────────────────────────────────────────────────────────────
    print("\n[4/4] faq...")
    faqs, faq_categories = etl_faq(DATA_DIR / "research_faq.txt", log)
    for name, records in [
        ("faq", faqs),
        ("faq_categories", faq_categories),
    ]:
        write_json(records, CLEANED_DIR / f"{name}.json")
        write_csv(records, CLEANED_DIR / f"{name}.csv")
    print(f"       {len(faqs)} entries | {len(faq_categories)} categories")

    # Report ──────────────────────────────────────────────────────────────────
    print("\n[+] quality report...")
    write_report(log, OUT_DIR / "data_quality_report.md")

    print("\n" + "=" * 52)
    print("  Done.")
    print(f"  Output: {CLEANED_DIR.relative_to(ROOT)}/")
    print("=" * 52)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[FATAL] Pipeline crashed: {type(e).__name__}: {e}")
        raise
