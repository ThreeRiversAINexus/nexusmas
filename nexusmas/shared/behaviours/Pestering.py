from spade.behaviour import PeriodicBehaviour

class Pestering(PeriodicBehaviour):
    def __init__(self, *args, **kwargs):
        self.message = kwargs.pop("message", None)
        self.target = kwargs.pop("target", None)
        # Every half hour
        super().__init__(period=3600, *args, **kwargs)
    
    async def run(self):
        await self.agent.start_conversation(self.target, self.message) 
