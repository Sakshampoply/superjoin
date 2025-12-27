from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime


class RecordBase(BaseModel):
    sheet_row_index: int
    data_payload: Dict[str, Any]
    source: Optional[str] = "DB"


class RecordCreate(RecordBase):
    pass


class RecordUpdate(RecordBase):
    pass


class RecordResponse(RecordBase):
    id: int
    updated_at: datetime
    last_sync_source: str
    version_ts: int

    class Config:
        from_attributes = True


class SheetSyncRequest(BaseModel):
    row: int
    data: Dict[str, Any]  # Or List[Any] depending on how we parse it
    source: str


class SheetBatchSyncRequest(BaseModel):
    updates: list[SheetSyncRequest]
