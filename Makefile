# Makefile для управления Telegram-ботом в Docker

APP_NAME=bybit_trading_bot

up:
	docker compose up --build -d

down:
	docker compose down

stop:
	docker stop $(APP_NAME) || true
	docker rm $(APP_NAME) || true

rebuild:
	git pull
	docker compose down
	docker compose up --build -d

logs:
	docker logs -f $(APP_NAME)

clean:
	docker compose down --rmi all --volumes --remove-orphans

shell:
	docker exec -it $(APP_NAME) /bin/bash

env:
	cp .env.example .env
	echo "⚠️  Обнови .env с реальными токенами!"

status:
	docker ps -a | grep $(APP_NAME)
