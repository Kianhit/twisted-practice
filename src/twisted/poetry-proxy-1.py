import optparse
from twisted.internet.protocol import Protocol, ClientFactory, ServerFactory
from twisted.internet import defer
from twisted.internet.defer import maybeDeferred

def parse_args():
    usage = """usage: %prog [options] [hostname]:port

This is the Poetry Proxy, version 1.0.

  python poetry-proxy.py [hostname]:port

"""

    parser = optparse.OptionParser(usage)

    help = "The port to listen on. Default to a random available port."
    parser.add_option('-p', '--port', type='int', help=help)

    help = "The interface to listen on. Default is localhost."
    parser.add_option('-s' ,'--host', help=help, default='localhost')

    options, args = parser.parse_args()

    if len(args) != 1:
        parser.error('Provide exactly one server address.')

    def parse_address(addr):
        if ':' not in addr:
            host = '127.0.0.1'
            port = addr
        else:
            host, port = addr.split(':', 1)

        if not port.isdigit():
            parser.error('Ports must be integers.')

        return host, int(port)

    return options, parse_address(args[0])

class PoetryProxyService(object):
    
    poem = None
    
    def __init__(self, host, port):
        self.host = host
        self.port = port
        
    def getPoem(self):
        #print '---calling getPoem---'
        if self.poem is not None:
            print '---Getting poem from cache---'
            return self.poem
        
        print '---Getting poem from the remote server---'
        d = defer.Deferred()
        factory = PoetryClientFactory(d)
        d.addCallback(self.setPoem)
        from twisted.internet import reactor
        reactor.connectTCP(self.host, self.port, factory)
        return d
    
    def setPoem(self, poem):
        #print '---calling setPoem---'
        self.poem = poem
        return poem
        
class PoetryClientProtocol(Protocol):
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
    protocol = PoetryClientProtocol # tell base class what proto to build
    
    def __init__(self, deferred):
        self.deferred = deferred
    
    def clientConnectionFailed(self, connector, reason):
        if self.deferred is not None:
            d, self.deferred = self.deferred, None
            d.errback(reason) 
    
    def poemFinished(self, poem=None):
        if self.deferred is not None:
            d, self.deferred = self.deferred, None
            #print '---calling poemFinished---'
            d.callback(poem)
            
class PoetryProxyProtocol(Protocol):
    
    def connectionMade(self):
        #print '---calling connectionMade---'
        d = maybeDeferred(self.factory.service.getPoem)
        d.addCallback(self.transport.write)
        d.addBoth(lambda r: self.transport.loseConnection())
                
class PoetryProxyFactory(ServerFactory):
    protocol = PoetryProxyProtocol
    
    def __init__(self, service):
        self.service = service
        
def proxy_main():
    options, server_addr = parse_args()
    
    service = PoetryProxyService(*server_addr)
    
    factory = PoetryProxyFactory(service)
    from twisted.internet import reactor

    port = reactor.listenTCP(options.port or 0, factory,
                             interface=options.host)
    
    print 'Proxying %s on %s.' % (server_addr, port.getHost())
    
    reactor.run()
    
if __name__ == '__main__':
    proxy_main()
    