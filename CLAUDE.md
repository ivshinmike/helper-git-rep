# Helper Git Rep
This project is an agent-based tool to help users move local projects to GitHub repositories.

## Core Workflow
1. **Analyze**: Scan for README, secrets, and project structure.
2. **Clean**: Ensure .gitignore is present and secrets are hidden.
3. **Generate**: Use LLM to create a meaningful README.md.
4. **Publish**: Use `gh` CLI to create a remote repo and push code.

## Tech Stack
- Python 3.10+
- Flask (for Web UI)
- GitHub CLI (`gh`)
- LLM API (for README generation)

## Guidelines
- Match Python naming conventions (snake_case).
- Use clear logging for the agent's decision process.
- Ensure all `gh` commands are executed with proper error handling.

## Communication & Workflow Preferences
- **Planning**: Always provide a detailed action plan for approval before starting non-trivial tasks.
- **Reporting**: After completing work, provide a summary of changes and a list of modified/created files.
- **Style**:
    - Avoid long introductions or "souless" confirmations (e.g., "Of course!", "Certainly!").
    - Be concise; avoid explaining basic concepts unless requested.
    - Deliver concrete, actionable insights.
- **Constraints**: Do not delete or rename files, change system configs, or send external notifications without explicit permission.
