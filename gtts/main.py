import threading
import tkinter as tk
from pynput import keyboard

from morse_core import check_gaps, on_press, on_release
from gui import MorseGUI


def main():
    root = tk.Tk()
    MorseGUI(root)

    gap_thread = threading.Thread(target=check_gaps, daemon=True)
    gap_thread.start()

    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()

    def on_closing():
        listener.stop()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == '__main__':
    main()
