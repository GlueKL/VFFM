#!/bin/bash

source venv/bin/activate
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Функция для определения цвета по конкретной координате
get_dominant_color() {
    local video="$1"
    local temp_dir="workspace/velosiped/temp"
    mkdir -p "$temp_dir"
    
    # Извлекаем кадр из середины видео
    local duration=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$video")
    local middle_time=$(echo "$duration / 2" | bc -l)
    local temp_frame="$temp_dir/temp_frame.png"
    
    ffmpeg -ss "$middle_time" -i "$video" -vframes 1 -f image2 "$temp_frame" -y 2>/dev/null
    
    # Получаем цвет в конкретной точке (40, 40)
    local color=$(convert "$temp_frame" -format "%[pixel:p{40,40}]" info:-)
    
    # Преобразуем в формат 0xRRGGBB
    color=$(echo "$color" | sed 's/rgb(//' | sed 's/)//' | awk -F, '{printf "0x%02X%02X%02X", $1, $2, $3}')
    
    # Очищаем временные файлы
    rm -f "$temp_frame"
    
    echo "$color"
}

# Пути к директориям
FOOTAGES_DIR="workspace/velosiped/footages"
INPUT_DIR="workspace/velosiped/velo_parts"
OUTPUT_DIR="workspace/velosiped/output"
CONFIG_FOOTAGES_DIR="workspace/velosiped/footages_config"
TEMP_CONFIG_DIR="$CONFIG_FOOTAGES_DIR/temp"

# Создаем директории
mkdir -p "$OUTPUT_DIR"
mkdir -p "$TEMP_CONFIG_DIR"

# Получаем списки файлов
footages=($FOOTAGES_DIR/*)
inputs=($INPUT_DIR/*)

# Проверяем наличие файлов
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
    footage_index=$((i % ${#footages[@]}))
    footage="${footages[$footage_index]}"
    
    input_name=$(basename "$input")
    input_name="${input_name%.*}"
    footage_name=$(basename "$footage")
    footage_name="${footage_name%.*}"
    
    echo "Обработка $input_name с футажем $footage_name"
    
    # Определяем цвет фона для футажа по координате (40, 40)
    echo "Определяем цвет фона по координате (40, 40)..."
    background_color=$(get_dominant_color "$footage")
    echo "Определен цвет фона: $background_color"
    
    # Создаем временный конфигурационный файл
    temp_config="$TEMP_CONFIG_DIR/config_${input_name}_${footage_name}.yaml"
    cat > "$temp_config" << EOF
input: "workspace/velosiped/input.mp4"
output: "workspace/velosiped/output.mp4"

modules:
  - name: utility.prepare_for_yt
  - name: delete_audio
  - name: resize
    params:
      width: 1920
      height: 1080
  - name: crop
    params:
      width: 540
      height: 960
      position: "center"
  - name: resize
    params:
      width: 1080
      height: 1920
  - name: chromakey 
    params:
      color: "$background_color"
      similarity: 0.1
      blend: 0.5
      overlay: "workspace/velosiped/working_footage.mp4"
      position: "center"
      width: 1080
      height: 1920
      mute_overlay: false
      audio_codec: "copy"
  - name: utility.prepare_for_yt
EOF
    
    # Копируем файлы
    cp "$input" "workspace/velosiped/input.mp4"
    cp "$footage" "workspace/velosiped/working_footage.mp4"
    
    # Запускаем обработку
    echo "Запускаем обработку с автоматически определенным цветом фона..."
    video-pipeline process -c "$temp_config"
    
    # Перемещаем результат
    if [ -f "workspace/velosiped/output.mp4" ]; then
        mv "workspace/velosiped/output.mp4" "$OUTPUT_DIR/output_${input_name}_${footage_name}.mp4"
        echo "Успешно создан файл: output_${input_name}_${footage_name}.mp4"
    else
        echo "Ошибка: выходной файл не создан для $input_name с футажем $footage_name"
    fi
    
    # Очищаем временные файлы
    rm -f "workspace/velosiped/input.mp4"
    rm -f "workspace/velosiped/working_footage.mp4"
    rm -f "$temp_config"
done

# Очищаем временную директорию
rm -rf "$TEMP_CONFIG_DIR"

echo "Обработка завершена!" 