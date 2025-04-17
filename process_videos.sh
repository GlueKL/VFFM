#!/bin/bash

source venv/bin/activate

WORKSPACE_DIR="workspace/pornushka"
ASMR_DIR="$WORKSPACE_DIR/ASMR"
ROBLOX_DIR="$WORKSPACE_DIR/ROBLOX"
OUTPUT_DIR="$WORKSPACE_DIR/OUTPUT"
TEMP_DIR="$WORKSPACE_DIR/TEMP"

# Создаем папку для выходных файлов если её нет
mkdir -p $ROBLOX_DIR $ASMR_DIR $OUTPUT_DIR $TEMP_DIR

# Счетчик для выходных файлов
counter=1

# Создаем массивы для файлов
asmr_files=($ASMR_DIR"/"*)
roblox_files=($ROBLOX_DIR"/"*)

# Определяем количество пар для обработки
num_pairs=$(( ${#asmr_files[@]} < ${#roblox_files[@]} ? ${#asmr_files[@]} : ${#roblox_files[@]} ))

# Функция для отображения прогресс-бара
show_progress() {
    local current=$1
    local total=$2
    local width=50
    local percentage=$((current * 100 / total))
    local completed=$((width * current / total))
    local remaining=$((width - completed))
    
    printf "\r["
    printf "%${completed}s" | tr " " "="
    printf ">"
    printf "%${remaining}s" | tr " " " "
    printf "] %3d%%" "$percentage"
}

# Обрабатываем пары файлов
for (( i=0; i<num_pairs; i++ )); do
    asmr_file="${asmr_files[i]}"
    roblox_file="${roblox_files[i]}"
    
    # Показываем прогресс
    show_progress $((i + 1)) $num_pairs
    echo -e "\nОбработка пары $((i+1))/$num_pairs"
    
    # Проверяем что оба файла существуют
    if [ -f "$asmr_file" ] && [ -f "$roblox_file" ]; then
        echo "ASMR: $(basename "$asmr_file")"
        echo "Roblox: $(basename "$roblox_file")"
        mkdir -p $TEMP_DIR
        # Копируем файлы с нужными именами
        cp "$asmr_file" "$TEMP_DIR/1.mp4"
        cp "$roblox_file" "$TEMP_DIR/2.mp4"
        
        # Запускаем основной pipeline
        video-pipeline process -c configs/config.yaml
        
        # Перемещаем финальный результат в папку out
        mv output.mp4 "$OUTPUT_DIR/$counter.mp4"
        echo "Создан файл: $OUTPUT_DIR/$counter.mp4"
        ((counter++))
        
        # Удаляем временные файлы
        rm -f -r "$TEMP_DIR"
    fi
done
rm -f -r "$TEMP_DIR"
echo -e "\nОбработка завершена. Создано $((counter-1)) видео." 