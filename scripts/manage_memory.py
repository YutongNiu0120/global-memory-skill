from __future__ import annotations

import argparse
import json
import re
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


VERSION = 1
DEFAULT_ROOT = Path.home() / ".codex" / "memories" / "global-memory"
TIER_MAP = {
    "short": "short-term",
    "short-term": "short-term",
    "long": "long-term",
    "long-term": "long-term",
    "inbox": "inbox",
    "archive": "archive",
}
FILE_MAP = {
    "short-term": "short-term.json",
    "long-term": "long-term.json",
    "inbox": "inbox.json",
    "archive": "archive.json",
}
ID_PREFIX = {
    "short-term": "st",
    "long-term": "lt",
    "inbox": "ib",
    "archive": "ar",
}


def now_utc() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def isoformat(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")


def parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def resolve_tier(name: str) -> str:
    try:
        return TIER_MAP[name]
    except KeyError as exc:
        raise ValueError(f"Unsupported tier: {name}") from exc


def normalize_key(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return normalized[:80] or "memory"


def clamp_confidence(value: float) -> float:
    return round(max(0.0, min(0.99, value)), 2)


def build_store(tier: str) -> dict[str, Any]:
    return {
        "version": VERSION,
        "tier": tier,
        "updated_at": isoformat(now_utc()),
        "entries": [],
    }


def store_path(root: Path, tier: str) -> Path:
    return root / FILE_MAP[tier]


def load_store(root: Path, tier: str) -> dict[str, Any]:
    path = store_path(root, tier)
    if not path.exists():
        return build_store(tier)
    data = json.loads(path.read_text(encoding="utf-8"))
    data.setdefault("version", VERSION)
    data.setdefault("tier", tier)
    data.setdefault("entries", [])
    return data


def save_store(root: Path, tier: str, data: dict[str, Any]) -> None:
    root.mkdir(parents=True, exist_ok=True)
    data["version"] = VERSION
    data["tier"] = tier
    data["updated_at"] = isoformat(now_utc())
    store_path(root, tier).write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def ensure_root(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    for tier in FILE_MAP:
        path = store_path(root, tier)
        if not path.exists():
            save_store(root, tier, build_store(tier))


def make_id(tier: str, captured_at: str) -> str:
    stamp = captured_at.replace("-", "").replace(":", "").replace("T", "").replace("Z", "")
    return f"{ID_PREFIX[tier]}-{stamp}-{uuid.uuid4().hex[:6]}"


def latest_reference(entry: dict[str, Any]) -> datetime:
    timestamps = [
        parse_time(entry.get("last_used_at")),
        parse_time(entry.get("last_validated_at")),
        parse_time(entry.get("last_decay_at")),
        parse_time(entry.get("last_seen_at")),
        parse_time(entry.get("created_at")),
    ]
    return max(ts for ts in timestamps if ts is not None)


def inbox_reference(entry: dict[str, Any]) -> datetime:
    return parse_time(entry.get("captured_at")) or now_utc()


def append_evidence(entry: dict[str, Any], note: str, captured_at: str) -> None:
    evidence = entry.setdefault("evidence", [])
    evidence.append(
        {
            "captured_at": captured_at,
            "note": note,
        }
    )
    if len(evidence) > 12:
        del evidence[:-12]


def find_index(entries: list[dict[str, Any]], *, key: str | None = None, entry_id: str | None = None) -> int:
    for index, entry in enumerate(entries):
        if key and entry.get("key") == key:
            return index
        if entry_id and entry.get("id") == entry_id:
            return index
    return -1


def archive_entry(
    archive_store: dict[str, Any],
    entry: dict[str, Any],
    *,
    source_tier: str,
    reason: str,
    archived_at: str,
) -> None:
    archived = dict(entry)
    archived["archived_at"] = archived_at
    archived["archive_reason"] = reason
    archived["source_tier"] = source_tier
    archive_store["entries"].append(archived)


def create_entry(
    tier: str,
    *,
    summary: str,
    abstract_summary: str | None,
    category: str,
    scope: str,
    key: str,
    confidence: float,
    tags: list[str],
    evidence_note: str,
    captured_at: str,
    ttl_days: int,
) -> dict[str, Any]:
    entry = {
        "id": make_id(tier, captured_at),
        "key": key,
        "summary": summary,
        "abstract_summary": abstract_summary,
        "category": category,
        "scope": scope,
        "confidence": clamp_confidence(confidence),
        "evidence_count": 1,
        "evidence": [],
        "tags": sorted(set(tags)),
        "created_at": captured_at,
        "last_seen_at": captured_at,
        "last_used_at": None,
    }
    append_evidence(entry, evidence_note, captured_at)
    if tier == "short-term":
        entry["expires_at"] = isoformat(parse_time(captured_at) + timedelta(days=ttl_days))
    if tier == "long-term":
        entry["last_validated_at"] = captured_at
        entry["last_decay_at"] = captured_at
        entry["source_ids"] = []
    return entry


def apply_memory_observation(
    short_store: dict[str, Any],
    long_store: dict[str, Any],
    archive_store: dict[str, Any],
    *,
    tier: str,
    summary: str,
    abstract_summary: str | None,
    category: str,
    scope: str,
    key: str,
    confidence: float,
    tags: list[str],
    evidence_note: str,
    captured_at: str,
    ttl_days: int,
    override: bool,
) -> tuple[str, dict[str, Any]]:
    if override:
        for store_tier, store in (("short-term", short_store), ("long-term", long_store)):
            while True:
                index = find_index(store["entries"], key=key)
                if index < 0:
                    break
                entry = store["entries"].pop(index)
                archive_entry(
                    archive_store,
                    entry,
                    source_tier=store_tier,
                    reason="overridden by newer evidence",
                    archived_at=captured_at,
                )

    target_store = short_store if tier == "short-term" else long_store
    index = find_index(target_store["entries"], key=key)
    if index >= 0:
        merge_entry(
            target_store["entries"][index],
            tier=tier,
            summary=summary,
            abstract_summary=abstract_summary,
            category=category,
            scope=scope,
            confidence=confidence,
            tags=tags,
            evidence_note=evidence_note,
            captured_at=captured_at,
            ttl_days=ttl_days,
        )
        return "updated", target_store["entries"][index]

    entry = create_entry(
        tier,
        summary=summary,
        abstract_summary=abstract_summary,
        category=category,
        scope=scope,
        key=key,
        confidence=confidence,
        tags=tags,
        evidence_note=evidence_note,
        captured_at=captured_at,
        ttl_days=ttl_days,
    )
    target_store["entries"].append(entry)
    return "created", entry


def merge_entry(
    entry: dict[str, Any],
    *,
    tier: str,
    summary: str,
    abstract_summary: str | None,
    category: str,
    scope: str,
    confidence: float,
    tags: list[str],
    evidence_note: str,
    captured_at: str,
    ttl_days: int,
) -> None:
    entry["summary"] = summary
    entry["category"] = category
    entry["scope"] = scope
    if abstract_summary:
        entry["abstract_summary"] = abstract_summary
    entry["confidence"] = clamp_confidence(max(entry.get("confidence", 0.0), confidence))
    entry["evidence_count"] = int(entry.get("evidence_count", 0)) + 1
    entry["last_seen_at"] = captured_at
    entry["tags"] = sorted(set(entry.get("tags", [])) | set(tags))
    append_evidence(entry, evidence_note, captured_at)
    if tier == "short-term":
        entry["expires_at"] = isoformat(parse_time(captured_at) + timedelta(days=ttl_days))
    if tier == "long-term":
        entry["last_validated_at"] = captured_at


def add_memory(args: argparse.Namespace) -> None:
    root = args.root
    ensure_root(root)
    short_store = load_store(root, "short-term")
    long_store = load_store(root, "long-term")
    archive_store = load_store(root, "archive")

    tier = resolve_tier(args.tier)
    captured_at = isoformat(now_utc())
    key = args.key or normalize_key(args.summary)
    evidence_note = args.evidence_note or args.summary
    tags = args.tag or []
    action, entry = apply_memory_observation(
        short_store,
        long_store,
        archive_store,
        tier=tier,
        summary=args.summary,
        abstract_summary=args.abstract_summary,
        category=args.category,
        scope=args.scope,
        key=key,
        confidence=args.confidence,
        tags=tags,
        evidence_note=evidence_note,
        captured_at=captured_at,
        ttl_days=args.ttl_days,
        override=args.override,
    )

    save_store(root, "short-term", short_store)
    save_store(root, "long-term", long_store)
    save_store(root, "archive", archive_store)
    print(f"{action}: {entry['id']} [{tier}] {entry['summary']}")


def touch_memory(args: argparse.Namespace) -> None:
    root = args.root
    ensure_root(root)
    tier = resolve_tier(args.tier)
    if tier == "archive":
        raise ValueError("Cannot touch archived memory.")
    store = load_store(root, tier)
    index = find_index(store["entries"], key=args.key, entry_id=args.id)
    if index < 0:
        raise ValueError("Memory not found.")

    captured_at = isoformat(now_utc())
    entry = store["entries"][index]
    entry["last_used_at"] = captured_at
    entry["last_seen_at"] = captured_at
    entry["confidence"] = clamp_confidence(entry.get("confidence", 0.0) + args.confidence_delta)
    entry["evidence_count"] = int(entry.get("evidence_count", 0)) + 1
    if args.note:
        append_evidence(entry, args.note, captured_at)
    if tier == "short-term":
        entry["expires_at"] = isoformat(parse_time(captured_at) + timedelta(days=args.extend_days))
    if tier == "long-term":
        entry["last_validated_at"] = captured_at

    save_store(root, tier, store)
    print(f"touched: {entry['id']} [{tier}] {entry['summary']}")


def forget_memory(args: argparse.Namespace) -> None:
    root = args.root
    ensure_root(root)
    tier = resolve_tier(args.tier)
    if tier == "archive":
        raise ValueError("Archive entries are already forgotten.")

    store = load_store(root, tier)
    archive_store = load_store(root, "archive")
    index = find_index(store["entries"], key=args.key, entry_id=args.id)
    if index < 0:
        raise ValueError("Memory not found.")

    captured_at = isoformat(now_utc())
    entry = store["entries"].pop(index)
    archive_entry(
        archive_store,
        entry,
        source_tier=tier,
        reason=args.reason,
        archived_at=captured_at,
    )
    save_store(root, tier, store)
    save_store(root, "archive", archive_store)
    print(f"forgotten: {entry['id']} [{tier}] {entry['summary']}")


def promote_entry(
    short_entry: dict[str, Any],
    long_store: dict[str, Any],
    promoted_at: str,
) -> str:
    key = short_entry["key"]
    summary = short_entry.get("abstract_summary") or short_entry["summary"]
    index = find_index(long_store["entries"], key=key)
    if index >= 0:
        target = long_store["entries"][index]
        target["summary"] = summary
        target["abstract_summary"] = short_entry.get("abstract_summary") or target.get("abstract_summary")
        target["confidence"] = clamp_confidence(max(target.get("confidence", 0.0), short_entry.get("confidence", 0.0) + 0.1))
        target["evidence_count"] = int(target.get("evidence_count", 0)) + int(short_entry.get("evidence_count", 0))
        target["last_seen_at"] = promoted_at
        target["last_validated_at"] = promoted_at
        target["tags"] = sorted(set(target.get("tags", [])) | set(short_entry.get("tags", [])))
        target.setdefault("source_ids", []).append(short_entry["id"])
        for evidence in short_entry.get("evidence", []):
            append_evidence(target, evidence["note"], promoted_at)
        return target["id"]

    target = {
        "id": make_id("long-term", promoted_at),
        "key": key,
        "summary": summary,
        "abstract_summary": short_entry.get("abstract_summary"),
        "category": short_entry.get("category"),
        "scope": short_entry.get("scope"),
        "confidence": clamp_confidence(short_entry.get("confidence", 0.0) + 0.15),
        "evidence_count": int(short_entry.get("evidence_count", 0)),
        "evidence": short_entry.get("evidence", [])[-12:],
        "tags": sorted(set(short_entry.get("tags", []))),
        "created_at": promoted_at,
        "last_seen_at": promoted_at,
        "last_used_at": short_entry.get("last_used_at"),
        "last_validated_at": promoted_at,
        "last_decay_at": promoted_at,
        "source_ids": [short_entry["id"]],
    }
    long_store["entries"].append(target)
    return target["id"]


def run_consolidation(
    short_store: dict[str, Any],
    long_store: dict[str, Any],
    archive_store: dict[str, Any],
    *,
    captured_at: str,
    promote_threshold: int,
    long_stale_days: int,
    decay_step: float,
    forget_threshold: float,
) -> dict[str, int]:
    now = parse_time(captured_at)
    promoted = 0
    expired = 0
    decayed = 0
    forgotten = 0

    kept_short_entries: list[dict[str, Any]] = []
    for entry in short_store["entries"]:
        expires_at = parse_time(entry.get("expires_at"))
        if expires_at and expires_at <= now:
            archive_entry(
                archive_store,
                entry,
                source_tier="short-term",
                reason="expired",
                archived_at=captured_at,
            )
            expired += 1
            continue
        if int(entry.get("evidence_count", 0)) >= promote_threshold:
            promote_entry(entry, long_store, captured_at)
            archive_entry(
                archive_store,
                entry,
                source_tier="short-term",
                reason="promoted to long-term",
                archived_at=captured_at,
            )
            promoted += 1
            continue
        kept_short_entries.append(entry)
    short_store["entries"] = kept_short_entries

    kept_long_entries: list[dict[str, Any]] = []
    for entry in long_store["entries"]:
        reference = latest_reference(entry)
        elapsed_days = max(0, (now - reference).days)
        if elapsed_days >= long_stale_days:
            steps = max(1, elapsed_days // long_stale_days)
            new_confidence = clamp_confidence(entry.get("confidence", 0.0) - (steps * decay_step))
            if new_confidence != entry.get("confidence"):
                entry["confidence"] = new_confidence
                entry["last_decay_at"] = captured_at
                decayed += 1
        if entry.get("confidence", 0.0) < forget_threshold:
            archive_entry(
                archive_store,
                entry,
                source_tier="long-term",
                reason="decayed below forget threshold",
                archived_at=captured_at,
            )
            forgotten += 1
            continue
        kept_long_entries.append(entry)
    long_store["entries"] = kept_long_entries

    return {
        "promoted": promoted,
        "expired": expired,
        "decayed": decayed,
        "forgotten": forgotten,
    }


def consolidate_memory(args: argparse.Namespace) -> None:
    root = args.root
    ensure_root(root)
    short_store = load_store(root, "short-term")
    long_store = load_store(root, "long-term")
    archive_store = load_store(root, "archive")

    captured_at = isoformat(now_utc())
    stats = run_consolidation(
        short_store,
        long_store,
        archive_store,
        captured_at=captured_at,
        promote_threshold=args.promote_threshold,
        long_stale_days=args.long_stale_days,
        decay_step=args.decay_step,
        forget_threshold=args.forget_threshold,
    )

    save_store(root, "short-term", short_store)
    save_store(root, "long-term", long_store)
    save_store(root, "archive", archive_store)
    print(
        "consolidated: "
        f"promoted={stats['promoted']}, expired={stats['expired']}, "
        f"decayed={stats['decayed']}, forgotten={stats['forgotten']}"
    )


def note_memory(args: argparse.Namespace) -> None:
    root = args.root
    ensure_root(root)
    inbox_store = load_store(root, "inbox")
    captured_at = isoformat(now_utc())
    note = {
        "id": make_id("inbox", captured_at),
        "session_id": args.session,
        "target_tier": resolve_tier(args.tier),
        "key": args.key or normalize_key(args.summary),
        "summary": args.summary,
        "abstract_summary": args.abstract_summary,
        "category": args.category,
        "scope": args.scope,
        "confidence": clamp_confidence(args.confidence),
        "ttl_days": args.ttl_days,
        "tags": sorted(set(args.tag or [])),
        "evidence_note": args.evidence_note or args.summary,
        "override": args.override,
        "captured_at": captured_at,
    }
    inbox_store["entries"].append(note)
    save_store(root, "inbox", inbox_store)
    print(f"queued: {note['id']} session={note['session_id']} key={note['key']}")


def flush_notes(args: argparse.Namespace) -> None:
    root = args.root
    ensure_root(root)
    short_store = load_store(root, "short-term")
    long_store = load_store(root, "long-term")
    inbox_store = load_store(root, "inbox")
    archive_store = load_store(root, "archive")

    selected_notes: list[dict[str, Any]] = []
    remaining_notes: list[dict[str, Any]] = []
    for note in inbox_store["entries"]:
        if args.session and note.get("session_id") != args.session:
            remaining_notes.append(note)
            continue
        selected_notes.append(note)

    if not selected_notes:
        print("flushed: 0 notes")
        return

    selected_notes.sort(key=inbox_reference)
    created = 0
    updated = 0
    flushed_at = isoformat(now_utc())

    for note in selected_notes:
        action, _ = apply_memory_observation(
            short_store,
            long_store,
            archive_store,
            tier=note["target_tier"],
            summary=note["summary"],
            abstract_summary=note.get("abstract_summary"),
            category=note["category"],
            scope=note["scope"],
            key=note["key"],
            confidence=note["confidence"],
            tags=note.get("tags", []),
            evidence_note=note.get("evidence_note", note["summary"]),
            captured_at=note.get("captured_at", flushed_at),
            ttl_days=int(note.get("ttl_days", 30)),
            override=bool(note.get("override")),
        )
        if action == "created":
            created += 1
        else:
            updated += 1
        archive_entry(
            archive_store,
            note,
            source_tier="inbox",
            reason="flushed into memory store",
            archived_at=flushed_at,
        )

    inbox_store["entries"] = remaining_notes

    summary = f"flushed: {len(selected_notes)} notes, created={created}, updated={updated}"
    if args.consolidate:
        stats = run_consolidation(
            short_store,
            long_store,
            archive_store,
            captured_at=flushed_at,
            promote_threshold=args.promote_threshold,
            long_stale_days=args.long_stale_days,
            decay_step=args.decay_step,
            forget_threshold=args.forget_threshold,
        )
        summary += (
            f", promoted={stats['promoted']}, expired={stats['expired']}, "
            f"decayed={stats['decayed']}, forgotten={stats['forgotten']}"
        )

    save_store(root, "short-term", short_store)
    save_store(root, "long-term", long_store)
    save_store(root, "inbox", inbox_store)
    save_store(root, "archive", archive_store)
    print(summary)


def list_memory(args: argparse.Namespace) -> None:
    root = args.root
    ensure_root(root)
    requested = args.tier
    tiers = ["inbox", "short-term", "long-term", "archive"] if requested == "all" else [resolve_tier(requested)]
    payload: dict[str, list[dict[str, Any]]] = {}

    for tier in tiers:
        entries = load_store(root, tier)["entries"]
        if args.category:
            entries = [entry for entry in entries if entry.get("category") == args.category]
        if args.tag:
            entries = [entry for entry in entries if args.tag in entry.get("tags", [])]
        if tier == "inbox":
            entries = sorted(entries, key=inbox_reference, reverse=True)[: args.limit]
        else:
            entries = sorted(entries, key=latest_reference, reverse=True)[: args.limit]
        payload[tier] = entries

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return

    for tier, entries in payload.items():
        print(f"[{tier}] {len(entries)} entries")
        for entry in entries:
            if tier == "inbox":
                print(
                    f"- {entry['id']} session={entry.get('session_id')} key={entry.get('key')} "
                    f"tier={entry.get('target_tier')} confidence={entry.get('confidence')} "
                    f"summary={entry.get('summary')}"
                )
            else:
                print(
                    f"- {entry['id']} key={entry.get('key')} "
                    f"confidence={entry.get('confidence')} evidence={entry.get('evidence_count')} "
                    f"summary={entry.get('summary')}"
                )
        if not entries:
            print("- none")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage collaboration memory.")
    parser.add_argument(
        "--root",
        type=Path,
        default=DEFAULT_ROOT,
        help="Memory root directory. Defaults to ~/.codex/memories/global-memory",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("init", help="Create the default memory store.")

    list_parser = subparsers.add_parser("list", help="List current memories.")
    list_parser.add_argument("--tier", choices=["inbox", "short", "long", "archive", "all"], default="all")
    list_parser.add_argument("--category")
    list_parser.add_argument("--tag")
    list_parser.add_argument("--limit", type=int, default=20)
    list_parser.add_argument("--json", action="store_true")

    note_parser = subparsers.add_parser("note", help="Queue a session observation for later flush.")
    note_parser.add_argument("--session", default="default")
    note_parser.add_argument("--tier", choices=["short", "long"], default="short")
    note_parser.add_argument("--summary", required=True)
    note_parser.add_argument("--abstract-summary")
    note_parser.add_argument("--category", required=True)
    note_parser.add_argument("--scope", default="global")
    note_parser.add_argument("--key")
    note_parser.add_argument("--confidence", type=float, default=0.6)
    note_parser.add_argument("--ttl-days", type=int, default=30)
    note_parser.add_argument("--tag", action="append")
    note_parser.add_argument("--evidence-note")
    note_parser.add_argument("--override", action="store_true")

    add_parser = subparsers.add_parser("add", help="Create or reinforce a memory entry.")
    add_parser.add_argument("--tier", choices=["short", "long"], default="short")
    add_parser.add_argument("--summary", required=True)
    add_parser.add_argument("--abstract-summary")
    add_parser.add_argument("--category", required=True)
    add_parser.add_argument("--scope", default="global")
    add_parser.add_argument("--key")
    add_parser.add_argument("--confidence", type=float, default=0.65)
    add_parser.add_argument("--ttl-days", type=int, default=30)
    add_parser.add_argument("--tag", action="append")
    add_parser.add_argument("--evidence-note")
    add_parser.add_argument("--override", action="store_true")

    touch_parser = subparsers.add_parser("touch", help="Mark a memory as useful in real work.")
    touch_parser.add_argument("--tier", choices=["short", "long"], required=True)
    touch_group = touch_parser.add_mutually_exclusive_group(required=True)
    touch_group.add_argument("--id")
    touch_group.add_argument("--key")
    touch_parser.add_argument("--note")
    touch_parser.add_argument("--confidence-delta", type=float, default=0.05)
    touch_parser.add_argument("--extend-days", type=int, default=14)

    forget_parser = subparsers.add_parser("forget", help="Archive a memory entry.")
    forget_parser.add_argument("--tier", choices=["short", "long"], required=True)
    forget_group = forget_parser.add_mutually_exclusive_group(required=True)
    forget_group.add_argument("--id")
    forget_group.add_argument("--key")
    forget_parser.add_argument("--reason", required=True)

    consolidate_parser = subparsers.add_parser("consolidate", help="Promote and forget memories.")
    consolidate_parser.add_argument("--promote-threshold", type=int, default=3)
    consolidate_parser.add_argument("--long-stale-days", type=int, default=120)
    consolidate_parser.add_argument("--decay-step", type=float, default=0.1)
    consolidate_parser.add_argument("--forget-threshold", type=float, default=0.35)

    flush_parser = subparsers.add_parser("flush", help="Apply queued notes into memory and optionally consolidate.")
    flush_parser.add_argument("--session")
    flush_parser.add_argument("--consolidate", action="store_true")
    flush_parser.add_argument("--promote-threshold", type=int, default=3)
    flush_parser.add_argument("--long-stale-days", type=int, default=120)
    flush_parser.add_argument("--decay-step", type=float, default=0.1)
    flush_parser.add_argument("--forget-threshold", type=float, default=0.35)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "init":
        ensure_root(args.root)
        print(f"initialized: {args.root}")
        return
    if args.command == "list":
        list_memory(args)
        return
    if args.command == "note":
        note_memory(args)
        return
    if args.command == "add":
        add_memory(args)
        return
    if args.command == "touch":
        touch_memory(args)
        return
    if args.command == "forget":
        forget_memory(args)
        return
    if args.command == "consolidate":
        consolidate_memory(args)
        return
    if args.command == "flush":
        flush_notes(args)
        return

    raise ValueError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    main()
