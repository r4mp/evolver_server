import asyncio
import msgpack
from collections import namedtuple

Client = namedtuple('Client', 'reader writer')

class Server:

    """
    took the structure from
    https://github.com/Mionar/aiosimplechat
    it was MIT licenced
    """

    clients = {}
    server = None

    def __init__(self, host='*', port=8001):
        self.host = host
        self.port = port
        self.clients = {}

    @asyncio.coroutine
    def run_server(self):
        try:
            self.server = yield from asyncio.start_server(
                self.client_connected, 
                self.host, self.port
            )
            print('Running server on {}:{}'.format(self.host, self.port))
        except OSError:
            print('Cannot bind to this port! Is the server already running?')
            self.loop.stop()

    def send_to_client(self, peername, msg):
        client = self.clients[peername]
        client.writer.write(msgpack.packb(msg))
        return

    def send_to_all_clients(self, msg):
        for peername in self.clients.keys():
            self.send_to_client(peername, msg)
        return

    def close_clients(self):
        for peername, client in self.clients.items():
            client.writer.write_eof()

    @asyncio.coroutine    
    def client_connected(self, reader, writer):
        peername = writer.transport.get_extra_info('peername')
        print("Client connected - {}".format(peername))
        new_client = Client(reader, writer)
        self.clients[peername] = new_client
        self.send_to_client(peername, 'Welcome {}'.format(peername))
        unpacker = msgpack.Unpacker(encoding='utf-8')
        while not reader.at_eof():
            try:
                pack = yield from reader.read(1024)
                unpacker.feed(pack)
                for msg in unpacker:
                    new_client.handle_msg(msg)
            except ConnectionResetError as e:
                print('ERROR: {}'.format(e))
                new_client.bye()
                del self.clients[peername]
                return
            except Exception as e:
                error = 'ERROR: {}'.format(e)
                print(error)
                self.send_to_client(peername, error)
                new_client.writer.write_eof()
                new_client.bye()
                del self.clients[peername]
                return        

    def close(self):
        self.send_to_all_clients("bye\n")
        self.close_clients()
