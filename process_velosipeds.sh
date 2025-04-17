#!/bin/bash

source venv/bin/activate

# Добавляем текущую директорию в PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Пути к директориям
FOOTAGES_DIR="workspace/velosiped/footages"
INPUT_DIR="workspace/velosiped/velo_parts"
OUTPUT_DIR="workspace/velosiped/output"
CONFIG_FOOTAGES_DIR="workspace/velosiped/footages_config"

# Создаем директории, если они не существуют
mkdir -p "$OUTPUT_DIR"

# Определяем конфиги для каждого футажа
declare -A configs
configs["испания 1"]="$CONFIG_FOOTAGES_DIR/config_create_velosipedes_1.yaml"
configs["испания 2"]="$CONFIG_FOOTAGES_DIR/config_create_velosipedes_2.yaml"
configs["испания 3"]="$CONFIG_FOOTAGES_DIR/config_create_velosipedes_3.yaml"
configs["испания 4"]="$CONFIG_FOOTAGES_DIR/config_create_velosipedes_4.yaml"

# Получаем список футажей и входных видео
footages=($FOOTAGES_DIR/*)
inputs=($INPUT_DIR/*)

# Проверяем, что у нас есть и футажи, и входные видео
if [ ${#footages[@]} -eq 0 ]; then
    echo "Нет футажей в директории $FOOTAGES_DIR"
    exit 1
fi

if [ ${#inputs[@]} -eq 0 ]; then
    echo "Нет входных видео в директории $INPUT_DIR"
    exit 1
fi

# Обрабатываем входные видео
for ((i=0; i<${#inputs[@]}; i++)); do
    input="${inputs[$i]}"
    # Вычисляем индекс футажа для текущего входного видео
    footage_index=$((i % ${#footages[@]}))
    footage="${footages[$footage_index]}"
    
    # Получаем имена файлов без расширения
    input_name=$(basename "$input")
    input_name="${input_name%.*}"
    footage_name=$(basename "$footage")
    footage_name="${footage_name%.*}"
    
    echo "Обработка $input_name с футажем $footage_name"
    
    # Копируем входное видео под именем из конфига
    cp "$input" "workspace/velosiped/input.mp4"
    
    # Копируем футаж под именем из конфига
    cp "$footage" "workspace/velosiped/working_footage.mp4"
    
    # Запускаем обработку видео с соответствующим конфигом
    video-pipeline process -c "${configs[$footage_name]}"
    
    # Переименовываем выходной файл
    if [ -f "workspace/velosiped/output.mp4" ]; then
        mv "workspace/velosiped/output.mp4" "$OUTPUT_DIR/output_${input_name}_${footage_name}.mp4"
    else
        echo "Ошибка: выходной файл не создан для $input_name с футажем $footage_name"
    fi
    
    # Удаляем временные файлы
    rm -f "workspace/velosiped/input.mp4"
    rm -f "workspace/velosiped/working_footage.mp4"
done

echo "Обработка завершена!" 