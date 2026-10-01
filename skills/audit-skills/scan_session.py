#!/usr/bin/env python3
"""scan_session.py — what the skills, subagents and tools in Claude Code sessions actually did.

Two modes:

* **Cross-session (default).** Finds every session under ``~/.claude/projects/`` in which a
  skill of the plugin (``--plugin``, default ``dev-skills``) actually ran — invoked through the
  ``Skill`` tool or typed as ``/<plugin>:<skill>`` — optionally narrowed to a window
  (``--since`` / ``--until`` / ``--days``) or one project (``--cwd``), and prints one compact
  digest across all of them: a session table, per-skill aggregates, subagent cost by role,
  tripwires and errors that recur, and the user turns inside skill runs. It is a map of where
  to look; drill into one session with ``--session``.
* **One session** (``--session <id|path>``, or ``--current`` for the newest transcript of this
  project). Reads the transcript plus the subagent transcripts stored next to it and prints a
  full Markdown digest:

* which skills were loaded, from where on disk, and how each invocation ended;
* per skill run: wall time, tool calls, errors — the evidence for "slow" or "thrashing";
* which subagents ran, at what duration / token / tool-call cost, and what each agent
  *type* cost in total (an `implementer` × 4 is one line, not four);
* per-tool usage, the slowest calls, and repetition signals (same command twice, same
  file read five times);
* every file the main thread wrote or edited — the write-scope evidence;
* tripwires for this skill set's own invariants: a branch created, a blanket `git add`,
  a push, a history rewrite, a non-English commit message, an AI-attribution trailer,
  an edit to a version-carrying manifest;
* every error, denial and API failure;
* the user's own turns verbatim (truncated) — where corrections and pushback live.

The digest is evidence, not judgement: `audit-skills` reads it and decides what it means.

Python 3 stdlib only. Reads; never writes.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from statistics import median

PROJECTS = Path.home() / ".claude" / "projects"
DEFAULT_PLUGIN = "dev-skills"
SELF = "audit-skills"  # its own runs don't make a session worth auditing

# ---------------------------------------------------------------- transcript discovery


def candidate_transcripts():
    """Every top-level session transcript, newest first. Subagent files live one level
    deeper (<session-id>/subagents/) and are deliberately not matched here."""
    if not PROJECTS.is_dir():
        return []
    files = [p for p in PROJECTS.glob("*/*.jsonl") if p.is_file()]
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return files


def peek(path, keys=("cwd", "sessionId", "gitBranch", "version"), limit=60):
    """Pull the first value seen for each key from the head of a transcript."""
    out = {}
    try:
        with path.open(errors="replace") as fh:
            for i, line in enumerate(fh):
                if i >= limit or len(out) == len(keys):
                    break
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except ValueError:
                    continue
                for k in keys:
                    if k not in out and row.get(k):
                        out[k] = row[k]
    except OSError:
        pass
    return out


def find_transcript(session, cwd):
    """--session wins (id or path); otherwise the newest transcript whose cwd matches."""
    if session:
        p = Path(session).expanduser()
        if p.is_file():
            return p
        hits = sorted(  # a full id, or the short prefix the cross-session digest prints
            PROJECTS.glob(f"*/{session}*.jsonl"),
            key=lambda q: q.stat().st_mtime,
            reverse=True,
        )
        if len({h.stem for h in hits}) > 1:
            sys.exit(f"session prefix '{session}' is ambiguous: " + ", ".join(sorted({h.stem for h in hits})))
        if hits:
            return hits[0]
        sys.exit(f"no transcript found for session '{session}'")

    target = str(Path(cwd or os.getcwd()).resolve())
    for path in candidate_transcripts():
        if peek(path).get("cwd") == target:
            return path
    sys.exit(
        f"no transcript found for cwd '{target}'.\n"
        "Run with --list to see what is available, or pass --session <id|path>."
    )


SLASH = re.compile(r"<command-name>/?([^<\s]+)</command-name>")


def invoked_names(row):
    """Skill names a single transcript row invokes: the model's `Skill` calls, the user's typed
    `/<name>` commands, and the harness's `invoked_skills` attachment."""
    names = []
    if row.get("isSidechain"):
        return names
    for b in blocks(row):
        if b.get("type") == "tool_use" and b.get("name") == "Skill":
            names.append(str((b.get("input") or {}).get("skill") or ""))
        elif b.get("type") == "text" and row.get("type") == "user":
            names += [m.lstrip("/") for m in SLASH.findall(b.get("text") or "")]
    att = row.get("attachment") or {}
    if att.get("type") == "invoked_skills":
        names += [s.get("name") or "" for s in att.get("skills") or []]
    return names


def ran_plugin(path, plugin):
    """True when a skill of `plugin` (other than this auditor) actually ran in the transcript.
    A raw substring pass first — most transcripts never mention the plugin — then a parse of
    only the lines that do, so a grep result or a pasted name never counts as a run."""
    needle = (plugin + ":").encode()
    try:
        data = path.read_bytes()
    except OSError:
        return False
    if needle not in data:
        return False
    for line in data.splitlines():
        if needle not in line:
            continue
        try:
            row = json.loads(line)
        except ValueError:
            continue
        for name in invoked_names(row):
            if name.startswith(plugin + ":") and name.split(":")[-1] != SELF:
                return True
    return False


def local_day(text):
    try:
        return datetime.strptime(text, "%Y-%m-%d").astimezone()
    except ValueError:
        sys.exit(f"bad date '{text}' — use YYYY-MM-DD")


def window_bounds(args):
    since = local_day(args.since) if args.since else None
    if args.days:
        since = datetime.now().astimezone() - timedelta(days=args.days)
    until = local_day(args.until) + timedelta(days=1) if args.until else None
    return since, until


def discover(plugin, since, until, cwd):
    """Transcripts in which the plugin ran, oldest first, plus how many were scanned and the
    oldest transcript still on disk (Claude Code deletes them after `cleanupPeriodDays`)."""
    target = str(Path(cwd).resolve()) if cwd else None
    found, scanned, oldest = [], 0, None
    for path in candidate_transcripts():
        mtime = datetime.fromtimestamp(path.stat().st_mtime).astimezone()
        oldest = mtime if oldest is None or mtime < oldest else oldest
        if since and mtime < since:  # last activity before the window opened
            continue
        if target and peek(path).get("cwd") != target:
            continue
        scanned += 1
        if ran_plugin(path, plugin):
            found.append(path)
    found.sort(key=lambda p: p.stat().st_mtime)
    return found, scanned, oldest


