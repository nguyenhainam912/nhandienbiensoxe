from  datetime import datetime
from pymongo import MongoClient
import math

# Kết nối đến MongoDB local (hoặc thay URI bằng Mongo Atlas nếu dùng cloud)
MONGO_URI = "mongodb+srv://dognam912:1grXOoLgxqvzpOJG@cluster0.b7pflkj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)

# Chọn database và collection
db = client["biensoxe"]
collection = db["bien_so"]


def luu_bien_so(strFinalString, tongframe):
    if strFinalString:
        # Tìm kiếm trong MongoDB xem biển số đã tồn tại chưa và đang ở trạng thái "Vào"
        existing_record = collection.find_one({"bien_so": strFinalString, "trang_thai": "Vào"})

        # Nếu không có biển số "Vào", thêm biển số vào cơ sở dữ liệu
        if not existing_record:
            # Kiểm tra nếu biển số chưa có hoặc đang ra, lưu lại là "Vào"
            existing_record_out = collection.find_one({"bien_so": strFinalString, "trang_thai": "Ra"})
            
            if existing_record_out:
                # Nếu xe đã ra trước đó, cập nhật thời gian ra
                collection.update_one(
                    {"bien_so": strFinalString, "trang_thai": "Ra"},
                    {"$set": {"thoi_gian_ra": str(datetime.now())}}
                )
                print(f"✅ Biển số {strFinalString} đã ra trước đó, cập nhật thời gian ra.")
            
            # Lưu lại trạng thái xe vào
            collection.insert_one({
                "bien_so": strFinalString,
                "trang_thai": "Vào",
                "thoi_gian_vao": str(datetime.now()),
                "thoi_gian_ra": None  # Chưa có thời gian ra
            })
            print(f"✅ Đã lưu biển số {strFinalString} với trạng thái Vào.")
        else:
            # Nếu biển số đã vào thì không làm gì (hoặc bạn có thể cập nhật nếu cần)
            print(f"❌ Biển số {strFinalString} đã vào trước đó.")

def cap_nhat_xe_ra(strFinalString):
    """
    Cập nhật trạng thái 'Ra' cho biển số đã vào trước đó,
    tính thời gian gửi xe và chi phí.
    """
    if not strFinalString:
        print("❌ Biển số trống.")
        return

    # Tìm bản ghi đang ở trạng thái "Vào"
    existing_record = collection.find_one({"bien_so": strFinalString, "trang_thai": "Vào"})

    if existing_record:
        thoi_gian_vao_str = existing_record.get("thoi_gian_vao")
        if not thoi_gian_vao_str:
            print("⚠️ Không có thời gian vào hợp lệ.")
            return

        # Chuyển chuỗi thời gian vào về dạng datetime
        thoi_gian_vao = datetime.strptime(thoi_gian_vao_str, "%Y-%m-%d %H:%M:%S.%f")
        thoi_gian_ra = datetime.now()

        # Tính thời gian chênh lệch (tổng số phút)
        tong_phut = (thoi_gian_ra - thoi_gian_vao).total_seconds() / 60
        tong_phut = math.ceil(tong_phut)  # Làm tròn lên phút

        # Quy đổi tiền gửi xe (ví dụ: 2.000 VND / giờ, làm tròn giờ)
        tien_moi_gio = 2000
        gio_gui = math.ceil(tong_phut / 60)
        tong_tien = gio_gui * tien_moi_gio

        # Cập nhật lại trạng thái là "Ra" và thời gian ra
        collection.update_one(
            {"bien_so": strFinalString, "trang_thai": "Vào"},
            {
                "$set": {
                    "trang_thai": "Ra",
                    "thoi_gian_ra": str(thoi_gian_ra),
                    "tong_thoi_gian_phut": tong_phut,
                    "tong_tien": tong_tien
                }
            }
        )

        print(f"✅ Xe {strFinalString} đã rời bãi.")
        print(f"⏱️ Thời gian gửi: {tong_phut} phút.")
        print(f"💰 Chi phí: {tong_tien:,} VND.")
    else:
        print(f"❌ Không tìm thấy xe {strFinalString} đang ở trạng thái Vào.")

def get_bien_so_by_trang_thai(trang_thai=None):
    """
    Lấy danh sách biển số theo trạng thái ("Vào", "Ra", hoặc None để lấy tất cả)
    """
    try:
        query = {}
        if trang_thai and trang_thai != "Tất cả":
            query["trang_thai"] = trang_thai

        records = list(collection.find(query, {"_id": 0}))
        return records
    except Exception as e:
        print(f"❌ Lỗi khi lấy dữ liệu: {e}")
        return []
