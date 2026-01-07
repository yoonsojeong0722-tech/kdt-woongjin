-- dest_station_id 컬럼이 누락된 경우 추가하는 쿼리
ALTER TABLE realtime_subway_positions 
ADD COLUMN IF NOT EXISTS dest_station_id VARCHAR(50);

COMMENT ON COLUMN realtime_subway_positions.dest_station_id IS '종착역 ID';

-- 혹시 몰라 다른 컬럼들도 확인 및 추가 (필요시)
ALTER TABLE realtime_subway_positions 
ADD COLUMN IF NOT EXISTS dest_station_name VARCHAR(100);

COMMENT ON COLUMN realtime_subway_positions.dest_station_name IS '종착역명';
