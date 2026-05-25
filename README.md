# Infoboard (Vue + FastAPI + PostgreSQL)

This project uses:

- Frontend: Vue 3 + Vite (JavaScript), Vue Router, Pinia, ESLint, Prettier
- Backend: FastAPI + SQLModel
- Database: PostgreSQL
- Deployment: Docker Compose

## Quick start

Run following command at the root of the project

```sh
docker compose -f docker-compose.yml up -d --build
```

This will build the images and run the containers of the project.

For environmental varibales needed to run the project check `.env.example` files.
