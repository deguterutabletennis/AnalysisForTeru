import streamlit as st
import pandas as pd

def display_serve_receive_analysis(df):
    """
    サーブ・レシーブ別得失点分析をStreamlitのUIに表示する関数
    
    Args:
        df (pd.DataFrame): 試合の得失点データ
    """
    required_columns = ['得失点の種類', 'ゲーム数', '誰のサーブか']
    if not df.empty and all(col in df.columns for col in required_columns):
        st.header('サーブ・レシーブ別 得失点分析')

        score_types = ['自分のプレーで得点', '相手のミスで得点', '得点（判断迷う）']
        loss_types = ['相手のプレーで失点', '自分のミスで失点', '失点（判断迷う）']

        try:
            df['ゲーム数'] = pd.to_numeric(df['ゲーム数'], errors='coerce')
            df = df.dropna(subset=['ゲーム数'])
            df['ゲーム数'] = df['ゲーム数'].astype(int)
        except Exception as e:
            st.error(f"「ゲーム数」列の型変換中にエラーが発生しました。データ形式を確認してください: {e}")
            st.stop()
        
        df['誰のサーブか'] = df['誰のサーブか'].astype(str).str.strip()

        unique_game_numbers = sorted(df['ゲーム数'].unique())
        
        final_summary_rows = []
        total_serve_points_gained_overall = 0
        total_serve_points_lost_overall = 0
        total_receive_points_gained_overall = 0
        total_receive_points_lost_overall = 0
        
        def safe_rate(count, total):
            return f"{count / total * 100:.1f}" if total > 0 else "0.0"

        if not unique_game_numbers:
            st.warning("「ゲーム数」列に有効なデータが見つかりませんでした。")
        else:
            for game_num in unique_game_numbers:
                df_game = df[df['ゲーム数'] == game_num]

                for server_type_raw in ['自分', '相手']:
                    df_filtered = df_game[df_game['誰のサーブか'] == server_type_raw]
                    category_name = 'サーブ' if server_type_raw == '自分' else 'レシーブ'

                    points_gained = 0
                    for s_type in score_types:
                        points_gained += df_filtered[df_filtered['得失点の種類'] == s_type].shape[0]
                    
                    points_lost = 0
                    for l_type in loss_types:
                        points_lost += df_filtered[df_filtered['得失点の種類'] == l_type].shape[0]
                    
                    total_plays = points_gained + points_lost

                    win_rate = safe_rate(points_gained, total_plays)
                    loss_rate = safe_rate(points_lost, total_plays)

                    final_summary_rows.append({
                        'ゲーム数': game_num,
                        'サーブ/レシーブ': category_name,
                        '得点数': points_gained,
                        '失点数': points_lost,
                        '得点率 (%)': win_rate,
                        '失点率 (%)': loss_rate
                    })
                    
                    if server_type_raw == '自分':
                        total_serve_points_gained_overall += points_gained
                        total_serve_points_lost_overall += points_lost
                    else:
                        total_receive_points_gained_overall += points_gained
                        total_receive_points_lost_overall += points_lost

            final_summary_df = pd.DataFrame(final_summary_rows)

            total_serve_plays_overall = total_serve_points_gained_overall + total_serve_points_lost_overall
            total_serve_win_rate = safe_rate(total_serve_points_gained_overall, total_serve_plays_overall)
            total_serve_loss_rate = safe_rate(total_serve_points_lost_overall, total_serve_plays_overall)
            final_summary_df.loc[len(final_summary_df)] = {
                'ゲーム数': 'Total',
                'サーブ/レシーブ': 'サーブ',
                '得点数': total_serve_points_gained_overall,
                '失点数': total_serve_points_lost_overall,
                '得点率 (%)': total_serve_win_rate,
                '失点率 (%)': total_serve_loss_rate
            }

            total_receive_plays_overall = total_receive_points_gained_overall + total_receive_points_lost_overall
            total_receive_win_rate = safe_rate(total_receive_points_gained_overall, total_receive_plays_overall)
            total_receive_loss_rate = safe_rate(total_receive_points_lost_overall, total_receive_plays_overall)
            final_summary_df.loc[len(final_summary_df)] = {
                'ゲーム数': 'Total',
                'サーブ/レシーブ': 'レシーブ',
                '得点数': total_receive_points_gained_overall,
                '失点数': total_receive_points_lost_overall,
                '得点率 (%)': total_receive_win_rate,
                '失点率 (%)': total_receive_loss_rate
            }
            
            final_summary_df['ゲーム数'] = final_summary_df['ゲーム数'].astype(str)

            st.subheader("試合全体のサーブ/レシーブ別得失点サマリー")
            total_df = final_summary_df[final_summary_df['ゲーム数'] == 'Total'].set_index('サーブ/レシーブ')
            
            col_serve_total, col_receive_total = st.columns(2)
            with col_serve_total:
                st.markdown("##### サーブ")
                st.table(total_df[['得点数', '失点数', '得点率 (%)', '失点率 (%)']].loc[['サーブ']])
            with col_receive_total:
                st.markdown("##### レシーブ")
                st.table(total_df[['得点数', '失点数', '得点率 (%)', '失点率 (%)']].loc[['レシーブ']])

            st.markdown("---")

            st.subheader("ゲームごとの詳細")
            for game_num in unique_game_numbers:
                with st.expander(f"ゲーム {game_num} の詳細を見る"):
                    game_df = final_summary_df[final_summary_df['ゲーム数'] == str(game_num)].set_index('サーブ/レシーブ')
                    
                    col_game_serve, col_game_receive = st.columns(2)
                    with col_game_serve:
                        st.markdown("##### サーブ")
                        st.table(game_df[['得点数', '失点数', '得点率 (%)', '失点率 (%)']].loc[['サーブ']])
                    with col_game_receive:
                        st.markdown("##### レシーブ")
                        st.table(game_df[['得点数', '失点数', '得点率 (%)', '失点率 (%)']].loc[['レシーブ']])
    else:
        st.warning('スプレッドシートの読み込みに失敗したか、必要な列（「得失点の種類」、「ゲーム数」、「誰のサーブか」）が見つかりませんでした。')

