# tests/test_import_app.py
# Test to check if the main application module can be imported.
import importlib


def test_can_import_app():
    importlib.import_module("app")
