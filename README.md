# Setup .env file
- `EMAIL_IMAP_USERNAME` - email username
- `EMAIL_IMAP_PASSWORD` - email password
- `EMAIL_IMAP_HOST` - email host
- `EMAIL_IMAP_PORT` - email port
- `EMAIL_IMAP_SSL` - email ssl
- `EMAIL_IMAP_FOLDER` - email folder
- `EMAILS_DATA_PATH` - emails JSON (storage) and XLSX (output) file location (no tailing /)
# Usage
```
pip install -r requirements.txt
python main.py
```
# Docker compose usage (with supercronic)
```
docker compose up -d --build
```