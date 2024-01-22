# Telegram reforward system

* Django Admin Panel
* Telegram Admin Bot
* filters
* rules

1) Copy .env.example to .env
2) Complete all data
3) Setup env for session creator
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
4) Create a session using the following command: `python create_pyrogram_session.py`
5) Get the Docker image: `docker compose pull` or build it:`docker compose build`
6) Run the Docker containers: `docker compose up -d`
7) Create admin account `docker compose exec web bash` & [IN THE CONTAINER] `python manage.py createsuperuser`
