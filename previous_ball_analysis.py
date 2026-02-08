import streamlit as st
import pandas as pd

# --- 相手の直前コースと自分の打球技術の成功率分析関数 ---
def display_previous_ball_analysis(df):
    """
    相手の直前コースと自分の打球技術（バックハンド系/フォアハンド系）の成功率の関連性をStreamlitのUIに一つの表で表示する。
    1行に複数の自分の打球イベントが記載されている場合に対応し、それぞれを独立してカウント。
    列名の数字部分を全角に対応。
    ただし、コースと逆の打球（例：コースがバックで打球がフォア）が発生したら、そのラリーの以後の打球は確認しない。
    得点数と得率は表示しない。
    
    Args:
        df (pd.DataFrame): 試合の得失点データ
    """
    st.subheader("相手の直前コースと自分の打球技術の成功率") # タイトルも修正

    # 列名マップ: コード内で使用するキーと、実際のデータフレームの列名（全角数字）のマッピング
    COLUMN_MAP = {
        '誰のサーブか': '誰のサーブか', 
        '得点者': '得点者', # この列はもう集計には使われないが、データの存在チェックのために残す
        'サーブのコース': 'サーブのコース', 
        'レシーブの種類': 'レシーブの種類', 
        'レシーブのコース': 'レシーブのコース', 
        'レシーブの質': 'レシーブの質',
        '３球目の種類': '３球目の種類',  # 全角に修正
        '３球目のコース': '３球目のコース',  # 全角に修正
        '３球目の質': '３球目の質',      # 全角に修正
        '４球目の種類': '４球目の種類',  # 全角に修正
        '４球目のコース': '４球目のコース',  # 全角に修正
        '４球目の質': '４球目の質',      # 全角に修正
        '５球目の種類': '５球目の種類',  # 全角に修正
        '５球目のコース': '５球目のコース',  # 全角に修正
        '５球目の質': '５球目の質',      # 全角に修正
        '６球目の種類': '６球目の種類',  # 全角に修正
        '６球目のコース': '６球目のコース',  # 全角に修正
        '６球目の質': '６球目の質'       # 全角に修正
    }
    
    # 必須列のチェック
    actual_required_cols = list(COLUMN_MAP.values())
    if df.empty or not all(col in df.columns for col in actual_required_cols):
        missing_cols = [col for col in actual_required_cols if col not in df.columns]
        st.warning(f"直前の打球分析に必要なデータ列が見つかりません: {', '.join(missing_cols)}")
        return

    df = df.fillna('')
    analysis_data = []

    for index, row in df.iterrows():
        current_ball_events = []
        skip_further_checks = False # 新しいフラグ

        # 自分のサーブ時のプレー
        if row[COLUMN_MAP['誰のサーブか']] == '自分':
            # 自分が３球目を打った場合
            if row[COLUMN_MAP['３球目の種類']] != '' and not skip_further_checks:
                opponent_course = 'バック' if 'バック' in row[COLUMN_MAP['レシーブのコース']] else ('フォア' if 'フォア' in row[COLUMN_MAP['レシーブのコース']] else None)
                my_stroke_type = 'バックハンド系' if 'バック' in row[COLUMN_MAP['３球目の種類']] else ('フォアハンド系' if 'フォア' in row[COLUMN_MAP['３球目の種類']] else None)
                is_success = 1 if 'ミス' not in row[COLUMN_MAP['３球目の質']] else 0
                
                if opponent_course and my_stroke_type and is_success is not None:
                    current_ball_events.append({
                        '相手の直前コース': opponent_course, '自分の打球技術': my_stroke_type,
                        '成功': is_success, '総数': 1
                    })
                    # コースと逆の打球が発生した場合、フラグを立てる
                    if (opponent_course == 'バック' and my_stroke_type == 'フォアハンド系') or \
                       (opponent_course == 'フォア' and my_stroke_type == 'バックハンド系'):
                        skip_further_checks = True
            
            # 自分が５球目を打った場合 (独立したif文)
            if row[COLUMN_MAP['５球目の種類']] != '' and not skip_further_checks:
                opponent_course = 'バック' if 'バック' in row[COLUMN_MAP['４球目のコース']] else ('フォア' if 'フォア' in row[COLUMN_MAP['４球目のコース']] else None)
                my_stroke_type = 'バックハンド系' if 'バック' in row[COLUMN_MAP['５球目の種類']] else ('フォアハンド系' if 'フォア' in row[COLUMN_MAP['５球目の種類']] else None)
                is_success = 1 if 'ミス' not in row[COLUMN_MAP['５球目の質']] else 0
                if opponent_course and my_stroke_type and is_success is not None:
                    current_ball_events.append({
                        '相手の直前コース': opponent_course, '自分の打球技術': my_stroke_type,
                        '成功': is_success, '総数': 1
                    })
                    if (opponent_course == 'バック' and my_stroke_type == 'フォアハンド系') or \
                       (opponent_course == 'フォア' and my_stroke_type == 'バックハンド系'):
                        skip_further_checks = True

        # 相手のサーブ時のプレー
        elif row[COLUMN_MAP['誰のサーブか']] == '相手':
            # 自分がレシーブ（2球目）を打った場合
            if row[COLUMN_MAP['レシーブの種類']] != '' and not skip_further_checks:
                opponent_course = 'バック' if 'バック' in row[COLUMN_MAP['サーブのコース']] else ('フォア' if 'フォア' in row[COLUMN_MAP['サーブのコース']] else None)
                my_stroke_type = 'バックハンド系' if 'バック' in row[COLUMN_MAP['レシーブの種類']] else ('フォアハンド系' if 'フォア' in row[COLUMN_MAP['レシーブの種類']] else None)
                is_success = 1 if 'ミス' not in row[COLUMN_MAP['レシーブの質']] else 0
                if opponent_course and my_stroke_type and is_success is not None:
                    current_ball_events.append({
                        '相手の直前コース': opponent_course, '自分の打球技術': my_stroke_type,
                        '成功': is_success, '総数': 1
                    })
                    if (opponent_course == 'バック' and my_stroke_type == 'フォアハンド系') or \
                       (opponent_course == 'フォア' and my_stroke_type == 'バックハンド系'):
                        skip_further_checks = True

            # 自分が４球目を打った場合 (独立したif文)
            if row[COLUMN_MAP['４球目の種類']] != '' and not skip_further_checks:
                opponent_course = 'バック' if 'バック' in row[COLUMN_MAP['３球目のコース']] else ('フォア' if 'フォア' in row[COLUMN_MAP['３球目のコース']] else None)
                my_stroke_type = 'バックハンド系' if 'バック' in row[COLUMN_MAP['４球目の種類']] else ('フォアハンド系' if 'フォア' in row[COLUMN_MAP['４球目の種類']] else None)
                is_success = 1 if 'ミス' not in row[COLUMN_MAP['４球目の質']] else 0
                if opponent_course and my_stroke_type and is_success is not None:
                    current_ball_events.append({
                        '相手の直前コース': opponent_course, '自分の打球技術': my_stroke_type,
                        '成功': is_success, '総数': 1
                    })
                    if (opponent_course == 'バック' and my_stroke_type == 'フォアハンド系') or \
                       (opponent_course == 'フォア' and my_stroke_type == 'バックハンド系'):
                        skip_further_checks = True

            # 自分が６球目を打った場合 (独立したif文)
            if row[COLUMN_MAP['６球目の種類']] != '' and not skip_further_checks:
                opponent_course = 'バック' if 'バック' in row[COLUMN_MAP['５球目のコース']] else ('フォア' if 'フォア' in row[COLUMN_MAP['５球目のコース']] else None)
                my_stroke_type = 'バックハンド系' if 'バック' in row[COLUMN_MAP['６球目の種類']] else ('フォアハンド系' if 'フォア' in row[COLUMN_MAP['６球目の種類']] else None)
                is_success = 1 if 'ミス' not in row[COLUMN_MAP['６球目の質']] else 0
                if opponent_course and my_stroke_type and is_success is not None:
                    current_ball_events.append({
                        '相手の直前コース': opponent_course, '自分の打球技術': my_stroke_type,
                        '成功': is_success, '総数': 1
                    })
                    if (opponent_course == 'バック' and my_stroke_type == 'フォアハンド系') or \
                       (opponent_course == 'フォア' and my_stroke_type == 'バックハンド系'):
                        skip_further_checks = True
        
        # そのラリー（行）で検出された全ての打球イベントを追加
        analysis_data.extend(current_ball_events)


    if not analysis_data:
        st.info("直前の打球分析に必要なデータが不足しているか、条件に合致するプレーがありませんでした。")
        return

    # 集計と整形
    analysis_df = pd.DataFrame(analysis_data)
    summary_df = analysis_df.groupby([
        '相手の直前コース', 
        '自分の打球技術'
    ]).agg(
        総数=('総数', 'sum'),
        成功数=('成功', 'sum')
    ).reset_index()

    summary_df['成功率 (%)'] = (summary_df['成功数'] / summary_df['総数']) * 100
    summary_df['成功率 (%)'] = summary_df['成功率 (%)'].round(1)
    
    summary_df = summary_df[['相手の直前コース', '自分の打球技術', '総数', '成功数', '成功率 (%)']]

    # UI表示
    st.markdown("---")
    st.dataframe(summary_df.style.format({'成功率 (%)': "{:.1f}%"}))


