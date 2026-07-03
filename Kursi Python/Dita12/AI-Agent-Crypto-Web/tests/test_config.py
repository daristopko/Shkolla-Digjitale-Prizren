import os
import unittest
from unittest.mock import patch

from app.config import Settings


class SettingsTest(unittest.TestCase):
    def test_openai_values_are_read_when_settings_is_created(self) -> None:
        with patch.dict(os.environ, {"OPENAI_API_KEY": "local-test-key", "OPENAI_MODEL": "test-model", "OPENAI_BASE_URL": "https://example.test/v1"}):
            settings = Settings()
        self.assertEqual(settings.openai_api_key, "local-test-key")
        self.assertEqual(settings.openai_model, "test-model")
        self.assertEqual(settings.openai_base_url, "https://example.test/v1")


if __name__ == "__main__":
    unittest.main()
