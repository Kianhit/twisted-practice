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

top_service = service.MultiService()

poetry_service = PoetryService(poetry_file)     
poetry_service.setServiceParent(top_service)

factory = PoetryFactory(poetry_service)
tcp_service = internet.TCPServer(port, factory, interface=iface)
tcp_service.setServiceParent(top_service)

application = service.Application('fastpoetry-twistd')
top_service.setServiceParent(application)
    

    