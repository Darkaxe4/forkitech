from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from sqlalchemy import desc, func
from typing import Optional
from tronpy import Tron

from .database import get_db, engine, Base
from .settings import get_settings, Settings
from .models import WalletQuery
from .schemas import WalletInfo, WalletInfoBase, WalletQueryResponse

app = FastAPI(title="TRON Wallet Info Service")

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.post("/wallet-info/", response_model=WalletInfo)
async def get_wallet_info(
    wallet: WalletInfoBase,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings)
):
    try:
        # Initialize TRON client with network from settings
        client = Tron(network=settings.tron_network)
        
        # Get account information
        account = client.get_account(wallet.wallet_address)
        
        # Get account resources
        resources = client.get_account_resource(wallet.wallet_address)
        
        # Create wallet query record
        db_wallet_query = WalletQuery(
            wallet_address=wallet.wallet_address,
            trx_balance=float(account.get("balance", 0)) / 1000000,  # Convert SUN to TRX
            bandwidth=resources.get("freeNetLimit", 0) + resources.get("NetLimit", 0),
            energy=resources.get("EnergyLimit", 0)
        )
        
        db.add(db_wallet_query)
        await db.commit()
        await db.refresh(db_wallet_query)
        
        return db_wallet_query

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.get("/wallet-queries/", response_model=WalletQueryResponse)
async def list_wallet_queries(
    page: int = 1,
    size: int = 10,
    db: AsyncSession = Depends(get_db)
):
    if page < 1:
        raise HTTPException(status_code=400, detail="Page must be greater than 0")
    if size < 1:
        raise HTTPException(status_code=400, detail="Size must be greater than 0")

    try:
        # Get total count
        total_query = select(func.count()).select_from(WalletQuery)  # import sqlalchemy.func as func
        result = await db.execute(total_query)
        total = result.scalar()

        # Get paginated results
        query = select(WalletQuery).order_by(desc(WalletQuery.timestamp)).offset((page - 1) * size).limit(size)
        result = await db.execute(query)
        items = result.scalars().all()

        return WalletQueryResponse(
            items=items,
            total=total,
            page=page,
            size=size
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")




