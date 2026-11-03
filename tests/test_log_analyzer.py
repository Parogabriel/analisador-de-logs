import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from log_analyzer import LEVELS, analyze, parse_level

ROOT = Path(__file__).resolve().parents[1]


class AnalyzerTests(unittest.TestCase):
    def test_accepts_each_level_and_messages_with_spaces(self):
        for level in LEVELS:
            with self.subTest(level=level):
                self.assertEqual(
                    parse_level(f"2026-11-03 09:15:00 {level} Pedido recebido com sucesso"),
                    level,
                )

    def test_rejects_invalid_records(self):
        for line in (
            "2026-02-30 09:00:00 INFO Data inexistente",
            "2026-11-03 25:00:00 INFO Hora inválida",
            "2026-11-03 09:00:00 TRACE Nível desconhecido",
            "2026-11-03 09:00:00 INFO",
            "2026-11-03 09:00:00 INFO   ",
            "registro incompleto",
        ):
            with self.subTest(line=line):
                self.assertIsNone(parse_level(line))

    def test_counts_levels_and_invalid_lines_from_an_iterator(self):
        lines = iter([
            "2026-11-03 09:00:00 INFO Iniciado\n",
            "2026-11-03 09:00:01 ERROR Falha\n",
            "registro inválido\n",
            "2026-11-03 09:00:02 ERROR Nova falha\n",
            "  \n",
        ])
        summary = analyze(lines)
        self.assertEqual(summary.valid, 3)
        self.assertEqual(summary.invalid, 1)
        self.assertEqual(summary.counts, {"INFO": 1, "ERROR": 2})

    def test_empty_or_blank_input_has_no_records(self):
        for lines in ([], ["\n", "  \t\n"]):
            with self.subTest(lines=lines):
                summary = analyze(lines)
                self.assertEqual(summary.valid, 0)
                self.assertEqual(summary.invalid, 0)

    def test_analyses_do_not_share_counts(self):
        analyze(["2026-11-03 09:00:00 INFO Iniciado"])
        self.assertEqual(analyze([]).valid, 0)


class CliTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, str(ROOT / "log_analyzer.py"), *map(str, args)],
            capture_output=True,
            encoding="utf-8",
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
            check=False,
        )

    def test_sample_output(self):
        result = self.run_cli(ROOT / "examples" / "app.log")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertEqual(result.stdout.splitlines(), [
            "Linhas válidas: 7", "Linhas inválidas: 1",
            "DEBUG: 1", "INFO: 2", "WARNING: 1", "ERROR: 2", "CRITICAL: 1",
        ])

    def test_missing_file_returns_error_without_traceback(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_cli(Path(directory) / "missing.log")
        self.assertEqual(result.returncode, 2)
        self.assertIn("Erro ao ler o arquivo:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(result.stdout, "")

    def test_invalid_encoding_returns_error(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invalid.log"
            path.write_bytes(b"\xff\xfe")
            result = self.run_cli(path)
        self.assertEqual(result.returncode, 2)
        self.assertIn("Erro ao ler o arquivo:", result.stderr)

    def test_requires_file_argument(self):
        self.assertEqual(self.run_cli().returncode, 2)


if __name__ == "__main__":
    unittest.main()
