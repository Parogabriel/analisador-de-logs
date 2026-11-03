"""Resume arquivos de log no formato DATA HORA NIVEL MENSAGEM."""

import argparse
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Iterable

LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")


@dataclass
class Summary:
    counts: Counter[str] = field(default_factory=Counter)
    invalid: int = 0

    @property
    def valid(self) -> int:
        return sum(self.counts.values())


def parse_level(line: str) -> str | None:
    parts = line.split(maxsplit=3)
    if len(parts) != 4 or parts[2] not in LEVELS:
        return None
    try:
        datetime.strptime(f"{parts[0]} {parts[1]}", "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None
    return parts[2]


def analyze(lines: Iterable[str]) -> Summary:
    summary = Summary()
    for line in lines:
        if not line.strip():
            continue
        level = parse_level(line)
        if level is None:
            summary.invalid += 1
        else:
            summary.counts[level] += 1
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path, help="arquivo de log em UTF-8")
    args = parser.parse_args()
    try:
        with args.file.open(encoding="utf-8") as log_file:
            summary = analyze(log_file)
    except (OSError, UnicodeError) as error:
        parser.exit(2, f"Erro ao ler o arquivo: {error}\n")

    print(f"Linhas válidas: {summary.valid}")
    print(f"Linhas inválidas: {summary.invalid}")
    for level in LEVELS:
        print(f"{level}: {summary.counts[level]}")


if __name__ == "__main__":
    main()
