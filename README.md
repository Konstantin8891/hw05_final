# Yatube social network

89670253660@mail.ru

+79117836285 WhatsApp, Telegram

Yatube social network

Post your images, video, text. Comment posts. Subscribe to authors. Based on Django framework 2.2.28. All dependencies are in requirements.txt.

Project uploaded to konstantin06.pythonanywhere.com

## System requirements:
- Install Python 3.7 and prepare enviroment
Install software: download and run files
Python: www.python.org/downloads/ устанавливаем Python 3.7
Visual Studio Code: code.visualstudio.com/download
Git: git-scm.com/download/win
- Terminal for Unix systems or emulator of terminal for Windows
> Everything else will be installed during steps below


1. Clone project 

git@github.com:Konstantin8891/hw05_final.git

2. cd hw05_final

3. Create virtual environment
 
python -m venv env

or

python3 -m venv venv

4. Activate virtual environment 

source venv/scripts/activate

or

. venv/bin/activate

5. Upgrade pip 

python -m pip install --upgrade pip

6. Install all requirements 

pip install -r requirements.txt

7. Make migrations

python manage.py migrate

8. Run project

python manage.py runserver

9. Now you're able to use all functionality at 

http://127.0.0.1:8000/

