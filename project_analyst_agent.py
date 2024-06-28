
import subprocess
import chain_of_thoughts as cot
import os
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

initial_prompt = SystemMessage(content="""You are project analyst agent. You will be given a problem and file project tree, and your role is to figure out which files in the project would be relevant to look at in order to solve the problem. Follow each step and prompt like your life depends on it. Do not generate more content or try to go ahead. Things will make sense as they go. Answer each prompt as you go and not more.
Your role is not to provide an answer or to write code. Your role is simply to figure out through a chain of thoughts which files in the project would be relevant to look at in order to solve the problem. Follow each steps and prompt like your life depends on it. Do not generate more content or try to go ahead. Things will make sens as they go. Answer each prompt as you go and not more.
The problem will be in the form of a usery query for code improvement, or a but report (a copy of a terminal output), or a stack trace. It could also be a query to improve one specific function in one simple file.
The project tree will be a list of files and directories.
""")

file_list_general_naive_diagnosis = SystemMessage(content="""On this first step you are simply task to diagnose the problem. What is the problem? What is the type of the user query ? Is it a stack trace ? A question on one simple file ? A refactoring of multiple files ?
Do not write any code.
Do not yet write any file or directory name. This is not what we are doing now.
What's the diagnosis ? How do you understand the problem ?
Give a step by step break trhough of the problem and what it is.
Here is the user's problem :
""")

file_list_generate_file_list = HumanMessage(content="""Now that you have a clear understanding of the problem, what would the files in this project given the following file tree that you would need to take a look at to solve the problem ?
Give your answer in a step by step explanation and break through. Of, according to the problem analysis, which of those files in the tree would be a great to look into in order to figure out what's the problem ?""")

file_list_format_file_list = HumanMessage(content="Reformulate your answer writing the files and directories relative paths separated by a comma. Do not use any space after the comma. Do not use any space before the comma. Do not use any space before or after the file or directory name. Do not write any unnecessary polite words or sentences. Do not write any code. Do not write any file or directory name that is not relevant to the problem. Only write the list of files formatted this way.")



diagnosis_reports_aggregation = HumanMessage(content="""During this step, you will be given a list of code file reports. Your role is to run through all of them and generate a broader report. You must based yourself on the previously reminded analysis that you have done yourself. Among those reports you will encounter highlighted pieces of code. You role is to careful select among those highlighted pieces the most relevant ones to the problem diagnosis. In the light of multiple file reports, you can proceed to eliminate some of the highlighted pieces of code that are no longer relevant to the diagnosis based on your expert's opinion, explain why before eliminating them. In this step, your role is not to formulate an answer or a final diagnosis, but simply to aggregate the reports of the files given to you. Generate a new project report using the final resulting highlighted pieces of code.""")

diagnosis_analysis_without_code = HumanMessage(content="""Given your final report, explain in a long reasoning process what the final diagonis of the problem is and why the problem occured.
After which you will propose, without writting code, an approach to a solution. Do not write code. Generate a blue print of the changes ahead of us to in order to correct the problem. Only a blue print, a general solving plan a detailed break down, no code.""")

diagnosis_partial_code = HumanMessage(content="""
Following your blue print and fixing plan, partially edit the code focusing on the modification, do not write the whole code only the edited section, break down why you think the code is still correct and will work despite the modification before proposing an edit code sample generation. Also break down how you think the modification will solve the issue before proposing an edit. If this is react code, please use types and typescript implementations. Focus on small edits, no entire file generation yet.""")

diagnosis_final_code = HumanMessage(content="""Now for each file that needs to be edited, based on the generated plan, re-write the entire file's code. Include those edits. Do not edit unnecessary code and leave the rest of the code as is. Do not remove comments or “useless code” if not directly related to the new changes. If this is react code, please use types and typescript implementations.
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
          message_tree = [[initial_prompt, file_list_general_naive_diagnosis, HumanMessage(content=self.problem)]]
          message_tree.append([file_list_generate_file_list, HumanMessage(content=self.generate_tree_output(self.repo_path))])
          message_tree.append([file_list_format_file_list])
          answer, context = cot.run_chain(message_tree)
          return answer, context
      
      def run_file_context_diagnosis(self):
          list_of_files, message_list = self.run_list_of_files()
          files = list_of_files.split(",")
          files = [f.strip() for f in files]
          message_list.append(diagnosis_reports_aggregation)
          for file in files:
              file_report = sub_agent_file_analysis(file, self.repo_path).run_file_analysis()
              message_list.append(SystemMessage(content=file_report))
          message_tree = [message_list]
          message_tree.append([diagnosis_analysis_without_code])
          message_tree.append([diagnosis_partial_code])
          message_tree.append([diagnosis_final_code])
          answer, context = cot.run_chain(message_tree)
          return answer


# This one is out of the conversation flow (it is a sub-agent)
file_analysis_first_step_understanding = SystemMessage(content="""Review the following file. Your role is to understand the code and understand the purpose of the file. What does a file like this typically does based on your knowledge. Give a detailed analysis of what the code of the whole file does.
Let's think step by step. What is the purpose of this file ? What is the purpose of each function ? What is the purpose of each class ? What is the purpose of each variable ? What is the purpose of each line of code ?""")

file_analysis_second_step_analysis = SystemMessage(content="""Given your understanding of the file answer, the user's problem and its analysis, break down in a detail reasoning process what piece of this code in this are relevant to the raised problem. Highlight those elements. Base your reasoning on the analysis
Let's think step by step.""")

file_analysis_third_step_diagnosis = SystemMessage(content="""
Now that you have a break down of the relevant piece of code relevant to the problem diagnosis. Leverage a list of elements in this file and generate a detailed summary of those highlighted elements. Generate a report of this file selecting among the highlighted code the most relevant pieces to the problem diagnosis. Explain why you think this piece is relevant and will help diagnosing the problem.
Generate a report of this file code.""")

class sub_agent_file_analysis:
      def __init__(self, file_path, repo_path):
          self.file_path = file_path
          file_path = os.path.join(repo_path, self.file_path)
          with open(file_path, "r") as f:
              self.file_content = f.read()

      def run_file_analysis(self):
          message_tree = [[file_analysis_first_step_understanding, HumanMessage(content=self.file_path+"\n---\n"+self.file_content)]]
          message_tree.append([file_analysis_second_step_analysis])
          message_tree.append([file_analysis_third_step_diagnosis])
          answer, context = cot.run_chain(message_tree)          
          return answer