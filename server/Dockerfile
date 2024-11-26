# 1 
FROM python:3.9

# 2
RUN pip install --upgrade pip
RUN pip install Flask gunicorn
RUN pip install Flask-WTF
RUN pip install flask-login
RUN pip install flask-mail
RUN pip install WTForms
RUN pip install pytz
RUN pip install firebase_admin

# 3
COPY src/ /app
WORKDIR /app

# 4
ENV PORT 8080

# 5
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 app:app