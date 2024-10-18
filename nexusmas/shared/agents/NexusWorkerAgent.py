from shared.beliefs.NexusConversationalist import NexusConversationalist
from shared.agents.NexusAgent import NexusAgent

class NexusWorkerAgent(NexusConversationalist, NexusAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        