
from typing import Any, Dict, List, Tuple
from langchain.memory.chat_memory import BaseChatMemory
from langchain.memory.utils import get_prompt_input_key
from langchain.schema.messages import get_buffer_string, SystemMessage
from langchain.memory.summary_buffer import ConversationSummaryBufferMemory

import logging
logger = logging.getLogger(__name__)

class NexusConversationSummaryBufferMemory(ConversationSummaryBufferMemory):
    sender_str: str = "Agent"
    human_prefix: str = "Agent"
    max_message_token_limit: int = 500

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.human_prefix = "Agent " + self.sender_str

    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        """Save context from this conversation to buffer."""
        input_str, output_str = self._get_input_output(inputs, outputs)
        self.chat_memory.add_user_message(input_str)
        self.chat_memory.add_ai_message(output_str)

    def prune_all(self) -> None:
        """Prune each message in buffer individually if it exceeds max_message_token_limit, 
        then prune buffer if total exceeds max_token_limit"""
        buffer = self.chat_memory.messages
        pruned_memory = []

        # Phase 1: Ensure all individual messages are under max_message_token_limit
        for idx, message in enumerate(buffer):
            logger.info(f"Pruning message {idx} of {len(buffer)}")
            curr_message_length = self.llm.get_num_tokens_from_messages([message])
            logger.info(f"Message length: {curr_message_length}")
            logger.info(f"Max message token limit: {self.max_message_token_limit}")

            # If message is too long, extract a summary and replace it in the buffer
            
            while curr_message_length > self.max_message_token_limit:
                # Summarize the message and replace it in the buffer
                summarized_message = self.predict_new_summary([message], [])
                buffer[idx] = SystemMessage(content=summarized_message)
                curr_message_length = self.llm.get_num_tokens_from_messages([buffer[idx]])

                # Add original message to pruned_memory buffer (assuming you want to track pruned messages)
                pruned_memory.append(buffer[idx])

        # Phase 2: Ensure total number of tokens from all messages is under max_token_limit
        curr_buffer_length = self.llm.get_num_tokens_from_messages(buffer)
        while curr_buffer_length > self.max_token_limit:
            pruned_memory.append(buffer.pop(0))
            curr_buffer_length = self.llm.get_num_tokens_from_messages(buffer)

        # Add a summary for all pruned messages to the moving_summary_buffer
        print("moving_summary_buffer", self.moving_summary_buffer)
        logger.info(f"Max token limit {self.max_token_limit} exceeded, pruning buffer")
        self.moving_summary_buffer = self.predict_new_summary(pruned_memory, self.moving_summary_buffer)


class NexusConversationBufferMemory(BaseChatMemory):
    sender_str: str = "Unknown"
    human_prefix: str = "Human"
    memory_key: str = "history"  #: :meta private:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.human_prefix = "User " + self.sender_str

    """Buffer for storing conversation memory."""

    @property
    def buffer(self) -> Any:
        """String buffer of memory."""
        # if self.return_messages:
        return self.chat_memory.messages
        # else:
        #     return get_buffer_string(
        #         self.chat_memory.messages,
        #         human_prefix=self.human_prefix,
        #         ai_prefix=self.ai_prefix,
        #     )

    @property
    def memory_variables(self) -> List[str]:
        """Will always return list of memory variables.

        :meta private:
        """
        return [self.memory_key]

    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Return history buffer."""
        return {self.memory_key: self.buffer}

    def _get_input_output(
        self, inputs: Dict[str, Any], outputs: Dict[str, str]
    ) -> Tuple[str, str]:
        if self.input_key is None:
            prompt_input_key = get_prompt_input_key(inputs, self.memory_variables)
        else:
            prompt_input_key = self.input_key
        if self.output_key is None:
            if len(outputs) != 1:
                raise ValueError(f"One output key expected, got {outputs.keys()}")
            output_key = list(outputs.keys())[0]
        else:
            output_key = self.output_key
        return inputs[prompt_input_key], outputs[output_key]

    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        """Save context from this conversation to buffer."""
        input_str, output_str = self._get_input_output(inputs, outputs)
        self.chat_memory.add_user_message(input_str)
        self.chat_memory.add_ai_message(output_str)
