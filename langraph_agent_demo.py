from typing import List, Dict
from langgraph.graph import StateGraph, START, END
from langchain_aws import BedrockLLM
from langchain_aws import ChatBedrock

import boto3



bedrock_client = boto3.client(service_name="bedrock-runtime",region_name = "us-east-1")
llm = ChatBedrock(
    client=bedrock_client,
    model_id="anthropic.claude-3-haiku-20240307-v1:0",
    model_kwargs={
        "max_tokens": 512,
        "temperature": 0.7,
        "anthropic_version": "bedrock-2023-05-31"  # Required parameter[5]
    }
)

class State(Dict):
    messages: List[Dict[str, str]] 

graph_builder = StateGraph(State)

def chatbot(state: State):
    response = llm.invoke(state["messages"])
    state["messages"].append({"role": "assistant", "content": response})  # Treat response as a string
    return {"messages": state["messages"]}

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

graph = graph_builder.compile()


def stream_graph_updates(user_input: str):    
    state = {"messages": [{"role": "user", "content": user_input}]}
    for event in graph.stream(state):
        for value in event.values():
            # print("j",value)
            # content = value["messages"][-1]["content"]
            # print(value["messages"][-1]["content"])



            # print("Assistant 1:", content)
            print("Assistant:", value["messages"][-1]["content"].content)

# Run chatbot in a loop
if __name__ == "__main__":
    while True:
        try:
            user_input = input("User: ")
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break

            stream_graph_updates(user_input)
        except Exception as e:
            print(f"An error occurred: {e}")
            break