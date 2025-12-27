from fastapi import FastAPI, Depends, HTTPException, Request, BackgroundTasks
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import engine, Base, get_db
from app.models import Record
from app.schemas import (
    SheetSyncRequest,
    RecordResponse,
    RecordUpdate,
    SheetBatchSyncRequest,
)
from app.sync.inbound import process_inbound_sync, process_inbound_batch_sync
from app.sync.outbound import process_outbound_sync, process_outbound_delete
import datetime

app = FastAPI(title="Sheet-DB Sync")

templates = Jinja2Templates(directory="app/templates")


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.post("/sync/from-sheet")
async def sync_from_sheet(
    payload: SheetSyncRequest, db: AsyncSession = Depends(get_db)
):
    try:
        record = await process_inbound_sync(payload, db)
        return {"status": "success", "id": record.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/sync/batch-from-sheet")
async def sync_batch_from_sheet(
    payload: SheetBatchSyncRequest, db: AsyncSession = Depends(get_db)
):
    try:
        records = await process_inbound_batch_sync(payload.updates, db)
        return {"status": "success", "count": len(records)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Record).order_by(Record.sheet_row_index))
    records = result.scalars().all()
    return templates.TemplateResponse(
        "index.html", {"request": request, "records": records}
    )


@app.post("/api/records/{record_id}")
async def update_record(
    record_id: int,
    update_data: RecordUpdate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Record).where(Record.id == record_id))
    record = result.scalars().first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    # Update DB
    record.data_payload = update_data.data_payload
    record.last_sync_source = "DB"
    record.version_ts = int(datetime.datetime.now().timestamp() * 1000)

    await db.commit()
    await db.refresh(record)

    # Trigger Outbound Sync
    background_tasks.add_task(process_outbound_sync, record)

    return record


@app.post("/api/records")
async def create_record(
    create_data: RecordUpdate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    # Check if row exists
    result = await db.execute(
        select(Record).where(Record.sheet_row_index == create_data.sheet_row_index)
    )
    existing = result.scalars().first()
    if existing:
        raise HTTPException(status_code=400, detail="Row already exists")

    record = Record(
        sheet_row_index=create_data.sheet_row_index,
        data_payload=create_data.data_payload,
        last_sync_source="DB",
        version_ts=int(datetime.datetime.now().timestamp() * 1000),
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)

    background_tasks.add_task(process_outbound_sync, record)
    return record


@app.delete("/api/records/{record_id}")
async def delete_record(
    record_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Record).where(Record.id == record_id))
    record = result.scalars().first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    sheet_row_index = record.sheet_row_index

    await db.delete(record)
    await db.commit()

    # Trigger Outbound Sync (Delete)
    background_tasks.add_task(process_outbound_delete, sheet_row_index)

    return {"status": "deleted", "id": record_id}
