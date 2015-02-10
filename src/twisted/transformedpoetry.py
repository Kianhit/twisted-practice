import optparse
from twisted.internet.protocol import ServerFactory
from twisted.protocols.basic import NetstringReceiver


def parse_args():
    usage = """usage: %prog [options]

This is the Poetry Transform Server.
Run it like this:

  python transformedpoetry.py

"""

    parser = optparse.OptionParser(usage)

    help = "The port to listen on. Default to a random available port."
    parser.add_option('-p', '--port', type='int', help=help)

    help = "The interface to listen on. Default is localhost."
    parser.add_option('-s', '--host', help=help, default='localhost')

    options, args = parser.parse_args()

    if len(args) != 0:
        parser.error('Bad arguments.')

    return options

class TransformService():
    
    def lowerPoem(self, poem):
        return poem.lower()
    
class TransformProtocol(NetstringReceiver):
    
    def stringReceived(self, request):
        if '.' not in request:
            self.transport.loseConnection()
            return
        
        xform_name, poem = request.split('.', 1)
        self.xformRequestReceived(xform_name, poem)
        
        
    def xformRequestReceived(self, xform_name, poem):     
        new_poem = self.factory.xformRequest(xform_name, poem)
        if new_poem is not None:
            self.sendString(new_poem)
        
        self.transport.loseConnection()
        
        
class TransformFactory(ServerFactory):
    protocol = TransformProtocol
    
    def __init__(self, service):
        self.service = service
        
    def xformRequest(self, xform_name, poem):
        trunk = getattr(self, 'xform_%s' % (xform_name,), None)
        if trunk is None:
            return None
        
        try:
            return trunk(poem)
        except:
            return None
        
    def xform_lower(self, poem):
        rslt = self.service.lowerPoem(poem)
        return rslt
    
def transform_main():
    options = parse_args()
    
    service =  TransformService()
    factory = TransformFactory(service)
    from twisted.internet import reactor
    port = reactor.listenTCP(options.port, factory, interface=options.host)
    print 'Serving transforms on %s' % (port.getHost())
    
    reactor.run()
    
if __name__ == '__main__':
    transform_main()
    