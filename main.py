import tkinter as tk
import random
from collections import deque

class Minesweeper:
    def __init__(self, root, rows=9, cols=9, num_mines=10):
        self.root = root
        self.rows = rows
        self.cols = cols
        self.num_mines = num_mines
        self.buttons = {}          # Dictionary to store button widgets
        self.mines = set()         # Set to store mine positions
        self.game_over = False     # Flag to indicate game status
        self.create_board()        # Initialize the GUI grid
        self.place_mines()         # Randomly place mines

    def create_board(self):
        # Create a grid of buttons and bind them to reveal_cell()
        for row in range(self.rows):
            for col in range(self.cols):
                button = tk.Button(self.root, width=2, height=1, 
                                   command=lambda r=row, c=col: self.reveal_cell(r, c))
                button.grid(row=row, column=col)
                self.buttons[(row, col)] = button  # Save reference to button

    def place_mines(self):
        # Randomly place mines in the grid
        while len(self.mines) < self.num_mines:
            mine = (random.randint(0, self.rows - 1), random.randint(0, self.cols - 1))
            self.mines.add(mine)

    def reveal_cell(self, row, col):
        # Do nothing if game is over
        if self.game_over:
            return

        # Skip if already revealed
        if self.buttons[(row, col)].cget('state') == "disabled":
            return

        # If clicked on a mine, show it and end the game
        if (row, col) in self.mines:
            self.buttons[(row, col)].config(text="*", bg="red")
            self.game_over = True
            self.show_all_mines()
            self.show_message("You Lose!")
            return

        # Otherwise, reveal the area starting from this cell
        self.flood_fill(row, col)

        # If all non-mine cells are revealed, player wins
        if self.check_win():
            self.game_over = True
            self.show_all_mines()
            self.show_message("You Win!")

    def flood_fill(self, start_row, start_col):
        # Use BFS to reveal empty cells and their neighbors
        queue = deque()
        queue.append((start_row, start_col))

        while queue:
            row, col = queue.popleft()

            # Skip if already revealed
            if self.buttons[(row, col)].cget('state') == "disabled":
                continue

            # Count surrounding mines
            count = self.count_surrounding_mines(row, col)
            self.buttons[(row, col)].config(
                text=str(count) if count > 0 else "", 
                state="disabled", 
                relief="sunken"
            )

            # If no adjacent mines, continue revealing neighbors
            if count == 0:
                for r in range(row - 1, row + 2):
                    for c in range(col - 1, col + 2):
                        if 0 <= r < self.rows and 0 <= c < self.cols:
                            if self.buttons[(r, c)].cget('state') != "disabled":
                                queue.append((r, c))

    def count_surrounding_mines(self, row, col):
        # Count mines in adjacent cells
        surrounding_mines = 0
        for r in range(row - 1, row + 2):
            for c in range(col - 1, col + 2):
                if 0 <= r < self.rows and 0 <= c < self.cols and (r, c) in self.mines:
                    surrounding_mines += 1
        return surrounding_mines

    def show_all_mines(self):
        # Reveal all mine locations (used at game end)
        for mine in self.mines:
            self.buttons[mine].config(text="*", bg="red")

    def check_win(self):
        # Check if all non-mine cells have been revealed
        uncovered_cells = sum(1 for r in range(self.rows) for c in range(self.cols)
                              if self.buttons[(r, c)].cget('state') == "disabled")
        return uncovered_cells == self.rows * self.cols - self.num_mines

    def show_message(self, message):
        # Display game result message in a popup window
        message_box = tk.Toplevel(self.root)
        message_box.title("Game Over")

        label = tk.Label(message_box, text=message, font=("Arial", 14))
        label.pack(padx=20, pady=20)

        button = tk.Button(message_box, text="OK", command=message_box.destroy)
        button.pack(pady=10)

        # Center the message box on screen
        message_box.update_idletasks()
        width = message_box.winfo_width()
        height = message_box.winfo_height()
        screen_width = message_box.winfo_screenwidth()
        screen_height = message_box.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2) - 30
        message_box.geometry(f"+{x}+{y}")

def get_game_settings():
    # Initial window for user to input game configuration
    def start_game_callback():
        try:
            rows = int(entry_rows.get())
            cols = int(entry_cols.get())
            num_mines = int(entry_mines.get())

            # Basic input validation
            if rows <= 0 or cols <= 0 or num_mines <= 0 or num_mines >= rows * cols:
                raise ValueError("Invalid values.")

            # Check screen size constraints
            button_width = 25
            button_height = 30
            screen_width = settings_window.winfo_screenwidth()
            screen_height = settings_window.winfo_screenheight()
            max_cols = screen_width // button_width
            max_rows = screen_height // button_height

            if cols > max_cols or rows > max_rows:
                label_error.config(
                    text=f"Too big. Max size: {max_rows} rows x {max_cols} cols."
                )
                return

            # Start the game if everything is valid
            settings_window.destroy()
            start_game(rows, cols, num_mines)
        except ValueError:
            label_error.config(text=f"Too many mines. Max mines: {rows * cols-1}")

    # Create settings input window
    settings_window = tk.Tk()
    settings_window.title("Game Settings")

    label_rows = tk.Label(settings_window, text="Rows:")
    label_rows.grid(row=0, column=0, padx=10, pady=5)
    entry_rows = tk.Entry(settings_window)
    entry_rows.grid(row=0, column=1, padx=10, pady=5)

    label_cols = tk.Label(settings_window, text="Columns:")
    label_cols.grid(row=1, column=0, padx=10, pady=5)
    entry_cols = tk.Entry(settings_window)
    entry_cols.grid(row=1, column=1, padx=10, pady=5)

    label_mines = tk.Label(settings_window, text="Mines:")
    label_mines.grid(row=2, column=0, padx=10, pady=5)
    entry_mines = tk.Entry(settings_window)
    entry_mines.grid(row=2, column=1, padx=10, pady=5)

    label_error = tk.Label(settings_window, text="", fg="red")
    label_error.grid(row=3, column=0, columnspan=2)

    button_start = tk.Button(settings_window, text="Start Game", command=start_game_callback)
    button_start.grid(row=4, column=0, columnspan=2, pady=10)

    # Center the settings window
    settings_window.update_idletasks()
    width = settings_window.winfo_width()
    height = settings_window.winfo_height()
    screen_width = settings_window.winfo_screenwidth()
    screen_height = settings_window.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2) - 30
    settings_window.geometry(f"+{x}+{y}")

    settings_window.mainloop()

def start_game(rows, cols, num_mines):
    # Main game window setup
    root = tk.Tk()
    root.title("Minesweeper")
    game = Minesweeper(root, rows, cols, num_mines)

    # Center the game window
    root.update_idletasks()
    window_width = root.winfo_width()
    window_height = root.winfo_height()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x_position = (screen_width // 2) - (window_width // 2)
    y_position = (screen_height // 2) - (window_height // 2) - 30
    root.geometry(f"+{x_position}+{y_position}")
    root.mainloop()

# Start the settings dialog to configure the game
get_game_settings()
