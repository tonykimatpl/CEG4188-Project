import json
import threading
import queue
import pygame
import websocket  # websocket-client library
import math
import random

BOARD_SIZE = 3
CELL_SIZE = 100  # Pixels per cell
WINDOW_SIZE = (BOARD_SIZE * CELL_SIZE + 40, BOARD_SIZE * CELL_SIZE + 100)  # Extra space for labels
HOLD_TIME_MS = 3000  # 3 seconds
ANIMATION_FPS = 60  # For smooth animation
ANIMATION_STEPS = int(HOLD_TIME_MS / (1000 / ANIMATION_FPS))  # Approx steps for hold time

class GameClient:
    def __init__(self):
        self.ws = None
        self.message_queue = queue.Queue()
        self.player_id = None
        self.symbol = None
        self.game_over = False
        self.board = [[' ' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.hold_start_time = None
        self.hold_row = None
        self.hold_col = None
        self.hold_progress = 0.0
        self.victory_particles = []

        # Colors
        self.colors = {'X': (255, 100, 100), 'O': (100, 100, 255), '△': (100, 255, 100)}  # Vibrant RGB
        self.base_color = (255, 255, 255)  # White
        self.grid_color = (50, 50, 50)  # Dark gray
        self.text_color = (0, 0, 0)  # Black
        self.hover_color = (220, 220, 220)  # Light gray for hover
        self.bg_color = (240, 240, 240)  # Light background

        # Pygame setup
        pygame.init()
        pygame.mixer.init()  # For sounds
        self.screen = pygame.display.set_mode(WINDOW_SIZE, pygame.RESIZABLE)
        pygame.display.set_caption("Deny and Conquer")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 24)
        self.big_font = pygame.font.SysFont("Arial", 36, bold=True)
        self.claim_sound = pygame.mixer.Sound(pygame.mixer.Sound(buffer=b'\x00\x00' * 1000))  # Placeholder; replace with actual sound file if desired

        # Start WebSocket in a thread
        threading.Thread(target=self.start_websocket, daemon=True).start()

        # Main loop
        self.run()

    def start_websocket(self):
        self.ws = websocket.WebSocketApp("ws://localhost:8765",
                                         on_open=self.on_open,
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close)
        self.ws.run_forever()

    def on_open(self, ws):
        pass

    def on_message(self, ws, message):
        self.message_queue.put(message)

    def on_error(self, ws, error):
        self.message_queue.put(json.dumps({"error": str(error)}))

    def on_close(self, ws, close_status_code, close_msg):
        self.message_queue.put(json.dumps({"status": "Connection closed"}))

    def process_messages(self):
        try:
            while not self.message_queue.empty():
                message = self.message_queue.get_nowait()
                data = json.loads(message)

                if 'error' in data:
                    print(f"Error: {data['error']}")
                    pygame.quit()
                    return True  # Signal to quit

                if 'player_id' in data:
                    self.player_id = data['player_id']
                    self.symbol = data['symbol']

                if 'status' in data:
                    if 'board' in data:
                        self.board = data['board']
                        self.reset_hold()  # Reset any ongoing hold
                    if data['status'] == 'game_over':
                        self.game_over = True
                        winner = data.get('winner')
                        print(f"Game Over: Winner {winner}")
                        if winner == self.symbol:
                            self.create_victory_particles()
                    elif data['status'] == 'Game aborted: Player disconnected':
                        self.game_over = True
                        print("Game Aborted: Player disconnected.")
                    elif data['status'] == 'Connection closed':
                        return True  # Quit
        except queue.Empty:
            pass
        return False

    def run(self):
        running = True
        while running:
            if self.process_messages():
                running = False
                continue

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and not self.game_over:
                    self.handle_mouse_down(event)
                elif event.type == pygame.MOUSEBUTTONUP and not self.game_over:
                    self.handle_mouse_up(event)

            # Draw everything
            self.draw()
            pygame.display.flip()
            self.clock.tick(ANIMATION_FPS)

            # Update hold progress if active
            if self.hold_row is not None and self.hold_col is not None:
                elapsed = pygame.time.get_ticks() - self.hold_start_time
                self.hold_progress = min(elapsed / HOLD_TIME_MS, 1.0)
                if self.hold_progress >= 1.0:
                    # Hold complete, but wait for release to claim
                    pass

            # Update particles
            self.update_particles()

        if self.ws:
            self.ws.close()
        pygame.quit()

    def handle_mouse_down(self, event):
        if event.button == 1:  # Left click
            mx, my = event.pos
            row, col = self.get_cell_from_pos(mx, my)
            if row is not None and col is not None and self.board[row][col] == ' ' and self.symbol:
                self.hold_start_time = pygame.time.get_ticks()
                self.hold_row = row
                self.hold_col = col
                self.hold_progress = 0.0

    def handle_mouse_up(self, event):
        if event.button == 1 and self.hold_row is not None and self.hold_col is not None:
            mx, my = event.pos
            row, col = self.get_cell_from_pos(mx, my)
            if (row, col) == (self.hold_row, self.hold_col) and self.hold_progress >= 1.0:
                # Send claim
                self.ws.send(json.dumps({"action": "claim", "row": row, "col": col}))
                self.claim_sound.play()  # Play sound
            self.reset_hold()

    def get_cell_from_pos(self, x, y):
        offset_x, offset_y = 20, 60  # Margins
        row = (y - offset_y) // CELL_SIZE
        col = (x - offset_x) // CELL_SIZE
        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
            return row, col
        return None, None

    def draw(self):
        self.screen.fill(self.bg_color)

        # Player label
        label_text = f"Player {self.player_id or '?'} ({self.symbol or '?'})" if self.player_id else "Connecting..."
        label = self.font.render(label_text, True, self.text_color)
        self.screen.blit(label, (20, 10))

        # Status (e.g., Game Over)
        status_text = "Game Over" if self.game_over else ""
        status = self.font.render(status_text, True, (255, 0, 0))
        self.screen.blit(status, (WINDOW_SIZE[0] // 2 - status.get_width() // 2, 10))

        # Draw board
        offset_x, offset_y = 20, 60
        mx, my = pygame.mouse.get_pos()
        hover_row, hover_col = self.get_cell_from_pos(mx, my)

        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                rect = pygame.Rect(offset_x + j * CELL_SIZE, offset_y + i * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                
                # Base fill
                if self.board[i][j] != ' ':
                    color = self.colors.get(self.board[i][j], self.base_color)
                else:
                    color = self.base_color
                
                # Hover effect
                if not self.game_over and self.board[i][j] == ' ' and (i, j) == (hover_row, hover_col):
                    color = self.hover_color
                
                pygame.draw.rect(self.screen, color, rect, border_radius=10)  # Rounded squares
                
                # Animation if holding
                if (i, j) == (self.hold_row, self.hold_col) and self.hold_progress > 0:
                    target_color = self.colors.get(self.symbol, self.base_color)
                    # Interpolate color
                    r = int(color[0] + self.hold_progress * (target_color[0] - color[0]))
                    g = int(color[1] + self.hold_progress * (target_color[1] - color[1]))
                    b = int(color[2] + self.hold_progress * (target_color[2] - color[2]))
                    anim_color = (r, g, b)
                    
                    # Radial pulse effect
                    center = (rect.centerx, rect.centery)
                    max_radius = math.sqrt((CELL_SIZE/2)**2 + (CELL_SIZE/2)**2)  # Corner to center
                    radius = self.hold_progress * max_radius
                    pygame.draw.circle(self.screen, anim_color, center, radius, width=0)  # Filled circle
                    
                # Draw symbol
                if self.board[i][j] != ' ':
                    symbol_text = self.big_font.render(self.board[i][j], True, self.text_color)
                    text_rect = symbol_text.get_rect(center=rect.center)
                    self.screen.blit(symbol_text, text_rect)

                # Grid lines
                pygame.draw.rect(self.screen, self.grid_color, rect, width=2, border_radius=10)

        # Draw victory particles
        for particle in self.victory_particles:
            pygame.draw.circle(self.screen, particle['color'], (int(particle['x']), int(particle['y'])), particle['size'])

    def reset_hold(self):
        self.hold_start_time = None
        self.hold_row = None
        self.hold_col = None
        self.hold_progress = 0.0

    def create_victory_particles(self):
        self.victory_particles = []
        for _ in range(50):
            self.victory_particles.append({
                'x': random.randint(0, WINDOW_SIZE[0]),
                'y': random.randint(0, WINDOW_SIZE[1]),
                'vx': random.uniform(-2, 2),
                'vy': random.uniform(-5, -1),  # Upward motion
                'color': random.choice(list(self.colors.values())),
                'size': random.randint(3, 7),
                'life': random.randint(100, 200)  # Frames to live
            })

    def update_particles(self):
        for particle in self.victory_particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] += 0.1  # Gravity
            particle['life'] -= 1
            particle['size'] = max(1, particle['size'] - 0.1)
            if particle['life'] <= 0 or particle['y'] > WINDOW_SIZE[1]:
                self.victory_particles.remove(particle)

if __name__ == "__main__":
    GameClient()
