import streamlit as st
import pandas as pd

def display_recieve_loss_pattern(df):
    """
    自分のレシーブで失点したパターンをStreamlitのUIに表示する関数
    
    Args:
        df (pd.DataFrame): 試合の得失点データ
    """
    required_columns = ['開始時刻', '得失点の種類', 'ゲーム数', '誰のサーブか', '得点者', 
                        'レシーブの種類', '失点の内容', 'YouTubeリンク']

    if df.empty or not all(col in df.columns for col in required_columns):
        st.warning('スプレッドシートの読み込みに失敗したか、必要な列が見つかりませんでした。')
        return

    with st.expander('レシーブ時の失点パターン一覧'):
        try:
            df['ゲーム数'] = pd.to_numeric(df['ゲーム数'], errors='coerce')
            df = df.dropna(subset=['ゲーム数'])
            df['ゲーム数'] = df['ゲーム数'].astype(int)
        except Exception as e:
            st.error(f"「ゲーム数」列の型変換中にエラーが発生しました。データ形式を確認してください: {e}")
            return

        df_temp = df.copy()
        df_temp['誰のサーブか'] = df_temp['誰のサーブか'].astype(str).str.strip()
        df_temp['得点者'] = df_temp['得点者'].astype(str).str.strip()
        df_temp['レシーブの種類'] = df_temp['レシーブの種類'].astype(str).str.strip()
        df_temp['失点の内容'] = df_temp['失点の内容'].astype(str).str.strip()

        loss_types = ['相手のプレーで失点', '自分のミスで失点', '失点（判断迷う）']

        filtered_df = df_temp[
            (df_temp['誰のサーブか'] == '相手') &
            (df_temp['得点者'] == '相手') &
            (df_temp['得失点の種類'].isin(loss_types)) &
            (df_temp['失点の内容'].astype(str).str.strip().str.lower() != 'nan') &
            (df_temp['失点の内容'].astype(str).str.strip() != '') &
            (df_temp['失点の内容'].notna())
        ].copy()

        if filtered_df.empty:
            st.warning('自分のレシーブで失点したパターンは見つかりませんでした。')
            return
        
        display_columns = [
            '開始時刻', 'ゲーム数', 'レシーブの種類', '失点の内容'
        ]

        def format_youtube_link_for_html(row):
            return f"<a href='{row['YouTubeリンク']}' target='_blank'>{row['開始時刻']}</a>"

        html_display_df = filtered_df[display_columns + ['YouTubeリンク']].copy()
        
        if 'YouTubeリンク' in filtered_df.columns:
            html_display_df['開始時刻'] = html_display_df.apply(format_youtube_link_for_html, axis=1)
            html_display_df = html_display_df.drop(columns='YouTubeリンク')
        
        st.markdown(
            html_display_df.to_html(escape=False, classes='dataframe table-striped'),
            unsafe_allow_html=True
        )
        st.info('この表は、自分のレシーブで失点した時の各パターンを表示しています。')

def get_recieve_loss_pattern_for_ai(df):
    """
    自分のレシーブで失点したパターンを抽出し、AIに渡すためのMarkdown文字列を生成する
    
    Args:
        df (pd.DataFrame): 試合の得失点データ
        
    Returns:
        str: レシーブ時の失点パターン文字列
    """
    required_columns = ['開始時刻', '得失点の種類', 'ゲーム数', '誰のサーブか', '得点者', 
                        'レシーブの種類', '失点の内容', 'YouTubeリンク']

    if df.empty or not all(col in df.columns for col in required_columns):
        return "レシーブ時の失点パターンデータが利用できません。"

    try:
        df['ゲーム数'] = pd.to_numeric(df['ゲーム数'], errors='coerce')
        df = df.dropna(subset=['ゲーム数'])
        df['ゲーム数'] = df['ゲーム数'].astype(int)
    except Exception:
        return "レシーブ時の失点パターンデータ生成中にエラーが発生しました。"

    # 関連する列の空白を除去
    df_temp = df.copy()
    df_temp['誰のサーブか'] = df_temp['誰のサーブか'].astype(str).str.strip()
    df_temp['得点者'] = df_temp['得点者'].astype(str).str.strip()
    df_temp['レシーブの種類'] = df_temp['レシーブの種類'].astype(str).str.strip()
    df_temp['失点の内容'] = df_temp['失点の内容'].astype(str).str.strip()

    loss_types = ['相手のプレーで失点', '自分のミスで失点', '失点（判断迷う）']

    filtered_df = df_temp[
        (df_temp['誰のサーブか'] == '相手') &
        (df_temp['得点者'] == '相手') &
        (df_temp['得失点の種類'].isin(loss_types)) &
        (df_temp['失点の内容'].astype(str).str.strip().str.lower() != 'nan') &
        (df_temp['失点の内容'].astype(str).str.strip() != '') &
        (df_temp['失点の内容'].notna())
    ].copy()

    if filtered_df.empty:
        return "自分のレシーブで失点したパターンは見つかりませんでした。"
    
    # AIに渡すための列を選択
    columns_for_ai = [
        'ゲーム数', 'レシーブの種類', '失点の内容'
    ]
    
    # Markdown形式に変換
    pattern_markdown = filtered_df[columns_for_ai].to_markdown(index=False)
    
    return f"## 自分のレシーブでの失点パターン一覧\n\n{pattern_markdown}"
