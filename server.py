import asyncio
import json
import websockets

# Game state
BOARD_SIZE = 5  # Increased to 5x5
board = [[' ' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]  # ' ' means white/neutral
players = {}  # websocket: {'id': int, 'symbol': str}
symbols = ['X', 'O', '△']
game_started = False
winner = None

# One lock per square for fine-grained concurrency control
locks = [[asyncio.Lock() for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

def check_winner(symbol):
    # Check rows, columns, diagonals for BOARD_SIZE in a row (scales to 5 for larger board)
    for i in range(BOARD_SIZE):
        if all(board[i][j] == symbol for j in range(BOARD_SIZE)) or \
           all(board[j][i] == symbol for j in range(BOARD_SIZE)):
            return True
    if all(board[i][i] == symbol for i in range(BOARD_SIZE)) or \
       all(board[i][BOARD_SIZE - 1 - i] == symbol for i in range(BOARD_SIZE)):
        return True
    return False

async def broadcast(message):
    for ws in list(players.keys()):
        try:
            await ws.send(json.dumps(message))
        except:
            pass  # Ignore failed sends

async def handler(websocket):
    global game_started, winner
    player_id = len(players) + 1
    if player_id > 3:
        await websocket.send(json.dumps({"error": "Game full (max 3 players)"}))
        return

    players[websocket] = {'id': player_id, 'symbol': symbols[player_id - 1]}
    await websocket.send(json.dumps({"player_id": player_id, "symbol": symbols[player_id - 1]}))

    if len(players) == 3:
        game_started = True
        await broadcast({"status": "Game started!", "board": board})

    try:
        async for message in websocket:
            if not game_started or winner:
                continue
            data = json.loads(message)
            if data.get('action') != 'claim':
                continue
            row, col = data.get('row'), data.get('col')
            if not (0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE):
                continue

            symbol = players[websocket]['symbol']
            lock = locks[row][col]
            async with lock:  # Lock the specific shared object (square)
                if board[row][col] == ' ':  # Still white/neutral?
                    board[row][col] = symbol
                    await broadcast({"status": "update", "board": board})
                    if check_winner(symbol):
                        winner = symbol
                        await broadcast({"status": "game_over", "winner": symbol})
    finally:
        del players[websocket]
        if game_started and len(players) < 3:
            await broadcast({"status": "Game aborted: Player disconnected"})

async def main():
    async with websockets.serve(handler, "localhost", 8765):
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
