from langchain.agents import Tool
from langchain.tools import StructuredTool
from typing import Callable

from pydantic import BaseModel, Field

class NexusQAChainInput(BaseModel):
    query: str = Field()

class NexusDirectoriesHaveTools():
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def directory_has_tool(self, directory, tool):
        if tool in directory:
            return True
        return False

    def directory_item_as_tool(self, key, item):
        # directory items have to have a description
        c = self.make_tool_func(key)

        tool = Tool.from_function(
            name=key,
            description=item["description"],
            func=c.run,
            args_schema=NexusQAChainInput
        )
        return tool
    
    def make_tool_func(self, key):
        raise Exception("make_tool_func not implemented in NexusDirectoriesHaveTools " + key)