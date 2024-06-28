from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# Initialize the Claude 3.5 Sonnet model
chat_model = ChatAnthropic(
    model="claude-3-5-sonnet-20240620",
    api_key="your-api-key-here",
    temperature=0.1,
    max_tokens=1024
)

# Function to generate responses using the chain of thought prompts
def run_chain(message_tree, model=chat_model):
    last_response = ""
    messages_step_by_step = []
    for i, message_node in enumerate(message_tree):
        for j, message in enumerate(message_node):
            messages_step_by_step.append(message)
        response = model.invoke(messages_step_by_step)
        while (hasattr(response, 'additional_kwargs') and 'stop_reason' in response.additional_kwargs) and response.additional_kwargs['stop_reason'] == "max_tokens":
            continuation_prompt = "Finish the response. Do not repeat what you've already said, just continue from the last point."
            messages_step_by_step.append(HumanMessage(content=continuation_prompt))
            response = chat_model.invoke(messages_step_by_step)
            full_response += " " + response.content
        last_response = full_response if full_response else response.content
        messages_step_by_step.append(AIMessage(content=last_response))
    return last_response, messages_step_by_step