import pandas as pd
import json
import hashlib

# 입력 파일 (기존 빌보드 100위 데이터 파일)
input_file = "./billboard_top100_history.txt"

# 출력 JSON 파일
songs_output_file = "./songs.json"
weekly_rankings_output_file = "./weekly_rankings.json"

# 데이터 로드
df = pd.read_csv(input_file, delimiter="\t", encoding="utf-8")

# 곡 정보를 저장할 딕셔너리 (중복 방지)
song_dict = {}

# 주간 순위 데이터를 저장할 리스트
weekly_rankings = []

# 고유한 곡 ID를 생성하는 함수
def generate_song_id(title, artist):
    hash_input = f"{title}-{artist}".encode("utf-8")
    return hashlib.md5(hash_input).hexdigest()[:16]  # 16자리 해시값

# 데이터 변환
for index, row in df.iterrows():
    date = row["날짜"]
    ranking_list = []

    for rank in range(1, 101):  # 1위부터 100위까지 반복
        song_title = row[f"{rank}위 제목"]
        artist_name = row[f"{rank}위 아티스트"]

        # 데이터 없음 처리
        if song_title == "(데이터 없음)" or artist_name == "(데이터 없음)":
            ranking_list.append(None)
            continue

        # 곡 ID 생성
        song_id = generate_song_id(song_title, artist_name)

        # 곡 정보 저장 (중복 방지)
        if song_id not in song_dict:
            song_dict[song_id] = {
                "_id": song_id,
                "title": song_title,
                "artist": artist_name
            }

        # 주간 순위 리스트에 곡 ID 추가
        ranking_list.append(song_id)

    # 주간 순위 데이터 저장
    weekly_rankings.append({
        "_id": date.replace("-", ""),  # 날짜 기반 ID (YYYYMMDD)
        "date": date,
        "rank": ranking_list
    })

# JSON 파일 저장
with open(songs_output_file, "w", encoding="utf-8") as f:
    json.dump(list(song_dict.values()), f, ensure_ascii=False, indent=4)

with open(weekly_rankings_output_file, "w", encoding="utf-8") as f:
    json.dump(weekly_rankings, f, ensure_ascii=False, indent=4)

print(f"곡 데이터가 '{songs_output_file}' 파일에 저장되었습니다.")
print(f"주간 순위 데이터가 '{weekly_rankings_output_file}' 파일에 저장되었습니다.")
