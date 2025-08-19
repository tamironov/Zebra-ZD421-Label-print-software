# gui.py
# This file handles the entire user interface and application logic using Tkinter.
# It imports functions from other files to perform printing and ZPL generation.

import tkinter as tk
from tkinter import messagebox, filedialog
import os
import datetime
import csv
from zpl_generator import generate_zpl_string
from usb_printer import print_label_usb

class ZebraPrintApp(tk.Tk):
    DEFAULT_STATUS = "Ready. Scan a serial number."

    def __init__(self):
        super().__init__()
        self.title("Zebra SN Printer (USB)")
        self.geometry("550x880")
        self.max_sn = 12
        self.serial_numbers = []
        self.last_printed_sns = []
        self.batch_counter = 0
        self.csv_path = "printed_serials.csv"
        self.help_text = """
***Created By Tamir Mironov***
        How to Use the Zebra SN Printer App:

        1.  Printer Name: Enter the exact name of your Zebra printer as it appears in Windows.
            Step 1) Open Settings on your computer.
            Step 2) Navigate to Printers & Scanners.
            Step 3) Select ZDesigner ZD421-203dpi from the list.
            Step 4) Click Printer Properties.
            Step 5) In the General tab, copy the Printer Name exactly as it appears.

        2.  Product Info: Fill in the Product Name and Part Number. This information will appear on the top of the label.

        3.  Offsets: Adjust the X and Y offsets in dots to fine-tune the position of the QR codes and Serial Numbers on your labels.

        4.  Scan/Enter SNs: Scan or type each serial number into the "Scan Serial Number" box and press Enter.

        5.  Collected SNs: A list of all collected serial numbers will appear. The maximum number of labels per batch is 12.

        6.  Print Labels: Click "Print Labels" to send all collected serial numbers to the printer. The list will be cleared automatically after a successful print.

        7.  Print Last Batch: If a print job fails or you need a duplicate, click this button to reprint the last batch of labels that were sent.

        8.  Delete/Clear: Use "Delete Selected SN" to remove a single entry or "Clear All" to empty the entire list.
"""
        self.create_widgets()

    def create_widgets(self):
        # ---------------- Printer Name Section ----------------
        frame = tk.LabelFrame(self, text="Printer Settings", padx=10, pady=5)
        frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(frame, text="Printer Name:").pack(side=tk.LEFT)
        self.printer_name_entry = tk.Entry(frame)
        self.printer_name_entry.insert(0, "ZDesigner ZD421-203dpi ZPL")
        self.printer_name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # ---------------- Product Info Section ----------------
        frame2 = tk.LabelFrame(self, text="Product Info", padx=10, pady=5)
        frame2.pack(fill=tk.X, padx=10, pady=5)
        self.include_product_var = tk.BooleanVar(value=True)
        self.product_check = tk.Checkbutton(frame2, text="Include Product Name", variable=self.include_product_var)
        self.product_check.grid(row=0, column=0, sticky=tk.W)
        self.product_name_entry = tk.Entry(frame2)
        self.product_name_entry.grid(row=0, column=1, sticky=tk.EW, padx=5)
        self.product_name_entry.insert(0, "Enter Product Name")
        self.product_name_entry.bind("<FocusIn>", lambda e: self.clear_entry_on_focus(self.product_name_entry, "Enter Product Name"))
        self.include_pn_var = tk.BooleanVar(value=True)
        self.pn_check = tk.Checkbutton(frame2, text="Include Part Number", variable=self.include_pn_var)
        self.pn_check.grid(row=1, column=0, sticky=tk.W)
        self.pn_entry = tk.Entry(frame2)
        self.pn_entry.grid(row=1, column=1, sticky=tk.EW, padx=5)
        self.pn_entry.insert(0, "Enter Part Number")
        self.pn_entry.bind("<FocusIn>", lambda e: self.clear_entry_on_focus(self.pn_entry, "Enter Part Number"))
        frame2.grid_columnconfigure(1, weight=1)

        # ---------------- Offsets Section ----------------
        frame3 = tk.LabelFrame(self, text="Offsets", padx=10, pady=5)
        frame3.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(frame3, text="QR X Offset:").pack(side=tk.LEFT)
        self.qr_x_offset_entry = tk.Entry(frame3, width=5)
        self.qr_x_offset_entry.insert(0, "50")
        self.qr_x_offset_entry.pack(side=tk.LEFT, padx=5)
        tk.Label(frame3, text="QR Y Offset:").pack(side=tk.LEFT, padx=(10,0))
        self.qr_y_offset_entry = tk.Entry(frame3, width=5)
        self.qr_y_offset_entry.insert(0, "0")
        self.qr_y_offset_entry.pack(side=tk.LEFT, padx=5)
        tk.Label(frame3, text="SN X Offset:").pack(side=tk.LEFT, padx=(10,0))
        self.sn_x_offset_entry = tk.Entry(frame3, width=5)
        self.sn_x_offset_entry.insert(0, "0")
        self.sn_x_offset_entry.pack(side=tk.LEFT, padx=5)
        tk.Label(frame3, text="SN Y Offset:").pack(side=tk.LEFT, padx=(10,0))
        self.sn_y_offset_entry = tk.Entry(frame3, width=5)
        self.sn_y_offset_entry.insert(0, "70")
        self.sn_y_offset_entry.pack(side=tk.LEFT, padx=5)

        # ---------------- Serial Numbers Section ----------------
        frame_sn = tk.LabelFrame(self, text="Serial Number Input", padx=10, pady=10)
        frame_sn.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Status Bar
        self.status_var = tk.StringVar(value=self.DEFAULT_STATUS)
        self.status_label = tk.Label(
            frame_sn,
            textvariable=self.status_var,
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.CENTER,
            justify=tk.CENTER,
            font=("Helvetica", 14),
            height=2
        )
        self.status_label.pack(fill=tk.X, pady=(0, 8))

        tk.Label(frame_sn, text="Scan Serial Number:").pack(anchor=tk.W)
        self.sn_entry = tk.Entry(frame_sn, font=("Helvetica", 14))
        self.sn_entry.pack(fill=tk.X, pady=5)
        self.sn_entry.focus_set()
        self.sn_entry.bind("<Return>", self.add_serial_number)

        self.listbox_label = tk.Label(frame_sn, text=f"Collected SNs (0/{self.max_sn}):")
        self.listbox_label.pack(anchor=tk.W, pady=(10,0))

        self.sn_listbox = tk.Listbox(frame_sn, height=12, font=("Courier New", 11))
        self.sn_listbox.pack(fill=tk.BOTH, expand=True)
        self.sn_listbox.bind("<<ListboxSelect>>", self.check_delete_button_state)

        # ---------------- Action Buttons Section ----------------
        action_frame = tk.Frame(frame_sn, pady=5)
        action_frame.pack(anchor=tk.W)
        self.delete_button = tk.Button(action_frame, text="Delete Selected SN", command=self.delete_selected_sn, state=tk.DISABLED)
        self.delete_button.pack(side=tk.LEFT, padx=(0,5))
        self.clear_button = tk.Button(action_frame, text="Clear All", command=self.clear_all)
        self.clear_button.pack(side=tk.LEFT)

        # ---------------- Print Buttons Section ----------------
        button_frame = tk.LabelFrame(self, text="Printing", padx=10, pady=10)
        button_frame.pack(fill=tk.X, padx=10, pady=5)

        # Auto-print checkbox
        self.auto_print_var = tk.BooleanVar(value=False)
        self.auto_print_check = tk.Checkbutton(button_frame, text="Auto-print when 12 SN scanned", variable=self.auto_print_var)
        self.auto_print_check.pack(side=tk.TOP, anchor=tk.W, pady=(0,5))

        self.print_button = tk.Button(button_frame, text="🖨️  Print Labels", command=self.print_labels, state=tk.DISABLED)
        self.print_button.pack(side=tk.TOP, fill=tk.X)
        self.print_last_button = tk.Button(button_frame, text="↩️  Print Last Batch", command=self.print_last_batch, state=tk.DISABLED)
        self.print_last_button.pack(side=tk.TOP, fill=tk.X, pady=(5,0))

        # ---------------- CSV / Help Section ----------------
        frame_csv = tk.LabelFrame(self, text="CSV Logging / Help", padx=10, pady=5)
        frame_csv.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=5)
        tk.Label(frame_csv, text="CSV File:").pack(side=tk.LEFT)
        self.csv_entry = tk.Entry(frame_csv)
        self.csv_entry.insert(0, self.csv_path)
        self.csv_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        tk.Button(frame_csv, text="Browse", command=self.select_csv_path).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_csv, text="View CSV", command=self.view_csv_file).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_csv, text="Help", command=self.show_help).pack(side=tk.BOTTOM, pady=5)

    # ----------------- Helpers -----------------
    def clear_entry_on_focus(self, entry_widget, default_text):
        if entry_widget.get() == default_text:
            entry_widget.delete(0, tk.END)

    def select_csv_path(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")])
        if path:
            self.csv_path = path
            self.csv_entry.delete(0, tk.END)
            self.csv_entry.insert(0, path)

    def view_csv_file(self):
        if not os.path.exists(self.csv_path):
            messagebox.showinfo("Info", f"No CSV found at {self.csv_path}")
            return
        viewer = tk.Toplevel(self)
        viewer.title("CSV Viewer")
        viewer.geometry("600x400")
        text = tk.Text(viewer)
        text.pack(fill=tk.BOTH, expand=True)
        with open(self.csv_path, newline="") as f:
            reader = csv.reader(f)
            for row in reader:
                text.insert(tk.END, ", ".join(row) + "\n")
        text.config(state=tk.DISABLED)

    def show_help(self):
        help_window = tk.Toplevel(self)
        help_window.title("Help")
        help_window.geometry("500x400")
        text_widget = tk.Text(help_window, wrap=tk.WORD, font=("Helvetica", 10), padx=10, pady=10)
        text_widget.insert(tk.END, self.help_text)
        text_widget.config(state=tk.DISABLED)
        text_widget.pack(fill=tk.BOTH, expand=True)
        tk.Button(help_window, text="Close", command=help_window.destroy).pack(pady=5)
        help_window.grab_set()
        help_window.transient(self)

    # ----------------- Status Helper -----------------
    def set_status(self, message, color="black", duration=3000):
        self.status_label.config(fg=color)
        self.status_var.set(message)
        if hasattr(self, "_status_clear_id"):
            self.after_cancel(self._status_clear_id)
        # After 'duration', reset back to default message instead of blank
        self._status_clear_id = self.after(duration, lambda: self.status_var.set(self.DEFAULT_STATUS))

    # ----------------- Serial Number Handling -----------------
    def add_serial_number(self, event=None):
        sn = self.sn_entry.get().strip()
        self.sn_entry.delete(0, tk.END)
        if not sn:
            self.set_status("No serial number entered.", color="red")
            return
        if sn in self.serial_numbers:
            self.set_status(f"Serial number '{sn}' was already scanned!", color="red")
            return
        if len(self.serial_numbers) >= self.max_sn:
            self.set_status("Maximum of 12 serial numbers reached.", color="red")
            return

        self.serial_numbers.append(sn)
        self.update_listbox()
        self.set_status(f"Added serial number: {sn}", color="green")

        # Auto-print if max SN reached AND checkbox is checked
        if len(self.serial_numbers) == self.max_sn and self.auto_print_var.get():
            self.print_labels()
            self.set_status(f"Auto-printed batch {self.batch_counter}", color="green")
            # Clear list for next batch
            self.serial_numbers = []
            self.update_listbox()

    def update_listbox(self):
        self.sn_listbox.delete(0, tk.END)
        for i, sn in enumerate(self.serial_numbers):
            self.sn_listbox.insert(tk.END, f"{i+1:02d}. {sn}")
        self.listbox_label.config(text=f"Collected SNs ({len(self.serial_numbers)}/{self.max_sn}):")
        self.print_button.config(state=tk.NORMAL if self.serial_numbers else tk.DISABLED)
        # Enable Print Last Batch if we have something stored
        self.print_last_button.config(state=tk.NORMAL if self.last_printed_sns else tk.DISABLED)

    def check_delete_button_state(self, event=None):
        self.delete_button.config(state=tk.NORMAL if self.sn_listbox.curselection() else tk.DISABLED)

    def delete_selected_sn(self):
        selection = self.sn_listbox.curselection()
        if selection:
            idx = selection[0]
            self.serial_numbers.pop(idx)
            self.update_listbox()

    def clear_all(self):
        self.serial_numbers = []
        self.update_listbox()

    # ----------------- Printing -----------------
    def execute_print(self, sns_to_print):
        if not sns_to_print:
            return False
        product_name = self.product_name_entry.get().strip()
        part_number = self.pn_entry.get().strip()
        try:
            sn_x_offset = int(self.sn_x_offset_entry.get())
            sn_y_offset = int(self.sn_y_offset_entry.get())
            qr_x_offset = int(self.qr_x_offset_entry.get())
            qr_y_offset = int(self.qr_y_offset_entry.get())
        except ValueError:
            return False
        printer_name = self.printer_name_entry.get().strip()
        zpl_string = generate_zpl_string(
            product_name, part_number, sns_to_print,
            qr_x_offset, qr_y_offset, sn_x_offset, sn_y_offset,
            include_product=self.include_product_var.get(),
            include_pn=self.include_pn_var.get()
        )
        success, msg = print_label_usb(zpl_string, printer_name)
        if success:
            self.batch_counter += 1
            self.log_to_csv(sns_to_print)
            self.last_printed_sns = list(sns_to_print)
            # Keep "Print Last Batch" enabled
            self.print_last_button.config(state=tk.NORMAL)
        else:
            self.set_status(msg, color="red")
        return success

    def print_labels(self):
        if self.execute_print(self.serial_numbers):
            messagebox.showinfo("Success", f"Printed {len(self.serial_numbers)} labels in batch {self.batch_counter}")
            self.clear_all()

    def print_last_batch(self):
        if self.last_printed_sns:
            if self.execute_print(self.last_printed_sns):
                self.set_status("Reprinted last batch.", color="green")
            else:
                self.set_status("Failed to reprint last batch.", color="red")

    # ----------------- CSV Logging -----------------
    def log_to_csv(self, sns):
        now = datetime.datetime.now()
        file_exists = os.path.exists(self.csv_path)
        with open(self.csv_path, 'a', newline='') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Batch", "Date", "Time", "Serial Number"])
            for sn in sns:
                writer.writerow([self.batch_counter, now.date(), now.time().strftime("%H:%M:%S"), sn])
