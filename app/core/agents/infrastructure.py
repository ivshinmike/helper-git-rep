from typing import Any, Dict
from app.core.agents.base import BaseAgent
from app.core.analyzer import ProjectAnalyzer
from app.core.cleaner import ProjectCleaner
from app.core.git_client import GitClient

class InfrastructureAgent(BaseAgent):
    """
    Infrastructure Agent (The Engineer).
    Responsible for project analysis, cleaning, and GitHub publication.
    """

    def __init__(self, llm_client=None):
        super().__init__("Infrastructure", llm_client)

    def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes infrastructure tasks based on the provided action.

        Expected task_data keys:
        - action: 'analyze' | 'clean' | 'publish' | 'maintenance_analyze' | 'maintenance_clean'
        - project_path: absolute path to the local project
        - repo_name: (optional) name for the GitHub repository
        """
        action = task_data.get("action")
        project_path = task_data.get("project_path")

        if not project_path:
            self.log("Missing project_path in task data", "error")
            return {"success": False, "error": "project_path is required"}

        if action == "analyze":
            return self._handle_analyze(project_path)
        elif action == "clean":
            return self._handle_clean(project_path)
        elif action == "publish":
            repo_name = task_data.get("repo_name")
            if not repo_name:
                self.log("Missing repo_name for publish action", "error")
                return {"success": False, "error": "repo_name is required for publishing"}
            return self._handle_publish(project_path, repo_name)
        elif action == "maintenance_analyze":
            return self._handle_maintenance_analyze(project_path)
        elif action == "maintenance_clean":
            return self._handle_maintenance_clean(project_path)
        else:
            self.log(f"Unknown action: {action}", "error")
            return {"success": False, "error": f"Unknown action: {action}"}

    def _handle_analyze(self, project_path: str) -> Dict[str, Any]:
        self.log(f"Analyzing project at {project_path}...")
        analyzer = ProjectAnalyzer(project_path)
        analysis = analyzer.analyze()

        self.log(f"Analysis complete. Found {len(analysis['secrets'])} potential secrets.")
        return {
            "success": True,
            "data": analysis
        }

    def _handle_clean(self, project_path: str) -> Dict[str, Any]:
        self.log(f"Cleaning project at {project_path}...")
        cleaner = ProjectCleaner(project_path)

        # 1. Ensure basic .gitignore
        cleaner.ensure_gitignore()

        # 2. Scan for secrets and add them to .gitignore
        analyzer = ProjectAnalyzer(project_path)
        secrets = analyzer.scan_for_secrets()

        for secret in secrets:
            # we add the filename to .gitignore if it's a known secret-holding file like .env
            filename = secret['file']
            if filename.startswith('.env') or filename.endswith('.env'):
                cleaner.add_to_gitignore(filename)

        self.log("Project cleaning completed.")
        return {
            "success": True,
            "secrets_found": len(secrets),
            "gitignore_updated": True
        }

    def _handle_publish(self, project_path: str, repo_name: str) -> Dict[str, Any]:
        self.log(f"Publishing project to GitHub as '{repo_name}'...")
        git = GitClient(project_path)

        # 1. Local Git Init
        if not git.init_git():
            self.log("Failed to initialize local git repository", "error")
            return {"success": False, "error": "git init failed"}
        self.log("Git initialized locally.")

        # 2. Create GitHub Repo
        if not git.create_github_repo(repo_name):
            self.log(f"Failed to create GitHub repository '{repo_name}'", "error")
            return {"success": False, "error": "gh repo create failed"}
        self.log(f"Remote repository '{repo_name}' created successfully.")

        # 3. Commit and Push
        if not git.commit_and_push():
            self.log("Failed to commit and push code to GitHub", "error")
            return {"success": False, "error": "git push failed"}
        self.log("Project committed and pushed successfully.")

        return {
            "success": True,
            "repo_url": f"https://github.com/user/{repo_name}" # Note: GitClient doesn't return the URL, would need to improve GitClient
        }

    def _handle_maintenance_analyze(self, project_path: str) -> Dict[str, Any]:
        self.log(f"Performing maintenance analysis for project at {project_path}...")
        git = GitClient(project_path)
        analyzer = ProjectAnalyzer(project_path)

        analysis = analyzer.analyze()

        report = {
            "is_git_repo": git.is_git_repo(),
            "remote_url": git.get_remote_url(),
            "has_readme": analysis['has_readme'],
            "secrets_found": len(analysis['secrets']),
            "secrets_details": analysis['secrets'],
            "project_size": analysis['project_size']
        }

        self.log(f"Maintenance analysis complete. Repo: {report['is_git_repo']}, README: {report['has_readme']}, Secrets: {report['secrets_found']}")
        return {"success": True, "data": report}

    def _handle_maintenance_clean(self, project_path: str) -> Dict[str, Any]:
        self.log(f"Performing maintenance cleaning for project at {project_path}...")
        cleaner = ProjectCleaner(project_path)
        analyzer = ProjectAnalyzer(project_path)

        # Ensure .gitignore
        cleaner.ensure_gitignore()

        secrets = analyzer.scan_for_secrets()
        for secret in secrets:
            filename = secret['file']
            if filename.startswith('.env') or filename.endswith('.env'):
                cleaner.add_to_gitignore(filename)

        self.log("Maintenance cleaning completed.")
        return {
            "success": True,
            "secrets_found": len(secrets),
            "gitignore_updated": True
        }
