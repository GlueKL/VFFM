"""
Модуль для вызова других модулей напрямую
"""
import os
import logging
import importlib
import shutil
from typing import Dict, Any, Type, Optional

from video_pipeline.modules.base import BaseModule

logger = logging.getLogger(__name__)

class ModuleWrapper(BaseModule):
    """
    Модуль-обертка для вызова других модулей напрямую.
    """
    
    def __init__(self, params: Dict[str, Any]):
        """
        Инициализация модуля-обертки.
        
        Args:
            params: Параметры модуля:
                - module_name: Имя модуля для вызова
                - module_params: Параметры для вызываемого модуля
                - custom_input: Путь к входному видео (необязательно)
                - custom_output: Путь к выходному видео (необязательно)
                - copy_to_pipeline: Копировать результат в основной конвейер (по умолчанию False)
        """
        super().__init__(params)
        
        self.module_name = params.get('module_name')
        if not self.module_name:
            raise ValueError("module_name is required")
            
        self.module_params = params.get('module_params', {})
        self.custom_input = params.get('custom_input')
        self.custom_output = params.get('custom_output')
        self.copy_to_pipeline = params.get('copy_to_pipeline', False)
        
        # Динамический импорт модуля
        self.module = self._import_module(self.module_name, self.module_params)
    
    def _import_module(self, module_name: str, module_params: Dict[str, Any]) -> BaseModule:
        """
        Динамический импорт модуля по имени.
        
        Args:
            module_name: Имя модуля для импорта
            module_params: Параметры для модуля
            
        Returns:
            Экземпляр импортированного модуля
        """
        try:
            # Разбиваем путь к модулю
            module_path_parts = module_name.split('.')
            
            # Пробуем несколько возможных путей импорта
            possible_paths = [
                f"video_pipeline.modules.{module_name}",  # Стандартный путь
                f"video_pipeline.modules.utility.{module_name}"  # Путь в utility
            ]
            
            # Если в имени модуля уже есть точки, значит путь уже указан полностью
            if len(module_path_parts) > 1:
                possible_paths = [f"video_pipeline.modules.{module_name}"] + possible_paths
            
            # Пробуем импортировать по каждому из путей
            for path in possible_paths:
                try:
                    module = importlib.import_module(path)
                    
                    # Получаем все классы из модуля
                    module_classes = [cls for name, cls in module.__dict__.items() 
                                    if isinstance(cls, type) and issubclass(cls, BaseModule) and cls != BaseModule]
                    
                    if module_classes:
                        # Берем первый найденный класс модуля
                        module_class = module_classes[0]
                        
                        # Создаем экземпляр модуля
                        logger.info(f"Successfully imported module from path: {path}")
                        return module_class(module_params)
                except ImportError:
                    continue
            
            # Если ни один импорт не сработал
            raise ImportError(f"Could not import module {module_name} from any possible paths")
            
        except (ImportError, AttributeError) as e:
            logger.error(f"Error importing module {module_name}: {str(e)}")
            raise ValueError(f"Failed to import module {module_name}: {str(e)}")
    
        
    def process(self, input_path: str, output_path: str):
        """
        Обработка видео с помощью выбранного модуля.
        
        Args:
            input_path: Путь к входному видео
            output_path: Путь к выходному видео
        """
        actual_input = self.custom_input
        actual_output = self.custom_output
        
        if not os.path.exists(actual_input):
            raise FileNotFoundError(f"Input file not found: {actual_input}")
            
        # Создаем директорию для выходного файла, если её нет
        os.makedirs(os.path.dirname(actual_output), exist_ok=True)
        
        # Вызываем модуль
        logger.info(f"Calling module {self.module_name} with params: {self.module_params}")
        logger.info(f"Using input: {actual_input}, output: {actual_output}")

        self.module.process(actual_input, actual_output)

        shutil.copy2(input_path, output_path)
        logger.info(f"{input_path} copied to pipeline output: {output_path}")