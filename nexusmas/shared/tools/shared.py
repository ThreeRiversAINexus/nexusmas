from langchain.tools import StructuredTool
from shared.factories.NexusAgentFactory import NexusAgentFactory

class NexusTool():
    def __init__(self, tool_function):
        self.tool_function = tool_function

    def tool_factory(self):
        tool = StructuredTool.from_function(getattr(self, self.tool_function))
        return tool

class NexusAgentAsTool(NexusTool):
    def __init__(self, tools):
        self.tools = tools
        self.tool_function = "do_tasks"
        self.agent = self.make_agent()

    def make_description(self):
        descriptions = []
        desc = """
        Input is a natural language prompt for the Nexus to complete a task the user requests.
        Example "Please foo the bar thoroughly."
        Options\n
        zzzzzzz\n
        """
        for tool in self.tools:
            descriptions += ["do_tasks - " + tool.description + "\n"]
        # Combine descriptions
        for description in descriptions:
            desc += description
        desc += "zzzzzzz\n"
        from pprint import pprint
        pprint(desc)
        return desc

    def make_agent(self):
        agent_factory = NexusAgentFactory()
        agent = agent_factory.create_structured_tool_agent(tools=self.tools, intermediate_steps=True)
        return agent
    
    def do_tasks(self, prompt: str):
        response = self.agent({"input": prompt})
        intermediate_steps = response["intermediate_steps"]
        # search_and_results = [(sublist[0][0], sublist[1]) for sublist in intermediate_steps]

        from pprint import pprint
        pprint(intermediate_steps) 
        return response["output"]
    
    def tool_factory(self):
        tool = StructuredTool.from_function(self.do_tasks, name="do_tasks", description=self.make_description())
        from pprint import pprint
        pprint("make_description_output: " + self.make_description())
        return tool
