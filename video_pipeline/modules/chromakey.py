"""
Модуль для удаления зеленого экрана (хромакей) и наложения на фоновое видео
"""
import os
import subprocess
import logging
from typing import Dict, Any

from video_pipeline.modules.base import BaseModule

logger = logging.getLogger(__name__)

class Chromakey(BaseModule):
    """
    Модуль для удаления зеленого экрана и наложения на фоновое видео с помощью FFmpeg.
    """
    
    def __init__(self, params: Dict[str, Any]):
        """
        Инициализация модуля удаления зеленого экрана.
        
        Args:
            params: Параметры модуля:
                - color: Цвет для удаления (по умолчанию 'green')
                - similarity: Сходство с цветом (0.0-1.0)
                - blend: Смешивание (0.0-1.0)
                - overlay: Путь к видео с зеленым экраном (обязательный параметр)
                - position: Положение накладываемого видео
                - x: Смещение по оси X
                - y: Смещение по оси Y
                - width: Ширина накладываемого видео
                - height: Высота накладываемого видео
                - scale: Масштаб накладываемого видео
                - mute_overlay: Удалить звук из видео с зеленым экраном (по умолчанию True)
        """
        super().__init__(params)
        
        self.color = params.get('color', 'green')
        # Преобразуем цвет в формат 0xRRGGBB если он в формате #RRGGBB
        if self.color.startswith('#'):
            self.color = '0x' + self.color[1:]
        elif self.color == 'green':
            self.color = '0x00FF00'
            
        self.similarity = params.get('similarity', 0.1)
        self.blend = params.get('blend', 0.0)
        
        # Параметры для наложения
        self.overlay = params.get('overlay')
        if not self.overlay or not os.path.exists(self.overlay):
            raise ValueError(f"Видео с зеленым экраном не найдено: {self.overlay}")
            
        self.position = params.get('position', 'center')
        self.x = params.get('x', None)
        self.y = params.get('y', None)
        self.width = params.get('width', None)
        self.height = params.get('height', None)
        self.scale = params.get('scale', 1.0)
        
        # Параметры для аудио
        self.mute_overlay = params.get('mute_overlay', True)
        
    def process(self, input_path: str, output_path: str):
        """
        Удаление зеленого экрана и наложение на фоновое видео с помощью FFmpeg.
        
        Args:
            input_path: Путь к входному видео
            output_path: Путь к выходному видео
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Входной файл не найден: {input_path}")
            
        # Формирование команды FFmpeg
        cmd = [
            'ffmpeg',
            '-i', input_path,      # Основное видео
            '-i', self.overlay,    # Видео с зеленым экраном
            '-filter_complex', self._get_filter_complex(),
            '-c:v', 'libx264',  # Используем NVIDIA GPU для кодирования
            '-preset', 'fast',
            '-threads', '8'
        ]
        
        # Управление аудио
        if self.mute_overlay:
            # Если нужно удалить звук из overlay, берем только аудио из основного видео
            cmd.extend(['-map', '0:a?'])
        else:
            # Иначе берем аудио из обоих видео
            cmd.extend(['-map', '0:a?', '-map', '1:a?'])
            
        # Добавляем видеопоток
        cmd.extend(['-map', '[out]'])
        
        # Обработка аудио
        cmd.extend(['-c:a', 'copy'])
            
        cmd.extend([
            output_path,
            '-y'  # Перезаписать выходной файл, если существует
        ])
        
        logger.debug(f"Выполнение команды: {' '.join(cmd)}")
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            logger.info(f"Видео успешно обработано: {input_path} -> {output_path}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Ошибка при обработке видео: {e.stderr.decode()}")
            raise
            
    def _get_filter_complex(self) -> str:
        """
        Формирование комплексного фильтра для FFmpeg.
        
        Returns:
            Строка фильтра для FFmpeg
        """
        filter_parts = []
        
        # 1. Обработка видео с зеленым экраном
        colorkey_filter = f"[1:v]colorkey={self.color}:{self.similarity}:{self.blend}[ckout]"
        filter_parts.append(colorkey_filter)
            
        # 2. Масштабирование видео с зеленым экраном
        if self.width is not None and self.height is not None:
            scale_filter = f"[ckout]scale={self.width}:{self.height}[scaled]"
            filter_parts.append(scale_filter)
            overlay_input = "[scaled]"
        elif self.scale != 1.0:
            scale_filter = f"[ckout]scale=iw*{self.scale}:ih*{self.scale}[scaled]"
            filter_parts.append(scale_filter)
            overlay_input = "[scaled]"
        else:
            overlay_input = "[ckout]"
            
        # 3. Позиционирование
        position_str = self._get_position_string()
        filter_parts.append(f"[0:v]{overlay_input}overlay={position_str}[out]")
        
        return ";".join(filter_parts)
        
    def _get_position_string(self) -> str:
        """
        Получение строки позиции для фильтра overlay.
        
        Returns:
            Строка позиции
        """
        # Если указаны x и y явно, используем их
        if self.x is not None and self.y is not None:
            return f"{self.x}:{self.y}"
            
        # Иначе используем предопределенные позиции
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
        elif self.position == 'topleft':
            return "0:0"
        elif self.position == 'topright':
            return "W-w:0"
        elif self.position == 'bottomleft':
            return "0:H-h"
        elif self.position == 'bottomright':
            return "W-w:H-h"
        else:
            return "(W-w)/2:(H-h)/2"  # По умолчанию в центре 