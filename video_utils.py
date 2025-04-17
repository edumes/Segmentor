import os
import subprocess
from tkinter import messagebox

def extract_segment(input_video, output_path, start_time, end_time, vertical=False):
    try:
        ffmpeg_cmd = [
            'ffmpeg',
            '-hwaccel', 'cuda',
            '-ss', str(start_time),
            '-i', input_video,
            '-to', str(end_time - start_time),
            '-c:v', 'h264_nvenc',
            '-preset', 'p7',
            '-cq', '20',
            '-profile:v', 'high',
            '-rc', 'vbr_hq',
            '-bf', '4',
            '-movflags', '+faststart'
        ]

        if vertical:
            ffmpeg_cmd.extend([
                '-vf', "crop=ih*(9/16):ih:(iw-ih*(9/16))/2:0,scale=1080:1920"
            ])

        ffmpeg_cmd.extend([
            '-c:a', 'aac',
            '-b:a', '128k',
            '-y',
            output_path
        ])

        subprocess.run(ffmpeg_cmd, check=True)
        return True

    except subprocess.CalledProcessError as e:
        print(f"Erro FFmpeg: {e}")
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
                    raise RuntimeError(f"Falha no segmento default {minute+1}")

            if minute in selected_times_vertical:
                output_path = os.path.join(output_folder, f"{video_name}_segment_{minute+1}_vertical.mp4")
                if not extract_segment(input_video, output_path, start_time, end_time, vertical=True):
                    raise RuntimeError(f"Falha no segmento vertical {minute+1}")

        messagebox.showinfo("Sucesso", f"Segmentos salvos na pasta: {output_folder}")
        return True

    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao processar vídeo: {str(e)}")
        return False