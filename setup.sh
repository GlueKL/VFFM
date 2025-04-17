#!/bin/bash

# Проверка на root права
if [ "$EUID" -ne 0 ]; then
    echo "Ошибка: Этот скрипт должен быть запущен с правами root"
    echo "Пожалуйста, запустите скрипт с помощью sudo:"
    echo "sudo $0"
    exit 1
fi

# Установка необходимых пакетов
sudo apt-get update
sudo apt-get install -y \
    python3-pip \
    python3-venv \
    ffmpeg \
    pv \
    imagemagick \
    bc

# Создание виртуального окружения
python3 -m venv venv

# Активация виртуального окружения
source venv/bin/activate

# Установка зависимостей из requirements.txt
pip install -r requirements.txt

echo "Установка завершена!"

echo "Checking for FFmpeg..."
if ! command -v ffmpeg &> /dev/null; then
    echo "WARNING: FFmpeg not found. Please install it using your package manager."
fi

echo "Checking for ImageMagick..."
if ! command -v convert &> /dev/null; then
    echo "WARNING: ImageMagick not found. Please install it using your package manager."
fi

echo "Setup complete. Use 'source venv/bin/activate' to activate the environment." 