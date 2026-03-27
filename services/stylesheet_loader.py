from pathlib import Path


_PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_stylesheet(relative_path: str) -> str:
    """Load a QSS stylesheet from the project directory."""
    return (_PROJECT_ROOT / relative_path).read_text(encoding="utf-8")
