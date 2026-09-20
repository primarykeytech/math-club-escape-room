# Math Club Retro Escape Room (Game Boy 4-Color)

A retro-style math escape room game built in Python using `pygame-ce`. Styled with an authentic 4-color Game Boy DMG palette, CRT scanlines, procedural 8-bit audio effects, and customizable JSON challenge definitions.

## Requirements

- Python 3.10+
- `pygame-ce`
- `pillow`
- `numpy`

## Setup Instructions

### 1. Create a Virtual Environment

It is recommended to run this project inside a Python virtual environment:

**On Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

> *Note:* If PowerShell gives an execution policy error, you can enable local script running for the current terminal with:
> `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned`

**On Windows (Command Prompt):**
```cmd
python -m venv .venv
.\.venv\Scripts\activate.bat
```

**On macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies

Once your virtual environment is activated, install the required packages:

```bash
pip install -r requirements.txt
```

### 3. Run the Game

```bash
python src/main.py
```

## Game Features

- **Game Boy DMG Aesthetics**: Authentic 4-shade greenish palette (`#0f380f`, `#306230`, `#8bac0f`, `#9bbc0f`), CRT scanlines, and beveled corner-notched retro dialogue boxes.
- **Dynamic Puzzles via JSON**: Puzzles, hints, images, time limits, and penalty rules are decoupled in [`data/escape_room.json`](data/escape_room.json) for easy editing.
- **Terminal-Style Prompt**: Real-time freeform keyboard input with blinking pixel cursor.
- **Ticking Timer & Penalties**: Configurable countdown clock with time deductions for wrong attempts.
- **Original 8-Bit Menacing Theme Song**: Authentic chiptune soundtrack in D minor with pulse leads, eerie arpeggios, and stepped triangle bass on title and prologue screens.
- **Procedural 8-Bit Audio Effects**: Real-time square/triangle wave sound synthesis for authentic clicks, error buzzers, fanfare chimes, and solve jingles.
- **Dynamic Closing Screens**: Custom Game Boy graphics and dialogues with The Professor—furious concession and vows of return upon victory, or merciless gloating upon system lockout/timeout.
- **Help System**: Type `hint` to reveal tiered hints per challenge.

## Project Structure

```
math-club-escape-room/
├── assets/
│   ├── images/          # 4-color dithered stage graphics
│   └── screenshots/     # Visual preview captures
├── data/
│   └── escape_room.json # Room configuration and challenge stages
├── src/
│   ├── config.py        # Display, color palette, and timing constants
│   ├── main.py          # State machine, input handler, and game loop
│   ├── palette.py       # Image quantizer and Floyd-Steinberg dithering tool
│   ├── sound.py         # Procedural 8-bit sound synthesizer
│   └── ui.py            # Retro panel drawing, scanlines, and text wrap
├── requirements.txt
└── README.md
```
