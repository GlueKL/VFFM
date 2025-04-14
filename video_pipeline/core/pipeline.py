"""
Core video processing pipeline class
"""
import os
import yaml
import logging
import sys
from typing import Dict, List, Any, Optional
from importlib import import_module

from video_pipeline.utils.ffmpeg import check_ffmpeg_installed

logger = logging.getLogger(__name__)

class Pipeline:
    """
    Main video processing pipeline class.
    Loads configuration from YAML and executes video processing modules.
    """
    
    def __init__(self, config_path: str):
        """
        Initialize the video processing pipeline.
        
        Args:
            config_path: Path to the YAML configuration file
        """
        self.config_path = config_path
        self.config = self._load_config()
        self.modules = []
        
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from YAML file.
        
        Returns:
            Dictionary with configuration
        """
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
            
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _load_modules(self):
        """
        Load processing modules from configuration.
        """
        if 'modules' not in self.config:
            raise ValueError("Configuration is missing 'modules' section")
            
        for module_config in self.config['modules']:
            module_name = module_config.get('name')
            if not module_name:
                raise ValueError("Module must have a name")
                
            try:
                # Разбиваем имя модуля на части
                module_parts = module_name.split('.')
                
                # Формируем путь к модулю
                if len(module_parts) > 1:
                    # Если есть подмодуль (например, utility.prepare_for_yt)
                    module_path = f"video_pipeline.modules.{module_parts[0]}.{module_parts[1]}"
                else:
                    # Если модуль в корневой директории
                    module_path = f"video_pipeline.modules.{module_name}"
                
                # Импортируем модуль
                module = import_module(module_path)
                
                # Получаем последнюю часть имени для поиска класса
                last_part = module_parts[-1]
                
                # Пробуем разные варианты имени класса
                class_variants = [
                    last_part.capitalize(),  # prepareforyt -> Prepareforyt
                    last_part,  # Оставить как есть (если в конфиге указано правильно)
                    # Convert snake_case to CamelCase
                    ''.join(x.capitalize() or '_' for x in last_part.split('_'))  # prepare_for_yt -> PrepareForYt
                ]
                
                # Пробуем каждый вариант
                module_class = None
                for variant in class_variants:
                    try:
                        module_class = getattr(module, variant)
                        break
                    except AttributeError:
                        continue
                        
                if module_class is None:
                    raise AttributeError(f"Could not find class for module {module_name}")
                    
                module_instance = module_class(module_config.get('params', {}))
                self.modules.append(module_instance)
                logger.info(f"Module {module_name} loaded successfully")
            except (ImportError, AttributeError) as e:
                logger.error(f"Error loading module {module_name}: {str(e)}")
                raise
    
    def process(self, input_path: Optional[str] = None, output_path: Optional[str] = None):
        """
        Start video processing.
        
        Args:
            input_path: Path to input video (overrides path from configuration)
            output_path: Path to output video (overrides path from configuration)
        """
        # Check for FFmpeg
        if not check_ffmpeg_installed():
            logger.error("FFmpeg not found. Install FFmpeg before using the pipeline.")
            return
            
        # Load modules if not loaded yet
        if not self.modules:
            self._load_modules()
            
        # Determine file paths
        input_file = input_path or self.config.get('input')
        output_file = output_path or self.config.get('output')
        
        if not input_file:
            raise ValueError("Input file not specified")
        if not output_file:
            raise ValueError("Output file not specified")
            
        # Check if input file exists
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file not found: {input_file}")
            
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Temporary files for intermediate results
        temp_input = input_file
        
        # Apply modules sequentially
        for i, module in enumerate(self.modules):
            is_last_module = i == len(self.modules) - 1
            temp_output = output_file if is_last_module else f"temp_{i}.mp4"
            
            logger.info(f"Applying module {module.__class__.__name__}")
            module.process(temp_input, temp_output)
            
            # If not the last module, update input file for the next one
            if not is_last_module:
                temp_input = temp_output
                
        logger.info(f"Processing complete. Result saved to {output_file}")
        
        # Clean up temporary files
        self._cleanup_temp_files()
    
    def _cleanup_temp_files(self):
        """
        Delete temporary files.
        """
        for i in range(len(self.modules) - 1):
            temp_file = f"temp_{i}.mp4"
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except OSError as e:
                    logger.warning(f"Failed to delete temporary file {temp_file}: {str(e)}") 