#usage: twistd -ny poetry-proxy-twistd.py --pidfile proxy.twistd.pid
from twisted.internet.protocol import Protocol, ClientFactory, ServerFactory
from twisted.application.service import Service
from twisted.application import service, internet
from twisted.internet.defer import Deferred, maybeDeferred
from twisted.python import log

class PoetryProtocol(Protocol):
    
    poem = ''
    
    def dataReceived(self, data):
        self.poem += data
        
    def connectionLost(self, reason):
        self.poemReceived()
        
    def poemReceived(self):
        self.factory.poemFinished(self.poem)
        
class PoetryClientFactory(ClientFactory):
    
    protocol = PoetryProtocol
    
    def __init__(self, deferred):
        self.deferred = deferred
    
    def poemFinished(self, poem):
        if self.deferred is not None:
            d, self.deferred = self.deferred, None
            return d.callback(poem)
        
    def clientConnectionFailed(self, connector, reason):
        if self.deferred is not None:
            d, self.deferred = self.deferred, None
            return d.errback(poem)
    
    clientConnectionLost = clientConnectionFailed
    
class PoetryProxyService(Service):
    poem = None
    
    def __init__(self, host, port):
        self.host = host
        self.port = port
    
    def startService(self):
        Service.startService(self)
    
    def getPoem(self):
        if self.poem is not None:
            log.msg('returned a poem from cache...')
            return self.poem
        else:
            log.msg('returned a poem from poetry server...')
            d = Deferred()
            factory = PoetryClientFactory(d)
            d.addCallback(self.setPoem)
            from twisted.internet import reactor
            reactor.connectTCP(self.host, self.port, factory)
            return d
        
    def setPoem(self, poem):
        self.poem = poem
        return poem
        
class PoetryProxyProtocol(Protocol):
    
    def connectionMade(self):
        d = maybeDeferred(self.factory.service.getPoem)
        d.addCallbacks(self.transport.write)
        d.addBoth(lambda r: self.transport.loseConnection())
        
class PoetryProxyFactory(ServerFactory):
    
    protocol = PoetryProxyProtocol
    
    def __init__(self, service):
        self.service = service
        
host = 'localhost'
port = 10002
port1 = 10000 

top_service = service.MultiService()
    
proxy_service = PoetryProxyService(host, port1)
proxy_service.setServiceParent(top_service)

factory = PoetryProxyFactory(proxy_service)
tcp_service = internet.TCPServer(port, factory, interface=host)
tcp_service.setServiceParent(top_service)

application = service.Application('fastpoetry-proxy-twistd')
top_service.setServiceParent(application)