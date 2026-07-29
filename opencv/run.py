import sys, os

_VENV = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".venv", "Scripts", "python.exe")
if not os.path.exists(_VENV):
    print("No .venv found in project root. Run: python -m venv .venv && pip install -r requirements.txt")
    sys.exit(1)

_PYTHON = _VENV
os.execv(_PYTHON, [_PYTHON, os.path.join(os.path.dirname(os.path.abspath(__file__)), "core", "detectar.py")])
