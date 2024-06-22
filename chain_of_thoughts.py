# from openai_api import chat_completion

# A class, some prompts given in the constructor, and a method execute.
class NormalChain:
    def __init__(self, prompts):
        self.prompts = prompts
    
    def execute(self, query):
        context = []
        result = query
        for prompt in self.prompts:
            context.append(prompt)
            context.append(result)
            result = chat_completion(context)
        return result