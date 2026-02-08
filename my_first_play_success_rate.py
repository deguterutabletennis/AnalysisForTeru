import streamlit as st
import pandas as pd

def display_my_first_play_success_rate(df):
    """
    自分が最初に仕掛けたプレーの成功率をStreamlitのUIに表示する関数
    
    Args:
        df (pd.DataFrame): 試合の得失点データ
    """
    st.write("---")
    st.subheader("自分が最初に仕掛けたプレーの成功率分析")

    required_cols = [
        '誰のサーブか', 'レシーブの種類', '３球目の種類', '４球目の種類', 
        '５球目の種類', '６球目の種類', 'レシーブの質', '３球目の質', 
        '４球目の質', '５球目の質', '６球目の質', '得失点の種類', '失点の内容', 
        '開始時刻', 'YouTubeリンク'
    ]

    if 'display_details' not in st.session_state:
        st.session_state.display_details = None
    
    if not df.empty and all(col in df.columns for col in required_cols):
        
        def analyze_my_first_play_success(row):
            who_serves = row['誰のサーブか']
            
            play_sequence = [
                ('レシーブの種類', 'レシーブの質', '相手' if who_serves == '自分' else '自分'),
                ('３球目の種類', '３球目の質', '自分' if who_serves == '自分' else '相手'),
                ('４球目の種類', '４球目の質', '相手' if who_serves == '自分' else '自分'),
                ('５球目の種類', '５球目の質', '自分' if who_serves == '自分' else '相手'),
                ('６球目の種類', '６球目の質', '相手' if who_serves == '自分' else '自分')
            ]
            
            for play_col, quality_col, player in play_sequence:
                if pd.notna(row[play_col]) and ('ドライブ' in str(row[play_col]) or 'チキータ' in str(row[play_col])):
                    if player == '自分':
                        is_successful = pd.notna(row[quality_col]) and 'ミス' not in str(row[quality_col])
                        
                        if 'フォアドライブ' in str(row[play_col]):
                            return 'フォアドライブ_成功' if is_successful else 'フォアドライブ_失敗'
                        elif 'バックドライブ' in str(row[play_col]):
                            return 'バックドライブ_成功' if is_successful else 'バックドライブ_失敗'
                        elif 'バックチキータ' in str(row[play_col]):
                            return 'バックチキータ_成功' if is_successful else 'バックチキータ_失敗'
                    else:
                        return 'その他'
            
            return 'その他'

        df_result = df.copy()
        df_result['自分が最初に仕掛けた結果'] = df_result.apply(analyze_my_first_play_success, axis=1)

        play_counts = df_result['自分が最初に仕掛けた結果'].value_counts()

        def format_youtube_link_for_html(row):
            return f"<a href='{row['YouTubeリンク']}' target='_blank'>{row['開始時刻']}</a>"

        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)

        # フォアドライブ
        fore_success = play_counts.get('フォアドライブ_成功', 0)
        fore_failure = play_counts.get('フォアドライブ_失敗', 0)
        fore_total = fore_success + fore_failure
        fore_rate = (fore_success / fore_total * 100) if fore_total > 0 else 0
        with col1:
            st.markdown("##### フォアドライブ")
            if fore_total > 0:
                st.metric(label="成功率", value=f"{fore_rate:.1f}%", delta=f"（成功: {fore_success}回, 失敗: {fore_failure}回）")
                if fore_failure > 0 and st.button("失敗の詳細", key="fore_drive_failure"):
                    st.session_state.display_details = 'fore_drive'
            else:
                st.info("データなし")

        # バックドライブ
        back_success = play_counts.get('バックドライブ_成功', 0)
        back_failure = play_counts.get('バックドライブ_失敗', 0)
        back_total = back_success + back_failure
        back_rate = (back_success / back_total * 100) if back_total > 0 else 0
        with col2:
            st.markdown("##### バックドライブ")
            if back_total > 0:
                st.metric(label="成功率", value=f"{back_rate:.1f}%", delta=f"（成功: {back_success}回, 失敗: {back_failure}回）")
                if back_failure > 0 and st.button("失敗の詳細", key="back_drive_failure"):
                    st.session_state.display_details = 'back_drive'
            else:
                st.info("データなし")

        # バックチキータ
        chiquita_success = play_counts.get('バックチキータ_成功', 0)
        chiquita_failure = play_counts.get('バックチキータ_失敗', 0)
        chiquita_total = chiquita_success + chiquita_failure
        chiquita_rate = (chiquita_success / chiquita_total * 100) if chiquita_total > 0 else 0
        with col3:
            st.markdown("##### バックチキータ")
            if chiquita_total > 0:
                st.metric(label="成功率", value=f"{chiquita_rate:.1f}%", delta=f"（成功: {chiquita_success}回, 失敗: {chiquita_failure}回）")
                if chiquita_failure > 0 and st.button("失敗の詳細", key="back_chiquita_failure"):
                    st.session_state.display_details = 'back_chiquita'
            else:
                st.info("データなし")

        # 詳細表示の処理
        if st.session_state.display_details:
            st.markdown("---")
            if st.session_state.display_details == 'fore_drive':
                st.markdown("##### フォアドライブ_失敗の詳細")
                filtered_df = df_result[df_result['自分が最初に仕掛けた結果'] == 'フォアドライブ_失敗']
                display_cols = ['開始時刻', '失点の種類', '失点の内容', 'YouTubeリンク']
                if all(col in filtered_df.columns for col in display_cols):
                    html_display_df = filtered_df[display_cols].copy()
                    html_display_df['開始時刻'] = html_display_df.apply(format_youtube_link_for_html, axis=1)
                    html_display_df = html_display_df.drop(columns='YouTubeリンク')
                    st.markdown(
                        html_display_df.to_html(escape=False, classes='dataframe table-striped'),
                        unsafe_allow_html=True
                    )
                else:
                    st.warning('「YouTubeリンク」または必要な列が見つかりませんでした。')
            
            elif st.session_state.display_details == 'back_drive':
                st.markdown("##### バックドライブ_失敗の詳細")
                filtered_df = df_result[df_result['自分が最初に仕掛けた結果'] == 'バックドライブ_失敗']
                display_cols = ['開始時刻', '失点の種類', '失点の内容', 'YouTubeリンク']
                if all(col in filtered_df.columns for col in display_cols):
                    html_display_df = filtered_df[display_cols].copy()
                    html_display_df['開始時刻'] = html_display_df.apply(format_youtube_link_for_html, axis=1)
                    html_display_df = html_display_df.drop(columns='YouTubeリンク')
                    st.markdown(
                        html_display_df.to_html(escape=False, classes='dataframe table-striped'),
                        unsafe_allow_html=True
                    )
                else:
                    st.warning('「YouTubeリンク」または必要な列が見つかりませんでした。')

            elif st.session_state.display_details == 'back_chiquita':
                st.markdown("##### バックチキータ_失敗の詳細")
                filtered_df = df_result[df_result['自分が最初に仕掛けた結果'] == 'バックチキータ_失敗']
                display_cols = ['開始時刻', '失点の種類', '失点の内容', 'YouTubeリンク']
                if all(col in filtered_df.columns for col in display_cols):
                    html_display_df = filtered_df[display_cols].copy()
                    html_display_df['開始時刻'] = html_display_df.apply(format_youtube_link_for_html, axis=1)
                    html_display_df = html_display_df.drop(columns='YouTubeリンク')
                    st.markdown(
                        html_display_df.to_html(escape=False, classes='dataframe table-striped'),
                        unsafe_allow_html=True
                    )
                else:
                    st.warning('「YouTubeリンク」または必要な列が見つかりませんでした。')
    
    else:
        st.warning("この分析に必要な列が見つかりませんでした。")

