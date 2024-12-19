import pygame
import numpy as np
import random
import time
import math
import pyttsx3
import threading

# Initialize pygame
pygame.init()

# Initialize text-to-speech engine
engine = pyttsx3.init()
tts_thread = None

# Constants
BOARD_SIZE = 14
CELL_SIZE = 40
GRID_LINE_WIDTH = 2
BORDER_WIDTH = 4
MARGIN_TOP = 10
MARGIN_LEFT = 10
MARGIN_RIGHT = 10
MARGIN_BOTTOM = 10

GRID_WIDTH = BOARD_SIZE * CELL_SIZE
GRID_HEIGHT = BOARD_SIZE * CELL_SIZE
SIDE_PANEL_WIDTH = 320  # Increased width to prevent text cutoff
SCREEN_WIDTH = GRID_WIDTH + MARGIN_LEFT + MARGIN_RIGHT + SIDE_PANEL_WIDTH
SCREEN_HEIGHT = GRID_HEIGHT + MARGIN_TOP + MARGIN_BOTTOM + 160

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_BLUE = (0, 102, 204)  # Player's color
PURPLE = (128, 0, 128)  # AI's color
BUTTON_COLOR = (30, 144, 255)  # Button color
BUTTON_HOVER_COLOR = (65, 105, 225)  # Button hover effect
TEXT_COLOR = WHITE
GRID_TEXT_COLOR = BLACK
BG_COLOR = (245, 245, 245)  # Light grey background
TURN_TEXT_COLOR = (255, 69, 0)  # Orange color for "Your Turn"
AI_TEXT_COLOR = (0, 128, 0)  # Green color for "AI Thinking..."
HINT_COLOR = (0, 255, 0)  # Green color for hints
ALERT_COLOR = (255, 0, 0)  # Red color for alerts
GENERAL_TIP_COLOR = (0, 128, 128)  # Teal color for general tips

# Difficulty levels
EASY = 1
MEDIUM = 2
HARD = 3

# Players
PLAYER = 1
AI = 2

# Initialize the game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("5 in a Row (Gomoku)")

# Game board
board = np.zeros((BOARD_SIZE, BOARD_SIZE))

# Directions for 5-in-a-row checking
directions = [(1, 0), (0, 1), (1, 1), (1, -1)]

# Scoring system for AI evaluation
SCORES = {
    'FIVE': 1000000,
    'OPEN_FOUR': 10000,
    'BLOCKED_FOUR': 1000,
    'OPEN_THREE': 1000,
    'BLOCKED_THREE': 100,
    'OPEN_TWO': 100,
    'BLOCKED_TWO': 10,
}


def draw_board():
    """Draws the game board with grid lines and border."""
    screen.fill(BG_COLOR)
    # Draw border
    grid_rect = pygame.Rect(MARGIN_LEFT, MARGIN_TOP, GRID_WIDTH, GRID_HEIGHT)
    pygame.draw.rect(screen, BLACK, grid_rect, BORDER_WIDTH)

    # Draw grid lines
    for x in range(BOARD_SIZE + 1):
        pygame.draw.line(
            screen, BLACK,
            (MARGIN_LEFT + x * CELL_SIZE, MARGIN_TOP),
            (MARGIN_LEFT + x * CELL_SIZE, MARGIN_TOP + GRID_HEIGHT),
            GRID_LINE_WIDTH
        )
    for y in range(BOARD_SIZE + 1):
        pygame.draw.line(
            screen, BLACK,
            (MARGIN_LEFT, MARGIN_TOP + y * CELL_SIZE),
            (MARGIN_LEFT + GRID_WIDTH, MARGIN_TOP + y * CELL_SIZE),
            GRID_LINE_WIDTH
        )


