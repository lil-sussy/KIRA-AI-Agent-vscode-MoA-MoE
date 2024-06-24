import os
import subprocess
import chromadb

class ProjectBInstance:
    def __init__(self, project_b_path):
        self.project_b_path = project_b_path
        self.files_contents = {}
        self.file_tree = {}
        self.tree_output = ""

        self.initialize_project_b_instance()

    def initialize_project_b_instance(self):
        if not os.path.exists(self.project_b_path):
            raise ValueError(f"The path {self.project_b_path} does not exist.")
        
        self.build_file_tree(self.project_b_path)
        self.generate_tree_output()

    def add_file_to_db(self, file_path):
        with open(file_path, 'r') as file:
            content = file.read()
            # Add to ChromaDB (dummy code, replace with actual ChromaDB code)
            client = chromadb.PersistentClient(path="my_chroma_data")
            collection = client.get_or_create_collection("project_b_files")
            collection.add(
                documents=[content],
                metadatas=[{"path": file_path}],
                ids=[file_path]
            )
            self.files_contents[file_path] = content

    def add_files_to_db(self, file_paths):
        for file_path in file_paths:
            self.add_file_to_db(file_path)

    def get_file_from_db(self, file_path):
        # Retrieve from ChromaDB (dummy code, replace with actual ChromaDB code)
        client = chromadb.PersistentClient(path="my_chroma_data")
        collection = client.get_collection("project_b_files")
        result = collection.query(
            query_texts=[file_path],
            n_results=1
        )
        return result['documents'][0]

    def get_files_from_db(self, file_paths):
        contents = {}
        for file_path in file_paths:
            contents[file_path] = self.get_file_from_db(file_path)
        return contents

    def build_file_tree(self, current_path, tree=None):
        if tree is None:
            tree = {}
        
        with os.scandir(current_path) as it:
            for entry in it:
                if entry.is_dir():
                    tree[entry.name] = self.build_file_tree(entry.path)
                else:
                    tree[entry.name] = None
                    self.files_contents[entry.path] = self.read_file_content(entry.path)
        self.file_tree = tree

    def read_file_content(self, file_path):
        with open(file_path, 'r') as file:
            return file.read()

    def generate_tree_output(self):
        result = subprocess.run(["tree", self.project_b_path], capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Tree command failed: {result.stderr}")
        self.tree_output = result.stdout

    def update_file_tree(self):
        self.files_contents.clear()
        self.build_file_tree(self.project_b_path)
        self.generate_tree_output()

# Example usage:
# tracker = ProjectBInstance('/path/to/projectB')
# tracker.add_file_to_db('/path/to/projectB/file1.txt')
# print(tracker.get_file_from_db('/path/to/projectB/file1.txt'))
# print(tracker.tree_output)
