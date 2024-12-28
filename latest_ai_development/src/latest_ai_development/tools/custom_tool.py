from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv


class MyCustomToolInput(BaseModel):
    """Input schema for MyCustomTool."""
    argument: str = Field(..., description="Description of the argument.")

class MyCustomTool(BaseTool):
    name: str = "Name of my tool"
    description: str = (
        "Clear description for what this tool is useful for, you agent will need this information to use it."
    )
    args_schema: Type[BaseModel] = MyCustomToolInput

    def _run(self, argument: str) -> str:
        # Implementation goes here
        return "this is an example of a tool output, ignore it and move along."

# class CustomSerperDevTool(BaseTool):
#     name: str = "Custom Serper Dev Tool"
#     description: str = "Search the internet for research labs and professors"
#     #args_schema: Type[BaseModel] = MyCustomToolInput

#     def _run(self, query: str) -> str:
#         import http.client
#         import json

#         conn = http.client.HTTPSConnection("google.serper.dev")
#         payload = json.dumps({
#         "q": "query",
#         "num": 10
#         })
#         headers = {
#         'X-API-KEY': os.getenv("SERPER_API_KEY"),
#         'Content-Type': 'application/json'
#         }
#         conn.request("POST", "/search", payload, headers)
#         res = conn.getresponse()
#         url = res.get("link")
#         print(url.decode("utf-8"))
