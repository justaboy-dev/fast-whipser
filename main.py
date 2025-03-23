from faster_whisper import WhisperModel
import sys
import logging
import os
from tqdm import tqdm
import time
import torch
import subprocess

# Thiết lập logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def limit_gpu_usage(percentage=50):
    """
    Giới hạn sử dụng GPU
    
    Args:
        percentage: Phần trăm GPU tối đa được sử dụng (0-100)
    """
    try:
        # Kiểm tra xem có GPU NVIDIA không
        if not torch.cuda.is_available():
            logging.warning("Không tìm thấy GPU NVIDIA")
            return False
            
        # Lấy số GPU có sẵn
        gpu_count = torch.cuda.device_count()
        if gpu_count == 0:
            logging.warning("Không tìm thấy GPU NVIDIA")
            return False
            
        # Tính toán số GPU cores được phép sử dụng
        allowed_cores = max(1, int(gpu_count * percentage / 100))
        
        # Chọn GPU cores để sử dụng
        selected_gpus = list(range(allowed_cores))
        
        # Thiết lập CUDA_VISIBLE_DEVICES
        os.environ['CUDA_VISIBLE_DEVICES'] = ','.join(map(str, selected_gpus))
        
        # Lấy tên GPU
        gpu_name = torch.cuda.get_device_name(0)
        logging.info(f"Đã tìm thấy GPU: {gpu_name}")
        
        try:
            # Giới hạn bộ nhớ GPU cho process hiện tại
            memory_fraction = percentage / 100.0
            torch.cuda.set_per_process_memory_fraction(memory_fraction, 0)
            
            # Lấy thông tin về bộ nhớ GPU
            total_memory = torch.cuda.get_device_properties(0).total_memory
            allocated_memory = torch.cuda.memory_allocated(0)
            reserved_memory = torch.cuda.memory_reserved(0)
            
            logging.info(f"Đã giới hạn GPU ở mức {percentage}%")
            logging.info(f"Bộ nhớ GPU:")
            logging.info(f"- Tổng bộ nhớ: {total_memory / 1024**3:.2f} GB")
            logging.info(f"- Đã cấp phát: {allocated_memory / 1024**3:.2f} GB")
            logging.info(f"- Đã dành riêng: {reserved_memory / 1024**3:.2f} GB")
            
        except Exception as e:
            logging.warning(f"Lỗi khi giới hạn GPU: {str(e)}")
            return False
                
        return True
    except Exception as e:
        logging.warning(f"Lỗi khi giới hạn GPU: {str(e)}")
        return False

def get_audio_duration(audio_path):
    """
    Lấy độ dài của file âm thanh
    """
    try:
        import ffmpeg
        
        # Đường dẫn đến ffmpeg và ffprobe
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
        
        # Tìm ffmpeg và ffprobe
        ffmpeg_path = None
        ffprobe_path = None
        
        for path in FFMPEG_PATHS:
            if os.path.exists(path):
                ffmpeg_path = path
                logging.info(f"Đã tìm thấy ffmpeg tại: {path}")
                break
            elif path == "ffmpeg":
                try:
                    subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
                    ffmpeg_path = path
                    logging.info("Đã tìm thấy ffmpeg trong PATH")
                    break
                except:
                    continue
                    
        for path in FFPROBE_PATHS:
            if os.path.exists(path):
                ffprobe_path = path
                logging.info(f"Đã tìm thấy ffprobe tại: {path}")
                break
            elif path == "ffprobe":
                try:
                    subprocess.run(['ffprobe', '-version'], capture_output=True, check=True)
                    ffprobe_path = path
                    logging.info("Đã tìm thấy ffprobe trong PATH")
                    break
                except:
                    continue
        
        if not ffmpeg_path or not ffprobe_path:
            logging.error("Không tìm thấy ffmpeg hoặc ffprobe")
            return None
            
        # Lấy thông tin về file âm thanh
        probe = ffmpeg.probe(audio_path, cmd=ffprobe_path)
        duration = float(probe['streams'][0]['duration'])
        logging.info(f"Độ dài file âm thanh: {duration:.2f} giây")
        return duration
        
    except Exception as e:
        logging.error(f"Lỗi khi lấy độ dài file âm thanh: {str(e)}")
        logging.error(f"Chi tiết lỗi: {type(e).__name__}")
        return None

