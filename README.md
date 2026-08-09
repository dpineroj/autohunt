# AutoHunt

A Boggle-style word-search solver for GamePigeon's Word Hunt, built with a
custom GUI in `cmu_graphics`. Type in the 4×4 letter grid you're given, and
AutoHunt finds every valid word on the board using a trie-backed
backtracking search, then animates each word's path so you can read it off
and play it.

## How it works

**Word list → trie.** A filtered Scrabble word list ([source][wordlist]) is
loaded and built into a prefix tree (`TreeNode`), so the search can
short-circuit the instant a partial path stops matching any valid word
prefix — no need to check full words against the list one at a time.

**Board → all valid words.** From every cell, an 8-directional depth-first
backtracking search (`backtrack`) walks the grid, following the trie one
letter at a time and tracking visited cells to avoid reusing a tile within
a single word. Whenever a path lands on a complete word, it's recorded
along with its exact path of grid coordinates.

**Deduplication and grouping.** Word-search boards often contain a long
word and several of its prefixes as separate valid words on the same path
(e.g., CAT → CATS). Rather than listing all of them as unrelated entries,
`backtrack` walks each newly found word's prefixes back through the trie
and consolidates same-path words into groups, sorted longest-to-shortest.

**Visualization.** The `game` screen accepts the board via direct keyboard
input, then steps through every found word, animating a line across the
grid tile-by-tile along its path — built entirely on `cmu_graphics` primitives,
with a custom `Button` class, dynamically resizing layout, and a live demo
grid with word-cycling arrows on the start screen.

## Files

| File | Purpose |
|---|---|
| `AutoHunt.py` | Full app: trie, search, GUI, animation |
| `words.txt` | Filtered word list used to build the trie |
| `wooden-tile.png`, `pattern-tiled-1920x1080.jpg` | UI assets |

## Run it

```
pip install cmu-graphics pillow
python3 AutoHunt.py
```

[wordlist]: https://boardgames.stackexchange.com/questions/38366/latest-collins-scrabble-words-list-in-text-file
