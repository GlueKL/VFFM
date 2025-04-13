"""
Базовый класс модуля обработки видео
"""
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseModule(ABC):
    """
    Базовый абстрактный класс для всех модулей обработки видео.
    Все модули должны наследоваться от этого класса и реализовать метод process.
    """
    
    def __init__(self, params: Dict[str, Any]):
        """
        Инициализация базового модуля.
        
        Args:
            params: Параметры модуля из конфигурации
        """
        self.width = params.get('width', 1280)
        self.height = params.get('height', 720)
        self.x = params.get('x', 0)
        self.y = params.get('y', 0)
        self.params = params
    
    @abstractmethod
    def process(self, input_path: str, output_path: str):
        """
        Обработка видео.
        
        Args:
            input_path: Путь к входному видео
            output_path: Путь к выходному видео
        """
        pass 