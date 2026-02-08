import streamlit as st

def display_match_data(df):
    """
    試合データ一覧をStreamlitのUIに表示する関数
    
    Args:
        df (pd.DataFrame): 試合の得失点データ
    """
    if df.empty:
        st.warning('スプレッドシートの読み込みに失敗したか、データが空です。')
        return

    with st.expander("📊 試合データ一覧"):
        # 表示するカラムを選択
        columns_to_display = [
            '開始時刻', 'ゲーム数', '自分の得点', '相手の得点', '得点者', 'コメント・課題'
        ]
        
        # 必要な列がすべて存在するか再確認
        missing_cols_for_display = [col for col in columns_to_display if col not in df.columns]
        if 'YouTubeリンク' not in df.columns:
            missing_cols_for_display.append('YouTubeリンク')
        
        if missing_cols_for_display:
            st.warning(f"データ一覧の表示に必要な以下の列が見つかりませんでした: {', '.join(missing_cols_for_display)}")
            return
        
        # 選択したカラムのみを新しいDataFrameとして表示
        display_df = df[columns_to_display].copy()

        # '開始時刻'をYouTubeリンクとしてHTMLフォーマットする関数
        def format_youtube_link_for_html(row):
            return f"<a href='{row['YouTubeリンク']}' target='_blank'>{row['開始時刻']}</a>"

        # HTMLコンテンツとして表示するためのDataFrameを準備
        html_display_df = display_df.copy()
        
        # 'YouTubeリンク'列が存在する場合のみ適用
        if 'YouTubeリンク' in df.columns:
            html_display_df['開始時刻'] = df.apply(format_youtube_link_for_html, axis=1)
        
        # StreamlitでHTMLテーブルを表示
        st.markdown(
            html_display_df.to_html(escape=False, classes='dataframe table-striped'),
            unsafe_allow_html=True
        )
        st.info('「開始時刻」をクリックするとYouTube動画の該当箇所へジャンプします。')

def get_match_data_for_ai(df):
    """
    試合データ一覧をAIに渡すためのMarkdown文字列を生成する
    
    Args:
        df (pd.DataFrame): 試合の得失点データ
        
    Returns:
        str: 試合データ一覧の文字列
    """
    if df.empty:
        return "試合データ一覧が利用できません。"
    
    # AIに渡すための列を選択
    columns_to_display = [
        'ゲーム数', '自分の得点', '相手の得点', '得失点の種類', '得点者', 'コメント・課題'
    ]
    
    # 必要な列がすべて存在するか確認
    missing_cols = [col for col in columns_to_display if col not in df.columns]
    if missing_cols:
        return f"試合データ一覧の表示に必要な以下の列が見つかりませんでした: {', '.join(missing_cols)}"

    # 選択したカラムのみを新しいDataFrameとして表示
    display_df = df[columns_to_display].copy()
    
    # Markdown形式に変換
    data_list_markdown = display_df.to_markdown(index=False)
    
    return f"## 試合データ一覧\n\n{data_list_markdown}"