def draw_dots():
    """Draws the already placed dots on the game board."""
    for x in range(BOARD_SIZE):
        for y in range(BOARD_SIZE):
            if board[x, y] == PLAYER:
                pygame.draw.circle(
                    screen, DARK_BLUE,
                    (MARGIN_LEFT + x * CELL_SIZE + CELL_SIZE // 2,
                     MARGIN_TOP + y * CELL_SIZE + CELL_SIZE // 2),
                    CELL_SIZE // 2 - 5
                )
            elif board[x, y] == AI:
                pygame.draw.circle(
                    screen, PURPLE,
                    (MARGIN_LEFT + x * CELL_SIZE + CELL_SIZE // 2,
                     MARGIN_TOP + y * CELL_SIZE + CELL_SIZE // 2),
                    CELL_SIZE // 2 - 5
                )


def update_display(hover_pos=None, selected_level=None, turn_message=None, winner=None,
                   hint_positions=None, suggestions=None):
    """Updates the display, drawing the grid, placed dots, and relevant messages."""
    draw_board()  # Draw the grid

    # Draw the placed dots
    draw_dots()

    # Draw hints if available
    if hint_positions:
        for x, y in hint_positions:
            pygame.draw.rect(
                screen, HINT_COLOR,
                (MARGIN_LEFT + x * CELL_SIZE, MARGIN_TOP + y * CELL_SIZE, CELL_SIZE, CELL_SIZE),
                3
            )

    # Improved hover effect: Semi-transparent circle
    if hover_pos and is_valid_move(*hover_pos):
        x, y = hover_pos
        # Create a semi-transparent surface
        hover_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        hover_color = (*DARK_BLUE, 150)  # Player's color with transparency
        pygame.draw.circle(hover_surface, hover_color, (CELL_SIZE // 2, CELL_SIZE // 2), CELL_SIZE // 2 - 5)
        screen.blit(hover_surface, (MARGIN_LEFT + x * CELL_SIZE, MARGIN_TOP + y * CELL_SIZE))

    # Show the selected difficulty, game name, and instructions
    font = pygame.font.Font(None, 22)
    title_font = pygame.font.Font(None, 40)
    if selected_level is not None:
        difficulty_text = f"5 in a Row | Difficulty: {['Easy', 'Medium', 'Hard'][selected_level - 1]}"
        difficulty_surface = title_font.render(difficulty_text, True, (0, 100, 200))
        screen.blit(difficulty_surface, (10, GRID_HEIGHT + MARGIN_TOP + 10))

    # Instructions
    instructions = [
        "How to Play:",
        "Connect 5 dots in a row horizontally, vertically, or diagonally to win!",
        "Click on an empty cell to place your dot.",
        "Hints are provided to help you!"
    ]

    for i, line in enumerate(instructions):
        instruction_surface = font.render(line, True, GRID_TEXT_COLOR)
        screen.blit(instruction_surface, (10, GRID_HEIGHT + MARGIN_TOP + 50 + i * 20))

    # Show whose turn it is
    if turn_message:
        turn_font = pygame.font.Font(None, 28)
        turn_surface = turn_font.render(turn_message, True,
                                        TURN_TEXT_COLOR if "Your Turn" in turn_message else AI_TEXT_COLOR)
        screen.blit(turn_surface, (MARGIN_LEFT + GRID_WIDTH - turn_surface.get_width(),
                                   GRID_HEIGHT + MARGIN_TOP + 10))

    # Draw the side panel with suggestions
    draw_side_panel(suggestions)

    pygame.display.update()


def draw_side_panel(suggestions):
    """Draws the side panel and displays suggestions."""
    # Define the area for the side panel
    panel_x = MARGIN_LEFT + GRID_WIDTH + 10
    panel_y = MARGIN_TOP
    panel_width = SIDE_PANEL_WIDTH - 20  # 10 pixels padding on both sides
    panel_height = GRID_HEIGHT

    # Draw the side panel background
    panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
    pygame.draw.rect(screen, WHITE, panel_rect)
    pygame.draw.rect(screen, BLACK, panel_rect, 2)

    # Render suggestions
    if suggestions:
        font = pygame.font.Font(None, 20)
        line_spacing = 5
        padding_top = 10
        padding_left = 10
        y = panel_y + padding_top
        for line in suggestions:
            # Check if line is an alert
            if line.startswith("Alert:"):
                suggestion_surface = font.render(line, True, ALERT_COLOR)
            else:
                suggestion_surface = font.render(line, True, GENERAL_TIP_COLOR)
            # Adjust text wrapping if necessary
            words = line.split(' ')
            line_buffer = ''
            for word in words:
                test_line = line_buffer + word + ' '
                test_surface = font.render(test_line, True, GRID_TEXT_COLOR)
                if test_surface.get_width() > panel_width - padding_left * 2:
                    suggestion_surface = font.render(line_buffer.strip(), True, ALERT_COLOR if line.startswith("Alert:") else GENERAL_TIP_COLOR)
                    screen.blit(suggestion_surface, (panel_x + padding_left, y))
                    y += suggestion_surface.get_height() + line_spacing
                    line_buffer = word + ' '
                else:
                    line_buffer = test_line
            if line_buffer:
                suggestion_surface = font.render(line_buffer.strip(), True, ALERT_COLOR if line.startswith("Alert:") else GENERAL_TIP_COLOR)
                screen.blit(suggestion_surface, (panel_x + padding_left, y))
                y += suggestion_surface.get_height() + line_spacing


def is_valid_move(x, y):
    return 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE and board[x, y] == 0


def make_move(x, y, player):
    board[x, y] = player


def check_win(player):
    for x in range(BOARD_SIZE):
        for y in range(BOARD_SIZE):
            if board[x, y] == player:
                for d in directions:
                    if check_direction(x, y, d[0], d[1], player):
                        return True
    return False


def check_direction(x, y, dx, dy, player):
    count = 0
    for i in range(5):
        nx = x + i * dx
        ny = y + i * dy
        if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE and board[nx, ny] == player:
            count += 1
        else:
            break
    return count == 5


def random_ai_move():
    """Select a random valid move for the AI."""
    empty_cells = np.argwhere(board == 0)
    if len(empty_cells) == 0:
        return None
    return tuple(empty_cells[np.random.randint(0, len(empty_cells))])


def block_player_threats(threat_level):
    """Check for player's potential threats and block them based on the threat level."""
    best_move = None
    best_score = -float('inf')
    for x, y in get_all_possible_moves():
        if is_valid_move(x, y):
            make_move(x, y, PLAYER)
            threat = evaluate_board(PLAYER)
            board[x, y] = 0
            if threat >= threat_level and threat > best_score:
                best_score = threat
                best_move = (x, y)
    return best_move


def create_ai_opportunities(opportunity_level):
    """Try to create potential winning opportunities for AI."""
    best_move = None
    best_score = -float('inf')
    for x, y in get_all_possible_moves():
        if is_valid_move(x, y):
            make_move(x, y, AI)
            score = evaluate_board(AI)
            board[x, y] = 0
            if score >= opportunity_level and score > best_score:
                best_score = score
                best_move = (x, y)
    return best_move


def get_all_possible_moves():
    """Returns a set of possible moves adjacent to existing stones for efficiency."""
    possible_moves = set()
    for x in range(BOARD_SIZE):
        for y in range(BOARD_SIZE):
            if board[x, y] != 0:
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        nx = x + dx
                        ny = y + dy
                        if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE and board[nx, ny] == 0:
                            possible_moves.add((nx, ny))
    if not possible_moves:
        center = BOARD_SIZE // 2
        return [(center, center)]
    return possible_moves


def get_ai_move(level):
    if level == EASY:
        # Easy level: Simplified AI
        # First, try to win
        for x, y in get_all_possible_moves():
            if is_valid_move(x, y):
                make_move(x, y, AI)
                if check_win(AI):
                    board[x, y] = 0
                    return (x, y)
                board[x, y] = 0
        # Block player's winning move
        for x, y in get_all_possible_moves():
            if is_valid_move(x, y):
                make_move(x, y, PLAYER)
                if check_win(PLAYER):
                    board[x, y] = 0
                    return (x, y)
                board[x, y] = 0
        # Else, make a random move
        return random_ai_move()
    elif level == MEDIUM:
        # Medium level: AI is more strategic
        # First, try to win
        for x, y in get_all_possible_moves():
            if is_valid_move(x, y):
                make_move(x, y, AI)
                if check_win(AI):
                    board[x, y] = 0
                    return (x, y)
                board[x, y] = 0
        # Block player's winning move
        for x, y in get_all_possible_moves():
            if is_valid_move(x, y):
                make_move(x, y, PLAYER)
                if check_win(PLAYER):
                    board[x, y] = 0
                    return (x, y)
                board[x, y] = 0
        # Then, block player's threats and create AI opportunities
        move = block_player_threats(SCORES['OPEN_THREE'])
        if move:
            return move
        move = create_ai_opportunities(SCORES['OPEN_THREE'])
        if move:
            return move
        # Else, make a random move
        return random_ai_move()
    elif level == HARD:
        # Hard level: AI uses Minimax algorithm with deeper search depth
        depth = 3  # Increase depth to make AI more challenging
        best_score = -float('inf')
        best_move = None

        # Start the timer to prevent the AI from exceeding time limit
        start_time = time.time()
        time_limit = 5.0  # AI has up to 5 seconds to make a move

        for move in get_all_possible_moves():
            make_move(move[0], move[1], AI)
            score = minimax(depth - 1, -float('inf'), float('inf'), False, AI, start_time, time_limit)
            board[move[0], move[1]] = 0  # Undo move

            if score > best_score:
                best_score = score
                best_move = move

        if best_move is None:
            return random_ai_move()
        else:
            return best_move


def minimax(depth, alpha, beta, maximizingPlayer, player, start_time, time_limit):
    opponent = PLAYER if player == AI else AI

    # Check for timeout to prevent AI from exceeding time limit
    if time.time() - start_time > time_limit:
        return evaluate_board(player)

    if depth == 0 or check_win(player) or check_win(opponent):
        return evaluate_board(player)

    if maximizingPlayer:
        maxEval = -float('inf')
        for move in get_all_possible_moves():
            make_move(move[0], move[1], player)
            eval = minimax(depth - 1, alpha, beta, False, player, start_time, time_limit)
            board[move[0], move[1]] = 0  # Undo move
            maxEval = max(maxEval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return maxEval
    else:
        minEval = float('inf')
        for move in get_all_possible_moves():
            make_move(move[0], move[1], opponent)
            eval = minimax(depth - 1, alpha, beta, True, player, start_time, time_limit)
            board[move[0], move[1]] = 0  # Undo move
            minEval = min(minEval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return minEval


def evaluate_board(player):
    """Evaluates the board and returns a score from the perspective of the given player."""
    opponent = PLAYER if player == AI else AI
    total_score = 0

    for x in range(BOARD_SIZE):
        for y in range(BOARD_SIZE):
            if board[x, y] == player:
                total_score += evaluate_position(x, y, player)
            elif board[x, y] == opponent:
                total_score -= evaluate_position(x, y, opponent)

    return total_score


def evaluate_position(x, y, player):
    """Evaluates the position for the given player."""
    score = 0
    for dx, dy in directions:
        score += evaluate_line(x, y, dx, dy, player)
    return score


def evaluate_line(x, y, dx, dy, player):
    """Evaluates a line starting from (x, y) in direction (dx, dy) for the given player."""
    count = 1  # Starts with 1 because (x, y) is occupied by player
    block = 0
    empty = 0

    # Forward direction
    i = 1
    while True:
        nx = x + dx * i
        ny = y + dy * i
        if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE:
            if board[nx, ny] == player:
                count += 1
            elif board[nx, ny] == 0:
                empty += 1
                break
            else:
                block += 1
                break
        else:
            block += 1
            break
        i += 1

    # Backward direction
    i = 1
    while True:
        nx = x - dx * i
        ny = y - dy * i
        if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE:
            if board[nx, ny] == player:
                count += 1
            elif board[nx, ny] == 0:
                empty += 1
                break
            else:
                block += 1
                break
        else:
            block += 1
            break
        i += 1

    return calculate_score(count, block, empty)


def calculate_score(count, block, empty):
    if block == 2 and count < 5:
        return 0
    if count >= 5:
        return SCORES['FIVE']
    if block == 0:
        if count == 4:
            return SCORES['OPEN_FOUR']
        elif count == 3:
            return SCORES['OPEN_THREE']
        elif count == 2:
            return SCORES['OPEN_TWO']
    elif block == 1:
        if count == 4:
            return SCORES['BLOCKED_FOUR']
        elif count == 3:
            return SCORES['BLOCKED_THREE']
        elif count == 2:
            return SCORES['BLOCKED_TWO']
    return 0


def get_potential_moves(player, score_type):
    """Finds potential moves that achieve at least the specified score type."""
    potential_moves = []
    score_threshold = SCORES[score_type]

    for x, y in get_all_possible_moves():
        if is_valid_move(x, y):
            make_move(x, y, player)
            score = evaluate_position(x, y, player)
            board[x, y] = 0  # Undo move
            if score >= score_threshold:
                potential_moves.append((x, y))
    return potential_moves


def get_hint_positions(ai_level):
    """Provides hint positions for the player on all levels."""
    hints = []

    # First, check if the player can win in the next move
    player_win_moves = get_winning_moves(PLAYER)
    if player_win_moves:
        hints.extend(player_win_moves)
        return hints

    # Next, check if the AI can win in the next move and suggest blocking
    ai_win_moves = get_winning_moves(AI)
    if ai_win_moves:
        hints.extend(ai_win_moves)
        return hints

    # Try to find player moves that create OPEN_FOUR
    player_open_four_moves = get_potential_moves(PLAYER, 'OPEN_FOUR')
    if player_open_four_moves:
        hints.extend(player_open_four_moves)
        return hints

    # Try to find AI moves that create OPEN_FOUR and suggest blocking
    ai_open_four_moves = get_potential_moves(AI, 'OPEN_FOUR')
    if ai_open_four_moves:
        hints.extend(ai_open_four_moves)
        return hints

    # Try to find player moves that create OPEN_THREE
    player_open_three_moves = get_potential_moves(PLAYER, 'OPEN_THREE')
    if player_open_three_moves:
        hints.extend(player_open_three_moves)
        return hints

    # Else, no hints to show
    return hints


def get_winning_moves(player):
    """Finds all winning moves for the given player."""
    winning_moves = []
    for x, y in get_all_possible_moves():
        if is_valid_move(x, y):
            make_move(x, y, player)
            if check_win(player):
                winning_moves.append((x, y))
            board[x, y] = 0
    return winning_moves


def get_dynamic_suggestions(player_turn):
    """
    Generates specific and general tips based on the current game state.
    """
    suggestions = []

    if player_turn == PLAYER:
        # Check if the player can win in the next move
        player_win_moves = get_winning_moves(PLAYER)
        if player_win_moves:
            suggestions.append("You can win in the next move! Look for the winning spot.")
            return suggestions

        # Check if the AI can win in the next move
        ai_win_moves = get_winning_moves(AI)
        if ai_win_moves:
            suggestions.append("Alert: Block the AI from winning in the next move!")
            return suggestions

        # Check if the player can create an open four
        player_open_four_moves = get_potential_moves(PLAYER, 'OPEN_FOUR')
        if player_open_four_moves:
            suggestions.append("You can create a strong line! Try to build an open four.")
            return suggestions

        # Check if the AI can create an open four
        ai_open_four_moves = get_potential_moves(AI, 'OPEN_FOUR')
        if ai_open_four_moves:
            suggestions.append("Alert: Prevent the AI from creating a strong line.")
            return suggestions

        # Check if the player can create an open three
        player_open_three_moves = get_potential_moves(PLAYER, 'OPEN_THREE')
        if player_open_three_moves:
            suggestions.append("Consider building up your line to threaten the AI.")

        # General tip
        suggestions.append("Think strategically to outmaneuver the AI.")
    else:
        # AI's turn: Display static message
        suggestions.append("AI is thinking...")

    return suggestions


def speak_suggestions(suggestions_text):
    global tts_thread
    def run():
        engine.say(suggestions_text)
        engine.runAndWait()
    # Stop any ongoing speech before starting new speech
    engine.stop()
    tts_thread = threading.Thread(target=run)
    tts_thread.start()


def main_game(ai_level):
    global board
    board = np.zeros((BOARD_SIZE, BOARD_SIZE))
    player_turn = AI  # Set AI to go first
    game_over = False
    hover_pos = None
    winner = None

    # Initial suggestions
    suggestions = get_dynamic_suggestions(player_turn)

    # Initialize last spoken suggestions
    last_spoken_suggestions = ''

    # Draw the initial board and place any existing dots
    update_display(selected_level=ai_level, turn_message="AI Thinking...", suggestions=suggestions)

    suggestions_need_update = True  # Ensure suggestions are spoken at the start

    while not game_over:
        need_update = False  # Track if a screen update is needed
        hint_positions = None

        # AI's turn first
        if player_turn == AI and not game_over:
            update_display(selected_level=ai_level, turn_message="AI Thinking...", winner=winner, suggestions=suggestions)
            pygame.display.update()

            pygame.time.wait(1000)  # Simulate AI thinking delay
            ai_move = get_ai_move(ai_level)
            if ai_move is None:
                winner = "Draw"
                game_over = True
                break
            make_move(ai_move[0], ai_move[1], AI)
            if check_win(AI):
                winner = "AI"
                game_over = True
                pygame.time.wait(1000)  # Pause to let the player see the AI's winning move
                break
            player_turn = PLAYER  # After AI's turn, switch to player
            need_update = True  # Update after AI makes a move
            suggestions_need_update = True  # Update suggestions after AI's turn

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False

            if event.type == pygame.MOUSEMOTION:
                mx, my = pygame.mouse.get_pos()
                if MARGIN_LEFT <= mx < MARGIN_LEFT + GRID_WIDTH and MARGIN_TOP <= my < MARGIN_TOP + GRID_HEIGHT:
                    x = (mx - MARGIN_LEFT) // CELL_SIZE
                    y = (my - MARGIN_TOP) // CELL_SIZE  # Corrected calculation
                    hover_pos = (x, y)
                    need_update = True  # Update when the mouse moves
                else:
                    hover_pos = None
                    need_update = True

            if event.type == pygame.MOUSEBUTTONDOWN and player_turn == PLAYER:
                if hover_pos:
                    x, y = hover_pos
                    if is_valid_move(x, y):
                        make_move(x, y, PLAYER)
                        if check_win(PLAYER):
                            winner = "Player"
                            game_over = True
                        player_turn = AI  # After player's turn, switch to AI
                        need_update = True  # Update after player makes a move
                        suggestions_need_update = True  # Update suggestions after player's move

                        # Stop TTS when player's turn ends
                        engine.stop()

        # Provide hints and alerts on all levels
        if player_turn == PLAYER:
            hint_positions = get_hint_positions(ai_level)

        # Update suggestions only when necessary
        if suggestions_need_update and player_turn == PLAYER:
            suggestions = get_dynamic_suggestions(player_turn)
            suggestions_need_update = False  # Reset the flag

            # Combine suggestions into a single string
            suggestions_text = ' '.join(suggestions)

            if suggestions_text != last_spoken_suggestions:
                speak_suggestions(suggestions_text)
                last_spoken_suggestions = suggestions_text

        # Only update the display if needed
        if need_update or hint_positions:
            update_display(hover_pos, selected_level=ai_level, turn_message="Your Turn", winner=winner,
                           hint_positions=hint_positions, suggestions=suggestions)

        if game_over:
            break

    # Stop TTS when game is over
    engine.stop()

    # Display end screen
    play_again = display_end_screen(winner)
    return play_again


def display_end_screen(winner):
    """Displays the end screen with enhanced graphics based on the winner."""
    clock = pygame.time.Clock()
    particles = []

    if winner == "Player":
        # Fireworks animation parameters
        fireworks = []
        for _ in range(5):  # Number of fireworks
            x = random.randint(100, SCREEN_WIDTH - 100)
            y = random.randint(100, GRID_HEIGHT // 2)
            color = (random.randint(150, 255), random.randint(100, 255), random.randint(100, 255))
            fireworks.append({'x': x, 'y': y, 'particles': [], 'color': color})

        message_line1 = "Congratulations!"
        message_line2 = "You Win!"
        background_color = (20, 20, 20)  # Dark background for fireworks

        # Announce the win audibly
        engine.say("Congratulations! You Win!")
        engine.runAndWait()

    elif winner == "AI":
        background_color = BLACK  # Plain black background
        message_line1 = "You Lose!"
        message_line2 = "Don't Give Up!"
        fireworks = []  # No fireworks animation

        # Announce the loss audibly
        engine.say("You Lose! Don't Give Up!")
        engine.runAndWait()

    else:
        background_color = BLACK  # Plain black background for a draw
        message_line1 = "It's a Draw!"
        message_line2 = ""  # No second line for a draw
        fireworks = []  # No fireworks animation

        # Announce the draw audibly
        engine.say("It's a Draw!")
        engine.runAndWait()

    # Prepare text surfaces
    font_large = pygame.font.Font(None, 80)
    font_small = pygame.font.Font(None, 60)  # Smaller font for the second line
    text_surface1 = font_large.render(message_line1, True, WHITE)
    text_surface2 = font_small.render(message_line2, True, WHITE)
    shadow_surface1 = font_large.render(message_line1, True, BLACK)
    shadow_surface2 = font_small.render(message_line2, True, BLACK)
    shadow_offset = 5

    # Add "Play Again" and "Exit" buttons
    button_font = pygame.font.Font(None, 50)
    if winner == "AI":
        play_again_text = "Try Again"  # Changed text when the player loses
    else:
        play_again_text = "Play Again"
    exit_text = "Exit"

    play_again_surface = button_font.render(play_again_text, True, WHITE)
    exit_surface = button_font.render(exit_text, True, WHITE)

    play_again_rect = play_again_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
    exit_rect = exit_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 170))

    running = True
    while running:
        screen.fill(background_color)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False  # Exit the game
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if play_again_rect.collidepoint((mx, my)):
                    return True  # Restart the game
                elif exit_rect.collidepoint((mx, my)):
                    return False  # Exit the game

        # Display the message with shadow effect for both lines
        screen.blit(shadow_surface1, (SCREEN_WIDTH // 2 - shadow_surface1.get_width() // 2 + shadow_offset,
                                      SCREEN_HEIGHT // 2 - shadow_surface1.get_height() // 2 - 40 + shadow_offset))
        screen.blit(text_surface1, (SCREEN_WIDTH // 2 - text_surface1.get_width() // 2,
                                    SCREEN_HEIGHT // 2 - text_surface1.get_height() // 2 - 40))

        if message_line2:
            screen.blit(shadow_surface2, (SCREEN_WIDTH // 2 - shadow_surface2.get_width() // 2 + shadow_offset,
                                          SCREEN_HEIGHT // 2 - shadow_surface2.get_height() // 2 + 20 + shadow_offset))
            screen.blit(text_surface2, (SCREEN_WIDTH // 2 - text_surface2.get_width() // 2,
                                        SCREEN_HEIGHT // 2 - text_surface2.get_height() // 2 + 20))

        # Draw the buttons
        pygame.draw.rect(screen, BUTTON_COLOR, play_again_rect.inflate(20, 10))
        screen.blit(play_again_surface, play_again_rect)
        pygame.draw.rect(screen, BUTTON_COLOR, exit_rect.inflate(20, 10))
        screen.blit(exit_surface, exit_rect)

        if winner == "Player":
            # Fireworks animation
            for fw in fireworks:
                if len(fw['particles']) == 0:
                    for _ in range(100):
                        angle = random.uniform(0, math.pi * 2)
                        speed = random.uniform(2, 5)
                        dx = math.cos(angle) * speed
                        dy = math.sin(angle) * speed
                        fw['particles'].append({'x': fw['x'], 'y': fw['y'], 'dx': dx, 'dy': dy,
                                                'life': random.randint(20, 40)})

                for p in fw['particles'][:]:
                    p['x'] += p['dx']
                    p['y'] += p['dy']
                    p['dy'] += 0.1  # Gravity effect
                    p['life'] -= 1
                    if p['life'] <= 0:
                        fw['particles'].remove(p)
                    else:
                        pygame.draw.circle(screen, fw['color'], (int(p['x']), int(p['y'])), 2)

            fireworks = [fw for fw in fireworks if fw['particles']]
            if len(fireworks) < 5:
                x = random.randint(100, SCREEN_WIDTH - 100)
                y = random.randint(100, SCREEN_HEIGHT // 2)
                color = (random.randint(150, 255), random.randint(100, 255), random.randint(100, 255))
                fireworks.append({'x': x, 'y': y, 'particles': [], 'color': color})

        pygame.display.update()
        clock.tick(60)  # 60 FPS


def draw_text(text, font, color, surface, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect(center=(SCREEN_WIDTH // 2, y))
    surface.blit(textobj, textrect)


def start_menu():
    # Fonts
    title_font = pygame.font.Font(None, 64)
    subtitle_font = pygame.font.Font(None, 48)

    # Texts
    welcome_text = 'Welcome to 5 in a Row'
    select_diff_text = 'Select Difficulty'

    # Calculate the height of all the elements
    spacing = 30
    title_height = title_font.size(welcome_text)[1]
    subtitle_height = subtitle_font.size(select_diff_text)[1]
    button_height = 50
    total_height = title_height + subtitle_height + button_height * 3 + spacing * 5

    # Starting Y position to center content vertically
    start_y = SCREEN_HEIGHT // 2 - total_height // 2

    while True:
        screen.fill(BLACK)  # Black background

        mx, my = pygame.mouse.get_pos()

        # Positions
        current_y = start_y
        draw_text(welcome_text, title_font, TEXT_COLOR, screen, current_y)
        current_y += title_height + spacing

        draw_text(select_diff_text, subtitle_font, TEXT_COLOR, screen, current_y)
        current_y += subtitle_height + spacing

        button_easy = pygame.Rect(SCREEN_WIDTH // 2 - 100, current_y, 200, button_height)
        current_y += button_height + spacing

        button_medium = pygame.Rect(SCREEN_WIDTH // 2 - 100, current_y, 200, button_height)
        current_y += button_height + spacing

        button_hard = pygame.Rect(SCREEN_WIDTH // 2 - 100, current_y, 200, button_height)
        current_y += button_height + spacing

        # Draw buttons and center the text within the buttons
        if button_easy.collidepoint((mx, my)):
            pygame.draw.rect(screen, BUTTON_HOVER_COLOR, button_easy)
        else:
            pygame.draw.rect(screen, BUTTON_COLOR, button_easy)

        if button_medium.collidepoint((mx, my)):
            pygame.draw.rect(screen, BUTTON_HOVER_COLOR, button_medium)
        else:
            pygame.draw.rect(screen, BUTTON_COLOR, button_medium)

        if button_hard.collidepoint((mx, my)):
            pygame.draw.rect(screen, BUTTON_HOVER_COLOR, button_hard)
        else:
            pygame.draw.rect(screen, BUTTON_COLOR, button_hard)

        # Center text within the buttons
        button_font = pygame.font.Font(None, 48)
        draw_text('Easy', button_font, WHITE, screen, button_easy.centery)
        draw_text('Medium', button_font, WHITE, screen, button_medium.centery)
        draw_text('Hard', button_font, WHITE, screen, button_hard.centery)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if button_easy.collidepoint((mx, my)):
                        return EASY
                    if button_medium.collidepoint((mx, my)):
                        return MEDIUM
                    if button_hard.collidepoint((mx, my)):
                        return HARD

        pygame.display.update()


if __name__ == "__main__":
    # Main game loop to allow replaying the game
    while True:
        ai_level = start_menu()
        if ai_level is None:
            break
        play_again = main_game(ai_level)
        if not play_again:
            break
    pygame.quit()
    engine.stop()  # Stop the TTS engine when the game exits
