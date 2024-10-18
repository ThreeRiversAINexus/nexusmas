class NexusChatHistories():
    _instance = None
    histories = {}

    def __init__(self):
        if NexusChatHistories._instance is not None:
            pass
        NexusChatHistories._instance = self

    @staticmethod
    def get_instance():
        if NexusChatHistories._instance is None:
            NexusChatHistories()
        return NexusChatHistories._instance
