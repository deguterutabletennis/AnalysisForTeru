import streamlit as st
import pandas as pd

def display_first_drive_analysis(df):
    """
    どちらが先にドライブを仕掛けたかの分析結果をStreamlitのUIに表示する関数
    
    Args:
        df (pd.DataFrame): 試合の得失点データ
    """
    st.subheader("どちらが先にドライブを仕掛けたか分析")
    
    required_drive_first_cols = ['誰のサーブか', 'レシーブの種類', '３球目の種類', '４球目の種類', '５球目の種類', '６球目の種類', '得点者']
    if not df.empty and all(col in df.columns for col in required_drive_first_cols):
        
        total_rallies = len(df)
        if total_rallies > 0:
            df_rally = df.copy()

            def analyze_first_drive(row):
                who_serves = row['誰のサーブか']
                play_sequence = [
                    ('レシーブの種類', '相手' if who_serves == '自分' else '自分'),
                    ('３球目の種類', '自分' if who_serves == '自分' else '相手'),
                    ('４球目の種類', '相手' if who_serves == '自分' else '自分'),
                    ('５球目の種類', '自分' if who_serves == '自分' else '相手'),
                    ('６球目の種類', '相手' if who_serves == '自分' else '自分')
                ]
                
                for column, player in play_sequence:
                    if pd.notna(row[column]) and ('ドライブ' in str(row[column]) or 'チキータ' in str(row[column])):
                        return player
                
                return '仕掛けなし'

            df_rally['先に仕掛けたプレーヤー'] = df_rally.apply(analyze_first_drive, axis=1)

            result_counts = df_rally['先に仕掛けたプレーヤー'].value_counts()
            
            my_first_drive_count = result_counts.get('自分', 0)
            opponent_first_drive_count = result_counts.get('相手', 0)
            no_drive_count = result_counts.get('仕掛けなし', 0)
            
            my_first_drive_rate = (my_first_drive_count / total_rallies * 100) if total_rallies > 0 else 0
            opponent_first_drive_rate = (opponent_first_drive_count / total_rallies * 100) if total_rallies > 0 else 0
            
            st.markdown(f"全ラリー数: **{total_rallies}回**")
            st.info("※「ドライブ」または「チキータ」をラリー中に最初に仕掛けた回数をカウントしています。")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    label="自分が先に仕掛けた",
                    value=f"{my_first_drive_rate:.1f}%",
                    delta=f"（回数: {my_first_drive_count}回）"
                )
            
            with col2:
                st.metric(
                    label="相手が先に仕掛けた",
                    value=f"{opponent_first_drive_rate:.1f}%",
                    delta=f"（回数: {opponent_first_drive_count}回）"
                )
                
            with col3:
                st.metric(
                    label="仕掛けなし",
                    value=f"{(no_drive_count / total_rallies * 100):.1f}%",
                    delta=f"（回数: {no_drive_count}回）"
                )
            
            st.markdown("---")
            
            st.markdown("#### 分類ごとの得点結果")
            
            crosstab_count = pd.crosstab(df_rally['先に仕掛けたプレーヤー'], df_rally['得点者']).rename_axis(None)
            crosstab_rate = pd.crosstab(df_rally['先に仕掛けたプレーヤー'], df_rally['得点者'], normalize='index').rename_axis(None)
            
            crosstab_count.loc['Total'] = crosstab_count.sum()
            crosstab_rate.loc['Total'] = crosstab_count.loc['Total'] / crosstab_count.loc['Total'].sum()

            if '自分' in crosstab_count.columns and '相手' in crosstab_count.columns:
                crosstab_count = crosstab_count[['自分', '相手']]
                crosstab_rate = crosstab_rate[['自分', '相手']]
            
            combined_df = pd.DataFrame(index=crosstab_count.index, columns=crosstab_count.columns)
            
            for col in combined_df.columns:
                combined_df[col] = crosstab_count[col].astype(str) + ' (' + crosstab_rate[col].apply(lambda x: f'{x:.1%}') + ')'
            
            combined_df = combined_df.rename(index={'相手': '相手が先に仕掛けた', '自分': '自分が先に仕掛けた', 'Total': '合計', '仕掛けなし': '仕掛けなし'})
            combined_df = combined_df.rename(columns={'自分': '自分の得点', '相手': '相手の得点'})

            st.dataframe(combined_df)
            st.caption("※（）内は、それぞれの分類（行）における得点者の割合を示しています。")

        else:
            st.info("分析対象のラリーデータがありません。")

    else:
        st.warning("この分析に必要な列「誰のサーブか」「レシーブの種類」「３球目の種類」「４球目の種類」「５球目の種類」「６球目の種類」「得点者」が見つかりませんでした。")


