#a none-blocking client based on twisted to receive poetry
import socket, optparse, errno, select

def parse_args():
    usage = """usage: %prog port1 [port2] [port3]

This is client to get poetry, blocking edition
Run it like this:

  python blockingclient.py 10000 10001 10002
"""
    parser = optparse.OptionParser(usage)
    _, addresses = parser.parse_args()
    if len(addresses) < 1:
        parser.error('Provide at least one port.')
        
    def parse_address(port):
        if not port.isdigit():
            parser.error('Ports must be integers.')
        return int(port)

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
    
    def format_address(self, address):
        """format address to a pretty string"""
        host, port = address
        return '%s:%s' % (host or '127.0.0.1', port)

    def doRead(self):
        """read data, callback function"""
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
        else:
            print 'Task %d received %d bytes from %' % (self.task_num, len(bytes), format_address(self.address))
            
        self.poem += bytes
        
    def fileno(self):
        
def connect(address):
    """Connect to the given server and return a non-blocking socket."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('localhost', address))
    sock.setblocking(0)
    return sock
    
def main():
    """entrance of this program"""
    addresses = parse_args()
    sockets = map(connect, addresses)
    poems = get_poetry(sockets)
    for i, sock in enumerate(sockets):
        print 'Task %d: %d bytes of poetry' % (i + 1, len(poems[sock]))
        
if __name__ == '__main__':
    main()
