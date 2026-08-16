import ast
from pathlib import Path

from django.test import SimpleTestCase


class SecurityConfigurationTests(SimpleTestCase):
    def test_smtp_credentials_are_not_literal_values(self):
        project_root = Path(__file__).resolve().parents[2]
        settings_path = (
            project_root
            / 'electrolineras_project'
            / 'electrolineras_project'
            / 'settings.py'
        )
        tree = ast.parse(settings_path.read_text(encoding='utf-8'))
        credential_names = {'EMAIL_HOST_USER', 'EMAIL_HOST_PASSWORD'}
        assignments = {}

        for node in ast.walk(tree):
            if not isinstance(node, ast.Assign) or len(node.targets) != 1:
                continue
            target = node.targets[0]
            if isinstance(target, ast.Name) and target.id in credential_names:
                assignments[target.id] = node.value

        self.assertEqual(set(assignments), credential_names)
        for name, value in assignments.items():
            self.assertIsInstance(
                value,
                ast.Call,
                msg=f'{name} must be loaded from the environment',
            )

    def test_dotenv_files_are_ignored(self):
        project_root = Path(__file__).resolve().parents[2]
        gitignore = (project_root / '.gitignore').read_text(encoding='utf-8')

        self.assertIn('.env\n', gitignore)
        self.assertIn('.env.*\n', gitignore)
