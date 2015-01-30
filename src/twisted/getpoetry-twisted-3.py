# This is the Twisted Get Poetry Now! client, version 2.0.

# NOTE: This should not be used as the basis for production code.

import optparse, sys
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
    """Protocol of twisted to receive a poem"""
    poem = ''    
    
    def dataReceived(self, data):
        self.poem += data
    
    def connectionLost(self, reason):
        self.poemReceived(self.poem)
        
    def poemReceived(self, poem):
        self.factory.poemFinished(poem)

class PoetryClientFactory(ClientFactory):
    """protocol factory of twisted to create protocol instances """
    protocol = PoetryProtocol # tell base class what proto to build
    
    def __init__(self, callback, errback):
        self.callback = callback
        self.errback = errback
    
    def clientConnectionFailed(self, connector, reason):
        self.errback(reason) 
    
    def poemFinished(self, poem=None):
        self.callback(poem)

def get_poetry(host, port, callback, errback):
    """
    Download a poem from the given host and port and invoke
 
      callback(poem)
 
    when the poem is complete. If there is a failure, invoke:
 
      errback(err)
 
    instead, where err is a twisted.python.failure.Failure instance.
    """
    factory = PoetryClientFactory(callback, errback)
    from twisted.internet import reactor
    reactor.connectTCP(host, port, factory)
    
def poetry_main():
    addresses = parse_args()
    poems = []
    errors = []
    
    def got_poem(poem):
        """a callback for getting poems"""
        poems.append(poem)
        poem_done()
        
    def poem_failed(err):
        """a errback for getting poems when exception"""
        print >>sys.stderr, 'Poem failed:', err
        errors.append(err)
        poem_done()
        
    def poem_done():
        if len(poems) + len(errors) == len(addresses):
            reactor.stop()
              
    from twisted.internet import reactor
    for address in addresses:
        host, port = address
        get_poetry(host, port, got_poem, poem_failed)
    
    reactor.run()
    for poem in poems:
        print poem
        
if __name__ == '__main__':
    poetry_main()