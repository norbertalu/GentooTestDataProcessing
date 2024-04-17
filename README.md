# Application Overview

This application provides tools for both generating G-code and analyzing and plotting test data for performance assessments. Depending on your needs, you can navigate to specific folders within this repository to perform the desired tasks.

## Getting Started

Before running any part of this application, ensure that your Python environment is set up with the necessary libraries installed. You might need libraries like `matplotlib`, `numpy`, or `pandas` for data analysis and plotting, and specific G-code generation libraries if applicable.

## Generating G-code

For users who need to generate G-code:

- **Navigate to the G-code Generate Folder**: This folder contains scripts and utilities specifically designed for G-code creation.

To run the G-code generator, execute the script located in the G-code Generate folder:

```bash
cd Gcode_Generate
python gcode_generator.py
```
This script will prompt you for the necessary inputs and output the G-code to the specified file or directory.

## Analyzing and Plotting Test Data
For users interested in analyzing and plotting test data:

Navigate to the Performance Test Folder: This folder contains scripts and tools for loading, analyzing, and visualizing performance data.
To perform data analysis and generate plots, follow these steps:

```bash
cd Performance_Test
python performance_analysis.py
```
You will be guided through selecting the test data files and setting parameters for the analysis. The script will process the data and generate plots according to the configured settings.

## Issues and Contributions
If you encounter any issues or would like to contribute to the project, please open an issue or a pull request on the project's GitHub repository. Your feedback and contributions are welcome and will help improve the functionality and usability of these tools.
