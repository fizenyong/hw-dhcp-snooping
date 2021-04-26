import logging
from pyats import aetest

#Disable AEtest default reporter logging to stdout
logging.getLogger('pyats.aetest').setLevel(logging.WARNING)

class ArpNeighbour(aetest.Testcase):

    @aetest.setup
    def setup(self):
        self.count = 0
        aetest.loop.mark(self.arp_neghbour, interf = self.parameters['generator']) #Loop for each interface
     
    @aetest.test
    def arp_neghbour(self, interf):
        #Each p2p interface neighbour arp discovery
        self.count += 1
        assert len(interf[1]['ipv4']['neighbors']) == 2

    @aetest.test
    def arp_neghbour_count(self):
        #Total 13 dwdm p2p interfaces
        assert self.count == 13

    @aetest.cleanup
    def cleanup(self):
        self.parent.result.data = self.reporter.section_details