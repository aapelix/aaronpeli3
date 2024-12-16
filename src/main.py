from game import Game
import asyncio

async def main():
    game = Game()
    await game.run()

asyncio.run(main())