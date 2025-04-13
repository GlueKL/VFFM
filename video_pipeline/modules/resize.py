"""
Модуль для изменения размера видео
"""
import os
import subprocess
import logging
from typing import Dict, Any

from video_pipeline.modules.base import BaseModule

logger = logging.getLogger(__name__)

class Resize(BaseModule):
    """
    Модуль для изменения размера видео с помощью FFmpeg.
    """
    
    def __init__(self, params: Dict[str, Any]):
        """
        Инициализация модуля изменения размера.
        
        Args:
            params: Параметры модуля:
                - width: Ширина видео в пикселях
                - height: Высота видео в пикселях
                - keep_aspect_ratio: Сохранять пропорции (по умолчанию True)
                - audio_codec: Аудио кодек (по умолчанию 'copy' - сохранить оригинальный)
        """
        super().__init__(params)
        self.width = params.get('width', 1280)
        self.height = params.get('height', 720)
        self.keep_aspect_ratio = params.get('keep_aspect_ratio', True)
        self.audio_codec = params.get('audio_codec', 'copy')
        
    def process(self, input_path: str, output_path: str):
        """
        Изменение размера видео с помощью FFmpeg.
        
        Args:
            input_path: Путь к входному видео
            output_path: Путь к выходному видео
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Входной файл не найден: {input_path}")
            
        # Подготовка параметров FFmpeg
        filter_complex = self._get_filter_complex()
        
        # Команда FFmpeg
        cmd = [
            'ffmpeg',
            '-i', input_path,
            '-vf', filter_complex,
            '-c:v', 'libx264',   
            '-preset', 'fast',
            '-threads', '8',         
            '-map', '0:v',           # Явно указываем, что берем видеопоток
            '-map', '0:a?',          # Явно указываем, что копируем аудиопоток, если он есть
        ]
        
        # Обработка аудио в зависимости от указанного кодека
        if self.audio_codec == 'libopus':
            cmd.extend([
                '-c:a', 'libopus',
                '-b:a', '128k',
                '-application', 'audio'
            ])
        else:
            cmd.extend(['-c:a', 'copy'])
            
        cmd.extend([
            output_path,
            '-y'  # Перезаписать выходной файл, если существует
        ])
        
        logger.debug(f"Выполнение команды: {' '.join(cmd)}")
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            logger.info(f"Размер видео успешно изменен: {input_path} -> {output_path}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Ошибка при изменении размера видео: {e.stderr.decode()}")
            raise
            
    def _get_filter_complex(self) -> str:
        """
        Формирование фильтра для изменения размера.
        
        Returns:
            Строка фильтра для FFmpeg
        """
        if self.keep_aspect_ratio:
            # Сохраняем пропорции, используя fit
            return f"scale={self.width}:{self.height}:force_original_aspect_ratio=decrease,pad={self.width}:{self.height}:(ow-iw)/2:(oh-ih)/2"
        else:
            # Принудительно изменяем размер без сохранения пропорций
            return f"scale={self.width}:{self.height}" 