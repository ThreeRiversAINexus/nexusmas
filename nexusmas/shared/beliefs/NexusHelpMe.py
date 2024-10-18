class NexusHelpMe():
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def run(self):
        print(f"{self.agent.agent_name} is getting help")
        # receive a message
        # given a list of agents
        # decide which agent to ask for help
        # then relay the answer to the original agent