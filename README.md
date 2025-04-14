# VFFM (Video Fast File Manager)

Быстрый и удобный инструмент для обработки видео с использованием FFmpeg.

## Возможности

- Модульная система обработки видео
- Конфигурация через YAML-файлы
- Поддержка различных операций с видео:
  - Изменение размера
  - Обрезка
  - Добавление водяных знаков
  - Удаление аудио
  - Добавление видео поверх основного
  - Хромакей
  - Добавление текста с эффектом
  - Нарезка на части
  - Подготовка видео для стандартов YouTube

## Установка

```bash
# Клонирование репозитория
git clone https://github.com/GlueKL/VFFM.git
cd VFFM

# Установка зависимостей
pip install -r requirements.txt
```

## Использование

1. Создайте конфигурационный файл на основе `config/example_config.yaml`
2. Запустите обработку:

```bash
python -m video_pipeline.main --config config/your_config.yaml
```

## Конфигурация

Пример конфигурационного файла:

```yaml
input: input.mp4
output: output.mp4
modules:
- name: resize
  params:
    width: 1920
    height: 1080
    keep_aspect_ratio: true
- name: watermark
  params:
    image_path: watermark.png
    position: bottomright
    opacity: 0.7
```

## Требования

- Python 3.8+
- FFmpeg
- Зависимости из requirements.txt

## Лицензия

MIT
