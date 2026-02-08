import streamlit as st
import pandas as pd
import plotly.express as px

def display_serve_win_rate_analysis(df, current_player):
    """
    サーブ種類別の得点率と構成比をStreamlitのUIに表示する関数
    
    Args:
        df (pd.DataFrame): 試合の得失点データ
        current_player (str): 分析対象のプレイヤー ('自分'または'相手')
    """
    st.write("---")
    st.subheader(f"{current_player}のサーブ種類別 得点率と構成比")

    # 必要な列がすべて存在するか確認
    required_cols = ['誰のサーブか', 'サーブの種類', '得点者', '自分の得点', '相手の得点']
    if not all(col in df.columns for col in required_cols):
        st.warning(f"サーブ分析に必要なデータ列が見つかりません: {', '.join(required_cols)}。データを確認してください。")
        return

    # ゲームのフェーズを判定する関数
    def get_game_phase(row):
        my_score = row['自分の得点']
        opponent_score = row['相手の得点']
        
        # ラリー開始時点のスコアで終盤を判定
        rally_start_my_score = my_score - 1 if row['得点者'] == '自分' else my_score
        rally_start_opponent_score = opponent_score - 1 if row['得点者'] == '相手' else opponent_score
        
        # ただし、スコアが0未満になることはないため補正
        rally_start_my_score = max(0, rally_start_my_score)
        rally_start_opponent_score = max(0, rally_start_opponent_score)

        if rally_start_my_score >= 8 and rally_start_opponent_score >= 8:
            return '終盤'
        else:
            return '序盤・中盤'

    # データをコピーし、サーブデータを抽出
    df_serve = df[df['誰のサーブか'] == current_player].copy()

    if df_serve.empty:
        st.info(f"「誰のサーブか」が「{current_player}」となっているデータが見つかりません。")
        return

    # ゲームフェーズ列を追加
    df_serve['ゲームフェーズ'] = df_serve.apply(get_game_phase, axis=1)
    
    # サーブ種類をグループ化する関数
    serve_keywords = {
        '順横': '順横',
        'YGサーブ': 'YG',
        '巻込みサーブ': '巻込み',
        'バックサーブ': 'バック',
        'キックサーブ': 'キック'
    }
    def categorize_serve(serve_type):
        serve_type = str(serve_type).strip()
        if serve_type == '':
            return 'その他'
        for group, keyword in serve_keywords.items():
            if keyword in serve_type:
                return group
        return 'その他'

    df_serve['サーブ種類（グループ化）'] = df_serve['サーブの種類'].apply(categorize_serve)

    # データを集計
    def get_serve_summary(df_subset, current_player_name):
        total_serves = df_subset.groupby('サーブ種類（グループ化）').size().reset_index(name='総本数')
        points_won = df_subset[df_subset['得点者'] == current_player_name].groupby('サーブ種類（グループ化）').size().reset_index(name='得点数')
        
        summary = pd.merge(total_serves, points_won, on='サーブ種類（グループ化）', how='left').fillna(0)
        summary['得点率'] = (summary['得点数'] / summary['総本数']) * 100
        
        summary = summary.rename(columns={
            'サーブ種類（グループ化）': 'サーブの種類',
            '総本数': '総回数'
        }).sort_values(by='総回数', ascending=False).reset_index(drop=True)
        return summary

    # 全体と終盤のサマリーを作成
    serve_summary_all = get_serve_summary(df_serve, current_player)
    serve_summary_ending = get_serve_summary(df_serve[df_serve['ゲームフェーズ'] == '終盤'], current_player)

    # データフレームと円グラフを並べて表示
    st.markdown("##### 得点率・構成比")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("###### 試合全体")
        st.dataframe(serve_summary_all.style.format({
            '得点数': "{:.0f}",
            '総回数': "{:.0f}",
            '得点率': "{:.1f}%"
        }))
        
    with col2:
        st.markdown("###### 終盤 (8-8以降)")
        if serve_summary_ending.empty:
            st.info("終盤のデータがありません。")
        else:
            st.dataframe(serve_summary_ending.style.format({
                '得点数': "{:.0f}",
                '総回数': "{:.0f}",
                '得点率': "{:.1f}%"
            }))

    st.write("---")
    
    # 円グラフを並べて表示
    col3, col4 = st.columns(2)

    with col3:
        fig_all = px.pie(serve_summary_all, values='総回数', names='サーブの種類', title='試合全体のサーブ構成比',
                         hover_data=['得点率'], labels={'総回数':'総回数', 'サーブの種類':'サーブの種類'})
        fig_all.update_traces(textinfo='percent+label')
        st.plotly_chart(fig_all, use_container_width=True)

    with col4:
        if serve_summary_ending.empty:
            st.info("終盤のサーブ構成比のデータがありません。")
        else:
            fig_ending = px.pie(serve_summary_ending, values='総回数', names='サーブの種類', title='終盤のサーブ構成比',
                                hover_data=['得点率'], labels={'総回数':'総回数', 'サーブの種類':'サーブの種類'})
            fig_ending.update_traces(textinfo='percent+label')
            st.plotly_chart(fig_ending, use_container_width=True)

