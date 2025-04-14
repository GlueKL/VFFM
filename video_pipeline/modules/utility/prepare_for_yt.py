import os
import subprocess
import logging
import json
from typing import Dict, Any, List

from video_pipeline.modules.base import BaseModule

logger = logging.getLogger(__name__)

class PrepareForYt(BaseModule):

    
    def __init__(self, params: Dict[str, Any]):

        super().__init__(params)
        
    def process(self, input_path: str, output_path: str):
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Входной файл не найден: {input_path}")
        
        # Получаем информацию о видеопотоках
        streams_info = self._get_streams_info(input_path)
        video_stream_indexes = [s['index'] for s in streams_info.get('streams', []) 
                              if s.get('codec_type') == 'video']
        
        logger.info(f"Обнаружено {len(video_stream_indexes)} видеопотоков: {video_stream_indexes}")
        
        if len(video_stream_indexes) <= 1:
            # Если только один поток, используем простую команду
            cmd = [
                'ffmpeg',
                '-i', input_path,
                '-map', '0:v',
                '-map', '0:a?',
                '-c:v', 'libx264',
                '-profile:v', 'high',
                '-level:v', '4.0',
                '-pix_fmt', 'yuv420p',
                '-crf', '18', 
                '-preset', 'fast',
                '-movflags', '+faststart',
                '-c:a', 'aac',
                '-b:a', '128k',
                '-y',
                output_path
            ]
        else:
            # Создаем filter_complex для объединения всех потоков
            filter_parts = []
            
            # Строим filter_complex
            if len(video_stream_indexes) > 1:
                first_stream = video_stream_indexes[0]
                second_stream = video_stream_indexes[1]
                
                # Объединяем видеопотоки с overlay с настройкой прозрачности
                filter_parts = [f"[0:{first_stream}][0:{second_stream}]overlay=format=auto:alpha=0.5[v1]"]
                
                # Если есть дополнительные потоки, добавляем их
                for i in range(2, len(video_stream_indexes)):
                    stream_idx = video_stream_indexes[i]
                    prev_label = f"v{i-1}"
                    current_label = f"v{i}"
                    filter_parts.append(f"[{prev_label}][0:{stream_idx}]overlay=format=auto:alpha=0.5[{current_label}]")
                
                filter_complex = ";".join(filter_parts)
                final_label = f"[v{len(video_stream_indexes) - 1}]"
            else:
                filter_complex = ""
                final_label = "0:v:0"
            
            # Логируем для диагностики
            logger.info(f"Используем filter_complex: {filter_complex}")
            logger.info(f"Финальная метка: {final_label}")
            
            cmd = [
                'ffmpeg',
                '-i', input_path,
                '-filter_complex', filter_complex,
                '-map', final_label,
                '-map', '0:a?',
                '-c:v', 'libx264',
                '-profile:v', 'high',
                '-level:v', '4.0',
                '-pix_fmt', 'yuv420p',
                '-crf', '18',
                '-preset', 'fast',
                '-movflags', '+faststart',
                '-c:a', 'aac',
                '-b:a', '128k',
                '-y',
                output_path
            ]
            
        logger.debug(f"Выполнение команды: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            logger.info(f"Видео обработано: {input_path} -> {output_path}")
            if result.stderr:
                logger.debug(f"Вывод FFmpeg: {result.stderr}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Ошибка при обработке видео: {e.stderr}")
            raise
    
    def _get_streams_info(self, input_path: str) -> Dict:
        """Получает полную информацию о потоках в файле"""
        cmd = [
            'ffprobe', 
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_streams',
            input_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
            
    def _get_video_dimensions(self, input_path: str, stream_index: int) -> Dict:
        """Получает размеры видеопотока"""
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-select_streams', f'v:{stream_index}',
            '-show_entries', 'stream=width,height',
            '-of', 'json',
            input_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        info = json.loads(result.stdout)
        
        if 'streams' in info and len(info['streams']) > 0:
            stream = info['streams'][0]
            return {
                'width': int(stream.get('width', 1920)),
                'height': int(stream.get('height', 1080))
            }
        
        return {'width': 1920, 'height': 1080}
            