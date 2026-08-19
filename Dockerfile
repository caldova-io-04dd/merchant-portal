FROM python:3.11-slim

WORKDIR /app

COPY wheelhouse ./wheelhouse
COPY merchant-portal/requirements.txt ./requirements.txt
RUN pip install --no-index --find-links=/app/wheelhouse --no-cache-dir -r requirements.txt

COPY merchant-portal/ ./

EXPOSE 5000

CMD ["sh", "-c", "python migrations/init_db.py && python run.py"]
