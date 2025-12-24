import pandas as pd
import json
import hashlib
import os

# 입력 파일 (기존 빌보드 100위 데이터 파일)
input_file = "./billboard_top100_history_today.txt"

# 기존 song.json 파일
existing_songs_file = "./songs.json"

# 출력 JSON 파일
songs_output_file = "./songs_today.json"
weekly_rankings_output_file = "./weekly_rankings_today.json"

# 기존 곡 ID 읽기
existing_song_ids = set()
if os.path.exists(existing_songs_file):
    with open(existing_songs_file, "r", encoding="utf-8") as f:
        existing_songs = json.load(f)
        existing_song_ids = {song["_id"] for song in existing_songs}

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

        # 기존 song.json에 있는 곡이면 새로 추가하지 않음
        if song_id not in existing_song_ids and song_id not in song_dict:
            song_dict[song_id] = {
                "_id": song_id,
                "title": song_title,
                "artist": artist_name
            }

        ranking_list.append(song_id)

    weekly_rankings.append({
        "_id": date.replace("-", ""),  # 날짜 기반 ID
        "date": date,
        "rank": ranking_list
    })

# 새로운 곡만 song_today.json으로 저장
with open(songs_output_file, "w", encoding="utf-8") as f:
    json.dump(list(song_dict.values()), f, ensure_ascii=False, indent=4)

# weekly_rankings_today.json은 기존과 동일하게 저장
with open(weekly_rankings_output_file, "w", encoding="utf-8") as f:
    json.dump(weekly_rankings, f, ensure_ascii=False, indent=4)

print(f"신규 곡 데이터가 '{songs_output_file}' 파일에 저장되었습니다.")
print(f"주간 순위 데이터가 '{weekly_rankings_output_file}' 파일에 저장되었습니다.")
