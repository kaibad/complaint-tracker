from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from . import auth, crud, models, schemas
from .database import Base, SessionLocal, engine, get_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)  # create tables on startup
    with SessionLocal() as db:
        auth.ensure_admin(db)
    yield


app = FastAPI(
    title="Citizen Complaint Tracker API",
    description="A simple API for citizens to file public-service complaints "
    "and for officers to track and resolve them.",
    version="1.0.0",
    lifespan=lifespan,
)

app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).resolve().parent.parent / "static"),
    name="static",
)


@app.get("/api/health", tags=["Health"])
def health_check():
    """Return a simple message so we can confirm the service is up."""
    return {"message": "Citizen Complaint Tracker API is running"}


@app.get("/", include_in_schema=False)
@app.get("/ui", include_in_schema=False)
@app.get("/index.html", include_in_schema=False)
def serve_frontend():
    return FileResponse(Path(__file__).resolve().parent.parent / "static" / "index.html")


@app.post("/auth/register", response_model=schemas.UserOut, status_code=201, tags=["Auth"])
def register(data: schemas.UserCreate, db: Session = Depends(get_db)):
    """Create a citizen account. Admin accounts cannot be created through the API."""
    if crud.get_user_by_username(db, data.username):
        raise HTTPException(status_code=409, detail="Username already taken")
    user = models.User(
        username=data.username, password_hash=auth.hash_password(data.password), role=models.Role.CITIZEN
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.post("/auth/login", response_model=schemas.TokenOut, tags=["Auth"])
def login(data: schemas.LoginIn, db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, data.username)
    if user is None or not auth.verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    return {"access_token": auth.create_token(db, user), "user": user}


@app.get("/auth/me", response_model=schemas.UserOut, tags=["Auth"])
def me(user: models.User = Depends(auth.get_current_user)):
    return user


@app.post("/auth/logout", status_code=204, tags=["Auth"])
def logout(
    creds: HTTPAuthorizationCredentials = Depends(auth._bearer),
    _: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    auth.revoke_token(db, creds.credentials)


def _scope(user: models.User) -> int | None:
    """Admins see everything (None = no owner filter); citizens only their own."""
    return None if user.role == models.Role.ADMIN else user.id


@app.post(
    "/complaints",
    response_model=schemas.ComplaintOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Complaints"],
)
def create_complaint(
    data: schemas.ComplaintCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
):
    """File a new complaint. It always starts with the status `pending`."""
    return crud.create_complaint(db, data, owner_id=user.id)


@app.get("/complaints", response_model=list[schemas.ComplaintOut], tags=["Complaints"])
def list_complaints(
    status: models.Status | None = None,
    category: models.Category | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
):
    """Admins: all complaints. Citizens: only their own. Newest first."""
    return crud.list_complaints(db, status, category, skip, limit, owner_id=_scope(user))


@app.get("/complaints/stats", tags=["Reports"])
def complaint_stats(
    db: Session = Depends(get_db), user: models.User = Depends(auth.get_current_user)
):
    """Counts per status (all complaints for admins, own for citizens)."""
    return crud.stats(db, owner_id=_scope(user))


def _get_or_404(db: Session, complaint_id: int, user: models.User) -> models.Complaint:
    """Fetch a complaint the user may see, or stop with 404 (also hides other people's ids)."""
    complaint = crud.get_complaint(db, complaint_id)
    if complaint is None or (_scope(user) is not None and complaint.owner_id != user.id):
        raise HTTPException(status_code=404, detail="Complaint not found")
    return complaint


@app.get("/complaints/{complaint_id}", response_model=schemas.ComplaintOut, tags=["Complaints"])
def get_complaint(
    complaint_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
):
    return _get_or_404(db, complaint_id, user)


@app.patch("/complaints/{complaint_id}/status", response_model=schemas.ComplaintOut, tags=["Complaints"])
def update_complaint_status(
    complaint_id: int,
    data: schemas.ComplaintUpdate,
    db: Session = Depends(get_db),
    admin: models.User = Depends(auth.require_admin),
):
    """Admin only. Resolved or rejected complaints are final (400)."""
    complaint = _get_or_404(db, complaint_id, admin)
    try:
        return crud.update_status(db, complaint, data)
    except crud.ClosedComplaintError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.delete("/complaints/{complaint_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Complaints"])
def delete_complaint(
    complaint_id: int,
    db: Session = Depends(get_db),
    admin: models.User = Depends(auth.require_admin),
):
    """Admin only. Permanently delete a complaint."""
    crud.delete_complaint(db, _get_or_404(db, complaint_id, admin))
