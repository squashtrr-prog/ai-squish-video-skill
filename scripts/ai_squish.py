#!/usr/bin/env python3
"""Small, dependency-free runtime helpers for the AI Squish Video skill."""

from __future__ import annotations

import argparse
import json
import os
import random
import re
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parent.parent
TOPICS_FILE = SKILL_ROOT / "scripts" / "topics.json"
CONFIG_ENV = "AI_SQUISH_CONFIG"
CONFIG_DIR_NAME = "ai-squish-video"
CONFIG_FILE_NAME = "config.json"
WINDOWS_RESERVED_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}


class CliError(RuntimeError):
    """Expected command error that should be shown without a traceback."""


def config_path() -> Path:
    override = os.environ.get(CONFIG_ENV)
    if override:
        return Path(override).expanduser().resolve()

    if os.name == "nt":
        base = os.environ.get("APPDATA")
        if base:
            return Path(base) / CONFIG_DIR_NAME / CONFIG_FILE_NAME

    base = os.environ.get("XDG_CONFIG_HOME")
    if base:
        return Path(base).expanduser() / CONFIG_DIR_NAME / CONFIG_FILE_NAME
    return Path.home() / ".config" / CONFIG_DIR_NAME / CONFIG_FILE_NAME


def emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def read_config() -> tuple[dict[str, Any] | None, str | None]:
    path = config_path()
    if not path.exists():
        return None, "configuration file does not exist"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return None, f"configuration file is invalid: {exc}"
    if not isinstance(data, dict) or not isinstance(data.get("output_root"), str):
        return None, "configuration is missing output_root"
    return data, None


def validate_output_root(value: str, *, create: bool) -> Path:
    if not value.strip():
        raise CliError("output root cannot be empty")
    root = Path(value).expanduser().resolve()
    try:
        if create:
            root.mkdir(parents=True, exist_ok=True)
        if not root.is_dir():
            raise CliError(f"output root is not a directory: {root}")
        with tempfile.NamedTemporaryFile(prefix=".ai-squish-write-test-", dir=root):
            pass
    except CliError:
        raise
    except OSError as exc:
        raise CliError(f"output root is not writable: {root} ({exc})") from exc
    return root


def show_config() -> int:
    path = config_path()
    data, error = read_config()
    if data is None:
        emit({"configured": False, "config_path": str(path), "reason": error})
        return 0
    try:
        root = validate_output_root(data["output_root"], create=False)
    except CliError as exc:
        emit(
            {
                "configured": False,
                "config_path": str(path),
                "output_root": data["output_root"],
                "reason": str(exc),
            }
        )
        return 0
    emit(
        {
            "configured": True,
            "config_path": str(path),
            "output_root": str(root),
            "version": data.get("version", 1),
        }
    )
    return 0


def set_config(output_root: str) -> int:
    root = validate_output_root(output_root, create=True)
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": 1,
        "output_root": str(root),
        "updated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
    }
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    temporary.replace(path)
    emit({"configured": True, "config_path": str(path), **payload})
    return 0


def load_topics() -> list[dict[str, str]]:
    try:
        payload = json.loads(TOPICS_FILE.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise CliError(f"cannot read topics file: {exc}") from exc

    results: list[dict[str, str]] = []
    seen: set[str] = set()
    for category in payload.get("categories", []):
        category_name = category.get("category")
        for item in category.get("items", []):
            topic = item.get("topic")
            if not category_name or not topic or topic in seen:
                continue
            seen.add(topic)
            results.append(
                {
                    "category": str(category_name),
                    "topic": str(topic),
                    "emoji": str(item.get("emoji", "")),
                }
            )
    if not results:
        raise CliError("topics file contains no usable topics")
    return results


def choose_topics(count: int) -> int:
    candidates = load_topics()
    if count < 1:
        raise CliError("count must be at least 1")
    if count > len(candidates):
        raise CliError(f"count cannot exceed {len(candidates)}")
    selected = random.SystemRandom().sample(candidates, count)
    emit({"count": count, "topics": selected})
    return 0


def sanitize_topic(topic: str, max_length: int = 48) -> str:
    value = re.sub(r"[<>:\"/\\|?*\x00-\x1f]", "-", topic.strip())
    value = re.sub(r"\s+", "-", value)
    value = re.sub(r"-+", "-", value).strip(" .-")
    if not value:
        value = "untitled"
    if value.upper() in WINDOWS_RESERVED_NAMES:
        value = f"topic-{value}"
    value = value[:max_length].rstrip(" .-")
    return value or "untitled"


def configured_output_root() -> Path:
    data, error = read_config()
    if data is None:
        raise CliError(
            f"skill is not configured: {error}; run 'config set --output-root PATH' first"
        )
    return validate_output_root(data["output_root"], create=False)


def create_run(topic: str) -> int:
    if not topic.strip():
        raise CliError("topic cannot be empty")
    root = configured_output_root()
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    slug = sanitize_topic(topic)
    base_name = f"{stamp}-{slug}"
    run_dir = root / base_name
    suffix = 2
    while run_dir.exists():
        run_dir = root / f"{base_name}-{suffix:02d}"
        suffix += 1
    run_dir.mkdir(parents=False)

    now = datetime.now().astimezone().isoformat(timespec="seconds")
    record = {
        "schema_version": 1,
        "created_at": now,
        "updated_at": now,
        "topic": topic.strip(),
        "topic_slug": slug,
        "state": "AWAITING_IMAGE_APPROVAL",
        "files": {},
    }
    (run_dir / "run.json").write_text(
        json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    emit(
        {
            "created": True,
            "topic": topic.strip(),
            "state": record["state"],
            "run_dir": str(run_dir.resolve()),
            "run_file": str((run_dir / "run.json").resolve()),
        }
    )
    return 0


def doctor() -> int:
    checks: dict[str, Any] = {
        "python": sys.version.split()[0],
        "skill_root": str(SKILL_ROOT),
        "topics_file": str(TOPICS_FILE),
        "topics_file_exists": TOPICS_FILE.is_file(),
        "config_path": str(config_path()),
    }
    data, error = read_config()
    checks["configured"] = data is not None
    if error:
        checks["config_reason"] = error
    elif data:
        checks["output_root"] = data.get("output_root")
        try:
            validate_output_root(data["output_root"], create=False)
            checks["output_root_writable"] = True
        except CliError as exc:
            checks["output_root_writable"] = False
            checks["output_root_reason"] = str(exc)
    emit(checks)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    config = commands.add_parser("config", help="show or update persistent settings")
    config_commands = config.add_subparsers(dest="config_command", required=True)
    config_commands.add_parser("show", help="show configuration without creating it")
    config_set = config_commands.add_parser("set", help="save a validated output directory")
    config_set.add_argument("--output-root", required=True)

    topics = commands.add_parser("topics", help="choose unique random food topics")
    topics.add_argument("--count", type=int, default=8)

    create = commands.add_parser("create-run", help="create a timestamped run directory")
    create.add_argument("--topic", required=True)

    commands.add_parser("doctor", help="report runtime and configuration status")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "config" and args.config_command == "show":
            return show_config()
        if args.command == "config" and args.config_command == "set":
            return set_config(args.output_root)
        if args.command == "topics":
            return choose_topics(args.count)
        if args.command == "create-run":
            return create_run(args.topic)
        if args.command == "doctor":
            return doctor()
    except CliError as exc:
        emit({"error": str(exc)})
        return 2
    raise AssertionError("unreachable")


if __name__ == "__main__":
    raise SystemExit(main())
