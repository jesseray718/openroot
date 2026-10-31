"""Import helper so tests can load a file whose name contains a hyphen."""
import importlib.util
import os


def load():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "openroot-classifier.py")
    spec = importlib.util.spec_from_file_location("openroot_classifier", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
