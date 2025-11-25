# Tapin Marketplace Platform

Tapin is a full-stack marketplace application built with a React.js frontend and a Python/Flask backend. It provides a robust platform for users to browse, create, and manage listings in a modern, interactive interface.

## Features

### Backend (Flask API)

- **User Authentication:** Secure user registration, login, and password reset functionality using JWT for protected endpoints.
- **Listings Management:** A comprehensive set of API endpoints to create, read, update, and delete listings.
- **Database Integration:** Uses SQLAlchemy for database abstraction, with support for SQLite in development and PostgreSQL or MySQL in production.
- **Database Migrations:** Alembic is used for managing database schema changes.
- **Search and Filtering:** The listings endpoint supports query-based searching and location filtering.

### Frontend (React SPA)

- **Interactive Listings:** A single-page application for a seamless user experience in browsing and managing listings.
- **Mapping Integration:** (Coming Soon) Leaflet integration for displaying listings on a map.
- **Component-Based:** Built with modern React components for easy maintenance and extensibility.

## Tech Stack

- **Frontend:** React.js, Vite
- **Backend:** Python, Flask, SQLAlchemy, Alembic
- **Database:** SQLite (dev), PostgreSQL/MySQL (prod)
- **Testing:** Pytest (backend), Playwright (frontend E2E)

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 20+
- A database engine (SQLite is used by default for local development)

### Installation and Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/4GeeksAcademy/Tapin_Correct.git
   cd Tapin_Correct
   ```

2. **Set up the backend:**

   ```bash
   cd src/backend
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   cd ../.. # Return to the root directory
   ```

3. **Set up the frontend:**

   ```bash
   npm install
   ```

4. **Configure environment variables:**
   - Copy the `.env.example` file to `.env` in the root directory.
   - Fill in the required variables, such as `SECRET_KEY`, `JWT_SECRET_KEY`, and database connection details.
   - For the frontend to connect to the backend, add the following to your `.env` file:
     ```
     VITE_BACKEND_URL=http://localhost:5000
     ```

5. **Initialize the database:**

   ```bash
   cd src/backend
   source .venv/bin/activate
   python manage.py upgrade
   python seed_sample_data.py # Optional: to seed the database with sample data
   cd ../..
   ```

### Running the Application

1. **Start the backend server:**

   ```bash
   cd src/backend
   source .venv/bin/activate
   python app.py
   ```

   The Flask API will be running at `http://127.0.0.1:5000`.

2. **Start the frontend development server:**

   ```bash
   npm run dev
   ```

   The React application will be available at `http://localhost:5173` (or the next available port).

### Running Tests

- **Backend:**

  ```bash
  cd src/backend
  source .venv/bin/activate
  pytest tests/ -v
  ```

- **Frontend:**

  ```bash
  npm run test
  ```
