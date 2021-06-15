from pade.misc.utility import display_message, start_loop
from pade.core.agent import Agent
from pade.acl.aid import AID
from sys import argv

class ToolReceiveAgent(Agent):

    def __init__(self, aid):
        super(ToolReceiveAgent, self).__init__(aid=aid)
        display_message(self.aid.localname, 'Hello World!')


if __name__ == '__main__':

    agents_per_process = 3
    c = 0
    agents = list()
    for i in range(agents_per_process):
        port = 1000 + c
        agent_name = 'agent_hello_{}@localhost:{}'.format(port, port)
        agente_tool = ToolReceiveAgent(AID(name=agent_name))
        agents.append(agente_tool)
        c += 1000

    start_loop(agents)