import asyncio
from server import Server

#def main(arguments):
def main():

    loop = asyncio.get_event_loop()
    server = Server()
    asyncio.async(server.run_server())

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print('Received interrupt, closing')
        server.close()
    finally:
        loop.stop()
        loop.close()

if __name__ == '__main__':
    #arguments = docopt(__doc__, version='evolver_server 0.1')
    #main(arguments)
    main()
