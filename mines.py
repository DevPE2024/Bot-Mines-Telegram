import random

def generate_mines_positions(rows, cols, mines_count):
    positions = [(row, col) for row in range(rows) for col in range(cols)]
    mines_positions = random.sample(positions, mines_count)
    return mines_positions

def get_safe_positions(rows, cols, mines_positions):
    positions = [(row, col) for row in range(rows) for col in range(cols)]
    safe_positions = [pos for pos in positions if pos not in mines_positions]
    return safe_positions

def get_mines_data():
    rows = 5
    cols = 5
    mines_count = 3

    mines_positions = generate_mines_positions(rows, cols, mines_count)
    safe_positions = get_safe_positions(rows, cols, mines_positions)

    signals = {
        'mines_positions': mines_positions,
        'safe_positions': safe_positions
    }

    return signals
