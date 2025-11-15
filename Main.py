import random
import tkinter as tk

GRID_SIZE = 15
MIN_PLACED_WORDS = 4


def pick_balanced_words(words, min_total=5, max_total=8):
    short = [w for w in words if 3 <= len(w) <= 4]
    medium = [w for w in words if 5 <= len(w) <= 6]
    long = [w for w in words if 7 <= len(w) <= 10]

    random.shuffle(short)
    random.shuffle(medium)
    random.shuffle(long)

    total_target = random.randint(min_total, max_total)

    want_short = random.randint(0, 1)
    want_medium = random.randint(3, 4)
    want_long = max(1, total_target - want_short - want_medium)

    chosen = []
    chosen += short[:min(want_short, len(short))]
    chosen += medium[:min(want_medium, len(medium))]
    chosen += long[:min(want_long, len(long))]

    while len(chosen) < total_target:
        for bucket in [medium, long, short]:
            if bucket:
                chosen.append(bucket.pop())
                break

    random.shuffle(chosen)
    return chosen



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
    """
    Try to place 'word' on 'grid' based on an overlap location.
    Enforces that words only touch at intersection cells (no side-adjacency).
    Returns new (row, col, direction) if successful, False otherwise.
    """
    _, (r, c, direction), i, j = overlap

    if direction == "H":
        new_row = r - j
        new_col = c + i

        if new_row < 0 or new_row + len(word) > GRID_SIZE:
            return False

        for k, ch in enumerate(word):
            rr = new_row + k
            cc = new_col
            cell = grid[rr][cc]

            if cell not in ("#", ch):
                return False

            if cell == "#":
                if cc - 1 >= 0 and grid[rr][cc - 1] != "#":
                    return False
                if cc + 1 < GRID_SIZE and grid[rr][cc + 1] != "#":
                    return False

        above = new_row - 1
        below = new_row + len(word)
        if above >= 0 and grid[above][new_col] != "#":
            return False
        if below < GRID_SIZE and grid[below][new_col] != "#":
            return False

        for k, ch in enumerate(word):
            rr = new_row + k
            cc = new_col
            grid[rr][cc] = ch

        return (new_row, new_col, "V")

    if direction == "V":
        new_row = r + i
        new_col = c - j

        if new_col < 0 or new_col + len(word) > GRID_SIZE:
            return False

        for k, ch in enumerate(word):
            rr = new_row
            cc = new_col + k
            cell = grid[rr][cc]

            if cell not in ("#", ch):
                return False

            if cell == "#":
                if rr - 1 >= 0 and grid[rr - 1][cc] != "#":
                    return False
                if rr + 1 < GRID_SIZE and grid[rr + 1][cc] != "#":
                    return False

        left = new_col - 1
        right = new_col + len(word)
        if left >= 0 and grid[new_row][left] != "#":
            return False
        if right < GRID_SIZE and grid[new_row][right] != "#":
            return False

        for k, ch in enumerate(word):
            rr = new_row
            cc = new_col + k
            grid[rr][cc] = ch

        return (new_row, new_col, "H")

    return False




def generate_crossword(words):
    words = words[:]  
    if not words:
        return empty_grid(GRID_SIZE), []

    grid = empty_grid(GRID_SIZE)

    first = random.choice(words)
    words.remove(first)

    placed_words = []
    r, c = place_first_word(grid, first)
    placed_words.append((first, (r, c, "H")))

    random.shuffle(words)

    for w in words:
        overlaps = find_overlap_positions(w, placed_words)
        random.shuffle(overlaps)
        for overlap in overlaps:
            res = try_place_word(grid, w, overlap)
            if res:
                placed_words.append((w, res))
                break

    return grid, placed_words



def validate_one_char(new_value):
    return len(new_value) <= 1


def build_gui(grid, placed_words):
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
                cell = tk.Label(
                    frame,
                    width=2,
                    height=1,
                    bg="white",
                    borderwidth=0,
                    highlightthickness=0
                )
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
                cell.bind("<KeyRelease>", lambda event: check_puzzle())
                row_entries.append(cell)  
        entries.append(row_entries)

    def show_message(msg):
        popup = tk.Toplevel(root)
        popup.title("Check Result")
        tk.Label(popup, text=msg, font=("Arial", 16)).pack(padx=20, pady=20)
        tk.Button(popup, text="OK", command=popup.destroy).pack(pady=10)

    def check_puzzle():
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                correct = grid[r][c]
                if correct == "#":
                    continue
                entry = entries[r][c]
                if entry is None:
                    return  
                text = entry.get().strip().lower()
                if text != correct.lower():
                    return
        show_message("🎉 Crossword complete!")

    root.mainloop()


def main():
    words = load_words("words10k.txt")

    for attempt in range(20):
        chosen_words = pick_balanced_words(words)
        grid, placed_words = generate_crossword(chosen_words)

        if len(placed_words) >= min(MIN_PLACED_WORDS, len(chosen_words)):
            break

    print("\nWords used in crossword:")
    for w, pos in placed_words:
        print("-", w)

    build_gui(grid, placed_words)


if __name__ == "__main__":
    main()
