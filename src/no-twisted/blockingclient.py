import socket

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("localhost", 10000))
    poem = ''
    while True:
        data = sock.recv(200)
        if not data:
            sock.close()
            break
        poem += data
    print poem

if __name__ == '__main__':
    main()
