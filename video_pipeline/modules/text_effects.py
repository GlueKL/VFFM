"""
Модуль для добавления текста с эффектами на видео
"""
import os
import subprocess
import logging
from typing import Dict, Any, List, Optional
from video_pipeline.modules.base import BaseModule

logger = logging.getLogger(__name__)

class TextEffects(BaseModule):
    """
    Модуль для добавления текста с эффектами на видео.
    """
    
    def __init__(self, params: Dict[str, Any]):
        """
        Инициализация модуля.
        
        Args:
            params: Параметры модуля:
                - text: Текст для добавления
                - font: Путь к файлу шрифта (TTF)
                - font_size: Размер шрифта (по умолчанию 72)
                - color: Цвет текста (по умолчанию white)
                - position: Позиция текста (center, top, bottom и т.д.)
                - x: Смещение по X (если нужно точное позиционирование)
                - y: Смещение по Y (если нужно точное позиционирование)
                - effect: Тип эффекта (shake, wave, rotate, fade, glow)
                - effect_intensity: Интенсивность эффекта (1-10)
                - start_time: Время появления текста (в секундах)
                - duration: Длительность показа текста (в секундах)
                - outline_color: Цвет обводки (по умолчанию black)
                - outline_width: Толщина обводки (по умолчанию 2)
        """
        super().__init__(params)
        
        self.text = params.get('text', 'Sample Text')
        self.font = params.get('font', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')
        self.font_size = params.get('font_size', 72)
        self.color = params.get('color', 'white')
        self.position = params.get('position', 'center')
        self.x = params.get('x', None)
        self.y = params.get('y', None)
        self.effect = params.get('effect', 'shake')
        self.effect_intensity = params.get('effect_intensity', 5)
        self.start_time = params.get('start_time', 0)
        self.duration = params.get('duration', None)
        self.outline_color = params.get('outline_color', 'black')
        self.outline_width = params.get('outline_width', 2)
        
    def _get_effect_filter(self) -> str:
        """
        Генерация фильтра эффекта в зависимости от выбранного типа.
        """
        intensity = self.effect_intensity / 10.0  # Нормализация интенсивности
        
        if self.effect == 'shake':
            amplitude = 10 * intensity
            freq = 5 * intensity
            return f"tremor=a={amplitude}:f={freq}"
        
        elif self.effect == 'wave':
            amplitude = 20 * intensity
            freq = 2 * intensity
            return f"wave=a={amplitude}:f={freq}"
        
        elif self.effect == 'rotate':
            speed = 30 * intensity
            return f"rotate=a='t*{speed}':c=none"
            
        elif self.effect == 'fade':
            freq = 2 * intensity
            return f"fade=t=in:st={self.start_time}:d=1,fade=t=out:st={self.start_time + self.duration - 1}:d=1"
            
        elif self.effect == 'glow':
            intensity = 2 * self.effect_intensity
            return f"gblur=sigma={intensity},colorbalance=gh=1:bh=1"
            
        return "null"

    def _get_position_string(self) -> str:
        """
        Получение строки позиции для фильтра drawtext.
        """
        if self.x is not None and self.y is not None:
            return f"x={self.x}:y={self.y}"
            
        positions = {
            'center': "x=(w-text_w)/2:y=(h-text_h)/2",
            'top': "x=(w-text_w)/2:y=10",
            'bottom': "x=(w-text_w)/2:y=h-text_h-10",
            'left': "x=10:y=(h-text_h)/2",
            'right': "x=w-text_w-10:y=(h-text_h)/2",
            'topleft': "x=10:y=10",
            'topright': "x=w-text_w-10:y=10",
            'bottomleft': "x=10:y=h-text_h-10",
            'bottomright': "x=w-text_w-10:y=h-text_h-10"
        }
        
        return positions.get(self.position, positions['center'])

    def process(self, input_path: str, output_path: str):
        """
        Добавление текста с эффектами на видео.
        
        Args:
            input_path: Путь к входному видео
            output_path: Путь к выходному видео
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Входной файл не найден: {input_path}")
            
        # Создаем временный слой для текста
        text_filter = (
            f"drawtext=fontfile='{self.font}':"
            f"text='{self.text}':"
            f"fontsize={self.font_size}:"
            f"fontcolor={self.color}:"
            f"{self._get_position_string()}:"
            f"bordercolor={self.outline_color}:"
            f"borderw={self.outline_width}"
        )
        
        # Добавляем эффект
        effect_filter = self._get_effect_filter()
        
        # Формируем полный фильтр
        filter_complex = f"[0:v]{text_filter},{effect_filter}[out]"
        
        # Добавляем временные параметры, если указаны
        if self.start_time is not None or self.duration is not None:
            enable_expr = []
            if self.start_time is not None:
                enable_expr.append(f"gte(t,{self.start_time})")
            if self.duration is not None:
                enable_expr.append(f"lte(t,{self.start_time + self.duration})")
            
            if enable_expr:
                text_filter += f":enable='{' * '.join(enable_expr)}'"
        
        # Команда FFmpeg
        cmd = [
            'ffmpeg',
            '-i', input_path,
            '-filter_complex', filter_complex,
            '-map', '[out]',
            '-map', '0:a?',
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-c:a', 'copy',
            output_path,
            '-y'
        ]
        
        logger.debug(f"Выполнение команды: {' '.join(cmd)}")
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            logger.info(f"Текст с эффектами добавлен: {input_path} -> {output_path}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Ошибка при добавлении текста: {e.stderr.decode()}")
            raise 