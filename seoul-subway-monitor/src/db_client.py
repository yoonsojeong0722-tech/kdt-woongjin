from supabase import create_client, Client
from .config import Config

class SubwayDB:
    """
    Supabase 데이터베이스와 상호작용하는 클라이언트
    """

    def __init__(self):
        self.supabase: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
        self.table_name = "realtime_subway_positions"

    def insert_positions(self, data_list: list):
        """
        수집된 열차 위치 데이터를 DB에 적재할 형식으로 변환 후 삽입합니다.

        Args:
            data_list (list): API로부터 수신한 원본 데이터 리스트

        Returns:
            bool: 성공 여부
        """
        if not data_list:
            return False

        transformed_data = []
        for item in data_list:
            # Snake Case로 키 매핑 및 데이터 타입 변환
            transformed_item = {
                "line_id": item.get("subwayId"),
                "line_name": item.get("subwayNm"),
                "station_id": item.get("statnId"),
                "station_name": item.get("statnNm"),
                "train_number": item.get("trainNo"),
                "last_received_date": item.get("lastRecptnDt"),
                "last_received_time": item.get("recptnDt"),
                "direction_type": item.get("updnLine"),
                "destination_station_id": item.get("statnTid"),
                "destination_station_name": item.get("statnTnm"),
                "train_status_code": item.get("trainSttus"),
                "is_express": item.get("directAt"),
                "is_last_train": item.get("lstcarAt") == "1", # Boolean 변환
                # created_at은 DB Default 값 사용 (now())
            }
            transformed_data.append(transformed_item)

        try:
            # 데이터 일괄 삽입 (bulk insert)
            response = self.supabase.table(self.table_name).insert(transformed_data).execute()
            print(f"[DB Info] Successfully inserted {len(transformed_data)} records.")
            return True
        except Exception as e:
            print(f"[DB Error] Failed to insert data: {e}")
            return False

    def fetch_train_data(self, line_id: str, limit: int = 1000):
        """
        분석을 위해 특정 호선의 최근 데이터를 가져옵니다.
        """
        try:
            response = self.supabase.table(self.table_name)\
                .select("*")\
                .eq("line_id", line_id)\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()
            return response.data
        except Exception as e:
            print(f"[DB Error] Failed to fetch data: {e}")
            return []
