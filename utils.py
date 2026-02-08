import datetime
import pandas as pd

def time_to_seconds(time_str):
    """'HH:MM:SS' または 'MM:SS' 形式の時間を秒に変換する"""
    # 文字列でない場合は文字列に変換し、'nan'文字列を0として扱う
    if not isinstance(time_str, str):
        time_str = str(time_str)

    # NaN（欠損値）または文字列の 'nan' の場合は0秒として扱う
    if pd.isna(time_str) or time_str.strip().lower() == 'nan':
        return 0

    try:
        parts = list(map(int, time_str.split(':')))
        if len(parts) == 3: # HH:MM:SS
            hours, minutes, seconds = parts
            return hours * 3600 + minutes * 60 + seconds
        elif len(parts) == 2: # MM:SS
            minutes, seconds = parts
            return minutes * 60 + seconds
        else:
            st.warning(f"時刻形式が不正です: {time_str}。'HH:MM:SS' または 'MM:SS' 形式か確認してください。")
            return 0
    except ValueError:
        st.warning(f"時刻形式が不正です: {time_str}。数値で構成されているか確認してください。")
        return 0

def create_youtube_link(video_id, timestamp_seconds):
    """YouTubeのタイムスタンプ付きURLを生成する"""
    if video_id and timestamp_seconds is not None:
        # YouTubeのURLは "VIDEO_ID&t=SECONDSs" の形式
        return f"{video_id}&t={timestamp_seconds}s"
    return "#" # video_idがない場合はリンクなし


# --- サーブの種類をグルーピングする関数 ---
def group_serve_type(serve_type):
    """サーブの種類を、指定された文字列が含まれるカテゴリにグルーピングする。"""
    if pd.isna(serve_type) or serve_type == '':
        return 'その他/不明'
    
    serve_type_lower = str(serve_type).lower()
    
    # ご指定の文字列が含まれるかチェック
    if 'yg' in serve_type_lower or 'ygサーブ' in serve_type_lower:
        return 'YGサーブ'
    elif '順横' in serve_type_lower:
        return '順横'
    elif '巻込み' in serve_type_lower or '巻き込み' in serve_type_lower:
        return '巻込み'
    elif 'バック' in serve_type_lower:
        return 'バック'
    elif 'キック' in serve_type_lower:
        return 'キック'
    else:
        return 'その他/不明'

# --- サーブのコースをグルーピングする関数 ---
def group_serve_course(serve_course):
    """サーブのコースを、「ロング」または「短いサーブ」にグルーピングする。"""
    if pd.isna(serve_course) or serve_course == '':
        return '不明なコース'
    
    serve_course_lower = str(serve_course).lower()

    if 'ロング' in serve_course_lower:
        return serve_course # ロングを含む場合は元のコース名を維持
    else:
        return '短いサーブ'


def group_detailed_serve_course(course_str):
    """
    サーブコースをフォア前、ミドル前、バック前、フォアロング、ミドルロング、バックロングにグループ化する。
    入力例: 'フォア前', 'ミドルロング', 'Bロング', 'F前' などに対応。
    """
    if pd.isna(course_str):
        return None
    
    course_str = str(course_str).strip().upper() # 大文字に変換して統一

    if 'フォア' in course_str or course_str.startswith('F'):
        if '前' in course_str or 'SHORT' in course_str or 'サイド' in course_str or 'ショート' in course_str:
            return 'フォア前'
        elif 'ロング' in course_str or 'LONG' in course_str:
            return 'フォアロング'
    elif 'ミドル' in course_str or course_str.startswith('M'):
        if '前' in course_str or 'SHORT' in course_str or 'ショート' in course_str:
            return 'ミドル前'
        elif 'ロング' in course_str or 'LONG' in course_str:
            return 'ミドルロング'
    elif 'バック' in course_str or course_str.startswith('B'):
        if '前' in course_str or 'SHORT' in course_str or 'サイド' in course_str or 'ショート' in course_str:
            return 'バック前'
        elif 'ロング' in course_str or 'LONG' in course_str:
            return 'バックロング'
    
    return 'その他' # どのカテゴリにも当てはまらない場合