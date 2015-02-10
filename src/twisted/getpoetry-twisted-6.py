# This is the Twisted Get Poetry Now! client, version 2.0.

# NOTE: This should not be used as the basis for production code.

import optparse, sys, random
from twisted.internet.protocol import Protocol, ClientFactory
from twisted.internet import defer
from twisted.protocols.basic import NetstringReceiver


def parse_args():
    usage = """usage: %prog [options] [hostname]:port ...

This is the Get Poetry Now! client, Twisted version 6.0 (getpoetry, a transformed one).
Run it like this:

  python getpoetry-twisted-6.py port1 port2 port3 ... 
  
  (It means to get poetry from port2 and port3, transform from port1)

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
    
    def __init__(self, deferred):
        self.deferred = deferred
    
    def clientConnectionFailed(self, connector, reason):
        if self.deferred is not None:
            d, self.deferred = self.deferred, None
            d.errback(reason) 
    
    def poemFinished(self, poem=None):
        if self.deferred is not None:
            d, self.deferred = self.deferred, None
            d.callback(poem)
            
class XformProtocol(NetstringReceiver):
    
    def connectionMade(self):
        self.sendRequest(self.factory.xform_name, self.factory.poem)
    
    def sendRequest(self, xform_name, poem):
        self.sendString(xform_name + '.' + poem)
        
    def stringReceived(self, s):
        self.transport.loseConnection()
        self.poemReceived(s)
        
    def poemReceived(self, poem):
        self.factory.handlePoem(poem)
        
class XformClientFactory(ClientFactory):
    
    protocol = XformProtocol
    
    def __init__(self, xform_name, poem):
        self.xform_name = xform_name
        self.poem = poem
        self.deferred = defer.Deferred()
    
    def handlePoem(self, poem):
        d, self.deferred = self.deferred, None
        d.callback(poem)
    
    def clientConnectionLost(self, connector, reason):
        if self.deferred is not None:
            d, self.deferred = self.deferred, None
            d.errback(reason)
    
    clientConnectionFailed = clientConnectionLost
    
class XformProxy(object):
    
    def __init__(self, host, port):
        self.host = host
        self.port = port
        
    def xform(self, xform_name, poem):
        factory = XformClientFactory(xform_name, poem)
        from twisted.internet import reactor
        reactor.connectTCP(self.host, self.port, factory)
        return factory.deferred
    
def get_poetry(host, port):
    """
    Download a poem from the given host and port. This function
    returns a Deferred which will be fired with the complete text of
    the poem or a Failure if the poem could not be downloaded.
    """
    d = defer.Deferred()
    factory = PoetryClientFactory(d)
    from twisted.internet import reactor
    reactor.connectTCP(host, port, factory)
    return d
    
def poetry_main():
    addresses = parse_args()
    
    xform_addr = addresses.pop(0)
    proxy = XformProxy(*xform_addr)
    
    poems = []
    errors = []
    
    def try_to_lowerPoem(poem):
        d = proxy.xform('lower', poem)
        
        def lower_failed(err):
            print >>sys.stderr, 'failed to lower the poem'
            return poem
        
        def lower_succeed(poem):
            print 'lower_succeed'
            return poem
        
        return d.addErrback(lower_failed)
        # return d.addCallbacks(lower_succeed, lower_failed)
        
    def got_poem(poem):
        """a callback for getting poems"""
        poems.append(poem)
        
    def poem_failed(err):
        """a errback for getting poems when exception"""
        print >>sys.stderr, 'failed to get the poem'
        errors.append(err)
        
    def poem_done(_):
        if len(poems) + len(errors) == len(addresses):
            reactor.stop()
              
    from twisted.internet import reactor
    for address in addresses:
        host, port = address
        d = get_poetry(host, port)
        d.addCallback(try_to_lowerPoem)
        d.addCallbacks(got_poem, poem_failed)
        d.addBoth(poem_done)
        
    
    reactor.run()
    for poem in poems:
        print poem
        
if __name__ == '__main__':
    poetry_main()