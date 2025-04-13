# Конвейер обработки видео (Video Pipeline)

Модульный конвейер для обработки видео на Python с конфигурацией через YAML.

## Возможности

- Гибкая настройка через YAML-конфигурацию
- Модульная архитектура, легко расширяемая новыми модулями обработки
- Поддержка базовых операций обработки видео
- Простой интерфейс командной строки

## Установка

```bash
# Установка
pip install -e .
```

## Требования

- Python 3.7+
- FFmpeg (должен быть установлен и доступен в PATH)
- Зависимости Python (устанавливаются автоматически):
  - PyYAML
  - jsonschema
  - opencv-python
  - numpy

## Использование

### Создание конфигурации

Создайте YAML-файл конфигурации:

```yaml
# config.yaml
input: input.mp4
output: output.mp4
modules:
  - name: resize
    params:
      width: 1280
      height: 720
      keep_aspect_ratio: true
  - name: watermark
    params:
      image_path: logo.png
      position: bottomright
      opacity: 0.5
      scale: 0.2
```

### Запуск обработки

```bash
# Запуск через консольную утилиту
video-pipeline process -c config.yaml

# Переопределение параметров входа/выхода
video-pipeline process -c config.yaml -i my_input.mp4 -o my_output.mp4

# Изменение уровня логгирования
video-pipeline process -c config.yaml -l DEBUG --log-file processing.log
```

### Программное использование

```python
from video_pipeline.core.pipeline import Pipeline

# Создание конвейера с конфигурацией
pipeline = Pipeline("config.yaml")

# Запуск обработки
pipeline.process()
```

## Добавление новых модулей

1. Создайте новый файл в директории `video_pipeline/modules/`
2. Создайте класс, наследующийся от `BaseModule`
3. Реализуйте метод `process()`
4. Добавьте схему валидации в `video_pipeline/config/schema.py`

## Лицензия

MIT
