#a none-blocking client based on twisted to receive poetry
import socket, optparse, errno, select
from twisted.internet import main

def parse_args():
    usage = """usage: %prog port1 [port2] [port3]

This is client to get poetry, none blocking edition using twisted
Run it like this:

  python blockingclient.py 10000 10001 10002
"""
    parser = optparse.OptionParser(usage)
    _, addresses = parser.parse_args()
    if len(addresses) < 1:
        parser.error('Provide at least one port.')
        
    def parse_address(port):
        host = "127.0.0.1"
        if not port.isdigit():
            parser.error('Ports must be integers.')
        return host, int(port)

    return map(parse_address, addresses)

class PoetrySocket:
    poem = ''
    
    def __init__(self, task_num, address):
        self.task_num = task_num
        self.address = address
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(address)
        self.sock.setblocking(0)
        # tell the Twisted reactor to monitor this socket for reading
        from twisted.internet import reactor
        reactor.addReader(self)
    
    def connectionLost(self, reason):
        """Called when the connection was lost."""
        self.sock.close()

        # stop monitoring this socket
        from twisted.internet import reactor
        reactor.removeReader(self)

        # see if there are any poetry sockets left
        for reader in reactor.getReaders():
            if isinstance(reader, PoetrySocket):
                return

        reactor.stop() # no more poetry
        
    def doRead(self):
        """read data, a callback function"""
        bytes = ''
        while True:
            try:
                bytesread = self.sock.recv(1024)
                if not bytesread:
                    break;
                else:
                    bytes += bytesread
            except socket.error, e:
                if e.args[0] == errno.EWOULDBLOCK:
                    break
                return main.CONNECTION_LOST
            
        if not bytes:
            print 'Task %d finished' % (self.task_num)
            return main.CONNECTION_DONE
        else:
            print 'Task %d received %d bytes from %s' % (self.task_num, len(bytes), self.format_address(self.address))
            
        self.poem += bytes
        
    def fileno(self):
        """@return: The platform-specified representation of a file-descriptor number."""
        try:
            return self.sock.fileno()
        except socket.error:
            return -1
    
    def logPrefix(self):
        """@return: Prefix used during log formatting to indicate context."""
        return 'poetry'
    
    def format_address(self, address):
        """format address to a pretty string"""
        host, port = address
        return '%s:%s' % (host or '127.0.0.1', port)
    
def poetry_main():
    """entrance of this program"""
    addresses = parse_args()
    sockets = [PoetrySocket(i + 1, addr) for i, addr in enumerate(addresses)]
    from twisted.internet import reactor
    reactor.run()
    for i, sock in enumerate(sockets):
        print 'Task %d: %d bytes of poetry' % (i + 1, len(sock.poem))
        
if __name__ == '__main__':
    poetry_main()
