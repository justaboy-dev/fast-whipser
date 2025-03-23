# Fast Whisper Transcription

Ứng dụng transcribe âm thanh sử dụng Faster Whisper với các tính năng:
- Transcribe âm thanh sang văn bản với độ chính xác cao
- Tự động phát hiện ngôn ngữ
- Bỏ qua các đoạn không có giọng nói
- Giới hạn sử dụng CPU
- Hiển thị tiến độ xử lý
- Hỗ trợ nhiều định dạng âm thanh (mp3, wav, m4a, etc.)
- Cắt audio theo timestamp từ transcript

## Yêu cầu hệ thống

- Python 3.8 trở lên
- FFmpeg (cần thiết cho xử lý âm thanh)
- Windows/Linux/MacOS

## Cài đặt

1. Cài đặt FFmpeg:
   - Windows: Sử dụng Chocolatey
     ```bash
     choco install ffmpeg
     ```
   - Linux:
     ```bash
     sudo apt update
     sudo apt install ffmpeg
     ```
   - MacOS:
     ```bash
     brew install ffmpeg
     ```

2. Tạo môi trường ảo và kích hoạt:
   ```bash
   # Windows
   python -m venv .venv
   .venv\Scripts\activate

   # Linux/MacOS
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Cài đặt các thư viện cần thiết:
   ```bash
   pip install -r requirements.txt
   ```

## Cách sử dụng

### 1. Transcribe âm thanh

#### Cơ bản
```bash
python main.py audio.mp3 output.txt
```

#### Tùy chọn nâng cao
```python
transcribe_audio(
    audio_path="audio.mp3",
    output_path="output.txt",
    min_segment_length=0.5,  # Độ dài tối thiểu của đoạn (giây)
    max_segment_length=30.0, # Độ dài tối đa của đoạn (giây)
    cpu_percentage=70        # Phần trăm CPU tối đa được sử dụng
)
```

### 2. Cắt audio theo transcript

#### Cơ bản
```bash
python split_audio.py audio.mp3 transcript.txt output_segments
```

#### Tùy chọn nâng cao
```python
split_audio_by_transcript(
    audio_path="audio.mp3",
    transcript_path="transcript.txt",
    output_dir="output_segments",
    output_format="wav"  # Định dạng file output (wav, mp3, etc.)
)
```

### Tham số

#### Transcribe
- `audio_path`: Đường dẫn đến file âm thanh cần transcribe
- `output_path`: Đường dẫn file output (tùy chọn)
- `min_segment_length`: Độ dài tối thiểu của đoạn (mặc định: 0.5 giây)
- `max_segment_length`: Độ dài tối đa của đoạn (mặc định: 30 giây)
- `cpu_percentage`: Phần trăm CPU tối đa được sử dụng (mặc định: 70%)

#### Cắt audio
- `audio_path`: Đường dẫn đến file âm thanh cần cắt
- `transcript_path`: Đường dẫn đến file transcript chứa timestamp
- `output_dir`: Thư mục lưu các file audio đã cắt
- `output_format`: Định dạng file output (mặc định: wav)

## Tính năng

1. **Tự động phát hiện ngôn ngữ**:
   - Hỗ trợ nhiều ngôn ngữ
   - Tự động phát hiện ngôn ngữ trong âm thanh

2. **Lọc đoạn không có giọng nói**:
   - Bỏ qua các đoạn quá ngắn (có thể là tiếng ồn)
   - Bỏ qua các đoạn quá dài (có thể là đoạn im lặng)
   - Bỏ qua các đoạn không có nội dung

3. **Quản lý tài nguyên**:
   - Giới hạn sử dụng CPU
   - Hiển thị tiến độ xử lý
   - Log chi tiết quá trình xử lý

4. **Định dạng output**:
   ```
   [0.00s -> 2.50s] Nội dung đoạn 1
   [2.50s -> 5.00s] Nội dung đoạn 2
   ...
   ```

5. **Cắt audio thông minh**:
   - Cắt audio theo timestamp từ transcript
   - Tự động tạo tên file theo thứ tự
   - Tạo file CSV chứa thông tin chi tiết về các đoạn
   - Hỗ trợ nhiều định dạng output (wav, mp3, etc.)

## Xử lý lỗi

Nếu gặp lỗi "ffmpeg not found":
1. Kiểm tra FFmpeg đã được cài đặt chưa:
   ```bash
   ffmpeg -version
   ```
2. Nếu chưa cài đặt, cài đặt FFmpeg theo hướng dẫn ở trên
3. Nếu đã cài đặt, kiểm tra đường dẫn FFmpeg trong PATH

## Ghi chú

- Sử dụng model "large-v3" cho kết quả tốt nhất với tiếng Việt
- Có thể điều chỉnh các tham số để tối ưu kết quả theo nhu cầu
- File output sẽ được lưu dưới dạng UTF-8
- Khi cắt audio, mỗi đoạn sẽ được lưu thành một file riêng biệt
- File CSV chứa thông tin chi tiết về thời gian và nội dung của mỗi đoạn

# Fast Whisper - Transcribe Tiếng Việt

Công cụ sử dụng Fast Whisper để chuyển đổi âm thanh tiếng Việt thành văn bản.

## Cài đặt

1. Cài đặt các thư viện cần thiết:
```bash
pip install -r requirements.txt
```

## Cách sử dụng

Chạy script với một trong hai cách sau:

1. In kết quả ra màn hình:
```bash
python main.py <đường_dẫn_file_âm_thanh>
```

2. Lưu kết quả vào file:
```bash
python main.py <đường_dẫn_file_âm_thanh> <đường_dẫn_file_output>
```

Ví dụ:
```bash
python main.py audio.mp3 transcript.txt
```

## Lưu ý

- Hỗ trợ các định dạng âm thanh phổ biến: mp3, wav, m4a, flac,...
- Sử dụng model "large-v3" cho kết quả tốt nhất với tiếng Việt
- Kết quả sẽ bao gồm timestamp cho mỗi đoạn văn bản 



python main.py audio.wav transcript.txt

python split_audio.py audio.wav transcript.txt output_segments