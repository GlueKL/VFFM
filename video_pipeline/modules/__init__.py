"""
Модули обработки видео для конвейера
"""

# Base
from video_pipeline.modules.base import BaseModule

# Processing
from video_pipeline.modules.crop import Crop
from video_pipeline.modules.resize import Resize
from video_pipeline.modules.watermark import Watermark
from video_pipeline.modules.delete_audio import DeleteAudio
from video_pipeline.modules.pad import Pad
from video_pipeline.modules.add_video import AddVideo
from video_pipeline.modules.text_effects import TextEffects
from video_pipeline.modules.chromakey import Chromakey

# Utility
from video_pipeline.modules.utility.prepare_for_yt import PrepareForYt
from video_pipeline.modules.utility.cut import Cut

__all__ = ['BaseModule', 'Crop', 'Resize', 'Watermark', 'DeleteAudio', 'Pad', 'AddVideo', 'TextEffects', 'Chromakey', 'PrepareForYt', 'Cut'] 