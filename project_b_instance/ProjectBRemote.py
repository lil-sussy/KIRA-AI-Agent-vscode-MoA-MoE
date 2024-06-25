import os
import subprocess

class ProjectBChangesTracker:
    def __init__(self, repo_path, last_commit_id):
        self.repo_path = repo_path
        self.last_commit_id = last_commit_id

    def git_command(self, command):
        result = subprocess.run(command, cwd=self.repo_path, capture_output=True, text=True, shell=True)
        if result.returncode != 0:
            raise Exception(f"Git command failed: {result.stderr}")
        return result.stdout.strip()

    def get_commits_since_last(self):
        if self.last_commit_id == "":
            command = f"git log HEAD --oneline"
        else:
            command = f"git log {self.last_commit_id}..HEAD --oneline"
        output = self.git_command(command)
        commits = [line.split()[0] for line in output.split('\n') if line]
        return commits

    def get_changes_in_commit(self, commit_hash):
        command = f"git show --name-status {commit_hash}"
        output = self.git_command(command)
        changes = [line.split("\t") for line in output.split('\n') if line.startswith('A\t') or line.startswith('M\t') or line.startswith('D\t') or line.startswith('R\t') or line.startswith('C\t') or line.startswith('T\t') or line.startswith('U\t') or line.startswith('X\t') or line.startswith('B\t')]
        return changes

    def get_uncommitted_changes(self):
        staged_command = "git diff --cached --name-status"
        unstaged_command = "git diff --name-status"

        staged_output = self.git_command(staged_command)
        unstaged_output = self.git_command(unstaged_command)

        staged_changes = [line.split("\t") for line in staged_output.split('\n') if line.startswith('A\t') or line.startswith('M\t') or line.startswith('D\t') or line.startswith('R\t') or line.startswith('C\t') or line.startswith('T\t') or line.startswith('U\t') or line.startswith('X\t') or line.startswith('B\t')]
        unstaged_changes = [line.split("\t") for line in unstaged_output.split('\n') if line.startswith('A\t') or line.startswith('M\t') or line.startswith('D\t') or line.startswith('R\t') or line.startswith('C\t') or line.startswith('T\t') or line.startswith('U\t') or line.startswith('X\t') or line.startswith('B\t')]

        return staged_changes + unstaged_changes

    def combine_changes(self, committed_changes, uncommitted_changes):
        combined_changes = committed_changes + uncommitted_changes
        # Prioritize deletions first, then modifications, and additions last
        deletions = [change for change in combined_changes if change[0] == 'D']
        modifications = [change for change in combined_changes if change[0] == 'M']
        additions = [change for change in combined_changes if change[0] == 'A']

        return deletions + modifications + additions
    
    def read_file_content(self, file_path):
        with open(os.path.join(self.repo_path, file_path), 'r') as file:
            return file.read()

    def generate_tree_output(self):
        result = subprocess.run(["tree", self.repo_path], capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Tree command failed: {result.stderr}")
        return result.stdout.strip()

    def generate_update_list(self):
        # Fetch committed changes since the last commit
        commits = self.get_commits_since_last()
        committed_changes = []
        for commit in commits:
            committed_changes.extend(self.get_changes_in_commit(commit))

        # Fetch uncommitted changes
        uncommitted_changes = self.get_uncommitted_changes()

        # Combine all changes
        all_changes = self.combine_changes(committed_changes, uncommitted_changes)

        # Generate the update list
        update_list = []
        for change in all_changes:
            action, path = change
            update_list.append({"action": action, "path": path})

        return update_list
    
    
    def build_file_tree(self, current_path, tree=None):
        if tree is None:
            tree = {}
        
        with os.scandir(current_path) as it:
            for entry in it:
                full_path = os.path.join(current_path, entry.name)
                if entry.is_dir():
                    tree[entry.name] = self.build_file_tree(full_path)
                else:
                    tree[entry.name] = None
                    self.files_contents[full_path] = self.read_file_content(full_path)
        self.file_tree = tree
        return tree

    def update_file_tree(self):
        self.files_contents.clear()
        self.file_tree = self.build_file_tree(self.project_b_path)
        self.tree_output = self.generate_tree_output()

# Example usage:
# tracker = ProjectBChangesTracker('/path/to/projectB', 'last_commit_id')
# updates = tracker.generate_update_list()
# print(updates)
