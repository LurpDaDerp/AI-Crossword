import random
import tkinter as tk

GRID_SIZE = 15

CELL_SIZE = 60
LETTER_FONT_SIZE = 20   
NUMBER_FONT_SIZE = 12
GRID_PAD = 30     

MIN_PLACED_WORDS = 4


def pick_balanced_words(words, min_total=6, max_total=20):
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

def is_normal_key(event):
    ignore = {
        "Shift_L", "Shift_R", "Control_L", "Control_R",
        "Alt_L", "Alt_R", "Meta_L", "Meta_R",
        "Caps_Lock", "Num_Lock", "Scroll_Lock",
        "Escape", "Tab",
        "Left", "Right", "Up", "Down",
        "Home", "End", "Prior", "Next", 
        "Insert", "Delete",
    }

    if event.keysym.upper().startswith("F") and event.keysym[1:].isdigit():
        return False

    if event.keysym in {"Return", "BackSpace"}:
        return False

    if event.char and event.char.strip() != "":
        return True

    return False


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

def build_gui(grid, placed_words):
    root = tk.Tk()
    root.title("Crossword Puzzle")
    root.configure(bg="white")

    total_width = GRID_SIZE * CELL_SIZE + 400
    total_height = GRID_SIZE * CELL_SIZE + 150
    root.geometry(f"{total_width}x{total_height}")

    main_frame = tk.Frame(root, bg="white")
    main_frame.pack(padx=GRID_PAD, pady=GRID_PAD, fill="both", expand=True)

    grid_frame = tk.Frame(main_frame, bg="white")
    grid_frame.pack(side="left", anchor="n")

    clues_frame = tk.Frame(main_frame, bg="white")
    clues_frame.pack(side="left", anchor="n", padx=40)

    word_infos = []
    cell_to_words = {}  

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
    active_word_idx = None
    highlighted_cells = []

    game_over = False
    overlay = None

    start_cells = set(info["cells"][0] for info in word_infos)
    sorted_starts = sorted(start_cells, key=lambda rc: (rc[0], rc[1]))
    clue_numbers = {rc: i + 1 for i, rc in enumerate(sorted_starts)}

    across_clues = []
    down_clues = []
    for info in word_infos:
        start = info["cells"][0]
        num = clue_numbers[start]
        word = info["word"].upper()
        if info["direction"] == "H":
            across_clues.append((num, word))
        else:
            down_clues.append((num, word))

    across_clues.sort(key=lambda x: x[0])
    down_clues.sort(key=lambda x: x[0])

    def move_focus(row, col, dr, dc):
        """Move focus in direction (dr, dc) to the next non-block cell."""
        nr, nc = row + dr, col + dc
        while 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE:
            target = entries[nr][nc]
            if target is not None:
                target.focus_set()
                return
            nr += dr
            nc += dc

    def is_word_filled(word_idx):
        for (rr, cc) in word_infos[word_idx]["cells"]:
            entry = entries[rr][cc]
            if entry is None:
                return False
            if entry.get().strip() == "":
                return False
        return True

    def clear_highlight():
        for (rr, cc) in highlighted_cells:
            entry = entries[rr][cc]
            if entry is not None:
                entry.config(bg="white")
        highlighted_cells.clear()

    def highlight_word(idx):
        clear_highlight()
        if idx is None:
            return
        for (rr, cc) in word_infos[idx]["cells"]:
            entry = entries[rr][cc]
            if entry is not None:
                entry.config(bg="#e5f0ff")
                highlighted_cells.append((rr, cc))

    def show_completion_overlay():
        nonlocal overlay, game_over
        game_over = True

        overlay = tk.Frame(root, bg="white")
        overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

        label = tk.Label(
            overlay,
            text="Puzzle complete!\nPress any key to play again",
            font=("Arial", 24),
            bg="white",
            fg="black",
            justify="center"
        )
        label.pack(expand=True)

        def on_any_key(event):
            if not is_normal_key(event):
                return 

            root.destroy()
            main()

        overlay.bind("<Key>", on_any_key)
        overlay.focus_set()

    def check_puzzle():
        if game_over:
            return
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
                    return
        root.after(1500, show_completion_overlay)

    def on_cell_click(event, row, col):
        nonlocal active_word_idx
        if game_over:
            return

        candidates = cell_to_words.get((row, col), [])
        if not candidates:
            active_word_idx = None
            clear_highlight()
            return

        starts_here = [i for i in candidates
                       if word_infos[i]["cells"][0] == (row, col)]
        start_unfilled = [i for i in starts_here if not is_word_filled(i)]

        def choose_with_horizontal_preference(indices):
            horiz = [i for i in indices if word_infos[i]["direction"] == "H"]
            return horiz[0] if horiz else indices[0]

        if start_unfilled:
            chosen = choose_with_horizontal_preference(start_unfilled)
        elif starts_here:
            chosen = choose_with_horizontal_preference(starts_here)
        else:
            unfilled = [i for i in candidates if not is_word_filled(i)]
            if unfilled:
                chosen = choose_with_horizontal_preference(unfilled)
            else:
                chosen = choose_with_horizontal_preference(candidates)

        active_word_idx = chosen
        highlight_word(active_word_idx)

    def on_root_click(event):
        nonlocal active_word_idx
        if game_over:
            return
        if isinstance(event.widget, tk.Entry):
            return
        clear_highlight()
        active_word_idx = None
        root.focus_set()

    root.bind("<Button-1>", on_root_click, add="+")

    def on_key(event, row, col):
        nonlocal active_word_idx
        if game_over:
            return "break"

        entry = entries[row][col]
        key = event.keysym
        ch = event.char

        if key == "Up":
            move_focus(row, col, -1, 0)
            return "break"
        if key == "Down":
            move_focus(row, col, 1, 0)
            return "break"
        if key == "Left":
            move_focus(row, col, 0, -1)
            return "break"
        if key == "Right":
            move_focus(row, col, 0, 1)
            return "break"

        if key == "BackSpace":
            entry.delete(0, tk.END)
            return "break"

        if not ch:
            return "break"

        if ch.isalpha():
            upper = ch.upper()
            entry.delete(0, tk.END)
            entry.insert(0, upper)

            if active_word_idx is not None:
                cells = word_infos[active_word_idx]["cells"]
                try:
                    idx = cells.index((row, col))
                except ValueError:
                    idx = -1

                if idx != -1 and idx + 1 < len(cells):
                    nr, nc = cells[idx + 1]
                    next_entry = entries[nr][nc]
                    if next_entry is not None:
                        next_entry.focus_set()
                        next_entry.icursor(1)

            check_puzzle()
            return "break"

        return "break"

    THIN = 1

    def on_focus_in(event):
        event.widget.config(highlightthickness=THIN)

    def on_focus_out(event):
        event.widget.config(highlightthickness=THIN)

    for r in range(GRID_SIZE):
        row_entries = []
        for c in range(GRID_SIZE):
            if grid[r][c] == "#":
                cell = tk.Label(
                    grid_frame,
                    width=2,
                    height=1,
                    bg="white",
                    borderwidth=0,
                    highlightthickness=0
                )
                cell.grid(row=r, column=c, padx=1, pady=1)
                row_entries.append(None)
            else:
                cell_frame = tk.Frame(
                    grid_frame,
                    bg="white",
                    width=CELL_SIZE,
                    height=CELL_SIZE
                )
                cell_frame.grid(row=r, column=c, padx=2, pady=2)
                cell_frame.grid_propagate(False)
                cell_frame.pack_propagate(False)

                var = tk.StringVar()
                entry = tk.Entry(
                    cell_frame,
                    width=2,
                    justify="center",
                    textvariable=var,
                    font=("Arial", LETTER_FONT_SIZE),
                    bg="white",
                    fg="black",
                    relief="solid",
                    borderwidth=1,
                    highlightthickness=THIN,
                    highlightbackground="white",
                    highlightcolor="black",
                )
                entry.pack(fill="both", expand=True)

                if (r, c) in clue_numbers:
                    num = clue_numbers[(r, c)]
                    num_label = tk.Label(
                        cell_frame,
                        text=str(num),
                        font=("Arial", NUMBER_FONT_SIZE),
                        bg="white"
                    )
                    num_label.place(x=1, y=0, anchor="nw")

                entry.bind("<FocusIn>", on_focus_in)
                entry.bind("<FocusOut>", on_focus_out)

                entry.bind("<Button-1>", lambda e, row=r, col=c: on_cell_click(e, row, col))
                entry.bind("<KeyPress>", lambda e, row=r, col=c: on_key(e, row, col))

                row_entries.append(entry)
        entries.append(row_entries)

    title = tk.Label(
        clues_frame,
        text="Clues",
        font=("Arial", 20, "bold"),
        bg="white"
    )
    title.pack(anchor="w")

    across_label = tk.Label(
        clues_frame,
        text="Across",
        font=("Arial", 16, "bold"),
        bg="white"
    )
    across_label.pack(anchor="w", pady=(10, 0))

    for num, word in across_clues:
        lbl = tk.Label(
            clues_frame,
            text=f"{num}. {word}",
            font=("Arial", 12),
            bg="white"
        )
        lbl.pack(anchor="w")

    down_label = tk.Label(
        clues_frame,
        text="Down",
        font=("Arial", 16, "bold"),
        bg="white"
    )
    down_label.pack(anchor="w", pady=(10, 0))

    for num, word in down_clues:
        lbl = tk.Label(
            clues_frame,
            text=f"{num}. {word}",
            font=("Arial", 12),
            bg="white"
        )
        lbl.pack(anchor="w")

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
