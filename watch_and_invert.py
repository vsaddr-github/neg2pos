import time
import sys
import subprocess
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# === Validate and parse command-line argument ===
if len(sys.argv) < 2:
    print("[ERROR] Usage: python watch_and_invert.py <folder_to_watch>", file=sys.stderr)
    sys.exit(1)

WATCH_FOLDER = Path(sys.argv[1])

if not WATCH_FOLDER.exists() or not WATCH_FOLDER.is_dir():
    print(f"[ERROR] The specified folder does not exist: {WATCH_FOLDER}", file=sys.stderr)
    sys.exit(1)

# === Configuration for tools ===
PYTHON_EXE = r"C:\\Program Files (x86)\\Google\\Cloud SDK\\google-cloud-sdk\\platform\\bundledpython\\python.exe"
SHAPE_SCRIPT = r"D:\\GitHub\\neg2pos\\shape_image.py"
INVERT_SCRIPT = r"D:\\GitHub\\neg2pos\\invert_image.py"
IRFANVIEW_EXE = r"C:\\Program Files\\IrfanView\\i_view64.exe"

# === Output control ===
VERBOSE = False  # Set to True to enable detailed logging

# Define the event handler for new files
class InvertHandler(FileSystemEventHandler):
    def on_created(self, event):
        self.process(Path(event.src_path))

    def on_moved(self, event):
        self.process(Path(event.dest_path))

    def process(self, file_path):
        if file_path.is_dir():
            return

        time.sleep(2)

        if not file_path.exists() or file_path.stat().st_size == 0:
            if VERBOSE:
                print(f"[WARNING] Skipped (file not ready): {file_path.name}")
            return

        if file_path.suffix.lower() not in [".jpg", ".png"]:
            return

        if "_inverted" in file_path.stem:
            if VERBOSE:
                print(f"[INFO] Skipped (already inverted): {file_path.name}")
            return

        inverted_path = file_path.with_name(file_path.stem + "_inverted.png")

        if inverted_path.exists():
            if VERBOSE:
                print(f"[INFO] Skipped (output exists): {inverted_path.name}")
            return

        if VERBOSE:
            print(f"[INFO] Processing: {file_path.name}")

        try:
            json_temp = Path.cwd() / "c4c.json"
            if VERBOSE:
                print(f"[INFO] Running: {PYTHON_EXE} {SHAPE_SCRIPT} \"{file_path.resolve()}\"")
            with open(json_temp, "w") as json_out:
                subprocess.run([PYTHON_EXE, SHAPE_SCRIPT, str(file_path)], stdout=json_out, check=True)

            subprocess.run([PYTHON_EXE, INVERT_SCRIPT, str(json_temp)], check=True)

            subprocess.Popen([IRFANVIEW_EXE, str(inverted_path)])
            time.sleep(5)
            subprocess.run([IRFANVIEW_EXE, "/killmesoftly"])

        except Exception as e:
            print(f"[ERROR] Failed to process {file_path.name}: {e}", file=sys.stderr)

# Entry point of the script
if __name__ == "__main__":
    if VERBOSE:
        print(f"[INFO] Watching folder: {WATCH_FOLDER}")

    event_handler = InvertHandler()
    observer = Observer()
    observer.schedule(event_handler, str(WATCH_FOLDER), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
