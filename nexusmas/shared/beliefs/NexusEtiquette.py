
from shared.beliefs.NexusConversationalist import NexusConversationalist
from spade.behaviour import PeriodicBehaviour
from shared.behaviours.Babbling import Babbling
from shared.behaviours.Replying import Replying
from shared.brains.NexusMemory import NexusMemory
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import PromptTemplate
from shared.factories.NexusChainFactory import NexusChainFactory
from shared.beliefs.prompts.NexusPromptFactory import NexusPromptFactory


class NexusEtiquette(NexusConversationalist):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message_per_conversation = 10
        self.message_counts = {}
        self.socializing = self.NexusAgentSocializing()
        self.add_behaviour(self.socializing)
        from pprint import pprint
        print("message_counts")
        pprint(self.message_counts)

    async def handle_reply(self, msg):
        sender_str = self.get_sender_str(msg)
        print("inside nexus etiquette")
        print(sender_str)
        # Agents will use FIPA-ACL performatives
        # Check if this is from a human (private chat)
        if msg.get_metadata("performative") is None:
            # Assume normal chats
            # Humans will stop talking after a while
            await super().handle_reply(msg)
        # Check if this is from an agent (private chat)
        elif msg.get_metadata("performative") is not None:
            # Agents will talk forever
            from pprint import pprint
            pprint(sender_str)
            if sender_str not in self.message_counts:
                self.message_counts[sender_str] = 0
            pprint(self.message_counts)
            pprint(self.message_per_conversation)

            if self.message_counts[sender_str] < self.message_per_conversation:
                babble = Babbling(babbling_to=sender_str, topic=msg.body)
                self.message_counts[sender_str] += 1
                self.add_behaviour(babble)
        # Check if this is from a node (group chat)
            # Nodes will talk forever
            # Limit the number of messages per hour
            # Only respond to cfp and propose
            # Limit the number of messages per proposal and cfp

    async def start_conversation(self, send_to, msg):
        memory = NexusMemory().get_memory([send_to], save_messages=True)
        prompt = NexusPromptFactory().create_simple_prompt(memory_variable="short_term_memory", point="""
            {}
            Convert this message into your own style:
            """.format(self.personality)
        )
        dumb_chain = NexusChainFactory().create_dumb_chain(prompt=prompt, memory=memory)
        response = dumb_chain.predict(input=msg)
        reply = Replying(target=send_to, message=response)
        print("send_to", send_to)
        self.add_behaviour(reply)

    def reset_message_counts(self):
        self.message_counts = {}

    def get_prompt_parts(self):
        return {
            "identity": self.identity,
            "personality": self.personality,
            "circumstances": self.circumstances,
            "rules": self.rules,
            "output_instructions": self.output_instructions,
            "before_prompt": self.before_prompt
        }

    async def post_reaction(self, request, response):
        sender_str = NexusConversationalist().get_sender_str(request)

        replying = Replying(target=sender_str, message=response)
        # replying = StartingConversation(target=sender_str, conversation_starter=response)
        self.add_behaviour(replying)
    
    class NexusAgentSocializing(PeriodicBehaviour):
        def __init__(self, *args, **kwargs):
            # Every half hour
            super().__init__(period=120, *args, **kwargs)

        async def run(self):
            self.agent.reset_message_counts()