def get_serve_win_rate_analysis_for_ai(df, current_player):
    """
    サーブ種類別の得点率分析結果をAIに渡すためのMarkdown文字列を生成する
    
    Args:
        df (pd.DataFrame): 試合の得失点データ
        current_player (str): 分析対象のプレイヤー ('自分'または'相手')
        
    Returns:
        str: 分析結果のMarkdown文字列
    """
    df_serve = df[df['誰のサーブか'] == current_player].copy()

    required_columns = ['誰のサーブか', 'サーブの種類', '得点者']
    if df_serve.empty or not all(col in df_serve.columns for col in required_columns):
        return f"{current_player}のサーブ種類別の得点率分析データが利用できません。"

    df_serve['サーブの種類'] = df_serve['サーブの種類'].astype(str).str.strip()

    serve_keywords = {
        '順横': '順横',
        'YGサーブ': 'YG',
        '巻込みサーブ': '巻込み',
        'バックサーブ': 'バック',
        'キックサーブ': 'キック'
    }

    def categorize_serve(serve_type):
        if pd.isna(serve_type) or serve_type == '':
            return 'その他'
        
        for group, keyword in serve_keywords.items():
            if keyword in serve_type:
                return group
        return 'その他'

    df_serve['サーブ種類（グループ化）'] = df_serve['サーブの種類'].apply(categorize_serve)

    total_serves = df_serve.groupby('サーブ種類（グループ化）').size().reset_index(name='総本数')
    points_won = df_serve[df_serve['得点者'] == current_player].groupby('サーブ種類（グループ化）').size().reset_index(name='得点数')

    serve_summary = pd.merge(total_serves, points_won, on='サーブ種類（グループ化）', how='left').fillna(0)
    
    serve_summary['得点率'] = (serve_summary['得点数'] / serve_summary['総本数']) * 100
    
    serve_summary = serve_summary.rename(columns={
        'サーブ種類（グループ化）': 'サーブの種類',
        '総本数': '総回数'
    })

    serve_summary['得点率'] = serve_summary['得点率'].round(1).astype(str) + '%'
    serve_summary['得点数'] = serve_summary['得点数'].astype(int)
    serve_summary['総回数'] = serve_summary['総回数'].astype(int)

    analysis_text = f"## {current_player}のサーブ種類別の得点率分析\n\n"
    if not serve_summary.empty:
        analysis_text += f"### {current_player}のサーブ種類ごとの得点率\n"
        analysis_text += serve_summary.to_markdown(index=False)
    else:
        analysis_text += f"{current_player}のサーブ種類別のデータが不足しているため、分析できませんでした。\n"
        
    return analysis_text