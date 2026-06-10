import os
import re
from typing import List, Dict

class ProjectAnalyzer:
    """Analyzes the local project for readiness to be pushed to Git."""

    SECRET_PATTERNS = [
        re.compile(r'api_key\s*=\s*["\'].*["\']', re.IGNORECASE),
        re.compile(r'secret\s*=\s*["\'].*["\']', re.IGNORECASE),
        re.compile(r'password\s*=\s*["\'].*["\']', re.IGNORECASE),
        re.compile(r'token\s*=\s*["\'].*["\']', re.IGNORECASE),
    ]

    def __init__(self, project_path: str):
        self.project_path = project_path

    def check_readme(self) -> bool:
        """Returns True if README.md exists, False otherwise."""
        return os.path.exists(os.path.join(self.project_path, 'README.md'))

    def scan_for_secrets(self) -> List[Dict[str, any]]:
        """Scans files for potential hardcoded secrets."""
        findings = []
        for root, _, files in os.walk(self.project_path):
            # Skip .git and common dependency folders
            if '.git' in root or 'node_modules' in root or 'venv' in root:
                continue

            for file in files:
                if file.endswith(('.py', '.js', '.env', '.txt', '.json')):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            for line_no, line in enumerate(f, 1):
                                for pattern in self.SECRET_PATTERNS:
                                    if pattern.search(line):
                                        findings.append({
                                            'file': os.path.relpath(file_path, self.project_path),
                                            'line': line_no,
                                            'content': line.strip()
                                        })
                    except Exception as e:
                        print(f"Error reading {file_path}: {e}")
        return findings

    def analyze(self) -> Dict[str, any]:
        """Performs a full analysis of the project."""
        return {
            'has_readme': self.check_readme(),
            'secrets': self.scan_for_secrets(),
            'project_size': self._get_project_size()
        }

    def _get_project_size(self) -> int:
        """Counts number of files in the project."""
        count = 0
        for root, _, files in os.walk(self.project_path):
            if '.git' in root: continue
            count += len(files)
        return count
