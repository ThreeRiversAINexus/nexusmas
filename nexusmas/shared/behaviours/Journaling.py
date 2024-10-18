from spade.behaviour import PeriodicBehaviour

class Journaling(PeriodicBehaviour):
    def __init__(self, *args, **kwargs):
        self.message = kwargs.pop("message", None)
        self.target = kwargs.pop("target", None)
        # Every half hour
        super().__init__(period=1800, *args, **kwargs)

    async def run(self):
        print("Journaling")
        ##  Prompt the agent
        ##  to write a journal entry
        ##  about the ongoing conversations
        ##  and their thoughts
        ##  and their objectives