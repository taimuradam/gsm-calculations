"""
Fabric Weight Calculator
=========================
A simple desktop GUI (tkinter, standard library only) that calculates
fabric weight from fabric width and GSM (grams per square meter).

CALCULATION
-----------
    width_m            = width_inches * 0.0254        # inches -> meters
    weight_per_meter_g = width_m * gsm                # grams per running meter
    meters_per_kg      = 1000 / weight_per_meter_g    # how many meters make 1 kg

To tweak later: the calculation lives in `calculate()`, and the layout is
built in `build_ui()`. Colors/sizes are grouped in the CONFIG block below.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox

# --------------------------------------------------------------------------
# CONFIG - easy visual tweaks live here
# --------------------------------------------------------------------------
INCH_TO_METER = 0.0254          # 1 inch = 0.0254 meters (fixed constant)

WINDOW_TITLE = "Fabric Weight Calculator"
BG_COLOR = "#f4f4f4"            # window background
RESULT_COLOR = "#0b5394"        # color for the big result numbers
LABEL_FONT = ("Segoe UI", 13)
INPUT_FONT = ("Segoe UI", 14)
BUTTON_FONT = ("Segoe UI", 12, "bold")
RESULT_FONT = ("Segoe UI", 18, "bold")     # large so results are easy to read
RESULT_TITLE_FONT = ("Segoe UI", 11)


class FabricCalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title(WINDOW_TITLE)
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(False, False)

        # Tk variables holding the text of each input field
        self.width_var = tk.StringVar()
        self.gsm_var = tk.StringVar()

        # Tk variables holding the result text shown on screen
        self.weight_g_var = tk.StringVar(value="—")
        self.weight_kg_var = tk.StringVar(value="—")
        self.meters_kg_var = tk.StringVar(value="—")

        self.build_ui()

    # ----------------------------------------------------------------------
    # UI construction
    # ----------------------------------------------------------------------
    def build_ui(self):
        pad = {"padx": 12, "pady": 8}

        # Main container frame with some breathing room
        container = tk.Frame(self.root, bg=BG_COLOR, padx=24, pady=20)
        container.grid(row=0, column=0)

        # --- Heading -------------------------------------------------------
        heading = tk.Label(
            container,
            text="Fabric Weight Calculator",
            font=("Segoe UI", 16, "bold"),
            bg=BG_COLOR,
        )
        heading.grid(row=0, column=0, columnspan=2, pady=(0, 16))

        # --- Width input ---------------------------------------------------
        tk.Label(container, text="Width (inches)", font=LABEL_FONT, bg=BG_COLOR).grid(
            row=1, column=0, sticky="w", **pad
        )
        width_entry = tk.Entry(
            container, textvariable=self.width_var, font=INPUT_FONT, width=14, justify="center"
        )
        width_entry.grid(row=1, column=1, **pad)
        width_entry.focus()  # cursor starts here

        # --- GSM input -----------------------------------------------------
        tk.Label(container, text="GSM (g/m²)", font=LABEL_FONT, bg=BG_COLOR).grid(
            row=2, column=0, sticky="w", **pad
        )
        gsm_entry = tk.Entry(
            container, textvariable=self.gsm_var, font=INPUT_FONT, width=14, justify="center"
        )
        gsm_entry.grid(row=2, column=1, **pad)

        # --- Buttons -------------------------------------------------------
        button_row = tk.Frame(container, bg=BG_COLOR)
        button_row.grid(row=3, column=0, columnspan=2, pady=(16, 8))

        calc_btn = tk.Button(
            button_row,
            text="Calculate",
            font=BUTTON_FONT,
            width=12,
            bg="#0b5394",
            fg="white",
            activebackground="#073763",
            activeforeground="white",
            relief="flat",
            command=self.calculate,
        )
        calc_btn.grid(row=0, column=0, padx=6)

        clear_btn = tk.Button(
            button_row,
            text="Clear",
            font=BUTTON_FONT,
            width=12,
            bg="#dddddd",
            activebackground="#bbbbbb",
            relief="flat",
            command=self.clear,
        )
        clear_btn.grid(row=0, column=1, padx=6)

        # Pressing Enter anywhere triggers Calculate (convenient for dad)
        self.root.bind("<Return>", lambda event: self.calculate())

        # --- Results panel -------------------------------------------------
        results = tk.Frame(container, bg="white", bd=1, relief="solid", padx=20, pady=16)
        results.grid(row=4, column=0, columnspan=2, pady=(12, 0), sticky="ew")

        self._add_result_row(results, 0, "Weight per meter (grams)", self.weight_g_var)
        self._add_result_row(results, 2, "Weight per meter (kg)", self.weight_kg_var)
        self._add_result_row(results, 4, "Meters per kg", self.meters_kg_var)

    def _add_result_row(self, parent, row, title, var):
        """Helper: a small title label above a large result value."""
        tk.Label(parent, text=title, font=RESULT_TITLE_FONT, bg="white", fg="#555555").grid(
            row=row, column=0, sticky="w", pady=(6, 0)
        )
        tk.Label(
            parent, textvariable=var, font=RESULT_FONT, bg="white", fg=RESULT_COLOR
        ).grid(row=row + 1, column=0, sticky="w", pady=(0, 6))

    # ----------------------------------------------------------------------
    # Actions
    # ----------------------------------------------------------------------
    def _parse_positive(self, raw, field_name):
        """
        Convert a text field into a positive float.
        Returns the float, or raises ValueError with a friendly message.
        """
        raw = raw.strip()
        if not raw:
            raise ValueError(f"Please enter a value for {field_name}.")
        try:
            value = float(raw)
        except ValueError:
            raise ValueError(f"{field_name} must be a number (you entered '{raw}').")
        if value <= 0:
            raise ValueError(f"{field_name} must be greater than zero.")
        return value

    def calculate(self):
        """Read inputs, validate, compute, and display results."""
        try:
            width_inches = self._parse_positive(self.width_var.get(), "Width (inches)")
            gsm = self._parse_positive(self.gsm_var.get(), "GSM (g/m²)")
        except ValueError as err:
            messagebox.showerror("Invalid input", str(err))
            return

        # Core calculation
        width_m = width_inches * INCH_TO_METER
        weight_per_meter_g = width_m * gsm

        # Guard against divide-by-zero (already excluded by the >0 checks,
        # but we keep this as a friendly safety net).
        if weight_per_meter_g <= 0:
            messagebox.showerror(
                "Cannot calculate",
                "Width and GSM must both be greater than zero.",
            )
            return

        meters_per_kg = 1000 / weight_per_meter_g

        # Update the on-screen results
        self.weight_g_var.set(f"{weight_per_meter_g:.2f} g")
        self.weight_kg_var.set(f"{weight_per_meter_g / 1000:.3f} kg")
        self.meters_kg_var.set(f"{meters_per_kg:.2f} m")

    def clear(self):
        """Reset all fields and results."""
        self.width_var.set("")
        self.gsm_var.set("")
        self.weight_g_var.set("—")
        self.weight_kg_var.set("—")
        self.meters_kg_var.set("—")


def _resource_path(filename):
    """
    Locate a bundled data file both when running as a plain .py script and
    when frozen into a PyInstaller --onefile .exe (which unpacks to a temp
    folder available as sys._MEIPASS).
    """
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, filename)


def main():
    root = tk.Tk()

    # Show the window/taskbar icon. Wrapped in try/except because .ico via
    # iconbitmap is a Windows feature; on other systems we just skip it.
    try:
        root.iconbitmap(_resource_path("icon.ico"))
    except Exception:
        pass

    FabricCalculatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
