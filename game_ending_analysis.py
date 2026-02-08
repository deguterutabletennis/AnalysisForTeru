import streamlit as st
import pandas as pd
from utils import(time_to_seconds, create_youtube_link, group_serve_type, group_serve_course)

def display_game_ending_analysis(df):
    """
    ゲーム終盤 (指定された条件: 両者8点以上) での得点率、および得点に繋がった
    サーブの種類（グルーピング済み）とコース（グルーピング済み）の組み合わせを分析し、
    StreamlitのUIに表示する。終盤前の同じサーブとコースの組み合わせでの得点率も表示する。
    「終盤前」は、そのラリーが行われるまでの全てのゲーム（現在のゲーム含む）の終盤前のラリーを対象とする。
    また、各プレーが行われた「場面」（ゲーム数とスコア）も表示する。

    追加機能：8-8以降のゲーム展開を一覧で出力する。
    """
    st.subheader("ゲームのフェーズ別得点分析") 

    COLUMN_MAP = {
        'ゲーム数': 'ゲーム数',
        '誰のサーブか': '誰のサーブか',
        '得点者': '得点者',
        '自分の得点': '自分の得点', 
        '相手の得点': '相手の得点', 
        'サーブの種類': 'サーブの種類',
        'サーブのコース': 'サーブのコース', 
        'レシーブの種類': 'レシーブの種類',
        'レシーブのコース': 'レシーブのコース',
        '得点の内容': '得点の内容', 
        '失点の内容': '失点の内容'  
    }

    actual_required_cols = list(COLUMN_MAP.values())
    if df.empty or not all(col in df.columns for col in actual_required_cols):
        missing_cols = [col for col in actual_required_cols if col not in df.columns]
        st.warning(f"ゲーム終盤分析に必要なデータ列が見つかりません: {', '.join(missing_cols)}")
        return

    df = df.fillna('')
    
    game_ending_points_data = []
    non_game_ending_points_data = [] 
    game_ending_serve_data = [] 
    game_ending_rallies_detail = [] # 8-8以降のゲーム展開詳細

    # 終盤前のサーブ統計を追跡するための辞書
    # キー: 'グルーピングされたサーブの種類 (グルーピングされたサーブのコース)', 値: {'total': 総回数, 'points': 得点回数}
    serve_stats_before_game_ending = {} # この辞書は、ラリーが進むにつれて累積的に更新される

    # データフレームのインデックスを一時的に列に変換し、ソートキーとして使用
    df_temp = df.reset_index()
    df_sorted = df_temp.sort_values(by=[COLUMN_MAP['ゲーム数'], 'index']).reset_index(drop=True)
    
    for idx, row in df_sorted.iterrows():
        game_num = row[COLUMN_MAP['ゲーム数']]
        current_my_score = row[COLUMN_MAP['自分の得点']]
        current_opponent_score = row[COLUMN_MAP['相手の得点']]
        scorer = row[COLUMN_MAP['得点者']]

        # ラリー開始時点のスコアを決定
        rally_start_my_score = current_my_score - 1 if scorer == '自分' else current_my_score
        rally_start_opponent_score = current_opponent_score - 1 if scorer == '相手' else current_opponent_score

        # ただし、スコアが0未満になることはないため補正
        rally_start_my_score = max(0, rally_start_my_score)
        rally_start_opponent_score = max(0, rally_start_opponent_score)
            
        # 場面文字列の生成（ラリー開始時点のスコア）
        situation_string = f"{int(game_num)}ゲーム目 {int(rally_start_my_score)}-{int(rally_start_opponent_score)}"

        # ゲーム終盤の条件チェック: 両者8点以上
        is_game_ending = False
        if rally_start_my_score >= 8 and rally_start_opponent_score >= 8:
            is_game_ending = True

        is_my_point = 1 if scorer == '自分' else 0

        # サーブの種類とコースをグループ化 (誰のサーブかに関わらず)
        serve_type_raw = row[COLUMN_MAP['サーブの種類']]
        grouped_serve_type = group_serve_type(serve_type_raw) 
        
        serve_course_raw = row[COLUMN_MAP['サーブのコース']]
        grouped_serve_course = group_serve_course(serve_course_raw)

        # レシーブの種類とコースを結合
        receive_type_raw = row[COLUMN_MAP['レシーブの種類']]
        receive_course_raw = row[COLUMN_MAP['レシーブのコース']]
        combined_receive = f"{receive_type_raw} ({receive_course_raw})" if receive_type_raw or receive_course_raw else ''

        # 得失点の内容を結合
        point_content = ''
        if scorer == '自分':
            point_content = row[COLUMN_MAP['得点の内容']]
        elif scorer == '相手':
            point_content = row[COLUMN_MAP['失点の内容']]
        
        # 自分のサーブだった場合（個々のサーブプレー分析用）
        if row[COLUMN_MAP['誰のサーブか']] == '自分':
            # 具体的なプレー名 (グルーピングされた種類とコースを結合)
            specific_play = f"{grouped_serve_type} ({grouped_serve_course})" if grouped_serve_type or grouped_serve_course else '不明なサーブ/コース'
            
            # この時点での「終盤前」の統計情報（`serve_stats_before_game_ending`）を取得
            before_game_ending_total = serve_stats_before_game_ending.get(specific_play, {}).get('total', 0)
            before_game_ending_points = serve_stats_before_game_ending.get(specific_play, {}).get('points', 0)

            # このラリーが終盤のラリーであれば、`game_ending_serve_data` に追加
            if is_game_ending:
                game_ending_serve_data.append({
                    'プレーヤー': '自分',
                    '具体的なプレー': specific_play, 
                    '結果': '得点' if is_my_point else '失点', 
                    '総回数 (終盤前まで)': before_game_ending_total, 
                    '得点に繋がった回数 (終盤前まで)': before_game_ending_points, 
                    '場面': situation_string 
                })
            
            # その後、このラリーが終盤であろうとなかろうと、
            # 次のラリーのために `serve_stats_before_game_ending` を更新
            # （このラリーのデータが次のラリーの「終盤前」の統計に含まれるように）
            if specific_play not in serve_stats_before_game_ending:
                serve_stats_before_game_ending[specific_play] = {'total': 0, 'points': 0}
            serve_stats_before_game_ending[specific_play]['total'] += 1
            if is_my_point:
                serve_stats_before_game_ending[specific_play]['points'] += 1

        # 各フェーズの得点率計算用のデータ収集
        if is_game_ending:
            game_ending_points_data.append({
                'ゲーム数': game_num,
                'ラリーの開始時点スコア': f"{rally_start_my_score}-{rally_start_opponent_score}",
                '得点後スコア': f"{current_my_score}-{current_opponent_score}",
                '自分の得点': is_my_point,
                '総ラリー数 (終盤)': 1,
                '場面': situation_string 
            })
            # 8-8以降のゲーム展開詳細を追加
            game_ending_rallies_detail.append({
                '場面': situation_string,
                '誰のサーブか': row[COLUMN_MAP['誰のサーブか']],
                '得点者': scorer, 
                'サーブ（種類-コース）': f"{grouped_serve_type} ({grouped_serve_course})" if grouped_serve_type or grouped_serve_course else '', 
                'レシーブ（種類-コース）': combined_receive, 
                '得失点の内容': point_content # 新しく結合した列
            })
        else: 
            non_game_ending_points_data.append({
                'ゲーム数': game_num,
                'ラリーの開始時点スコア': f"{rally_start_my_score}-{rally_start_opponent_score}",
                '得点後スコア': f"{current_my_score}-{current_opponent_score}",
                '自分の得点': is_my_point,
                '総ラリー数 (非終盤)': 1,
                '場面': situation_string 
            })


    st.markdown("---")
    
    # 各フェーズの得点率をまとめるためのデータ準備
    summary_rates = []

    # 試合全体の得点率
    total_rallies_in_match = df_sorted.shape[0]
    total_my_points_in_match = df_sorted[df_sorted[COLUMN_MAP['得点者']] == '自分'].shape[0]

    if total_rallies_in_match > 0:
        overall_point_rate = (total_my_points_in_match / total_rallies_in_match) * 100
        summary_rates.append({
            'フェーズ': '試合全体',
            '自分の得点数': total_my_points_in_match,
            '総ラリー数': total_rallies_in_match,
            '得点率 (%)': round(overall_point_rate, 1)
        })
    else:
        summary_rates.append({
            'フェーズ': '試合全体',
            '自分の得点数': 0,
            '総ラリー数': 0,
            '得点率 (%)': 0.0
        })

    # ゲーム終盤を除くラリーの得点率 (序盤・中盤)
    if non_game_ending_points_data:
        non_game_ending_points_df = pd.DataFrame(non_game_ending_points_data)
        total_non_game_ending_rallies = non_game_ending_points_df['総ラリー数 (非終盤)'].sum()
        my_non_game_ending_points = non_game_ending_points_df['自分の得点'].sum()

        if total_non_game_ending_rallies > 0:
            non_game_ending_point_rate = (my_non_game_ending_points / total_non_game_ending_rallies) * 100
            summary_rates.append({
                'フェーズ': 'ゲーム序盤・中盤',
                '自分の得点数': my_non_game_ending_points,
                '総ラリー数': total_non_game_ending_rallies,
                '得点率 (%)': round(non_game_ending_point_rate, 1)
            })
        else:
            summary_rates.append({
                'フェーズ': 'ゲーム序盤・中盤',
                '自分の得点数': 0,
                '総ラリー数': 0,
                '得点率 (%)': 0.0
            })
    else:
        summary_rates.append({
            'フェーズ': 'ゲーム序盤・中盤',
            '自分の得点数': 0,
            '総ラリー数': 0,
            '得点率 (%)': 0.0
        })

    # ゲーム終盤の得点率
    if game_ending_points_data:
        game_ending_points_df = pd.DataFrame(game_ending_points_data)
        total_game_ending_rallies = game_ending_points_df['総ラリー数 (終盤)'].sum()
        my_game_ending_points = game_ending_points_df['自分の得点'].sum()
        
        if total_game_ending_rallies > 0:
            game_ending_point_rate = (my_game_ending_points / total_game_ending_rallies) * 100
            summary_rates.append({
                'フェーズ': 'ゲーム終盤',
                '自分の得点数': my_game_ending_points,
                '総ラリー数': total_game_ending_rallies,
                '得点率 (%)': round(game_ending_point_rate, 1)
            })
        else:
            summary_rates.append({
                'フェーズ': 'ゲーム終盤',
                '自分の得点数': 0,
                '総ラリー数': 0,
            '得点率 (%)': 0.0
        })
    else:
        summary_rates.append({
            'フェーズ': 'ゲーム終盤',
            '自分の得点数': 0,
            '総ラリー数': 0,
            '得点率 (%)': 0.0
        })

    summary_rates_df = pd.DataFrame(summary_rates)
    st.dataframe(summary_rates_df.style.format({'得点率 (%)': "{:.1f}%"}))

    st.markdown("---")
    st.subheader("ゲーム終盤での個々のサーブプレー分析") # 見出し変更
    if game_ending_serve_data:
        # game_ending_serve_data はすでに個々のプレーを含んでいるので、groupbyは不要
        summary_serve_df = pd.DataFrame(game_ending_serve_data)
        
        # 終盤前までの得点率を計算 (ゼロ除算対策)
        summary_serve_df['得点率 (%) (終盤前まで)'] = summary_serve_df.apply(
            lambda row: round((row['得点に繋がった回数 (終盤前まで)'] / row['総回数 (終盤前まで)']) * 100, 1) 
            if row['総回数 (終盤前まで)'] > 0 else 0.0, axis=1
        )
        
        # 表示する列の順序と名称を調整
        summary_serve_df = summary_serve_df[[
            '場面', 
            '具体的なプレー', 
            '結果', # 新しい「結果」列
            '総回数 (終盤前まで)', 
            '得点に繋がった回数 (終盤前まで)', 
            '得点率 (%) (終盤前まで)'
        ]].sort_values(by=['場面'], ascending=[True]) # 場面でソート

        st.dataframe(summary_serve_df.style.format({
            '得点率 (%) (終盤前まで)': "{:.1f}%"
        }))
    else:
        st.info("ゲーム終盤でのサーブのデータがありません。")

    st.markdown("---")
    st.subheader("8-8以降のゲーム展開詳細")
    if game_ending_rallies_detail:
        df_game_ending_rallies_detail = pd.DataFrame(game_ending_rallies_detail)
        # 不要になった '得点の内容' と '失点の内容' を削除してから表示
        df_game_ending_rallies_detail = df_game_ending_rallies_detail.drop(columns=['得点の内容', '失点の内容'], errors='ignore')
        st.dataframe(df_game_ending_rallies_detail)
    else:
        st.info("8-8以降のゲーム展開データがありません。")

