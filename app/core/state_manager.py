import json
import os
from datetime import datetime
from typing import Dict, Optional

class StateManager:
    """Handles persistence of project processing state."""

    STATE_FILE = ".helper_git_state.json"

    def __init__(self):
        self.state_path = os.path.join(os.getcwd(), self.STATE_FILE)
        self.state = self._load_state()

    def _load_state(self) -> Dict:
        if os.path.exists(self.state_path):
            try:
                with open(self.state_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading state file: {e}")
                return {"projects": {}}
        return {"projects": {}}

    def save_state(self):
        try:
            with open(self.state_path, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, indent=4)
        except Exception as e:
            print(f"Error saving state: {e}")

    def update_project_status(self, project_path: str, repo_name: str, status: str):
        """Updates the status of a project. Using path as key for simplicity."""
        abs_path = os.path.abspath(project_path)
        if "projects" not in self.state:
            self.state["projects"] = {}

        self.state["projects"][abs_path] = {
            "repo_name": repo_name,
            "status": status,
            "last_updated": datetime.now().isoformat()
        }
        self.save_state()

    def get_project_status(self, project_path: str) -> Optional[str]:
        abs_path = os.path.abspath(project_path)
        project = self.state.get("projects", {}).get(abs_path)
        return project["status"] if project else None

    def get_pending_projects(self) -> Dict[str, Dict]:
        """Returns projects that are not yet COMPLETED."""
        return {path: info for path, info in self.state.get("projects", {}).items()
                if info["status"] != "COMPLETED"}

    def clear_project(self, project_path: str):
        abs_path = os.path.abspath(project_path)
        if abs_path in self.state.get("projects", {}):
            del self.state["projects"][abs_path]
            self.save_state()
