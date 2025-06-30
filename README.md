# Mickey-Keeps-Live

**Mickey-Keeps-Live** is a lightweight Windows utility that simulates minimal mouse movement (“mickeys”) to prevent the system from entering idle states such as screen sleep. It leverages the native **SendInput** API to generate genuine input events without dragging your cursor off-screen.

## Features

- **Configurable Duration**  
  Specify how many minutes the tool should run before terminating automatically.
- **Adjustable Interval**  
  Define the pause (in seconds) between each simulated movement, with a hard minimum of 5 seconds.
- **Custom “Mickeys”**  
  Control the size of each movement in pixel units to suit different display resolutions and sensitivity settings.
- **Minimal Overhead**  
  Runs a tight loop with timed sleeps, ensuring very low CPU usage and preserving battery life.
- **Clean GUI**  
  Provides a simple Qt-based interface (via PySide6) for non-technical users, or can be invoked from the command line in headless mode.

## Installation

1. **Prerequisites**  
   - Windows 10 or later  
   - Python 3.7+  
   - [PySide6](https://pypi.org/project/PySide6/)  
     ```bat
     pip install PySide6
     ```
2. **Download**  
   Clone or download the repository, then build a self-contained executable:
   ```bat
   pip install pyinstaller
   pyinstaller --onefile --windowed Mickey-Keeps-Live.py
