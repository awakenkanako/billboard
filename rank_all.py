import pandas as pd

def extract_songs_with_highest_rank(rank_limit, df):
    output_file = f"./rank_{rank_limit}.txt"
    
    # (1위 ~ (n-1)위) 곡 목록
    top_n_minus_1_set = set()
    if rank_limit > 1:
        for r in range(1, rank_limit):
            top_n_minus_1_set |= set(zip(df[f"{r}위 제목"], df[f"{r}위 아티스트"]))

    # n위 곡 추출
    result_dict = {}
    for _, row in df.iterrows():
        nth_song = row[f"{rank_limit}위 제목"]
        nth_artist = row[f"{rank_limit}위 아티스트"]

        if (nth_song, nth_artist) not in top_n_minus_1_set:
            if (nth_song, nth_artist) not in result_dict:
                result_dict[(nth_song, nth_artist)] = row["날짜"]

    # 파일로 저장
    with open(output_file, "w", encoding="utf-8") as file:
        file.write(f"최초{rank_limit}위 날짜\t곡 제목\t아티스트\n")
        for (song, artist), date in sorted(result_dict.items(), key=lambda x: x[1]):
            file.write(f"{date}\t{song}\t{artist}\n")

    print(f"✅ rank_{rank_limit}.txt 생성 완료")


if __name__ == "__main__":
    input_file = "./billboard_top100_history.txt"
    df = pd.read_csv(input_file, delimiter="\t", encoding="utf-8")

    for rank in range(1, 101):
        extract_songs_with_highest_rank(rank, df)
    
    print("🎉 1위부터 100위까지의 곡 리스트가 모두 생성되었습니다.")
