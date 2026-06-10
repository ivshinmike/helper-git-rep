import subprocess
import os

class GitClient:
    """Wrapper for gh CLI and git commands."""

    def __init__(self, project_path: str):
        self.project_path = project_path

    def _run(self, cmd: list) -> subprocess.CompletedProcess:
        """Helper to run shell commands in the project directory."""
        return subprocess.run(
            cmd,
            cwd=self.project_path,
            capture_output=True,
            text=True,
            shell=False
        )

    def create_github_repo(self, repo_name: str, public: bool = True) -> bool:
        """Creates a repository on GitHub using gh cli."""
        visibility = "public" if public else "private"
        # gh repo create <name> --public/--private --source=. --remote=origin --push
        # We'll do it in steps for better error tracking
        cmd = ["gh", "repo", "create", repo_name, f"--{visibility}", "--source=."]
        result = self._run(cmd)
        return result.returncode == 0

    def init_git(self) -> bool:
        """Initializes a local git repository."""
        if os.path.exists(os.path.join(self.project_path, '.git')):
            return True

        result = self._run(["git", "init"])
        return result.returncode == 0

    def commit_and_push(self, message: str = "Initial commit from helper-git-rep") -> bool:
        """Adds all files, commits, and pushes to origin main."""
        # 1. git add .
        self._run(["git", "add", "."])

        # 2. git commit
        commit_res = self._run(["git", "commit", "-m", message])

        # 3. git push -u origin main
        # Note: gh repo create --source=. usually handles the remote and first push
        # But we do it explicitly for robustness.
        push_res = self._run(["git", "push", "-u", "origin", "main"])

        return push_res.returncode == 0

    def get_status(self) -> str:
        """Returns current git status."""
        result = self._run(["git", "status"])
        return result.stdout
