import streamlit as st
import pandas as pd

def display_consecutive_ball_analysis(df):
    """
    バックハンド系打球で相手の1つ前のコースがバック、
    またはフォアハンド系打球で相手の1つ前のコースがフォアだった場合に、
    次の自分の打球が同じ組み合わせで登場した時の成功率をStreamlitのUIに表示する。
    """
    st.subheader("特定の連続打球成功率")
    st.caption("（同じコース・同じ打球技術の組み合わせが連続した際の成功率）")

    COLUMN_MAP = {
        '誰のサーブか': '誰のサーブか',
        'サーブのコース': 'サーブのコース',
        'レシーブの種類': 'レシーブの種類', 'レシーブのコース': 'レシーブのコース', 'レシーブの質': 'レシーブの質',
        '3球目の種類': '３球目の種類', '3球目のコース': '３球目のコース', '3球目の質': '３球目の質',
        '4球目の種類': '４球目の種類', '4球目のコース': '４球目のコース', '4球目の質': '４球目の質',
        '5球目の種類': '５球目の種類', '5球目のコース': '５球目のコース', '5球目の質': '５球目の質',
        '6球目の種類': '６球目の種類', '6球目のコース': '６球目のコース', '6球目の質': '６球目の質'
    }

    actual_required_cols = list(COLUMN_MAP.values())
    if df.empty or not all(col in df.columns for col in actual_required_cols):
        missing_cols = [col for col in actual_required_cols if col not in df.columns]
        st.warning(f"連続打球分析に必要なデータ列が見つかりません: {', '.join(missing_cols)}")
        return

    df = df.fillna('')
    consecutive_analysis_data = []

    for index, row in df.iterrows():
        # ラリー内の打球イベントを時系列順に格納
        # [(自分の打球の種類, 相手の直前コース, 自分の打球の質)]
        rally_sequence = []

        # 自分のサーブ時
        if row[COLUMN_MAP['誰のサーブか']] == '自分':
            # 2球目 (相手レシーブ) -> 3球目 (自分)
            if row[COLUMN_MAP['レシーブのコース']] != '' and row[COLUMN_MAP['3球目の種類']] != '':
                opponent_course = 'バック' if 'バック' in row[COLUMN_MAP['レシーブのコース']] else ('フォア' if 'フォア' in row[COLUMN_MAP['レシーブのコース']] else None)
                my_stroke_type = 'バックハンド系' if 'バック' in row[COLUMN_MAP['3球目の種類']] else ('フォアハンド系' if 'フォア' in row[COLUMN_MAP['3球目の種類']] else None)
                my_stroke_quality = row[COLUMN_MAP['3球目の質']]
                if opponent_course and my_stroke_type:
                    rally_sequence.append((my_stroke_type, opponent_course, my_stroke_quality))
            
            # 4球目 (相手) -> 5球目 (自分)
            if row[COLUMN_MAP['4球目のコース']] != '' and row[COLUMN_MAP['5球目の種類']] != '':
                opponent_course = 'バック' if 'バック' in row[COLUMN_MAP['4球目のコース']] else ('フォア' if 'フォア' in row[COLUMN_MAP['4球目のコース']] else None)
                my_stroke_type = 'バックハンド系' if 'バック' in row[COLUMN_MAP['5球目の種類']] else ('フォアハンド系' if 'フォア' in row[COLUMN_MAP['5球目の種類']] else None)
                my_stroke_quality = row[COLUMN_MAP['5球目の質']]
                if opponent_course and my_stroke_type:
                    rally_sequence.append((my_stroke_type, opponent_course, my_stroke_quality))

        # 相手のサーブ時
        elif row[COLUMN_MAP['誰のサーブか']] == '相手':
            # 1球目 (相手サーブ) -> 2球目 (自分レシーブ)
            if row[COLUMN_MAP['サーブのコース']] != '' and row[COLUMN_MAP['レシーブの種類']] != '':
                opponent_course = 'バック' if 'バック' in row[COLUMN_MAP['サーブのコース']] else ('フォア' if 'フォア' in row[COLUMN_MAP['サーブのコース']] else None)
                my_stroke_type = 'バックハンド系' if 'バック' in row[COLUMN_MAP['レシーブの種類']] else ('フォアハンド系' if 'フォア' in row[COLUMN_MAP['レシーブの種類']] else None)
                my_stroke_quality = row[COLUMN_MAP['レシーブの質']]
                if opponent_course and my_stroke_type:
                    rally_sequence.append((my_stroke_type, opponent_course, my_stroke_quality))

            # 3球目 (相手) -> 4球目 (自分)
            if row[COLUMN_MAP['3球目のコース']] != '' and row[COLUMN_MAP['4球目の種類']] != '':
                opponent_course = 'バック' if 'バック' in row[COLUMN_MAP['3球目のコース']] else ('フォア' if 'フォア' in row[COLUMN_MAP['3球目のコース']] else None)
                my_stroke_type = 'バックハンド系' if 'バック' in row[COLUMN_MAP['4球目の種類']] else ('フォアハンド系' if 'フォア' in row[COLUMN_MAP['4球目の種類']] else None)
                my_stroke_quality = row[COLUMN_MAP['4球目の質']]
                if opponent_course and my_stroke_type:
                    rally_sequence.append((my_stroke_type, opponent_course, my_stroke_quality))

            # 5球目 (相手) -> 6球目 (自分)
            if row[COLUMN_MAP['5球目のコース']] != '' and row[COLUMN_MAP['6球目の種類']] != '':
                opponent_course = 'バック' if 'バック' in row[COLUMN_MAP['5球目のコース']] else ('フォア' if 'フォア' in row[COLUMN_MAP['5球目のコース']] else None)
                my_stroke_type = 'バックハンド系' if 'バック' in row[COLUMN_MAP['6球目の種類']] else ('フォアハンド系' if 'フォア' in row[COLUMN_MAP['6球目の種類']] else None)
                my_stroke_quality = row[COLUMN_MAP['6球目の質']]
                if opponent_course and my_stroke_type:
                    rally_sequence.append((my_stroke_type, opponent_course, my_stroke_quality))
        
        # ラリーシーケンスをチェックし、連続する同じ組み合わせを抽出
        for i in range(len(rally_sequence) - 1):
            current_event = rally_sequence[i] # (自分の打球の種類, 相手の直前コース, 自分の打球の質)
            next_event = rally_sequence[i+1]

            # 今回の自分の打球の種類が「バックハンド系」で、その前の相手のコースが「バック」
            # かつ、次の自分の打球の種類が「バックハンド系」で、その前の相手のコースが「バック」
            if (current_event[0] == 'バックハンド系' and current_event[1] == 'バック') and \
               (next_event[0] == 'バックハンド系' and next_event[1] == 'バック'):
                is_success = 1 if 'ミス' not in next_event[2] else 0
                consecutive_analysis_data.append({
                    '連続パターン': '相手コースバック → 自分バックハンド系',
                    '成功': is_success,
                    '総数': 1
                })
            
            # 今回の自分の打球の種類が「フォアハンド系」で、その前の相手のコースが「フォア」
            # かつ、次の自分の打球の種類が「フォアハンド系」で、その前の相手のコースが「フォア」
            elif (current_event[0] == 'フォアハンド系' and current_event[1] == 'フォア') and \
                 (next_event[0] == 'フォアハンド系' and next_event[1] == 'フォア'):
                is_success = 1 if 'ミス' not in next_event[2] else 0
                consecutive_analysis_data.append({
                    '連続パターン': '相手コースフォア → 自分フォアハンド系',
                    '成功': is_success,
                    '総数': 1
                })

    if not consecutive_analysis_data:
        st.info("特定の連続打球分析に必要なデータが不足しているか、条件に合致するプレーがありませんでした。")
        return

    # 集計と整形
    analysis_df = pd.DataFrame(consecutive_analysis_data)
    summary_df = analysis_df.groupby('連続パターン').agg(
        総数=('総数', 'sum'),
        成功数=('成功', 'sum')
    ).reset_index()

    summary_df['成功率 (%)'] = (summary_df['成功数'] / summary_df['総数']) * 100
    summary_df['成功率 (%)'] = summary_df['成功率 (%)'].round(1)
    
    summary_df = summary_df[['連続パターン', '総数', '成功率 (%)']]

    # UI表示
    st.markdown("---")
    st.dataframe(summary_df.style.format({'成功率 (%)': "{:.1f}%"}))

