# Importing Libraries

import textbase
from textbase.message import Message
from textbase import models
import os
from typing import List
import os
from langchain.agents.agent_toolkits import create_python_agent
from langchain.chat_models import ChatOpenAI
from langchain.tools import PythonREPLTool,Tool
from langchain.agents import AgentType, create_csv_agent, initialize_agent

# Load your OpenAI API key
API_KEY = "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"


@textbase.chatbot("talking-bot")
def on_message(message_history: List[Message], state: dict = None):
    """Your chatbot logic here
    message_history: List of user messages
    state: A dictionary to store any stateful information

    Return a string with the bot_response or a tuple of (bot_response: str, new_state: dict)
    """

    if state is None or "counter" not in state:
        state = {"counter": 0}
    else:
        state["counter"] += 1

    # Creating python agent for handling python code for the input
    python_agent_executer = create_python_agent(llm=ChatOpenAI(temperature=0,model='gpt-3.5-turbo',
                                                               openai_api_key=API_KEY),tool=PythonREPLTool(),
                                                               agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                                                               verbose=True)
    

    # Creating csv agent for handling questions related titanic.csv dataset
    # Any dataset can be used. "titanic.csv" is used for demonstration purpose

    csv_agent = create_csv_agent(llm=ChatOpenAI(temperature=0,model='gpt-3.5-turbo',openai_api_key=API_KEY),
                                 path='E:\\Large language models udemy\\Code interpreter\\titanic.csv', tool=PythonREPLTool(),verbose=True,agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION)
    


    # Creating router agent which selects the best tool based on the prompt given by the user
    grand_agent = initialize_agent(
        tools=[
            Tool(
                name="PythonAgent",
                func=python_agent_executer.run,
                description="""useful when you need to transform natural language and write from it python and execute the python code,
                              returning the results of the code execution,
                            DO NOT SEND PYTHON CODE TO THIS TOOL""",
            ),
            Tool(
                name="CSVAgent",
                func=csv_agent.run,
                description="""useful when you need to answer question over titanic.csv file,
                             takes an input the entire question and returns the answer after running pandas calculations""",
            ),
        ],
        llm=ChatOpenAI(temperature=0, model="gpt-3.5-turbo",openai_api_key=API_KEY),
        agent_type=AgentType.OPENAI_FUNCTIONS,
        verbose=True
    )


    bot_response = grand_agent.run(message_history[-1])

    return bot_response, state