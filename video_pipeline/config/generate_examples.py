"""
Скрипт для генерации примеров конфигурации из схем
"""
import yaml
from pathlib import Path
from typing import Dict, Any

from video_pipeline.config.schema import MODULE_SCHEMAS

def generate_example_config() -> Dict[str, Any]:
    """
    Генерация примера конфигурации из схем модулей.
    
    Returns:
        Словарь с примером конфигурации
    """
    config = {
        "input": "input.mp4",
        "output": "output.mp4",
        "modules": []
    }
    
    for module_name, schema in MODULE_SCHEMAS.items():
        example_params = {}
        
        # Генерируем примеры параметров на основе схемы
        for param_name, param_schema in schema["properties"].items():
            if "default" in param_schema:
                example_params[param_name] = param_schema["default"]
            else:
                # Генерируем примеры значений в зависимости от типа
                if param_schema["type"] == "string":
                    if "format" in param_schema and param_schema["format"] == "file":
                        example_params[param_name] = f"path/to/{module_name}_file.mp4"
                    else:
                        example_params[param_name] = f"example_{param_name}"
                elif param_schema["type"] == "number":
                    example_params[param_name] = 1.0
                elif param_schema["type"] == "integer":
                    example_params[param_name] = 100
                elif param_schema["type"] == "boolean":
                    example_params[param_name] = False
                elif param_schema["type"] == "array":
                    example_params[param_name] = []
                elif param_schema["type"] == "object":
                    example_params[param_name] = {}
        
        # Добавляем модуль в конфигурацию
        config["modules"].append({
            "name": module_name,
            "params": example_params
        })
    
    return config

def main():
    """
    Генерация и сохранение примера конфигурации.
    """
    # Генерируем пример конфигурации
    example_config = generate_example_config()
    
    # Сохраняем в файл
    output_path = Path(__file__).parent / "example_config.yaml"
    with open(output_path, "w", encoding="utf-8") as f:
        yaml.dump(example_config, f, allow_unicode=True, sort_keys=False)
    
    print(f"Пример конфигурации сохранен в {output_path}")

if __name__ == "__main__":
    main() 