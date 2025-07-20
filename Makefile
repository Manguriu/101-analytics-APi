# Makefile for Dockerized Django Project

# Build image and run containers (rebuilds if needed)
build:
	docker-compose up --build

# Clean everything and rebuild from scratch
rebuild:
	docker-compose down --volumes && docker-compose up --build

# Start the app using existing image (no rebuild)
start:
	docker-compose up

# Stop and remove containers + volumes
clean:
	docker-compose down --volumes

# Shell access to the app container
shell:
	docker-compose exec app sh

# Run Django migrations
migrate:
	docker-compose exec app python manage.py migrate

# Create Django superuser
createsuperuser:
	docker-compose exec app python manage.py createsuperuser

# Collect static files
collectstatic:
	docker-compose exec app python manage.py collectstatic --noinput

# Tail app logs
logs:
	docker-compose logs -f app

	

images:
	docker-compose images


# | Task                              | Command                |
# | --------------------------------- | ---------------------- |
# | Build and run app                 | `make build`           |
# | Start app using existing image    | `make start`           |
# | Stop everything and clean volumes | `make clean`           |
# | Rebuild from scratch              | `make rebuild`         |
# | Run DB migrations                 | `make migrate`         |
# | Create superuser                  | `make createsuperuser` |
# | View logs                         | `make logs`            |
# | Get shell in container            | `make shell`           |
