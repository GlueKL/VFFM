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
        "properties": {
            "image_path": {
                "type": "string"
            },
            "position": {
                "type": "string",
                "enum": ["center", "top", "bottom", "left", "right", "topleft", "topright", "bottomleft", "bottomright"]
            },
            "opacity": {
                "type": "number",
                "minimum": 0.0,
                "maximum": 1.0
            },
            "scale": {
                "type": "number",
                "minimum": 0.1
            }
        },
        "required": ["image_path"]
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
                "enum": ["none", "center", "topleft", "topright", "bottomleft", "bottomright"]
            },
            "width": {
                "type": "integer",
                "minimum": 1
            },
            "height": {
                "type": "integer",
                "minimum": 1
            },
            "x": {
                "type": "integer",
                "minimum": 0
            },
            "y": {
                "type": "integer",
                "minimum": 0
            }
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
                "enum": ["center", "top", "bottom", "left", "right", "topleft", "topright", "bottomleft", "bottomright"]
            },
            "color": {
                "type": "string"
            },
            "image_path": {
                "type": "string"
            }
        },
        "required": ["width", "height"]
    },
    "addvideo": {
        "type": "object",
        "properties": {
            "video_path": {
                "type": "string"
            },
            "position": {
                "type": "string",
                "enum": ["center", "top", "bottom", "left", "right", "topleft", "topright", "bottomleft", "bottomright"]
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
                "minimum": 0.0,
                "maximum": 1.0
            },
            "start_time": {
                "type": "number",
                "minimum": 0.0
            },
            "end_time": {
                "type": "number",
                "minimum": 0.0
            },
            "loop": {
                "type": "boolean"
            },
            "mute": {
                "type": "boolean"
            }
        },
        "required": ["video_path"]
    },
    "chromakey": {
        "type": "object",
        "properties": {
            "color": {
                "type": "array",
                "items": {
                    "type": "string"
                }
            },
            "similarity": {
                "type": "array",
                "items": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0
                }
            },
            "blend": {
                "type": "array",
                "items": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0
                }
            },
            "yuv": {
                "type": "boolean"
            },
            "overlay": {
                "type": "string"
            },
            "position": {
                "type": "string",
                "enum": ["center", "top", "bottom", "left", "right", "topleft", "topright", "bottomleft", "bottomright"]
            },
            "scale": {
                "type": "number",
                "minimum": 0.1
            },
            "mute_overlay": {
                "type": "boolean"
            }
        },
        "required": ["overlay"]
    },
    "utility.cut": {
        "type": "object",
        "properties": {
            "duration": {
                "type": "number",
                "minimum": 0.1
            },
            "output_dir": {
                "type": "string"
            },
            "prefix": {
                "type": "string"
            },
            "use_input_name": {
                "type": "boolean"
            }
        },
        "required": ["duration"],
        "description": "Модуль для нарезки видео на равные части"
    },
    "utility.prepareforyt": {
        "type": "object",
        "properties": {},
        "description": "Модуль для подготовки видео к загрузке на YouTube"
    },
    "text_effects": {
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "description": "Текст для добавления"
            },
            "font": {
                "type": "string",
                "description": "Путь к файлу шрифта (TTF)"
            },
            "font_size": {
                "type": "integer",
                "minimum": 1,
                "description": "Размер шрифта"
            },
            "color": {
                "type": "string",
                "description": "Цвет текста"
            },
            "position": {
                "type": "string",
                "enum": ["center", "top", "bottom", "left", "right", "topleft", "topright", "bottomleft", "bottomright"],
                "description": "Позиция текста"
            },
            "x": {
                "type": "integer",
                "description": "Смещение по X (если нужно точное позиционирование)"
            },
            "y": {
                "type": "integer",
                "description": "Смещение по Y (если нужно точное позиционирование)"
            },
            "effect": {
                "type": "string",
                "enum": ["shake", "wave", "rotate", "fade", "glow"],
                "description": "Тип эффекта"
            },
            "effect_intensity": {
                "type": "integer",
                "minimum": 1,
                "maximum": 10,
                "description": "Интенсивность эффекта (1-10)"
            },
            "start_time": {
                "type": "number",
                "minimum": 0,
                "description": "Время появления текста (в секундах)"
            },
            "duration": {
                "type": "number",
                "minimum": 0,
                "description": "Длительность показа текста (в секундах)"
            },
            "outline_color": {
                "type": "string",
                "description": "Цвет обводки"
            },
            "outline_width": {
                "type": "integer",
                "minimum": 0,
                "description": "Толщина обводки"
            }
        }
    },
    "utility.module_wrapper": {
        "type": "object",
        "properties": {
            "module_name": {
                "type": "string",
                "description": "Имя модуля для вызова"
            },
            "module_params": {
                "type": "object",
                "description": "Параметры для вызываемого модуля",
                "additionalProperties": {
                    "type": ["string", "number", "boolean", "object", "array"]
                }
            },
            "custom_input": {
                "type": "string",
                "description": "Путь к входному видео (обязательный параметр)"
            },
            "custom_output": {
                "type": "string",
                "description": "Путь к выходному видео (обязательный параметр)"
            },
            "copy_to_pipeline": {
                "type": "boolean",
                "description": "Копировать результат в основной конвейер",
                "default": False
            }
        },
        "required": ["module_name", "custom_input", "custom_output"],
        "description": "Модуль для вызова других модулей напрямую, может работать изолированно от основного конвейера"
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