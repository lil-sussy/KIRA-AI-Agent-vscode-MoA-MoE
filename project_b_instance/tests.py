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
        db.delete_collection(db.list_collections()[0].name)
        pass

    def test_synchronize_instances(self):
        # Create and commit various changes
        # 1. Delete a file
        file_to_delete = os.path.join(self.fake_project_b_path, 'file1.txt')
        os.remove(file_to_delete)
        subprocess.run(["git", "rm", "file1.txt"], cwd=self.fake_project_b_path)
        subprocess.run(["git", "commit", "-m", "Deleted file1.txt"], cwd=self.fake_project_b_path)
        
        # 2. Rename a file
        old_file = os.path.join(self.fake_project_b_path, 'file2.txt')
        new_file = os.path.join(self.fake_project_b_path, 'file2_renamed.txt')
        os.rename(old_file, new_file)
        subprocess.run(["git", "add", "file2_renamed.txt"], cwd=self.fake_project_b_path)
        subprocess.run(["git", "commit", "-m", "Renamed file2.txt to file2_renamed.txt"], cwd=self.fake_project_b_path)

        # 3. Move a file
        old_file = os.path.join(self.fake_project_b_path, 'subdir/file3.txt')
        new_location = os.path.join(self.fake_project_b_path, 'subdir/subsubdir/')
        os.makedirs(new_location, exist_ok=True)
        new_file = os.path.join(new_location, 'file3_moved.txt')
        shutil.move(old_file, new_file)
        subprocess.run(["git", "add", 'subdir/subsubdir/file3_moved.txt'], cwd=self.fake_project_b_path)
        subprocess.run(["git", "add", "-u"], cwd=self.fake_project_b_path)  # Ensure deletions are tracked
        subprocess.run(["git", "commit", "-m", "Moved file3.txt to subdir/subsubdir/file3_moved.txt"], cwd=self.fake_project_b_path)

        # 4. Create a new file
        new_file = os.path.join(self.fake_project_b_path, 'newdir/file4.txt')
        os.makedirs(os.path.dirname(new_file), exist_ok=True)
        with open(new_file, 'w') as f:
            f.write('This is the content of file4.')
        subprocess.run(["git", "add", 'newdir/file4.txt'], cwd=self.fake_project_b_path)
        subprocess.run(["git", "commit", "-m", "Created new file newdir/file4.txt"], cwd=self.fake_project_b_path)

        # 5. Update an existing file
        file_to_update = os.path.join(self.fake_project_b_path, 'subdir/subsubdir/file3_moved.txt')
        with open(file_to_update, 'a') as f:
            f.write(' This is an update to the content of file3.')
        subprocess.run(["git", "add", 'subdir/subsubdir/file3_moved.txt'], cwd=self.fake_project_b_path)
        subprocess.run(["git", "commit", "-m", "Updated file3_moved.txt"], cwd=self.fake_project_b_path)

        # Create uncommitted changes
        # Create a new file without committing
        uncommitted_file = os.path.join(self.fake_project_b_path, 'uncommitted_file.txt')
        with open(uncommitted_file, 'w') as f:
            f.write('This is an uncommitted file.')

        # Modify an existing file without committing
        with open(file_to_update, 'a') as f:
            f.write(' Another uncommitted change to file3_moved.txt.')

        # Apply updates
        self.project_b_instance.apply_updates()

        # Verification
        # Check if all changes are correctly reflected
        def compare_file_content(path, expected_content):
            with open(path, 'r') as f:
                return f.read() == expected_content

        # File system verification
        expected_files = {
            'file2_renamed.txt': 'This is the content of file2.',
            'subdir/subsubdir/file3_moved.txt': 'This is the content of file3. This is an update to the content of file3. Another uncommitted change to file3_moved.txt.',
            'newdir/file4.txt': 'This is the content of file4.',
            'uncommitted_file.txt': 'This is an uncommitted file.'
        }

        for path, content in expected_files.items():
            full_path = os.path.join(self.fake_project_b_path, path)
            self.assertTrue(os.path.exists(full_path), f"{path} does not exist.")
            self.assertTrue(compare_file_content(full_path, content), f"Content of {path} does not match expected content.")

        # Database verification
        client = chromadb.PersistentClient(path=settings.CHRMADB_PERSIST_DIR)
        collection = client.get_collection(self.fake_project_b_path.replace('/','.')[3:-1])
        for path in expected_files:
            result = collection.query(query_texts=[path], n_results=1)
            self.assertEqual(result['documents'][0], expected_files[path], f"Content of {path} in database does not match expected content.")