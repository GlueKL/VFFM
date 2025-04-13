#!/bin/bash

source venv/bin/activate

# Пути к директориям
SOURCE_DIR="workspace/velosiped/velosipeds"
CONFIG_FILE="configs/config_cut_velosiped.yaml"

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

echo "All videos processed!" 