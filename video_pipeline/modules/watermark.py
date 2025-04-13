"""
Модуль для добавления водяного знака на видео
"""
import os
import subprocess
import logging
from typing import Dict, Any

from video_pipeline.modules.base import BaseModule

logger = logging.getLogger(__name__)

class Watermark(BaseModule):
    """
    Модуль для добавления водяного знака (изображения) на видео.
    """
    
    def __init__(self, params: Dict[str, Any]):
        """
        Инициализация модуля добавления водяного знака.
        
        Args:
            params: Параметры модуля:
                - image_path: Путь к изображению водяного знака
                - position: Позиция водяного знака ('topleft', 'topright', 'bottomleft', 'bottomright', 'center')
                - opacity: Прозрачность водяного знака (0.0-1.0)
                - scale: Масштаб водяного знака относительно размера видео (0.0-1.0)
                - audio_codec: Аудио кодек (по умолчанию 'copy' - сохранить оригинальный)
        """
        super().__init__(params)
        self.image_path = params.get('image_path')
        self.position = params.get('position', 'bottomright')
        self.opacity = params.get('opacity', 0.5)
        self.scale = params.get('scale', 0.2)
        self.audio_codec = params.get('audio_codec', 'copy')
        
        if not self.image_path:
            raise ValueError("Не указан путь к изображению водяного знака")
        
    def process(self, input_path: str, output_path: str):
        """
        Добавление водяного знака на видео с помощью FFmpeg.
        
        Args:
            input_path: Путь к входному видео
            output_path: Путь к выходному видео
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Входной файл не найден: {input_path}")
            
        if not os.path.exists(self.image_path):
            raise FileNotFoundError(f"Файл с водяным знаком не найден: {self.image_path}")
            
        # Подготовка параметров FFmpeg
        overlay_filter = self._get_overlay_filter()
        
        # Команда FFmpeg
        cmd = [
            'ffmpeg',
            '-i', input_path,
            '-i', self.image_path,
            '-filter_complex', overlay_filter,
            '-map', '[out]',
            '-c:v', 'libx264',   
            '-preset', 'fast',
            '-threads', '8',    
            '-map', '0:a?',
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
        
        # Добавляем параметр -shortest для ограничения длительности выходного видео
        # до длительности самого короткого входного потока (в нашем случае - основного видео)
        cmd.extend(['-shortest'])
        

        cmd.extend([
            output_path,
            '-y'  # Перезаписать выходной файл, если существует
        ])
        
        logger.debug(f"Выполнение команды: {' '.join(cmd)}")
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            logger.info(f"Водяной знак успешно добавлен: {input_path} -> {output_path}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Ошибка при добавлении водяного знака: {e.stderr.decode()}")
            raise
            
    def _get_overlay_filter(self) -> str:
        """
        Формирование фильтра для наложения водяного знака.
        
        Returns:
            Строка фильтра для FFmpeg
        """
        # Масштабирование водяного знака
        overlay = f"[1:v]scale=iw*{self.scale}:-1"
        
        # Применение прозрачности
        if self.opacity < 1.0:
            overlay += f",format=rgba,colorchannelmixer=aa={self.opacity}"
            
        overlay += "[watermark];"
        
        # Позиционирование водяного знака
        position_expr = self._get_position_expression()
        overlay += f"[0:v][watermark]overlay={position_expr}[out]"
        
        return overlay
    
    def _get_position_expression(self) -> str:
        """
        Формирование выражения для позиционирования водяного знака.
        
        Returns:
            Строка выражения для фильтра overlay
        """
        positions = {
            'topleft': '0:0',
            'topright': 'main_w-overlay_w:0',
            'bottomleft': '0:main_h-overlay_h',
            'bottomright': 'main_w-overlay_w:main_h-overlay_h',
            'center': '(main_w-overlay_w)/2:(main_h-overlay_h)/2'
        }
        
        return positions.get(self.position.lower(), positions['bottomright']) 