import json, wave
from pathlib import Path
from difflib import SequenceMatcher
import tkinter as tk
from tkinter import filedialog, messagebox
from vosk import Model, KaldiRecognizer

MODEL_PATH = "vosk-model-small-en-us-0.15"

def browse_file():
    path = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
    file_entry.delete(0, tk.END); file_entry.insert(0, path)

def check():
    expected = expected_entry.get().strip().lower(); path = file_entry.get().strip()
    if not expected: messagebox.showwarning("Warning", "Enter a word or sentence."); return
    if not path or not Path(path).exists(): messagebox.showerror("Error", "Select a valid WAV file."); return
    if not Path(MODEL_PATH).exists(): messagebox.showerror("Error", "Vosk model not found."); return
    try:
        model = Model(MODEL_PATH); recognized = ""
        with wave.open(path, "rb") as audio:
            recognizer = KaldiRecognizer(model, audio.getframerate())
            while True:
                data = audio.readframes(4000)
                if len(data) == 0: break
                if recognizer.AcceptWaveform(data): recognized += " " + json.loads(recognizer.Result()).get("text", "")
            recognized += " " + json.loads(recognizer.FinalResult()).get("text", "")
        recognized = recognized.strip().lower()
        score = SequenceMatcher(None, expected, recognized).ratio() * 100
        output_box.delete("1.0", tk.END)
        output_box.insert(tk.END, f"Expected: {expected}\nRecognized: {recognized}\nScore: {score:.2f}%\n\n")
        feedback = "Excellent pronunciation!" if score >= 90 else "Good pronunciation." if score >= 75 else "Fair pronunciation. Practice more." if score >= 60 else "Needs improvement."
        output_box.insert(tk.END, f"Feedback: {feedback}")
    except Exception as error:
        messagebox.showerror("Error", str(error))

root = tk.Tk(); root.title("Pronunciation Checker"); root.geometry("700x550")
tk.Label(root, text="Pronunciation Checker", font=("Arial", 18, "bold")).pack(pady=10)
tk.Label(root, text="Expected word or sentence:").pack(anchor="w", padx=15)
expected_entry = tk.Entry(root, font=("Arial", 12)); expected_entry.pack(fill="x", padx=15, pady=5)
frame = tk.Frame(root); frame.pack(fill="x", padx=15, pady=5)
tk.Label(frame, text="WAV file:").pack(side="left")
file_entry = tk.Entry(frame); file_entry.pack(side="left", fill="x", expand=True, padx=8)
tk.Button(frame, text="Browse", command=browse_file).pack(side="left")
tk.Button(root, text="Check Pronunciation", command=check, font=("Arial", 12, "bold"), bg="#2563eb", fg="white").pack(pady=10)
output_box = tk.Text(root, height=12, font=("Consolas", 12)); output_box.pack(fill="both", expand=True, padx=15, pady=5)
root.mainloop()
