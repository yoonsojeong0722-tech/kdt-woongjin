import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class Config:
    """
    환경 변수 및 설정 값을 관리하는 클래스
    """
    SEOUL_API_KEY = os.getenv("SEOUL_API_KEY")
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")

    # API Base URL
    SEOUL_API_BASE_URL = "http://swopenAPI.seoul.go.kr/api/subway"
    
    # 수집 대상 호선 목록 (필요에 따라 추가/삭제)
    TARGET_LINES = [
        "1호선",
        "2호선",
        "3호선",
        "4호선",
        "5호선",
        "6호선",
        "7호선",
        "8호선",
        "9호선",
        "신분당선",
        "경의중앙선",
        "공항철도"
    ]

    @staticmethod
    def validate_config():
        """
        필수 환경 변수가 설정되어 있는지 확인
        """
        if not Config.SEOUL_API_KEY:
            raise ValueError("SEOUL_API_KEY is not set in environment variables.")
        if not Config.SUPABASE_URL:
            raise ValueError("SUPABASE_URL is not set in environment variables.")
        if not Config.SUPABASE_KEY:
            raise ValueError("SUPABASE_KEY is not set in environment variables.")
