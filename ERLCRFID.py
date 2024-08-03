import pyautogui
import keyboard
import time
from PIL import ImageGrab, Image
import numpy as np
import cv2

# Settings
area_size = 3  # Size of the area around the mouse to monitor (in pixels)
toggle_key = 't'  # Key to toggle the monitoring on and off
interval = 0.00001  # Time interval for checking the pixel area (in seconds)
target_color = (211, 211, 211)  # The RGB color to detect (example: medium grey)
tolerance = 50  # Tolerance for color similarity
change_buffer = 100  # Number of frames to buffer for detecting significant color change

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
    global recent_colors
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


