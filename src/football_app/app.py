from tools.football import get_raw_match_dataa
# src\football_app\tools\football.py

if __name__ == "__main__":
    match_id = 22949
    match_data = get_raw_match_dataa(match_id)
    print(match_data)