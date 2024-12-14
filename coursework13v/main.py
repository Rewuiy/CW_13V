from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates # рендеринг HTML-страниц
from pydantic import BaseModel
from typing import Optional
import asyncpg # фреймворк для работы с БД PostgreSQL
from fastapi.staticfiles import StaticFiles # для отображения фона 
import os # Стандартная библиотека Python для работы с операционной системой
# Инициализация приложения и шаблонов
app = FastAPI() # Создание экземпляра приложения FastAPI
templates = Jinja2Templates(directory="templates") # Указание директории templates для хранения шаблонов

# Подключение к базе данных
# DB_HOST = 'localhost'
# DB_USER = 'postgres'
# DB_PASSWORD = 'postgres'
# DB_NAME = 'coursework'
DB_HOST=os.getenv("DB_HOST", "postgres")
DB_USER=os.getenv("DB_USER", "postgres")
DB_PASSWORD=os.getenv("DB_PASSWORD", "postgres")
DB_NAME=os.getenv("DB_NAME", "coursework")

# Эта функция создаёт асинхронное подключение к базе данных PostgreSQL с использованием библиотеки asyncpg
async def get_db_connection():
    return await asyncpg.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)

# Pydantic модели

class Module(BaseModel):
    module_name: str
    language: Optional[str] = None
    lines: Optional[str] = None

class Program(BaseModel):
    program_name: str
    module_1: Optional[str] = None
    module_2: Optional[str] = None
    module_3: Optional[str] = None

app.mount("/static",StaticFiles(directory="static"), name='background') # Этот фрагмент монтирует директорию static для обслуживания статических файлов через URL /static

# Главная страница
@app.get("/", response_class=HTMLResponse) # Декорирует функцию как обработчик GET-запросов на корневой путь, определяет тип ответа как HTML
async def main(request: Request):
    conn = await get_db_connection() # Устанавливает соединение с базой данны
    # Изначально пустые списки, которые передаются в шаблон
    programs= []
    modules =[]
    await conn.close() # Закрывает соединение с базой данных

    return templates.TemplateResponse("mainpage.html", {"request": request, "programs": programs, "modules": modules}) # Рендерит шаблон mainpage.html с передачей контекста (запроса, списков программ и модулей)

# Маршруты для управления страницами
@app.get("/add_program_page", response_class=HTMLResponse) # маршрут для отображения формы ввода полей записи сущности программ
async def add_program_page(request: Request):
    return templates.TemplateResponse("add_program.html", {"request": request})

@app.get("/add_module_page", response_class=HTMLResponse) # маршрут для отображения формы ввода полей записи сущности модулей
async def add_module_page(request: Request):
    return templates.TemplateResponse("add_module.html", {"request": request})

# Функция для добавления программы
@app.post("/add_program") # Обработчик POST-запросов для добавления программы. Он принимает параметры name_program, module_1, module_2, module_3 и вставляет их в базу данных. В случае ошибки возвращает шаблон с сообщением об ошибке
async def add_program(
    request: Request,
    name_program: str = Form(...),
    module_1: Optional[str] = Form(None),
    module_2: Optional[str] = Form(None),
    module_3: Optional[str] = Form(None)
):
    conn = await get_db_connection()
    try:
        # Добавление новой программы
        await conn.execute("INSERT INTO programs (program_name, module_1, module_2, module_3) VALUES ($1, $2, $3, $4)", name_program, module_1, module_2, module_3)
    except Exception as e:
        message =(f"Ошибка: {str(e)}")
        await conn.close()
        return templates.TemplateResponse("add_program.html", {"request": request, "message":message})
    await conn.close()
    message = "Запись успешно добавлена"
    return templates.TemplateResponse("add_program.html", {"request": request, "message":message})

# Функция для добавления модуля
@app.post("/add_module")
async def add_module(
    request: Request,
    name_module: str = Form(...),
    language: Optional[str] = Form(None),
    lines_of_code: int = Form(None)
):
    conn = await get_db_connection()
    try:
        # Добавление нового модуля
        await conn.execute("INSERT INTO modules (module_name, language, lines) VALUES ($1, $2, $3)",name_module, language, lines_of_code)
    except Exception as e:
        message = (f"Ошибка: {str(e)}")
        await conn.close()
        return templates.TemplateResponse("add_module.html", {"request": request, "message":message})
    await conn.close()
    message = "Запись успешно добавлена"
    return templates.TemplateResponse("add_module.html", {"request": request, "message":message})

