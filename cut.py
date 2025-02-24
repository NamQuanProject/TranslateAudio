from pydub import AudioSegment
import os

def handle_cut(file_name):
    # Đọc file audio
    audio = AudioSegment.from_mp3(file_name)

    # Tạo thư mục lưu các đoạn cắt
    folder = os.path.splitext(file_name)[0]  # Tránh lỗi với tên file có nhiều dấu chấm
    os.makedirs(folder, exist_ok=True)

    # Cắt audio thành đoạn 30 giây
    chunk_length = 25 * 1000  # 30 giây (milliseconds)
    for i, start in enumerate(range(0, len(audio), chunk_length)):
        chunk = audio[start:start + chunk_length]
        save_path = os.path.join(folder, f"output_{i:03d}.mp3")
        chunk.export(save_path, format="mp3")
    
    return folder  # Trả về đường dẫn thư mục chứa các file cắt
