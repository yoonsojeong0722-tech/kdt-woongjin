import requests
import urllib.parse
from .config import Config

class SeoulMetroAPI:
    """
    서울시 실시간 지하철 위치 정보를 가져오는 API 클라이언트
    """

    def __init__(self):
        self.api_key = Config.SEOUL_API_KEY
        self.base_url = Config.SEOUL_API_BASE_URL

    def get_realtime_position(self, line_name: str):
        """
        특정 호선의 실시간 열차 위치 정보를 가져옵니다.

        Args:
            line_name (str): 검색할 호선명 (예: '1호선', '2호선')

        Returns:
            list: 열차 위치 정보 리스트 (오류 시 빈 리스트 반환)
        """
        # 호선명 URL 인코딩 (한글 처리)
        encoded_line_name = urllib.parse.quote(line_name)
        
        # API 요청 URL 구성 (인증키/json/서비스명/시작위치/종료위치/호선명)
        url = f"{self.base_url}/{self.api_key}/json/realtimePosition/0/100/{encoded_line_name}"

        try:
            response = requests.get(url)
            response.raise_for_status() # HTTP 오류 발생 시 예외 발생
            
            data = response.json()
            
            # API 응답 상태 확인 ('realtimePosition' 또는 'realtimePositionList' 확인)
            if 'realtimePosition' in data:
                return data['realtimePosition']
            elif 'realtimePositionList' in data:
                return data['realtimePositionList']
            else:
                print(f"[API Warning] No data found for {line_name}. Type: {type(data)}, Response: {data}")
                return []

        except requests.exceptions.RequestException as e:
            print(f"[API Error] Failed to fetch data for {line_name}: {e}")
            return []
        except Exception as e:
            print(f"[API Error] Unexpected error for {line_name}: {e}")
            return []
