import os
import subprocess
import logging
from typing import Dict, Any

from video_pipeline.modules.base import BaseModule

logger = logging.getLogger(__name__)

class Crop(BaseModule):

    
    def __init__(self, params: Dict[str, Any]):

        super().__init__(params)

        self.width = params.get('width', 1280)
        self.height = params.get('height', 720)
        self.x = params.get('x', 0)
        self.y = params.get('y', 0)
        self.position = params.get('position', 'none')

    def process(self, input_path: str, output_path: str):
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Входной файл не найден: {input_path}")
        
        # Команда FFmpeg
        cmd = [
            'ffmpeg',
            '-i', input_path,
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-threads', '8',
            '-vf', self._get_filter_complex(),
            '-c:a', 'copy'
        ]
        
        cmd.extend([
            output_path,
            '-y'  # Перезаписать выходной файл, если существует
        ])
        
        logger.debug(f"Выполнение команды: {' '.join(cmd)}")
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            logger.info(f"Видео обрезанно: {input_path} -> {output_path}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Ошибка при обрезке видео: {e.stderr.decode()}")
            raise

    def _get_filter_complex(self) -> str:
        if self.position == 'none':
            return f"crop={self.width}:{self.height}:{self.x}:{self.y}"
        else:
            return "crop=" + self._get_position_expression()

    def _get_position_expression(self) -> str:
        positions = {
            'none': '',
            'topleft': f'{self.width}:{self.height}:0:0',
            'topright': f'{self.width}:{self.height}:in_w-{self.width}:0',
            'bottomleft': f'{self.width}:{self.height}:0:in_h-{self.height}',
            'bottomright': f'{self.width}:{self.height}:in_w-{self.width}:in_h-{self.height}',
            'center': f'{self.width}:{self.height}:(in_w-{self.width})/2:(in_h-{self.height})/2'
        }
        
        return positions.get(self.position.lower(), positions['none']) 