def transcribe_audio(audio_path, output_path=None, min_segment_length=0.5, max_segment_length=30.0, gpu_percentage=50):
    """
    Transcribe audio file và bỏ qua các đoạn không có giọng nói
    
    Args:
        audio_path: Đường dẫn đến file âm thanh
        output_path: Đường dẫn file output (tùy chọn)
        min_segment_length: Độ dài tối thiểu của đoạn (giây)
        max_segment_length: Độ dài tối đa của đoạn (giây)
        gpu_percentage: Phần trăm GPU tối đa được sử dụng (0-100)
    """
    # Giới hạn sử dụng GPU
    limit_gpu_usage(gpu_percentage)
    
    # Lấy độ dài file âm thanh
    duration = get_audio_duration(audio_path)
    if duration is None:
        logging.warning("Không thể lấy độ dài file âm thanh, sẽ không hiển thị tiến độ chính xác")
        duration = 0
    
    # Khởi tạo model Whisper (sử dụng model "large-v3" cho kết quả tốt nhất với tiếng Việt)
    logging.info("Đang khởi tạo model Whisper...")
    model = WhisperModel("large-v3", device="cuda", compute_type="float16")
    
    # Thực hiện transcribe
    logging.info("Bắt đầu quá trình transcribe...")
    segments, info = model.transcribe(audio_path, language="vi", beam_size=5)
    
    # In thông tin về ngôn ngữ được phát hiện
    logging.info(f"Detected language: {info.language} (probability: {info.language_probability:.2f})")
    
    # Tạo thanh tiến độ
    pbar = tqdm(total=duration, unit="s", desc="Transcribing")
    last_time = 0
    
    # Xử lý kết quả
    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            for segment in segments:
                # Cập nhật tiến độ
                current_time = segment.end
                pbar.update(current_time - last_time)
                last_time = current_time
                
                # Kiểm tra độ dài đoạn và nội dung
                segment_length = segment.end - segment.start
                text = segment.text.strip()
                
                # Bỏ qua nếu:
                # 1. Đoạn quá ngắn (có thể là tiếng ồn)
                # 2. Đoạn quá dài (có thể là đoạn im lặng)
                # 3. Không có nội dung hoặc chỉ có ký tự đặc biệt
                if (segment_length < min_segment_length or 
                    segment_length > max_segment_length or 
                    not text or 
                    text.isspace() or 
                    all(not c.isalnum() for c in text)):
                    logging.debug(f"Bỏ qua đoạn: [{segment.start:.2f}s -> {segment.end:.2f}s] {text}")
                    continue
                
                f.write(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {text}\n")
        pbar.close()
        logging.info(f"Transcript đã được lưu vào file: {output_path}")
    else:
        # In kết quả ra màn hình
        for segment in segments:
            # Cập nhật tiến độ
            current_time = segment.end
            pbar.update(current_time - last_time)
            last_time = current_time
            
            # Kiểm tra độ dài đoạn và nội dung
            segment_length = segment.end - segment.start
            text = segment.text.strip()
            
            # Bỏ qua nếu:
            # 1. Đoạn quá ngắn (có thể là tiếng ồn)
            # 2. Đoạn quá dài (có thể là đoạn im lặng)
            # 3. Không có nội dung hoặc chỉ có ký tự đặc biệt
            if (segment_length < min_segment_length or 
                segment_length > max_segment_length or 
                not text or 
                text.isspace() or 
                all(not c.isalnum() for c in text)):
                logging.debug(f"Bỏ qua đoạn: [{segment.start:.2f}s -> {segment.end:.2f}s] {text}")
                continue
            
            logging.info(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {text}")
        pbar.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        logging.error("Cách sử dụng: python main.py <đường_dẫn_file_âm_thanh> [đường_dẫn_file_output]")
        sys.exit(1)
    
    audio_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    transcribe_audio(audio_path, output_path, gpu_percentage=50) 