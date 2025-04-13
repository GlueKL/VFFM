"""
Модуль для нарезки видео на равные части
"""
import os
import subprocess
import logging
from typing import Dict, Any

from video_pipeline.modules.base import BaseModule

logger = logging.getLogger(__name__)

class Cut(BaseModule):
    """
    Модуль для нарезки видео на равные части с помощью FFmpeg.
    """
    
    def __init__(self, params: Dict[str, Any]):
        """
        Инициализация модуля нарезки.
        
        Args:
            params: Параметры модуля:
                - duration: Длительность каждой части в секундах
                - output_dir: Директория для сохранения частей
                - prefix: Префикс для имен файлов частей
                - use_input_name: Использовать имя входного файла как префикс
        """
        super().__init__(params)
        self.duration = params.get('duration')
        if not self.duration or self.duration <= 0:
            raise ValueError("Duration must be a positive number")
            
        self.output_dir = params.get('output_dir', 'parts')
        self.prefix = params.get('prefix', 'part_')
        self.use_input_name = params.get('use_input_name', False)
        
    def process(self, input_path: str, output_path: str):
        """
        Нарезка видео на равные части.
        
        Args:
            input_path: Путь к входному видео
            output_path: Путь к выходному видео (не используется, так как генерируется автоматически)
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")
            
        # Создаем директорию для частей, если её нет
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Получаем длительность видео
        duration = self._get_video_duration(input_path)
        if duration == 0:
            raise ValueError("Could not determine video duration")
            
        # Рассчитываем количество частей
        num_parts = int(duration / self.duration) + (1 if duration % self.duration > 0 else 0)
        
        # Формируем префикс для имен файлов
        if self.use_input_name:
            input_name = os.path.splitext(os.path.basename(input_path))[0]
            file_prefix = f"{input_name}_"
        else:
            file_prefix = self.prefix
            
        # Нарезаем видео на части
        for i in range(num_parts):
            start_time = i * self.duration
            output_file = os.path.join(self.output_dir, f"{file_prefix}{i+1:03d}.mp4")
            
            cmd = [
                'ffmpeg',
                '-i', input_path,
                '-ss', str(start_time),
                '-t', str(self.duration),
                '-c:v', 'libx264',
                '-preset', 'fast',
                '-c:a', 'copy',  # Копируем аудио без перекодирования
                '-threads', '8',
                output_file,
                '-y'  # Перезаписать выходной файл, если существует
            ]
            
            logger.debug(f"Executing command: {' '.join(cmd)}")
            
            try:
                subprocess.run(cmd, check=True, capture_output=True)
                logger.info(f"Part {i+1}/{num_parts} created: {output_file}")
            except subprocess.CalledProcessError as e:
                logger.error(f"Error creating part {i+1}: {e.stderr.decode()}")
                raise
                
    def _get_video_duration(self, video_path: str) -> float:
        """
        Получение длительности видео в секундах.
        
        Args:
            video_path: Путь к видеофайлу
            
        Returns:
            Длительность видео в секундах
        """
        cmd = [
            'ffprobe', 
            '-v', 'error', 
            '-show_entries', 'format=duration', 
            '-of', 'default=noprint_wrappers=1:nokey=1', 
            video_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            duration = float(result.stdout.strip())
            return duration
        except (subprocess.SubprocessError, ValueError) as e:
            logger.warning(f"Could not get video duration: {str(e)}")
            return 0.0
