FROM python:3.11-slim

WORKDIR /app

# Set timezone to Europe/Dublin
RUN apt-get update && apt-get install -y tzdata && \
    ln -fs /usr/share/zoneinfo/Europe/Dublin /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata && \
    apt-get clean

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create a volume for the database persistence
VOLUME /app/data

# Environment variable for DB path to use the volume
ENV DB_PATH=/app/data/bot.db

CMD ["python", "bot.py"]
