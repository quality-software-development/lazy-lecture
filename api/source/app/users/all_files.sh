#!/bin/bash

# Получаем текущую директорию
startFolder=$(pwd)

# Имя файла для записи результатов
outputFile="all_files.txt"

# Массивы для игнорирования папок и допустимых расширений файлов
ignoreFolders=("venv" "__pycache__" "dist" ".idea")    # Папки, которые нужно игнорировать
allowedExtensions=("sh" "py" "md" "frag" "vert" "ini")            # Допустимые расширения файлов

# Получаем имя текущего скрипта
scriptName=$(basename "$0")

# Очищаем или создаём файл для записи результатов
> "$outputFile"

# Функция для проверки, нужно ли игнорировать папку
function should_ignore_folder {
  local folder=$1
  for ignoreFolder in "${ignoreFolders[@]}"; do
    if [[ "$(basename "$folder")" == "$ignoreFolder" ]]; then
      return 0
    fi
  done
  return 1
}

# Функция для проверки, допустимо ли расширение файла
function is_allowed_file {
  local file=$1
  local extension="${file##*.}"
  for allowedExt in "${allowedExtensions[@]}"; do
    if [[ "$extension" == "$allowedExt" ]]; then
      return 0
    fi
  done
  return 1
}

# Функция для обработки файлов рекурсивно
function process_directory {
  local folder=$1
  for file in "$folder"/*; do
    # Проверяем, существует ли файл или папка (могут возникать ошибки с символическими ссылками)
    if [ ! -e "$file" ]; then
      continue
    fi

    # Если это директория, проверяем, нужно ли её игнорировать
    if [ -d "$file" ]; then
      if should_ignore_folder "$file"; then
        echo "Игнорируем папку: $file" >> "$outputFile"
      else
        # Если папку не нужно игнорировать, рекурсивно обрабатываем её
        process_directory "$file"
      fi
    elif [ -f "$file" ]; then
      # Пропускаем сам скрипт
      if [[ "$(basename "$file")" == "$scriptName" ]]; then
        continue
      fi

      # Проверяем, допустимо ли расширение файла
      if is_allowed_file "$file"; then
        # Если расширение файла допустимо, записываем путь и содержимое файла в выходной файл
        echo "Файл: $file" >> "$outputFile"
        echo "Содержимое:" >> "$outputFile"
        cat "$file" >> "$outputFile"
        echo -e "\n------------------------------------\n" >> "$outputFile"
      else
        echo "Пропускаем файл (недопустимое расширение): $file" >> "$outputFile"
      fi
    fi
  done
}

# Запускаем обработку с текущей директории
process_directory "$startFolder"

# Сообщаем, что результаты записаны
echo "Результаты записаны в файл $outputFile"
