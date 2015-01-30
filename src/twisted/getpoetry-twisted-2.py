# This is the Twisted Get Poetry Now! client, version 2.0.

# NOTE: This should not be used as the basis for production code.

import datetime, optparse
from twisted.internet.protocol import Protocol, ClientFactory


def parse_args():
    usage = """usage: %prog [options] [hostname]:port ...

This is the Get Poetry Now! client, Twisted version 2.0.
Run it like this:

  python getpoetry-twisted-2.py port1 port2 port3 ...

"""

    parser = optparse.OptionParser(usage)

    _, addresses = parser.parse_args()

    if not addresses:
        print parser.format_help()
        parser.exit()

    def parse_address(addr):
        if ':' not in addr:
            host = '127.0.0.1'
            port = addr
        else:
            host, port = addr.split(':', 1)

        if not port.isdigit():
            parser.error('Ports must be integers.')

        return host, int(port)

    return map(parse_address, addresses)


class PoetryProtocol(Protocol):
    poem = ''
    task_num = 0
    
    def dataReceived(self, data):
        self.poem += data
        print 'Task %d received %d bytes' % (self.task_num, len(data))
    
    def connectionLost(self, reason):
        self.factory.poemFinished(self.task_num, self.poem)

class PoetryClientFactory(ClientFactory):
    task_num = 1
    protocol = PoetryProtocol
    
    def __init__(self, poetry_count):
        self.poetry_count = poetry_count
        self.poems = {}
        
    def buildProtocol(self, addr):
        proto = ClientFactory.buildProtocol(self, addr)
        proto.task_num = self.task_num
        self.task_num += 1
        return proto
    
    def clientConnectionFailed(self, connector, reason):
        print 'Failed to connect to :' , connector.getDestination() 
    
    def poemFinished(self, task_num, poem):
        print 'Task %d finished receiving data' % task_num
        self.poems[task_num] = poem
        self.poetry_count -= 1
        
        if self.poetry_count == 0:
            self.report()
            from twisted.internet import reactor
            reactor.stop()
    
    def report(self):
        # print self.poems
        for i in self.poems:
            print 'Task %d: %d bytes of a poetry' % (i, len(self.poems[i]))
        
def poetry_main():
    addresses = parse_args()

    start = datetime.datetime.now()

    factory = PoetryClientFactory(len(addresses))

    from twisted.internet import reactor

    for address in addresses:
        host, port = address
        reactor.connectTCP(host, port, factory)

    reactor.run()

    elapsed = datetime.datetime.now() - start

    print 'Got %d poems in %s' % (len(addresses), elapsed)


if __name__ == '__main__':
    poetry_main()
