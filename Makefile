start:
	uvicorn app:app --host 0.0.0.0 --port 8002 --reload
docker:
	docker compose up -d --build --remove-orphans

