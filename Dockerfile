
# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем все файлы в контейнер
COPY . .

# Установка зависимостей
RUN pip install --upgrade pip && pip install -r requirements.txt

# Запуск бота
CMD ["python", "main.py"]
