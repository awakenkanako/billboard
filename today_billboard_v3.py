import argparse
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup

def parse_date(s: str) -> datetime:
    return datetime.strptime(s, "%Y-%m-%d")

def this_week_saturday(today=None) -> datetime:
    """월=0 ... 일=6 기준으로 같은 주 토요일(5)을 반환.
    일요일(6)에는 전날(어제) 토요일을 반환합니다."""
    if today is None:
        today = datetime.now()
    wd = today.weekday()  # Mon=0 ... Sun=6
    delta = 5 - wd
    return (today + timedelta(days=delta)).replace(hour=0, minute=0, second=0, microsecond=0)

def daterange_by_7days(start: datetime, end: datetime):
    cur = start
    while cur <= end:
        yield cur.strftime("%Y-%m-%d")
        cur += timedelta(days=7)

def main(start_date: datetime, end_date: datetime, file_path: str):
    if end_date < start_date:
        raise ValueError("끝날짜가 시작날짜보다 빠릅니다.")

    # 헤더 1회 기록
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("날짜\t" + "\t".join([f"{i}위 제목\t{i}위 아티스트" for i in range(1, 101)]) + "\n")
        f.flush()

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/91.0.4472.124 Safari/537.36"
        )
    }

    with open(file_path, "a", encoding="utf-8") as f:
        for date in daterange_by_7days(start_date, end_date):
            url = f"https://www.billboard.com/charts/hot-100/{date}/"
            try:
                resp = requests.get(url, headers=headers, timeout=20)
            except Exception as e:
                print(f"{date} 요청 실패: {e}")
                f.write(f"{date}\t(요청 실패)\n")
                f.flush()
                continue

            if resp.status_code != 200:
                print(f"{date} 페이지 로드 실패: {resp.status_code}")
                f.write(f"{date}\t(페이지 로드 실패)\n")
                f.flush()
                continue

            soup = BeautifulSoup(resp.text, "html.parser")

            # 곡명
            title_tags = soup.find_all(
                "h3",
                class_="c-title a-font-basic u-letter-spacing-0010 u-max-width-397 "
                       "lrv-u-font-size-16 lrv-u-font-size-14@mobile-max u-line-height-22px "
                       "u-word-spacing-0063 u-line-height-normal@mobile-max a-truncate-ellipsis-2line "
                       "lrv-u-margin-b-025 lrv-u-margin-b-00@mobile-max",
            )
            song_titles = [t.get_text(strip=True) for t in title_tags]
            if len(song_titles) < 100:
                song_titles += ["(데이터 없음)"] * (100 - len(song_titles))
            song_titles = song_titles[:100]

            # 아티스트
            artist_tags = soup.find_all(
                "span",
                class_=[
                    "c-label a-font-secondary",
                    "u-letter-spacing-0010",
                    "u-font-size-15",
                    "u-line-height-21px",
                    "u-line-height-18px@mobile-max",
                    "u-font-size-13@mobile-max",
                    "lrv-u-display-block",
                    "u-max-width-397",
                    "a-truncate-ellipsis-2line",
                ],
            )
            before_filter = [t.get_text(strip=True) for t in artist_tags]
            artist_names = [a for a in before_filter if "RIAA Certification:" not in a]
            if len(artist_names) < 100:
                artist_names += ["(데이터 없음)"] * (100 - len(artist_names))
            artist_names = artist_names[:100]

            # 콘솔 샘플
            print(f"저장 완료: {date}")
            print(f"곡 숫자 : {len(title_tags)}")
            print(f"1위: {song_titles[0]} - {artist_names[0]}")
            print(f"2위: {song_titles[1]} - {artist_names[1]}")
            print(f"3위: {song_titles[2]} - {artist_names[2]}")
            print("=" * 50)

            # 파일 기록
            row = [date] + [x for pair in zip(song_titles, artist_names) for x in pair]
            f.write("\t".join(row) + "\n")
            f.flush()

    print(f"모든 데이터가 '{file_path}' 파일로 저장되었습니다.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Billboard Hot 100 스크래퍼 (7일 간격)")
    # 날짜는 0~2개 허용: [], [start], [start, end]
    parser.add_argument("dates", nargs="*", help="0~2개: [시작(YYYY-MM-DD) [끝(YYYY-MM-DD)]]")
    parser.add_argument("--out", default="./billboard_top100_history_today.txt", help="출력 파일 경로")
    args = parser.parse_args()

    if len(args.dates) == 0:
        sat = this_week_saturday()
        start_dt = end_dt = sat
    elif len(args.dates) == 1:
        start_dt = end_dt = parse_date(args.dates[0])
    elif len(args.dates) == 2:
        start_dt, end_dt = parse_date(args.dates[0]), parse_date(args.dates[1])
    else:
        raise SystemExit("날짜 인자는 0개, 1개 또는 2개만 허용합니다.")

    main(start_dt, end_dt, args.out)
