# Gomoku-Game (5-in-a-Row)

This project is a Python implementation of the **Gomoku Game (5-in-a-Row)** using `pygame`. 
It features an interactive graphical user interface, AI opponent with adjustable difficulty levels, and text-to-speech functionality for providing game hints and suggestions.

## How to Play
The objective is to connect 5 dots in a row (horizontally, vertically, or diagonally).
- Player Turn: Click on an empty cell to place your dot.
- AI Turn: The AI will make its move after some thinking time.
- Winning Condition: The first to get 5 dots in a row wins.

<img width="677" alt="{F9CF5AE5-B8A7-422A-9661-F539A6B54E92}" src="https://github.com/user-attachments/assets/a952d353-fbe9-4609-8949-0f22ee0c2f52" />

## Features

- **Interactive Gameplay**: Play against the computer on a 14x14 grid.
- **Adjustable Difficulty Levels**:
  - **Easy**: Basic AI with random moves and minimal strategy.
  - **Medium**: Strategic AI with scoring-based decisions.
  - **Hard**: Advanced AI using the Minimax algorithm with alpha-beta pruning.
 <img width="404" alt="{F2E65105-0AD8-462E-8955-0D14190E12C2}" src="https://github.com/user-attachments/assets/f6236828-31a7-4492-b8a0-e8349bb07852" />

- **Hints and Suggestions**: Provides dynamic tips and alerts to help the player.
- **Text-to-Speech**: Hints and game suggestions are spoken audibly using TTS.
- **Fireworks Animation**: Celebratory effects on winning.
<img width="624" alt="{07D18721-3509-4E93-B8B7-ECB766D5DE81}" src="https://github.com/user-attachments/assets/c880e855-3d4d-4157-a1a8-889cbc3bd368" />

## Installation
### Prerequisites
- Python 3.x
- Required Python libraries:
  - `pygame`
  - `numpy`
  - `pyttsx3`