def get_first_drive_analysis_for_ai(df):
    """
    どちらが先にドライブを仕掛けたかの分析結果をAIに渡すためのMarkdown文字列を生成する
    
    Args:
        df (pd.DataFrame): 試合の得失点データ
        
    Returns:
        str: 分析結果の文字列
    """
    required_drive_first_cols = ['誰のサーブか', 'レシーブの種類', '３球目の種類', '４球目の種類', '５球目の種類', '６球目の種類', '得点者']
    
    if df.empty or not all(col in df.columns for col in required_drive_first_cols):
        return "先にドライブを仕掛けたかの分析データが利用できません。"
    
    total_rallies = len(df)
    if total_rallies == 0:
        return "分析対象のラリーデータがありません。"

    df_rally = df.copy()

    # ラリーの球数ごとに、どちらがドライブを仕掛けたかを判定する関数
    def analyze_first_drive(row):
        who_serves = row['誰のサーブか']
        play_sequence = [
            ('レシーブの種類', '相手' if who_serves == '自分' else '自分'),
            ('３球目の種類', '自分' if who_serves == '自分' else '相手'),
            ('４球目の種類', '相手' if who_serves == '自分' else '自分'),
            ('５球目の種類', '自分' if who_serves == '自分' else '相手'),
            ('６球目の種類', '相手' if who_serves == '自分' else '自分')
        ]
        
        for column, player in play_sequence:
            if pd.notna(row[column]) and ('ドライブ' in str(row[column]) or 'チキータ' in str(row[column])):
                return player
        
        return '仕掛けなし'

    df_rally['先に仕掛けたプレーヤー'] = df_rally.apply(analyze_first_drive, axis=1)
    result_counts = df_rally['先に仕掛けたプレーヤー'].value_counts()
    
    my_first_drive_count = result_counts.get('自分', 0)
    opponent_first_drive_count = result_counts.get('相手', 0)
    no_drive_count = result_counts.get('仕掛けなし', 0)
    
    my_first_drive_rate = (my_first_drive_count / total_rallies) if total_rallies > 0 else 0
    opponent_first_drive_rate = (opponent_first_drive_count / total_rallies) if total_rallies > 0 else 0
    
    # AI向けサマリー文字列を生成
    summary_text = f"## どちらが先にドライブを仕掛けたか分析\n"
    summary_text += f"全ラリー数: {total_rallies}回\n"
    summary_text += f"・自分が先に仕掛けた: {my_first_drive_count}回 ({my_first_drive_rate:.1%})\n"
    summary_text += f"・相手が先に仕掛けた: {opponent_first_drive_count}回 ({opponent_first_drive_rate:.1%})\n"
    summary_text += f"・仕掛けなし: {no_drive_count}回 ({(no_drive_count / total_rallies):.1%})\n\n"
    
    # 分類ごとの得点結果
    crosstab_count = pd.crosstab(df_rally['先に仕掛けたプレーヤー'], df_rally['得点者']).rename_axis(None)
    crosstab_rate = pd.crosstab(df_rally['先に仕掛けたプレーヤー'], df_rally['得点者'], normalize='index').rename_axis(None)
    
    if '自分' in crosstab_count.columns and '相手' in crosstab_count.columns:
        crosstab_count = crosstab_count[['自分', '相手']]
        crosstab_rate = crosstab_rate[['自分', '相手']]
    
    combined_df = pd.DataFrame(index=crosstab_count.index, columns=crosstab_count.columns)
    for col in combined_df.columns:
        combined_df[col] = crosstab_count[col].astype(str) + ' (' + crosstab_rate[col].apply(lambda x: f'{x:.1%}') + ')'
    
    combined_df = combined_df.rename(index={'相手': '相手が先に仕掛けた', '自分': '自分が先に仕掛けた', '仕掛けなし': '仕掛けなし'})
    combined_df = combined_df.rename(columns={'自分': '自分の得点', '相手': '相手の得点'})

    summary_text += f"### 分類ごとの得点結果 (得点数と得点率)\n"
    summary_text += combined_df.to_markdown()
    
    return summary_text


