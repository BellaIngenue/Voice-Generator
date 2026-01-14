import os
import random
import argparse
from pydub import AudioSegment
from pydub.effects import speedup

# --- Functions ---
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
        print(f"🔊 Loading sounds from: {folder}")
        clips = [AudioSegment.from_wav(os.path.join(folder, f))
                 for f in os.listdir(folder) if f.endswith(".wav")]
    else:
        print("🔀 No category selected — loading all sounds...")
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

# --- Main ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Typing Voice Generator with category-based sounds")
    parser.add_argument("text", help="Text to convert into voice")
    parser.add_argument("--category", default="soft", help="Sound folder to use (inside /sounds/)")
    parser.add_argument("--pitch", type=float, default=0, help="Base pitch shift in semitones")
    parser.add_argument("--speed", type=float, default=1.2, help="Playback speed multiplier")
    parser.add_argument("--output", default="outputs/typingvoice.ogg", help="Output .ogg file name")

    args = parser.parse_args()

    sound_folder = os.path.join("sounds", args.category)
    output_folder = os.path.dirname(args.output)
    os.makedirs(output_folder, exist_ok=True)

    print(f"🔊 Using category: {args.category}")
    print(f"📄 Output will be saved to: {args.output}")

    clips = load_clips(args.category if args.category else None)
    final_audio = generate_talk_audio(args.text, clips, args.pitch, args.speed)
    final_audio.export(args.output, format="ogg")

    print("✅ Done!")
