import json
from pathlib import Path

DB_PATH=Path("db.json")

def read_db():
    with DB_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)
    
def write_db(data):
    with DB_PATH.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        
def p_read_db(path: str):
    P_DB_PATH = Path(path)
    with P_DB_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)
    
def p_write_db(data, path: str):
    P_DB_PATH = Path(path)
    with P_DB_PATH.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        