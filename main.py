from flask import Flask, render_template, request, jsonify, Blueprint
import os
from app.core.agents.orchestrator import OrchestratorAgent
from app.core.llm_client import LLMClient

# Get the absolute path to the project root
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__,
            template_folder=os.path.join(BASE_DIR, 'app', 'web', 'templates'),
            static_folder=os.path.join(BASE_DIR, 'app', 'web', 'static'))

# API Blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/migrate', methods=['POST'])
def migrate_project():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON payload provided"}), 400

    project_path = data.get("project_path")
    repo_name = data.get("repo_name")
    force_restart = data.get("force_restart", False)
    language = data.get("language", "en")

    if not project_path or not repo_name:
        return jsonify({"error": "project_path and repo_name are required"}), 400

    try:
        llm_client = LLMClient()
        orchestrator = OrchestratorAgent(llm_client=llm_client)
        result = orchestrator.execute({
            "mode": "migrate",
            "project_path": project_path,
            "repo_name": repo_name,
            "force_restart": force_restart,
            "language": language
        })

        if result["success"]:
            return jsonify({
                "status": "success",
                "final_status": result.get("final_status"),
                "repo_name": result.get("repo_name")
            }), 200
        return jsonify({"status": "error", "error": result.get("error")}), 500
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

@api_bp.route('/maintenance', methods=['POST'])
def maintenance_project():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON payload provided"}), 400

    project_path = data.get("project_path")
    repo_name = data.get("repo_name")
    language = data.get("language", "en")

    if not project_path or not repo_name:
        return jsonify({"error": "project_path and repo_name are required"}), 400

    try:
        llm_client = LLMClient()
        orchestrator = OrchestratorAgent(llm_client=llm_client)
        result = orchestrator.execute({
            "mode": "maintenance",
            "project_path": project_path,
            "repo_name": repo_name,
            "language": language
        })

        if result["success"]:
            return jsonify({
                "status": "success",
                "maintenance_report": result
            }), 200
        return jsonify({"status": "error", "error": result.get("error")}), 500
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

@api_bp.route('/status', methods=['GET'])
def get_status():
    from app.core.state_manager import StateManager
    sm = StateManager()
    return jsonify({"projects": sm.get_pending_projects()}), 200

app.register_blueprint(api_bp)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    print("\n" + "="*50)
    print("🚀 Helper Git Rep is starting...")
    print(f"📂 Root directory: {BASE_DIR}")
    print(f"📁 Templates: {app.template_folder}")
    print(f"🌐 URL: http://127.0.0.1:5000")
    print("="*50 + "\n")
    app.run(debug=True, port=5000, host='0.0.0.0')
