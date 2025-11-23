# Інструкція з деплою (Deployment Guide)

## 1. Локально (на твоєму комп'ютері)

Завантаж код на GitHub/GitLab:

```bash
# Ініціалізуй репозиторій (якщо ще не зробив)
git init

# Додай файли (завдяки .gitignore секрети не додадуться)
git add .

# Зроби коміт
git commit -m "Initial commit: Telegram bot with Docker"

# Додай посилання на твій репозиторій (створи його на GitHub)
git remote add origin https://github.com/your-username/your-repo.git

# Відправ код
git push -u origin master
```

## 2. На сервері

Підключись до сервера через SSH і виконай:

```bash
# 1. Клонуй репозиторій (або зроби git pull, якщо папка вже є)
git clone https://github.com/your-username/your-repo.git
cd your-repo/telegram_bot

# 2. Створи файл .env (це треба зробити вручну, бо він не в гіті!)
nano .env
```

Встав у файл `.env` свої дані:

```
BOT_TOKEN=your_token_here
ADMIN_ID=your_admin_id
```

(Натисни `Ctrl+O`, `Enter` щоб зберегти, і `Ctrl+X` щоб вийти)

```bash
# 3. Запусти бота через Docker
docker-compose up -d --build
```

## Корисні команди

- **Перевірити статус**: `docker-compose ps`
- **Дивитися логи**: `docker-compose logs -f`
- **Зупинити**: `docker-compose down`
- **Оновити код**:
  ```bash
  git pull
  docker-compose up -d --build
  ```

## Альтернатива: Запуск через tmux (щоб бачити логи)

Якщо хочеш запустити бота і бачити логи, але мати змогу закрити термінал:

1. **Створи сесію**:

   ```bash
   tmux new -s bot
   ```

2. **Запусти бота** (без -d):

   ```bash
   docker-compose up --build
   ```

3. **Вийди з сесії** (залиш бота працювати):
   Натисни `Ctrl+B`, відпусти, потім натисни `D`.

4. **Повернутися до бота**:
   ```bash
   tmux attach -t bot
   ```
