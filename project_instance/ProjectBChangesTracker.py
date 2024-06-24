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
        command = f"git log {self.last_commit_id}..HEAD --oneline"
        output = self.git_command(command)
        commits = [line.split()[0] for line in output.split('\n')]
        return commits

    def get_changes_in_commit(self, commit_hash):
        command = f"git diff-tree --no-commit-id --name-status -r {commit_hash}"
        output = self.git_command(command)
        changes = [line.split('\t') for line in output.split('\n') if line]
        return changes

    def get_uncommitted_changes(self):
        staged_command = "git diff --cached --name-status"
        unstaged_command = "git diff --name-status"

        staged_output = self.git_command(staged_command)
        unstaged_output = self.git_command(unstaged_command)

        staged_changes = [line.split('\t') for line in staged_output.split('\n') if line]
        unstaged_changes = [line.split('\t') for line in unstaged_output.split('\n') if line]

        return staged_changes + unstaged_changes

    def combine_changes(self, committed_changes, uncommitted_changes):
        combined_changes = committed_changes + uncommitted_changes

        # Prioritize deletions first, then modifications, and additions last
        deletions = [change for change in combined_changes if change[0] == 'D']
        modifications = [change for change in combined_changes if change[0] == 'M']
        additions = [change for change in combined_changes if change[0] == 'A']

        return deletions + modifications + additions

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

# Example usage:
# tracker = ProjectBChangesTracker('/path/to/projectB', 'last_commit_id')
# updates = tracker.generate_update_list()
# print(updates)
