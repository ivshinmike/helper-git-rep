from flask import Flask, request, jsonify
import os
from app.core.agents.orchestrator import OrchestratorAgent
from app.core.llm_client import LLMClient

app = Flask(__name__)

# Initialize the Orchestrator and LLM Client
llm_client = LLMClient()
orchestrator = OrchestratorAgent(llm_client=llm_client)

@app.route('/api/migrate', methods=['POST'])
def migrate_project():
    """
    Triggers the migration process for a local project.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON payload provided"}), 400

    project_path = data.get("project_path")
    repo_name = data.get("repo_name")
    force_restart = data.get("force_restart", False)

    if not project_path or not repo_name:
        return jsonify({"error": "project_path and repo_name are required"}), 400

    # The orchestrator handles the full sequence: Analyze -> Clean -> Document -> Publish
    result = orchestrator.execute({
        "project_path": project_path,
        "repo_name": repo_name,
        "force_restart": force_restart
    })

    if result["success"]:
        return jsonify({
            "status": "success",
            "final_status": result.get("final_status"),
            "repo_name": result.get("repo_name"),
            "message": "Project successfully migrated to GitHub"
        }), 200
    else:
        return jsonify({
            "status": "error",
            "error": result.get("error"),
            "failed_phase": result.get("failed_phase")
        }), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """
    Returns the status of all projects tracked by the state manager.
    """
    from app.core.state_manager import StateManager
    sm = StateManager()
    projects = sm.get_pending_projects()

    return jsonify({
        "projects": projects
    }), 200

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "version": "1.0.0-MVP"}), 200

if __name__ == "__main__":
    # Using a different port to avoid conflicts with future frontend
    app.run(debug=True, port=5000)
