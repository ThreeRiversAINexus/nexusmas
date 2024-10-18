from spade.behaviour import PeriodicBehaviour
from shared.factories.NexusChainFactory import NexusChainFactory
from shared.beliefs.prompts.NexusPromptFactory import NexusPromptFactory
from shared.brains.NexusMemory import NexusMemory
from shared.behaviours.Replying import Replying
from shared.factories.language_models.NexusLLMFactory import NexusLLMFactory
import asyncio

class Thinking(PeriodicBehaviour):
    def __init__(self, *args, **kwargs):
        self.meditation_topic = kwargs.pop("meditation_topic", None)
        minutes = 30
        super().__init__(period=(60*minutes), *args, **kwargs)
    
    async def run(self):
        print(f"{self.agent.identity} is thinking")
        memory = NexusMemory().get_memory(["pat@nexus.pat-server.lan"], save_messages=False)
        prompt_parts = self.agent.get_prompt_parts()
        prompt = NexusPromptFactory().create_simple_prompt(point=f"""
=======
About the AI:
You are {prompt_parts["identity"]}
{prompt_parts["personality"]}
{prompt_parts["circumstances"]}
=======
System: The AI is sharing their thoughts and coming up with something to say.Thinking is the process of considering or reasoning about something. It involves processing information, generating thoughts, and drawing conclusions based on that information. You are now thinking freely.
=======""")
        llm = NexusLLMFactory().create_chat_llm(temperature=1.0)
        dumb_chain = NexusChainFactory().create_dumb_chain(prompt=prompt, memory=memory, llm=llm)
        response = dumb_chain.predict(input="{}".format(
    f"""Agent {self.agent.identity}@nexus.pat-server.lan: """))
        # memory.save_context(inputs={}, outputs={response})

        name = "pat"
        target = "{}@nexus.pat-server.lan".format(name) 
        print(f"Sending message to {target}")
        print(f"Message: {response}")

        memory = NexusMemory().get_memory(["pat@nexus.pat-server.lan"], save_messages=True, max_token_limit=500)
        memory.save_context(inputs={"input": "(user said nothing, you started the conversation)"}, outputs={"output": response})
        
        reply = Replying(target=target, message=response)
        # sleep for 10 seconds
        self.agent.add_behaviour(reply)