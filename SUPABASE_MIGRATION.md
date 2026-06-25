# Switch UGSP from In-Memory to Supabase PostgreSQL

## 1. Create Supabase Project

1. Go to https://supabase.com → **New project**
2. Fill in name (e.g. `ugsp-portal`), set a secure DB password
3. Wait for provisioning (~2 min)
4. Go to **Project Settings → Database → Connection string**
5. Copy the URI: `postgresql://postgres:xxxx@aws-0-xx-x-x.supabase.co:5432/postgres`

## 2. Add Dependency

```bash
pip install psycopg2-binary
```

Add to `requirements.txt`:
```
psycopg2-binary==2.9.9
```

## 3. Create `app/core/database.py`

```python
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.schemas import Base

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/ugsp"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## 4. Update `app/main.py`

Add startup event to create tables:

```python
from app.core.database import init_db

@app.on_event("startup")
async def startup():
    init_db()
```

## 5. Update Router Files

Each endpoint that reads mock data now needs a `db: Session = Depends(get_db)` parameter.

### Example — `auth.py` Profile endpoint

**Before (mock):**
```python
user = MOCK_USERS.get(nin)
return {"name": user["name"], ...}
```

**After (database):**
```python
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.schemas import User  # you'll need to create a User model

@router.get("/profile")
async def profile(authorization: str = Header(None), db: Session = Depends(get_db)):
    nin = _verify(authorization)
    user = db.query(User).filter(User.nin == nin).first()
    if not user:
        raise HTTPException(404, "User not found")
    return {"name": user.name, ...}
```

## 6. Create a `User` Model in `app/models/schemas.py`

The current mock data stores users but there's no SQLAlchemy `User` model yet. Add:

```python
class User(Base):
    __tablename__ = "users"
    nin = Column(String(20), primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(50))
    password = Column(String(255), nullable=False)
    category = Column(String(20), default="citizen")
    photo_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
```

Then run:
```python
# In database.py init_db(), tables will auto-create.
# Or via Alembic:
# alembic revision --autogenerate -m "add users table"
```

## 7. Seed into Supabase

Update `seed_fast.py` to write to Supabase instead of API calls:

```python
from app.core.database import SessionLocal
from app.models.schemas import User, Service, Application, Payment

db = SessionLocal()

for u in SEED_USERS:
    db.add(User(**u))
db.commit()
```

## 8. Deploy

Add `DATABASE_URL` as an environment variable on Render:

```
DATABASE_URL=postgresql://postgres:xxxx@aws-0-xx-x-x.supabase.co:5432/postgres
```

---

**TL;DR:** Create Supabase project → add `psycopg2-binary` → create `app/core/database.py` → update routers to use `db: Session = Depends(get_db)` → add User model → seed → deploy.
