import unittest
from unittest.mock import patch

from app.services.openai_service import OpenAIService


class OpenAIServiceTest(unittest.TestCase):
    @patch("app.services.openai_service.OpenAI")
    def test_nvapi_key_uses_nvidia_base_url_by_default(self, openai: object) -> None:
        service = OpenAIService("nvapi-test-key", "openai/gpt-oss-120b")

        args = openai.call_args.kwargs
        self.assertEqual(args["api_key"], "nvapi-test-key")
        self.assertEqual(args["base_url"], "https://integrate.api.nvidia.com/v1")
        self.assertIn("http_client", args)
        self.assertEqual(service.base_url, "https://integrate.api.nvidia.com/v1")


if __name__ == "__main__":
    unittest.main()
