from src.db_client import SubwayDB

db = SubwayDB()
response = db.supabase.table("realtime_subway_positions").select("train_status_code").limit(50).execute()
print([x['train_status_code'] for x in response.data])
