# amogus
Утилита для предзаписи на модеус

## Запуск
1. Клонируй репозиторий
`git clone https://github.com/Matvke/amogus.git`
2. Перейди в рабочкую директорию
`cd amogus`
3. Создай виртуальное окружение
`python -m venv .venv`
4. Активируй виртуальное окружение
Windows
`.\venv\Scripts\activate`
Linux/MacOS
`source .venv/bin/activate`
5. Установи зависимости
`pip install -r requirements`
6. Получи код меню из URL меню выбора и впиши его в .env
`https://urfu.modeus.org/learning-path-selection/api/selection/menus/{menu_id}`
> Пример .env фала можешь посмотреть в .env.example
7. Получи JWT токен и запиши его в .env
    1) Для этого перейди на страницу выбора
    2) Перейди в панель админа `f12`
    3) Вкладка Storage -> Session Storage
    4) Скопируй значение `id_token` в .env в поле token
8. Запусти TUI приложение
`python3 tui-app.py` 