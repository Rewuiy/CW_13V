# Используем официальный Python образ как базовый
FROM python:3.11-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файлы проекта в контейнер
COPY . /app/
# Устанавливаем зависимости проекта
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Открываем порт, на котором будет работать приложение
EXPOSE 8091

# Команда для запуска FastAPI приложения с помощью Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8091"]