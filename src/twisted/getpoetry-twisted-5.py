# This is the Twisted Get Poetry Now! client, version 2.0.

# NOTE: This should not be used as the basis for production code.

import optparse, sys, random
from twisted.internet.protocol import Protocol, ClientFactory
from twisted.internet import defer


def parse_args():
    usage = """usage: %prog [options] [hostname]:port ...

This is the Get Poetry Now! client, Twisted version 5.0 (a defered version with Lord Byron).
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

class ByronExcept(Exception): pass

class ByronBugExcept(Exception): pass

def transferToByronStylePoem(poem):
    
    def succeed():
        print '-------calling succeed()-------'
        return poem.lower()
    
    def raiseByronError():
        print '-------calling raiseByronError()-------'
        raise ByronExcept
    
    def bug():
        print '-------calling bug()-------'
        raise ByronBugExcept(poem)
    
    return random.choice([succeed, raiseByronError, bug])()
    
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
    poems = []
    errors = []
    
    def byronStyle_failed(err):
        if err.check(ByronBugExcept):
            print 'failed to transfer to Byron style'
            return err.value.args[0]
        return err
    
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
        d.addCallback(transferToByronStylePoem)
        d.addErrback(byronStyle_failed)
        d.addCallbacks(got_poem, poem_failed)
        d.addBoth(poem_done)
        
    
    reactor.run()
    for poem in poems:
        print poem
        
if __name__ == '__main__':
    poetry_main()