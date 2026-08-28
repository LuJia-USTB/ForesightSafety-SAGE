#!/usr/bin/env python3
"""Offline pre-push checks for the public code and data release."""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Iterable

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
SELF_PATH = Path(__file__).resolve()

EXPECTED_BENCHMARK_FILES = 16
EXPECTED_INSTANCES_PER_FILE = 67
EXPECTED_TOTAL_INSTANCES = 1072

FORBIDDEN_DIRECTORY_NAMES = {
    "outputs",
    "logs",
    "generated",
    "old",
    "annotations",
    "human_annotations",
    "vesta_rebuttal",
    "__pycache__",
}

SKIP_DIRECTORY_NAMES = {".git", ".venv", "venv"}
TEXT_SUFFIXES = {
    "",
    ".cfg",
    ".ini",
    ".json",
    ".md",
    ".py",
    ".sh",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}

SECRET_PATTERNS = {
    "OpenAI-style API key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "GitHub token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    "AWS access key": re.compile(r"\bAKIA[A-Z0-9]{16}\b"),
    "private key block": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "local absolute path": re.compile(r"(?<![A-Za-z0-9])/(?:mnt/home|root|home)/[^\s\"']+"),
}

YAML_API_KEY_PATTERN = re.compile(r"(?im)^\s*api_key\s*:")
JSON_API_KEY_PATTERN = re.compile(r'(?i)"api_key"\s*:')


def iter_repository_files() -> Iterable[Path]:
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file() or path.is_symlink():
            continue
        relative = path.relative_to(REPO_ROOT)
        if any(part in SKIP_DIRECTORY_NAMES for part in relative.parts):
            continue
        yield path


def scan_repository() -> list[str]:
    issues: list[str] = []

    forbidden_seen: set[Path] = set()
    for path in REPO_ROOT.rglob("*"):
        if not path.is_dir():
            continue
        relative = path.relative_to(REPO_ROOT)
        if any(part in SKIP_DIRECTORY_NAMES for part in relative.parts):
            continue
        if path.name in FORBIDDEN_DIRECTORY_NAMES or "rebuttal" in path.name.lower():
            forbidden_seen.add(relative)

    for relative in sorted(forbidden_seen):
        issues.append(f"excluded directory is present: {relative}")

    for path in iter_repository_files():
        if path.resolve() == SELF_PATH or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        relative = path.relative_to(REPO_ROOT)
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for label, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                issues.append(f"{label} detected in {relative}")
        if path.suffix.lower() in {".yaml", ".yml"} and YAML_API_KEY_PATTERN.search(text):
            issues.append(f"inline api_key field detected in {relative}")
        if path.suffix.lower() == ".json" and JSON_API_KEY_PATTERN.search(text):
            issues.append(f"inline api_key field detected in {relative}")

    return issues


def check_model_configs() -> list[str]:
    issues: list[str] = []
    for directory in ("configs/llm", "configs/auxiliary_llm"):
        for path in sorted((REPO_ROOT / directory).glob("*.yaml")):
            relative = path.relative_to(REPO_ROOT)
            try:
                config = yaml.safe_load(path.read_text(encoding="utf-8"))
            except Exception as exc:
                issues.append(f"cannot load {relative}: {exc}")
                continue

            if not isinstance(config, dict):
                issues.append(f"model config is not a mapping: {relative}")
                continue
            if "api_key" in config:
                issues.append(f"inline api_key field detected in {relative}")
            api_key_env = config.get("api_key_env")
            if not isinstance(api_key_env, str) or not api_key_env.strip():
                issues.append(f"model config missing api_key_env: {relative}")
            if "base_url" not in config:
                issues.append(f"model config missing base_url: {relative}")
            if not (config.get("model") or config.get("model_name") or config.get("name")):
                issues.append(f"model config missing model name: {relative}")

    return issues


def load_instances(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        instances = data
    elif isinstance(data, dict):
        instances = data.get("instances")
    else:
        instances = None
    if not isinstance(instances, list) or not all(isinstance(item, dict) for item in instances):
        raise ValueError("expected a list of scenario objects")
    return instances


def check_benchmark() -> tuple[list[str], Counter[str]]:
    issues: list[str] = []
    counts: Counter[str] = Counter()
    all_ids: list[str] = []
    paths = sorted((REPO_ROOT / "data" / "tasks").glob("*/*/benchmark.json"))

    if len(paths) != EXPECTED_BENCHMARK_FILES:
        issues.append(
            f"expected {EXPECTED_BENCHMARK_FILES} benchmark files, found {len(paths)}"
        )

    for path in paths:
        relative = path.relative_to(REPO_ROOT)
        try:
            instances = load_instances(path)
        except Exception as exc:
            issues.append(f"cannot load {relative}: {exc}")
            continue

        dimension = relative.parts[2]
        counts[dimension] += len(instances)
        if len(instances) != EXPECTED_INSTANCES_PER_FILE:
            issues.append(
                f"{relative} has {len(instances)} instances; expected {EXPECTED_INSTANCES_PER_FILE}"
            )

        ids = [str(item.get("instance_id") or "") for item in instances]
        if any(not item_id for item_id in ids):
            issues.append(f"{relative} contains an empty instance_id")
        if len(ids) != len(set(ids)):
            issues.append(f"{relative} contains duplicate instance_id values")
        all_ids.extend(ids)

    if len(all_ids) != EXPECTED_TOTAL_INSTANCES:
        issues.append(
            f"expected {EXPECTED_TOTAL_INSTANCES} total instances, found {len(all_ids)}"
        )
    if len(all_ids) != len(set(all_ids)):
        issues.append("instance_id values are not globally unique")

    return issues, counts


def main() -> int:
    issues = scan_repository()
    issues.extend(check_model_configs())
    benchmark_issues, counts = check_benchmark()
    issues.extend(benchmark_issues)

    if issues:
        print("Release check failed:")
        for issue in issues:
            print(f"- {issue}")
        return 1

    print("Release check passed.")
    print(f"- benchmark files: {EXPECTED_BENCHMARK_FILES}")
    print(f"- unique scenarios: {EXPECTED_TOTAL_INSTANCES}")
    for dimension, count in sorted(counts.items()):
        print(f"- {dimension}: {count}")
    print("- no excluded artifact directories or suspicious credential patterns detected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
