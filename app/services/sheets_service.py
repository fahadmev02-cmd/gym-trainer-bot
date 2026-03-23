# app/services/sheets_service.py

import gspread
import json
import os
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv

load_dotenv()


class SheetsService:
    def __init__(self):
        self.sheet = None
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        try:
            creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")

            if creds_json:
                creds_dict = json.loads(creds_json)
                credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                    creds_dict, scope
                )
            else:
                creds_file = os.getenv(
                    "GOOGLE_SHEETS_CREDENTIALS_FILE",
                    "credentials.json"
                )
                credentials = ServiceAccountCredentials.from_json_keyfile_name(
                    creds_file, scope
                )

            client = gspread.authorize(credentials)
            sheet_name = os.getenv("GOOGLE_SHEET_NAME", "GymMembers")
            self.sheet = client.open(sheet_name).sheet1
            print("✅ Google Sheets connected successfully")

        except Exception as e:
            print("❌ Google Sheets connection failed:", e)

    def verify_membership(self, receipt_number: str) -> dict:
        if not self.sheet:
            return {"is_valid": False, "name": None, "phone": None}
        try:
            all_records = self.sheet.get_all_records()
            for record in all_records:
                if str(record.get("receipt_number", "")) == str(receipt_number).strip():
                    return {
                        "is_valid": True,
                        "name": record.get("name", ""),
                        "phone": str(record.get("phone", ""))
                    }
            return {"is_valid": False, "name": None, "phone": None}
        except Exception as e:
            print("❌ Error verifying membership:", e)
            return {"is_valid": False, "name": None, "phone": None}


sheets_service = SheetsService()