# Fabric Weight Calculator

A simple desktop app that calculates fabric weight from **width (inches)** and
**GSM (g/m²)**. Built with Python's standard-library `tkinter` — no extra
dependencies to run the app itself.

![icon](icon.ico)

## What it calculates

```
width_m            = width_inches × 0.0254        # inches → meters
weight_per_meter_g = width_m × gsm                # grams per running meter
meters_per_kg      = 1000 ÷ weight_per_meter_g    # meters that make 1 kg
```

Results shown: weight per meter (grams **and** kg), and meters per kg.
Inputs are validated — empty, non-numeric, zero, or negative values show a
friendly error instead of crashing.

## Run it directly (no build needed)

Requires [Python for Windows](https://www.python.org/downloads/windows/).

```cmd
python fabric_calculator.py
```

---

## Build the standalone .exe (Windows)

This produces a single `.exe` that runs by double-clicking from the desktop —
no Python install, no terminal, no console window.

Open **Command Prompt**, then run:

```cmd
pip install pyinstaller
cd path\to\gsm-calculations
pyinstaller --onefile --windowed --noconsole --icon=icon.ico --add-data "icon.ico;." --name "Fabric Weight Calculator" fabric_calculator.py
```

> Run this from the folder that contains **both** `fabric_calculator.py` and
> `icon.ico`. On Windows the `--add-data` separator is a **semicolon** (`;`) —
> that is not a typo.

### What each flag does

| Flag | Purpose |
|------|---------|
| `--onefile` | Bundle everything into one self-contained `.exe` |
| `--windowed` / `--noconsole` | GUI only — **no terminal/console window ever appears** |
| `--icon=icon.ico` | Gives the `.exe` file its fabric-roll icon |
| `--add-data "icon.ico;."` | Bundles the icon so the window & taskbar show it too |
| `--name "..."` | Names the output `.exe` |

### Where the .exe ends up

```
dist\Fabric Weight Calculator.exe
```

Copy **just that one file** to the desktop. The `build` folder and the `.spec`
file are build scratch — you can ignore or delete them.

---

## Testing the build

1. In the `dist` folder, the `.exe` should already show the **fabric-roll icon**.
2. Double-click it → the GUI opens with **no console window and no flash**;
   the icon appears in the title bar and taskbar.
3. Enter Width `44`, GSM `180`, click **Calculate**. Expected results:
   - Weight per meter: **201.17 g**
   - Weight per meter: **0.201 kg**
   - Meters per kg: **4.97 m**
4. Click **Clear** to reset. Try blank / letters / `0` to confirm the friendly
   error message appears instead of a crash.

### Troubleshooting

- **A console window flashes:** you ran an old build. Delete the `build` and
  `dist` folders and the `.spec` file, then rebuild.
- **Desktop icon looks generic:** Windows is caching the old icon. Rename the
  `.exe` or reboot to refresh it.
- **"Windows protected your PC" on first launch:** normal for unsigned apps.
  Click **More info → Run anyway** once; it won't ask again.
- **First launch is slow:** `--onefile` unpacks itself on first run; this is
  normal and only noticeable the first time.

---

## Files

| File | What it is |
|------|-----------|
| `fabric_calculator.py` | The whole app, in one commented file |
| `icon.ico` | The app icon (multi-size: 256/64/48/32/16) |
| `make_icon.py` | Regenerates `icon.ico` (pure standard library). Run `python make_icon.py` if you want to tweak the icon's colors/design |
