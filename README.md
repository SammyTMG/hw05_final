## Социальная сеть Yatube

Социальная сеть повзоляет написание постов и публикации их в отдельных группах, подписки на посты, добавление и удаление записей и их комментирование. Подписки на любимых авторов.

Стек: Python 3.7, Django 2.2

### Инструкции по установке

- Клонируйте репозиторий:
```
git clone git@github.com:SammyTMG/hw05_final.git
```

- Переходим в папку с проектом:
```
cd hw05_final
```
- Установите и активируйте виртуальное окружение:
- 
для MacOS
```
python3 -m venv venv
source venv/bin/activate
```
для Windows
```
python -m venv venv
source venv/Scripts/activate
```
- Установите зависимости из файла requirements.txt:
```
pip install -r requirements.txt
```
- Примените миграции:
```
python yatube/manage.py makemigrations
python yatube/manage.py migrate
```
- В папке с файлом manage.py выполните команду:
```
python manage.py runserver
```
