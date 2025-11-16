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

    # ----- Build word metadata: word_infos + cell_to_words -----
    # word_infos[i] = {"word": str, "direction": "H"/"V", "cells": [(r,c), ...]}
    word_infos = []
    cell_to_words = {}  # (r,c) -> list of word indices that include this cell

    for w, (r, c, direction) in placed_words:
        cells = []
        if direction == "H":
            for i, ch in enumerate(w):
                cells.append((r, c + i))
        else:  # "V"
            for i, ch in enumerate(w):
                cells.append((r + i, c))

        idx = len(word_infos)
        word_infos.append({
            "word": w,
            "direction": direction,
            "cells": cells
        })

        for coord in cells:
            cell_to_words.setdefault(coord, []).append(idx)

    entries = []
    active_word_idx = None  # index into word_infos, or None

    # helper: is a given word fully filled in UI?
    def is_word_filled(word_idx):
        for (rr, cc) in word_infos[word_idx]["cells"]:
            entry = entries[rr][cc]
            if entry is None:
                return False
            if entry.get().strip() == "":
                return False
        return True

    # ----- POPUP MESSAGE -----
    def show_message(msg):
        popup = tk.Toplevel(root)
        popup.title("Check Result")
        tk.Label(popup, text=msg, font=("Arial", 16)).pack(padx=20, pady=20)
        tk.Button(popup, text="OK", command=popup.destroy).pack(pady=10)

    # ----- CHECK PUZZLE (only reacts on success) -----
    def check_puzzle():
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                correct = grid[r][c]
                if correct == "#":
                    continue
                entry = entries[r][c]
                if entry is None:
                    return
                text = entry.get().strip().upper()
                if text != correct.upper():
                    return  # not complete yet or wrong
        show_message("🎉 Crossword complete!")

    # ----- CLICK HANDLER: choose active word -----
    def on_cell_click(event, row, col):
        nonlocal active_word_idx
        candidates = cell_to_words.get((row, col), [])
        if not candidates:
            active_word_idx = None
            return

        # 1) words that START at this cell
        starts_here = [i for i in candidates
                       if word_infos[i]["cells"][0] == (row, col)]

        # among starts_here, prefer unfilled
        start_unfilled = [i for i in starts_here if not is_word_filled(i)]

        def choose_with_horizontal_preference(indices):
            # prefer horizontal, else first
            horiz = [i for i in indices if word_infos[i]["direction"] == "H"]
            return horiz[0] if horiz else indices[0]

        if start_unfilled:
            chosen = choose_with_horizontal_preference(start_unfilled)
        elif starts_here:
            chosen = choose_with_horizontal_preference(starts_here)
        else:
            # 2) No word starts here -> fall back to old logic
            unfilled = [i for i in candidates if not is_word_filled(i)]
            if unfilled:
                chosen = choose_with_horizontal_preference(unfilled)
            else:
                chosen = choose_with_horizontal_preference(candidates)

        active_word_idx = chosen

    # ----- KEY HANDLER: uppercase + auto-advance -----
    def on_key_release(event, row, col):
        nonlocal active_word_idx

        entry = entries[row][col]
        text = entry.get()

        # enforce uppercase, but rely on validate_one_char for length
        if text:
            ch = text[0].upper()
            entry.delete(0, tk.END)
            entry.insert(0, ch)
        else:
            return  # nothing typed, don't advance

        # ignore navigation / control keys for auto-advance
        if event.keysym in (
            "BackSpace", "Left", "Right", "Up", "Down",
            "Tab", "Shift_L", "Shift_R", "Control_L", "Control_R"
        ):
            return

        ch = entry.get()
        if not ch.isalpha():
            return  # don't advance on non-letters

        # If we don't have an active word, nothing to advance in
        if active_word_idx is None:
            return

        cells = word_infos[active_word_idx]["cells"]
        try:
            idx = cells.index((row, col))
        except ValueError:
            return

        # Move to next cell in the active word, if any
        if idx + 1 < len(cells):
            nr, nc = cells[idx + 1]
            next_entry = entries[nr][nc]
            if next_entry is not None:
                next_entry.focus_set()
                next_entry.icursor(1)

        # Optional: auto-check after each letter
        check_puzzle()

    # ----- BUILD THE GRID UI -----
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

                # click selects active word (with new start-priority logic)
                cell.bind("<Button-1>", lambda e, row=r, col=c: on_cell_click(e, row, col))
                # typing -> uppercase + auto-advance + auto-check
                cell.bind("<KeyRelease>", lambda e, row=r, col=c: on_key_release(e, row, col))

                row_entries.append(cell)
        entries.append(row_entries)

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
