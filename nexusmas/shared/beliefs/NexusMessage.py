# Here's where we're gonna try
# to create the custom message class
# we need to make memory intelligible

from langchain.schema import BaseMessage
from langchain.schema import AIMessage
from langchain.schema import HumanMessage
from langchain.schema import SystemMessage

class NexusMessage(BaseMessage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pass

class NexusAgentAIMessage(AIMessage, NexusMessage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pass

class NexusAgentHumanMessage(HumanMessage, NexusMessage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pass

class NexusSystemMessage(SystemMessage, NexusMessage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pass