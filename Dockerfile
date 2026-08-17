FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py logger.py ./
COPY drive_utils/__init__.py drive_utils/drive_operations.py ./drive_utils/

CMD ["python", "main.py"]
