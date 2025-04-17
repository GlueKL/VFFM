import os
import subprocess
import logging
from typing import Dict, Any

from video_pipeline.modules.base import BaseModule

logger = logging.getLogger(__name__)

class CutVideo(BaseModule):
    """
    Модуль для обрезки видео по времени (извлечения определенного фрагмента).
    
    Параметры:
        start (float): Время начала фрагмента в секундах (по умолчанию 0)
        duration (float): Длительность фрагмента в секундах (по умолчанию 10)
    """
    
    def __init__(self, params: Dict[str, Any]):
        super().__init__(params)
        self.start = params.get('start', 0)
        self.duration = params.get('duration', 10)
    
    def process(self, input_path: str, output_path: str):
        """
        Обрезать видео по заданному времени.
        
        Args:
            input_path: Путь к входному видео
            output_path: Путь к выходному видео
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Входной файл не найден: {input_path}")
        
        # Создаем директорию для выходного файла, если она не существует
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Формируем команду ffmpeg для обрезки видео
        cmd = [
            'ffmpeg',
            '-y',                         # Перезаписывать выходной файл
            '-i', input_path,             # Входной файл
            '-ss', str(self.start),       # Время начала
            '-t', str(self.duration),     # Длительность
            '-c', 'copy',                 # Копировать кодеки (быстрее, чем перекодирование)
            output_path                   # Выходной файл
        ]
        
        # Если нужно точное обрезание, используем другой подход (перекодирование)
        if self.params.get('accurate', False):
            cmd = [
                'ffmpeg',
                '-y',                         # Перезаписывать выходной файл
                '-ss', str(self.start),       # Время начала (перед входным файлом для точности)
                '-i', input_path,             # Входной файл
                '-t', str(self.duration),     # Длительность
                '-c:v', 'libx264',            # Кодек видео
                '-c:a', 'aac',                # Кодек аудио
                '-preset', 'fast',            # Предустановка кодирования
                output_path                   # Выходной файл
            ]
        
        logger.info(f"Обрезка видео: с {self.start} сек, длительность {self.duration} сек")
        
        # Выполняем команду
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            logger.info(f"Видео успешно обрезано и сохранено в {output_path}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Ошибка при обрезке видео: {e.stderr.decode()}")
            raise
            