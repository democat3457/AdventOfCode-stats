from collections import defaultdict
from typing import Any, Callable
import requests
import re
from datetime import time, timedelta
from statistics import median
import csv
from pathlib import Path
from tqdm import tqdm

data: dict[tuple[int, int], tuple[list[time], list[time]]] = {}

cache_folder = Path("cache_aoclb")
cache_folder.mkdir(exist_ok=True)

save_folder = Path("aoc_data")
save_folder.mkdir(exist_ok=True)

start_year = 2015
end_year = 2023

def median_both_stars(tbs: list[timedelta], tfs: list[timedelta]):
    return median(tbs)
def median_first_star(tbs: list[timedelta], tfs: list[timedelta]):
    return median(tfs)
def median_second_star(tbs: list[timedelta], tfs: list[timedelta]):
    return median(tbs)-median(tfs)
def min_both_stars(tbs: list[timedelta], tfs: list[timedelta]):
    return min(tbs)
def min_first_star(tbs: list[timedelta], tfs: list[timedelta]):
    return min(tfs)
def min_second_star(tbs: list[timedelta], tfs: list[timedelta]):
    return min(tbs)-min(tfs)
def median_star_ratio(tbs: list[timedelta], tfs: list[timedelta]):
    return median(tfs) / median(tbs)
def min_star_ratio(tbs: list[timedelta], tfs: list[timedelta]):
    return min(tfs) / min(tbs)

funcs: list[Callable[[list[timedelta], list[timedelta]], Any]] = [
    median_both_stars,
    median_first_star,
    median_second_star,
    min_both_stars,
    min_first_star,
    min_second_star,
    median_star_ratio,
    min_star_ratio,
]

for year in range(start_year, end_year+1):
    for day in range(1, 26):
        yd_path = (cache_folder / f'{year}_{day}.html')
        if yd_path.exists():
            html = yd_path.read_text()
        else:
            url = f'https://adventofcode.com/{year}/leaderboard/day/{day}'
            response = requests.get(url)
            if response.status_code != 200:
                if year != end_year:
                    print('error fetching url')
                continue
            html = response.text
            yd_path.write_text(html)
        both_stars = html.index('>both stars<')
        first_star = html.index('>first star<')
        bs: list[time] = [ time.fromisoformat(match) for match in re.findall(r'<span class="leaderboard-time">.+  (\d\d:\d\d:\d\d)</span>', html[both_stars:first_star]) ]
        fs: list[time] = [ time.fromisoformat(match) for match in re.findall(r'<span class="leaderboard-time">.+  (\d\d:\d\d:\d\d)</span>', html[first_star:]) ]
        data[(year, day)] = (bs, fs)

year_day_data_per_func: dict[str, dict[int, list[str]]] = defaultdict(lambda: defaultdict(list))
for year in range(start_year, end_year+1):
    for day in range(1, 26):
        if (year, day) not in data:
            for func in funcs:
                year_day_data_per_func[func.__name__][year].append('')
            continue
        bs, fs = data[(year, day)]
        tbs = [timedelta(hours=t.hour, minutes=t.minute, seconds=t.second, microseconds=t.microsecond) for t in bs]
        tfs = [timedelta(hours=t.hour, minutes=t.minute, seconds=t.second, microseconds=t.microsecond) for t in fs]
        for func in funcs:
            result = func(tbs, tfs)
            if isinstance(result, timedelta):
                s = str(result).rjust(8, '0')
            elif isinstance(result, str):
                s = result
            else:
                s = f'{result:g}'
            year_day_data_per_func[func.__name__][year].append(s)

for func_name, year_day_data in year_day_data_per_func.items():
    rows = [list(range(start_year, end_year+1))]
    for day in range(0,25):
        rows.append([year_day_data[year][day] for year in range(start_year, end_year+1)])

    print(f"Writing to {save_folder}/{func_name}.csv...")
    with (save_folder / f"{func_name}.csv").open('w') as f:
        writer = csv.writer(f)
        writer.writerows(rows)
