from langchain.memory.chat_message_histories import ZepChatMessageHistory

import logging
from typing import TYPE_CHECKING, Dict, List, Optional

from langchain.schema import (
    AIMessage,
    BaseChatMessageHistory,
    BaseMessage,
    HumanMessage,
)

if TYPE_CHECKING:
    from zep_python import Memory, MemorySearchResult, Message, NotFoundError

import os

from shared.database.NexusDatabase import NexusDatabase

logger = logging.getLogger(__name__)
class NexusZepMemoryHistory(ZepChatMessageHistory):
    def __init__(self, participants, save_messages=True, *args, **kwargs):
        # participants is a [] of jabber_ids
        zep_session_id = self._get_zep_session_id(participants)
        self.save_messages = save_messages

        zep_url = kwargs.pop("zep_url", os.environ.get("NEXUS_ZEP_URL", None))
        from pprint import pprint
        pprint(zep_url)
        super().__init__(session_id=str(zep_session_id), url=zep_url, *args, **kwargs)

    def clear(self):
        pass

    def add_message(self, *args, **kwargs):
        from pprint import pprint
        pprint(*args, )
        if self.save_messages:
            return super().add_message(*args, **kwargs)
        else:
            pass

    def get_zep_session_id(self):
        return str(self.session_id)

    def _get_zep_session_id(self, participants) -> str:
        nexus_database = NexusDatabase()
        created_by = nexus_database.get_user(jabber_id=participants[0])["id"]

        for participant in participants:
            nexus_database.get_user(jabber_id=participant)

        # Find the latest session with these participants
        query = """
            SELECT s.zep_session_id
            FROM sessions AS s
            JOIN session_users AS su ON su.session_id = s.id
            JOIN users AS u ON u.id = su.user_id
            WHERE u.jabber_id = ANY(%s)
            AND s.created_by = %s
            GROUP BY s.zep_session_id
            HAVING COUNT(DISTINCT u.jabber_id) = %s
            ORDER BY MAX(s.created_at) DESC
            LIMIT 1;
        """

        # Fetch the latest session ID with the given participants
        created_by_id = nexus_database.get_user(jabber_id=participants[0])["id"]
        result = nexus_database.query(query, (participants, created_by_id, len(participants)))
        from pprint import pprint
        print("nexuz zep memory history")
        pprint(result)
        if result:
            return result[0]["zep_session_id"]

        # If no session exists, create a new session
        create_session_query = """
            INSERT INTO sessions (zep_session_id, created_by)
            VALUES (gen_random_uuid(), %s)
            RETURNING zep_session_id;
        """
        result = nexus_database.insert(create_session_query, (created_by,))
        zep_session_id = result["zep_session_id"]

        # get the session_id
        get_sesh_id = """
            SELECT id
            FROM sessions
            WHERE zep_session_id = %s;
        """
        result = nexus_database.query(get_sesh_id, (zep_session_id,))
        session_id = result[0]["id"]

        # Insert participants into the session_users table
        from pprint import pprint
        pprint(participants)
        pprint(result)

        insert_participants_query = """
            INSERT INTO session_users (session_id, user_id)
            SELECT %s, u.id
            FROM users AS u
            WHERE u.jabber_id = ANY(%s)
            RETURNING session_id;
        """
        nexus_database.insert(insert_participants_query, (session_id, participants))

        return str(zep_session_id)

from langchain.schema import BaseMemory
from pydantic import BaseModel
from typing import Dict, Any
from langchain.retrievers import ZepRetriever
from zep_python.exceptions import NotFoundError
from langchain.chains import RetrievalQA
from langchain.memory.chat_memory import BaseChatMemory
from langchain.llms import OpenAI
class ZepSearchMemory(BaseMemory, BaseModel):
    url: str
    session_id: str
    memory_key: str
    zep_retriever: Optional[ZepRetriever] = None
    short_term_memory: BaseChatMemory

    """Memory class for searching Zep about any inputs."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        zep_retriever = ZepRetriever(
            session_id=str(self.session_id),
            url=self.url,
            top_k=3,
        )
        self.zep_retriever = zep_retriever

    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        query = inputs.get("input")
        if query:
            try:
                short_term_memory_context = self.short_term_memory.buffer
                docs = self.zep_retriever.get_relevant_documents(' '.join([str(short_term_memory_context)] + [str(query)]))

                relevant_documents = []
                for doc in docs:
                    page_content = doc.page_content
                    relevant_documents += [page_content]
                
                relevant_documents = '\n'.join(relevant_documents)

            except NotFoundError:
                relevant_documents = []
            return {self.memory_key: relevant_documents}
        return {}

    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        pass

    def clear(self) -> None:
        pass

    @property
    def memory_variables(self) -> List[str]:
        """Will always return list of memory variables.

        :meta private:
        """
        return [self.memory_key]