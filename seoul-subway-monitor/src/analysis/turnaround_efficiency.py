from datetime import datetime
import pandas as pd
from ..db_client import SubwayDB

class TurnaroundAnalyzer:
    def __init__(self):
        self.db = SubwayDB()

    def analyze_turnaround(self, line_id: str):
        """
        회차 효율성 분석
        :param line_id: 분석할 호선 ID
        """
        print(f"--- Analyzing Turnaround Efficiency for Line {line_id} ---")

        data = self.db.fetch_train_data(line_id, limit=5000)
        if not data:
            print("No data found.")
            return

        df = pd.DataFrame(data)
        df['created_at'] = pd.to_datetime(df['created_at'])

        # 종착역 근처 데이터만 필요하지만, 일단 전체에서 로직 처리
        # 로직: 동일 train_number가 방향(direction_type)을 바꾸는 시점 포착
        
        df = df.sort_values(by=['train_number', 'created_at'])
        
        df['prev_direction'] = df.groupby('train_number')['direction_type'].shift(1)
        df['prev_time'] = df.groupby('train_number')['created_at'].shift(1)
        
        # 방향이 변경된 케이스 (예: 0 -> 1 또는 1 -> 0)
        # 단, 실제 운행 중 방향 변경은 종착역 회차 외에는 드물다.
        turnarounds = df[
            (df['direction_type'] != df['prev_direction']) &
            (df['prev_direction'].notnull())
        ].copy()
        
        if turnarounds.empty:
            print("No turnaround events detected.")
            return

        turnarounds['turnaround_time_min'] = (turnarounds['created_at'] - turnarounds['prev_time']).dt.total_seconds() / 60
        
        print("\n[Analysis Result: Turnaround Events]")
        for _, row in turnarounds.iterrows():
            train = row['train_number']
            station = row['station_name'] # 회차 후 첫 식별 역
            time_diff = row['turnaround_time_min']
            print(f"- Train {train} at {station}: {time_diff:.1f} min gap between direction change")
            
if __name__ == "__main__":
    analyzer = TurnaroundAnalyzer()
    analyzer.analyze_turnaround("1002")
