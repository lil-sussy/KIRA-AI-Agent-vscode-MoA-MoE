
import subprocess
import chain_of_thoughts as cot
import os
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

initial_prompt = SystemMessage(content="""You are code creator agent. You will be given an algorithm, or a task and file project tree, and your role is to figure out which files in the project would be relevant to look at in order to implement this task or algorithm.
We will proceed step by step during this conversation, so for each message, limit yourself to each task and do not attempt to predit and go ahead of yourself.
""")

file_list_naive_blueprint_generation = HumanMessage(content="""
Without writing any code break down and explain step by step how you could achieve this in a long reasoning process without knowning the code inside the project. Propose solutions knowing that you do not have full access to the code yet. That will come.
I insist on DO NOT WRITE CODE, the code generation is going to be the following step. Focus on the analysis.
""")

file_list_further_naive_code_generation = HumanMessage(content="""
Now to implement this algorithm and write the necessary code, we first are going to generate the boiler plate basic code for those edit, what are the blueprints and the basic bricks of the edits that we are going to implement. 
We will be generating the whole code later.
Explain this in a complex reasoning process and step by step break down.
I insist on do not generate the whole code now, that will come after.
""")

file_list_generate_file_list = HumanMessage(content="""Now that you have a clear understanding of how to achieve this, given the file tree, what files in this project would you want to take a look at before generating any code ?
Let's think step by step.""")

file_list_format_file_list = HumanMessage(content="""Reformulate your answer writing the files and directories relative paths separated by a comma. Do not use any space after the comma. Do not use any space before the comma. Do not use any space before or after the file or directory name. Do not write any unnecessary polite words or sentences. Do not write any code. Do not write any file or directory name that is not relevant to the problem. Only write the list of files formatted this way.
Do NOT generate other content or polite answer other than the list of file paths
The format should directly be :
<No pre content>
path/to/file1.py,path/to/file2.py,path/to/file3.py
path/to/file4.py,path/to/file5.py
...
<No last content>""")



implementation_reports_aggregation = HumanMessage(content="""During this step, you will be given a list of code file reports. Your role is to run through all of them and generate a broader report. You must based yourself on the previously reminded analysis that you have done yourself. Among those reports you will encounter highlighted pieces of code. You role is to careful select among those highlighted pieces the most relevant ones to in order to complete the task. In the light of multiple file reports, you can proceed to eliminate some of the highlighted pieces of code that are no longer relevant to the task based on your expert's opinion, explain why before eliminating them. In this step, your role is not to formulate an answer, but simply to aggregate the reports of the files given to you. Generate a new project report using the final resulting highlighted pieces of code.""")

implementation_analysis_without_code = HumanMessage(content="""Given your final report, explain in a long reasoning process which files must be edited or changed in order to implement this new feature.
After which you will propose, without writting code, an approach to a solution. Do not write code. Generate a blue print of the changes ahead of us to in order to correct the problem. Only a blue print, a general solving plan a detailed break down, no code.""")

implementation_partial_code = HumanMessage(content="""
Given your previously generated blueprint and those files edits, partially edit the code focusing on the modification, do not write the whole code only the edited section, break down why you think the code is still correct and will work despite the modification before proposing an edit code sample generation. Also break down how you think the modification will solve the feature implementation before proposing an edit. If this is react code, please use types and typescript implementations. Focus on small edits, no entire file generation yet. If this is python code, use types as much as possible.
""")

implementation_final_code = HumanMessage(content="""Now for each file that needs to be edited, based on the generated plan, re-write the entire file's code. Include those edits. Do not edit unnecessary code and leave the rest of the code as is. Do not remove comments or “useless code” if not directly related to the new changes. If this is react code, please use types and typescript implementations.
Generate every file.
The format must be :
path/to/file1.py
---
<code of file1.py>
---
path/to/file2.py
---
etc...""")

