import streamlit as st

def display_match_summary(df, df_opponents):
    """
    試合全体のサマリーを計算し、StreamlitのUIに表示する関数
    
    Args:
        df (pd.DataFrame): 試合の得失点データ
        df_opponents (pd.DataFrame): 相手選手の情報
    """
    if df.empty or 'ゲーム数' not in df.columns:
        st.warning("試合サマリーを表示できませんでした。「ゲーム数」の列を確認してください。")
        return

    game_scores = []
    my_games_won = 0
    opponent_games_won = 0

    unique_game_numbers = sorted(df['ゲーム数'].unique())
    
    for game_num in unique_game_numbers:
        df_game = df[df['ゲーム数'] == game_num]
        
        if '自分の得点' in df_game.columns and '相手の得点' in df_game.columns:
            # ゲーム終了時の最終得点を取得
            if not df_game.empty:
                final_my_score = df_game['自分の得点'].iloc[-1]
                final_opponent_score = df_game['相手の得点'].iloc[-1]
            else:
                continue

            game_scores.append(f"{final_my_score}-{final_opponent_score}")
            
            if final_my_score > final_opponent_score:
                my_games_won += 1
            else:
                opponent_games_won += 1

    if not game_scores:
        st.warning("試合スコアを計算できませんでした。「自分の得点」、「相手の得点」の列を確認してください。")
        return

    winner_mark = "〇" if my_games_won > opponent_games_won else "×"
    opponent_mark = "〇" if opponent_games_won > my_games_won else "×"
    
    opponent_name = df_opponents.loc[0, '名前'] if '名前' in df_opponents.columns and not df_opponents.empty else ""
    opponent_affiliation = df_opponents.loc[0, '所属'] if '所属' in df_opponents.columns and not df_opponents.empty else ""

    opponent_display_name = opponent_name
    if opponent_affiliation:
        opponent_display_name = str(opponent_display_name) + f"({str(opponent_affiliation)})"
#        opponent_display_name += f"({opponent_affiliation})"
    
    summary_text = f"{winner_mark}自分 {my_games_won}-{opponent_games_won} {opponent_display_name}{opponent_mark}\n"
    summary_text += f"（{', '.join(game_scores)}）"
    
    st.subheader("試合結果サマリー")
    st.markdown(f"**{summary_text}**")


# --- AI分析用の関数 ---
def get_match_summary_for_ai(df, df_opponents):
    """
    試合全体のサマリーを計算し、AIに渡すための文字列として返す関数
    
    Args:
        df (pd.DataFrame): 試合の得失点データ
        df_opponents (pd.DataFrame): 相手選手の情報
        
    Returns:
        str: 試合結果のサマリー文字列
    """
    if df.empty or 'ゲーム数' not in df.columns or '自分の得点' not in df.columns or '相手の得点' not in df.columns:
        return "試合結果のサマリーデータが利用できません。"

    game_scores = []
    my_games_won = 0
    opponent_games_won = 0

    unique_game_numbers = sorted(df['ゲーム数'].unique())
    
    for game_num in unique_game_numbers:
        df_game = df[df['ゲーム数'] == game_num]
        
        if not df_game.empty:
            final_my_score = df_game['自分の得点'].iloc[-1]
            final_opponent_score = df_game['相手の得点'].iloc[-1]
        else:
            continue
            
        game_scores.append(f"{final_my_score}-{final_opponent_score}")
        
        if final_my_score > final_opponent_score:
            my_games_won += 1
        else:
            opponent_games_won += 1
    
    if not game_scores:
        return "試合スコアを計算できませんでした。"

    match_result = "勝利" if my_games_won > opponent_games_won else "敗北"
    
    # AIが理解しやすいように、構造化された情報として文字列を生成
    summary_text = f"## 試合結果\n"
    summary_text += f"**勝敗**: あなたの{match_result} ({my_games_won}-{opponent_games_won})\n"
    summary_text += f"**ゲームごとのスコア**: {', '.join(game_scores)}\n"
    
    opponent_name = df_opponents.loc[0, '名前'] if '名前' in df_opponents.columns and not df_opponents.empty else "不明"
    opponent_affiliation = df_opponents.loc[0, '所属'] if '所属' in df_opponents.columns and not df_opponents.empty else "不明"
    summary_text += f"**対戦相手**: {opponent_name} ({opponent_affiliation})\n"
    
    return summary_text

