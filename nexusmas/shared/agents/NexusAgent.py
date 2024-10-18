import sys
import os
import time
import traceback

sys.path.append("/home/pat-server/git/nexus-multi-agent-system/nexus-multi-agent-system")

from spade.agent import Agent
from shared.behaviours.Appearing import Appearing

class NexusAgent(Agent):
    def __init__(self, jid, passphrase, *args, **kwargs):
        super().__init__(jid, passphrase)
        self.identity = kwargs.get("agent_name")
        print(f"Initializing {self.identity}")
        self.agent_type = kwargs.get("agent_type")
        # self.config_file = kwargs.get("config_file")

    async def setup(self):
        print(f"{self.identity} began setup")
        if not self.start_behaviours:
            self.start_behaviours = []
        # self.start_behaviours += [Appearing()]
        await self.attach_behaviours(self.start_behaviours)

    async def attach_behaviours(self, behaviours):
        for i, behaviour in enumerate(behaviours):
            try:
                self.add_behaviour(behaviour)
            except Exception as e:
                print(f"Error encountered when adding behaviour at index {i}.")
                print(f"Type of behaviour: {type(behaviour)}")
                print(f"Behaviour: {behaviour}")
                print(f"Error details: {str(e)}")
                print(f"Traceback:\n{traceback.format_exc()}")
                continue


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--jid", type=str, required=True)
    # parser.add_argument("--config-file", type=str, required=True)
    args = parser.parse_args()
    jid = args.jid
    # config_file = args.config_file

    passphrase = os.environ["AGENT_PASSWORD"]

    agent = NexusAgent(jid, passphrase, identity="NexusAgent")
    agent_future = agent.start()
    agent_future.result()

    while agent.is_alive():
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            agent.stop()
            break

    print("Agent finished")