import os
import subprocess
import shutil
import chromadb
from project_b_instance.ProjectBRemote import ProjectBChangesTracker
import server_app.settings as settings
import uuid

db = chromadb.PersistentClient(path=settings.CHRMADB_PERSIST_DIR)

class ProjectBInstance:
    def __init__(self, project_b_path):
        self.project_b_path = project_b_path
        self.file_tree = {}
        self.project_b_remote = None
        self.initialize_project_b_instance()

    def initialize_project_b_instance(self):
        if not os.path.exists(self.project_b_path):
            raise ValueError(f"The path {self.project_b_path} does not exist.")
        
        self.project_b_remote = ProjectBChangesTracker(self.project_b_path, "") # initial commit id is empty
        # self.file_tree = self.change_tracker.build_file_tree(self.project_b_path)
        self.apply_updates()
        self.project_b_remote.last_commit_id = os.popen(f'git -C {self.project_b_path} rev-parse HEAD').read().strip()

    def add_file_to_db(self, file_path):
        content = self.project_b_remote.read_file_content(file_path)
        client = chromadb.PersistentClient(path=settings.CHRMADB_PERSIST_DIR)
        collection = client.get_or_create_collection(self.project_b_path.replace('/','.')[3:-1])
        collection.add(
            documents=[content],
            metadatas=[{"path": file_path}],
            ids=[file_path]
        )

    def get_file_from_db(self, file_path):
        # Retrieve from ChromaDB (dummy code, replace with actual ChromaDB code)
        client = chromadb.PersistentClient(path=settings.CHRMADB_PERSIST_DIR)
        collection = client.get_collection(self.project_b_path.replace('/','.')[3:-1])
        result = collection.query(
            query_texts=[file_path],
            n_results=1
        )
        return result['documents'][0]
    
    def edit_file_to_db(self, file_path):
        new_content = self.project_b_remote.read_file_content(file_path)
        client = chromadb.PersistentClient(path=settings.CHRMADB_PERSIST_DIR)
        collection = client.get_collection(self.project_b_path.replace('/','.')[3:-1])
        collection.update(
            documents=[new_content],
            ids=[file_path]
        )

    def move_file_in_db(self, file_path, new_path):
        content = self.project_b_remote.read_file_content(file_path)
        client = chromadb.PersistentClient(path=settings.CHRMADB_PERSIST_DIR)
        collection = client.get_collection(self.project_b_path.replace('/','.')[3:-1])
        collection.delete(ids=[file_path])
        collection.add(
            documents=[content],
            metadatas=[{"path": new_path}],
            ids=[new_path]
        )
    
    def delete_file_from_db(self, file_path):
        client = chromadb.PersistentClient(path=settings.CHRMADB_PERSIST_DIR)
        collection = client.get_collection(self.project_b_path.replace('/','.')[3:-1])
        collection.delete(ids=[file_path])
    
    def apply_updates(self):
        updates = self.project_b_remote.generate_update_list()

        for update in updates:
            action = update["action"]
            file_path = update["path"]
            full_path = os.path.join(self.project_b_path, file_path)

            if action == "A":
                self.add_file_to_db(file_path)
            elif action == "M":
                self.edit_file_to_db(file_path)
            elif action == "D":
                self.delete_file_from_db(file_path)
            elif action == "R":
                self.move_file_in_db(file_path)
            elif action == "C":
                self.add_file_to_db(file_path)
            elif action == "T":
                self.add_file_to_db(file_path)
            elif action == "U":
                self.add_file_to_db(file_path)


# Example usage:
# tracker = ProjectBInstance('/path/to/projectB')
# tracker.add_file_to_db('/path/to/projectB/file1.txt')
# print(tracker.get_file_from_db('/path/to/projectB/file1.txt'))
# print(tracker.tree_output)