def get_previous_ball_analysis_for_ai(df):
    """
    相手の直前コースと自分の打球技術（バックハンド系/フォアハンド系）の成功率を統合してAIに渡すためのMarkdown文字列を生成する。
    ただし、コースと逆の打球（例：コースがバックで打球がフォア）が発生したら、そのラリーの以後の打球は確認しない。
    
    Args:
        df (pd.DataFrame): 試合の得失点データ
        
    Returns:
        str: 分析結果のMarkdown文字列
    """
    # 列名マップ: コード内で使用するキーと、実際のデータフレームの列名（全角数字）のマッピング
    COLUMN_MAP = {
        '誰のサーブか': '誰のサーブか', 
        '得点者': '得点者', # この列はもう集計には使われないが、データの存在チェックのために残す
        'サーブのコース': 'サーブのコース', 
        'レシーブの種類': 'レシーブの種類', 
        'レシーブのコース': 'レシーブのコース', 
        'レシーブの質': 'レシーブの質',
        '３球目の種類': '３球目の種類',  # 全角に修正
        '３球目のコース': '３球目のコース',  # 全角に修正
        '３球目の質': '３球目の質',      # 全角に修正
        '４球目の種類': '４球目の種類',  # 全角に修正
        '４球目のコース': '４球目のコース',  # 全角に修正
        '４球目の質': '４球目の質',      # 全角に修正
        '５球目の種類': '５球目の種類',  # 全角に修正
        '５球目のコース': '５球目のコース',  # 全角に修正
        '５球目の質': '５球目の質',      # 全角に修正
        '６球目の種類': '６球目の種類',  # 全角に修正
        '６球目のコース': '６球目のコース',  # 全角に修正
        '６球目の質': '６球目の質'       # 全角に修正
    }
    
    # 必須列のチェック
    actual_required_cols = list(COLUMN_MAP.values())
    if df.empty or not all(col in df.columns for col in actual_required_cols):
        missing_cols = [col for col in actual_required_cols if col not in df.columns]
        return f"直前の打球分析に必要なデータ列が見つかりません: {', '.join(missing_cols)}"

    df = df.fillna('')
    analysis_data = []

    for index, row in df.iterrows():
        current_ball_events = []
        skip_further_checks = False # 新しいフラグ

        # 自分のサーブ時のプレー
        if row[COLUMN_MAP['誰のサーブか']] == '自分':
            # 自分が３球目を打った場合
            if row[COLUMN_MAP['３球目の種類']] != '' and not skip_further_checks:
                opponent_course = 'バック' if 'バック' in row[COLUMN_MAP['レシーブのコース']] else ('フォア' if 'フォア' in row[COLUMN_MAP['レシーブのコース']] else None)
                my_stroke_type = 'バックハンド系' if 'バック' in row[COLUMN_MAP['３球目の種類']] else ('フォアハンド系' if 'フォア' in row[COLUMN_MAP['３球目の種類']] else None)
                is_success = 1 if 'ミス' not in row[COLUMN_MAP['３球目の質']] else 0
                
                if opponent_course and my_stroke_type and is_success is not None:
                    current_ball_events.append({
                        '相手の直前コース': opponent_course, '自分の打球技術': my_stroke_type,
                        '成功': is_success, '総数': 1
                    })
                    # コースと逆の打球が発生した場合、フラグを立てる
                    if (opponent_course == 'バック' and my_stroke_type == 'フォアハンド系') or \
                       (opponent_course == 'フォア' and my_stroke_type == 'バックハンド系'):
                        skip_further_checks = True
            
            # 自分が５球目を打った場合 (独立したif文)
            if row[COLUMN_MAP['５球目の種類']] != '' and not skip_further_checks:
                opponent_course = 'バック' if 'バック' in row[COLUMN_MAP['４球目のコース']] else ('フォア' if 'フォア' in row[COLUMN_MAP['４球目のコース']] else None)
                my_stroke_type = 'バックハンド系' if 'バック' in row[COLUMN_MAP['５球目の種類']] else ('フォアハンド系' if 'フォア' in row[COLUMN_MAP['５球目の種類']] else None)
                is_success = 1 if 'ミス' not in row[COLUMN_MAP['５球目の質']] else 0
                if opponent_course and my_stroke_type and is_success is not None:
                    current_ball_events.append({
                        '相手の直前コース': opponent_course, '自分の打球技術': my_stroke_type,
                        '成功': is_success, '総数': 1
                    })
                    if (opponent_course == 'バック' and my_stroke_type == 'フォアハンド系') or \
                       (opponent_course == 'フォア' and my_stroke_type == 'バックハンド系'):
                        skip_further_checks = True

        # 相手のサーブ時のプレー
        elif row[COLUMN_MAP['誰のサーブか']] == '相手':
            # 自分がレシーブ（2球目）を打った場合
            if row[COLUMN_MAP['レシーブの種類']] != '' and not skip_further_checks:
                opponent_course = 'バック' if 'バック' in row[COLUMN_MAP['サーブのコース']] else ('フォア' if 'フォア' in row[COLUMN_MAP['サーブのコース']] else None)
                my_stroke_type = 'バックハンド系' if 'バック' in row[COLUMN_MAP['レシーブの種類']] else ('フォアハンド系' if 'フォア' in row[COLUMN_MAP['レシーブの種類']] else None)
                is_success = 1 if 'ミス' not in row[COLUMN_MAP['レシーブの質']] else 0
                if opponent_course and my_stroke_type and is_success is not None:
                    current_ball_events.append({
                        '相手の直前コース': opponent_course, '自分の打球技術': my_stroke_type,
                        '成功': is_success, '総数': 1
                    })
                    if (opponent_course == 'バック' and my_stroke_type == 'フォアハンド系') or \
                       (opponent_course == 'フォア' and my_stroke_type == 'バックハンド系'):
                        skip_further_checks = True

            # 自分が４球目を打った場合 (独立したif文)
            if row[COLUMN_MAP['４球目の種類']] != '' and not skip_further_checks:
                opponent_course = 'バック' if 'バック' in row[COLUMN_MAP['３球目のコース']] else ('フォア' if 'フォア' in row[COLUMN_MAP['３球目のコース']] else None)
                my_stroke_type = 'バックハンド系' if 'バック' in row[COLUMN_MAP['４球目の種類']] else ('フォアハンド系' if 'フォア' in row[COLUMN_MAP['４球目の種類']] else None)
                is_success = 1 if 'ミス' not in row[COLUMN_MAP['４球目の質']] else 0
                if opponent_course and my_stroke_type and is_success is not None:
                    current_ball_events.append({
                        '相手の直前コース': opponent_course, '自分の打球技術': my_stroke_type,
                        '成功': is_success, '総数': 1
                    })
                    if (opponent_course == 'バック' and my_stroke_type == 'フォアハンド系') or \
                       (opponent_course == 'フォア' and my_stroke_type == 'バックハンド系'):
                        skip_further_checks = True

            # 自分が６球目を打った場合 (独立したif文)
            if row[COLUMN_MAP['６球目の種類']] != '' and not skip_further_checks:
                opponent_course = 'バック' if 'バック' in row[COLUMN_MAP['５球目のコース']] else ('フォア' if 'フォア' in row[COLUMN_MAP['５球目のコース']] else None)
                my_stroke_type = 'バックハンド系' if 'バック' in row[COLUMN_MAP['６球目の種類']] else ('フォアハンド系' if 'フォア' in row[COLUMN_MAP['６球目の種類']] else None)
                is_success = 1 if 'ミス' not in row[COLUMN_MAP['６球目の質']] else 0
                if opponent_course and my_stroke_type and is_success is not None:
                    current_ball_events.append({
                        '相手の直前コース': opponent_course, '自分の打球技術': my_stroke_type,
                        '成功': is_success, '総数': 1
                    })
                    if (opponent_course == 'バック' and my_stroke_type == 'フォアハンド系') or \
                       (opponent_course == 'フォア' and my_stroke_type == 'バックハンド系'):
                        skip_further_checks = True
        
        # そのラリー（行）で検出された全ての打球イベントを追加
        analysis_data.extend(current_ball_events)


    if not analysis_data:
        return "直前の打球分析に必要なデータが不足しているか、条件に合致するプレーがありませんでした。"

    # 集計と整形
    analysis_df = pd.DataFrame(analysis_data)
    summary_df = analysis_df.groupby([
        '相手の直前コース', 
        '自分の打球技術'
    ]).agg(
        総数=('総数', 'sum'),
        成功数=('成功', 'sum')
    ).reset_index()

    summary_df['成功率 (%)'] = (summary_df['成功数'] / summary_df['総数']) * 100
    summary_df['成功率 (%)'] = summary_df['成功率 (%)'].round(1)
    
    summary_df = summary_df[['相手の直前コース', '自分の打球技術', '総数', '成功数', '成功率 (%)']]

    analysis_text = "## 相手の直前コースと自分の打球技術の成功率\n\n" # タイトルも修正
    analysis_text += summary_df.to_markdown(index=False)
    
    return analysis_text
