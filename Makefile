.PHONY: migration migrate rollback db-shell server-shell logs clean

# Generate a new migration
migration:
	@read -p "Enter migration message: " msg; \
	docker compose run --rm server sh -c "cd server && python -m alembic revision --autogenerate -m \"$$msg\""

# Apply migrations
migrate:
	docker compose run --rm server sh -c "cd server && python -m alembic upgrade head"

# Rollback one migration
rollback:
	docker compose run --rm server sh -c "cd server && python -m alembic downgrade -1"

# Database shell
db-shell:
	docker compose exec db psql -U servp -d servp

# Server shell
server-shell:
	docker compose exec server sh

# View logs
logs:
	docker compose logs -f

# Clean up
clean:
	docker compose down -v
	rm -rf db_data uploads

# Start services
up:
	docker compose up -d

# Stop services
down:
	docker compose down

# Rebuild and start
rebuild:
	docker compose up --build -d