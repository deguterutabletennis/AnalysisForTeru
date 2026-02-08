import streamlit as st
import pandas as pd

def display_point_breakdown_analysis(df):
    """
    得失点合計と内訳をStreamlitのUIに表示する関数
    
    Args:
        df (pd.DataFrame): 試合の得失点データ
    """
    if not df.empty and '得失点の種類' in df.columns and 'ゲーム数' in df.columns:
        st.header('得失点合計と内訳')

        score_types = ['自分のプレーで得点', '相手のミスで得点', '得点（判断迷う）']
        loss_types = ['相手のプレーで失点', '自分のミスで失点', '失点（判断迷う）']

        category_mapping = {
            '自分/相手のプレー': {
                'score': '自分のプレーで得点',
                'loss': '相手のプレーで失点'
            },
            '相手/自分のミス': {
                'score': '相手のミスで得点',
                'loss': '自分のミスで失点'
            },
            '判断迷う': {
                'score': '得点（判断迷う）',
                'loss': '失点（判断迷う）'
            }
        }

        try:
            df['ゲーム数'] = pd.to_numeric(df['ゲーム数'], errors='coerce')
            df = df.dropna(subset=['ゲーム数'])
            df['ゲーム数'] = df['ゲーム数'].astype(int)
        except Exception as e:
            st.error(f"「ゲーム数」列の型変換中にエラーが発生しました。データ形式を確認してください: {e}")
            st.stop()

        unique_game_numbers = sorted(df['ゲーム数'].unique())
        
        final_summary_rows = []
        total_score_overall = 0
        total_loss_overall = 0
        total_player_play_score = 0
        total_player_play_loss = 0
        total_opponent_mistake_score = 0
        total_opponent_mistake_loss = 0
        total_confusing_score = 0
        total_confusing_loss = 0

        def safe_rate(count, total):
            return f"{count / total * 100:.1f}" if total > 0 else "0.0"

        if not unique_game_numbers:
            st.warning("「ゲーム数」列に有効なデータが見つかりませんでした。")
        else:
            for game_num in unique_game_numbers:
                df_game = df[df['ゲーム数'] == game_num]

                score_data = {s_type: df_game[df_game['得失点の種類'] == s_type].shape[0] for s_type in score_types}
                total_score = sum(score_data.values())
                
                loss_data = {l_type: df_game[df_game['得失点の種類'] == l_type].shape[0] for l_type in loss_types}
                total_loss = sum(loss_data.values())
                
                player_play_score = score_data.get(category_mapping['自分/相手のプレー']['score'], 0)
                opponent_mistake_score = score_data.get(category_mapping['相手/自分のミス']['score'], 0)
                confusing_score = score_data.get(category_mapping['判断迷う']['score'], 0)
                player_play_loss = loss_data.get(category_mapping['自分/相手のプレー']['loss'], 0)
                opponent_mistake_loss = loss_data.get(category_mapping['相手/自分のミス']['loss'], 0)
                confusing_loss = loss_data.get(category_mapping['判断迷う']['loss'], 0)

                final_summary_rows.append({
                    'ゲーム数': game_num, '種類': '得点', '合計': total_score,
                    '自分/相手のプレー': player_play_score, '相手/自分のミス': opponent_mistake_score, '判断迷う': confusing_score,
                    '自分/相手のプレー 率 (%)': safe_rate(player_play_score, total_score),
                    '相手/自分のミス 率 (%)': safe_rate(opponent_mistake_score, total_score),
                    '判断迷う 率 (%)': safe_rate(confusing_score, total_score)
                })
                final_summary_rows.append({
                    'ゲーム数': game_num, '種類': '失点', '合計': total_loss,
                    '自分/相手のプレー': player_play_loss, 
                    '相手/自分のミス': opponent_mistake_loss, 
                    '判断迷う': confusing_loss, 
                    '自分/相手のプレー 率 (%)': safe_rate(player_play_loss, total_loss),
                    '相手/自分のミス 率 (%)': safe_rate(opponent_mistake_loss, total_loss),
                    '判断迷う 率 (%)': safe_rate(confusing_loss, total_loss)
                })
                
                total_score_overall += total_score
                total_loss_overall += total_loss
                total_player_play_score += player_play_score
                total_player_play_loss += player_play_loss
                total_opponent_mistake_score += opponent_mistake_score
                total_opponent_mistake_loss += opponent_mistake_loss
                total_confusing_score += confusing_score
                total_confusing_loss += confusing_loss

            final_summary_df = pd.DataFrame(final_summary_rows)
            
            total_score_row = {
                'ゲーム数': 'Total', '種類': '得点', '合計': total_score_overall,
                '自分/相手のプレー': total_player_play_score, '相手/自分のミス': total_opponent_mistake_score, '判断迷う': total_confusing_score,
                '自分/相手のプレー 率 (%)': safe_rate(total_player_play_score, total_score_overall),
                '相手/自分のミス 率 (%)': safe_rate(total_opponent_mistake_score, total_score_overall),
                '判断迷う 率 (%)': safe_rate(total_confusing_score, total_score_overall)
            }
            total_loss_row = {
                'ゲーム数': 'Total', '種類': '失点', '合計': total_loss_overall,
                '自分/相手のプレー': total_player_play_loss, '相手/自分のミス': total_opponent_mistake_loss, '判断迷う': total_confusing_loss,
                '自分/相手のプレー 率 (%)': safe_rate(total_player_play_loss, total_loss_overall),
                '相手/自分のミス 率 (%)': safe_rate(total_opponent_mistake_loss, total_loss_overall),
                '判断迷う 率 (%)': safe_rate(total_confusing_loss, total_loss_overall)
            }
            
            final_summary_df = pd.concat([final_summary_df, pd.DataFrame([total_score_row, total_loss_row])], ignore_index=True)

            final_summary_df['ゲーム数'] = final_summary_df['ゲーム数'].astype(str)
            
            st.subheader("試合全体の得失点合計")
            total_df = final_summary_df[final_summary_df['ゲーム数'] == 'Total'].set_index('種類')

            col_score_total, col_loss_total = st.columns(2)
            with col_score_total:
                st.markdown("##### 得点合計")
                df_score_display = total_df[['合計', '自分/相手のプレー', '相手/自分のミス', '判断迷う']].loc[['得点']].rename(columns={
                    '自分/相手のプレー': '自分のプレー',
                    '相手/自分のミス': '相手のミス'
                })
                st.table(df_score_display)
            with col_loss_total:
                st.markdown("##### 失点合計")
                df_loss_display = total_df[['合計', '自分/相手のプレー', '相手/自分のミス', '判断迷う']].loc[['失点']].rename(columns={
                    '自分/相手のプレー': '相手のプレー',
                    '相手/自分のミス': '自分のミス'
                })
                st.table(df_loss_display)

            st.markdown("---")

            st.subheader("ゲームごとの詳細")
            for game_num in unique_game_numbers:
                with st.expander(f"ゲーム {game_num} の詳細を見る"):
                    game_df = final_summary_df[final_summary_df['ゲーム数'] == str(game_num)].set_index('種類')
                    
                    col_game_score, col_game_loss = st.columns(2)
                    with col_game_score:
                        st.markdown("##### 得点")
                        df_game_score_display = game_df[['合計', '自分/相手のプレー', '相手/自分のミス', '判断迷う']].loc[['得点']].rename(columns={
                            '自分/相手のプレー': '自分のプレー',
                            '相手/自分のミス': '相手のミス'
                        })
                        st.table(df_game_score_display)
                    with col_game_loss:
                        st.markdown("##### 失点")
                        df_game_loss_display = game_df[['合計', '自分/相手のプレー', '相手/自分のミス', '判断迷う']].loc[['失点']].rename(columns={
                            '自分/相手のプレー': '相手のプレー',
                            '相手/自分のミス': '自分のミス'
                        })
                        st.table(df_game_loss_display)

    else:
        st.warning('スプレッドシートの読み込みに失敗したか、必要な列（「得失点の種類」または「ゲーム数」）が見つかりませんでした。')

