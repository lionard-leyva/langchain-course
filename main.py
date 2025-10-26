import os
import ssl
import urllib3
from dotenv import load_dotenv
from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent
from langchain_anthropic import ChatAnthropic
from langchain_tavily import TavilySearch

from langchain_core.output_parsers.pydantic import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda

from prompt import REACT_PROMPT_WITH_FORMAT_INTRUCTIONS
from schemas import AgentResponse


# Desactivar SSL verification
ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['REQUESTS_CA_BUNDLE'] = ''
os.environ['SSL_CERT_FILE'] = ''

# Monkey patch requests para desactivar SSL verification
import requests
original_request = requests.Session.request
def patched_request(self, method, url, *args, **kwargs):
    kwargs['verify'] = False
    return original_request(self, method, url, *args, **kwargs)
requests.Session.request = patched_request

# Monkey patch httpx para desactivar SSL
import httpx
original_client_init = httpx.Client.__init__
def patched_client_init(self, *args, **kwargs):
    kwargs['verify'] = False
    original_client_init(self, *args, **kwargs)
httpx.Client.__init__ = patched_client_init

original_async_client_init = httpx.AsyncClient.__init__
def patched_async_client_init(self, *args, **kwargs):
    kwargs['verify'] = False
    original_async_client_init(self, *args, **kwargs)
httpx.AsyncClient.__init__ = patched_async_client_init



load_dotenv()
tools = [TavilySearch()]
llm = ChatAnthropic(
    model="bedrock/claude-sonnet-4.5",
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    base_url=os.getenv("ANTHROPIC_BASE_URL"),
    temperature=0.1
)
react_prompt = hub.pull("hwchase17/react")

output_parser = PydanticOutputParser(pydantic_object=AgentResponse)
react_prompt_with_format_instructions = PromptTemplate(
    template=REACT_PROMPT_WITH_FORMAT_INTRUCTIONS,
    input_variables=["input", "agent_scratchpad", "tools_names"]
).partial(format_instructions=output_parser.get_format_instructions())


agent =create_react_agent(
    llm=llm,
    tools=tools,
    prompt= react_prompt_with_format_instructions
)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)


def main():
    result = agent_executor.invoke({
        "input": "search for 3 job postings for an ai engineer using langchain in the bay area PERU on linkedin and list their details"
    })
    print(result)


if __name__ == "__main__":
    main()
