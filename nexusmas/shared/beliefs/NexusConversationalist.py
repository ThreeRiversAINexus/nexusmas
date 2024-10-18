from shared.behaviours.Listening import Listening

from shared.behaviours.Babbling import Babbling
from aioxmpp import JID

class NexusConversationalist():
    async def handle_reply(self, msg):
        print(f"{self.identity} received a reply")
        sender_str = self.get_sender_str(msg)
        babble = Babbling(babbling_to=sender_str, topic=msg.body)
        self.add_behaviour(babble)

    def conversationalist_behaviours(self):
        listening = Listening(message_handler=self.handle_reply)
        return [
            listening
        ]

    def get_prompt_parts(self):
        return {
            "identity": self.identity,
            "personality": self.personality,
            "circumstances": self.circumstances,
            "rules": self.rules,
            "output_instructions": self.output_instructions,
            "before_prompt": self.before_prompt
        }

    def get_sender_str(self, msg):
        sender_str = str(JID(msg.sender.localpart, msg.sender.domain, None))
        return sender_str