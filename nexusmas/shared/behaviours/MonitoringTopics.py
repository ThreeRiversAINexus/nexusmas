from spade.behaviour import OneShotBehaviour
from shared.tools.nexusgensim import NexusGensim
class MonitoringTopics(OneShotBehaviour):
    def __init__(self, corpus, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.corpus = corpus
        self.callback = kwargs.pop("callback", None)

    async def run(self):
        gs = NexusGensim()
        gs.preprocess(self.corpus)
        gs.run_lda()
        topics = gs.get_dominant_topic_terms()
        if self.callback:
            self.callback(topics)
        