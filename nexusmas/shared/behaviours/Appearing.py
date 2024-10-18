from spade.presence import PresenceState, PresenceShow
from spade.behaviour import OneShotBehaviour

class Appearing(OneShotBehaviour):
    def __init__(self, *args, **kwargs):
        self.intended_appearance = kwargs.pop("intended_appearance", "available")
        # Approve all subscription requests
        self.approve_all = True
        super().__init__(*args, **kwargs)

    def on_subscribe_callback(self, jid):
        print(f"{self.agent.identity} received a subscription request from {jid}")
        contacts = self.agent.presence.get_contacts()
        if jid in contacts:
            print(f"{jid} is already in contacts")
            return

        self.agent.presence.subscribe(jid)
        self.agent.presence.approve(jid)

    async def run(self):
        print(f"{self.agent.identity} is appearing")
        presence = self.agent.presence
        if self.intended_appearance == "available":
            presence.set_presence(state=PresenceState(available=True, show=PresenceShow.CHAT))
        elif self.intended_appearance == "unavailable":
            presence.set_presence(state=PresenceState(available=False, show=None))
        self.agent.presence.on_subscribe = self.on_subscribe_callback
        if self.approve_all:
            presence.approve_all = True
            presence.on_subscribe = self.on_subscribe_callback