import pyautogui
import keyboard
import time
from PIL import ImageGrab
import subprocess
import sys

try:
    import numpy as np
except:
    NumpyDownload = input("[+] Numpy is not installed! Do you want this program to install these libraries for you [y/N]").lower()
    if NumpyDownload == "y":
        command = ["pip", "install", "numpy"]
        result = subprocess.run(command, capture_output=True, text=True)
        print("Standard Output:\n", result.stdout)
        print("Standard Error:\n", result.stderr)
        print("Return Code:", result.returncode)
    elif NumpyDownload == "n":
        print("Please install the correct libraries yourself. You can see those in the GitHub repo.")
        sys.exit()
    else:
       print("[-] No valid input was given, aborting.") 
       sys.exit()

try:
    import cv2 
except:
    NumpyDownload = input("[+] cv2 is not installed! Do you want this program to install these libraries for you [y/N]").lower()
    if NumpyDownload == "y":
        command = ["pip", "install", "opencv-python"]
        result = subprocess.run(command, capture_output=True, text=True)
        print("Standard Output:\n", result.stdout)
        print("Standard Error:\n", result.stderr)
        print("Return Code:", result.returncode)
    elif NumpyDownload == "n":
        print("Please install the correct libraries yourself. You can see those in the GitHub repo.")
        sys.exit()
    else:
       print("[-] No valid input was given, aborting.") 
       sys.exit()

try:
    import customtkinter as ctk
except:
    NumpyDownload = input("[+] Customtkinter is not installed! Do you want this program to install these libraries for you [y/N]").lower()
    if NumpyDownload == "y":
        command = ["pip", "install", "customtkinter"]
        result = subprocess.run(command, capture_output=True, text=True)
        print("Standard Output:\n", result.stdout)
        print("Standard Error:\n", result.stderr)
        print("Return Code:", result.returncode)
    elif NumpyDownload == "n":
        print("Please install the correct libraries yourself. You can see those in the GitHub repo.")
        sys.exit()
    else:
       print("[-] No valid input was given, aborting.") 
       sys.exit()

# Settings


print("[*] Creating CTk window")

app = ctk.CTk()
app.title("ERLCRFIDGUI.py")

app.geometry("500x500")
app.maxsize(500, 500)



def Activation():
    global monitoring
    monitoring = False
    initial_image = None
    recent_colors = []

    def get_mouse_area_color():
        x, y = pyautogui.position()
        left = max(0, x - area_size)
        top = max(0, y - area_size)
        right = min(pyautogui.size().width, x + area_size)
        bottom = min(pyautogui.size().height, y + area_size)
        bbox = (left, top, right, bottom)
        screenshot = ImageGrab.grab(bbox)
        return screenshot

    def is_color_similar(color1, color2, tolerance):
        return all(abs(a - b) <= tolerance for a, b in zip(color1, color2))

    def detect_color_change(initial_image, current_image, tolerance):
        initial_pixels = list(initial_image.getdata())
        current_pixels = list(current_image.getdata())
        color_changes = sum(
            1 for i in range(len(initial_pixels))
            if not is_color_similar(current_pixels[i], initial_pixels[i], tolerance)
        )
        total_pixels = len(initial_pixels)
        return (color_changes / total_pixels) * 100  # Return percentage of pixels that changed

    def detect_target_color(image, target_color, tolerance):
        pixels = list(image.getdata())
        for pixel in pixels:
            if is_color_similar(pixel[:3], target_color, tolerance):
                return True
        return False

    def update_recent_colors(image):
        nonlocal recent_colors
        new_colors = list(image.getdata())
        recent_colors.append(new_colors)
        if len(recent_colors) > change_buffer:
            recent_colors.pop(0)

    def significant_color_change():
        if len(recent_colors) < 2:
            return False

        previous_colors = recent_colors[-2]
        current_colors = recent_colors[-1]

        color_changes = sum(
            1 for i in range(len(previous_colors))
            if not is_color_similar(current_colors[i], previous_colors[i], tolerance)
        )
        total_pixels = len(previous_colors)
        return (color_changes / total_pixels) * 100 > 10  # Example threshold

    def toggle_monitoring(event):
        global monitoring
        monitoring = not monitoring
        print(f"Monitoring: {'On' if monitoring else 'Off'}")

    # Register the toggle key
    keyboard.on_press_key(toggle_key, toggle_monitoring)

    print("Press 't' to toggle monitoring on and off.")

    try:
        while True:
            if monitoring:
                if initial_image is None:
                    initial_image = get_mouse_area_color()
                
                current_image = get_mouse_area_color()
                
                # Update the recent colors buffer
                update_recent_colors(current_image)
                
                # Check for significant color change or target color similarity
                if significant_color_change() or detect_target_color(current_image, target_color, tolerance):
                    pyautogui.click()
                    print("Significant color change or similar target color detected. Click performed.")
                    monitoring = False  # Stop monitoring after the click
                    initial_image = None  # Reset the initial image
                    recent_colors = []  # Clear the color buffer
                
                # Display the monitored area in a window
                img_array = np.array(current_image)
                img_resized = cv2.resize(img_array, (300, 300), interpolation=cv2.INTER_NEAREST)
                cv2.imshow("Monitored Area", cv2.cvtColor(img_resized, cv2.COLOR_RGB2BGR))
                
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
            time.sleep(interval)

    except KeyboardInterrupt:
        print("Script terminated.")
    finally:
        cv2.destroyAllWindows()

