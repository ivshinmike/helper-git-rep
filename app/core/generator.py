import os
from typing import List

class READMEGenerator:
    """Generates a meaningful README based on project analysis."""

    def __init__(self, project_path: str):
        self.project_path = project_path

    def collect_context(self) -> str:
        """Gathers file structure and snippets of key files for the LLM."""
        context = []
        context.append("Project Structure:")

        for root, dirs, files in os.walk(self.project_path):
            # Skip hidden dirs and common junk
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ('node_modules', 'venv', '__pycache__')]

            level = root.replace(self.project_path, '').count(os.sep)
            indent = ' ' * 4 * (level)
            context.append(f"{indent}{os.path.basename(root)}/")
            sub_indent = ' ' * 4 * (level + 1)
            for f in files:
                if not f.startswith('.'):
                    context.append(f"{sub_indent}{f}")

        context.append("\nKey File Contents:")
        # Collect a few important files to help the LLM understand the project
        important_files = ['main.py', 'app.py', 'index.html', 'requirements.txt', 'package.json']
        for root, _, files in os.walk(self.project_path):
            for f in files:
                if f in important_files:
                    file_path = os.path.join(root, f)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as content_file:
                            content = content_file.read()[:1000] # Limit to 1000 chars per file
                            context.append(f"\n--- {f} ---\n{content}")
                    except Exception as e:
                        context.append(f"\nCould not read {f}: {e}")

        return "\n".join(context)

    def generate_prompt(self, language: str = 'en') -> str:
        """Creates a prompt for the LLM to generate the README in the specified language."""
        context = self.collect_context()

        lang_instruction = "English" if language == 'en' else "Russian"

        prompt = f"""
You are an expert Technical Writer. Based on the following project context, generate a professional and comprehensive README.md file in {lang_instruction} language.

PROJECT CONTEXT:
{context}

The README should include:
1. A catchy Project Title.
2. A clear, concise Description of what the project does.
3. Key Features list.
4. Tech Stack used.
5. Installation instructions (based on the detected files like requirements.txt).
6. How to run the project.
7. A professional structure.

Use Markdown formatting. Return ONLY the content of the README.md file in {lang_instruction}.
"""
        return prompt

    def write_readme(self, content: str) -> bool:
        """Writes the generated content to README.md."""
        try:
            with open(os.path.join(self.project_path, 'README.md'), 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error writing README.md: {e}")
            return False