def get_game_ending_analysis_for_ai(df):
    """
    ゲーム終盤 (指定された条件: 両者8点以上) での得点率、および得点に繋がった
    サーブの種類（グルーピング済み）とコース（グルーピング済み）の組み合わせを分析し、
    AIに渡すためのMarkdown文字列を生成する。終盤前の同じサーブとコースの組み合わせでの得点率も表示する。
    「終盤前」は、そのラリーが行われるまでの全てのゲーム（現在のゲーム含む）の終盤前のラリーを対象とする。
    また、各プレーが行われた「場面」（ゲーム数とスコア）も表示する。
    
    追加機能：8-8以降のゲーム展開を一覧で出力する。
    """
    COLUMN_MAP = {
        'ゲーム数': 'ゲーム数',
        '誰のサーブか': '誰のサーブか',
        '得点者': '得点者',
        '自分の得点': '自分の得点', 
        '相手の得点': '相手の得点', 
        'サーブの種類': 'サーブの種類',
        'サーブのコース': 'サーブのコース', 
        'レシーブの種類': 'レシーブの種類',
        'レシーブのコース': 'レシーブのコース',
        '得点の内容': '得点の内容', 
        '失点の内容': '失点の内容'  
    }

    actual_required_cols = list(COLUMN_MAP.values())
    if df.empty or not all(col in df.columns for col in actual_required_cols):
        missing_cols = [col for col in actual_required_cols if col not in df.columns]
        return f"ゲーム終盤分析に必要なデータ列が見つかりません: {', '.join(missing_cols)}"

    df = df.fillna('')
    
    game_ending_points_data = []
    non_game_ending_points_data = [] 
    game_ending_serve_data = [] 
    game_ending_rallies_detail = [] # 8-8以降のゲーム展開詳細

    # 終盤前のサーブ統計を追跡するための辞書
    # キー: 'グルーピングされたサーブの種類 (グルーピングされたサーブのコース)', 値: {'total': 総回数, 'points': 得点回数}
    serve_stats_before_game_ending = {} # この辞書は、ラリーが進むにつれて累積的に更新される

    # データフレームのインデックスを一時的に列に変換し、ソートキーとして使用
    df_temp = df.reset_index() 
    df_sorted = df_temp.sort_values(by=[COLUMN_MAP['ゲーム数'], 'index']).reset_index(drop=True)


    for idx, row in df_sorted.iterrows():
        game_num = row[COLUMN_MAP['ゲーム数']]
        current_my_score = row[COLUMN_MAP['自分の得点']]
        current_opponent_score = row[COLUMN_MAP['相手の得点']]
        scorer = row[COLUMN_MAP['得点者']]

        # ラリー開始時点のスコアを決定
        rally_start_my_score = current_my_score - 1 if scorer == '自分' else current_my_score
        rally_start_opponent_score = current_opponent_score - 1 if scorer == '相手' else current_opponent_score
        
        # ただし、スコアが0未満になることはないため補正
        rally_start_my_score = max(0, rally_start_my_score)
        rally_start_opponent_score = max(0, rally_start_opponent_score)

        # 場面文字列の生成（ラリー開始時点のスコア）
        situation_string = f"{int(game_num)}ゲーム目 {int(rally_start_my_score)}-{int(rally_start_opponent_score)}"

        # ゲーム終盤の条件チェック: 両者8点以上
        is_game_ending = False
        if rally_start_my_score >= 8 and rally_start_opponent_score >= 8:
            is_game_ending = True
        
        is_my_point = 1 if scorer == '自分' else 0

        # サーブの種類とコースをグループ化 (誰のサーブかに関わらず)
        serve_type_raw = row[COLUMN_MAP['サーブの種類']]
        grouped_serve_type = group_serve_type(serve_type_raw) 
        
        serve_course_raw = row[COLUMN_MAP['サーブのコース']]
        grouped_serve_course = group_serve_course(serve_course_raw)

        # レシーブの種類とコースを結合
        receive_type_raw = row[COLUMN_MAP['レシーブの種類']]
        receive_course_raw = row[COLUMN_MAP['レシーブのコース']]
        combined_receive = f"{receive_type_raw} ({receive_course_raw})" if receive_type_raw or receive_course_raw else ''
        
        # 得失点の内容を結合
        point_content = ''
        if scorer == '自分':
            point_content = row[COLUMN_MAP['得点の内容']]
        elif scorer == '相手':
            point_content = row[COLUMN_MAP['失点の内容']]

        # 自分のサーブだった場合（個々のサーブプレー分析用）
        if row[COLUMN_MAP['誰のサーブか']] == '自分':
            # 具体的なプレー名 (グルーピングされた種類とコースを結合)
            specific_play = f"{grouped_serve_type} ({grouped_serve_course})" if grouped_serve_type or grouped_serve_course else '不明なサーブ/コース'
            
            # この時点での「終盤前」の統計情報（`serve_stats_before_game_ending`）を取得
            before_game_ending_total = serve_stats_before_game_ending.get(specific_play, {}).get('total', 0)
            before_game_ending_points = serve_stats_before_game_ending.get(specific_play, {}).get('points', 0)

            # このラリーが終盤のラリーであれば、`game_ending_serve_data` に追加
            if is_game_ending:
                game_ending_serve_data.append({
                    'プレーヤー': '自分',
                    '具体的なプレー': specific_play, 
                    '結果': '得点' if is_my_point else '失点', 
                    '総回数 (終盤前まで)': before_game_ending_total, 
                    '得点に繋がった回数 (終盤前まで)': before_game_ending_points, 
                    '場面': situation_string 
                })
            
            # その後、このラリーが終盤であろうとなかろうと、
            # 次のラリーのために `serve_stats_before_game_ending` を更新
            # （このラリーのデータが次のラリーの「終盤前」の統計に含まれるように）
            if specific_play not in serve_stats_before_game_ending:
                serve_stats_before_game_ending[specific_play] = {'total': 0, 'points': 0}
            serve_stats_before_game_ending[specific_play]['total'] += 1
            if is_my_point:
                serve_stats_before_game_ending[specific_play]['points'] += 1

        # 各フェーズの得点率計算用のデータ収集
        if is_game_ending:
            game_ending_points_data.append({
                'ゲーム数': game_num,
                'ラリーの開始時点スコア': f"{rally_start_my_score}-{rally_start_opponent_score}",
                '得点後スコア': f"{current_my_score}-{current_opponent_score}",
                '自分の得点': is_my_point,
                '総ラリー数 (終盤)': 1,
                '場面': situation_string 
            })
            # 8-8以降のゲーム展開詳細を追加
            game_ending_rallies_detail.append({
                '場面': situation_string,
                '誰のサーブか': row[COLUMN_MAP['誰のサーブか']],
                '得点者': scorer, # '得点者'カラムを追加
                'サーブ（種類-コース）': f"{grouped_serve_type} ({grouped_serve_course})" if grouped_serve_type or grouped_serve_course else '', # 結合して表示
                'レシーブ（種類-コース）': combined_receive, # 結合して表示
                '得失点の内容': point_content # 新しく結合した列
            })
        else: 
            non_game_ending_points_data.append({
                'ゲーム数': game_num,
                'ラリーの開始時点スコア': f"{rally_start_my_score}-{rally_start_opponent_score}",
                '得点後スコア': f"{current_my_score}-{current_opponent_score}",
                '自分の得点': is_my_point,
                '総ラリー数 (非終盤)': 1,
                '場面': situation_string 
            })


    analysis_text = "## ゲームのフェーズ別得点分析\n\n" 

    # 1. 各フェーズの得点率をまとめるためのデータ準備
    summary_rates = []

    # 試合全体の得点率
    total_rallies_in_match = df_sorted.shape[0]
    total_my_points_in_match = df_sorted[df_sorted[COLUMN_MAP['得点者']] == '自分'].shape[0]

    if total_rallies_in_match > 0:
        overall_point_rate = (total_my_points_in_match / total_rallies_in_match) * 100
        summary_rates.append({
            'フェーズ': '試合全体',
            '自分の得点数': total_my_points_in_match,
            '総ラリー数': total_rallies_in_match,
            '得点率 (%)': round(overall_point_rate, 1)
        })
    else:
        summary_rates.append({
            'フェーズ': '試合全体',
            '自分の得点数': 0,
            '総ラリー数': 0,
            '得点率 (%)': 0.0
        })

    # ゲーム終盤を除くラリーの得点率 (序盤・中盤)
    if non_game_ending_points_data:
        non_game_ending_points_df = pd.DataFrame(non_game_ending_points_data)
        total_non_game_ending_rallies = non_game_ending_points_df['総ラリー数 (非終盤)'].sum()
        my_non_game_ending_points = non_game_ending_points_df['自分の得点'].sum()

        if total_non_game_ending_rallies > 0:
            non_game_ending_point_rate = (my_non_game_ending_points / total_non_game_ending_rallies) * 100
            summary_rates.append({
                'フェーズ': 'ゲーム序盤・中盤',
                '自分の得点数': my_non_game_ending_points,
                '総ラリー数': total_non_game_ending_rallies,
                '得点率 (%)': round(non_game_ending_point_rate, 1)
            })
        else:
            summary_rates.append({
                'フェーズ': 'ゲーム序盤・中盤',
                '自分の得点数': 0,
                '総ラリー数': 0,
                '得点率 (%)': 0.0
            })
    else:
        summary_rates.append({
            'フェーズ': 'ゲーム序盤・中盤',
            '自分の得点数': 0,
            '総ラリー数': 0,
            '得点率 (%)': 0.0
        })

    # ゲーム終盤の得点率
    if game_ending_points_data:
        game_ending_points_df = pd.DataFrame(game_ending_points_data)
        total_game_ending_rallies = game_ending_points_df['総ラリー数 (終盤)'].sum()
        my_game_ending_points = game_ending_points_df['自分の得点'].sum()
        
        if total_game_ending_rallies > 0:
            game_ending_point_rate = (my_game_ending_points / total_game_ending_rallies) * 100
            summary_rates.append({
                'フェーズ': 'ゲーム終盤',
                '自分の得点数': my_game_ending_points,
                '総ラリー数': total_game_ending_rallies,
                '得点率 (%)': round(game_ending_point_rate, 1)
            })
        else:
            summary_rates.append({
                'フェーズ': 'ゲーム終盤',
                '自分の得点数': 0,
                '総ラリー数': 0,
            '得点率 (%)': 0.0
        })
    else:
        summary_rates.append({
            'フェーズ': 'ゲーム終盤',
            '自分の得点数': 0,
            '総ラリー数': 0,
            '得点率 (%)': 0.0
        })

    summary_rates_df = pd.DataFrame(summary_rates)
    analysis_text += summary_rates_df.to_markdown(index=False)
    analysis_text += "\n\n"

    # ゲーム終盤で得点に繋がったサーブの分析 (終盤前までの得点率も表示)
    analysis_text += "### ゲーム終盤での個々のサーブプレー分析\n\n" # 見出し変更
    if game_ending_serve_data:
        # game_ending_serve_data はすでに個々のプレーを含んでいるので、groupbyは不要
        summary_serve_df = pd.DataFrame(game_ending_serve_data)
        
        # 終盤前までの得点率を計算 (ゼロ除算対策)
        summary_serve_df['得点率 (%) (終盤前まで)'] = summary_serve_df.apply(
            lambda row: round((row['得点に繋がった回数 (終盤前まで)'] / row['総回数 (終盤前まで)']) * 100, 1) 
            if row['総回数 (終盤前まで)'] > 0 else 0.0, axis=1
        )
        
        # 表示する列の順序と名称を調整
        summary_serve_df = summary_serve_df[[
            '場面', 
            '具体的なプレー', 
            '結果', # 新しい「結果」列
            '総回数 (終盤前まで)', 
            '得点に繋がった回数 (終盤前まで)', 
            '得点率 (%) (終盤前まで)'
        ]].sort_values(by=['場面'], ascending=[True]) # 場面でソート

        analysis_text += summary_serve_df.to_markdown(index=False)
        analysis_text += "\n\n"

    else:
        analysis_text += "ゲーム終盤でのサーブのデータがありません。\n\n"

    # --- 8-8以降のゲーム展開詳細 ---
    analysis_text += "### 8-8以降のゲーム展開詳細\n\n"
    if game_ending_rallies_detail:
        df_game_ending_rallies_detail = pd.DataFrame(game_ending_rallies_detail)
        # 不要になった '得点の内容' と '失点の内容' を削除してから表示
        df_game_ending_rallies_detail = df_game_ending_rallies_detail.drop(columns=['得点の内容', '失点の内容'], errors='ignore')
        analysis_text += df_game_ending_rallies_detail.to_markdown(index=False)
        analysis_text += "\n\n"
    else:
        analysis_text += "8-8以降のゲーム展開データがありません。\n\n"

    return analysis_text


