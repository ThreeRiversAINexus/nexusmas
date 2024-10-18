from spade.behaviour import OneShotBehaviour
from spade.message import Message

class Replying(OneShotBehaviour):
    def __init__(self, *args, **kwargs):
        self.message = kwargs.pop("message", None)
        self.target = kwargs.pop("target", None)
        super().__init__(*args, **kwargs)
    
    async def run(self):
        # self.agent.start_conversation(self.target, self.message)
        msg = Message(to=self.target, body=self.message)
        msg.set_metadata("performative", "inform")
        msg.set_metadata("ontology", "the-nexus-multi-agent-system")
        # from pprint import pprint
        # pprint(msg.body)
        await self.send(msg)