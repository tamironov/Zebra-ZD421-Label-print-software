# usb_printer.py
# This file handles the communication with the USB printer using the pywin32 library.

import tkinter as tk
from tkinter import messagebox
import win32print
import win32api
import pywintypes

def print_label_usb(zpl_string, printer_name):
    """
    Sends a ZPL string to a specified USB printer on Windows.

    Args:
        zpl_string (str): The ZPL II string to be printed.
        printer_name (str): The name of the printer as it appears in Windows.

    Returns:
        tuple: A tuple (bool, str) indicating success and a message.
    """
    try:
        hPrinter = win32print.OpenPrinter(printer_name)
        DOC_INFO_1 = ("ZPL Label", None, "RAW")
        job = win32print.StartDocPrinter(hPrinter, 1, DOC_INFO_1)
        if job:
            win32print.StartPagePrinter(hPrinter)
            win32print.WritePrinter(hPrinter, zpl_string.encode('utf-8'))
            win32print.EndPagePrinter(hPrinter)
            win32print.EndDocPrinter(hPrinter)
            win32print.ClosePrinter(hPrinter)
            return True, "ZPL data sent successfully."
        else:
            return False, "Failed to start print job."
    except pywintypes.error as e:
        messagebox.showerror("Printer Error", f"A printer error occurred:\n{e}")
        return False, f"Printer error: {e}"
    except Exception as e:
        messagebox.showerror("Unexpected Error", f"An unexpected error occurred:\n{e}")
        return False, f"Unexpected error: {e}"
