from langchain.prompts import PromptTemplate
from langchain.prompts.chat import ChatPromptTemplate
import datetime
import pytz

class NexusSimplePrompt():
    def __init__(self, point=None):
        if point is None:
            raise Exception("point cannot be None")
        self.point = point
    
    def get_simple_prompt(self, memory_variable="short_term_memory"):
        if memory_variable is None:
            memory_variable = "short_term_memory"
        formatted_memory_variable = f"{{{memory_variable}}}"
        template = f"""
Your short term memory
===
{formatted_memory_variable}
===
{self.point}
{{input}}"""
        print(template)
        # input_variables = ["input", memory_variable]
        return PromptTemplate.from_template(
            template=template,
        )

class NexusPrompt():
    def __init__(self, sender_str=None, identity=None, personality=None, circumstances=None, rules=None, output_instructions=None, before_prompt=None):
        if sender_str is None:
            raise Exception("sender_str cannot be None")
        self.sender_str = sender_str

        self.sender_name = sender_str.split("@")[0]

        if identity is None:
            raise Exception("Identity cannot be None")
        self.identity = identity 
        
        if personality is None:
            raise Exception("Personality cannot be None")
        self.personality = personality

        if circumstances is None:
            raise Exception("Circumstances cannot be None")
        self.circumstances = circumstances

        if rules is None:
            raise Exception("Rules cannot be None")
        self.rules = rules

        if output_instructions is None:
            raise Exception("Output instructions cannot be None")
        self.output_instructions = output_instructions

        if before_prompt is None:
            raise Exception("Before prompt cannot be None")
        self.before_prompt = before_prompt

    def get_prompt_template_object(self):
        from pprint import pprint
        pprint(self.get_prompt_skeleton())
        return PromptTemplate(
            template=self.get_prompt_skeleton(), 
            input_variables=self.get_input_variables(),
        )

    def get_chat_prompt_template_object(self):
        return ChatPromptTemplate(
            template=self.get_prompt_skeleton(), 
            input_variables=self.get_input_variables(),
        )

    def get_current_time(self):
        local_timezone = pytz.timezone('America/New_York')
        current_time = datetime.datetime.now().astimezone(local_timezone)
        return current_time.strftime('Current date: %Y-%m-%d Current time: %H:%M:%S')

    def get_prompt_personality_skeleton(self):
        # All of these should be written in
        # the second-person perspective.
        current_time = self.get_current_time()
        return f"""
{current_time}
{self.identity}
{self.personality}
{self.circumstances}
{self.rules}
{self.output_instructions}
"""
        

    def get_prompt_skeleton(self):
        # All of these should be written in
        # the second-person perspective.
        current_time = self.get_current_time()
        
        return f"""
{current_time}
{self.identity}
{self.personality}
{self.circumstances}
{self.rules}
{self.output_instructions}
===
Your short term memory of chats:
{{short_term_memory}}
===
{self.before_prompt}
===
Agent {self.sender_name}: {{input}}
Agent:
         """
    
    def get_input_variables(self):
        input_variables = ["input"]
        input_variables += ["short_term_memory"]
        # input_variables += ["long_term_memory"]
        return input_variables