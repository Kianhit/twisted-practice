# This is the blocking version of the Slow Poetry Server.
import socket, time, os
import optparse

def parse_args():
    usage = """usage: %prog [options] poetry-file

This is the Slow Poetry Server, blocking edition.
Run it like this:

  python slowpoetry.py <path-to-poetry-file>
"""
    parser = optparse.OptionParser(usage)
    
    help = "The port to listen on. Default to a random available port."
    parser.add_option('-p', '--port', type='int', help=help)
    
    help = "The host to listen on. Default is localhost."
    parser.add_option('-s', '--host', default='localhost', help=help)
    
    help = "number of bytes to send at a time"
    parser.add_option('-n', '--num_bytes', type='int', default=100, help=help)
    
    help = "number of seconds between sending bytes"
    parser.add_option('-d', '--delay', type='float', default=0.7, help=help)
    
    (options, args) = parser.parse_args()
    
    if len(args) != 1:
        parser.error('Provide exactly one poetry file.')

    poetry_file = args[0]

    if not os.path.exists(args[0]):
        parser.error('No such file: %s' % poetry_file)

    return options, poetry_file

def send_poetry(sock, poetry_file, num_bytes, delay):
    """Send some poetry slowly down the socket."""
    inputf = open(poetry_file)
    while True:
        poetry_bytes = inputf.read(num_bytes)
            
        if not poetry_bytes:
            inputf.close()
            sock.close()
            return
        print 'Sending %d bytes' % len(poetry_bytes)
            
        try:
            sock.sendall(poetry_bytes)
        except socket.error:
            inputf.close()
            sock.close()
            return
        
        time.sleep(delay)
        
def serve(listen_socket, poetry_file, num_bytes, delay):
    """serve clients"""
    while True:
        sock, addr = listen_socket.accept()
        print 'Somebody at %s wants poetry!' % (addr,)
        send_poetry(sock, poetry_file, num_bytes, delay)

def main():
    """entrance of this program"""
    options, poetry_file = parse_args()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((options.host, options.port or 0))
    sock.listen(5)
    print 'Serving %s on port %s.' % (poetry_file, sock.getsockname()[1])
    serve(sock, poetry_file, options.num_bytes, options.delay)

if __name__ == '__main__':
    main()
    
