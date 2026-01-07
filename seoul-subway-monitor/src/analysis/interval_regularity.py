from datetime import datetime
import pandas as pd
from ..db_client import SubwayDB

class IntervalAnalyzer:
    def __init__(self):
        self.db = SubwayDB()

    def analyze_interval(self, line_id: str):
        """
        배차 간격 정기성 분석
        :param line_id: 분석할 호선 ID
        """
        print(f"--- Analyzing Interval Regularity for Line {line_id} ---")
        
        # 1. 데이터 가져오기
        data = self.db.fetch_train_data(line_id, limit=2000)
        if not data:
            print("No data found.")
            return

        df = pd.DataFrame(data)
        
        # 2. 필요한 컬럼 선택 및 전처리
        # created_at을 datetime 객체로 변환
        df['created_at'] = pd.to_datetime(df['created_at'])
        
        # 분석 대상: "특정 역"에 도착(train_status_code='1')한 데이터
        # 역별, 방향별로 그룹화
        # train_status_code: 0:진입, 1:도착, 2:출발
        # 데이터 타입 안전성을 위해 문자열로 변환
        df['train_status_code'] = df['train_status_code'].astype(str)
        
        arrivals = df[df['train_status_code'] == '1'].copy()
        print(f"[Debug] Total records: {len(df)}, Arrivals(1): {len(arrivals)}")
        
        if arrivals.empty:
            print("No arrival data found.")
            return
            
        # 정렬: 역, 방향, 시간순
        arrivals = arrivals.sort_values(by=['station_name', 'direction_type', 'created_at'])
        
        # 3. 배차 간격 계산
        # 이전 열차와의 시간 차이 계산 (초 단위)
        arrivals['prev_arrival'] = arrivals.groupby(['station_name', 'direction_type'])['created_at'].shift(1)
        arrivals['interval_seconds'] = (arrivals['created_at'] - arrivals['prev_arrival']).dt.total_seconds()
        
        # 4. 통계 산출
        # 역별, 방향별 평균 간격 및 표준편차
        stats = arrivals.groupby(['station_name', 'direction_type'])['interval_seconds'].agg(['mean', 'std', 'count']).reset_index()
        
        # 결과 출력 (NaN 제외)
        stats = stats.dropna()
        
        print("\n[Analysis Result: Station Intervals]")
        for _, row in stats.iterrows():
            station = row['station_name']
            direction = "Up/Inner" if row['direction_type'] == '0' else "Down/Outer"
            mean_min = row['mean'] / 60
            std_min = row['std'] / 60
            count = int(row['count'])
            
            print(f"- {station} ({direction}): Avg {mean_min:.1f} min (+/- {std_min:.1f} min) [n={count}]")
            
            # 간단한 이상치 탐지 (Bunching)
            if std_min > 5.0: # 표준편차가 5분 이상이면 불규칙하다고 판단 (임의 기준)
                print(f"  >>> WARNING: Irregular intervals detected at {station}!")

if __name__ == "__main__":
    analyzer = IntervalAnalyzer()
    # 예시: 2호선(ID: 1002) 테스트
    analyzer.analyze_interval("1002")
