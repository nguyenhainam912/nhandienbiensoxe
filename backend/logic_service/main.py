from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import math
import requests

app = FastAPI()

# Database Service endpoints
DB_INSERT_API = "http://localhost:8000/insert_record"
DB_UPDATE_API = "http://localhost:8000/update_record"
DB_FIND_API = "http://localhost:8000/find_records"

class LicensePlate(BaseModel):
    bien_so: str
    frame_count: int

class LicensePlateExit(BaseModel):
    bien_so: str

@app.post("/save_license_plate")
async def save_license_plate(plate: LicensePlate):
    try:
        # Check for existing record with status "Vào"
        response = requests.post(DB_FIND_API, json={"bien_so": plate.bien_so, "trang_thai": "Vào"})
        response.raise_for_status()
        existing_record = response.json()

        if not existing_record:
            # Check for existing record with status "Ra"
            response_out = requests.post(DB_FIND_API, json={"bien_so": plate.bien_so, "trang_thai": "Ra"})
            response_out.raise_for_status()
            existing_record_out = response_out.json()

            if existing_record_out:
                # Update the "Ra" record with new exit time
                update_response = requests.post(
                    DB_UPDATE_API,
                    json={
                        "filter": {"bien_so": plate.bien_so, "trang_thai": "Ra"},
                        "update_data": {"thoi_gian_ra": str(datetime.now())}
                    }
                )
                update_response.raise_for_status()

            # Insert new "Vào" record
            new_record = {
                "bien_so": plate.bien_so,
                "trang_thai": "Vào",
                "thoi_gian_vao": str(datetime.now()),
                "thoi_gian_ra": None
            }
            insert_response = requests.post(DB_INSERT_API, json=new_record)
            insert_response.raise_for_status()
            return {"bien_so": plate.bien_so, "status": "Vào"}
        return {"bien_so": plate.bien_so, "status": "Đã vào trước đó"}
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi gọi Database Service: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/update_exit")
async def update_exit(plate: LicensePlateExit):
    try:
        # Find existing record with status "Vào"
        response = requests.post(DB_FIND_API, json={"bien_so": plate.bien_so, "trang_thai": "Vào"})
        response.raise_for_status()
        existing_record = response.json()

        if existing_record:
            existing_record = existing_record[0]  # Take the first matching record
            thoi_gian_vao_str = existing_record.get("thoi_gian_vao")
            if not thoi_gian_vao_str:
                raise HTTPException(status_code=400, detail="Không có thời gian vào hợp lệ")

            thoi_gian_vao = datetime.strptime(thoi_gian_vao_str, "%Y-%m-%d %H:%M:%S.%f")
            thoi_gian_ra = datetime.now()
            tong_phut = (thoi_gian_ra - thoi_gian_vao).total_seconds() / 60
            tong_phut = math.ceil(tong_phut)
            tien_moi_gio = 2000
            gio_gui = math.ceil(tong_phut / 60)
            tong_tien = gio_gui * tien_moi_gio

            # Update the record to "Ra" with exit details
            update_response = requests.post(
                DB_UPDATE_API,
                json={
                    "filter": {"bien_so": plate.bien_so, "trang_thai": "Vào"},
                    "update_data": {
                        "trang_thai": "Ra",
                        "thoi_gian_ra": str(thoi_gian_ra),
                        "tong_thoi_gian_phut": tong_phut,
                        "tong_tien": tong_tien
                    }
                }
            )
            update_response.raise_for_status()
            return {"bien_so": plate.bien_so, "tong_tien": tong_tien, "tong_phut": tong_phut}
        return {"bien_so": plate.bien_so, "status": "Không tìm thấy xe đang ở trạng thái Vào"}
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi gọi Database Service: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_license_plates")
async def get_license_plates(trang_thai: str = None):
    try:
        query = {}
        if trang_thai and trang_thai != "Tất cả":
            query["trang_thai"] = trang_thai
        response = requests.post(DB_FIND_API, json=query)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi gọi Database Service: {str(e)}")