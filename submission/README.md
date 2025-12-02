# Deny and Conquer

A multiplayer Python game inspired by Tic-Tac-Toe, but with a twist: players must *hold* their mouse on a neutral square for 3 seconds to claim it. The first player to complete a full row, column, or diagonal wins. If the board fills without a line win, the player with the most claimed squares takes the victory. Supports 2 or 3 players, with real-time multiplayer over WebSockets.

Built using Python, Pygame for the client UI, and WebSockets for communication between server and clients.

## Features
- **Multiplayer Support**: Play with 1-3 players (2 or 3 recommended for balanced gameplay).
- **Hold-to-Claim Mechanic**: Neutral squares require a 3-second hold to capture—adds strategy and tension!
- **Win Conditions**:
  - Line Win: Complete a row, column, or diagonal with your symbol (X, O, or △).
  - Majority Win: Most claimed squares if the board fills without a line.
- **Visual Effects**: Hover highlights, hold animations, victory particles, and sounds (optional).
- **Game Over Handling**: Ties, player disconnections, and restart voting.
- **Resizable Window**: Adapts to screen size.
- **Sidebar Stats**: Track connected players and scores in real-time.
- **Sounds**: Claim and victory audio (requires `claim.mp3` and `victory.mp3` files in the directory; falls back to silent if missing).

## Requirements
- Python 3.8+ (tested on 3.10+).
- Libraries: `pygame`, `websockets`, `websocket-client`.
- Windows-specific batch files for easy setup and launch (cross-platform manual instructions provided below).
- Optional: Audio files (`claim.mp3` for claiming a square, `victory.mp3` for wins—place in the project root).

No additional hardware required beyond a mouse for holding interactions.

## Setup
### Windows (Recommended: Use Batch Files)
1. Ensure Python is installed and added to your PATH (download from [python.org](https://www.python.org/downloads/)).
2. Double-click `setup.bat` in the project root. This will automatically install the required libraries:
   ```
   pip install pygame websockets
   ```
   - If you encounter permission issues, run as administrator or use `pip install --user`.

### Manual Setup (Any OS)
1. Clone or download the project files.
2. Open a terminal/command prompt in the project root.
3. Install dependencies:
   ```
   pip install pygame websockets
   ```
   - For audio, ensure `claim.mp3` and `victory.mp3` are in the root (free sound effects can be sourced online).

## How to Run
### Windows (Easy Mode: Batch Files)
1. After setup, choose one:
   - Double-click `run2Player.bat` to launch the server and 2 clients (for 2-player game).
   - Double-click `run3Player.bat` to launch the server and 3 clients (for 3-player game).
   
   Each batch file starts the server in one terminal and opens client windows. Players join automatically.

2. **Manual Launch Alternative** (if batch files don't suit):
   - Double-click `startServer.bat` to run the server.
   - In separate terminals/windows, double-click `startClient.bat` (repeat for each player, up to 3).

### Manual Run (Any OS, No Batch Files)
1. **Start the Server** (one instance only):
   ```
   python server.py
   ```
   - The server listens on `ws://localhost:8765`. Keep this terminal open.

2. **Start Clients** (one per player, up to 3):
   ```
   python client.py
   ```
   - Each client connects automatically. Launch additional clients for more players.
   - For 2 players: Run server + 2 clients.
   - For 3 players: Run server + 3 clients.

3. **Play**:
   - Clients will show "Connecting..." then "Waiting for players".
   - Once enough players join, the game starts automatically.
   - If a player disconnects mid-game, the game aborts, and players can vote to restart.

### Closing the Game
- Close client windows to disconnect.
- Stop the server with Ctrl+C in its terminal.
- Restart votes: In a game over screen, click "Vote to Restart" (requires majority to restart).

## Controls
- **Claim a Square**: Hover over a white (neutral) square and hold left mouse button for 3 seconds. Release to claim (if held long enough).
- **Resize**: Drag window edges to resize (board adapts).
- **Restart**: After game over, vote via the button (one vote per player).
- No keyboard needed—pure mouse interaction!

## Game Rules
1. **Board**: 5x5 grid starts empty (white squares).
2. **Symbols**: Players get unique symbols (X, O, △).
3. **Claiming**: Hold on an empty square for 3 seconds. Your symbol appears if successful. Interrupt (move mouse/release early) cancels.
4. **Winning**:
   - **Line Victory**: First to fill an entire row, column, or diagonal (like Tic-Tac-Toe).
   - **Majority**: If board full and no line, most squares wins. Ties possible.
5. **Multiplayer Notes**:
   - 2 players: Standard duel.
   - 3 players: Chaotic fun—block opponents strategically!
   - Late joins: Possible if under max players.
6. **Game Over**:
   - Winner celebrated with particles and "Winner Winner Chicken Dinner!".
   - Ties or aborts show status. Vote to restart.

## Project Structure
- `server.py`: Handles game logic, WebSocket connections, board state, win checks.
- `client.py`: Pygame-based UI for players (the code you see in the main file).
- `setup.bat`: Installs dependencies.
- `run2Player.bat`, `run3Player.bat`: Launches server + clients.
- `startServer.bat`, `startClient.bat`: Manual launch helpers.
- `claim.mp3`, `victory.mp3`: Optional sound files.

## Troubleshooting
- **"No module named 'pygame'"**: Run `setup.bat` or `pip install pygame`.
- **WebSocket Connection Failed**: Ensure server is running first. Check firewall (localhost:8765).
- **No Sound**: Missing MP3 files? The game uses silent fallbacks. Add files to root.
- **Window Too Small**: Resize manually or adjust `CELL_SIZE` in `client.py`.
- **Players Not Joining**: Max 3 players. Restart server if stuck.
- **Errors on Non-Windows**: Batch files are Windows-only. Use manual commands.
- **Performance**: On low-end hardware, reduce `ANIMATION_FPS` in `client.py`.
- **Customization**: Edit colors, board size, or hold time in `client.py` constants.

## Contributing
Feel free to fork and improve! Add features like chat, AI opponents, or cross-platform launchers. Report issues or PRs welcome.

## License
MIT License—use freely, credit appreciated.

---

*Created with ❤️ for strategic showdowns. May the best denier conquer!*
Made by Tony Kim for CEG 4188 Project