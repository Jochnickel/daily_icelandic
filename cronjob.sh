cd "$(dirname "$0")"
timeout 60 ./background.sh & timeout 60 python3 ../telegram_bot_lua/main.py
