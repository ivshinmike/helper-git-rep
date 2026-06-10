from typing import Any, Dict, Optional
from app.core.agents.base import BaseAgent
from app.core.agents.infrastructure import InfrastructureAgent
from app.core.agents.content import ContentAgent
from app.core.state_manager import StateManager
from app.core.llm_client import LLMClient

class OrchestratorAgent(BaseAgent):
    """
    Orchestrator Agent (The Director).
    Coordinates the Infrastructure and Content agents to migrate a project to GitHub.
    """

    def __init__(self, llm_client: Optional[LLMClient] = None):
        super().__init__("Orchestrator", llm_client)

        # Initialize specialized agents
        self.infra_agent = InfrastructureAgent(llm_client=self.llm_client)
        self.content_agent = ContentAgent(llm_client=self.llm_client)
        self.state_manager = StateManager()

    def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for the orchestrator.
        Expected task_data keys:
        - project_path: absolute path to the local project
        - repo_name: name for the GitHub repository
        - force_restart: (optional) if True, starts from PENDING regardless of current state
        - language: (optional) 'en' or 'ru' for README generation
        """
        project_path = task_data.get("project_path")
        repo_name = task_data.get("repo_name")
        force_restart = task_data.get("force_restart", False)
        language = task_data.get("language", "en")

        if not project_path or not repo_name:
            self.log("Missing project_path or repo_name", "error")
            return {"success": False, "error": "project_path and repo_name are required"}

        self.log(f"Starting orchestration for project: {project_path} -> {repo_name}")

        # Determine starting status
        current_status = "PENDING"
        if not force_restart:
            status = self.state_manager.get_project_status(project_path)
            if status:
                current_status = status
                self.log(f"Resuming project from status: {current_status}")

        try:
            # 1. ANALYSIS PHASE
            if current_status == "PENDING":
                res = self.infra_agent.execute({"action": "analyze", "project_path": project_path})
                if not res["success"]:
                    return self._handle_failure("Analysis", res)

                self.state_manager.update_project_status(project_path, repo_name, "ANALYZED")
                current_status = "ANALYZED"
                self.log("Phase [Analysis] completed.")

            # 2. CLEANING PHASE
            if current_status == "ANALYZED":
                res = self.infra_agent.execute({"action": "clean", "project_path": project_path})
                if not res["success"]:
                    return self._handle_failure("Cleaning", res)

                self.state_manager.update_project_status(project_path, repo_name, "CLEANED")
                current_status = "CLEANED"
                self.log("Phase [Cleaning] completed.")

            # 3. DOCUMENTATION PHASE
            if current_status == "CLEANED":
                # a) Understand purpose
                analysis_res = self.content_agent.execute({"action": "analyze_content", "project_path": project_path})
                if not analysis_res["success"]:
                    return self._handle_failure("Content Analysis", analysis_res)

                # b) Generate README
                gen_res = self.content_agent.execute({
                    "action": "generate_readme",
                    "project_path": project_path,
                    "repo_name": repo_name,
                    "language": task_data.get("language", "en")
                })
                if not gen_res["success"]:
                    return self._handle_failure("README Generation", gen_res)

                # c) Validate README
                val_res = self.content_agent.execute({"action": "validate_readme", "project_path": project_path})
                if not val_res["success"]:
                    self.log(f"README validation failed: {val_res.get('error')}. Proceeding anyway, but marking for review.", "warning")

                self.state_manager.update_project_status(project_path, repo_name, "DOCUMENTED")
                current_status = "DOCUMENTED"
                self.log("Phase [Documentation] completed.")

            # 4. PUBLISHING PHASE
            if current_status == "DOCUMENTED":
                res = self.infra_agent.execute({
                    "action": "publish",
                    "project_path": project_path,
                    "repo_name": repo_name
                })
                if not res["success"]:
                    return self._handle_failure("Publishing", res)

                self.state_manager.update_project_status(project_path, repo_name, "COMPLETED")
                current_status = "COMPLETED"
                self.log("Phase [Publishing] completed.")

            self.log(f"✨ Successfully migrated {project_path} to GitHub as {repo_name}!")
            return {
                "success": True,
                "final_status": current_status,
                "repo_name": repo_name
            }

        except Exception as e:
            self.log(f"Unexpected error during orchestration: {e}", "error")
            return {"success": False, "error": str(e)}

    def _handle_failure(self, phase: str, result: Dict[str, Any]) -> Dict[str, Any]:
        error_msg = result.get("error", "Unknown error")
        self.log(f"Failure in phase [{phase}]: {error_msg}", "error")
        return {
            "success": False,
            "failed_phase": phase,
            "error": error_msg
        }
