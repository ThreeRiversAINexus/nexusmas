from spade.behaviour import OneShotBehaviour
from shared.factories.NexusChainFactory import NexusChainFactory

class Picking(OneShotBehaviour):
    def __init__(self, situation, choices):
        super().__init__()
        self.situation = situation
        self.choices = choices

    async def run(self):
        from pprint import pprint
        situation = self.situation
        choices = self.choices
        pprint(choices)
        prompt = """
        Given the situation: {}
        Pick one of the following options:
        """.format(situation)
        for i, choice in enumerate(choices):
            prompt += "\n{}) {}".format(i, choice)
        prompt += "\n"
        print(prompt)
        choice = NexusChainFactory().create_dumb_chain().predict(input=prompt)
        return choice    