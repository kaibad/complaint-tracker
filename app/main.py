from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import Base, engine, get_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)  # create tables on startup
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


@app.post(
    "/complaints",
    response_model=schemas.ComplaintOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Complaints"],
)
def create_complaint(data: schemas.ComplaintCreate, db: Session = Depends(get_db)):
    """File a new complaint. It always starts with the status `pending`."""
    return crud.create_complaint(db, data)


@app.get("/complaints", response_model=list[schemas.ComplaintOut], tags=["Complaints"])
def list_complaints(
    status: models.Status | None = None,
    category: models.Category | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List complaints, newest first. Filter by status and/or category; use skip and limit to page."""
    return crud.list_complaints(db, status, category, skip, limit)


@app.get("/complaints/stats", tags=["Reports"])
def complaint_stats(db: Session = Depends(get_db)):
    """Return the number of complaints in each status, plus the total."""
    return crud.stats(db)


def _get_or_404(db: Session, complaint_id: int) -> models.Complaint:
    """Fetch a complaint or stop the request with a 404 error."""
    complaint = crud.get_complaint(db, complaint_id)
    if complaint is None:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return complaint


@app.get("/complaints/{complaint_id}", response_model=schemas.ComplaintOut, tags=["Complaints"])
def get_complaint(complaint_id: int, db: Session = Depends(get_db)):
    """Return one complaint by its id."""
    return _get_or_404(db, complaint_id)


@app.patch("/complaints/{complaint_id}/status", response_model=schemas.ComplaintOut, tags=["Complaints"])
def update_complaint_status(
    complaint_id: int, data: schemas.ComplaintUpdate, db: Session = Depends(get_db)
):
    """Move a complaint to a new status. Resolved or rejected complaints are final (400)."""
    complaint = _get_or_404(db, complaint_id)
    try:
        return crud.update_status(db, complaint, data)
    except crud.ClosedComplaintError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.delete("/complaints/{complaint_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Complaints"])
def delete_complaint(complaint_id: int, db: Session = Depends(get_db)):
    """Permanently delete a complaint."""
    crud.delete_complaint(db, _get_or_404(db, complaint_id))