def get_consecutive_ball_analysis_for_ai(df):
    """
    バックハンド系打球で相手の1つ前のコースがバック、
    またはフォアハンド系打球で相手の1つ前のコースがフォアだった場合に、
    次の自分の打球が同じ組み合わせで登場した時の成功率をAIに渡すためのMarkdown文字列を生成する。
    """
    COLUMN_MAP = {
        '誰のサーブか': '誰のサーブか',
        'サーブのコース': 'サーブのコース',
        'レシーブの種類': 'レシーブの種類', 'レシーブのコース': 'レシーブのコース', 'レシーブの質': 'レシーブの質',
        '3球目の種類': '３球目の種類', '3球目のコース': '３球目のコース', '3球目の質': '３球目の質',
        '4球目の種類': '４球目の種類', '4球目のコース': '４球目のコース', '4球目の質': '４球目の質',
        '5球目の種類': '５球目の種類', '5球目のコース': '５球目のコース', '5球目の質': '５球目の質',
        '6球目の種類': '６球目の種類', '6球目のコース': '６球目のコース', '6球目の質': '６球目の質'
    }

    actual_required_cols = list(COLUMN_MAP.values())
    if df.empty or not all(col in df.columns for col in actual_required_cols):
        missing_cols = [col for col in actual_required_cols if col not in df.columns]
        return f"連続打球分析に必要なデータ列が見つかりません: {', '.join(missing_cols)}"

    df = df.fillna('')
    consecutive_analysis_data = []

    for index, row in df.iterrows():
        # ラリー内の打球イベントを時系列順に格納
        # [(自分の打球の種類, 相手の直前コース, 自分の打球の質)]
        rally_sequence = []

        # 自分のサーブ時
        if row[COLUMN_MAP['誰のサーブか']] == '自分':
            # 2球目 (相手レシーブ) -> 3球目 (自分)
            if row[COLUMN_MAP['レシーブのコース']] != '' and row[COLUMN_MAP['3球目の種類']] != '':
                opponent_course = 'バック' if 'バック' in row[COLUMN_MAP['レシーブのコース']] else ('フォア' if 'フォア' in row[COLUMN_MAP['レシーブのコース']] else None)
                my_stroke_type = 'バックハンド系' if 'バック' in row[COLUMN_MAP['3球目の種類']] else ('フォアハンド系' if 'フォア' in row[COLUMN_MAP['3球目の種類']] else None)
                my_stroke_quality = row[COLUMN_MAP['3球目の質']]
                if opponent_course and my_stroke_type:
                    rally_sequence.append((my_stroke_type, opponent_course, my_stroke_quality))
            
            # 4球目 (相手) -> 5球目 (自分)
            if row[COLUMN_MAP['4球目のコース']] != '' and row[COLUMN_MAP['5球目の種類']] != '':
                opponent_course = 'バック' if 'バック' in row[COLUMN_MAP['4球目のコース']] else ('フォア' if 'フォア' in row[COLUMN_MAP['4球目のコース']] else None)
                my_stroke_type = 'バックハンド系' if 'バック' in row[COLUMN_MAP['5球目の種類']] else ('フォアハンド系' if 'フォア' in row[COLUMN_MAP['5球目の種類']] else None)
                my_stroke_quality = row[COLUMN_MAP['5球目の質']]
                if opponent_course and my_stroke_type:
                    rally_sequence.append((my_stroke_type, opponent_course, my_stroke_quality))

        # 相手のサーブ時
        elif row[COLUMN_MAP['誰のサーブか']] == '相手':
            # 1球目 (相手サーブ) -> 2球目 (自分レシーブ)
            if row[COLUMN_MAP['サーブのコース']] != '' and row[COLUMN_MAP['レシーブの種類']] != '':
                opponent_course = 'バック' if 'バック' in row[COLUMN_MAP['サーブのコース']] else ('フォア' if 'フォア' in row[COLUMN_MAP['サーブのコース']] else None)
                my_stroke_type = 'バックハンド系' if 'バック' in row[COLUMN_MAP['レシーブの種類']] else ('フォアハンド系' if 'フォア' in row[COLUMN_MAP['レシーブの種類']] else None)
                my_stroke_quality = row[COLUMN_MAP['レシーブの質']]
                if opponent_course and my_stroke_type:
                    rally_sequence.append((my_stroke_type, opponent_course, my_stroke_quality))

            # 3球目 (相手) -> 4球目 (自分)
            if row[COLUMN_MAP['3球目のコース']] != '' and row[COLUMN_MAP['4球目の種類']] != '':
                opponent_course = 'バック' if 'バック' in row[COLUMN_MAP['3球目のコース']] else ('フォア' if 'フォア' in row[COLUMN_MAP['3球目のコース']] else None)
                my_stroke_type = 'バックハンド系' if 'バック' in row[COLUMN_MAP['4球目の種類']] else ('フォアハンド系' if 'フォア' in row[COLUMN_MAP['4球目の種類']] else None)
                my_stroke_quality = row[COLUMN_MAP['4球目の質']]
                if opponent_course and my_stroke_type:
                    rally_sequence.append((my_stroke_type, opponent_course, my_stroke_quality))

            # 5球目 (相手) -> 6球目 (自分)
            if row[COLUMN_MAP['5球目のコース']] != '' and row[COLUMN_MAP['6球目の種類']] != '':
                opponent_course = 'バック' if 'バック' in row[COLUMN_MAP['5球目のコース']] else ('フォア' if 'フォア' in row[COLUMN_MAP['5球目のコース']] else None)
                my_stroke_type = 'バックハンド系' if 'バック' in row[COLUMN_MAP['6球目の種類']] else ('フォアハンド系' if 'フォア' in row[COLUMN_MAP['6球目の種類']] else None)
                my_stroke_quality = row[COLUMN_MAP['6球目の質']]
                if opponent_course and my_stroke_type:
                    rally_sequence.append((my_stroke_type, opponent_course, my_stroke_quality))
        
        # ラリーシーケンスをチェックし、連続する同じ組み合わせを抽出
        for i in range(len(rally_sequence) - 1):
            current_event = rally_sequence[i] # (自分の打球の種類, 相手の直前コース, 自分の打球の質)
            next_event = rally_sequence[i+1]

            # 今回の自分の打球の種類が「バックハンド系」で、その前の相手のコースが「バック」
            # かつ、次の自分の打球の種類が「バックハンド系」で、その前の相手のコースが「バック」
            if (current_event[0] == 'バックハンド系' and current_event[1] == 'バック') and \
               (next_event[0] == 'バックハンド系' and next_event[1] == 'バック'):
                is_success = 1 if 'ミス' not in next_event[2] else 0
                consecutive_analysis_data.append({
                    '連続パターン': '相手コースバック → 自分バックハンド系',
                    '成功': is_success,
                    '総数': 1
                })
            
            # 今回の自分の打球の種類が「フォアハンド系」で、その前の相手のコースが「フォア」
            # かつ、次の自分の打球の種類が「フォアハンド系」で、その前の相手のコースが「フォア」
            elif (current_event[0] == 'フォアハンド系' and current_event[1] == 'フォア') and \
                 (next_event[0] == 'フォアハンド系' and next_event[1] == 'フォア'):
                is_success = 1 if 'ミス' not in next_event[2] else 0
                consecutive_analysis_data.append({
                    '連続パターン': '相手コースフォア → 自分フォアハンド系',
                    '成功': is_success,
                    '総数': 1
                })

    if not consecutive_analysis_data:
        return "特定の連続打球分析に必要なデータが不足しているか、条件に合致するプレーがありませんでした。"

    # 集計と整形
    analysis_df = pd.DataFrame(consecutive_analysis_data)
    summary_df = analysis_df.groupby('連続パターン').agg(
        総数=('総数', 'sum'),
        成功数=('成功', 'sum')
    ).reset_index()

    summary_df['成功率 (%)'] = (summary_df['成功数'] / summary_df['総数']) * 100
    summary_df['成功率 (%)'] = summary_df['成功率 (%)'].round(1)
    
    summary_df = summary_df[['連続パターン', '総数', '成功数', '成功率 (%)']]

    analysis_text = "## 特定の連続打球成功率\n\n"
    analysis_text += "（同じコース・同じ打球技術の組み合わせが連続した際の成功率）\n\n"
    analysis_text += summary_df.to_markdown(index=False)
    
    return analysis_text
