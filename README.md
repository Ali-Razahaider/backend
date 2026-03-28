# 📝 BlogAPI — Cold Rebuild Project

A fully functional blogging backend API where users can register, write posts, comment on others' posts, and like posts. No tutorials, no looking back at Corey's code. Just you and a blank file.

---

## What You're Building

A REST API that powers a blogging platform. Think of it like a minimal version of Medium or Dev.to — backend only. Users can sign up, log in, write posts, comment on posts, and like them. Every user can only manage their own content. The whole thing is structured properly with separated routers, services, and models — not everything dumped in one `main.py`.

---

## Database Models

### User
- `id`, `email`, `password` (hashed), `created_at`
- A user has many posts, many comments, many likes

### Post
- `id`, `title`, `content`, `published` (boolean), `created_at`
- Belongs to a user (foreign key)
- Has many comments, many likes

### Comment
- `id`, `content`, `created_at`
- Belongs to a user and a post (two foreign keys)

### Like
- `id`, `created_at`
- Belongs to a user and a post
- A user can only like a post once (unique constraint on `user_id` + `post_id`)

---

## API Endpoints

### Auth
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/auth/register` | ❌ | Create new user, hash password, return user info |
| POST | `/auth/login` | ❌ | Verify credentials, return JWT token |

### Users
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/users/{id}` | ❌ | Get public profile of any user |
| GET | `/users/me` | ✅ | Get current logged in user's profile |

### Posts
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/posts` | ❌ | Get all published posts (paginated) |
| GET | `/posts/{id}` | ❌ | Get single post with comment and like count |
| POST | `/posts` | ✅ | Create a post |
| PUT | `/posts/{id}` | ✅ | Update your own post (owner only) |
| DELETE | `/posts/{id}` | ✅ | Delete your own post (owner only) |
| GET | `/posts/me` | ✅ | Get all posts by the logged in user |

### Comments
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/posts/{id}/comments` | ❌ | Get all comments on a post (paginated) |
| POST | `/posts/{id}/comments` | ✅ | Add a comment to a post |
| DELETE | `/comments/{id}` | ✅ | Delete your own comment (owner only) |

### Likes
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/posts/{id}/like` | ✅ | Like a post (can't like your own) |
| DELETE | `/posts/{id}/like` | ✅ | Unlike a post |
| GET | `/posts/{id}/likes` | ❌ | Get like count for a post |

---

## Project Structure

Don't put everything in `main.py`. Structure it like this from day one:

```
blogapi/
├── main.py
├── database.py
├── config.py
├── models/
│   ├── __init__.py
│   ├── user.py
│   ├── post.py
│   ├── comment.py
│   └── like.py
├── schemas/
│   ├── __init__.py
│   ├── user.py
│   ├── post.py
│   ├── comment.py
│   └── like.py
├── routers/
│   ├── __init__.py
│   ├── auth.py
│   ├── users.py
│   ├── posts.py
│   ├── comments.py
│   └── likes.py
├── services/
│   ├── __init__.py
│   ├── auth.py
│   └── posts.py
└── dependencies.py
```

| Folder | Purpose |
|--------|---------|
| `models/` | SQLAlchemy ORM models (DB tables) |
| `schemas/` | Pydantic models (request/response validation) |
| `routers/` | Endpoint definitions only, no business logic |
| `services/` | Actual business logic (DB queries, password hashing etc) |
| `dependencies.py` | Shared dependencies like `get_db` and `get_current_user` |

---

## Pydantic Schemas

For each resource define at minimum three schemas. Example for Post:

- `PostCreate` — what the client sends to create a post (`title`, `content`, `published`)
- `PostUpdate` — what the client sends to update (all fields optional)
- `PostResponse` — what you send back (includes `id`, `created_at`, owner info)

Same pattern for User, Comment, Like. **Never expose the password hash in any response schema.**

---

## Business Rules

These are the rules your API must enforce:

- Passwords must be hashed with bcrypt — never store plain text
- A user cannot update or delete another user's post
- A user cannot update or delete another user's comment
- A user cannot like their own post
- A user cannot like the same post twice
- Deleting a post should cascade delete its comments and likes
- Pagination on all list endpoints — default 10 items, max 50
- Posts have a `published` flag — unpublished posts only visible to their owner

---

## Build Sequence

Follow this exact order. Don't jump ahead — each step depends on the previous one.

### Step 1 — Project Setup
- Create the folder structure above
- Set up virtual environment
- Install dependencies: `fastapi`, `uvicorn`, `sqlalchemy`, `psycopg2-binary`, `python-jose[cryptography]`, `passlib[bcrypt]`, `python-dotenv`, `alembic`
- Set up `.env` file with `DB_URL`, `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`
- Create `config.py` with Pydantic `BaseSettings` reading from `.env`
- Create `database.py` with async engine and session
- Verify the app starts with a basic health check at `GET /health`

### Step 2 — Database Models
- Write all four SQLAlchemy models (User, Post, Comment, Like)
- Add proper relationships and foreign keys
- Define the unique constraint on Like (`user_id` + `post_id`)
- Let SQLAlchemy create tables on startup first — don't worry about Alembic yet
- Verify all tables appear in pgAdmin

### Step 3 — Pydantic Schemas
- Write all schemas for all four resources
- Focus on getting response schemas right — what should and shouldn't be exposed
- Write a `UserBasic` schema (just `id` and `email`) that gets nested inside `PostResponse`

### Step 4 — Auth ✅ Checkpoint
- Build registration and login endpoints
- Hash passwords on registration
- On login verify hash, generate JWT, return token
- Write `get_current_user` dependency in `dependencies.py`
- **Test both endpoints in Postman before moving on**
- **Come back and check in here before continuing**

### Step 5 — Users Endpoints
- `GET /users/{id}` and `GET /users/me`
- Good practice for using the `get_current_user` dependency

### Step 6 — Posts CRUD
- All post endpoints
- Enforce ownership on update and delete — return `403` if user tries to modify someone else's post
- Add pagination to `GET /posts`
- Filter unpublished posts for non-owners

### Step 7 — Comments
- Comments endpoints
- A comment belongs to both a user and a post — set both foreign keys correctly on create
- Enforce ownership on delete

### Step 8 — Likes
- `POST /posts/{id}/like` — check user isn't liking their own post, and hasn't already liked it
- Handle the unique constraint violation gracefully with a `400` response instead of a `500`
- `DELETE /posts/{id}/like` and `GET /posts/{id}/likes`

### Step 9 — Testing in Postman
Go through every single endpoint. Test happy paths AND error cases:
- Like your own post → should be rejected
- Delete someone else's post → should be rejected
- Send an expired token → should be rejected
- Like the same post twice → should be rejected
- Fix everything that breaks

### Step 10 — Clean Up and Push to GitHub
- Review every file
- Add comments where logic is non-obvious
- Make sure no passwords or secret keys are hardcoded anywhere
- Write a proper README (what the project is, how to set it up, all endpoints)
- Push to GitHub

---

## Dependencies

```
fastapi
uvicorn[standard]
sqlalchemy
psycopg2-binary
python-jose[cryptography]
passlib[bcrypt]
python-dotenv
alembic
```

---

## What This Rebuild Will Prove

If you can finish this without looking at Corey's code or copying from anywhere, you genuinely understand FastAPI at a foundational level. Every wall you hit and push through during this rebuild is worth more than 5 hours of watching tutorials.

---

> **Come back after Step 4 (auth working) to check in. Then again when fully done before moving to SmartTask.**