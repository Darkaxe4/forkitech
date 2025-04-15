from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class WalletInfoBase(BaseModel):
    wallet_address: str

class WalletInfo(WalletInfoBase):
    trx_balance: float
    bandwidth: int
    energy: int
    timestamp: datetime

    class Config:
        orm_mode = True

class WalletQueryResponse(BaseModel):
    items: List[WalletInfo]
    total: int
    page: int
    size: int