def get_point_breakdown_analysis_for_ai(df):
    """
    得失点合計と内訳の分析結果をAIに渡すためのMarkdown文字列を生成する
    
    Args:
        df (pd.DataFrame): 試合の得失点データ
        
    Returns:
        str: 分析結果のMarkdown文字列
    """
    required_columns = ['得失点の種類', 'ゲーム数']
    if df.empty or not all(col in df.columns for col in required_columns):
        return "得失点合計と内訳の分析に必要なデータ列が見つかりません。"

    score_types = ['自分のプレーで得点', '相手のミスで得点', '得点（判断迷う）']
    loss_types = ['相手のプレーで失点', '自分のミスで失点', '失点（判断迷う）']

    category_mapping = {
        '自分/相手のプレー': {
            'score': '自分のプレーで得点',
            'loss': '相手のプレーで失点'
        },
        '相手/自分のミス': {
            'score': '相手のミスで得点',
            'loss': '自分のミスで失点'
        },
        '判断迷う': {
            'score': '得点（判断迷う）',
            'loss': '失点（判断迷う）'
        }
    }

    try:
        df['ゲーム数'] = pd.to_numeric(df['ゲーム数'], errors='coerce')
        df = df.dropna(subset=['ゲーム数'])
        df['ゲーム数'] = df['ゲーム数'].astype(int)
    except Exception as e:
        return f"「ゲーム数」列の型変換中にエラーが発生しました: {e}"

    unique_game_numbers = sorted(df['ゲーム数'].unique())
    if not unique_game_numbers:
        return "「ゲーム数」列に有効なデータが見つかりませんでした。"
    
    final_summary_rows = []
    total_score_overall = 0
    total_loss_overall = 0
    total_player_play_score = 0
    total_player_play_loss = 0
    total_opponent_mistake_score = 0
    total_opponent_mistake_loss = 0
    total_confusing_score = 0
    total_confusing_loss = 0

    def safe_rate(count, total):
        return round(count / total * 100, 1) if total > 0 else 0.0

    for game_num in unique_game_numbers:
        df_game = df[df['ゲーム数'] == game_num]

        score_data = {s_type: df_game[df_game['得失点の種類'] == s_type].shape[0] for s_type in score_types}
        total_score = sum(score_data.values())
        
        loss_data = {l_type: df_game[df_game['得失点の種類'] == l_type].shape[0] for l_type in loss_types}
        total_loss = sum(loss_data.values())

        player_play_score = score_data.get(category_mapping['自分/相手のプレー']['score'], 0)
        opponent_mistake_score = score_data.get(category_mapping['相手/自分のミス']['score'], 0)
        confusing_score = score_data.get(category_mapping['判断迷う']['score'], 0)
        player_play_loss = loss_data.get(category_mapping['自分/相手のプレー']['loss'], 0)
        opponent_mistake_loss = loss_data.get(category_mapping['相手/自分のミス']['loss'], 0)
        confusing_loss = loss_data.get(category_mapping['判断迷う']['loss'], 0)

        final_summary_rows.append({
            'ゲーム数': str(game_num), '種類': '得点', '合計': total_score,
            '自分のプレーで得点': player_play_score, '相手のミスで得点': opponent_mistake_score, '得点（判断迷う）': confusing_score,
            '自分のプレーで得点率 (%)': f"{safe_rate(player_play_score, total_score)}%",
            '相手のミスで得点率 (%)': f"{safe_rate(opponent_mistake_score, total_score)}%",
            '得点（判断迷う）率 (%)': f"{safe_rate(confusing_score, total_score)}%"
        })
        final_summary_rows.append({
            'ゲーム数': str(game_num), '種類': '失点', '合計': total_loss,
            '相手のプレーで失点': player_play_loss, '自分のミスで失点': opponent_mistake_loss, '失点（判断迷う）': confusing_loss,
            '相手のプレーで失点率 (%)': f"{safe_rate(player_play_loss, total_loss)}%",
            '自分のミスで失点率 (%)': f"{safe_rate(opponent_mistake_loss, total_loss)}%",
            '失点（判断迷う）率 (%)': f"{safe_rate(confusing_loss, total_loss)}%"
        })
        
        total_score_overall += total_score
        total_loss_overall += total_loss
        total_player_play_score += player_play_score
        total_player_play_loss += player_play_loss
        total_opponent_mistake_score += opponent_mistake_score
        total_opponent_mistake_loss += opponent_mistake_loss
        total_confusing_score += confusing_score
        total_confusing_loss += confusing_loss

    final_summary_df = pd.DataFrame(final_summary_rows)
    
    total_score_row = {
        'ゲーム数': 'Total', '種類': '得点', '合計': total_score_overall,
        '自分のプレーで得点': total_player_play_score, '相手のミスで得点': total_opponent_mistake_score, '得点（判断迷う）': total_confusing_score,
        '自分のプレーで得点率 (%)': f"{safe_rate(total_player_play_score, total_score_overall)}%",
        '相手のミスで得点率 (%)': f"{safe_rate(total_opponent_mistake_score, total_score_overall)}%",
        '得点（判断迷う）率 (%)': f"{safe_rate(total_confusing_score, total_score_overall)}%"
    }
    total_loss_row = {
        'ゲーム数': 'Total', '種類': '失点', '合計': total_loss_overall,
        '相手のプレーで失点': total_player_play_loss, '自分のミスで失点': total_opponent_mistake_loss, '失点（判断迷う）': total_confusing_loss,
        '相手のプレーで失点率 (%)': f"{safe_rate(total_player_play_loss, total_loss_overall)}%",
        '自分のミスで失点率 (%)': f"{safe_rate(total_opponent_mistake_loss, total_loss_overall)}%",
        '失点（判断迷う）率 (%)': f"{safe_rate(total_confusing_loss, total_loss_overall)}%"
    }
    
    final_summary_df = pd.concat([final_summary_df, pd.DataFrame([total_score_row, total_loss_row])], ignore_index=True)
    
    analysis_text = "## 得失点合計と内訳\n\n"
    analysis_text += "### 試合全体の得失点サマリー\n"
    analysis_text += "試合全体の得失点の合計と、その内訳（プレー、ミス、その他）です。\n"
    total_df_markdown = final_summary_df[final_summary_df['ゲーム数'] == 'Total'].to_markdown(index=False)
    analysis_text += total_df_markdown + "\n\n"
    
    analysis_text += "### ゲームごとの詳細\n"
    analysis_text += "ゲームごとの得失点合計とその内訳の推移です。\n"
    game_df_markdown = final_summary_df[final_summary_df['ゲーム数'] != 'Total'].to_markdown(index=False)
    analysis_text += game_df_markdown
    
    return analysis_text
