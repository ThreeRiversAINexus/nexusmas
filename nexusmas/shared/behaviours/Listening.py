from spade.behaviour import CyclicBehaviour
from pprint import pprint

from shared.tools.detailed_dump import DetailedDump
from shared.behaviours.Choosing import Choosing

import asyncio

class Listening(CyclicBehaviour):
    def __init__(self, *args, **kwargs):
        self.message_handler = kwargs.pop("message_handler", None)
        super().__init__(*args, **kwargs)

    async def run(self):
        timeout = 5
        msg = await self.receive(timeout=timeout)
        if msg:
            print(f"{self.agent.identity} received a message")
            if msg.body is not None:
                # pprint(msg.sender, msg.body)
                # pprint(msg.sender)
                # pprint(msg.body)
                # choice = Choosing(msg.body)
                # self.agent.add_behaviour(choice)
                # result = choice.join()
                # pprint(result)
                asyncio.create_task(self.message_handler(msg))
            else:
                print(f"{self.agent.identity} received an empty message")