"""
Модуль для расширения видео пустыми областями
"""
import os
import subprocess
import logging
from typing import Dict, Any, Optional

from video_pipeline.modules.base import BaseModule

logger = logging.getLogger(__name__)

class Pad(BaseModule):
    """
    Модуль для расширения видео пустыми областями с помощью FFmpeg.
    """
    
    def __init__(self, params: Dict[str, Any]):
        """
        Инициализация модуля расширения.
        
        Args:
            params: Параметры модуля:
                - width: Итоговая ширина видео в пикселях
                - height: Итоговая высота видео в пикселях
                - position: Положение оригинального видео (center, top, bottom, left, right, center_left, center_right)
                - color: Цвет пустой области в формате hex (по умолчанию "black")
                - image_path: Путь к изображению для заполнения фона (имеет приоритет над color)
        """
        super().__init__(params)
        self.width = params.get('width', 1920)
        self.height = params.get('height', 1080)
        self.position = params.get('position', 'center')
        self.color = params.get('color', 'black')
        self.image_path = params.get('image_path', None)
        
        # Проверяем существование изображения, если оно указано
        if self.image_path and not os.path.exists(self.image_path):
            raise FileNotFoundError(f"Изображение для фона не найдено: {self.image_path}")
        
    def process(self, input_path: str, output_path: str):
        """
        Расширение видео пустыми областями с помощью FFmpeg.
        
        Args:
            input_path: Путь к входному видео
            output_path: Путь к выходному видео
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Входной файл не найден: {input_path}")
            
        # Если используется изображение для фона, используем другой подход
        if self.image_path:
            self._process_with_image(input_path, output_path)
        else:
            self._process_with_color(input_path, output_path)
            
    def _process_with_color(self, input_path: str, output_path: str):
        """
        Обработка с использованием цвета для фона.
        
        Args:
            input_path: Путь к входному видео
            output_path: Путь к выходному видео
        """
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
            '-c:a', 'copy',
        ]
        
        cmd.extend([
            output_path,
            '-y'  # Перезаписать выходной файл, если существует
        ])
        
        logger.debug(f"Выполнение команды: {' '.join(cmd)}")
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            logger.info(f"Видео успешно расширено пустыми областями: {input_path} -> {output_path}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Ошибка при расширении видео: {e.stderr.decode()}")
            raise
            
    def _process_with_image(self, input_path: str, output_path: str):
        """
        Обработка с использованием изображения для фона.
        
        Args:
            input_path: Путь к входному видео
            output_path: Путь к выходному видео
        """
        # Получаем строку позиции для фильтра overlay
        position_str = self._get_position_string()
        
        # Фильтр для масштабирования изображения до нужных размеров и наложения видео
        filter_complex = (
            f"[1:v]scale={self.width}:{self.height},setsar=1[bg];"
            f"[bg][0:v]overlay={position_str}"
        )
        
        # Команда FFmpeg для наложения видео на изображение
        cmd = [
            'ffmpeg',
            '-i', input_path,        # Основное видео (будет наложено)
            '-i', self.image_path,   # Изображение фона
            '-filter_complex', filter_complex,
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-threads', '8',
            '-map', '0:a?',          # Копируем аудио из основного видео, если оно есть
            '-c:a', 'copy',
        ]
        
        cmd.extend([
            output_path,
            '-y'  # Перезаписать выходной файл, если существует
        ])
        
        logger.debug(f"Выполнение команды: {' '.join(cmd)}")
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            logger.info(f"Видео успешно расширено с изображением фона: {input_path} -> {output_path}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Ошибка при расширении видео с изображением: {e.stderr.decode()}")
            raise
            
    def _get_filter_complex(self) -> str:
        """
        Формирование фильтра для расширения пустыми областями.
        
        Returns:
            Строка фильтра для FFmpeg
        """
        # Определяем положение оригинального видео в расширенном видео
        if self.position == 'center':
            x = f"(ow-iw)/2"
            y = f"(oh-ih)/2"
        elif self.position == 'top':
            x = f"(ow-iw)/2"
            y = "0"
        elif self.position == 'bottom':
            x = f"(ow-iw)/2"
            y = f"oh-ih"
        elif self.position == 'left':
            x = "0"
            y = f"(oh-ih)/2"
        elif self.position == 'right':
            x = f"ow-iw"
            y = f"(oh-ih)/2"
        elif self.position == 'center_left':
            x = "0"
            y = f"(oh-ih)/2"
        elif self.position == 'center_right':
            x = f"ow-iw"
            y = f"(oh-ih)/2"
        else:  # по умолчанию center
            x = f"(ow-iw)/2"
            y = f"(oh-ih)/2"
            
        return f"pad={self.width}:{self.height}:{x}:{y}:{self.color}"
        
    def _get_position_string(self) -> str:
        """
        Получение строки позиции для фильтра overlay.
        
        Returns:
            Строка позиции для overlay
        """
        if self.position == 'center':
            return "(W-w)/2:(H-h)/2"
        elif self.position == 'top':
            return "(W-w)/2:0"
        elif self.position == 'bottom':
            return "(W-w)/2:H-h"
        elif self.position == 'left':
            return "0:(H-h)/2"
        elif self.position == 'right':
            return "W-w:(H-h)/2"
        elif self.position == 'center_left':
            return "0:(H-h)/2"
        elif self.position == 'center_right':
            return "W-w:(H-h)/2"
        else:  # по умолчанию center
            return "(W-w)/2:(H-h)/2" 