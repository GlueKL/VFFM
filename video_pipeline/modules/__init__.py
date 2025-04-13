"""
Модули обработки видео для конвейера
"""
from video_pipeline.modules.base import BaseModule
from video_pipeline.modules.crop import Crop
from video_pipeline.modules.resize import Resize
from video_pipeline.modules.watermark import Watermark
from video_pipeline.modules.deleteaudio import Deleteaudio
from video_pipeline.modules.pad import Pad
from video_pipeline.modules.addvideo import Addvideo

__all__ = ['BaseModule', 'Crop', 'Resize', 'Watermark', 'Deleteaudio', 'Pad', 'Addvideo'] 