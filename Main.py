import random
import tkinter as tk

GRID_SIZE = 15   # 15x15 crossword grid
WORD_COUNT = 8   # number of words to place


def load_words(filename="words10k.txt"):
    words = []
    with open(filename, "r") as f:
        for line in f:
            w = line.strip().lower()
            if 3 <= len(w) <= 10 and w.isalpha():
                words.append(w)
    return words


def empty_grid(n):
    return [["#" for _ in range(n)] for _ in range(n)]


def place_first_word(grid, word):
    row = GRID_SIZE // 2
    col_start = (GRID_SIZE - len(word)) // 2
    for i, ch in enumerate(word):
        grid[row][col_start + i] = ch
    return (row, col_start)


def find_overlap_positions(word, placed_words):
    positions = []
    for placed_word, (r, c, direction) in placed_words:
        for i, ch1 in enumerate(placed_word):
            for j, ch2 in enumerate(word):
                if ch1 == ch2:
                    positions.append((placed_word, (r, c, direction), i, j))
    return positions


def try_place_word(grid, word, overlap):
    _, (r, c, direction), i, j = overlap
    if direction == "H":
        new_row = r - j
        new_col = c + i
        if new_row < 0 or new_row + len(word) > GRID_SIZE:
            return False
        for k, ch in enumerate(word):
            if grid[new_row + k][new_col] not in ("#", ch):
                return False
        for k, ch in enumerate(word):
            grid[new_row + k][new_col] = ch
        return (new_row, new_col, "V")

    if direction == "V":
        new_row = r + i
        new_col = c - j
        if new_col < 0 or new_col + len(word) > GRID_SIZE:
            return False
        for k, ch in enumerate(word):
            if grid[new_row][new_col + k] not in ("#", ch):
                return False
        for k, ch in enumerate(word):
            grid[new_row][new_col + k] = ch
        return (new_row, new_col, "H")

    return False


def generate_crossword(words):
    grid = empty_grid(GRID_SIZE)

    first = random.choice(words)
    words.remove(first)

    placed_words = []
    r, c = place_first_word(grid, first)
    placed_words.append((first, (r, c, "H")))

    for w in random.sample(words, WORD_COUNT - 1):
        overlaps = find_overlap_positions(w, placed_words)
        random.shuffle(overlaps)
        placed = False

        for overlap in overlaps:
            res = try_place_word(grid, w, overlap)
            if res:
                placed_words.append((w, res))
                placed = True
                break

    return grid

def validate_one_char(new_value):
    return len(new_value) <= 1

def build_gui(grid):
    root = tk.Tk()
    root.title("Crossword Puzzle")
    root.configure(bg="white")
    frame = tk.Frame(root, bg="white")
    frame.pack(padx=20, pady=20)
    
    vcmd = (root.register(validate_one_char), "%P")

    entries = []

    for r in range(GRID_SIZE):
        row_entries = []
        for c in range(GRID_SIZE):
            if grid[r][c] == "#":
                cell = tk.Label(frame, width=2, height=1, bg="white", borderwidth=0, highlightthickness=0)
                cell.grid(row=r, column=c, padx=1, pady=1)
                row_entries.append(None)
            else:
                var = tk.StringVar()
                cell = tk.Entry(
                frame,
                width=2,
                justify="center",
                textvariable=var,
                font=("Arial", 18),
                bg="white",
                fg="black",
                relief="solid",

                borderwidth=1,   
                highlightthickness=3,
                highlightbackground="white",
                highlightcolor="black", 

                validate="key",
                validatecommand=vcmd
            )

                cell.grid(row=r, column=c, padx=1, pady=1)
                row_entries.append(var)
        entries.append(row_entries)

    root.mainloop()


def main():
    words = load_words("words10k.txt")
    random.shuffle(words)

    grid = generate_crossword(words)
    build_gui(grid)


if __name__ == "__main__":
    main()
