
# 🖼️ invert.bat — Image Inversion via Windows SendTo

This script is designed to make it easy to invert scanned film images using a simple right-click operation on `.jpg` or `.png` files in Windows Explorer. It processes a single image by analyzing it with a Python script, inverting it, and displaying the result temporarily in IrfanView before automatically closing.

---

## 📦 What It Does

1. **Analyzes** the selected image using `shape_image.py`, which outputs shape data to a JSON file.
2. **Processes** the shape data using `invert_image.py` to produce a new, inverted `.png` file.
3. **Saves** the output image in the **same folder** as the original, with `_inverted` added to the filename.
4. **Opens** the result in **IrfanView** for 10 seconds.
5. **Closes** IrfanView automatically using its `/killmesoftly` switch.

---

## 🛠 Requirements

Make sure you have the following installed and correctly located:

- **Google Cloud SDK** (specifically its bundled Python interpreter):

  ```
  C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\platform\bundledpython\python.exe
  ```

- Two custom Python scripts:
  - `shape_image.py`
  - `invert_image.py`

  These must be placed in:

  ```
  D:\GitHub\neg2pos\
  ```

- **IrfanView** installed at:

  ```
  C:\Program Files\IrfanView\i_view64.exe
  ```

---

## 📂 Installation

1. Press `Windows + R` to open the Run dialog.
2. Type:
   ```
   shell:sendto
   ```
3. Press **Enter** — this opens your personal SendTo folder.
4. Copy `invert.bat` into the **SendTo** folder.

Now, it will appear in the context menu when you right-click on a supported image file.

---

## 🚀 How to Use

1. Right-click on a `.jpg` or `.png` image file.
2. Choose:
   ```
   Send to > invert.bat
   ```
3. The script will:
   - Run analysis and inversion on the image.
   - Save the result as a `.png` file with `_inverted` added to the filename.
   - Show the result in **IrfanView** for 10 seconds.
   - Close IrfanView automatically.

---

## 📁 Output File Naming

Output image is saved to the **same folder** as the original with the format:

```
Original:   filename.jpg
Converted:  filename_inverted.png
```

---

## 💡 Example

If you right-click on:

```
C:\Scans\frame001.jpg
```

You’ll get:

```
C:\Scans\frame001_inverted.png
```

And it will open automatically in IrfanView, then close.

---

## 🔧 Script Summary

Below is a simplified view of what the batch script does internally:

```batch
:: Run shape analysis and write JSON
python shape_image.py input.jpg > %TEMP%\c4c.json

:: Use JSON to perform inversion
python invert_image.py %TEMP%\c4c.json

:: Build new filename with _inverted suffix
:: Launch and auto-close in IrfanView
```

---

## 📝 Notes

- The script currently supports **one file at a time**.  
- Batch processing of multiple files via SendTo is not yet implemented.
- IrfanView is closed cleanly using its `/killmesoftly` switch — no `taskkill` used.

---

## 🔄 Planned Enhancements

- [ ] Add support for processing **multiple images** at once.
- [ ] Make paths configurable via environment variables or a config file.
- [ ] Add error handling for missing dependencies or scripts.

---

## 📬 Questions or Suggestions?

Feel free to open an issue or contribute improvements if you’re using this in your own film scanning workflow.
