#!/bin/bash

source venv/bin/activate

# Пути к директориям
SOURCE_DIR="workspace/velosiped/velosipeds"
CONFIG_FILE="configs/config_cut_velosiped.yaml"
OUTPUT_DIR="workspace/velosiped/velo_parts"

mkdir -p "$SOURCE_DIR"
mkdir -p "$OUTPUT_DIR"


# Обрабатываем каждый видеофайл
for video in "$SOURCE_DIR"/*.mp4; do
    if [ -f "$video" ]; then
        echo "Processing $video..."
        
        # Запускаем обработку через video-pipeline
        python -m video_pipeline.cli process \
            -c "$CONFIG_FILE" \
            -i "$video"
            
        if [ $? -eq 0 ]; then
            echo "Successfully processed $video"
        else
            echo "Error processing $video"
        fi
    fi
done


# Удаляем видео, если они короче 40 секунд
for video in "$OUTPUT_DIR"/*.mp4; do
    if [ -f "$video" ]; then
        # Получаем длительность видео в секундах
        duration=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$video")
        
        # Проверяем длительность
        if (( $(echo "$duration < 40" | bc -l) )); then
            echo "Удаляем $video с длительностью $duration секунд..."
            rm "$video"
        fi
    fi
done

echo "All videos processed!" 