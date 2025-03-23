import os
import csv
import logging
import ffmpeg
from datetime import datetime
import argparse
import sys
import subprocess

# Thiết lập logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def find_ffmpeg():
    """
    Tìm đường dẫn đến ffmpeg và ffprobe
    """
    FFMPEG_PATHS = [
        "C:\\ProgramData\\chocolatey\\bin\\ffmpeg.exe",
        "C:\\ffmpeg\\bin\\ffmpeg.exe",
        "C:\\Program Files\\ffmpeg\\bin\\ffmpeg.exe",
        "ffmpeg"  # Thử tìm trong PATH
    ]
    
    FFPROBE_PATHS = [
        "C:\\ProgramData\\chocolatey\\bin\\ffprobe.exe",
        "C:\\ffmpeg\\bin\\ffprobe.exe",
        "C:\\Program Files\\ffmpeg\\bin\\ffprobe.exe",
        "ffprobe"  # Thử tìm trong PATH
    ]
    
    # Tìm ffmpeg
    for path in FFMPEG_PATHS:
        if os.path.exists(path):
            logging.info(f"Đã tìm thấy ffmpeg tại: {path}")
            return path
        elif path == "ffmpeg":  # Nếu là lệnh ffmpeg
            try:
                subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
                logging.info("Đã tìm thấy ffmpeg trong PATH")
                return path
            except:
                continue
    
    logging.error("Không tìm thấy ffmpeg ở bất kỳ vị trí nào")
    return None

def parse_timestamp(timestamp_str):
    """
    Chuyển đổi timestamp từ định dạng [start -> end] sang số giây
    """
    try:
        # Loại bỏ dấu ngoặc vuông và khoảng trắng
        timestamp_str = timestamp_str.strip('[]').strip()
        # Tách thời gian bắt đầu và kết thúc
        start, end = timestamp_str.split('->')
        # Chuyển đổi sang số giây
        start_seconds = float(start.strip().replace('s', ''))
        end_seconds = float(end.strip().replace('s', ''))
        return start_seconds, end_seconds
    except Exception as e:
        logging.error(f"Lỗi khi phân tích timestamp '{timestamp_str}': {str(e)}")
        return None, None

def split_audio_by_transcript(audio_path, transcript_path, output_dir, output_format="wav"):
    """
    Cắt file âm thanh theo timestamp từ file transcript
    
    Args:
        audio_path: Đường dẫn đến file âm thanh
        transcript_path: Đường dẫn đến file transcript
        output_dir: Thư mục lưu các file audio đã cắt
        output_format: Định dạng file output (wav, mp3, etc.)
    """
    # Kiểm tra file âm thanh và transcript có tồn tại không
    if not os.path.exists(audio_path):
        logging.error(f"Không tìm thấy file âm thanh: {audio_path}")
        return
    if not os.path.exists(transcript_path):
        logging.error(f"Không tìm thấy file transcript: {transcript_path}")
        return
        
    # Tạo thư mục output nếu chưa tồn tại
    os.makedirs(output_dir, exist_ok=True)
    
    # Tìm ffmpeg
    ffmpeg_path = find_ffmpeg()
    if not ffmpeg_path:
        return
        
    # Đọc file transcript
    segments = []
    with open(transcript_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
                
            # Tìm timestamp trong dòng
            start_idx = line.find('[')
            end_idx = line.find(']')
            if start_idx == -1 or end_idx == -1:
                continue
                
            timestamp_str = line[start_idx:end_idx + 1]
            text = line[end_idx + 1:].strip()
            
            # Phân tích timestamp
            start_time, end_time = parse_timestamp(timestamp_str)
            if start_time is None or end_time is None:
                continue
                
            segments.append({
                'start': start_time,
                'end': end_time,
                'text': text
            })
    
    if not segments:
        logging.error("Không tìm thấy timestamp hợp lệ trong file transcript")
        return
        
    # Cắt audio theo từng đoạn
    for i, segment in enumerate(segments, 1):
        output_file = os.path.join(output_dir, f"audio_{i:03d}.{output_format}")
        duration = segment['end'] - segment['start']
        
        try:
            # Sử dụng ffmpeg-python để cắt audio
            stream = ffmpeg.input(audio_path, ss=segment['start'], t=duration)
            stream = ffmpeg.output(stream, output_file, acodec='pcm_s16le' if output_format == 'wav' else 'libmp3lame')
            ffmpeg.run(stream, cmd=ffmpeg_path, capture_stdout=True, capture_stderr=True)
            
            logging.info(f"Đã cắt đoạn {i}: {output_file} ({duration:.2f}s)")
            
        except ffmpeg.Error as e:
            logging.error(f"Lỗi khi cắt đoạn {i}: {str(e)}")
            continue
    
    # Tạo file CSV chứa thông tin chi tiết
    csv_file = os.path.join(output_dir, "segments_info.csv")
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['File', 'Start Time', 'End Time', 'Duration', 'Text'])
        for i, segment in enumerate(segments, 1):
            writer.writerow([
                f"audio_{i:03d}.{output_format}",
                f"{segment['start']:.2f}s",
                f"{segment['end']:.2f}s",
                f"{segment['end'] - segment['start']:.2f}s",
                segment['text']
            ])
    
    logging.info(f"Đã tạo file CSV: {csv_file}")

def main():
    try:
        parser = argparse.ArgumentParser(description="Cắt file âm thanh thành các đoạn nhỏ dựa trên file transcript")
        parser.add_argument("audio_path", help="Đường dẫn đến file âm thanh")
        parser.add_argument("transcript_path", help="Đường dẫn đến file transcript")
        parser.add_argument("output_dir", help="Thư mục lưu các đoạn âm thanh đã cắt")
        
        args = parser.parse_args()
        
        split_audio_by_transcript(args.audio_path, args.transcript_path, args.output_dir)
        
    except Exception as e:
        logging.error(f"Lỗi chương trình: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 