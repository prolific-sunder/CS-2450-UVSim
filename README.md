## CS-2450-UVSim

Collaborators: Kylynn Fuhriman, Casey Wolf, Kaleb Fulwider, Lindsey Glod
Creation Date: 09/11/2025

## Description
Collaborative project to create UVSim.
UVSim is a virtual machine designed to interpret BasicML instructions. This implementation provides a graphical interface (GUI) for easier interaction.
-BasicML: Programs are written as signed four-digit decimal numbers (e.g., +1234, -0456).<br>
-Memory: UVSim supports 100 memory locations (00–99).<br>
-CPU & Registers: Tracks the Accumulator and Program Counter in real time.<br>
-GUI Features: Configure color scheme, load files, save files, run programs, reset memory, monitor execution, view memory/register state and edit memory/instructions directly in a Tkinter window.

## Installation
1. Download this repository.
2. Ensure Python 3.8+ is installed.<br>
3. Install dependencies<br>

Dependencies:

pip install pytest

## Instruction for use

-To run the program (main.py), utilize the terminal or command line with the following: python main.py. This will open the tkinter window for use. <br>

### GUI Functionality
Within the GUI window, the user will have access to the following functionalities:
-Load File Button – Select a BasicML program file (.txt) to load into memory.<br>
-Run Program Button – Execute the loaded program line by line.<br>
-Reset Program Button – Restore memory, accumulator, and program counter to their initial state.<br>
-Theme Settings Button – Allows user to configure primary and secondary color scheme, can also reset to UVU default<br>
-Program Use Button - Pops open dialog box that explains how the program functions.<br>
-How to Edit Button - Pops open dialog box that explains how to edit the memory/instructions. IMPORTANT: UVSim works on an internal clipboard and can only copy from within the program. Copying outside sources will not paste into the program.<br>
-User Console - Allows user to type input at the programs request.<br>
-System Messages – A scrolling log showing program status, errors, and input prompts.<br>
-System Variables – Displays the current Accumulator and Program Counter.<br>
-Program Instructions – Shows the currently executing instruction.<br>
-Memory Table - Displays all 100 memory locations (00–99) and their current values. Updates in real time. Allows editing based on click instructions.

### Editing Memory 

- All editing command are performed on the Memory table, all clicks must be within that table to properly function.<br>
- Double-click a memory cell to edit its value.<br>
- Right-click a row for Cut / Copy / Paste / Delete options.<br>
- Invalid entries are highlighted in red and listed in System Messages.<br>
- Selected memory cell is highlighted in white.<br>
- You can load, inspect, and modify memory before running the program.<br>
- Save your file by typing 'CTRL+S'.<br>

### File/Input Requirements
-When loading a file, program expects no more than 4 digits and one potential +/- sign. If more than 4 digits, invalid characters, or duplicate signs are added, an error will be thrown.<br>
EXAMPLES: +1102 | -0009 | 4300 <br>
ERRORS: abcde | 209123 | 0.0 <br>
-When giving User Input, program expects no more than 4 digits and one potential +/- sign. If more than 4 digits, program will treat it as overflow and use the last 4 digits in the integer. Invalid characters or duplicate signs will result in an error being thrown.<br>
EXAMPLES: +1102 | -0009 | 4300 | 918234 (overflowed to 8234) <br>
ERRORS: abc | ++2091 | 0.0 <br>

## Changelog 
09/11/2025 - Initial creation, added README.md basic format and blank main.py.<br>
09/19/2025 - Validated tests for main.py in main-function and merged main-function branch with main branch.<br>
10/1/2025 - Implemented new GUI with tkinter and integrated it with main.py. Added overflow handling functions to main.py.<br>
10/22/2025 - Implemented color theme for GUI and config.json file.<br>
10/23/2025 - Implemented editing, invalid entry flags, warnings, and file saving of memory.<br>
