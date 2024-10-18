from langchain.memory import PostgresChatMessageHistory
import os
import json
import logging
from langchain.schema import (
    BaseChatMessageHistory,
    BaseMessage,
    messages_from_dict,
    _message_to_dict
)

from shared.database.NexusDatabase import NexusDatabase

from typing import List

logger = logging.getLogger(__name__)

class NexusPostgresMemoryHistory(PostgresChatMessageHistory):
    def __init__(self, sender_str=None, *args, **kwargs):
        if sender_str is None:
            raise Exception("sender_str is required")
        self.sender_str = sender_str
        self.last_n_messages = kwargs.pop("last_n_messages", 10)
        self.nexus_database = NexusDatabase()
        self.nexus_database.bootstrap()
        self.my_jabber_id = kwargs.pop("my_jabber_id", os.environ.get("NEXUS_AGENT_JID", None))
        session_id = kwargs.pop("session_id", None)
        if session_id is None:
            # select sessions with this user_id
            # in the last 24 hours
            sessions = self.nexus_database.query("""
                SELECT id FROM sessions WHERE user_id = %s AND created_at > NOW() - INTERVAL '24 hours';
            """, (self.get_user(jabber_id=self.my_jabber_id)["id"],))
            # Get the last session
            print("sessions")
            from pprint import pprint
            pprint(sessions)
            if len(sessions) > 0:
                session_id = sessions[0]["id"]
            else:
                session_id = self.new_session(sender_str=self.my_jabber_id)
        self.session_id = session_id

    def new_session(self, sender_str: str) -> None:
        user = self.get_user(jabber_id=sender_str)

        user_id = int(user["id"])
        from pprint import pprint
        print("new_session")
        pprint(user)
        result = self.nexus_database.insert("""
            INSERT INTO sessions (user_id) VALUES (%s)
            RETURNING id;
        """, (user_id,))
        print("new_session")
        pprint(result)
        return result["id"]

    @property
    def messages(self) -> List[BaseMessage]:  # type: ignore
        """Retrieve the last N messages from PostgreSQL in reverse order"""
        query = f"SELECT content FROM messages WHERE session_id = %s ORDER BY id DESC LIMIT %s;"
        items = self.nexus_database.query(query, (self.session_id, self.last_n_messages))
        from pprint import pprint
        items = [record["content"] for record in reversed(items)]
        print("items")
        pprint(items)
        messages = messages_from_dict(items)
        print("messages")
        pprint(messages)
        cleaned_messages = []

        for message in messages:
            if message.type == "ai":
                cleaned_messages.append("You: " + message.content + "\n")
            elif message.type == "human":
                cleaned_messages.append("User " + self.sender_str + ": " + message.content + "\n")
            elif message.type == "system":
                cleaned_messages.append("System: " + message.content + "\n")
        
        cleaned_messages = "".join(cleaned_messages)
        return cleaned_messages

    def _create_user(self, user: dict) -> None:
        result = self.nexus_database.insert("""
            INSERT INTO users (jabber_id) VALUES (%s)
            RETURNING id;
        """, (user["jabber_id"],))
        from pprint import pprint
        print("_create_user")
        pprint(result)
        return result
    
    def get_user(self, jabber_id):
        query = "SELECT * FROM users WHERE jabber_id = %s;"
        result = self.nexus_database.query(query, (jabber_id,))
        if len(result) == 0:
            user_id = self._create_user({
                "jabber_id": jabber_id 
            })
            result = self.nexus_database.query(query, (jabber_id,))
            user = result[0]
        else:
            user = result[0]
        return user

    def add_message(self, message: BaseMessage) -> None:
        """Append the message to the record in PostgreSQL"""
        if message.type == "ai":
            user = self.get_user(jabber_id=self.my_jabber_id)
        elif message.type == "human":
            user = self.get_user(jabber_id=self.sender_str)

        from pprint import pprint
        pprint(user)
        pprint(self.session_id)
        self.nexus_database.insert("""
            INSERT INTO messages (session_id, user_id, content) VALUES (%s, %s, %s)
            RETURNING id;
        """, (self.session_id, user["id"], json.dumps(_message_to_dict(message))))
    
    def __del__(self):
        pass