import pytesseract
from PIL import ImageGrab
import tkinter as tk
import pygame
import sys
import numpy as np
import json

def load_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        return {"lang": "deu"}

def save_config(config_s):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config_s, f)

def save_text():
    global filename_entry
    filename = filename_entry.get()  # Get the filename from the entry
    text = text_widget.get(1.0, tk.END)  # Get the text from the text widget
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)

def take_screenshot(filename):
    if filename:
        screenshot = ImageGrab.grab()
        screenshot.save(filename)
        return screenshot
    else:
        return None

def select_screenshot_area(screen, screen_copy):
    clock = pygame.time.Clock()
    drawing = False
    rect = pygame.Rect(0, 0, 0, 0)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button, start drawing rectangle
                    drawing = True
                    rect.topleft = event.pos
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left mouse button, stop drawing rectangle
                    drawing = False
                    pygame.quit()
                    return rect.left, rect.top, rect.right, rect.bottom  # Return the screenshot box
            elif event.type == pygame.MOUSEMOTION:
                if drawing:
                    rect.width = event.pos[0] - rect.topleft[0]
                    rect.height = event.pos[1] - rect.topleft[1]
        screen.blit(screen_copy, (0, 0))  # Fill the screen with a screenshot
        if drawing:
            pygame.draw.rect(screen, (255, 255, 255), rect, 2)  # Draw the rectangle
        pygame.display.flip()
        clock.tick(30)  # Cap the framerate to 30 frames per second

def start_program(isconfig, text_widget=None):
    if isconfig == 1:
        print('skip')
    else:
        screenshot = take_screenshot("screenshot.png")
        pygame.init()
        size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
        screen = pygame.display.set_mode(size, pygame.NOFRAME)
        pygame.display.set_caption('Select screenshot area')

        screenshot_arr = np.array(screenshot)  # Convert PIL Image to numpy array
        screenshot_arr = screenshot_arr.transpose((1, 0, 2))  # Transpose the array to fit pygame's dimension order
        screen_copy = pygame.surfarray.make_surface(screenshot_arr)
        box = select_screenshot_area(screen, screen_copy)
        text = read_screenshot(screenshot, box)
        try:
            text_widget.delete(1.0, tk.END)  # Delete old text
            text_widget.insert(tk.END, text)
        except:
            print('error')

def read_screenshot(screenshot, box):
    config = load_config()
    pytesseract.pytesseract.tesseract_cmd = config.get("path", "tesseract")
    cropped_screenshot = screenshot.crop(box)
    cropped_screenshot.save("cropped_screenshot.png")
    if config is not None:
        config_options = f"--psm {config.get('psm', 3)} --oem {config.get('oem', 3)}"
        print(config_options)
        print(config.get('lang', 'deu'))
        string = pytesseract.image_to_string(cropped_screenshot, lang=config.get('lang', 'deu'), config=config_options)
    else:
        string = pytesseract.image_to_string(cropped_screenshot, lang=config.get('lang', 'deu'))
    return string

def open_config_menu():
    config_window = tk.Toplevel(root)
    config_window.title("Konfigurationsoptionen")

    config = load_config()
    psm_value = config.get("psm", "3: Auto")
    oem_value = config.get("oem", "3: Default")
    path_value = config.get("path", "C:\Program Files\Tesseract-OCR\tesseract.exe")
    lang_value = config.get("lang", "deu")

    label_path = tk.Label(config_window, text="Tesseract Path:")
    label_path.pack()

    path_entry = tk.Entry(config_window)
    path_entry.pack()
    path_entry.insert(0, path_value)

    label_psm = tk.Label(config_window, text="Page Segmentation Mode (psm):")
    label_psm.pack()

    psm_options = ["0: OSD only", "1: Auto OSD", "3: Auto", "4: Single column", "6: Uniform block of text"]
    psm_var = tk.StringVar()
    psm_var.set(psm_value)

    psm_dropdown = tk.OptionMenu(config_window, psm_var, *psm_options)
    psm_dropdown.pack()

    label_oem = tk.Label(config_window, text="OCR Engine Mode (oem):")
    label_oem.pack()

    oem_options = ["0: Legacy", "1: LSTM only", "2: Legacy + LSTM", "3: Default"]
    oem_var = tk.StringVar()
    oem_var.set(oem_value)

    oem_dropdown = tk.OptionMenu(config_window, oem_var, *oem_options)
    oem_dropdown.pack()

    label_lang = tk.Label(config_window, text="Sprache:")
    label_lang.pack()

    lang_options = ["deu", "eng", "fra", "spa", "ita", "por", "rus"]  # possible language options
    lang_var = tk.StringVar()
    lang_var.set(lang_value)

    lang_dropdown = tk.OptionMenu(config_window, lang_var, *lang_options)
    lang_dropdown.pack()

    def apply_config():
        psm_value = int(psm_var.get().split(":")[0])
        oem_value = int(oem_var.get().split(":")[0])
        path_value = path_entry.get()
        lang_value = lang_var.get()
        config = {"psm": psm_value, "oem": oem_value, "path": path_value, "lang": lang_value}
        save_config(config)
        start_program(1)
        config_window.destroy()

    # save option button
    button_apply = tk.Button(config_window, text="Anwenden", command=apply_config)
    button_apply.pack()

filename_entry = None
text_widget = None

if __name__ == "__main__":
    CONFIG_FILE = "config.json"
    root = tk.Tk()
    root.title("Screen2txt")
    config = load_config()
    button = tk.Button(root, text="Neuen Screenshot", command=lambda: start_program(0, text_widget=text_widget))
    button.pack()

    text_widget = tk.Text(root)
    text_widget.pack()

    filename_entry = tk.Entry(root)
    filename_entry.pack()
    filename_entry.insert(0, "output.txt")  # Default filename

    button_save = tk.Button(root, text="Text speichern", command=save_text)
    button_save.pack()
    button_config = tk.Button(root, text="Konfiguration", command=open_config_menu)  # add button config menue
    button_config.pack()

    root.mainloop()