# Маршруты для управления страницами
@app.get("/delete_program/{program_name}", response_class=RedirectResponse)
async def delete_program(program_name: str):
    conn = await get_db_connection()
    try:
        # Удаляем программу по ID
        await conn.execute("DELETE FROM programs WHERE program_name = $1", program_name)
    except Exception as e:
        print(f"Ошибка при удалении программы: {str(e)}")
    finally:
        await conn.close()
    return RedirectResponse("/", status_code=303)

@app.get("/delete_module/{module_name}", response_class=RedirectResponse) # получение информации для формирования запроса для удлаени модуля
async def delete_module(module_name: str):
    conn = await get_db_connection()
    try:
        # Удаляем модуль по ID
        await conn.execute("DELETE FROM modules WHERE module_name = $1", module_name)
    except Exception as e:
        print(f"Ошибка при удалении модуля: {str(e)}")
    finally:
        await conn.close()
    return RedirectResponse("/", status_code=303)

@app.post("/delete_program_attribute") # удаление атрибута програм
async def delete_program_attribute(
    request: Request,
    program_name: str = Form(...),
    attribute_name: str = Form(...),
):
    conn = await get_db_connection()
    try:
        # Удаляем атрибут программы
        await conn.execute(f"UPDATE programs SET {attribute_name} = NULL WHERE program_name = $1", program_name) # удалить выбранные атрибуты
    except Exception:
        return RedirectResponse("/", status_code=404)
    finally:
        await conn.close()
    return RedirectResponse("/", status_code=303)

@app.post("/delete_module_attribute") # Декоратор, который указывает, что данная функция будет обрабатывать GET-запросы. Маршрут, по которому будут обрабатываться запросы. {module_name} означает, что часть URL после delete_module/ будет передана в функцию как параметр module_name. Указывает, что ответ от этой функции будет типа RedirectResponse, т.е. это перенаправление на другой URL
async def delete_module_attribute(request: Request, module_name: str = Form(...), attribute_name: str = Form(...),): # Функция объявлена как асинхронная, чтобы можно было использовать await внутри неё. Имя функции. Аргумент функции, который представляет собой строку с именем модуля, передаваемую из URL
    conn = await get_db_connection() # Вызывается функция для установления соединения с базой данных. Ожидает завершения асинхронной операции до продолжения выполнения следующего шага. Переменная, которая хранит объект соединения с базой данных
    try: # Блок для обработки исключений. Все действия внутри блока будут выполнены, если не возникнет ошибка
        # Удаляем атрибут модуля
        await conn.execute(f"UPDATE modules SET {attribute_name} = NULL WHERE module_name = $1", module_name) # Выполняется асинхронное удаление записи из таблицы modules, где поле module_name соответствует переданному значению module_name и выполнение SQL-запроса для удаления записи
    except Exception as e: # Обработчик исключений. Если в блоке try возникает исключение, выполнение перейдет сюда
        print(f"Ошибка: {str(e)}") # Выводится сообщение об ошибке вместе с текстом исключения
    finally: # Блок выполняется всегда, независимо от того, возникло ли исключение или нет
        await conn.close() # Закрывается соединение с базой данных
    return RedirectResponse("/", status_code=303) # Возвращается ответ с типом RedirectResponse, который перенаправляет клиента на главную страницу с кодом состояния HTTP, указывающий на временное перенаправление

