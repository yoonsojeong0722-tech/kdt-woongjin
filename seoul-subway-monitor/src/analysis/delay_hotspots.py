from datetime import datetime
import pandas as pd
from ..db_client import SubwayDB

class DelayAnalyzer:
    def __init__(self):
        self.db = SubwayDB()

    def analyze_station_dwell_time(self, line_id: str):
        """
        지연 발생 구간 탐지: 역별 체류 시간 분석
        :param line_id: 분석할 호선 ID
        """
        print(f"--- Analyzing Delay Hotspots (Dwell Time) for Line {line_id} ---")
        
        # 1. 데이터 가져오기
        data = self.db.fetch_train_data(line_id, limit=3000)
        if not data:
            print("No data found.")
            return

        df = pd.DataFrame(data)
        df['created_at'] = pd.to_datetime(df['created_at'])
        
        # 2. 도착(1) 및 출발(2) 데이터만 필터링
        dwell_events = df[df['train_status_code'].isin(['1', '2'])].copy()
        
        # 정렬: 열차번호, 시간순
        dwell_events = dwell_events.sort_values(by=['train_number', 'created_at'])
        
        # 3. 체류 시간 계산 로직
        # 동일 열차가 동일 역에서 '도착' 후 '출발'한 시간 차이를 계산해야 함
        # 이를 위해 pivot 또는 shift 사용. 여기서는 단순화하여 shift 사용
        
        dwell_events['prev_status'] = dwell_events.groupby(['train_number', 'station_name'])['train_status_code'].shift(1)
        dwell_events['prev_time'] = dwell_events.groupby(['train_number', 'station_name'])['created_at'].shift(1)
        
        # 조건: 이전 상태가 '1'(도착)이고 현재 상태가 '2'(출발)인 경우
        departures = dwell_events[
            (dwell_events['train_status_code'] == '2') & 
            (dwell_events['prev_status'] == '1')
        ].copy()
        
        if departures.empty:
            print("No valid dwell time data found (need arrival->departure pairs).")
            return
            
        departures['dwell_seconds'] = (departures['created_at'] - departures['prev_time']).dt.total_seconds()
        
        # 4. 통계 산출
        stats = departures.groupby('station_name')['dwell_seconds'].agg(['mean', 'max', 'count']).sort_values(by='mean', ascending=False)
        
        print("\n[Analysis Result: Station Dwell Times]")
        for station, row in stats.iterrows():
            mean_sec = row['mean']
            max_sec = row['max']
            count = int(row['count'])
            
            print(f"- {station}: Avg {mean_sec:.1f}s (Max {max_sec:.1f}s) [n={count}]")
            
            if mean_sec > 60: # 평균 60초 이상 정차 시 경고
                print(f"  >>> WARNING: Long dwell time at {station}!")

if __name__ == "__main__":
    analyzer = DelayAnalyzer()
    analyzer.analyze_station_dwell_time("1002")
