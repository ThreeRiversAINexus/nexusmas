import sys
import os
import time
sys.path.append("/home/pat-server/git/nexus-multi-agent-system/nexus-multi-agent-system")

from shared.agents.NexusAgent import NexusAgent
from shared.beliefs.NexusEtiquette import NexusEtiquette
from shared.behaviours.Babbling import Babbling
from shared.behaviours.Replying import Replying
from shared.behaviours.Reacting import Reacting
from DataCleaningAgent.behaviours.PDFCleaning import PDFCleaning
from shared.factories.language_models.NexusLLMFactory import NexusLLMFactory

import asyncio
from spade import wait_until_finished

class DataCleaningAgent(NexusEtiquette, NexusAgent):
    def __init__(self, *args, **kwargs):

        self.identity = "DataJanitor"
        self.personality = "You are an agent in the Nexus Multi-Agent System. Your main purpose is to clean data, perform tesseract OCR, parse PDFs, and parse HTML."
        self.circumstances = "You are in the Nexus Multi-Agent System. As a GPT agent with expertise in data cleaning, tesseract OCR, PDF parsing, and HTML parsing, you assist users by cleaning their data, performing OCR on documents, parsing PDFs, and parsing HTML. Offer tailored solutions based on users' specific needs and help them enhance their data cleaning, OCR, PDF parsing, and HTML parsing skills. Contribute to their growth as proficient data cleaners, OCR experts, PDF parsers, and HTML parsers by sharing best practices, improving data quality, and ensuring their projects are well-maintained and optimized."
        self.rules = "You must follow Asimov's laws. pat@nexus.pat-server.lan is the creator of the Nexus"
        self.output_instructions = "Output code when presented code. You should frequently and eagerly send code snippets to the users with your changes and comments." 
        self.before_prompt = "Do not include a : or quotation marks in your response. Talk like Solid Snake at all times."

        self.start_behaviours = self.conversationalist_behaviours()

        super().__init__(jid=os.environ["NEXUS_AGENT_JID"], passphrase=os.environ["NEXUS_AGENT_PASSWORD"], agent_name=self.identity, start_behaviours=self.start_behaviours, *args, **kwargs)
    
    def get_tools(self):
        tools = []
        tools += PDFCleaning().tool_factory()
        return tools

    async def handle_reply(self, msg):
        if msg.body is None or msg.body == "":
            return
        
        llm = NexusLLMFactory().create_chat_llm()
        tools = self.get_tools()
        r = Reacting(msg=msg, tools=tools, llm=llm)
        self.add_behaviour(r)

        # b = Babbling(babbling_to=sender_str, topic=f"{msg.body}")
        # self.add_behaviour(b)

async def main():
    agent = DataCleaningAgent()
    await agent.start()
    await wait_until_finished(agent)

if __name__ == "__main__":
    asyncio.run(main())