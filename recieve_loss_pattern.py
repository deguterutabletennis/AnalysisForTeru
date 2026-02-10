import streamlit as st
import pandas as pd

def display_recieve_loss_pattern(df):
    """
    自分のレシーブで失点したパターンをStreamlitのUIに表示する関数
    """
    # 必須列に「コメント・課題」を追加
    required_columns = ['開始時刻', '得失点の種類', 'ゲーム数', '誰のサーブか', '得点者', 
                        'レシーブの種類', '失点の内容', 'コメント・課題', 'YouTubeリンク']

    if df.empty or not all(col in df.columns for col in required_columns):
        st.warning('スプレッドシートの読み込みに失敗したか、必要な列が見つかりませんでした。')
        return

    with st.expander('レシーブ時の失点パターン一覧'):
        try:
            df['ゲーム数'] = pd.to_numeric(df['ゲーム数'], errors='coerce')
            df = df.dropna(subset=['ゲーム数'])
            df['ゲーム数'] = df['ゲーム数'].astype(int)
        except Exception as e:
            st.error(f"「ゲーム数」列の型変換中にエラーが発生しました: {e}")
            return

        df_temp = df.copy()
        
        # --- 修正ポイント：NaNを空文字に置換してから文字列変換（コメント・課題を含む） ---
        str_columns = ['誰のサーブか', '得点者', 'レシーブの種類', '失点の内容', 'コメント・課題']
        for col in str_columns:
            df_temp[col] = df_temp[col].fillna('').astype(str).str.strip()

        loss_types = ['相手のプレーで失点', '自分のミスで失点', '失点（判断迷う）']

        filtered_df = df_temp[
            (df_temp['誰のサーブか'] == '相手') &
            (df_temp['得点者'] == '相手') &
            (df_temp['得失点の種類'].isin(loss_types)) &
            (df_temp['失点の内容'] != '') # nan判定を簡略化
        ].copy()

        if filtered_df.empty:
            st.warning('自分のレシーブで失点したパターンは見つかりませんでした。')
            return
        
        # 表示列に「コメント・課題」を追加
        display_columns = [
            '開始時刻', 'レシーブの種類', '失点の内容', 'コメント・課題'
        ]

        def format_youtube_link_for_html(row):
            return f"<a href='{row['YouTubeリンク']}' target='_blank'>{row['開始時刻']}</a>"

        html_display_df = filtered_df[display_columns + ['YouTubeリンク']].copy()
        
        if 'YouTubeリンク' in filtered_df.columns:
            html_display_df['開始時刻'] = html_display_df.apply(format_youtube_link_for_html, axis=1)
            html_display_df = html_display_df.drop(columns='YouTubeリンク')
        
        # index=False で行番号を非表示に
        st.markdown(
            html_display_df.to_html(escape=False, classes='dataframe table-striped', index=False),
            unsafe_allow_html=True
        )
        st.info('この表は、自分のレシーブで失点した時の各パターンを表示しています。')

def get_recieve_loss_pattern_for_ai(df):
    """
    自分のレシーブで失点したパターンを抽出し、AIに渡すためのMarkdown文字列を生成する
    """
    required_columns = ['開始時刻', '得失点の種類', 'ゲーム数', '誰のサーブか', '得点者', 
                        'レシーブの種類', '失点の内容', 'コメント・課題', 'YouTubeリンク']

    if df.empty or not all(col in df.columns for col in required_columns):
        return "レシーブ時の失点パターンデータが利用できません。"

    try:
        df['ゲーム数'] = pd.to_numeric(df['ゲーム数'], errors='coerce')
        df = df.dropna(subset=['ゲーム数'])
        df['ゲーム数'] = df['ゲーム数'].astype(int)
    except Exception:
        return "レシーブ時の失点パターンデータ生成中にエラーが発生しました。"

    df_temp = df.copy()
    
    # 欠損値を空文字に置換
    str_columns = ['誰のサーブか', '得点者', 'レシーブの種類', '失点の内容', 'コメント・課題']
    for col in str_columns:
        df_temp[col] = df_temp[col].fillna('').astype(str).str.strip()

    loss_types = ['相手のプレーで失点', '自分のミスで失点', '失点（判断迷う）']

    filtered_df = df_temp[
        (df_temp['誰のサーブか'] == '相手') &
        (df_temp['得点者'] == '相手') &
        (df_temp['得失点の種類'].isin(loss_types)) &
        (df_temp['失点の内容'] != '')
    ].copy()

    if filtered_df.empty:
        return "自分のレシーブで失点したパターンは見つかりませんでした。"
    
    # AIへの送信項目に「コメント・課題」を追加
    columns_for_ai = [
        'ゲーム数', 'レシーブの種類', '失点の内容', 'コメント・課題'
    ]
    
    pattern_markdown = filtered_df[columns_for_ai].to_markdown(index=False)
    
    return f"## 自分のレシーブでの失点パターン一覧\n\n{pattern_markdown}"