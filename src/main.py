from game import Game
from network import Network
import asyncio


async def main():
    network = Network()

    if not network.connect():
        print("Could not connect to server!")
        return

    game = Game(network=network)
    await game.run()


asyncio.run(main())