class diagnosis_agent:
      def __init__(self, problem, repo_path):
          self.problem = problem
          self.repo_path = repo_path

      def generate_tree_output(self):
          exclude_pattern = ".git|node_modules|__pycache__|.next|.build"
          command = ["tree", "-a", "-I", exclude_pattern ]
          result = subprocess.run(command, cwd=self.repo_path, capture_output=True, text=True)
          if result.returncode != 0:
              raise Exception(f"Tree command failed: {result.stderr}")
          return result.stdout.strip()

      def run_list_of_files(self):
          message_tree = [[initial_prompt, file_list_naive_blueprint_generation, HumanMessage(content=self.problem)]]
          message_tree.append([file_list_further_naive_code_generation])
          message_tree.append([file_list_generate_file_list, HumanMessage(content=self.generate_tree_output())])
          message_tree.append([file_list_format_file_list])
          answer, context = cot.run_chain(message_tree)
          return answer, context
      
      def run_file_context_diagnosis(self):
          list_of_files, message_list = self.run_list_of_files()
          reminder = message_list[5].content
          files = list_of_files.split(",")
          files = [f.strip() for f in files]
          message_list.append(implementation_reports_aggregation)
          for file in files:
              file_report, sub_context = sub_agent_file_analysis(file, self.repo_path).run_file_analysis([HumanMessage("Remind yourself of the given task and your plan to achieve it"), AIMessage("Answer: "+reminder)])
              message_list.append(HumanMessage(content=file_report))
          message_tree = [message_list]
          message_tree.append([implementation_analysis_without_code])
          message_tree.append([HumanMessage(content="Please remind yourself of you previously generated blueprint and boiler plate edits"), AIMessage(content=reminder), implementation_partial_code])
          message_tree.append([implementation_final_code])
          answer, context = cot.run_chain(message_tree)
          return answer


# This one is out of the conversation flow (it is a sub-agent)
file_analysis_first_step_understanding = SystemMessage(content="""Review the following file. Your role is to understand the code and understand the purpose of the file. What does a file like this typically does based on your knowledge. Give a detailed analysis of what the code of the whole file does.
Let's think step by step. What is the purpose of this file ? What is the purpose of each function ? What is the purpose of each class ? What is the purpose of each variable ? What is the purpose of each line of code ?""")

file_analysis_second_step_analysis = HumanMessage(content="""Given your understanding of the file answer, the user's feature implementation or user task and its analysis, break down in a detail reasoning process what piece of this code in this are relevant to the raised problem. Highlight those elements. Base your reasoning on the analysis
Let's think step by step.""")

file_analysis_third_step_diagnosis = HumanMessage(content="""
Now that you have a break down of the relevant piece of code relevant to the feature implementation or user task. Leverage a list of elements in this file and generate a detailed summary of those highlighted elements. Generate a report of this file selecting among the highlighted code the most relevant pieces, relevant to the new feature implementation or task. Explain why you think this piece is relevant and will help solving the implementation.
Generate a report of this file code.""")

class sub_agent_file_analysis:
      def __init__(self, file_path, repo_path):
          self.file_path = file_path
          file_path = os.path.join(repo_path, self.file_path)
          with open(file_path, "r") as f:
              self.file_content = f.read()

      def run_file_analysis(self, previous_analysis_list):
          message_tree = [[file_analysis_first_step_understanding, HumanMessage(content=self.file_path+"\n---\n"+self.file_content)]]
          message_tree.append(previous_analysis_list)
          message_tree[-1].append(file_analysis_second_step_analysis)
          message_tree.append([file_analysis_third_step_diagnosis])
          answer, context = cot.run_chain(message_tree)          
          return answer, context


import sys

def main():
    if len(sys.argv) < 3:
        print("Error: This script requires two arguments.")
        sys.exit(1)

    first_argument = sys.argv[1]
    second_argument = sys.argv[2]

    diagnosis_agent_instance = diagnosis_agent(first_argument, second_argument)
    answer = diagnosis_agent_instance.run_file_context_diagnosis()
    print(answer)

if __name__ == "__main__":
    main()