#!/usr/bin/env python3

"""
Cross-platform desktop automation library
"""

import os, sys, time, shutil, subprocess, re, urllib.request

from pymouse import PyMouse # from PyUserInput
from pykeyboard import PyKeyboard # from PyUserInput
import easygui

m = PyMouse()
k = PyKeyboard()

MOUSE_BUTTONS = {
    "left": 1,
    "middle": 2,
    "right": 3,
    "scroll_up": 4,
    "scroll_down": 5,
    "scroll_left": 6,
    "scroll_right": 7,
}

KEYBOARD_ALIASES = {
    # modifiers
    "Ctrl":        k.control_key,
    "Alt":         k.alt_key,
    "Shift":       k.shift_key,
    "Win":         k.super_l_key,
    
    # special keys
    "\n":          k.return_key,
    "\t":          k.tab_key,
    "Backspace":   k.backspace_key,
    "Delete":      k.delete_key,
    "Escape":      k.escape_key,
    "PrintScreen": k.print_screen_key,
    
    # navigation
    "Left":        k.left_key,
    "Right":       k.right_key,
    "Up":          k.up_key,
    "Down":        k.down_key,
    "Home":        k.home_key,
    "End":         k.end_key,
    "PageUp":      k.page_up_key,
    "PageDown":    k.page_down_key,
    
    # toggles
    "CapsLock":    k.caps_lock_key,
    "NumLock":     k.num_lock_key,
    "ScrollLock":  k.scroll_lock_key,
}

def _get_key(key):
    assert str(key) != "", "Invalid key name: {}".format(key)
    if key in KEYBOARD_ALIASES: return KEYBOARD_ALIASES[key]
    if len(key) == 1 and key.lower() in "abcdefghijklmnopqrstuvwxyz1234567890": return key.lower()
    raise ValueError("Invalid key: \"{}\"".format(key))

def mouse_get_position():
    """
    Returns the X and Y coordinates of the mouse.
    """
    return m.position()

def mouse_set_position(x, y, relative = False):
    """
    Move the mouse to the coordinate defined by `x` and `y`.
    
    If `relative` is truthy, `x` and `y` are interpreted as offsets from the current mouse position.
    """
    if relative:
        current_x, current_y = mouse_get_position()
        x, y = current_x + x, current_y + y
    m.move(int(x), int(y))

def mouse_click(x = None, y = None, button = "left", duration = 0.05):
    """
    Click the mouse button `button` at the coordinate defined by `x` and `y` for duration `duration`.
    """
    assert button in MOUSE_BUTTONS, "Button must be one of: {}".format(", ".join(sorted(MOUSE_BUTTONS.keys())))
    assert float(duration) >= 0, "Click duration must be positive"
    current_x, current_y = mouse_get_position()
    x, y = int(current_x if x is None else x), int(current_y if y is None else y)
    m.press(x, y, MOUSE_BUTTONS[button])
    time.sleep(duration)
    m.release(x, y, MOUSE_BUTTONS[button])

def mouse_down(x = None, y = None, button = "left"):
    """
    Hold down the mouse button `button` at the coordinate defined by `x` and `y`.
    """
    assert button in MOUSE_BUTTONS, "Button must be one of: {}".format(", ".join(sorted(MOUSE_BUTTONS.keys())))
    current_x, current_y = mouse_get_position()
    x, y = int(current_x if x is None else x), int(current_y if y is None else y)
    m.press(x, y, MOUSE_BUTTONS[button])

def mouse_up(x = None, y = None, button = "left"):
    """
    Release the mouse button `button` at the coordinate defined by `x` and `y`.
    """
    assert button in MOUSE_BUTTONS, "Button must be one of: {}".format(", ".join(sorted(MOUSE_BUTTONS.keys())))
    current_x, current_y = mouse_get_position()
    x, y = int(current_x if x is None else x), int(current_y if y is None else y)
    m.release(x, y, MOUSE_BUTTONS[button])

def keyboard_press(keys, delay = 0.01, duration = 0.01):
    keys = [_get_key(key) for key in keys]
    for i, key in enumerate(keys):
        if i != 0: time.sleep(delay)
        k.press_key(key)
    time.sleep(duration)
    for i, key in enumerate(reversed(keys)):
        if i != 0: time.sleep(delay)
        k.release_key(key)

def keyboard_down(keys, delay = 0.01):
    keys = [_get_key(key) for key in keys]
    for i, key in enumerate(keys):
        if i != 0: time.sleep(delay)
        k.press_key(key)

def keyboard_up(keys, delay = 0.01):
    keys = [_get_key(key) for key in keys]
    for i, key in enumerate(reversed(keys)):
        if i != 0: time.sleep(delay)
        k.release_key(key)

def keyboard_type(string, delay = 0.01, duration = 0.01):
    keys = [_get_key(key) for key in string]
    for i, key in enumerate(keys):
        if i != 0: time.sleep(delay)
        k.press_key(key)
        time.sleep(duration)
        k.release_key(key)

