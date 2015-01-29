#a none-blocking client to receive poetry
import socket, optparse, errno, select

def parse_args():
    usage = """usage: %prog port1 [port2] [port3]

This is client to get poetry, none blocking edition
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

def get_poetry(sockets):
    """Download poetry from all the given sockets."""
    poems = dict.fromkeys(sockets, '') # socket -> accumulated poem
    sock2task = dict([(s, i + 1) for i, s in enumerate(sockets)])
    while sockets:
        rlist, _, _ = select.select(sockets, [], [])
        # rlist is the list of sockets with data ready to read
        for sock in rlist:
            poem = ''
            task_num = sock2task[sock]
            address_format = format_address(sock.getpeername())
            while True:
                try:
                    data = sock.recv(1024)
                except socket.error, e:
                    if e.args[0] == errno.EWOULDBLOCK:
                        # this error code means we would have
                        # blocked if the socket was blocking.
                        # instead we skip to the next socket
                        break
                    raise
                else:
                    if not data:
                        break
                    else:
                        poem += data
            if not poem:
                sockets.remove(sock)
                sock.close()
                print 'Task %d finished' % task_num
            else:
                print 'Task %d got %d bytes from %s' % (task_num, len(poem), address_format)
            poems[sock] += poem
    return poems

def format_address(address):
    """format address to a pretty string"""
    host, port = address
    return '%s:%s' % (host or '127.0.0.1', port)
    
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