def get_my_first_play_success_rate_for_ai(df):
    """
    自分が最初に仕掛けたプレーの成功率分析結果をAIに渡すためのMarkdown文字列を生成する
    
    Args:
        df (pd.DataFrame): 試合の得失点データ
        
    Returns:
        str: 分析結果の文字列
    """
    required_cols = [
        '誰のサーブか', 'レシーブの種類', '３球目の種類', '４球目の種類', 
        '５球目の種類', '６球目の種類', 'レシーブの質', '３球目の質', 
        '４球目の質', '５球目の質', '６球目の質', '得失点の種類', '失点の内容', 
        '開始時刻', 'YouTubeリンク'
    ]

    if df.empty or not all(col in df.columns for col in required_cols):
        return "自分が最初に仕掛けたプレーの成功率分析データが利用できません。"

    def analyze_my_first_play_success(row):
        who_serves = row['誰のサーブか']
        
        play_sequence = [
            ('レシーブの種類', 'レシーブの質', '相手' if who_serves == '自分' else '自分'),
            ('３球目の種類', '３球目の質', '自分' if who_serves == '自分' else '相手'),
            ('４球目の種類', '４球目の質', '相手' if who_serves == '自分' else '自分'),
            ('５球目の種類', '５球目の質', '自分' if who_serves == '自分' else '相手'),
            ('６球目の種類', '６球目の質', '相手' if who_serves == '自分' else '自分')
        ]
        
        for play_col, quality_col, player in play_sequence:
            if pd.notna(row[play_col]) and ('ドライブ' in str(row[play_col]) or 'チキータ' in str(row[play_col])):
                if player == '自分':
                    is_successful = pd.notna(row[quality_col]) and 'ミス' not in str(row[quality_col])
                    if 'フォアドライブ' in str(row[play_col]):
                        return 'フォアドライブ_成功' if is_successful else 'フォアドライブ_失敗'
                    elif 'バックドライブ' in str(row[play_col]):
                        return 'バックドライブ_成功' if is_successful else 'バックドライブ_失敗'
                    elif 'バックチキータ' in str(row[play_col]):
                        return 'バックチキータ_成功' if is_successful else 'バックチキータ_失敗'
                else:
                    return 'その他'
        
        return 'その他'

    df_result = df.copy()
    df_result['自分が最初に仕掛けた結果'] = df_result.apply(analyze_my_first_play_success, axis=1)

    play_counts = df_result['自分が最初に仕掛けた結果'].value_counts()
    
    summary_text = "## 自分が最初に仕掛けたプレーの成功率分析\n\n"

    # フォアドライブ
    fore_success = play_counts.get('フォアドライブ_成功', 0)
    fore_failure = play_counts.get('フォアドライブ_失敗', 0)
    fore_total = fore_success + fore_failure
    fore_rate = (fore_success / fore_total) if fore_total > 0 else 0
    if fore_total > 0:
        summary_text += f"### フォアドライブ\n"
        summary_text += f"・成功率: {fore_rate:.1%} (成功: {fore_success}回, 失敗: {fore_failure}回)\n"
        if fore_failure > 0:
            summary_text += f"以下の詳細データは失敗したラリーです。\n"
            filtered_df = df_result[df_result['自分が最初に仕掛けた結果'] == 'フォアドライブ_失敗']
            if not filtered_df.empty:
                summary_text += filtered_df[['開始時刻', '失点の種類', '失点の内容']].to_markdown(index=False)
            summary_text += "\n\n"

    # バックドライブ
    back_success = play_counts.get('バックドライブ_成功', 0)
    back_failure = play_counts.get('バックドライブ_失敗', 0)
    back_total = back_success + back_failure
    back_rate = (back_success / back_total) if back_total > 0 else 0
    if back_total > 0:
        summary_text += f"### バックドライブ\n"
        summary_text += f"・成功率: {back_rate:.1%} (成功: {back_success}回, 失敗: {back_failure}回)\n"
        if back_failure > 0:
            summary_text += f"以下の詳細データは失敗したラリーです。\n"
            filtered_df = df_result[df_result['自分が最初に仕掛けた結果'] == 'バックドライブ_失敗']
            if not filtered_df.empty:
                summary_text += filtered_df[['開始時刻', '失点の種類', '失点の内容']].to_markdown(index=False)
            summary_text += "\n\n"

    # バックチキータ
    chiquita_success = play_counts.get('バックチキータ_成功', 0)
    chiquita_failure = play_counts.get('バックチキータ_失敗', 0)
    chiquita_total = chiquita_success + chiquita_failure
    chiquita_rate = (chiquita_success / chiquita_total) if chiquita_total > 0 else 0
    if chiquita_total > 0:
        summary_text += f"### バックチキータ\n"
        summary_text += f"・成功率: {chiquita_rate:.1%} (成功: {chiquita_success}回, 失敗: {chiquita_failure}回)\n"
        if chiquita_failure > 0:
            summary_text += f"以下の詳細データは失敗したラリーです。\n"
            filtered_df = df_result[df_result['自分が最初に仕掛けた結果'] == 'バックチキータ_失敗']
            if not filtered_df.empty:
                summary_text += filtered_df[['開始時刻', '失点の種類', '失点の内容']].to_markdown(index=False)
            summary_text += "\n\n"

    return summary_text

