import pytest

from scripts.article_generator import ArticleGenerator


def test_valid_html():
    html = """<!DOCTYPE html><html lang='fr'><head><title>Test</title></head><body><h1>Hello</h1><p>Paragraphe</p></body></html>"""
    assert ArticleGenerator._is_valid_html(html) is True


def test_invalid_html():
    html = "<h1>Titre seul</h1>"
    assert ArticleGenerator._is_valid_html(html) is False 