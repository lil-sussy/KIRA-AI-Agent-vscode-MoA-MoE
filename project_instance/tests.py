import os
import shutil
import json
from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
from .models import ProjectBInstance

class ProjectBInstanceTestCase(TestCase):
    def setUp(self):
        # Set up the fake project B folder
        self.fake_project_b_path = './test/fake_project_b/'
        self.local_instance_path = './test/local_instance/'
        self.client = Client()
        
        os.makedirs(self.fake_project_b_path, exist_ok=True)
        os.makedirs(self.local_instance_path, exist_ok=True)
        os.makedirs(os.path.join(self.fake_project_b_path, 'folder1'), exist_ok=True)
        os.makedirs(os.path.join(self.local_instance_path, 'folder1'), exist_ok=True)
        
        with open(os.path.join(self.fake_project_b_path, 'folder1', 'file1.txt'), 'w') as f:
            f.write('This is file1.')
        
        with open(os.path.join(self.fake_project_b_path, 'file2.txt'), 'w') as f:
            f.write('This is file2.')

        # Initialize Git repository
        os.system(f'git init {self.fake_project_b_path}')
        
        # Initialize ProjectBInstance
        self.project_b_instance = ProjectBInstance(self.fake_project_b_path)

        # Perform fake edits and commits
        os.system(f'echo "Edit in file1" > {self.fake_project_b_path}/folder1/file1.txt')
        os.system(f'git -C {self.fake_project_b_path} add folder1/file1.txt')
        os.system(f'git -C {self.fake_project_b_path} commit -m "Edit file1.txt"')

        os.system(f'echo "This is file3." > {self.fake_project_b_path}/file3.txt')
        os.system(f'git -C {self.fake_project_b_path} add file3.txt')
        os.system(f'git -C {self.fake_project_b_path} commit -m "Add file3.txt"')

        os.system(f'rm {self.fake_project_b_path}/file2.txt')
        os.system(f'git -C {self.fake_project_b_path} rm file2.txt')
        os.system(f'git -C {self.fake_project_b_path} commit -m "Delete file2.txt"')

        # Make changes without committing
        os.system(f'echo "Uncommitted edit in file1" >> {self.fake_project_b_path}/folder1/file1.txt')
        os.system(f'echo "This is uncommitted file4." > {self.fake_project_b_path}/file4.txt')

    def tearDown(self):
        # Clean up by removing the fake project B folder
        shutil.rmtree(self.fake_project_b_path)
        shutil.rmtree(self.local_instance_path)

    @patch('project_b_instance.models.ProjectBInstance.generate_update_list')
    def test_generate_update_list_view(self, mock_generate_update_list):
        mock_generate_update_list.return_value = ['update1', 'update2']
        response = self.client.get(reverse('generate_update_list'))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, ['update1', 'update2'])

    @patch('project_b_instance.models.ProjectBInstance.add_files_to_db')
    def test_store_files_in_db_view(self, mock_add_files_to_db):
        file_paths = [os.path.join(self.fake_project_b_path, 'folder1', 'file1.txt'), os.path.join(self.fake_project_b_path, 'file3.txt')]
        response = self.client.post(reverse('store_files_in_db'), json.dumps({'file_paths': file_paths}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'message': 'Files stored successfully'})

    @patch('project_b_instance.models.ProjectBInstance.update_file_tree')
    def test_update_file_tree_view(self, mock_update_file_tree):
        mock_update_file_tree.return_value = None
        response = self.client.post(reverse('update_file_tree'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', json.loads(response.content))

    @patch('project_b_instance.models.ProjectBInstance.add_files_to_db')
    def test_update_file_or_files_view(self, mock_add_files_to_db):
        file_paths = [os.path.join(self.fake_project_b_path, 'folder1', 'file1.txt'), os.path.join(self.fake_project_b_path, 'file3.txt')]
        response = self.client.post(reverse('update_file_or_files'), json.dumps({'file_paths': file_paths}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'message': 'Files updated successfully'})

    @patch('project_b_instance.models.ProjectBInstance.get_files_from_db')
    def test_get_file_or_files_view(self, mock_get_files_from_db):
        file_paths = [os.path.join(self.fake_project_b_path, 'folder1', 'file1.txt'), os.path.join(self.fake_project_b_path, 'file3.txt')]
        mock_get_files_from_db.return_value = {'file1.txt': 'This is file1. Edit in file1\nUncommitted edit in file1', 'file3.txt': 'This is file3.'}
        response = self.client.get(reverse('get_file_or_files'), {'file_paths': file_paths})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'file1.txt': 'This is file1. Edit in file1\nUncommitted edit in file1', 'file3.txt': 'This is file3.'})

    @patch('project_b_instance.models.ProjectBInstance.delete_files_from_db')
    def test_delete_file_or_files_view(self, mock_delete_files_from_db):
        file_paths = [os.path.join(self.fake_project_b_path, 'file2.txt')]
        response = self.client.delete(reverse('delete_file_or_files'), json.dumps({'file_paths': file_paths}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'message': 'Files deleted successfully'})

    def test_get_current_tree_view(self):
        response = self.client.get(reverse('get_current_tree'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('file_tree', json.loads(response.content))
        self.assertIn('tree_output', json.loads(response.content))

    def test_get_updated_tree_view(self):
        response = self.client.get(reverse('get_updated_tree'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('tree_output', json.loads(response.content))

    def test_synchronize_instances(self):
        # Step 1: Generate update list from the fake project B
        response = self.client.get(reverse('generate_update_list'))
        self.assertEqual(response.status_code, 200)
        update_list = json.loads(response.content)

        # Step 2: Apply updates to the local instance
        for update in update_list:
            action = update['action']
            file_path = update['path']
            if action == 'add' or action == 'modify':
                response = self.client.post(reverse('store_files_in_db'), json.dumps({'file_paths': [file_path]}), content_type='application/json')
                self.assertEqual(response.status_code, 200)
            elif action == 'delete':
                response = self.client.delete(reverse('delete_file_or_files'), json.dumps({'file_paths': [file_path]}), content_type='application/json')
                self.assertEqual(response.status_code, 200)

        # Step 3: Verify synchronization
        original_files = self._get_files_in_directory(self.fake_project_b_path)
        local_files = self._get_files_in_directory(self.local_instance_path)
        
        self.assertEqual(original_files, local_files)

        original_contents = self._get_files_content(self.fake_project_b_path)
        local_contents = self._get_files_content(self.local_instance_path)
        
        self.assertEqual(original_contents, local_contents)

    def _get_files_in_directory(self, directory):
        files = []
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                files.append(os.path.relpath(os.path.join(dirpath, filename), directory))
        return sorted(files)

    def _get_files_content(self, directory):
        contents = {}
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                with open(os.path.join(dirpath, filename), 'r') as file:
                    contents[os.path.relpath(os.path.join(dirpath, filename), directory)] = file.read()
        return contents
