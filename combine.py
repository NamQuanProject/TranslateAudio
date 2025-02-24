import os
import re

def combine(folder_name):
    output_text = ""

    # List and sort files (numeric order if applicable)
    output_files = sorted(
        os.listdir(folder_name),
        key=lambda x: int(re.findall(r'\d+', x)[0]) if re.findall(r'\d+', x) else x
    )

    text_files = [f for f in output_files if f.endswith(".txt")]

    if not text_files:
        print("⚠️ No text files found to combine!")
        return None

    for file in text_files:
        with open(os.path.join(folder_name, file), "r", encoding="utf-8") as f:
            output_text += f.read().strip() + "\n"  # Ensure clean formatting

    # Save combined text
    output_path = os.path.join(folder_name, "combined_transcription.txt")
    with open(output_path, "w", encoding="utf-8") as write_file:
        write_file.write(output_text.strip())  # Remove leading/trailing spaces

    print(f"✅ Done! Combined text saved to {output_path}")
    return output_path  # Return the path for further use
