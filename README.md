# WebApp boilerplate with React JS and Flask API

Build web applications using React.js for the front end and python/flask for your backend API.

- Documentation can be found here: https://4geeks.com/docs/start/react-flask-template
- Here is a video on [how to use this template](https://www.loom.com/share/f37c6838b3f1496c95111e515e83dd9b)
- Integrated with Pipenv for package managing.
- Fast deployment to Render [in just a few steps here](https://4geeks.com/docs/start/deploy-to-render-com).
- Use of .env file.
- SQLAlchemy integration for database abstraction.

## Tapin project layout (migrated from `Tapin_`)
new fix

- **Backend**: `src/backend` contains the Tapin Flask API (users, listings, saved searches, email flows). Run it directly with `python src/backend/app.py` or configure your WSGI server to import `backend.app`.
- **Frontend**: `src/front` is the Vite/React Leaflet SPA copied from `Tapin_/frontend`. `npm` commands live at the repo root and point to this folder through `vite.config.js`.
- **Build output**: `npm run build` writes to the root `dist/` folder. `src/app.py` serves those files while re-exporting the Flask backend.
- **Dependencies**: use `python -m venv .venv && pip install -r src/backend/requirements.txt` for the API and `npm install` for the SPA. The top-level `requirements.txt` simply references the backend list.
- **Environment**: copy `.env.example` to `.env` and fill the variables required by `src/backend/app.py` (database URL, JWT secrets, SMTP settings, etc.). The frontend expects `VITE_BACKEND_URL` to point at the running API.

### 1) Installation:

> If you use Github Codespaces (recommended) or Gitpod this template will already come with Python, Node and the Posgres Database installed. If you are working locally make sure to install Python 3.10, Node 

It is recommended to install the backend first. Make sure you have Python 3.10+, Node 20, and whichever database engine you plan to use (SQLite works out-of-the-box for local dev).

### Backend (src/backend)

1. Create your virtual environment and install dependencies:

   ```powershell
   cd src/backend
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Back at the repository root copy the environment template:

   ```powershell
   cd ../..  # from src/backend back to the repo root
   copy .env.example .env  # or use cp on mac/linux
   ```

   Set `SQLALCHEMY_DATABASE_URI`, `SECRET_KEY`, `JWT_SECRET_KEY`, email SMTP creds, etc. as required by `src/backend/app.py`.

3. Apply migrations / seed data if needed. The Tapin backend ships with Alembic scripts and helpers such as `manage.py`, `migrate_db.py`, and `seed_data.py`. Example:

   ```powershell
   flask --app backend.app db upgrade      # apply migrations
   python backend/seed_data.py             # optional seed data
   ```

4. Run the API:

   ```powershell
   python backend/app.py
   ```

   The service defaults to SQLite at `src/backend/data.db` but will honor any `SQLALCHEMY_DATABASE_URI` you provide.

### Front-End (src/front via root npm scripts)

> **Where do npm commands live?**  
> `package.json` sits at the repository root, so always run `npm install`, `npm run dev`, etc. from the root folder (`.../Tapin_Correct`). Those scripts automatically point to `src/front` via `vite.config.js`.

1. From the repo root install the Vite dependencies and configure the API URL:

   ```powershell
   cd C:\Users\BOMAU\OneDrive\Desktop\4geeks\Project\adjustments\Tapin_Correct
   npm install
   echo VITE_BACKEND_URL=http://localhost:5000 >> .env   # or edit existing .env
   ```

2. Run the dev server and tests:

   ```powershell
   npm run dev
   npm run test
   ```

3. Build for production (output goes to `/dist`, which Flask serves automatically):

   ```powershell
   npm run build
   ```

### Start everything locally

1. Back end: `cd src/backend && .\.venv\Scripts\activate && python app.py` (or `flask --app backend.app run`).  
   - Default SQLite DB lives at `src/backend/data.db`. If you override `SQLALCHEMY_DATABASE_URI`, make sure it resolves from the directory you launch the server in.
2. Front end: from the repo root run `npm run dev` and open the URL Vite prints (usually `http://localhost:5173`).  
3. Ensure `.env` has `VITE_BACKEND_URL=http://localhost:5000` (or whatever host/port Flask uses) so the SPA can reach the API.  
4. For production-style verification run `npm run build` and then hit the Flask root (`http://localhost:5000/`); it serves the files from `dist/`.

## Publish your website!

This boilerplate it's 100% read to deploy with Render.com and Heroku in a matter of minutes. Please read the [official documentation about it](https://4geeks.com/docs/start/deploy-to-render-com).

### Contributors

This template was built as part of the 4Geeks Academy [Coding Bootcamp](https://4geeksacademy.com/us/coding-bootcamp) by [Alejandro Sanchez](https://twitter.com/alesanchezr) and many other contributors. Find out more about our [Full Stack Developer Course](https://4geeksacademy.com/us/coding-bootcamps/part-time-full-stack-developer), and [Data Science Bootcamp](https://4geeksacademy.com/us/coding-bootcamps/datascience-machine-learning).

You can find other templates and resources like this at the [school github page](https://github.com/4geeksacademy/).
