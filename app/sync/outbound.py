from app.models import Record
from app.sync.google_client import sheet_client
import asyncio


async def process_outbound_sync(record: Record):
    """
    Triggered after DB update.
    If source is SHEET, do nothing (Loop Breaker).
    If source is DB, push to Sheet.
    """
    if record.last_sync_source == "SHEET":
        print(
            f"Skipping outbound sync for Row {record.sheet_row_index} (Source is SHEET)"
        )
        return

    print(f"Pushing to Sheet: Row {record.sheet_row_index}")

    # Convert payload dict to list of values expected by Sheet
    # Assumption: data_payload is a dict like {"col1": "val1", "col2": "val2"}
    # We need a deterministic order. For now, let's assume simple list or specific keys.
    # To make it generic, let's assume the payload IS the list of values for the row.

    values = []
    if isinstance(record.data_payload, list):
        values = record.data_payload
    elif isinstance(record.data_payload, dict):
        # Naive conversion, in real world we need a schema mapping
        values = list(record.data_payload.values())

    try:
        # In a real app, this should be a background task (Celery/Redis)
        # For now, we run it here (blocking or threaded)
        # Since google client is sync, we might want to run it in executor
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None, sheet_client.update_row, record.sheet_row_index, values
        )
    except Exception as e:
        print(f"Failed to sync to sheet: {e}")
        # Implement retry logic here


async def process_outbound_delete(sheet_row_index: int):
    print(f"Clearing Sheet Row: {sheet_row_index}")
    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, sheet_client.clear_row, sheet_row_index)
    except Exception as e:
        print(f"Failed to clear sheet row: {e}")