def list_sessions(plugin, since, until, cwd):
    found, scanned, _ = discover(plugin, since, until, cwd)
    listed = []
    for path in found:
        rows = load_rows(path)
        stamps = [r["_ts"] for r in rows if r["_ts"]]
        if not stamps or (until and min(stamps) >= until):
            continue
        names = {n.split(":")[-1] for r in rows for n in invoked_names(r) if n.startswith(plugin + ":")}
        listed.append((min(stamps), max(stamps), peek(path), path, names))
    listed.sort(key=lambda x: x[0])
    print("started              last active          session                               project  —  skills\n")
    for start, last, info, path, names in listed:
        print(
            f"  {full_ts(start)}  {full_ts(last)}  {info.get('sessionId', path.stem)}  "
            f"{Path(info.get('cwd', '?')).name}  —  {', '.join(sorted(names)) or '—'}"
        )
    print(f"\n{len(listed)} session(s) ran `{plugin}:` skills ({scanned} transcripts scanned).")


# ---------------------------------------------------------------- loading


def load_rows(path):
    """Parse a transcript, drop duplicate uuids (forks re-append history), order by time."""
    rows, seen = [], set()
    with path.open(errors="replace") as fh:
        for i, line in enumerate(fh):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except ValueError:
                continue
            uid = row.get("uuid")
            if uid:
                if uid in seen:
                    continue
                seen.add(uid)
            row["_i"] = i
            rows.append(row)

    # rows without a timestamp (attachments, queue ops) inherit the previous one
    last = None
    for row in rows:
        ts = parse_ts(row.get("timestamp"))
        if ts is None:
            ts = last
        else:
            last = ts
        row["_ts"] = ts
    known = [r for r in rows if r["_ts"] is not None]
    floor = min((r["_ts"] for r in known), default=None)
    for row in rows:
        if row["_ts"] is None:
            row["_ts"] = floor
    rows.sort(key=lambda r: (r["_ts"] or datetime.min, r["_i"]))
    return rows


