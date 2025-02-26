FROM python:3.9

WORKDIR /app

COPY requirements.txt ./
RUN pip install --upgrade pip setuptools wheel && pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["sh", "-c", "[ ! -f db/media_feedback.db ] && python db/setup.py; gunicorn -w 4 -b 0.0.0.0:5000 run:app"]