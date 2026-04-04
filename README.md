sqlalchemy
# 📝 BlogAPI

A RESTful backend API for a blogging platform. Users can register, log in, write posts, comment, and like posts. Each user manages their own content. Built with FastAPI, SQLAlchemy, and JWT authentication.

---

## Features

- User registration and login (JWT-based authentication)
- Create, read, update, and delete posts (ownership enforced)
- Comment on posts
- Like and unlike posts
- Secure password hashing
- Proper project structure with routers, models, and schemas

---

## Tech Stack

- **Framework:** FastAPI
- **Database:** PostgreSQL (recommended, via asyncpg/psycopg2-binary), SQLite (via aiosqlite), SQLAlchemy ORM
- **Auth:** JWT (via PyJWT)
- **Password Hashing:** Argon2 (via pwdlib[argon2])
- **Settings Management:** pydantic-settings

---

## Project Structure

```
backend/
├── main.py
├── database.py
├── config.py
├── models/
├── schemas/
├── routers/
├── services/
└── dependencies.py
```

---

## Setup

1. **Clone the repo and enter the directory**
2. **Create a virtual environment and activate it**
3. **Install dependencies:**
	 ```
	 pip install -r requirements.txt
	 ```
4. **Set up your `.env` file** with:
	 ```
	 DB_URL=postgresql://user:password@host:port/dbname
	 SECRET_KEY=your_secret_key
	 ALGORITHM=HS256
	 ACCESS_TOKEN_EXPIRE_MINUTES=30
	 ```
5. **Run the app:**
	 ```
	 uvicorn main:app --reload
	 ```

---

## API Overview

- **Auth:**  
	- `POST /auth/register` — Register a new user  
	- `POST /auth/login` — Log in and get a JWT token

- **Users:**  
	- `GET /users/{id}` — Public user profile  
	- `GET /users/me` — Current user profile (auth required)

- **Posts:**  
	- `GET /posts` — List all posts  
	- `POST /posts` — Create a post (auth required)  
	- `PUT /posts/{id}` — Update your post (auth required)  
	- `DELETE /posts/{id}` — Delete your post (auth required)

- **Comments:**  
	- `GET /posts/{id}/comments` — List comments on a post  
	- `POST /posts/{id}/comments` — Add a comment (auth required)  
	- `DELETE /comments/{id}` — Delete your comment (auth required)

- **Likes:**  
	- `POST /posts/{id}/like` — Like a post (auth required)  
	- `DELETE /posts/{id}/like` — Unlike a post (auth required)  
	- `GET /posts/{id}/likes` — Get like count

---

## Interactive Docs

- Visit `http://localhost:8000/docs` for Swagger UI.

---

## License

MIT