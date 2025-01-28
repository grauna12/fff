import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

def connect_to_gsheet(sheet_name:str, credentials:dict):

    try:
        creds = Credentials.from_service_account_info(
            credentials,
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
            ]
        )
        client = gspread.authorize(creds)
        return client.open(sheet_name).sheet1
    except Exception as e:
        raise RuntimeError('Erro de conecção')
    
def load_sheet_data(sheet):
    try:                                                                                                                                                                                                                                                                                        
        data= sheet.get_all_records()
        return pd.DataFrame(data)
    except Exception as e:
        raise RuntimeError(f"Error loading")