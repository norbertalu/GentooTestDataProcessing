# G-code Generator for Motor Control

## Overview

This Python application generates G-code for controlling motors, specifically designed for applications where precise movement and timing are crucial. Users can specify parameters such as feed rate, initial position, hold-up time, hold-down time, and the number of loops. The generated G-code is then saved to a specified file, making it easy to use in CNC machines or other motor control systems.

## Features

- **Generate custom G-code** based on user inputs.
- **Simple graphical user interface** for ease of use.
- **Input validation** to ensure only valid numbers are entered.
- **Error handling** for file operations.
- **Option to specify output file name and path**.

## Requirements

To run this application, you'll need:

- Python 3.x
- `tkinter` library for Python (usually comes with Python installation)

## Setup

1. Ensure Python 3.x is installed on your system.
2. Clone or download this repository to your local machine.
3. No additional installation is required since the application uses `tkinter`, which is included in the standard Python library.

## How to Use

1. **Launch the application** by running the Python script. A window titled "G-code Generator for Motor Control" will open.
2. **Fill in the required fields**:
   - `Feedrate(mm/min)`: The speed at which the motor moves.
   - `Initial Height(mm)`: The starting position of the motor along the X-axis.
   - `Hold Up Time (s)`: The delay time before moving back.
   - `Hold Down Time (s)`: The delay time before moving forward.
   - `Number of Loops`: How many times the above sequence should repeat.
   - `Filename`: The name of the file to save the generated G-code. If not specified, it defaults to "gcode_output.gcode". The `.gcode` extension is added automatically if omitted.
3. **Click the "Browse" button** to select the output path where the G-code file will be saved. This field is read-only and is filled by selecting a directory through the file dialog.
4. **Click "Start"** to generate the G-code. The application validates the inputs and shows an error message if any input is invalid. Otherwise, it will generate the G-code and save it to the specified file, displaying a success message upon completion.

## Troubleshooting

- Ensure all input fields are filled with numeric values where expected.
- The initial height must be at least 45 mm for the G-code to generate correctly.
- If you encounter file-saving issues, check the specified path for permissions and disk space.

## Contributing

We welcome contributions to improve this application. Please feel free to fork the repository, make your changes, and submit a pull request.