MyFont= ctk.CTkFont(size=20)
ButtonFont = ctk.CTkFont(size=15)

lableI = ctk.CTkLabel(app, text="press this button to activate the script", font=MyFont)
lableI.grid(pady = 10)

activationButton = ctk.CTkButton(app,
                                 text="Activate", 
                                 command=Activation,
                                 width=250, 
                                 font=ButtonFont)
activationButton.grid(row=2, column=0)

def area_size_value(value):
    print(value)

lableII = ctk.CTkLabel(app, text="The areasize to be Monitored:",font=MyFont)
lableII.grid(pady = 10, column=0)

area_size = ctk.CTkSlider(app, 
                          from_=1, 
                          to=20, 
                          command=area_size_value, 
                          number_of_steps=19,
                          height= 20
                          )  # Size of the area around the mouse to monitor (in pixels)
area_size.grid(pady = 10)
area_size.set(3)


toggle_key = 't'  # Key to toggle the monitoring on and off

interval = 0.000001  # Time interval for checking the pixel area (in seconds)
target_color = (211, 211, 211)  # The RGB color to detect (example: medium grey)

def tolerance_value(value):
    print("Tolerance is set to: ", value)

lableIII = ctk.CTkLabel(app, 
                        text="The tolerance of the colorsimularity", font=MyFont)
lableIII.grid(pady = 10)

tolerance = ctk.CTkSlider(app, 
                          from_=1, 
                          to= 100, 
                          command=tolerance_value, 
                          number_of_steps=99,
                          height= 20)  # Tolerance for color similarity
tolerance.grid(pady = 10)
tolerance.set(50)


def change_buffer_value(value):
    print("The change Buffer is set to: ", value)

lableIV = ctk.CTkLabel(app, text="The number of frames to buffer", font=MyFont)
lableIV.grid(pady = 10)

change_buffer = ctk.CTkSlider(app, 
                              from_=50, 
                              to=200, 
                              command=change_buffer_value, 
                              number_of_steps=149,
                              height= 20)  # Number of frames to buffer for detecting significant color change
change_buffer.grid(pady = 10)
change_buffer.set(100)

WarningLable = ctk.CTkLabel(app,text="Once the script is acctivated you will have to  \n resart the script to change these settings", font=MyFont)
WarningLable.grid(pady = 10)



app.mainloop()
