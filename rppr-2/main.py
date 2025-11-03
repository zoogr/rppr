from fastapi import FastAPI, HTTPException
from datetime import datetime
import json
import os
from typing import List
from models import AppealCreate

# Создаем экземпляр FastAPI
app = FastAPI(
    title="Сервис сбора обращений абонентов",
    description="Сервис для приема и валидации обращений абонентов",
    version="1.0.0"
)

# Папка для хранения файлов
STORAGE_DIR = "storage"
os.makedirs(STORAGE_DIR, exist_ok=True)


def save_appeal_to_file(appeal_data: dict) -> str:
    """
    Сохраняет данные обращения в JSON файл
    """
    # Создаем уникальное имя файла на основе timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"appeal_{timestamp}.json"
    filepath = os.path.join(STORAGE_DIR, filename)

    # Сохраняем данные в файл
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(appeal_data, f, ensure_ascii=False, indent=2)

    return filename


@app.post("/appeals/", summary="Создать новое обращение")
async def create_appeal(appeal: AppealCreate):
    """
    Создает новое обращение абонента с валидацией данных.

    - **last_name**: Фамилия (кириллица, с заглавной буквы)
    - **first_name**: Имя (кириллица, с заглавной буквы)
    - **birth_date**: Дата рождения
    - **phone_number**: Номер телефона
    - **email**: E-mail адрес
    """
    try:
        # Преобразуем модель в словарь
        appeal_data = appeal.model_dump()

        # Добавляем timestamp создания
        appeal_data['created_at'] = datetime.now().isoformat()

        # Сохраняем в файл
        filename = save_appeal_to_file(appeal_data)

        return {
            "message": "Обращение успешно создано",
            "filename": filename,
            "data": appeal_data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при сохранении обращения: {str(e)}")


@app.get("/appeals/list", summary="Получить список всех обращений")
async def list_appeals():
    """
    Возвращает список всех сохраненных обращений
    """
    try:
        appeals = []

        # Читаем все JSON файлы из папки storage
        for filename in os.listdir(STORAGE_DIR):
            if filename.endswith('.json'):
                filepath = os.path.join(STORAGE_DIR, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    appeal_data = json.load(f)
                    appeals.append({
                        "filename": filename,
                        "data": appeal_data
                    })

        return {
            "total": len(appeals),
            "appeals": appeals
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при чтении обращений: {str(e)}")


@app.get("/")
async def root():
    return {
        "message": "Сервис сбора обращений абонентов",
        "version": "1.0.0",
        "endpoints": {
            "create_appeal": "POST /appeals/",
            "list_appeals": "GET /appeals/list"
        }
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)