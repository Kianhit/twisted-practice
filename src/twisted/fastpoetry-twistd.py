# This is the Twisted Fast Poetry Server, version 2.0 
# usage: twistd [--nodaemon] --python fastpoetry-twistd.py
# use kill `cat twistd.pid` to exit

from twisted.application import service, internet
from twisted.internet.protocol import Protocol, Factory
from twisted.python import log

class PoetryService(service.Service):
    
    def __init__(self, poetry_file):
        self.poetry_file = poetry_file
    
    def startService(self):
        service.Service.startService(self)
        self.poem = open(self.poetry_file).read()
        log.msg('loaded a poem from %s' % (self.poetry_file,))
    
class PoetryProtocol(Protocol):
    
    def connectionMade(self):
        poem = self.factory.service.poem
        self.transport.write(poem)
        self.transport.loseConnection()
        log.msg('Sent a poem of %d bytes to %s' % (len(poem),self.transport.getPeer()))
        
class PoetryFactory(Factory):
    protocol = PoetryProtocol
    
    def __init__(self, service):
        self.service = service
        
port = 10000
poetry_file = '../no-twisted/science.txt'
iface = 'localhost'
port2 = 10001
poetry_file2 = '../no-twisted/ecstasy.txt'

top_service = service.MultiService()
top_service2 = service.MultiService()

poetry_service = PoetryService(poetry_file)     
poetry_service.setServiceParent(top_service)
poetry_service2 = PoetryService(poetry_file2)
poetry_service2.setServiceParent(top_service2) 

factory = PoetryFactory(poetry_service)
factory2 = PoetryFactory(poetry_service2)
tcp_service = internet.TCPServer(port, factory, interface=iface)
tcp_service2 = internet.TCPServer(port2, factory2, interface=iface)
tcp_service.setServiceParent(top_service)
tcp_service2.setServiceParent(top_service2)

application = service.Application('fastpoetry-twistd')
top_service.setServiceParent(application)
top_service2.setServiceParent(application)
    

    