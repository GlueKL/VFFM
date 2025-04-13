"""
Схема валидации YAML-конфигурации
"""
import jsonschema
from typing import Dict, Any

# Базовая схема для валидации конфигурации
CONFIG_SCHEMA = {
    "type": "object",
    "required": ["input", "output", "modules"],
    "properties": {
        "input": {
            "type": "string",
            "description": "Путь к входному видео"
        },
        "output": {
            "type": "string",
            "description": "Путь к выходному видео"
        },
        "modules": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name"],
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Имя модуля"
                    },
                    "params": {
                        "type": "object",
                        "description": "Параметры модуля"
                    }
                }
            }
        }
    }
}

# Схемы для конкретных модулей
MODULE_SCHEMAS = {
    "resize": {
        "type": "object",
        "properties": {
            "width": {
                "type": "integer",
                "minimum": 1
            },
            "height": {
                "type": "integer",
                "minimum": 1
            },
            "keep_aspect_ratio": {
                "type": "boolean"
            }
        }
    },
    "watermark": {
        "type": "object",
        "required": ["image_path"],
        "properties": {
            "image_path": {
                "type": "string"
            },
            "position": {
                "type": "string",
                "enum": ["topleft", "topright", "bottomleft", "bottomright", "center"]
            },
            "opacity": {
                "type": "number",
                "minimum": 0,
                "maximum": 1
            },
            "scale": {
                "type": "number",
                "minimum": 0,
                "maximum": 1
            },
            "audio_codec": {
                "type": "string",
                "description": "Аудио кодек (по умолчанию 'copy' - сохранить оригинальный)"
            }
        }
    },
    "deleteaudio": {
        "type": "object",
        "properties": {}
    },
    "crop": {
        "type": "object",
        "properties": {
            "position": {
                "type": "string",
                "enum": ["none", "topleft", "topright", "bottomleft", "bottomright", "center"]
            },
            "width": {"type": "integer", "minimum": 1},
            "height": {"type": "integer", "minimum": 1},
            "x": {"type": "integer", "minimum": 0},
            "y": {"type": "integer", "minimum": 0}
        }
    },
    "pad": {
        "type": "object",
        "properties": {
            "width": {
                "type": "integer",
                "minimum": 1
            },
            "height": {
                "type": "integer",
                "minimum": 1
            },
            "position": {
                "type": "string",
                "enum": ["center", "top", "bottom", "left", "right", "center_left", "center_right"]
            },
            "color": {
                "type": "string"
            },
            "image_path": {
                "type": "string"
            }
        }
    },
    "addvideo": {
        "type": "object",
        "required": ["video_path"],
        "properties": {
            "video_path": {
                "type": "string"
            },
            "position": {
                "type": "string",
                "enum": ["center", "top", "bottom", "left", "right", "center_left", "center_right", 
                         "topleft", "topright", "bottomleft", "bottomright"]
            },
            "x": {
                "type": "integer"
            },
            "y": {
                "type": "integer"
            },
            "width": {
                "type": "integer",
                "minimum": 1
            },
            "height": {
                "type": "integer",
                "minimum": 1
            },
            "scale": {
                "type": "number",
                "minimum": 0.1
            },
            "alpha": {
                "type": "number",
                "minimum": 0,
                "maximum": 1
            },
            "start_time": {
                "type": "number",
                "minimum": 0
            },
            "end_time": {
                "type": "number",
                "minimum": 0
            },
            "loop": {
                "type": "boolean"
            },
            "mute": {
                "type": "boolean"
            }
        }
    },
    "chromakey": {
        "type": "object",
        "required": ["overlay"],
        "properties": {
            "color": {
                "type": "string",
                "description": "Цвет для удаления. Можно указать 'green' или в формате '#00FF00' или '0x00FF00'",
                "default": "green"
            },
            "similarity": {
                "type": "number",
                "description": "Уровень схожести с выбранным цветом",
                "minimum": 0.0,
                "maximum": 1.0,
                "default": 0.1
            },
            "blend": {
                "type": "number",
                "description": "Степень смешивания краев",
                "minimum": 0.0,
                "maximum": 1.0,
                "default": 0.0
            },
            "overlay": {
                "type": "string",
                "description": "Путь к видео с зеленым экраном"
            },
            "position": {
                "type": "string",
                "description": "Положение накладываемого видео",
                "enum": ["center", "top", "bottom", "left", "right", "center_left", "center_right", 
                        "topleft", "topright", "bottomleft", "bottomright"],
                "default": "center"
            },
            "x": {
                "type": ["number", "null"],
                "description": "Смещение по оси X (игнорируется если указан position)",
                "default": None
            },
            "y": {
                "type": ["number", "null"],
                "description": "Смещение по оси Y (игнорируется если указан position)",
                "default": None
            },
            "width": {
                "type": ["number", "null"],
                "description": "Ширина накладываемого видео",
                "default": None
            },
            "height": {
                "type": ["number", "null"],
                "description": "Высота накладываемого видео",
                "default": None
            },
            "scale": {
                "type": "number",
                "description": "Масштаб накладываемого видео",
                "minimum": 0.1,
                "default": 1.0
            },
            "audio_codec": {
                "type": "string",
                "description": "Аудио кодек (copy - сохранить оригинальный, libopus - перекодировать в Opus)",
                "enum": ["copy", "libopus"],
                "default": "copy"
            },
            "mute_overlay": {
                "type": "boolean",
                "description": "Удалить звук из видео с зеленым экраном",
                "default": True
            }
        },
        "description": "Модуль для удаления зеленого экрана и наложения на фоновое видео"
    },
    "cut": {
        "type": "object",
        "required": ["duration"],
        "properties": {
            "duration": {
                "type": "number",
                "description": "Длительность каждой части в секундах",
                "minimum": 0.1
            },
            "output_dir": {
                "type": "string",
                "description": "Директория для сохранения частей",
                "default": "parts"
            },
            "prefix": {
                "type": "string",
                "description": "Префикс для имен файлов",
                "default": "part_"
            }
        }
    },
    "utility.prepareforyt": {
        "type": "object",
        "properties": {}
    },
    "utility.cut": {
        "type": "object",
        "properties": {
            "duration": {
                "type": "number",
                "minimum": 0.1,
                "description": "Длительность каждой части в секундах"
            },
            "output_dir": {
                "type": "string",
                "default": "parts",
                "description": "Директория для сохранения частей"
            },
            "prefix": {
                "type": "string",
                "default": "part_",
                "description": "Префикс для имен файлов частей"
            },
            "use_input_name": {
                "type": "boolean",
                "default": False,
                "description": "Использовать имя входного файла как префикс"
            }
        },
        "required": ["duration"],
        "description": "Модуль для нарезки видео на равные части"
    }
}

def validate_config(config: Dict[str, Any]) -> None:
    """
    Валидация конфигурации.
    
    Args:
        config: Словарь с конфигурацией
        
    Raises:
        jsonschema.exceptions.ValidationError: Если конфигурация не соответствует схеме
    """
    # Валидация основной схемы
    jsonschema.validate(config, CONFIG_SCHEMA)
    
    # Валидация параметров каждого модуля
    for module_config in config.get("modules", []):
        module_name = module_config.get("name")
        module_params = module_config.get("params", {})
        
        if module_name in MODULE_SCHEMAS:
            try:
                jsonschema.validate(module_params, MODULE_SCHEMAS[module_name])
            except jsonschema.exceptions.ValidationError as e:
                raise jsonschema.exceptions.ValidationError(
                    f"Ошибка валидации параметров модуля '{module_name}': {str(e)}")
                    
    return True 