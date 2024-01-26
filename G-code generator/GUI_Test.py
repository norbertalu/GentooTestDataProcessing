import pyautogui
import threading
import unittest
import gui_try1  # Replace with your actual GUI script name

class TestGUIScript(unittest.TestCase):

    def test_button_click(self):
        # Start the GUI in a separate thread
        gui_thread = threading.Thread(target=your_gui_script.start_gui, args=())
        gui_thread.daemon = True
        gui_thread.start()

        # Give the GUI time to open
        pyautogui.sleep(2)

        # Simulate GUI interactions
        pyautogui.write('300', interval=0.25)
        pyautogui.press('tab')
        pyautogui.write('420', interval=0.25)
        pyautogui.press('tab')
        pyautogui.write('10', interval=0.25)
        pyautogui.press('tab')
        pyautogui.write('30', interval=0.25)

        # Click the button (coordinates need to be adjusted based on your screen)
        pyautogui.click(x=button_x_coordinate, y=button_y_coordinate)

        # Add assertions to verify the behavior
        # ...

if __name__ == '__main__':
    unittest.main()