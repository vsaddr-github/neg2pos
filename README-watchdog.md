# 🖼️ watch_and_invert.py — Real-Time Folder Watcher for Film Inversion

A utility by **Vlad's Test Target** for automating film scan inversion using a camera scanning workflow.  
This script watches a folder in real time and processes each new or renamed `.jpg` or `.png` file by analyzing it, inverting it, and briefly displaying the result in IrfanView.

---

## 🔧 Features

- 🕵️ Watches for new or renamed image files in the specified folder
- 🧠 Skips:
  - Files with `_inverted` in the name
  - Already processed files (output exists)
  - Empty or incomplete files
- 🛠️ Executes two Python scripts:
  - `shape_image.py` — metadata extraction
  - `invert_image.py` — actual inversion
- 📷 Opens result in IrfanView for a 5-second preview
- 🧭 Gracefully shuts down on Ctrl+C
- 🤫 Minimal console output by default (controlled with a `VERBOSE` flag)

---

## 🛠 Requirements

- Python 3.x
- [`watchdog`](https://pypi.org/project/watchdog/)
- Google Cloud SDK (or another Python environment)
- IrfanView installed
- Custom scripts:
  - `shape_image.py`
  - `invert_image.py`

---

## 🚀 Usage

Run the script from the command line with the folder to watch:

```bash
python watch_and_invert.py "D:\Scans\ToProcess"
```

It will continuously watch for `.jpg` and `.png` files added or renamed into the folder.

---

## ⚙️ Configuration

Edit the top of the script to set your paths:

```python
PYTHON_EXE = r"C:\Program Files (x86)\Google\Cloud SDK\..."
SHAPE_SCRIPT = r"D:\GitHub\neg2pos\shape_image.py"
INVERT_SCRIPT = r"D:\GitHub\neg2pos\invert_image.py"
IRFANVIEW_EXE = r"C:\Program Files\IrfanView\i_view64.exe"
```

To enable verbose logging:

```python
VERBOSE = True
```

Errors are always printed to `stderr`, even when `VERBOSE` is `False`.

---

## 🧰 Install Watchdog

To install `watchdog` with Google Cloud SDK Python:

```bash
"C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\platform\bundledpython\python.exe" -m pip install watchdog
```

---

## 📝 Notes

- Files are only processed once writing is complete (2-second delay).
- IrfanView auto-closes after each preview using `/killmesoftly`.
- Error messages (e.g., file read issues, script failures) are clearly printed to `stderr`.

---

## 🧷 Attribution

Developed and maintained by **Vlad's Test Target**  
For professional scanning tools and tips, visit [film4ever.info/vtt](https://film4ever.info/vtt)
