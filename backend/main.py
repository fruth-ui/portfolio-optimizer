from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List
import traceback

from optimizer import optimize

app = FastAPI(title="Portfolio Optimizer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)


class OptimizeRequest(BaseModel):
    tickers: List[str] = Field(..., min_length=2)
    start_date: str
    end_date: str
    rf_rate: float = Field(default=0.05, ge=0.0, le=1.0)
    n_simulations: int = Field(default=5000, ge=100, le=50000)


@app.post("/optimize")
async def optimize_endpoint(req: OptimizeRequest):
    tickers = [t.upper().strip() for t in req.tickers if t.strip()]
    if len(tickers) < 2:
        raise HTTPException(status_code=400, detail="At least 2 tickers required.")
    try:
        result = optimize(
            tickers=tickers,
            start_date=req.start_date,
            end_date=req.end_date,
            rf_rate=req.rf_rate,
            n_simulations=req.n_simulations,
        )
        return result
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
