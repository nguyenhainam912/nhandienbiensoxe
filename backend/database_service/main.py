from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

app = FastAPI()

# MongoDB connection
MONGO_URI = "mongodb+srv://dognam912:1grXOoLgxqvzpOJG@cluster0.b7pflkj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client["biensoxe"]
collection = db["bien_so"]

class LicensePlateRecord(BaseModel):
    bien_so: str
    trang_thai: str
    thoi_gian_vao: Optional[str] = None
    thoi_gian_ra: Optional[str] = None
    tong_thoi_gian_phut: Optional[float] = None
    tong_tien: Optional[float] = None

class QueryFilter(BaseModel):
    bien_so: Optional[str] = None
    trang_thai: Optional[str] = None

@app.post("/insert_record")
async def insert_record(record: LicensePlateRecord):
    try:
        result = collection.insert_one(record.dict(exclude_unset=True))
        return {"inserted_id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/update_record")
async def update_record(filter: QueryFilter, update_data: Dict[str, Any]):
    try:
        result = collection.update_one(
            filter.dict(exclude_unset=True),
            {"$set": update_data}
        )
        if result.matched_count == 0:
            return {"status": "Không tìm thấy bản ghi phù hợp"}
        return {"modified_count": result.modified_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/find_records")
async def find_records(filter: QueryFilter):
    try:
        query = filter.dict(exclude_unset=True)
        records = list(collection.find(query, {"_id": 0}))
        return records
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))