cd "$(dirname "$0")"
timeout 60 python3 ./main.py & sleep 30; timeout 30 python3 ./main.py
