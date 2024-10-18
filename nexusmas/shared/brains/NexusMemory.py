import os
from langchain.memory import CombinedMemory, ConversationBufferMemory
from shared.brains.NexusPostgresMemoryHistory import NexusPostgresMemoryHistory
from shared.brains.NexusZepMemoryHistory import NexusZepMemoryHistory, ZepSearchMemory
from shared.brains.NexusVectorstoreMemory import NexusVectorstoreMemory
from shared.brains.NexusChatHistories import NexusChatHistories
from shared.brains.NexusConversationBufferMemory import NexusConversationBufferMemory, NexusConversationSummaryBufferMemory
from shared.factories.language_models.NexusLLMFactory import NexusLLMFactory
from langchain.memory import VectorStoreRetrieverMemory
from langchain.retrievers import ZepRetriever
from langchain.vectorstores.base import VectorStoreRetriever
from langchain.memory import ConversationEntityMemory

# https://python.langchain.com/en/latest/modules/memory/examples/multiple_memory.html
# https://python.langchain.com/en/latest/modules/memory/types/vectorstore_retriever_memory.html

class NexusMemory():
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_memory(self, participants, *args, **kwargs):
        my_jabber_id = kwargs.pop("my_jabber_id", os.environ.get("NEXUS_AGENT_JID", None))
        participants = [my_jabber_id] + participants
        participants = [participant.lower() for participant in participants]

        from pprint import pprint
        pprint(participants)

        if 'save_messages' in kwargs:
            save_messages = kwargs['save_messages']
        else:
            save_messages = True

        zep_chat_memory = NexusZepMemoryHistory(participants, save_messages=save_messages)

        if 'short_term_memory_key' in kwargs:
            short_term_memory_key = kwargs['short_term_memory_key']
        else:
            short_term_memory_key = "short_term_memory"

        if 'return_messages' in kwargs:
            return_messages = kwargs['return_messages']
        else:
            return_messages = False

        if 'max_token_limit' in kwargs:
            max_token_limit = kwargs['max_token_limit']
        else:
            max_token_limit = 1000

        from pprint import pprint
        pprint(max_token_limit)
        short_term_memory = NexusConversationSummaryBufferMemory(
            llm=NexusLLMFactory().create_llm(),
            input_key="input",
            chat_memory=zep_chat_memory,
            memory_key=short_term_memory_key,
            ai_prefix = "Agent " + participants[0],
            sender_str = participants[1],
            max_token_limit=max_token_limit,
            return_messages=return_messages
        )
        short_term_memory.prune_all()

        return CombinedMemory(memories=[short_term_memory])

    def get_dumb_memory(self, participants, *args, **kwargs):
        my_jabber_id = kwargs.pop("my_jabber_id", os.environ.get("NEXUS_AGENT_JID", None))
        participants = [my_jabber_id] + participants
        participants = [participant.lower() for participant in participants]

        from pprint import pprint
        pprint(participants)

        # zep_chat_memory = NexusZepMemoryHistory(participants)

        if 'short_term_memory_key' in kwargs:
            short_term_memory_key = kwargs['short_term_memory_key']
        else:
            short_term_memory_key = "short_term_memory"

        if 'return_messages' in kwargs:
            return_messages = kwargs['return_messages']
        else:
            return_messages = True

        short_term_memory = ConversationBufferMemory(
            input_key="input",
            # chat_memory=zep_chat_memory,
            memory_key=short_term_memory_key,
            ai_prefix = "Agent " + participants[0],
            human_prefix = "Agent " + participants[1],
        )

        return short_term_memory



# Need a custom BaseMessage and AIMessage/HumanMessage/SystemMessage

# Need BaseChatMemory save_context overrode.

#   File "/home/pat-server/git/nexus-multi-agent-system/nexus-multi-agent-system/shared/behaviours/Babbling.py", line 22, in run
#     msg.body = self.chain.predict(input=self.topic)
#   File "/home/pat-server/.pyenv/versions/3.9.16/lib/python3.9/site-packages/langchain/chains/llm.py", line 213, in predict
#     return self(kwargs, callbacks=callbacks)[self.output_key]
#   File "/home/pat-server/.pyenv/versions/3.9.16/lib/python3.9/site-packages/langchain/chains/base.py", line 147, in __call__
#     final_outputs: Dict[str, Any] = self.prep_outputs(
#   File "/home/pat-server/.pyenv/versions/3.9.16/lib/python3.9/site-packages/langchain/chains/base.py", line 211, in prep_outputs
#     self.memory.save_context(inputs, outputs)
#   File "/home/pat-server/.pyenv/versions/3.9.16/lib/python3.9/site-packages/langchain/memory/combined.py", line 75, in save_context
#     memory.save_context(inputs, outputs)
#   File "/home/pat-server/.pyenv/versions/3.9.16/lib/python3.9/site-packages/langchain/memory/chat_memory.py", line 35, in save_context
#     self.chat_memory.add_user_message(input_str)
#   File "/home/pat-server/.pyenv/versions/3.9.16/lib/python3.9/site-packages/langchain/schema.py", line 270, in add_user_message
#     self.add_message(HumanMessage(content=message))