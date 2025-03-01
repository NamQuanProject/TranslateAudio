import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import os
import streamlit as st
import time  # For simulating real-time progress updates



@st.cache_resource
def load_model():
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

    model_id = "openai/whisper-small"

    st.write("📥 **Loading model...** (This may take some time ⏳)")
    
    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
    )
    model.to(device)

    processor = AutoProcessor.from_pretrained(model_id)

    return model, processor, device, torch_dtype




def translate(folder_name):
    model, processor, device, torch_dtype = load_model()
    pipe = pipeline(
        "automatic-speech-recognition",
        model=model,
        tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor,
        torch_dtype=torch_dtype,
        device=device,
    )

    files = [file for file in os.listdir(folder_name) if file.endswith(".mp3")]
    total_files = len(files)

    if total_files == 0:
        st.warning("⚠️ No MP3 files found in the folder.")
        return

    progress_bar = st.progress(0)
    status_text = st.empty()

    st.write("🔄 **Translating audio files...**")

    for idx, file in enumerate(files):
        file_path = os.path.join(folder_name, file)
        output_txt_path = os.path.join(folder_name, f"{os.path.splitext(file)[0]}.txt")  # Save without .mp3 in filename

        try:
            result = pipe(file_path)
            with open(output_txt_path, "w", encoding="utf-8") as f:  # Overwrite instead of append
                f.write(result["text"])

            # Update progress
            progress = (idx + 1) / total_files
            progress_bar.progress(progress)
            status_text.text(f"✅ Processed {idx + 1}/{total_files}: `{file}`")

        except Exception as e:
            st.error(f"❌ Error processing `{file}`: {e}")

        time.sleep(0.5)  # Artificial delay for smoother updates

    st.success("🎉 **All files have been transcribed successfully!**")
