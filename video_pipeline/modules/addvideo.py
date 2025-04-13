"""
Модуль для добавления видео поверх основного
"""
import os
import subprocess
import logging
from typing import Dict, Any, Optional, List

from video_pipeline.modules.base import BaseModule

logger = logging.getLogger(__name__)

class Addvideo(BaseModule):
    """
    Модуль для добавления видео поверх основного с помощью FFmpeg.
    """
    
    def __init__(self, params: Dict[str, Any]):
        """
        Инициализация модуля добавления видео.
        
        Args:
            params: Параметры модуля:
                - video_path: Путь к видео, которое нужно добавить
                - position: Положение видео (center, top, bottom, left, right, center_left, center_right, 
                           topleft, topright, bottomleft, bottomright)
                - x: Смещение по оси X (если не указано положение или нужно точное позиционирование)
                - y: Смещение по оси Y (если не указано положение или нужно точное позиционирование)
                - width: Ширина видео в пикселях (имеет приоритет над scale)
                - height: Высота видео в пикселях (имеет приоритет над scale)
                - scale: Масштаб видео (1.0 = оригинальный размер)
                - alpha: Прозрачность видео (0.0-1.0)
                - start_time: Время начала вставки в секундах
                - end_time: Время окончания вставки в секундах
                - loop: Зацикливать видео до конца основного (по умолчанию False)
                - mute: Удалить звук из добавляемого видео (по умолчанию False)
                - audio_codec: Аудио кодек (по умолчанию 'copy' - сохранить оригинальный)
        """
        super().__init__(params)
        
        self.video_path = params.get('video_path')
        if not self.video_path or not os.path.exists(self.video_path):
            raise ValueError(f"Видеофайл для вставки не найден: {self.video_path}")
            
        self.position = params.get('position', 'center')
        self.x = params.get('x', None)
        self.y = params.get('y', None)
        self.width = params.get('width', None)
        self.height = params.get('height', None)
        self.scale = params.get('scale', 1.0)
        self.alpha = params.get('alpha', 1.0)
        self.start_time = params.get('start_time', None)
        self.end_time = params.get('end_time', None)
        self.loop = params.get('loop', False)
        self.mute = params.get('mute', False)
        self.audio_codec = params.get('audio_codec', 'copy')
        
    def process(self, input_path: str, output_path: str):
        """
        Добавление видео поверх основного с помощью FFmpeg.
        
        Args:
            input_path: Путь к входному видео
            output_path: Путь к выходному видео
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Входной файл не найден: {input_path}")
            
        # Подготовка параметров FFmpeg
        filter_complex = self._get_filter_complex()
        
        # Формирование базовой команды FFmpeg
        cmd = []
        
        # Добавляем входное основное видео с аппаратным ускорением
        cmd.extend(['ffmpeg', '-i', input_path])
        
        # Добавляем входное накладываемое видео, с зацикливанием если нужно
        if self.loop:
            # Используем -stream_loop для зацикливания
            # Получим количество повторений, если возможно
            overlay_duration = self._get_video_duration(self.video_path)
            main_duration = self._get_video_duration(input_path)
            
            if overlay_duration > 0 and main_duration > 0:
                # Вычисляем количество повторений плюс запас
                loop_count = int(main_duration / overlay_duration) + 2
                logger.info(f"Длительность основного видео: {main_duration} секунд")
                logger.info(f"Длительность накладываемого видео: {overlay_duration} секунд")
                logger.info(f"Количество повторений для зацикливания: {loop_count}")
                
                cmd.extend(['-stream_loop', str(loop_count)])
            else:
                # Если не удалось получить длительность, делаем бесконечное зацикливание
                logger.warning("Не удалось точно рассчитать количество повторений, используем бесконечное зацикливание")
                cmd.extend(['-stream_loop', '-1'])
        
        # Добавляем накладываемое видео
        cmd.extend(['-i', self.video_path])
        
        # Далее идут общие параметры
        cmd.extend([
            '-filter_complex', filter_complex,
            '-c:v', 'libx264',  
            '-preset', 'fast'
        ])
        
        # Добавляем опции для аудио
        if self.mute:
            # Если нужно удалить звук, берем только аудиопоток из основного видео
            cmd.extend(['-map', '0:a?'])
        else:
            # Иначе берем аудио из обоих видео
            cmd.extend(['-map', '0:a?'])
            
        # Добавляем видеопоток и исключаем потоки данных
        cmd.extend(['-map', '0:v', '-map', '-0:d'])
        
        # Добавляем параметр -shortest для ограничения длительности выходного видео
        # до длительности самого короткого входного потока (в нашем случае - основного видео)
        cmd.extend(['-shortest'])
        
        # Обработка аудио
        if self.audio_codec == 'libopus':
            # Если указан Opus, используем специфичные параметры
            cmd.extend([
                '-c:a', 'libopus',
                '-b:a', '128k',
                '-application', 'audio'
            ])
        else:
            # По умолчанию копируем оригинальный аудио поток без перекодирования
            cmd.extend(['-c:a', 'copy'])
        
        cmd.extend([
            output_path,
            '-y'  # Перезаписать выходной файл, если существует
        ])
        
        logger.debug(f"Выполнение команды: {' '.join(cmd)}")
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            logger.info(f"Видео успешно добавлено: {input_path} -> {output_path}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Ошибка при добавлении видео: {e.stderr.decode()}")
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
            logger.warning(f"Не удалось получить длительность видео: {str(e)}")
            return 0.0  # Возвращаем 0, если не удалось получить длительность
            
    def _get_filter_complex(self) -> str:
        """
        Формирование строки фильтра для FFmpeg.
        
        Returns:
            Строка фильтра для FFmpeg
        """
        # Определение позиции для вставки
        position_str = self._get_position_string()
        
        # Формирование фильтра
        filter_parts = []
            
        # Масштабирование видео
        if self.width is not None and self.height is not None:
            # Если указаны конкретные размеры, используем их
            filter_parts.append("[1:v]scale={0}:{1}[scaled]".format(self.width, self.height))
        elif self.width is not None:
            # Если указана только ширина, сохраняем пропорции
            filter_parts.append("[1:v]scale={0}:-1[scaled]".format(self.width))
        elif self.height is not None:
            # Если указана только высота, сохраняем пропорции
            filter_parts.append("[1:v]scale=-1:{0}[scaled]".format(self.height))
        elif self.scale != 1.0:
            # Если указан масштаб, используем его
            filter_parts.append("[1:v]scale=iw*{0}:ih*{0}[scaled]".format(self.scale))
        else:
            # Если ничего не указано, оставляем как есть
            filter_parts.append("[1:v]null[scaled]")
        
        # Установка прозрачности
        if self.alpha < 1.0:
            filter_parts.append("[scaled]format=rgba,colorchannelmixer=aa={0}[overlay]".format(self.alpha))
        else:
            filter_parts.append("[scaled]null[overlay]")
        
        # Начальное и конечное время
        enable_expr = ""
        if self.start_time is not None or self.end_time is not None:
            start_expr = "gte(t,{0})".format(self.start_time) if self.start_time is not None else "1"
            end_expr = "lte(t,{0})".format(self.end_time) if self.end_time is not None else "1"
            enable_expr = ":enable='{0}*{1}'".format(start_expr, end_expr)
        
        # Итоговое наложение
        filter_parts.append("[0:v][overlay]overlay={0}{1}".format(position_str, enable_expr))
        
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
            # По умолчанию центр
            return "(W-w)/2:(H-h)/2" 