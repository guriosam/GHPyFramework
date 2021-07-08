from pade.misc.utility import display_message, start_loop
from pade.core.agent import Agent
from pade.acl.messages import ACLMessage
from pade.acl.aid import AID


class Sender(Agent):
    def __init__(self, aid, receiver):
        print("[SENDER] initializing sender agent")
        super(Sender, self).__init__(aid=aid, debug=False)
        self.receiver = receiver
        self.message = None

    def on_start(self):
        print("[SENDER] started sender. executing")
        message = ACLMessage(ACLMessage.INFORM)
        print(self.receiver)
        self.agentInstance.table.update({self.receiver:AID(self.receiver)})
        message.add_receiver(AID(self.receiver))
        self.message = message

    def react(self, message):
        print("[SENDER] sender agent is reacting")
        pass