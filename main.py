import streamlit as st
import tempfile
import os
from cut import handle_cut
from translate import translate
from combine import combine
from openai import OpenAI
from dotenv import load_dotenv
import asyncio

try:
    asyncio.get_running_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())


load_dotenv()
st.title("🎙️ Audio Upload & Transcription")
uploaded_file = st.file_uploader("Chọn file audio (MP3, WAV, M4A)", type=["mp3", "wav", "m4a"])

if uploaded_file:
    file_name = uploaded_file.name  # Get original file name
    st.audio(uploaded_file, format="audio/mp3", start_time=0)

    # Save temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
        temp_audio.write(uploaded_file.read())
        temp_audio_path = temp_audio.name  # Temp file path

    st.write(f"📂 **File uploaded:** `{file_name}`")

    # Process: Cut Audio
    output_folder = handle_cut(temp_audio_path)  # Returns the folder with split audio files
    if not output_folder:
        st.error("❌ Lỗi khi cắt audio!")
    else:
        st.success(f"✅ **Audio cut successfully**, saved in: `{output_folder}`")

        # Translate
        translate(output_folder)
        st.success("✅ **Transcription completed.**")

        # Combine all text
        combined_text_path = combine(output_folder)  # Returns the combined text file path
        if combined_text_path:
            st.success("✅ **Transcription merged successfully.**")

            # Read combined text
            with open(combined_text_path, "r", encoding="utf-8") as f:
                combined_text = f.read()

            st.download_button(
                label="📄 **Download Transcription**",
                data=combined_text,
                file_name=f"{file_name}.txt",
                mime="text/plain"
            )

            # Button for translation
            
            st.write("🔄 **Translating... Please wait.**")

            # OpenAI API Call (Replace `API_KEY` with your OpenAI API Key)
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                st.error("❌ **OpenAI API Key not found.**")
                st.stop()
            client = OpenAI(api_key=api_key)
            system_prompt = """ 
            🌟 **Expert Chinese Translator Mode Activated!** 🌟

            Translate Chinese text with **precision and clarity**, ensuring:  

            🔹 **Accurate meaning** - Capture the original intent without distortion.  
            🔹 **Pinyin transcription** - Provide pronunciation for each Chinese sentence.  
            🔹 **Well-structured formatting** - Present translations neatly for readability.  
            🔹 **Natural Vietnamese translation** - Adapt sentences to sound fluent and culturally appropriate.  
            🔹 **Detailed sentence breakdown** – Explain nuances where necessary.  

            Format:  

            **Chinese:** 你好，世界！  
            **Pinyin:** Nǐ hǎo, shìjiè!  
            **Vietnamese:** Xin chào, thế giới!  

            Ensure the translation maintains the **original tone**, whether formal, poetic, or conversational.  
            """

            user_prompt = f"""
            Translate the following Chinese transcription into Vietnamese.
            Also, provide pinyin for each sentence and a detailed word-by-word meaning.

            Return the output in Markdown format like this:
            ---
            ### 📜 **Chinese Transcription**
            ```
            (Original Chinese text)
            ```
            ### 🌍 **Vietnamese Translation**
            ```
            (Vietnamese translation)
            ```
            ### 📝 **Pinyin**
            ```
            (Pinyin)
            ```
            ### 🔍 **Word-by-Word Meaning**
            - **Chinese Word** (*pinyin*) → **Vietnamese Meaning**
            - **Chinese Word** (*pinyin*) → **Vietnamese Meaning**
            ---

            **Text to translate:**
            {combined_text}
            """

            client = OpenAI(api_key=api_key)
            model = 'gpt-4o-mini'
            
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
            )
            translated_text = response.choices[0].message.content

            # Display translation beautifully
            st.markdown(translated_text)

            # Provide a download button for translated text
            st.download_button(
                label="📥 **Download Translated Text**",
                data=translated_text,
                file_name=f"{file_name}_translated.md",
                mime="text/markdown"
            )

        else:
            st.error("❌ **Error merging transcription.**")

    # Clean up temp file
    os.remove(temp_audio_path)
