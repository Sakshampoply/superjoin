from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import Record
from app.schemas import SheetSyncRequest
import datetime
import json


async def process_inbound_sync(payload: SheetSyncRequest, db: AsyncSession):
    # Check if row exists
    result = await db.execute(
        select(Record).where(Record.sheet_row_index == payload.row)
    )
    record = result.scalars().first()

    current_ts = int(datetime.datetime.now().timestamp() * 1000)

    if record:
        # Last Write Wins Logic
        # If the DB record is newer (higher version_ts) and source was DB, we might have a conflict.
        # However, for simplicity in this "Sheet pushed" event, we assume Sheet is the source of truth
        # for this specific moment unless we want strict LWW.
        # Let's implement strict LWW based on a hypothetical timestamp from sheet if available,
        # but usually sheet doesn't send granular TS. We'll assume this inbound request IS the latest.

        record.data_payload = payload.data
        record.last_sync_source = "SHEET"
        record.version_ts = current_ts
        # updated_at is auto-handled
    else:
        record = Record(
            sheet_row_index=payload.row,
            data_payload=payload.data,
            last_sync_source="SHEET",
            version_ts=current_ts,
        )
        db.add(record)

    await db.commit()
    await db.refresh(record)
    return record


async def process_inbound_batch_sync(
    payload_list: list[SheetSyncRequest], db: AsyncSession
):
    results = []
    for payload in payload_list:
        # We can optimize this to be a single transaction or bulk upsert later
        # For now, reuse the logic to ensure consistency
        record = await process_inbound_sync(payload, db)
        results.append(record)
    return results
