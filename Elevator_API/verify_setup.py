#!/usr/bin/env python3
"""Verification script to check if the backend is properly set up."""
import sys
from pathlib import Path


def check_file(path: Path, description: str) -> bool:
    """Check if a file exists."""
    if path.exists():
        print(f"✅ {description}: {path}")
        return True
    else:
        print(f"❌ {description}: {path} (NOT FOUND)")
        return False


def check_imports() -> bool:
    """Check if all required modules can be imported."""
    print("\n📦 Checking Python imports...")
    required_modules = [
        ("app.models", "Data models"),
        ("app.algorithm", "SCAN algorithm"),
        ("app.state", "State management"),
        ("app.schema", "GraphQL schema"),
        ("app.config", "Configuration"),
        ("app.notifications", "Notifications"),
        ("app.main", "FastAPI app"),
    ]

    all_ok = True
    for module_name, description in required_modules:
        try:
            __import__(module_name)
            print(f"✅ {description} ({module_name})")
        except ImportError as e:
            print(f"❌ {description} ({module_name}): {e}")
            all_ok = False

    return all_ok


def main():
    """Run verification checks."""
    print("🔍 Verifying Elevator System Backend Setup\n")
    print("=" * 60)

    backend_dir = Path(__file__).parent
    app_dir = backend_dir / "app"

    # Check files
    print("\n📁 Checking files...\n")
    checks = [
        (backend_dir / "pyproject.toml", "pyproject.toml"),
        (backend_dir / "requirements.txt", "requirements.txt"),
        (backend_dir / ".env.example", ".env.example"),
        (backend_dir / ".gitignore", ".gitignore"),
        (backend_dir / "README.md", "README.md"),
        (app_dir / "__init__.py", "app/__init__.py"),
        (app_dir / "main.py", "app/main.py"),
        (app_dir / "models.py", "app/models.py"),
        (app_dir / "algorithm.py", "app/algorithm.py"),
        (app_dir / "state.py", "app/state.py"),
        (app_dir / "schema.py", "app/schema.py"),
        (app_dir / "config.py", "app/config.py"),
        (app_dir / "notifications.py", "app/notifications.py"),
    ]

    files_ok = all(check_file(path, desc) for path, desc in checks)

    # Check if .env exists
    env_file = backend_dir / ".env"
    if env_file.exists():
        print(f"✅ .env file exists (configured)")
    else:
        print(f"⚠️  .env file not found (copy from .env.example)")

    # Check imports
    imports_ok = check_imports()

    # Summary
    print("\n" + "=" * 60)
    print("\n📊 Summary:\n")

    if files_ok and imports_ok:
        print("✅ All checks passed!")
        print("\n🚀 Ready to run:")
        print("   uvicorn app.main:app --reload --port 8000")
        print("\n📖 Then visit:")
        print("   http://localhost:8000/graphql (GraphQL playground)")
        print("   http://localhost:8000/health (Health check)")
        return 0
    else:
        print("❌ Some checks failed.")
        print("\n🔧 To fix:")
        print("   1. Install dependencies: uv pip install -e .")
        print("   2. Create .env file: cp .env.example .env")
        print("   3. Edit .env with your Resend API key")
        return 1


if __name__ == "__main__":
    sys.exit(main())
