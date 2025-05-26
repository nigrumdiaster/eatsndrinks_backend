@echo off
call .\env\Scripts\activate
cd eatsndrinks
python manage.py runserver
