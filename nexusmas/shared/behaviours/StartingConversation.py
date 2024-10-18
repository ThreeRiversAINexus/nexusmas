from spade.behaviour import OneShotBehaviour

class StartingConversation(OneShotBehaviour):
    def __init__(self, *args, **kwargs):
        self.target = kwargs.pop("target", None)
        self.conversation_starter = kwargs.pop("conversation_starter", None)
        super().__init__(*args, **kwargs)

    async def run(self):
        await self.agent.start_conversation(self.target, self.conversation_starter)