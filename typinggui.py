import os
import random
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from pydub import AudioSegment
from pydub.effects import speedup

# --- Original Audio Logic ---
def distort_clip(base_clip, semitone_shift=0):
    new_sample_rate = int(base_clip.frame_rate * (2.0 ** (semitone_shift / 12.0)))
    distorted = base_clip._spawn(base_clip.raw_data, overrides={'frame_rate': new_sample_rate})
    return distorted.set_frame_rate(44100)

def load_clips(category=None):
    base_path = "sounds"
    clips = []

    if category:
        folder = os.path.join(base_path, category)
        if not os.path.isdir(folder):
            raise FileNotFoundError(f"Category folder not found: {folder}")
        clips = [AudioSegment.from_wav(os.path.join(folder, f))
                 for f in os.listdir(folder) if f.endswith(".wav")]
    else:
        for subfolder in os.listdir(base_path):
            full_path = os.path.join(base_path, subfolder)
            if os.path.isdir(full_path):
                for f in os.listdir(full_path):
                    if f.endswith(".wav"):
                        clips.append(AudioSegment.from_wav(os.path.join(full_path, f)))

    if not clips:
        raise RuntimeError("No sound clips found!")
    return clips

def generate_talk_audio(text, clips, semitone_shift=0, speed=1.2):
    output = AudioSegment.silent(duration=0)

    for char in text:
        if char.isalnum():
            clip = random.choice(clips)
            pitch_variation = random.uniform(-0.5, 0.5)
            glitched = distort_clip(clip, semitone_shift + pitch_variation)
            pause = random.randint(25, 45)
            output += glitched + AudioSegment.silent(duration=pause)

    return speedup(output, playback_speed=speed)

def get_sound_categories():
    base_path = "sounds"
    if not os.path.exists(base_path):
        return []
    folders = [name for name in os.listdir(base_path)
               if os.path.isdir(os.path.join(base_path, name))]
    return ["mixed"] + folders  # Add "mixed" at the top
    

# --- GUI Logic ---
def generate_voice():
    text = text_entry.get("1.0", tk.END).strip()
    category = selected_category.get().strip()
    try:
        pitch = float(pitch_entry.get())
        speed = float(speed_entry.get())
    except ValueError:
        messagebox.showerror("Invalid Input", "Pitch and speed must be numbers.")
        return
    output_path = output_entry.get().strip()

    try:
        clips = load_clips(None if category == "mixed" else category)
        final_audio = generate_talk_audio(text, clips, pitch, speed)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        final_audio.export(output_path, format="ogg")
        messagebox.showinfo("Success", f"Saved to {output_path}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# --- Build GUI ---
root = tk.Tk()
root.title("Undertale Dialogue Voice Generator")

frame = ttk.Frame(root, padding=15)
frame.grid(row=0, column=0)
categories = get_sound_categories()
selected_category = tk.StringVar()
selected_category.set(categories[0] if categories else "")

# Text input
ttk.Label(frame, text="Text:").grid(row=0, column=0, sticky="w")
text_entry = tk.Text(frame, width=40, height=4)
text_entry.grid(row=0, column=1, pady=5)

# Category
ttk.Label(frame, text="Category (folder):").grid(row=1, column=0, sticky="w")
category_dropdown = ttk.Combobox(frame, textvariable=selected_category, values=categories, state="readonly")
category_dropdown.grid(row=1, column=1, pady=5)

# Pitch
ttk.Label(frame, text="Pitch (semitones):").grid(row=2, column=0, sticky="w")
pitch_entry = ttk.Entry(frame, width=30)
pitch_entry.insert(0, "0")
pitch_entry.grid(row=2, column=1, pady=5)

# Speed
ttk.Label(frame, text="Speed multiplier:").grid(row=3, column=0, sticky="w")
speed_entry = ttk.Entry(frame, width=30)
speed_entry.insert(0, "1.2")
speed_entry.grid(row=3, column=1, pady=5)

# Output path
ttk.Label(frame, text="Output filename:").grid(row=4, column=0, sticky="w")
output_entry = ttk.Entry(frame, width=30)
output_entry.insert(0, "outputs/typingvoice.ogg")
output_entry.grid(row=4, column=1, pady=5)

# Generate button
generate_btn = ttk.Button(frame, text="Generate Voice", command=generate_voice)
generate_btn.grid(row=5, column=1, pady=10, sticky="e")

root.mainloop()
