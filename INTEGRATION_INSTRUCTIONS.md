# Module Integration Instructions

This file explains how to register and migrate the modular features (ML, Admin, Gamification).

1. Register blueprints in `src/backend/app.py` (after creating the Flask app):

```py
from backend.ml import ml_blueprint
from backend.admin import admin_blueprint
from backend.gamification import gamification_blueprint

app.register_blueprint(ml_blueprint)
app.register_blueprint(admin_blueprint)
app.register_blueprint(gamification_blueprint)
```

2. Create Alembic migration (review before applying):

```bash
cd src/backend
flask db migrate -m "Add ML, gamification, admin modules"
# review migration in migrations/versions
flask db upgrade
```

3. Seed achievements (dev/admin only):

```bash
curl -X POST http://localhost:5000/api/achievements/seed \
  -H "Authorization: Bearer YOUR_TOKEN"
```

4. Test endpoints with a valid JWT token for a volunteer/admin user.

If you want, I can register the blueprints automatically in `app.py` and scaffold the migration file. Ask me to proceed and I will make the edits and run a local lint/test pass.
