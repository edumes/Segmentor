import os
import subprocess
import logging
from platform_utils import platform_detector, get_platform_config, is_apple_silicon, is_macos

# Configurar logging para substituir messagebox
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def extract_segment(input_video, output_path, start_time, end_time, vertical=False):
    """Extrai segmento de vídeo com otimizações específicas da plataforma"""
    try:
        config = get_platform_config()
        
        # Construir comando FFmpeg otimizado para a plataforma
        ffmpeg_cmd = platform_detector.get_ffmpeg_base_args()
        
        # Adicionar parâmetros de entrada
        ffmpeg_cmd.extend([
            '-ss', str(start_time),
            '-i', input_video,
            '-to', str(end_time - start_time)
        ])
        
        # Adicionar configurações de codificação otimizadas
        encoding_args = platform_detector.get_encoding_args(vertical)
        ffmpeg_cmd.extend(encoding_args)
        
        # Adicionar otimizações de memória específicas da plataforma
        memory_opts = config.memory_optimization
        if memory_opts.get('buffer_size'):
            ffmpeg_cmd.extend(['-bufsize', memory_opts['buffer_size']])
        if memory_opts.get('max_muxing_queue_size'):
            ffmpeg_cmd.extend(['-max_muxing_queue_size', str(memory_opts['max_muxing_queue_size'])])
        if memory_opts.get('thread_queue_size'):
            ffmpeg_cmd.extend(['-thread_queue_size', str(memory_opts['thread_queue_size'])])
        
        # Configurações específicas do Apple Silicon
        if is_apple_silicon():
            # Usar otimizações específicas do VideoToolbox
            ffmpeg_cmd.extend([
                '-pix_fmt', 'yuv420p',
                '-color_primaries', 'bt709',
                '-color_trc', 'bt709',
                '-colorspace', 'bt709'
            ])
        
        # Adicionar parâmetros finais
        ffmpeg_cmd.extend(['-y', output_path])
        
        # Executar comando com timeout apropriado
        timeout = 300 if not is_apple_silicon() else 180  # Apple Silicon é mais rápido
        
        print(f"Executando: {' '.join(ffmpeg_cmd)}")
        result = subprocess.run(
            ffmpeg_cmd, 
            check=True, 
            timeout=timeout,
            capture_output=True,
            text=True
        )
        
        return True

    except subprocess.TimeoutExpired:
        print(f"Timeout ao processar segmento: {output_path}")
        return False
    except subprocess.CalledProcessError as e:
        print(f"Erro no FFmpeg: {e}")
        if e.stderr:
            print(f"Stderr: {e.stderr}")
        return False
    except Exception as e:
        print(f"Erro inesperado: {e}")
        return False

def extract_segments(input_video, selected_times_default, selected_times_vertical):
    try:
        video_name = os.path.splitext(os.path.basename(input_video))[0]
        output_folder = os.path.join(os.path.dirname(input_video), video_name)
        os.makedirs(output_folder, exist_ok=True)

        all_segments = set(selected_times_default + selected_times_vertical)

        for minute in all_segments:
            start_time = minute * 60
            end_time = (minute + 1) * 60

            if minute in selected_times_default:
                output_path = os.path.join(output_folder, f"{video_name}_segment_{minute+1}_default.mp4")
                if not extract_segment(input_video, output_path, start_time, end_time):
                    raise RuntimeError(f"Failed on default segment {minute+1}")

            if minute in selected_times_vertical:
                output_path = os.path.join(output_folder, f"{video_name}_segment_{minute+1}_vertical.mp4")
                if not extract_segment(input_video, output_path, start_time, end_time, vertical=True):
                    raise RuntimeError(f"Failed on vertical segment {minute+1}")

        logging.info(f"Segments saved in folder: {output_folder}")
        return True

    except Exception as e:
        logging.error(f"Error processing video: {str(e)}")
        return False