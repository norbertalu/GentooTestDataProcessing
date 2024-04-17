# Swirl Pattern G-code Generator for CNC Machines

## Overview

This project consists of a Python application designed to generate G-code for CNC machines, specifically tailored for creating swirl patterns. It includes two main components:

- `gcode.py`: Contains the core logic for G-code generation.
- `GUI_Run_Me.py`: A graphical user interface (GUI) built with Tkinter, allowing users to input parameters and generate G-code files interactively.

## Requirements

- Python 3.x
- Tkinter (usually comes pre-installed with Python)
- Optional: PyAutoGUI for automated GUI testing (not required for standard usage)

## Installation

1. Ensure Python 3.x is installed on your system.
2. Clone or download this repository to your local machine.
3. Navigate to the project directory.

## Running the Application

To run the application, execute the `GUI_Run_Me.py` script:

```bash
python GUI_Run_Me.py
```
This will open the GUI, where you can input parameters for the G-code generation.

## Using the GUI
- Width (mm): Enter the width of the workspace in millimeters.
- Height (mm): Enter the height of the workspace in millimeters.
- Number of paths: Enter the number of paths for the swirl pattern.
- Initial Height (mm): Enter the initial height from the bottom in millimeters.
- Select Output Path: Click this button to choose the directory where the G-code file will be saved.
- Filename: Enter a name for the G-code file. If left blank, a default name will be used.
- Generate G-code: Click this button to generate the G-code file with the specified parameters. A success message will confirm the file creation.

## G-Code Logic
The core logic for G-code generation is housed in gcode.py. This module includes functions to calculate the swirl pattern based on the given parameters and ensures that the generated paths are within the specified workspace limits.
