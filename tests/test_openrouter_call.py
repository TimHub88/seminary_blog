import json
from unittest.mock import patch
import pytest

from scripts.article_generator import ArticleGenerator


def fake_post(url, headers=None, json=None, timeout=60):
    class FakeResponse:
        status_code = 200
        def json(self_inner):
            return {
                "choices": [
                    {"message": {"content": "<h1>Titre</h1><p>Contenu de test</p>"}}
                ]
            }
        def raise_for_status(self_inner):
            pass
    return FakeResponse()

@patch('scripts.article_generator.requests.post', side_effect=fake_post)
def test_openrouter_call(mock_post):
    gen = ArticleGenerator(openrouter_api_key="test_key")
    result = gen.call_openrouter_api("Bonjour", max_tokens=10)
    assert result.startswith("<h1>") 