# Новый маршрут для поиска
@app.get("/search", response_class=HTMLResponse)
async def search(request: Request, search_value: str, attribute: str): # Атрибут, по которому производится поиск
    conn = await get_db_connection()
    
    try:
        if attribute == "program_name": # Проверка, что атрибут равен program_name
            query = "SELECT * FROM programs WHERE program_name ILIKE $1" # Формирование SQL-запроса для поиска всех записей в таблице programs, где поле program_name содержит подстроку, введенную пользователем
            modules = [] # Инициализируется пустой список для модулей, так как мы ищем только программы
            results = await conn.fetch(query, f"%{search_value}%") # Выполняется запрос к базе данных с использованием параметра, который ищет совпадения по подстроке
            return templates.TemplateResponse("mainpage.html", {"request": request, "programs": results, "modules": modules}) # Возвращается шаблон mainpage.html с результатами поиска
        elif attribute == "module_name": # Проверка, что атрибут равен module_name
            query = "SELECT * FROM modules WHERE module_name ILIKE $1" # Формирование SQL-запроса для поиска всех записей в таблице modules, где поле module_name содержит подстроку, введенную пользователем
            programs = [] # Инициализируется пустой список для программ, так как мы ищем только модули
            results = await conn.fetch(query, f"%{search_value}%") # Выполняется запрос к базе данных с использованием параметра, который ищет совпадения по подстроке
            return templates.TemplateResponse("mainpage.html", {"request": request, "programs": programs, "modules": results}) # Возвращается шаблон mainpage.html с результатами поиска
        elif attribute == "language": # Проверка, что атрибут равен language
            query = "SELECT * FROM modules WHERE language LIKE $1" # Формирование SQL-запроса для поиска всех записей в таблице modules, где поле language содержит подстроку, введенную пользователем
            programs = [] # Инициализируется пустой список для программ, так как мы ищем только модули
            results = await conn.fetch(query, f"%{search_value}%") # Выполняется запрос к базе данных с использованием параметра, который ищет совпадения по подстроке
            return templates.TemplateResponse("mainpage.html", {"request": request, "programs": programs, "modules": results}) # Возвращается шаблон mainpage.html с результатами поиска
        elif attribute == "lines": # Проверка, что атрибут равен lines
            query = "SELECT * FROM modules WHERE lines = $1" # Формирование SQL-запроса для поиска всех записей в таблице modules, где поле lines равно числу, введенному пользователем
            programs = [] # Инициализируется пустой список для программ, так как мы ищем только модули
            results = await conn.fetch(query, int(search_value)) # Выполняется запрос к базе данных с использованием числового значения для точного сравнения
            return templates.TemplateResponse("mainpage.html", {"request": request, "programs": programs, "modules": results}) # Возвращается шаблон mainpage.html с результатами поиска
        else:
            query = "" # Если ни одно условие выше не выполнено, то присваивается пустое значение для запроса
        
        # Выполнение запроса
        if attribute in ["program_name", "module_name", "language"]:
            results = await conn.fetch(query, f"%{search_value}%")
        else:  # Для поля "lines"
            results = await conn.fetch(query, int(search_value))
            
        return templates.TemplateResponse("mainpage.html", {"request": request, "programs": programs, "modules": results})

    except Exception as e:
        results = []
        print(f"Ошибка: {e}")
    finally:
        await conn.close()

    # Передаем данные на шаблон
    return templates.TemplateResponse("mainpage.html", {"request": request, "programs": results, "modules": results})

@app.get("/view_db", response_class=HTMLResponse) # Маршрут для просмотра всей базы данных
async def view_db(request: Request):
    conn = await get_db_connection()
    try:
        # Запрос для получения связанных модулей
        query_connected_modules = """ 
        SELECT 
            p.program_name, 
            p.module_1, 
            p.module_2, 
            p.module_3, 
            m.module_name AS module_name, 
            m.language AS module_language, 
            m.lines AS module_lines
        FROM 
            programs p
        INNER JOIN modules m ON 
            m.module_name IN (p.module_1, p.module_2, p.module_3);
        """

        connected_data = await conn.fetch(query_connected_modules) # Выполняет запрос к базе данных и сохраняет полученные данные в переменной connected_data

        # Запрос для получения несвязанных модулей
        query_unconnected_modules = """
        SELECT 
            m.module_name, 
            m.language, 
            m.lines
        FROM 
            modules m
        LEFT JOIN programs p 
            ON m.module_name = p.module_1 
               OR m.module_name = p.module_2 
               OR m.module_name = p.module_3
        WHERE 
            p.program_name IS NULL;
        """

        unconnected_data = await conn.fetch(query_unconnected_modules) # Выполняет запрос к базе данных и сохраняет полученные данные в переменной unconnected_data

        # SQL-запрос для получения информации о программах, которые не содержат модулей.
        query_unconnected_programs = """ SELECT program_name FROM programs WHERE module_1 IS NULL AND module_2 IS NULL AND module_3 IS NULL; """
        unconnected_programs = await conn.fetch(query_unconnected_programs) # Выполняет запрос к базе данных и сохраняет полученные данные в переменной unconnected_programs

        # Объединение результатов
        data = connected_data + unconnected_data + unconnected_programs

    except Exception:
        data = [] # Если произошла ошибка, сбрасываются данные
    finally:
        await conn.close()

    # Передача объединенных данных на шаблон
    return templates.TemplateResponse("view_db.html", {"request": request, "data": data}) # Возвращает шаблон для отображения страницы с объединенными данными

# Запуск приложения
if __name__ == "__main__": # проверка, выполняется ли данный файл как основной скрипт, а не импортируется как модуль
    import uvicorn # импорт библиотеки uvicorn, используемой для запуска и обслуживания HTTP-сервера
    uvicorn.run(app, host="0.0.0.0", port=8091) # запуск приложения порт 8091