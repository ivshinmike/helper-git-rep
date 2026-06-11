from typing import Any, Dict, Optional
import os
from app.core.agents.base import BaseAgent
from app.core.generator import READMEGenerator
from app.core.llm_client import LLMClient

class ContentAgent(BaseAgent):
    """
    Content Agent (The Technical Writer).
    Responsible for understanding the project purpose and generating high-quality documentation.
    """

    def __init__(self, llm_client: Optional[LLMClient] = None):
        super().__init__("Content", llm_client)
        # We use the same llm_client instance to share session/config
        self.generator = None
        # Generator will be initialized per project path in execute()

    def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes content-related tasks.

        Expected task_data keys:
        - action: 'analyze_content' | 'generate_readme' | 'validate_readme' | 'maintenance_readme_audit'
        - project_path: absolute path to the local project
        - repo_name: (optional) name for the GitHub repository
        """
        action = task_data.get("action")
        project_path = task_data.get("project_path")

        if not project_path:
            self.log("Missing project_path in task data", "error")
            return {"success": False, "error": "project_path is required"}

        # Initialize generator for the specific project
        self.generator = READMEGenerator(project_path)

        if action == "analyze_content":
            return self._handle_analyze_content(project_path)
        elif action == "generate_readme":
            return self._handle_generate_readme(task_data)
        elif action == "validate_readme":
            return self._handle_validate_readme(project_path)
        elif action == "maintenance_readme_audit":
            return self._handle_maintenance_readme_audit(task_data)
        else:
            self.log(f"Unknown action: {action}", "error")
            return {"success": False, "error": f"Unknown action: {action}"}

    def _handle_analyze_content(self, project_path: str) -> Dict[str, Any]:
        """
        Gathers the structural and code context of the project to understand its purpose.
        """
        self.log("Analyzing project content to understand its purpose...")
        context = self.generator.collect_context()

        # We can use LLM to summarize the project's purpose in one sentence
        # This summary can be used by the Orchestrator to verify if the project is even worth publishing
        summary = self.llm_client.generate_text(
            prompt=f"Analyze this project structure and code snippets. In one short sentence, describe what this project does. Project context: {context}"
        )

        self.log(f"Project summary: {summary}")
        return {
            "success": True,
            "summary": summary,
            "context": context
        }

    def _handle_generate_readme(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates a professional README.md using LLM context.
        """
        project_path = task_data.get("project_path")
        repo_name = task_data.get("repo_name", "Unknown Project")
        language = task_data.get("language", "en")

        self.log(f"Generating professional README for {repo_name} in {language}...")

        # 1. Get context from the generator
        context = self.generator.collect_context()

        # 2. Create the prompt based on the template and language
        prompt = self.generator.generate_prompt(language=language)

        # 3. Generate content using the LLMClient
        content = self.llm_client.generate_text(prompt=prompt)

        if not content:
            self.log("LLM failed to generate README content", "error")
            return {"success": False, "error": "LLM generation failed"}

        # 4. Write to file
        if self.generator.write_readme(content):
            self.log("✅ README.md successfully written to disk.")
            return {
                "success": True,
                "content": content
            }
        else:
            self.log("Error writing README.md to file system", "error")
            return {"success": False, "error": "FileSystem write error"}

    def _handle_validate_readme(self, project_path: str) -> Dict[str, Any]:
        """
        Checks if the generated README is of high quality.
        """
        self.log("Validating generated README quality...")

        # Read the existing README.md
        try:
            with open(os.path.join(project_path, 'README.md'), 'r', encoding='utf-8') as f:
                readme_content = f.read()
        except Exception as e:
            self.log(f"Could not read README.md: {e}", "error")
            return {"success": False, "error": "README.md not found or unreadable"}

        # Ask LLM to validate the README
        validation_prompt = (
            f"Review this README.md content. Does it accurately describe the project based on the project context? "
            f"Is it professional, formatted correctly in Markdown and complete? "
            f"Return ONLY 'VALID' or 'INVALID' with a brief reason."
        )

        # We need the project context for validation
        context = self.generator.collect_context()
        full_validation_prompt = f"Context: {context}\n\nREADME: {readme_content}\n\n{validation_prompt}"

        verdict = self.llm_client.generate_text(prompt=full_validation_prompt)

        if verdict and "VALID" in verdict.upper():
            self.log("README validation successful.")
            return {"success": True, "grade": "A"}
        else:
            self.log(f"README validation failed: {verdict}", "warning")
            return {"success": False, "error": f"Validation failed: {verdict}"}

    def _handle_maintenance_readme_audit(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Audits existing README and updates it if necessary.
        """
        project_path = task_data.get("project_path")
        repo_name = task_data.get("repo_name", "Unknown Project")
        language = task_data.get("language", "en")

        self.log(f"Auditing README.md for {repo_name}...")

        # 1. Check if README exists
        try:
            with open(os.path.join(project_path, 'README.md'), 'r', encoding='utf-8') as f:
                current_readme = f.read()
        except Exception:
            self.log("README.md not found. Falling back to full generation.")
            # If it doesn't exist, just generate a new one
            return self._handle_generate_readme(task_data)

        # 2. Run audit
        audit_prompt = self.generator.generate_audit_prompt(current_readme, language=language)
        verdict = self.llm_client.generate_text(prompt=audit_prompt)

        if verdict and "VALID" == verdict.strip().upper():
            self.log("README.md is already professional and complete.")
            return {"success": True, "status": "valid"}
        else:
            self.log(f"README.md audit failed: {verdict}. Generating improved version...")
            # If invalid, we generate a new one (or we could prompt for a diff, but for now full regen is safer)
            return self._handle_generate_readme(task_data)
