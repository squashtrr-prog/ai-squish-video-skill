from __future__ import annotations

import importlib.util
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "ai_squish.py"
SPEC = importlib.util.spec_from_file_location("ai_squish", SCRIPT)
assert SPEC and SPEC.loader
ai_squish = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ai_squish)


class AiSquishRuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.config = self.root / "settings" / "config.json"
        self.output = self.root / "outputs"
        self.env = patch.dict(os.environ, {"AI_SQUISH_CONFIG": str(self.config)})
        self.env.start()

    def tearDown(self) -> None:
        self.env.stop()
        self.temp_dir.cleanup()

    def capture(self, function, *args):
        stream = StringIO()
        with redirect_stdout(stream):
            code = function(*args)
        return code, json.loads(stream.getvalue())

    def test_config_show_does_not_create_file(self) -> None:
        code, result = self.capture(ai_squish.show_config)
        self.assertEqual(code, 0)
        self.assertFalse(result["configured"])
        self.assertFalse(self.config.exists())

    def test_config_round_trip(self) -> None:
        code, saved = self.capture(ai_squish.set_config, str(self.output))
        self.assertEqual(code, 0)
        self.assertTrue(saved["configured"])
        self.assertTrue(self.output.is_dir())

        code, shown = self.capture(ai_squish.show_config)
        self.assertEqual(code, 0)
        self.assertTrue(shown["configured"])
        self.assertEqual(Path(shown["output_root"]), self.output.resolve())

    def test_topics_are_unique(self) -> None:
        code, result = self.capture(ai_squish.choose_topics, 8)
        self.assertEqual(code, 0)
        self.assertEqual(result["count"], 8)
        topics = [item["topic"] for item in result["topics"]]
        self.assertEqual(len(topics), len(set(topics)))

    def test_sanitize_topic_for_directory_name(self) -> None:
        self.assertEqual(ai_squish.sanitize_topic('  草莓 / 果冻:*?  '), "草莓-果冻")
        self.assertEqual(ai_squish.sanitize_topic("CON"), "topic-CON")
        self.assertEqual(ai_squish.sanitize_topic("***"), "untitled")

    def test_create_run_increments_duplicate_name(self) -> None:
        self.capture(ai_squish.set_config, str(self.output))
        fixed = ai_squish.datetime(2026, 7, 21, 12, 34, 56)
        with patch.object(ai_squish, "datetime") as mocked_datetime:
            mocked_datetime.now.return_value = fixed
            first_code, first = self.capture(ai_squish.create_run, "草莓果冻")
            second_code, second = self.capture(ai_squish.create_run, "草莓果冻")

        self.assertEqual(first_code, 0)
        self.assertEqual(second_code, 0)
        self.assertNotEqual(first["run_dir"], second["run_dir"])
        self.assertTrue(second["run_dir"].endswith("-02"))
        record = json.loads(Path(first["run_file"]).read_text(encoding="utf-8"))
        self.assertEqual(record["topic"], "草莓果冻")
        self.assertEqual(record["state"], "AWAITING_IMAGE_APPROVAL")

    def test_create_run_requires_configuration(self) -> None:
        with self.assertRaises(ai_squish.CliError):
            ai_squish.create_run("土豆")


if __name__ == "__main__":
    unittest.main()
