from shared.beliefs.NexusEtiquette import NexusEtiquette
from spade_pubsub import PubSubMixin


# here's what I'm thinking
# nexus collaborator is lets nexus
# agents send a message to a node
# the node will send a message to
# all of the other collaborators
# then the collaborators will respond
# to the node

# We want to limit the number of messages
# We also want to wait until all collaborators
# have responded

# I actually need an agent to pre-process
# the messages before they get sent to the
# node
class NexusCollaborator(NexusEtiquette, PubSubMixin):
    def __init__(self, *args, **kwargs):
        pass

    async def request_collaboration(self, msg):
        pass
    
    def collaborate(self, msg):
        pass