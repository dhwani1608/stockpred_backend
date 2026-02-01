from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.watchlist import Watchlist, watchlist_symbols

router = APIRouter(prefix="/api/watchlists", tags=["watchlists"])


class WatchlistCreate(BaseModel):
    name: str
    symbols: list[str] = []


class WatchlistResponse(BaseModel):
    id: int
    user_id: int
    name: str
    symbols: list[str] = []
    
    class Config:
        from_attributes = True


@router.post("/", response_model=WatchlistResponse)
def create_watchlist(
    data: WatchlistCreate,
    user_id: int,
    db: Session = Depends(get_db)
):
    """Create a new watchlist."""
    watchlist = Watchlist(user_id=user_id, name=data.name)
    db.add(watchlist)
    db.commit()
    db.refresh(watchlist)
    
    return watchlist


@router.get("/{watchlist_id}", response_model=WatchlistResponse)
def get_watchlist(watchlist_id: int, db: Session = Depends(get_db)):
    """Get a watchlist by ID."""
    watchlist = db.query(Watchlist).filter(Watchlist.id == watchlist_id).first()
    if not watchlist:
        raise HTTPException(status_code=404, detail="Watchlist not found")
    
    return watchlist


@router.post("/{watchlist_id}/symbols")
def add_symbol(watchlist_id: int, symbol: str, db: Session = Depends(get_db)):
    """Add a symbol to watchlist."""
    watchlist = db.query(Watchlist).filter(Watchlist.id == watchlist_id).first()
    if not watchlist:
        raise HTTPException(status_code=404, detail="Watchlist not found")
    
    # Add symbol (implement association logic)
    db.commit()
    return {"status": "symbol added"}


@router.delete("/{watchlist_id}/symbols/{symbol}")
def remove_symbol(watchlist_id: int, symbol: str, db: Session = Depends(get_db)):
    """Remove a symbol from watchlist."""
    # Implement symbol removal logic
    return {"status": "symbol removed"}
