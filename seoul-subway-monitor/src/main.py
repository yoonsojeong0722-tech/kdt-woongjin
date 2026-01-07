import schedule
import time
from .config import Config
from .api_client import SeoulMetroAPI
from .db_client import SubwayDB

def job():
    """
    주기적으로 실행될 작업:
    1. 각 호선별 API 데이터 수집
    2. DB 적재
    """
    print(f"[System] Starting data collection job at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    api_client = SeoulMetroAPI()
    db_client = SubwayDB()

    for line_name in Config.TARGET_LINES:
        # 1. 데이터 수집
        data = api_client.get_realtime_position(line_name)
        
        if data:
            # 2. 데이터 적재
            success = db_client.insert_positions(data)
            if success:
                print(f" -> {line_name}: Success")
            else:
                print(f" -> {line_name}: Failed to insert DB")
        else:
            print(f" -> {line_name}: No data or API Error")

    print("[System] Job finished.\n")

def main():
    print("=== Seoul Subway Monitoring System Started ===")
    
    # 설정 검증
    try:
        Config.validate_config()
    except ValueError as e:
        print(f"[Critical Error] Configuration failed: {e}")
        return

    # 초기 1회 실행
    job()

    # 스케줄 설정 (1분마다 실행)
    schedule.every(1).minutes.do(job)

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[System] Monitoring stopped by user.")

if __name__ == "__main__":
    main()
