import os
import shutil
import json
from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
from project_b_instance.ProjectBInstance import ProjectBInstance
import subprocess
import chromadb
import server_app.settings as settings

class ProjectBInstanceTestCase(TestCase):
    def setUp(self):
        self.fake_project_b_path = './test/fake_project_b/'
        self.client = Client()
        os.makedirs(os.path.join(self.fake_project_b_path, 'subdir'), exist_ok=True)

        files = {
            'file1.txt': 'This is the content of file1.',
            'file2.txt': 'This is the content of file2.',
            'subdir/file3.txt': 'This is the content of file3.',
        }

        for path, content in files.items():
            full_path = os.path.join(self.fake_project_b_path, path)
            with open(full_path, 'w') as f:
                f.write(content)
        
        subprocess.run(["git", "init"], cwd=self.fake_project_b_path)
        subprocess.run(["git", "add", "."], cwd=self.fake_project_b_path)
        subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=self.fake_project_b_path)
        self.project_b_instance = ProjectBInstance(self.fake_project_b_path)
        print("Instance initialization successful and verified.")

    def tearDown(self):
        shutil.rmtree(self.fake_project_b_path)
        db = chromadb.PersistentClient(path=settings.CHRMADB_PERSIST_DIR)
        db.list_collections()[0].delete()
        pass

    def test_synchronize_instances(self):
        pass
