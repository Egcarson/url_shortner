# 🔗 FastAPI URL Shortener

A simple, high-performance URL shortener built with **FastAPI**, **SQLModel**, and **PostgreSQL**, supporting user authentication and personal dashboards for managing shortened links.

## 🚀 Features
- 🔒 User registration & JWT authentication
- 🔗 Shorten long URLs into unique short codes
- 👤 Authenticated users can manage their own URLs
- 🔄 Automatic redirect via short code
- ⚡ Fully asynchronous and production-ready

## 📦 Tech Stack
- **Python 3.11**
- **FastAPI** + **SQLModel**
- **PostgreSQL** (via asyncpg)
- **JWT** (for auth)
- **Docker + Docker Compose** for deployment

## 🧪 Run Locally (Dev)

### 1. Clone the repo
```bash
git clone https://github.com/egcarson/url_shortner.git
cd url_shortner
```

### 2. Create & activate a virtual environment
```bash
python -m venv env
env\Scripts\activate    #Linux: source env/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure `.env`
Create a `.env` file:
```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/urlshortener
JWT_SECRET=your_super_secret_key
```

## 🐳 Docker Setup (Recommended)

### 1. Build & run the project
```bash
docker compose up --build
```

### 2. Open the API docs
[http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)

## 📬 API Endpoints

### 🔐 Authentication
| Method | Endpoint     | Description           |
|--------|--------------|-----------------------|
| POST   | `/register`  | Register new user     |
| POST   | `/login`     | Get JWT token         |
| POST   | `/logout`    | Blacklist JWT token   |

### 🔗 URL Operations
| Method | Endpoint               | Auth? | Description                  |
|--------|------------------------|-------|------------------------------|
| POST   | `/urls`                | ✅    | Shorten a long URL           |
| GET    | `/urls/{short_code}`   | ❌    | Redirect to original URL     |
| GET    | `/urls/me`             | ✅    | List URLs by current user    |

## ✅ TODO (Next Features)
- [ ] QR Code support for shortened URLs
- [ ] Click analytics and tracking
- [ ] Custom short code names (e.g., `/u/my-brand`)

## 📄 License
Licensed under the **MIT License**.

## ✨ Credits
Built with ❤️ using **FastAPI** and **SQLModel** by [Godprevail].