def parse_ts(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def blocks(row):
    msg = row.get("message") or {}
    content = msg.get("content")
    if isinstance(content, list):
        return [b for b in content if isinstance(b, dict)]
    if isinstance(content, str):
        return [{"type": "text", "text": content}]
    return []


# ---------------------------------------------------------------- formatting helpers

REMINDER = re.compile(r"<system-reminder>.*?</system-reminder>", re.S)
COMMAND = re.compile(r"<command-(name|message|args)>(.*?)</command-\1>", re.S)
NOISE = re.compile(
    r"\s*(?:<task-notification>|<local-command-caveat>|<local-command-stdout>|<ide_opened_file>"
    r"|<ide_selection>|Caveat: The messages below|Stop hook feedback:"
    r"|Base directory for this skill:"
    r"|This session is being continued from a previous conversation)",
    re.S,
)
INTERRUPT = re.compile(r"\[Request interrupted by user", re.I)


def clean_text(text):
    text = REMINDER.sub("", text or "")
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def cut(text, n=160):
    text = " ".join(str(text or "").split())
    return text if len(text) <= n else text[: n - 1] + "…"


def fmt_dur(ms):
    if ms is None:
        return "—"
    s = ms / 1000.0
    if s < 60:
        return f"{s:.1f}s"
    m, s = divmod(int(s), 60)
    if m < 60:
        return f"{m}m {s:02d}s"
    h, m = divmod(m, 60)
    return f"{h}h {m:02d}m {s:02d}s"


MULTIDAY = False  # set once the session's span is known; adds the date to every stamp


def hhmmss(ts):
    if not ts:
        return "—"
    return ts.astimezone().strftime("%m-%d %H:%M:%S" if MULTIDAY else "%H:%M:%S")


def full_ts(ts):
    return ts.astimezone().strftime("%Y-%m-%d %H:%M:%S") if ts else "—"


def table(header, rows):
    if not rows:
        return ["_(none)_", ""]
    out = ["| " + " | ".join(header) + " |", "|" + "|".join(["---"] * len(header)) + "|"]
    out += ["| " + " | ".join(str(c).replace("|", "\\|") for c in r) + " |" for r in rows]
    out.append("")
    return out


def input_key(name, payload):
    """A stable identity for a tool call, used to spot repeats."""
    if not isinstance(payload, dict):
        return cut(payload, 200)
    for field in ("command", "file_path", "pattern", "path", "url", "skill", "prompt"):
        if field in payload:
            return f"{field}={cut(payload[field], 200)}"
    return cut(json.dumps(payload, ensure_ascii=False, sort_keys=True), 200)


# ---------------------------------------------------------------- invariant tripwires
#
# The dev-skills set states a few invariants about itself: one branch (the current one),
# commit messages in English, no attribution trailers, the plugin version is the user's to
# bump. A tripwire is a *signal*, never a verdict — the user may have asked for the branch,
# and `git rebase` may be exactly what was wanted. The audit reads the surrounding
# conversation before calling any of these a finding.

CYRILLIC = re.compile(r"[А-Яа-яЁё]")

TRIPWIRES = (
    ("branch / worktree created", re.compile(r"\bgit\s+(?:checkout\s+-b|switch\s+-c|worktree\s+add|branch\s+(?!-[dDlvra-]))")),
    ("blanket staging", re.compile(r"\bgit\s+add\s+(?:-A\b|--all\b|\.\s*$|\.\s+)")),
    ("push", re.compile(r"\bgit\s+push\b")),
    ("history rewrite", re.compile(r"\bgit\s+(?:commit[^|;&]*--amend|rebase\b|reset\s+--hard|push[^|;&]*--force)")),
    ("AI attribution trailer", re.compile(r"Co-Authored-By:\s*Claude|Generated with \[Claude", re.I)),
)

MANIFEST = re.compile(r"/\.claude-plugin/(?:plugin|marketplace)\.json$")


HEREDOC = re.compile(r"<<-?\s*['\"]?(\w+)['\"]?[^\n]*\n(.*?)\n\s*\1\b", re.S)
QUOTED = re.compile(r"\"[^\"\n]*\"|«[^»]*»|“[^”]*”|`[^`\n]*`")  # quoted product text is not the message's language
MESSAGE_ARG = re.compile(r"\s(?:-m|--message)(?:\s+|=)(?:\"((?:[^\"\\]|\\.)*)\"|'([^']*)')")


def commit_message(cmd):
    """The message text of a `git commit` in a shell command — the heredoc body or the -m
    arguments — so Cyrillic in a neighbouring `echo` doesn't count as the message."""
    if not re.search(r"\bgit\s+commit\b", cmd):
        return ""
    tail = cmd[re.search(r"\bgit\s+commit\b", cmd).start():]
    parts = [m.group(2) for m in HEREDOC.finditer(tail)]
    parts += [a or b for a, b in MESSAGE_ARG.findall(tail)]
    return "\n".join(parts)


def tripwires(calls):
    """Bash commands that touch one of the set's stated invariants, in time order."""
    hits = []
    for c in calls:
        if c["name"] != "Bash":
            continue
        cmd = (c["input"] or {}).get("command") or ""
        for label, rx in TRIPWIRES:
            if rx.search(cmd):
                hits.append((c, label, cmd))
        if CYRILLIC.search(QUOTED.sub("", commit_message(cmd))):
            hits.append((c, "non-English commit message", cmd))
    return hits


# ---------------------------------------------------------------- background agents
#
# An agent launched in the background returns `status: async_launched` at once; its real
# outcome and cost arrive later in a <task-notification> (a queued_command attachment, or the
# text of a user turn), keyed by the same id.

NOTE_ID = re.compile(r"<task-id>\s*([^<\s]+)\s*</task-id>")
NOTE_STATUS = re.compile(r"<status>\s*([^<\s]+)\s*</status>")
NOTE_NUM = {
    "tokens": re.compile(r"(?:totalTokens'?\"?:\s*|<subagent_tokens>\s*)(\d+)"),
    "ms": re.compile(r"(?:durationMs'?\"?:\s*|<duration_ms>\s*)(\d+)"),
    "tools": re.compile(r"(?:toolUses'?\"?:\s*|<tool_uses>\s*)(\d+)"),
}


def notifications(rows):
    """task id → the last reported {status, ms, tokens, tools} for background agents."""
    notes = {}
    for row in rows:
        texts = []
        att = row.get("attachment") or {}
        if att.get("commandMode") == "task-notification":
            texts.append(f"{att.get('prompt') or ''} {att.get('usage') or ''}")
        if row.get("type") == "user":
            texts += [b.get("text", "") for b in blocks(row) if b.get("type") == "text" and "<task-notification>" in b.get("text", "")]
        for text in texts:
            tid = NOTE_ID.search(text)
            if not tid:
                continue
            note = notes.setdefault(tid.group(1), {})
            status = NOTE_STATUS.search(text)
            if status:
                note["status"] = status.group(1)
            for key, rx in NOTE_NUM.items():
                m = rx.search(text)
                if m:
                    note[key] = int(m.group(1))
    return notes


def agent_result(call, notes):
    """The Agent/Task result with a background agent's later notification merged in."""
    res = dict(call["result"]) if isinstance(call["result"], dict) else {}
    if res.get("status") == "async_launched":
        note = notes.get(res.get("agentId") or "", {})
        res["status"] = note.get("status", "background — no result in transcript")
        res["totalDurationMs"] = note.get("ms")
        res["totalTokens"] = note.get("tokens")
        res["totalToolUseCount"] = note.get("tools")
    return res


def run_end(start, next_start, stamps, idle_ms):
    """Where a skill run stops: the next skill invocation, or the first stretch of silence
    longer than `idle_ms` (the user walked away; whatever follows is a new piece of work)."""
    prev = start
    for ts in stamps:
        if ts <= start:
            continue
        if next_start and ts >= next_start:
            return next_start
        if (ts - prev).total_seconds() * 1000 > idle_ms:
            return prev
        prev = ts
    return next_start or prev


# ---------------------------------------------------------------- extraction


def collect_calls(rows):
    """tool_use blocks paired with their tool_result, in time order."""
    calls, by_id = [], {}
    for row in rows:
        for b in blocks(row):
            if b.get("type") == "tool_use":
                call = {
                    "id": b.get("id"),
                    "name": b.get("name") or "?",
                    "input": b.get("input") or {},
                    "ts": row["_ts"],
                    "end": None,
                    "ms": None,
                    "error": None,
                    "result": None,
                }
                calls.append(call)
                if call["id"]:
                    by_id[call["id"]] = call

    for row in rows:
        for b in blocks(row):
            if b.get("type") != "tool_result":
                continue
            call = by_id.get(b.get("tool_use_id"))
            if not call:
                continue
            call["end"] = row["_ts"]
            if call["ts"] and row["_ts"]:
                call["ms"] = (row["_ts"] - call["ts"]).total_seconds() * 1000
            call["result"] = row.get("toolUseResult")
            if b.get("is_error"):
                content = b.get("content")
                text = content if isinstance(content, str) else json.dumps(content, ensure_ascii=False)
                call["error"] = cut(text, 300)
    return calls


def collect_skills(rows):
    """Skills whose body was actually loaded — name, origin, base directory on disk."""
    loaded = {}
    for row in rows:
        att = row.get("attachment") or {}
        if row.get("type") != "attachment" or att.get("type") != "invoked_skills":
            continue
        for skill in att.get("skills") or []:
            name = skill.get("name")
            if not name:
                continue
            content = skill.get("content") or ""
            match = re.match(r"Base directory for this skill:\s*(\S.*)", content)
            entry = loaded.setdefault(name, {"name": name, "path": skill.get("path"), "dir": None, "chars": len(content)})
            if match and not entry["dir"]:
                entry["dir"] = match.group(1).strip()
            entry["chars"] = max(entry["chars"], len(content))
    for entry in loaded.values():
        if entry["dir"] and (Path(entry["dir"]) / "SKILL.md").is_file():
            entry["file"] = str(Path(entry["dir"]) / "SKILL.md")
        else:
            entry["file"] = resolve_source(entry["name"], entry["path"])
            entry["guessed"] = bool(entry["file"])
    return loaded


def resolve_source(name, origin=None):
    """Find the file a skill (or the slash command behind it) was defined in.

    `origin` is the transcript's own label — `plugin:<plugin>:<skill>`,
    `userSettings:<skill>`, `projectSettings:<skill>` — and decides which candidate wins
    when the same name exists in several places."""
    leaf = name.split(":")[-1]
    home = Path.home() / ".claude"
    origin = origin or ""
    parts = origin.split(":")
    plugin = parts[1] if origin.startswith("plugin:") and len(parts) >= 3 else None

    cands = []
    if origin.startswith("userSettings"):
        cands += [home / "skills" / leaf / "SKILL.md", home / "commands" / f"{leaf}.md"]
    if origin.startswith("projectSettings"):
        base = Path.cwd() / ".claude"
        cands += [base / "skills" / leaf / "SKILL.md", base / "commands" / f"{leaf}.md"]
    for root in (home / "plugins" / "marketplaces", home / "plugins" / "cache"):
        if not root.is_dir():
            continue
        for prefix in ("*", "*/*", "*/*/*"):
            cands += sorted(root.glob(f"{prefix}/skills/{leaf}/SKILL.md"))[:8]
            cands += sorted(root.glob(f"{prefix}/commands/{leaf}.md"))[:8]
    cands += [
        home / "skills" / leaf / "SKILL.md",
        Path.cwd() / ".claude" / "skills" / leaf / "SKILL.md",
        home / "commands" / f"{leaf}.md",
        Path.cwd() / ".claude" / "commands" / f"{leaf}.md",
    ]
    if plugin:  # stable sort: a path carrying the plugin's own name wins
        cands.sort(key=lambda p: 0 if f"/{plugin}/" in str(p) else 1)

    for candidate in cands:
        if candidate.is_file():
            return str(candidate)
    return None


def user_turns(rows, max_chars):
    """Real user turns only — harness chatter (task notifications, IDE events, hook
    output, compaction summaries) is dropped, but interrupts are kept: they mark
    exactly where the user stopped a skill mid-run."""
    turns, dropped = [], 0
    for row in rows:
        if row.get("type") != "user" or row.get("isSidechain"):
            continue
        parts = [b.get("text", "") for b in blocks(row) if b.get("type") == "text"]
        if not parts:
            continue
        text = clean_text("\n".join(parts))
        cmd = COMMAND.findall(text)
        if cmd:
            text = " ".join(
                "/" + v.strip().lstrip("/") if k == "name" else v.strip() for k, v in cmd if v.strip()
            )
        if not text:
            continue
        if NOISE.match(text):
            dropped += 1
            continue
        turns.append({"ts": row["_ts"], "text": text[:max_chars] + ("…" if len(text) > max_chars else "")})
    return turns, dropped


def subagent_dir(transcript):
    d = transcript.parent / transcript.stem / "subagents"
    return d if d.is_dir() else None


def read_subagent(path):
    """Tool mix and skill usage inside one subagent transcript."""
    tools, skills, turns = Counter(), set(), 0
    try:
        for line in path.open(errors="replace"):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except ValueError:
                continue
            turns += 1
            for b in blocks(row):
                if b.get("type") == "tool_use":
                    tools[b.get("name") or "?"] += 1
                    if b.get("name") == "Skill":
                        skills.add((b.get("input") or {}).get("skill", "?"))
            att = row.get("attachment") or {}
            if att.get("type") == "invoked_skills":
                skills.update(s.get("name") for s in att.get("skills") or [] if s.get("name"))
    except OSError:
        pass
    return tools, sorted(skills), turns


# ---------------------------------------------------------------- report


def build(transcript, rows, args):
    global MULTIDAY
    out = []
    calls = collect_calls(rows)
    skills = collect_skills(rows)
    turns, muted = user_turns(rows, args.max_user_chars)
    interrupts = sum(1 for t in turns if INTERRUPT.search(t["text"]))
    head = peek(transcript)

    stamps = [r["_ts"] for r in rows if r["_ts"]]
    start, end = (min(stamps), max(stamps)) if stamps else (None, None)
    span = (end - start).total_seconds() * 1000 if start and end else None
    MULTIDAY = bool(start and end and start.astimezone().date() != end.astimezone().date())
    compactions = sum(1 for r in rows if r.get("type") == "system" and r.get("subtype") == "compact_boundary")
    api_errors = sum(1 for r in rows if r.get("type") == "system" and r.get("subtype") == "api_error")

    # ---- header
    out += [
        "# Session digest",
        "",
        f"- **transcript**: `{transcript}`",
        f"- **session**: `{head.get('sessionId', transcript.stem)}`",
        f"- **cwd**: `{head.get('cwd', '?')}`  ·  **branch**: `{head.get('gitBranch') or '—'}`"
        f"  ·  **cli**: `{head.get('version', '?')}`",
        f"- **window**: {full_ts(start)} → {full_ts(end)} ({fmt_dur(span)})",
        f"- **turns**: {len(turns)} user · {sum(1 for r in rows if r.get('type') == 'assistant')} assistant"
        f" · {len(calls)} tool calls",
        f"- **compactions**: {compactions}  ·  **api errors**: {api_errors}"
        f"  ·  **user interrupts**: {interrupts}",
        "",
    ]
    if compactions:
        out += [
            "> The conversation was compacted — turns before the boundary survive only in this",
            "> transcript, not in the agent's context.",
            "",
        ]

    # ---- skills
    out += ["## Skills loaded", ""]
    out += table(
        ["skill", "origin", "source file", "body chars"],
        [
            [
                s["name"],
                s["path"] or "—",
                (s["file"] or "not found on disk")
                + (" ⚠︎ found by search — check the name in its frontmatter" if s.get("guessed") else ""),
                s["chars"],
            ]
            for s in skills.values()
        ],
    )

    skill_calls = [c for c in calls if c["name"] == "Skill"]
    out += ["### Skill invocations", ""]
    out += table(
        ["at", "skill", "args", "outcome"],
        [
            [
                hhmmss(c["ts"]),
                (c["input"] or {}).get("skill", "?"),
                cut((c["input"] or {}).get("args"), 80) or "—",
                "ERROR: " + cut(c["error"], 120) if c["error"] else "ok",
            ]
            for c in skill_calls
        ],
    )
    never_called = [n for n in skills if not any((c["input"] or {}).get("skill") == n for c in skill_calls)]
    if never_called:
        out += [
            "Loaded without a `Skill` tool call (typed as `/<name>` by the user, or injected): "
            + ", ".join(f"`{n}`" for n in never_called),
            "",
        ]

    # ---- what each skill run did
    if skill_calls:
        out += [
            "### What each skill run did",
            "",
            "_A run spans from its invocation to the next skill invocation. User turns inside the span"
            " are the back-and-forth the skill needed to get through._",
            "",
        ]
    starts = sorted(c["ts"] for c in skill_calls if c["ts"])
    for c in skill_calls[: args.top]:
        if not c["ts"]:
            continue
        stop = run_end(c["ts"], next((b for b in starts if b > c["ts"]), None), stamps, args.idle * 60000)
        window = [x for x in calls if x["ts"] and c["ts"] <= x["ts"] < (stop or end) and x["name"] != "Skill"]
        mix = Counter(x["name"] for x in window)
        errs = [x for x in window if x["error"]]
        asked = sum(1 for t in turns if t["ts"] and c["ts"] < t["ts"] < (stop or end))
        wall = (stop - c["ts"]).total_seconds() * 1000 if stop else None
        name = (c["input"] or {}).get("skill", "?")
        out += [
            f"**{hhmmss(c['ts'])} · `{name}`** — until {hhmmss(stop)} ({fmt_dur(wall)}), "
            f"{len(window)} tool calls, {len(errs)} errored, {asked} user turns"
            + (f" · {', '.join(f'{k}×{v}' for k, v in mix.most_common(6))}" if mix else ""),
        ]
        for x in errs[:3]:
            out += [f"    - error in `{x['name']}` at {hhmmss(x['ts'])}: {cut(x['error'], 140)}"]
    out += [""]

    # ---- subagents
    out += ["## Subagents", ""]
    agent_calls = [c for c in calls if c["name"] in ("Agent", "Task")]
    notes = notifications(rows)
    rows_out = []
    details = []
    for c in agent_calls:
        res = agent_result(c, notes)
        stats = res.get("toolStats") if isinstance(res.get("toolStats"), dict) else {}
        rows_out.append(
            [
                hhmmss(c["ts"]),
                res.get("agentType") or (c["input"] or {}).get("subagent_type", "?"),
                cut((c["input"] or {}).get("description"), 40) or "—",
                res.get("status") or ("error" if c["error"] else "?"),
                fmt_dur(res.get("totalDurationMs") if res.get("isAsync") else (res.get("totalDurationMs") or c["ms"])),
                res.get("totalTokens") or "—",
                res.get("totalToolUseCount") or "—",
                res.get("resolvedModel") or "—",
            ]
        )
        details.append((c, res, stats))
    out += table(
        ["at", "agent", "description", "status", "duration", "tokens", "tool calls", "model"], rows_out
    )

    if len(details) > 1:
        by_type = defaultdict(lambda: {"n": 0, "ms": 0.0, "tok": 0, "tools": 0})
        for c, res, _ in details:
            key = res.get("agentType") or (c["input"] or {}).get("subagent_type", "?")
            a = by_type[key]
            a["n"] += 1
            a["ms"] += res.get("totalDurationMs") or (0 if res.get("isAsync") else c["ms"]) or 0
            a["tok"] += res.get("totalTokens") or 0
            a["tools"] += res.get("totalToolUseCount") or 0
        out += ["### Cost by agent type", ""]
        out += table(
            ["agent", "runs", "total duration", "total tokens", "tool calls"],
            [
                [k, v["n"], fmt_dur(v["ms"]), v["tok"] or "—", v["tools"] or "—"]
                for k, v in sorted(by_type.items(), key=lambda kv: kv[1]["ms"], reverse=True)
            ],
        )
        out += ["_The same role run N times is where a per-run inefficiency multiplies._", ""]

    sub_dir = subagent_dir(transcript)
    if sub_dir:
        out += [f"Subagent transcripts: `{sub_dir}/agent-<id>.jsonl` — read one to see what an agent actually did.", ""]
        for c, res, stats in details[: args.top]:
            agent_id = res.get("agentId")
            if not agent_id:
                continue
            path = sub_dir / f"agent-{agent_id}.jsonl"
            if not path.is_file():
                continue
            tools, used_skills, turn_count = read_subagent(path)
            line = (
                f"- `{res.get('agentType', '?')}` (`{path.name}`, {turn_count} rows)"
                f" — {', '.join(f'{k}×{v}' for k, v in tools.most_common(8)) or 'no tool calls'}"
            )
            if used_skills:
                line += f" · skills: {', '.join(used_skills)}"
            if stats:
                line += f" · {', '.join(f'{k}={v}' for k, v in stats.items() if v)}"
            out += [line]
        out += [""]

    # ---- tools
    out += ["## Tool usage (main thread)", ""]
    agg = defaultdict(lambda: {"n": 0, "err": 0, "ms": 0.0, "max": 0.0, "slowest": ""})
    for c in calls:
        a = agg[c["name"]]
        a["n"] += 1
        a["err"] += 1 if c["error"] else 0
        if c["ms"]:
            a["ms"] += c["ms"]
            if c["ms"] > a["max"]:
                a["max"] = c["ms"]
                a["slowest"] = input_key(c["name"], c["input"])
    out += table(
        ["tool", "calls", "errors", "total wall", "slowest", "slowest call"],
        [
            [k, v["n"], v["err"], fmt_dur(v["ms"]), fmt_dur(v["max"]), cut(v["slowest"], 70)]
            for k, v in sorted(agg.items(), key=lambda kv: kv[1]["ms"], reverse=True)
        ],
    )

    slow = sorted([c for c in calls if c["ms"]], key=lambda c: c["ms"], reverse=True)[: args.top]
    out += ["### Slowest individual calls", ""]
    out += table(
        ["at", "tool", "duration", "call"],
        [[hhmmss(c["ts"]), c["name"], fmt_dur(c["ms"]), cut(input_key(c["name"], c["input"]), 90)] for c in slow],
    )

    # ---- repetition
    out += ["## Repetition signals", ""]
    repeats = Counter((c["name"], input_key(c["name"], c["input"])) for c in calls)
    dupes = [(k, n) for k, n in repeats.most_common() if n > 1][: args.top]
    if dupes:
        out += table(
            ["tool", "repeats", "call"], [[k[0], n, cut(k[1], 90)] for k, n in dupes]
        )
        out += ["_Identical calls repeated across the session — a skill re-deriving what it already knew._", ""]
    else:
        out += ["_No identical tool call was made twice._", ""]

    reads = Counter(
        (c["input"] or {}).get("file_path") for c in calls if c["name"] == "Read" and (c["input"] or {}).get("file_path")
    )
    heavy = [(f, n) for f, n in reads.most_common() if n >= 3][:10]
    if heavy:
        out += ["Files read 3+ times: " + ", ".join(f"`{f}` ×{n}" for f, n in heavy), ""]

    # ---- writes
    out += [
        "## Files written (main thread)",
        "",
        "_What the session actually changed — check it against the write scope each skill claims._",
        "",
    ]
    writes = defaultdict(Counter)
    for c in calls:
        if c["name"] not in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
            continue
        path = (c["input"] or {}).get("file_path") or (c["input"] or {}).get("notebook_path")
        if path:
            writes[path][c["name"]] += 1
    out += table(
        ["file", "edits", "how", "note"],
        [
            [
                path,
                sum(mix.values()),
                ", ".join(f"{k}×{v}" for k, v in mix.most_common()),
                "⚠︎ version-carrying manifest" if MANIFEST.search(path) else "",
            ]
            for path, mix in sorted(writes.items(), key=lambda kv: sum(kv[1].values()), reverse=True)[: args.top * 2]
        ],
    )
    if len(writes) > args.top * 2:
        out += [f"_… and {len(writes) - args.top * 2} more files written._", ""]

    # ---- invariants
    out += [
        "## Invariant tripwires",
        "",
        "_Signals, not verdicts — the user may have asked for exactly this. Read the conversation "
        "around each one before calling it a finding._",
        "",
    ]
    hits = tripwires(calls)
    out += table(
        ["at", "tripwire", "command"],
        [[hhmmss(c["ts"]), label, cut(cmd, 100)] for c, label, cmd in hits[: args.top]],
    )
    if len(hits) > args.top:
        out += [f"_… and {len(hits) - args.top} more tripped commands._", ""]

    # ---- friction
    out += ["## Errors, denials and retries", ""]
    errored = [c for c in calls if c["error"]]
    out += table(
        ["at", "tool", "error", "call"],
        [
            [hhmmss(c["ts"]), c["name"], cut(c["error"], 110), cut(input_key(c["name"], c["input"]), 60)]
            for c in errored[: args.top * 2]
        ],
    )
    if len(errored) > args.top * 2:
        out += [f"_… and {len(errored) - args.top * 2} more errored calls._", ""]

    hooks = Counter()
    for row in rows:
        att = row.get("attachment") or {}
        if row.get("type") == "attachment" and att.get("type") == "hook_non_blocking_error":
            hooks[(att.get("hookName") or "?", cut(att.get("stderr") or att.get("message"), 140))] += 1
    if hooks:
        out += ["Hook errors (grouped):"]
        out += [f"- `{name}` ×{n} — {msg}" for (name, msg), n in hooks.most_common(10)]
        out += [""]

    # ---- user turns
    out += [
        "## User turns (verbatim)",
        "",
        "_Where the user corrects, repeats, rephrases or interrupts is where a skill misfired._",
        "",
    ]
    for t in turns:
        text = t["text"].replace("\n", "\n  ")
        out += [f"- **{hhmmss(t['ts'])}** — {text}"]
    out += ["", f"_({muted} harness messages — task notifications, IDE events, hook output — omitted.)_", ""]

    return "\n".join(out)


# ---------------------------------------------------------------- cross-session digest

CORRECTION = re.compile(
    r"^\W*(?:нет\b|не\s+(?:так|надо|нужно|то)\b|стоп|подожди|зачем|почему|опять|снова|неправильн"
    r"|ты\s+(?:не|опять|зачем)\b|no\b|nope|stop\b|wait\b|why\b|don'?t\b|wrong|again\b|that'?s not)",
    re.I,
)
VERSION = re.compile(r"/(\d+\.\d+\.\d+)/skills/")


def norm_error(text):
    """Collapse paths, ids and numbers so the same failure in two sessions groups together."""
    text = re.sub(r"(?:~|/)[\w.@~-]*(?:/[\w.@~-]+)+", "<path>", text or "")
    text = re.sub(r"\b[0-9a-f]{8,}\b", "<id>", text)
    return cut(re.sub(r"\d+", "#", text), 110)


def summarize(path, rows, plugin, args):
    """Everything the cross-session digest needs from one transcript."""
    calls = collect_calls(rows)
    turns, _ = user_turns(rows, args.max_user_chars)
    loaded = collect_skills(rows)
    head = peek(path)
    stamps = sorted(r["_ts"] for r in rows if r["_ts"])
    start, end = stamps[0], stamps[-1]
    sid = str(head.get("sessionId", path.stem))

    # where the plugin's skills were loaded from: an installed version or a local checkout
    sources = {e["dir"] for n, e in loaded.items() if n.startswith(plugin + ":") and e.get("dir")}
    versions = sorted({m.group(1) for d in sources for m in [VERSION.search(d + "/")] if m})
    loaded_from = ", ".join(versions) if versions else ("local checkout" if sources else "—")

    events = []
    for c in calls:
        if c["name"] == "Skill" and c["ts"]:
            events.append({"ts": c["ts"], "skill": str((c["input"] or {}).get("skill") or "?"),
                           "via": "tool", "error": c["error"]})
    for row in rows:
        if row.get("type") == "user" and not row.get("isSidechain") and row["_ts"]:
            for b in blocks(row):
                if b.get("type") == "text":
                    for m in SLASH.findall(b.get("text") or ""):
                        name = m.lstrip("/")
                        if name.startswith(plugin + ":") or name in loaded:
                            events.append({"ts": row["_ts"], "skill": name, "via": "typed", "error": None})
    events.sort(key=lambda e: e["ts"])
    deduped = []
    for e in events:  # a typed command and its own load can both appear — keep one
        if deduped and deduped[-1]["skill"] == e["skill"] and (e["ts"] - deduped[-1]["ts"]).total_seconds() < 5:
            continue
        deduped.append(e)
    bounds = [e["ts"] for e in deduped]

    runs = []
    since, until = getattr(args, "window", (None, None))
    for e in deduped:
        if not e["skill"].startswith(plugin + ":"):
            continue
        if (since and e["ts"] < since) or (until and e["ts"] >= until):
            continue  # a long session overlaps the window; only its runs inside it count
        stop = run_end(e["ts"], next((b for b in bounds if b > e["ts"]), None), stamps, args.idle * 60000)
        window = [x for x in calls if x["ts"] and e["ts"] <= x["ts"] < stop and x["name"] != "Skill"]
        inside = [t for t in turns if t["ts"] and e["ts"] < t["ts"] < stop]
        runs.append({
            "skill": e["skill"].split(":", 1)[1], "ts": e["ts"], "via": e["via"], "error": e["error"],
            "ms": (stop - e["ts"]).total_seconds() * 1000, "calls": len(window),
            "errors": [x for x in window if x["error"]], "turns": inside,
        })

    agents = []
    notes = notifications(rows)
    for c in calls:
        if c["name"] not in ("Agent", "Task"):
            continue
        res = agent_result(c, notes)
        agents.append({
            "type": res.get("agentType") or (c["input"] or {}).get("subagent_type") or "general-purpose",
            "status": res.get("status") or ("error" if c["error"] else "?"),
            "ms": res.get("totalDurationMs") or (0 if res.get("isAsync") else c["ms"]) or 0,
            "tokens": res.get("totalTokens") or 0,
            "model": res.get("resolvedModel") or "—",
        })

    hooks = Counter()
    for row in rows:
        att = row.get("attachment") or {}
        if row.get("type") == "attachment" and att.get("type") == "hook_non_blocking_error":
            hooks[(att.get("hookName") or "?", norm_error(att.get("stderr") or att.get("message")))] += 1

    return {
        "sid": sid, "short": sid[:8], "project": Path(head.get("cwd", "?")).name, "start": start, "end": end,
        "loaded_from": loaded_from, "runs": runs, "agents": agents, "turns": turns,
        "interrupts": sum(1 for t in turns if INTERRUPT.search(t["text"])),
        "compactions": sum(1 for r in rows if r.get("type") == "system" and r.get("subtype") == "compact_boundary"),
        "api_errors": sum(1 for r in rows if r.get("type") == "system" and r.get("subtype") == "api_error"),
        "errors": [c for c in calls if c["error"]], "tripwires": tripwires(calls), "hooks": hooks,
    }


def flagged(text):
    return bool(INTERRUPT.search(text) or CORRECTION.search(text))


def build_multi(sessions, plugin, scanned, oldest, since, until, args):
    global MULTIDAY
    MULTIDAY = True
    out = []
    runs = [(s, r) for s in sessions for r in s["runs"]]
    projects = {s["project"] for s in sessions}
    agents = [(s, a) for s in sessions for a in s["agents"]]

    out += [
        f"# Cross-session digest — `{plugin}`",
        "",
        f"- **window**: {full_ts(since) if since else 'everything on disk'} → {full_ts(until) if until else 'now'}"
        f"  ·  oldest transcript on disk: {full_ts(oldest)}",
        "  _(Claude Code deletes transcripts older than `cleanupPeriodDays`, 30 days by default —"
        " nothing older can be audited.)_",
        f"- **sessions**: {len(sessions)} ran `{plugin}:` skills, across {len(projects)} project(s)"
        f"  ·  {scanned} transcripts scanned",
        f"- **skill runs**: {len(runs)} ({sum(1 for _, r in runs if r['via'] == 'tool')} by the model,"
        f" {sum(1 for _, r in runs if r['via'] == 'typed')} typed by the user)  ·  **subagents**: {len(agents)}"
        f"  ·  **compactions**: {sum(s['compactions'] for s in sessions)}"
        f"  ·  **user interrupts**: {sum(s['interrupts'] for s in sessions)}",
        "",
        "_A run spans from its invocation to the next skill invocation (or the session's end — so the"
        " last run of a session may include idle time). Older sessions may have run an older version of"
        " a skill: check the current file still carries the cause before proposing a fix._",
        "",
    ]

    # ---- sessions
    out += ["## Sessions", ""]
    out += table(
        ["#", "started", "session", "project", "span", "plugin", "skills run", "user turns", "interrupts",
         "compactions", "errors", "tripwires"],
        [
            [
                i, full_ts(s["start"]), s["short"], s["project"],
                fmt_dur((s["end"] - s["start"]).total_seconds() * 1000), s["loaded_from"],
                ", ".join(f"{k}×{v}" if v > 1 else k for k, v in Counter(r["skill"] for r in s["runs"]).most_common()),
                len(s["turns"]), s["interrupts"], s["compactions"], len(s["errors"]), len(s["tripwires"]),
            ]
            for i, s in enumerate(sessions, 1)
        ],
    )

    # ---- per skill
    out += ["## Per skill", "", "_Where to look first: many user turns, flagged turns or errors inside a skill's runs._", ""]
    by_skill = defaultdict(list)
    for s, r in runs:
        by_skill[r["skill"]].append((s, r))
    out += table(
        ["skill", "runs", "sessions", "typed", "invocation errors", "median wall", "longest", "median tool calls",
         "user turns inside", "⚑ flagged", "tool errors inside"],
        [
            [
                k, len(v), len({s["sid"] for s, _ in v}), sum(1 for _, r in v if r["via"] == "typed"),
                sum(1 for _, r in v if r["error"]), fmt_dur(median(r["ms"] for _, r in v)),
                fmt_dur(max(r["ms"] for _, r in v)), int(median(r["calls"] for _, r in v)),
                sum(len(r["turns"]) for _, r in v), sum(1 for _, r in v for t in r["turns"] if flagged(t["text"])),
                sum(len(r["errors"]) for _, r in v),
            ]
            for k, v in sorted(by_skill.items(), key=lambda kv: len(kv[1]), reverse=True)
        ],
    )

    # ---- subagents
    out += ["## Subagents by role", ""]
    by_type = defaultdict(list)
    for s, a in agents:
        by_type[a["type"]].append((s, a))
    out += table(
        ["agent", "runs", "sessions", "not completed", "no result", "median duration", "total duration", "total tokens", "models"],
        [
            [
                k, len(v), len({s["sid"] for s, _ in v}),
                sum(1 for _, a in v if a["status"] not in ("completed", "?") and not a["status"].startswith("background")),
                sum(1 for _, a in v if a["status"].startswith("background")),
                fmt_dur(median([a["ms"] for _, a in v if a["ms"]] or [0])), fmt_dur(sum(a["ms"] for _, a in v)),
                sum(a["tokens"] for _, a in v) or "—", ", ".join(sorted({a["model"] for _, a in v})),
            ]
            for k, v in sorted(by_type.items(), key=lambda kv: sum(a["ms"] for _, a in kv[1]), reverse=True)
        ],
    )
    out += ["_The same role run N times is where a per-run inefficiency multiplies._", ""]

    # ---- tripwires
    out += [
        "## Invariant tripwires",
        "",
        "_Signals, not verdicts — the user may have asked for exactly this. Drill into the session and read around it._",
        "",
    ]
    trip = defaultdict(list)
    for s in sessions:
        for c, label, cmd in s["tripwires"]:
            trip[label].append((s, c, cmd))
    out += table(
        ["tripwire", "hits", "sessions", "example"],
        [
            [label, len(v), len({s["sid"] for s, _, _ in v}), f"`{v[0][0]['short']}` {hhmmss(v[0][1]['ts'])} — {cut(v[0][2], 80)}"]
            for label, v in sorted(trip.items(), key=lambda kv: len(kv[1]), reverse=True)
        ],
    )

    # ---- errors
    out += ["## Recurring errors", "", "_Grouped with paths, ids and numbers collapsed; most widespread first._", ""]
    errs = defaultdict(list)
    for s in sessions:
        for c in s["errors"]:
            errs[norm_error(c["error"])].append((s, c))
    ranked = sorted(errs.items(), key=lambda kv: (len({s["sid"] for s, _ in kv[1]}), len(kv[1])), reverse=True)
    out += table(
        ["error", "hits", "sessions", "tools"],
        [
            [msg, len(v), len({s["sid"] for s, _ in v}), ", ".join(sorted({c["name"] for _, c in v}))]
            for msg, v in ranked[: args.top * 2]
        ],
    )
    if len(ranked) > args.top * 2:
        out += [f"_… and {len(ranked) - args.top * 2} more distinct errors._", ""]

    hooks = Counter()
    for s in sessions:
        hooks.update(s["hooks"])
    if hooks:
        out += ["Hook errors (grouped):"]
        out += [f"- `{name}` ×{n} — {msg}" for (name, msg), n in hooks.most_common(10)]
        out += [""]

    # ---- user turns inside skill runs
    out += [
        "## User turns inside skill runs",
        "",
        "_⚑ = an interrupt or a correction-shaped opening («нет», «стоп», «зачем», «no», «wait» …) — where to"
        " read around first, not a verdict. Flagged turns first, then in time order; capped per skill._",
        "",
    ]
    for k, v in sorted(by_skill.items(), key=lambda kv: len(kv[1]), reverse=True):
        inside = [(s, t) for s, r in v for t in r["turns"]]
        if not inside:
            continue
        inside.sort(key=lambda st: (not flagged(st[1]["text"]), st[1]["ts"]))
        out += [f"### {k} — {len(inside)} turn(s)", ""]
        for s, t in inside[: args.top]:
            text = cut(t["text"], args.max_user_chars)
            out += [f"- {'⚑ ' if flagged(t['text']) else ''}`{s['short']}` {hhmmss(t['ts'])} — {text}"]
        if len(inside) > args.top:
            out += [f"- _… {len(inside) - args.top} more_"]
        out += [""]

    out += [
        "## Drill down",
        "",
        "`scan_session.py --session <id>` prints the full single-session digest — tool mix, slowest and repeated"
        " calls, files written, subagent transcripts, every user turn. Full ids:",
        "",
    ]
    out += [f"- `{s['short']}` → `{s['sid']}` ({s['project']})" for s in sessions]
    out += [""]
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(
        description="Digest of skill/agent/tool activity across Claude Code sessions (default) or in one session."
    )
    ap.add_argument("--session", help="one session: id or path to a transcript .jsonl")
    ap.add_argument("--current", action="store_true", help="one session: the newest transcript of this project")
    ap.add_argument("--plugin", default=DEFAULT_PLUGIN, help=f"whose skills mark a session (default: {DEFAULT_PLUGIN})")
    ap.add_argument("--since", help="only sessions active on or after YYYY-MM-DD")
    ap.add_argument("--until", help="only sessions started on or before YYYY-MM-DD")
    ap.add_argument("--days", type=int, help="only sessions active in the last N days")
    ap.add_argument("--cwd", help="only sessions of this project directory")
    ap.add_argument("--list", action="store_true", help="list the sessions that ran the plugin and exit")
    ap.add_argument("--idle", type=int, default=30, help="minutes of silence that end a skill run (default: 30)")
    ap.add_argument("--top", type=int, default=12, help="rows per truncated section (default: 12)")
    ap.add_argument("--max-user-chars", type=int, help="truncate each user turn (default: 700 one session, 280 across)")
    args = ap.parse_args()

    if args.session or args.current:
        args.max_user_chars = args.max_user_chars or 700
        transcript = find_transcript(args.session, args.cwd)
        rows = load_rows(transcript)
        if not rows:
            sys.exit(f"transcript {transcript} is empty")
        print(build(transcript, rows, args))
        return

    args.max_user_chars = args.max_user_chars or 280
    since, until = window_bounds(args)
    args.window = (since, until)
    if args.list:
        list_sessions(args.plugin, since, until, args.cwd)
        return

    found, scanned, oldest = discover(args.plugin, since, until, args.cwd)
    sessions = []
    for path in found:
        rows = load_rows(path)
        stamps = [r["_ts"] for r in rows if r["_ts"]]
        if not stamps or (until and min(stamps) >= until):
            continue
        summary = summarize(path, rows, args.plugin, args)
        if summary["runs"]:
            sessions.append(summary)
    if not sessions:
        print(
            f"No session in the window ran a `{args.plugin}:` skill ({scanned} transcripts scanned;"
            f" oldest on disk: {full_ts(oldest)}). Try a wider window, or --session <id> for one session."
        )
        return
    sessions.sort(key=lambda s: s["start"])
    print(build_multi(sessions, args.plugin, scanned, oldest, since, until, args))


if __name__ == "__main__":
    main()
