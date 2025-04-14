import os
import subprocess
import logging
from typing import Dict, Any

from video_pipeline.modules.base import BaseModule

logger = logging.getLogger(__name__)

class Prepareforyt(BaseModule):

    
    def __init__(self, params: Dict[str, Any]):

        super().__init__(params)
        
    def process(self, input_path: str, output_path: str):
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Входной файл не найден: {input_path}")
        
        # Команда FFmpeg
        cmd = [
            'ffmpeg',
            '-i', input_path,
            '-filter_complex', '[0:v]concat=n=1:v=1[outv]',  # Сведение всех видео-потоков в один
            '-map', '[outv]',  # Использовать объединенный видео-поток
            '-map', '0:a?',    # Использовать все аудио-потоки (если есть)
            '-c:v', 'libx264',
            '-profile:v', 'high',
            '-level:v', '4.0',
            '-pix_fmt', 'yuv420p',
            '-crf', '18',
            '-preset', 'fast',
            '-movflags', '+faststart',

            '-c:a', 'aac',
            '-b:a', '128k',
            output_path,
            '-y'  # Перезаписать выходной файл, если существует
        ]
        
        logger.debug(f"Выполнение команды: {' '.join(cmd)}")
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            logger.info(f"Видео обработано: {input_path} -> {output_path}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Ошибка при обработке видео: {e.stderr.decode()}")
            raise
            