def get_serve_receive_analysis_for_ai(df):
    """
    サーブ・レシーブ別得失点分析結果をAIに渡すためのMarkdown文字列を生成する
    
    Args:
        df (pd.DataFrame): 試合の得失点データ
        
    Returns:
        str: 分析結果のMarkdown文字列
    """
    required_columns = ['得失点の種類', 'ゲーム数', '誰のサーブか']
    if df.empty or not all(col in df.columns for col in required_columns):
        return "サーブ・レシーブ別 得失点分析に必要なデータ列が見つかりません。"

    score_types = ['自分のプレーで得点', '相手のミスで得点', '得点（判断迷う）']
    loss_types = ['相手のプレーで失点', '自分のミスで失点', '失点（判断迷う）']

    try:
        df['ゲーム数'] = pd.to_numeric(df['ゲーム数'], errors='coerce')
        df = df.dropna(subset=['ゲーム数'])
        df['ゲーム数'] = df['ゲーム数'].astype(int)
    except Exception as e:
        return f"「ゲーム数」列の型変換中にエラーが発生しました: {e}"
    
    df['誰のサーブか'] = df['誰のサーブか'].astype(str).str.strip()

    unique_game_numbers = sorted(df['ゲーム数'].unique())
    if not unique_game_numbers:
        return "「ゲーム数」列に有効なデータが見つかりませんでした。"
    
    final_summary_rows = []
    total_serve_points_gained_overall = 0
    total_serve_points_lost_overall = 0
    total_receive_points_gained_overall = 0
    total_receive_points_lost_overall = 0
    
    def safe_rate(count, total):
        return round(count / total * 100, 1) if total > 0 else 0.0

    for game_num in unique_game_numbers:
        df_game = df[df['ゲーム数'] == game_num]
        
        for server_type_raw in ['自分', '相手']:
            df_filtered = df_game[df_game['誰のサーブか'] == server_type_raw]
            category_name = 'サーブ' if server_type_raw == '自分' else 'レシーブ'
            
            points_gained = sum(df_filtered[df_filtered['得失点の種類'].isin(score_types)].shape[0] for _ in range(1))
            points_lost = sum(df_filtered[df_filtered['得失点の種類'].isin(loss_types)].shape[0] for _ in range(1))
            total_plays = points_gained + points_lost
            
            win_rate = safe_rate(points_gained, total_plays)
            loss_rate = safe_rate(points_lost, total_plays)

            final_summary_rows.append({
                'ゲーム数': str(game_num),
                'サーブ/レシーブ': category_name,
                '得点数': points_gained,
                '失点数': points_lost,
                '得点率 (%)': f"{win_rate}%",
                '失点率 (%)': f"{loss_rate}%"
            })

            if server_type_raw == '自分':
                total_serve_points_gained_overall += points_gained
                total_serve_points_lost_overall += points_lost
            else:
                total_receive_points_gained_overall += points_gained
                total_receive_points_lost_overall += points_lost

    final_summary_df = pd.DataFrame(final_summary_rows)

    total_serve_plays_overall = total_serve_points_gained_overall + total_serve_points_lost_overall
    total_serve_win_rate = safe_rate(total_serve_points_gained_overall, total_serve_plays_overall)
    total_serve_loss_rate = safe_rate(total_serve_points_lost_overall, total_serve_plays_overall)
    final_summary_df.loc[len(final_summary_df)] = {
        'ゲーム数': 'Total',
        'サーブ/レシーブ': 'サーブ',
        '得点数': total_serve_points_gained_overall,
        '失点数': total_serve_points_lost_overall,
        '得点率 (%)': f"{total_serve_win_rate}%",
        '失点率 (%)': f"{total_serve_loss_rate}%"
    }

    total_receive_plays_overall = total_receive_points_gained_overall + total_receive_points_lost_overall
    total_receive_win_rate = safe_rate(total_receive_points_gained_overall, total_receive_plays_overall)
    total_receive_loss_rate = safe_rate(total_receive_points_lost_overall, total_receive_plays_overall)
    final_summary_df.loc[len(final_summary_df)] = {
        'ゲーム数': 'Total',
        'サーブ/レシーブ': 'レシーブ',
        '得点数': total_receive_points_gained_overall,
        '失点数': total_receive_points_lost_overall,
        '得点率 (%)': f"{total_receive_win_rate}%",
        '失点率 (%)': f"{total_receive_loss_rate}%"
    }
    
    # AI向けにMarkdownを整形
    analysis_text = "## サーブ・レシーブ別 得失点分析\n\n"
    analysis_text += "### 試合全体のサマリー\n"
    analysis_text += "サーブとレシーブそれぞれの得失点数、得点率、失点率の合計です。\n"
    total_df_markdown = final_summary_df[final_summary_df['ゲーム数'] == 'Total'].to_markdown(index=False)
    analysis_text += total_df_markdown + "\n\n"
    
    analysis_text += "### ゲームごとの詳細\n"
    analysis_text += "ゲームごとの得失点数と得点率、失点率の推移です。\n"
    game_df_markdown = final_summary_df[final_summary_df['ゲーム数'] != 'Total'].to_markdown(index=False)
    analysis_text += game_df_markdown
    
    return analysis_text

