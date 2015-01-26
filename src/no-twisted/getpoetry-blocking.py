#a blocking client to receive poetry
import socket, optparse

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
        
    def parse_address(addr):
        return int(addr)

    return map(parse_address, addresses)

def get_poetry(address):
    """Download poety from the given address."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('localhost', address))
    poem = ''
    while True:
        data = sock.recv(200)
        if not data:
            sock.close()
            break
        poem += data
    return poem

def main():
    """entrance of this program"""
    addresses = parse_args()
    for i, address in enumerate(addresses):
        print 'Task %d begins to receive data from %d' % (i+1, address)
        poem = get_poetry(address)
        print 'Task %d received %d bytes' % (i+1, len(poem))
        
if __name__ == '__main__':
    main()
