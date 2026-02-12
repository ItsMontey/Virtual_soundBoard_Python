Virtual Soundboard Application
A modern, responsive desktop soundboard built with Python. This application allows users to create a personalized dashboard of audio clips, assign global hotkeys, and manage their sound library through an intuitive "dark mode" interface.

🚀 Features
Customizable Sound Tiles: Add, rename, and delete sound tiles dynamically within the app.

Global Hotkeys: Assign specific keyboard keys to trigger sounds instantly.

Responsive Grid Layout: The UI automatically adjusts tile sizes and positions when the window is resized.

Persistent Storage: All sound paths and key bindings are saved to local JSON files, so your setup persists across sessions.

Modern UI/UX: Built with a sleek Black and Gold theme using CustomTkinter.

Real-time Control: Includes a master volume slider and a global "Stop" button for immediate playback control.

🛠️ Technical Stack
Language: Python 3.x

GUI Framework: CustomTkinter (for modern UI components)

Audio Engine: Pygame (specifically the mixer module)

Data Management: JSON (for lightweight configuration storage)

📦 Installation & Setup
Clone the repository:

Bash
git clone https://github.com/yourusername/virtual-soundboard.git
cd virtual-soundboard
Install dependencies:

Bash
pip install customtkinter pygame
Run the application:

Bash
python main.py
🎮 How to Use
Add a Sound: Click the "New" tile to open your file explorer and select an audio file (.mp3, .wav, or .ogg).

Play: Click any tile to play the associated sound.

Manage: Right-click any tile to open a context menu where you can:

Rename the tile.

Edit/Delete key bindings.

Remove the tile entirely.

Volume: Use the slider at the bottom to adjust the output levels.

📁 Project Structure
main.py: The core application logic and UI layout.

sounds.json: Stores the mapping of tile names to file paths.

key_bindings.json: Stores the user-defined hotkeys for each sound.
