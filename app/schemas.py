from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional

class WalletInfoBase(BaseModel):
    wallet_address: str

class WalletInfo(WalletInfoBase):
    trx_balance: float
    bandwidth: int
    energy: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)

class WalletQueryResponse(BaseModel):
    items: List[WalletInfo]
    total: int
    page: int
    size: int
