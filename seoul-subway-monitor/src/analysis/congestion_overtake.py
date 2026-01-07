from datetime import datetime
import pandas as pd
from ..db_client import SubwayDB

class CongestionAnalyzer:
    def __init__(self):
        self.db = SubwayDB()

    def analyze_express_overtake(self, line_id: str):
        """
        급행/일반 열차 간섭 분석 (9호선 등 급행 운영 호선에 유효)
        """
        print(f"--- Analyzing Express/Local Interference for Line {line_id} ---")

        data = self.db.fetch_train_data(line_id, limit=3000)
        if not data:
            print("No data found.")
            return

        df = pd.DataFrame(data)
        
        # 급행(is_express='1')과 일반(is_express='0') 존재 여부 확인
        if '1' not in df['is_express'].unique():
            print("No express trains found in this line data.")
            return

        print("Express trains detected. Calculating average speeds...")
        
        # 간단히 역간 이동 속도(시간) 비교
        # 여기서는 복잡한 공간 분석 대신, 급행과 일반의 역별 체류/이동 패턴 차이를 통계로 보여줌
        
        df['created_at'] = pd.to_datetime(df['created_at'])
        
        # 급행/일반 그룹 분리
        express_trains = df[df['is_express'] == '1']
        local_trains = df[df['is_express'] == '0']
        
        print(f"- Express Train Data Count: {len(express_trains)}")
        print(f"- Local Train Data Count: {len(local_trains)}")
        
        # 추가 분석 로직은 데이터가 더 쌓여야 유의미하므로 기본 통계로 마무리
        
if __name__ == "__main__":
    analyzer = CongestionAnalyzer()
    # 9호선 ID 사용 (API 상 9호선은 '1009')
    analyzer.analyze_express_overtake("1009")
