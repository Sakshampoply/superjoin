from google.oauth2 import service_account
from googleapiclient.discovery import build
from app.config import settings
import os

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


class GoogleSheetClient:
    def __init__(self):
        self.creds = None
        self.service = None
        self.sheet_id = settings.GOOGLE_SHEET_ID

        if os.path.exists(settings.GOOGLE_CREDENTIALS_FILE):
            self.creds = service_account.Credentials.from_service_account_file(
                settings.GOOGLE_CREDENTIALS_FILE, scopes=SCOPES
            )
            self.service = build("sheets", "v4", credentials=self.creds)
        else:
            print(
                "Warning: Google Credentials file not found. Outbound sync will fail."
            )

    def update_row(self, row_index: int, values: list):
        if not self.service:
            print(f"Mock Update Sheet: Row {row_index}, Values {values}")
            return

        range_name = f"A{row_index}"  # Assuming data starts at col A
        body = {"values": [values]}
        result = (
            self.service.spreadsheets()
            .values()
            .update(
                spreadsheetId=self.sheet_id,
                range=range_name,
                valueInputOption="RAW",
                body=body,
            )
            .execute()
        )
        return result

    def clear_row(self, row_index: int):
        if not self.service:
            print(f"Mock Clear Sheet: Row {row_index}")
            return

        range_name = f"A{row_index}:Z{row_index}"  # Clear the whole row
        result = (
            self.service.spreadsheets()
            .values()
            .clear(spreadsheetId=self.sheet_id, range=range_name)
            .execute()
        )
        return result


sheet_client = GoogleSheetClient()
