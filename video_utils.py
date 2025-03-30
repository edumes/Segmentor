# video_utils.py

import os
from moviepy.editor import VideoFileClip
from moviepy.video.fx.all import resize, colorx, lum_contrast
from tkinter import messagebox

def verticalize_clip(clip, start_time, end_time):
    # Função para ajustar o clipe para o formato vertical 9:16 e redimensioná-lo para 1080x1920
    width, height = clip.size
    target_width = int((9 / 16) * height)
    x_offset = (width - target_width) // 2

    cropped_clip = clip.subclip(start_time, end_time).crop(x1=x_offset, y1=0, x2=x_offset + target_width, y2=height)
    return resize(cropped_clip, newsize=(1080, 1920))

def extract_segments(input_video, selected_times_default, selected_times_vertical):
    try:
        # Carregar o vídeo original
        video_clip = VideoFileClip(input_video)

        # Criar uma pasta para salvar os segmentos, com o nome do vídeo original (sem extensão)
        video_name = os.path.splitext(os.path.basename(input_video))[0]
        output_folder = os.path.join(os.path.dirname(input_video), video_name)
        os.makedirs(output_folder, exist_ok=True)

        # Processar segmentos no formato default
        for minute in selected_times_default:
            try:
                start_time = minute * 60
                end_time = (minute + 1) * 60 if (minute + 1) * 60 < video_clip.duration else video_clip.duration
                
                # Criar o clipe no formato original
                segment_clip = video_clip.subclip(start_time, end_time)
                
                # Nome do arquivo de saída para cada segmento
                output_video_path = os.path.join(output_folder, f"{video_name}_segment_{minute + 1}_default.mp4")
                segment_clip.write_videofile(
                    output_video_path,
                    ffmpeg_params=["-vcodec", "h264_nvenc"],
                )
                
                segment_clip.close()

            except Exception as e:
                print(f"Erro no segmento default {minute + 1}: {e}")

        # Processar segmentos no formato vertical
        for minute in selected_times_vertical:
            try:
                start_time = minute * 60
                end_time = (minute + 1) * 60 if (minute + 1) * 60 < video_clip.duration else video_clip.duration
                
                # Criar o clipe verticalizado
                vertical_clip = verticalize_clip(video_clip, start_time, end_time)
                
                # Nome do arquivo de saída para cada segmento
                output_video_path = os.path.join(output_folder, f"{video_name}_segment_{minute + 1}_vertical.mp4")
                vertical_clip.write_videofile(
                    output_video_path,
                    ffmpeg_params=["-vcodec", "h264_nvenc"],
                )
                
                vertical_clip.close()

            except Exception as e:
                print(f"Erro no segmento vertical {minute + 1}: {e}")

        video_clip.close()
        messagebox.showinfo("Sucesso", f"Segmentos salvos na pasta: {output_folder}")

    except Exception as e:
        print(e)
        messagebox.showerror("Erro", f"Erro ao extrair e salvar segmentos: {str(e)}")
