import os

class ProjectCleaner:
    """Handles cleaning of the project: .gitignore management and secret hiding."""

    DEFAULT_GITIGNORE = """
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# Environments
.env
.venv
env/
venv/
ENV/

# IDEs
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
"""

    def __init__(self, project_path: str):
        self.project_path = project_path

    def ensure_gitignore(self) -> bool:
        """Creates a .gitignore file if it doesn't exist or adds common defaults."""
        gitignore_path = os.path.join(self.project_path, '.gitignore')
        if not os.path.exists(gitignore_path):
            with open(gitignore_path, 'w', encoding='utf-8') as f:
                f.write(self.DEFAULT_GITIGNORE)
            return True
        return False

    def add_to_gitignore(self, pattern: str) -> bool:
        """Adds a specific pattern to .gitignore if not already present."""
        gitignore_path = os.path.join(self.project_path, '.gitignore')
        if not os.path.exists(gitignore_path):
            self.ensure_gitignore()

        with open(gitignore_path, 'r') as f:
            lines = f.readlines()

        if any(pattern in line for line in lines):
            return False

        with open(gitignore_path, 'a') as f:
            f.write(f"\n{pattern}\n")
        return True

    def clean_secrets(self, secrets: list) -> int:
        """
        Informational tool: in a real agent, this might prompt the user
        to replace secrets with env vars. For now, it marks files for review.
        """
        # In MVP, we mainly rely on .gitignore for .env files.
        # For hardcoded secrets in .py files, we report them.
        return len(secrets)
