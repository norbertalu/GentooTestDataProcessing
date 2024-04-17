This GUI application is designed to facilitate the analysis and visualization of performance data for different HVAC prototypes. It leverages several libraries such as Tkinter for the GUI, Pandas for data manipulation, Matplotlib for plotting, and Psychrolib for psychrometric calculations.

Features
Data Input Handling: Users can select input datasheets, control log input files, and specify output folders through a user-friendly interface.
Prototype Configuration: Supports multiple prototype configurations which can be easily selected and used for calculations.
Performance Metrics Calculation: Calculates a variety of performance metrics including power, cooling capacity, EER, COP, and more.
Data Visualization: Generates multiple plots based on selected data intervals, illustrating various performance aspects over time.
Persistent Settings: Remembers the last used paths for datasheets, control logs, and output folders to streamline repeated use.
Installation
To run this application, you need Python installed on your system along with the following packages:

tkinter
pandas
numpy
matplotlib
psychrolib
Pillow
You can install these with the following pip command:

bash
Copy code
pip install pandas numpy matplotlib psychrolib Pillow
Ensure psychrolib is initialized correctly as per your regional settings for units (SI or IP).

Usage
Run the application by executing the script in a Python environment:

bash
Copy code
python path_to_script.py
Select Input Files: Use the "Browse" buttons to select the datasheet and control log input files.
Select Output Folder: Specify where the output files (Excel and plots) should be saved.
Choose Prototype: Select the prototype configuration from the dropdown menu.
Calculate: Click "Calculate" to process the data and generate output files and plots based on the provided input.
View Plots: Select specific plots to generate and view them directly within the application.
Configuring Prototypes
Prototypes are configured within the script. To add or modify prototypes, adjust the prototypes dictionary in the script.

Customization
The script can be modified to add new types of plots, metrics, or to change the data processing logic to suit different experimental setups or data formats.

Issues and Contributions
For issues, suggestions, or contributions, please open an issue or pull request on the project's GitHub repository.

