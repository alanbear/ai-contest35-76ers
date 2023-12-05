from function_app import query_openai

import pytest


def test_query_openai():
    assert query_openai("QQ") == "Hello from Azure Functions!"