def keyboard_get_toggles():
    if sys.platform == "win32":
        from win32api import GetKeyState # from pywin32, which we have because PyUserInput depends on it
        from win32con import VK_CAPITAL, VK_NUMLOCK, VK_SCROLL # from pywin32, which we have because PyUserInput depends on it
        return {
            "CapsLock": GetKeyState(VK_CAPITAL) != 0,
            "NumLock": GetKeyState(VK_NUMLOCK) != 0,
            "ScrollLock": GetKeyState(VK_SCROLL) != 0,
        }
    xset_path = shutil.which("xset")
    if xset_path:
        response = subprocess.check_output([xset_path, "q"]).decode("utf-8")
        result = re.search(r"LED\s+mask:\s+(\d+)", response)
        if not result: raise ValueError("Could not obtain toggle states from X")
        toggles = int(result.group(1))
        return {
            "CapsLock": (toggles & 0b1) != 0,
            "NumLock": (toggles & 0b10) != 0,
            "ScrollLock": (toggles & 0b100) != 0,
        }
    raise ValueError("Could not find X settings controller")

def dialog_prompt(message = "Press any button to continue", title = "Message Box", buttons = ["OK"]):
    """
    Show a dialog with prompt `message`, title `title`, and a set of buttons `buttons` to choose from.
    
    Returns the text of the button chosen, or `None` if closed.
    """
    return easygui.buttonbox(str(message), str(title), str(buttons))

def dialog_text(message = "Press OK to continue", title = "Text Box", text = ""):
    """
    Show a dialog with prompt `message`, title `title`, and text content `text`.
    """
    easygui.codebox(str(message), str(title), str(text))

def dialog_text_entry(message = "Enter a value:", title = "Input Box", initial_value = "", is_password = False):
    """
    Show a dialog with prompt `message`, title `title`, and a text input box (or password input box if `is_password` is truthy) with initial value `initial_value`.
    
    Returns the value entered by the user, or `None` if closed or cancelled.
    """
    if is_password: return easygui.passwordbox(str(message), str(title), str(initial_value))
    return easygui.enterbox(str(message), str(title), str(initial_value))

def dialog_file_select(title = "Choose file(s)", initial_shown_glob = "./*", is_save_dialog = False, multiselect = False):
    """
    Show a file selection dialog with title `title`, initially showing files matching the glob `initial_shown_glob`.
    
    Has "Save" button when `is_save_dialog` is truthy, and otherwise an "Open" button.
    
    Returns a list of selected paths when `multiselect` is truthy and otherwise just the selected path, or `None` if cancelled.
    """
    if is_save_dialog: return easygui.filesavebox(None, str(title), str(initial_shown_glob))
    path = easygui.fileopenbox(None, str(title), str(initial_shown_glob), None, str(multiselect))
    if os.path.isfile(path): return path
    return None

def dialog_folder_select(title = "Choose a folder", initial_shown_glob = None):
    """
    Show a folder selection dialog with title `title`, initially showing files matching the glob `initial_shown_glob`.
    
    Returns the selected path.
    """
    return easygui.diropenbox(None, str(title), str(initial_shown_glob))

def sound_get_volume():
    amixer_path = shutil.which("amixer")
    if amixer_path:
        response = subprocess.check_output([amixer_path, "-D", "pulse", "sget", "Master"]).decode("utf-8")
        result = re.search(r"\d+(?=%)", response)
        if not result: raise ValueError("Could not obtain volume from ALSA")
        return int(result.group())
    raise ValueError("Could not find ALSA mixer controller")
    # wip: windows

def sound_get_mute():
    amixer_path = shutil.which("amixer")
    if amixer_path:
        response = subprocess.check_output([amixer_path, "-D", "pulse", "sget", "Master"]).decode("utf-8")
        return "[off]" in response
    raise ValueError("Could not find ALSA mixer controller")
    # wip: windows

def sound_set_volume(volume, relative = False):
    assert 0 <= float(volume) <= 100, "Volume must be a valid percentage between 0 and 100"
    amixer_path = shutil.which("amixer")
    if amixer_path:
        level = "{}%{}".format(abs(volume), ("+" if volume >= 0 else "-") if relative else "")
        subprocess.call([amixer_path, "-D", "pulse", "sset", "Master", level])
        return
    raise ValueError("Could not find ALSA mixer controller")
    # wip: windows

def sound_set_mute(mute = True):
    amixer_path = shutil.which("amixer")
    if amixer_path:
        subprocess.call([amixer_path, "-D", "pulse", "sset", "Master", "1+", "mute" if mute else "unmute"])
        return
    raise ValueError("Could not find ALSA mixer controller")
    # wip: windows

def web_download_file(url, file_path):
    os.makedirs(os.path.dirname(file_path)) # ensure that the folder hierarchy is in place
    with urllib.request.urlopen(url) as response, open(file_path, "wb") as out_file:
        shutil.copyfileobj(response, out_file)
