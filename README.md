# Fast Whisper Transcription

Ứng dụng chuyển đổi âm thanh thành văn bản sử dụng Whisper, với các tính năng:
- Hỗ trợ tiếng Việt
- Bỏ qua các đoạn không có giọng nói
- Hiển thị tiến độ
- Lưu kết quả vào Google Drive
- Cắt nhỏ file âm thanh theo transcript
- Tạo file CSV chứa thông tin các đoạn

## Cài đặt

### Cách 1: Sử dụng Google Colab (Khuyến nghị)

1. Mở [Google Colab](https://colab.research.google.com/)
2. Upload file `whisper_transcribe.ipynb` vào Google Colab
3. Upload file âm thanh vào Google Drive của bạn
4. Điều chỉnh đường dẫn trong cell cấu hình:
   ```python
   DRIVE_BASE_PATH = '/content/drive/MyDrive'  # Thay đổi nếu cần
   AUDIO_FILE_PATH = os.path.join(DRIVE_BASE_PATH, 'audio.mp3')  # Đường dẫn tới file âm thanh
   OUTPUT_DIR = os.path.join(DRIVE_BASE_PATH, 'whisper_output')  # Thư mục lưu kết quả
   ```
5. Chạy các cell theo thứ tự

### Cách 2: Cài đặt local

1. Clone repository:
   ```bash
   git clone https://github.com/justaboy-dev/fast-whisper.git
   cd fast-whisper
   ```

2. Cài đặt các thư viện cần thiết:
   ```bash
   pip install -r requirements.txt
   ```

3. Cài đặt ffmpeg:
   - Windows: Sử dụng Chocolatey: `choco install ffmpeg`
   - Linux: `sudo apt-get install ffmpeg`
   - macOS: `brew install ffmpeg`

4. Chạy script:
   ```bash
   python main.py audio.mp3 output.txt
   ```

## Cấu trúc thư mục

```
fast-whisper/
├── main.py              # Script chính
├── split_audio.py       # Script cắt file âm thanh
├── whisper_transcribe.ipynb  # Notebook cho Google Colab
├── requirements.txt     # Các thư viện cần thiết
└── README.md           # Tài liệu hướng dẫn
```

## Các tham số

### main.py
- `audio_path`: Đường dẫn đến file âm thanh
- `output_path`: Đường dẫn file output (tùy chọn)
- `min_segment_length`: Độ dài tối thiểu của đoạn (giây)
- `max_segment_length`: Độ dài tối đa của đoạn (giây)

### split_audio.py
- `audio_path`: Đường dẫn đến file âm thanh
- `transcript_path`: Đường dẫn đến file transcript
- `output_dir`: Thư mục lưu các file âm thanh đã cắt
- `min_segment_length`: Độ dài tối thiểu của đoạn (giây)
- `max_segment_length`: Độ dài tối đa của đoạn (giây)

## Kết quả

### Khi chạy main.py
- File transcript chứa nội dung đã chuyển đổi
- Mỗi dòng có định dạng: `[start_time -> end_time] text`

### Khi chạy split_audio.py
- Thư mục `segments/` chứa các file âm thanh đã cắt
- File `segments_info.csv` chứa thông tin chi tiết về các đoạn:
  - segment_id: ID của đoạn
  - start_time: Thời điểm bắt đầu (giây)
  - end_time: Thời điểm kết thúc (giây)
  - duration: Độ dài đoạn (giây)
  - text: Nội dung văn bản
  - audio_file: Tên file âm thanh

## Lưu ý

1. Khi sử dụng Google Colab:
   - Đảm bảo đã kết nối với Google Drive
   - Kiểm tra đường dẫn file âm thanh trong Google Drive
   - Các file kết quả sẽ được lưu trong thư mục `whisper_output` trong Google Drive

2. Khi cài đặt local:
   - Cần cài đặt CUDA và driver NVIDIA mới nhất để sử dụng GPU
   - Đảm bảo ffmpeg đã được cài đặt và có thể truy cập từ command line

## License

Distributed under the MIT License. See `LICENSE` for more information.