def display_aite_game_ending_serve_analysis(df):
    """
    ゲームのフェーズ（序盤・中盤、終盤）ごとに、相手サーブの傾向を分析し、
    StreamlitのUIに表示する関数
    
    Args:
        df (pd.DataFrame): 試合の得失点データ
    """
    st.markdown("---")
    st.subheader("8-8以降の相手のサーブ分析")

    COLUMN_MAP = {
        'ゲーム数': 'ゲーム数',
        '誰のサーブか': '誰のサーブか',
        '得点者': '得点者',
        '自分の得点': '自分の得点',
        '相手の得点': '相手の得点',
        'サーブの種類': 'サーブの種類',
        'サーブのコース': 'サーブのコース',
    }

    actual_required_cols = list(COLUMN_MAP.values())
    if df.empty or not all(col in df.columns for col in actual_required_cols):
        missing_cols = [col for col in actual_required_cols if col not in df.columns]
        st.warning(f"相手のサーブ分析に必要なデータ列が見つかりません: {', '.join(missing_cols)}")
        return

    df = df.fillna('')
    
    # 相手がサーブを出したラリーのみを抽出
    aite_serves_df = df[df[COLUMN_MAP['誰のサーブか']] == '相手'].copy()

    if aite_serves_df.empty:
        st.info("相手のサーブのデータがありません。")
        return

    # ゲームのフェーズを判定する関数
    def get_game_phase(row):
        my_score = row[COLUMN_MAP['自分の得点']]
        opponent_score = row[COLUMN_MAP['相手の得点']]
        # ラリー開始時点のスコアで終盤を判定
        rally_start_my_score = my_score - 1 if row[COLUMN_MAP['得点者']] == '自分' else my_score
        rally_start_opponent_score = opponent_score - 1 if row[COLUMN_MAP['得点者']] == '相手' else opponent_score
        
        # ただし、スコアが0未満になることはないため補正
        rally_start_my_score = max(0, rally_start_my_score)
        rally_start_opponent_score = max(0, rally_start_opponent_score)

        if rally_start_my_score >= 8 and rally_start_opponent_score >= 8:
            return '終盤'
        else:
            return '序盤・中盤'
    
    aite_serves_df['ゲームフェーズ'] = aite_serves_df.apply(get_game_phase, axis=1)

    # サーブの傾向を分析
    def analyze_serves(df_subset, phase_name):
        serve_counts = {}
        for _, row in df_subset.iterrows():
            serve_type_raw = row[COLUMN_MAP['サーブの種類']]
            grouped_serve_type = group_serve_type(serve_type_raw)
            
            serve_course_raw = row[COLUMN_MAP['サーブのコース']]
            grouped_serve_course = group_serve_course(serve_course_raw)
            
            specific_play = f"{grouped_serve_type} ({grouped_serve_course})" if grouped_serve_type or grouped_serve_course else '不明なサーブ/コース'
            
            scorer = row[COLUMN_MAP['得点者']]
            
            if specific_play not in serve_counts:
                serve_counts[specific_play] = {'総回数': 0, '自分の得点': 0, '相手の得点': 0}
                
            serve_counts[specific_play]['総回数'] += 1
            if scorer == '自分':
                serve_counts[specific_play]['自分の得点'] += 1
            elif scorer == '相手':
                serve_counts[specific_play]['相手の得点'] += 1
        
        analysis_df = pd.DataFrame.from_dict(serve_counts, orient='index')
        analysis_df.index.name = '相手のサーブ（種類・コース）'
        analysis_df.reset_index(inplace=True)

        analysis_df['自分の得点率 (%)'] = analysis_df.apply(
            lambda row: round((row['自分の得点'] / row['総回数']) * 100, 1) if row['総回数'] > 0 else 0.0,
            axis=1
        )
        analysis_df['相手の得点率 (%)'] = analysis_df.apply(
            lambda row: round((row['相手の得点'] / row['総回数']) * 100, 1) if row['総回数'] > 0 else 0.0,
            axis=1
        )
        
        analysis_df = analysis_df.rename(columns={'相手のサーブ（種類・コース）': '相手のサーブ'})
        analysis_df = analysis_df[['相手のサーブ', '総回数', '自分の得点', '相手の得点', '自分の得点率 (%)', '相手の得点率 (%)']]
        
        st.markdown(f"##### ゲーム{phase_name}の相手サーブ傾向")
        st.dataframe(analysis_df)
        st.write(f"※**自分の得点率**は、相手のサーブに対して自分がラリーを制した確率を示します。")


    # 序盤・中盤の分析を表示
    non_game_ending_df = aite_serves_df[aite_serves_df['ゲームフェーズ'] == '序盤・中盤']
    if not non_game_ending_df.empty:
        analyze_serves(non_game_ending_df, "序盤・中盤")
    else:
        st.markdown("##### ゲーム序盤・中盤の相手サーブ傾向")
        st.info("ゲーム序盤・中盤に相手が出したサーブのデータがありません。")

    st.markdown("---")
    
    # 終盤の分析を表示
    game_ending_df = aite_serves_df[aite_serves_df['ゲームフェーズ'] == '終盤']
    if not game_ending_df.empty:
        analyze_serves(game_ending_df, "終盤")
    else:
        st.markdown("##### ゲーム終盤の相手サーブ傾向")
        st.info("ゲーム終盤に相手が出したサーブのデータがありません。")
