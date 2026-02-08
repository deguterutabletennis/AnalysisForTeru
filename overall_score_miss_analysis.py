import streamlit as st
import pandas as pd
import plotly.express as px

def display_overall_score_miss_analysis(df):
    """
    全ゲーム合計の得点・失点の種類別集計をStreamlitのUIに表示する関数
    
    Args:
        df (pd.DataFrame): 試合の得失点データ
    """
    st.write("---")
    st.subheader("全ゲーム合計 得点・失点の種類別集計（円グラフ）")
    
    required_columns = ['ゲーム数', '得点の種類', '失点の種類', '開始時刻', '得点の内容', '失点の内容', 'YouTubeリンク', '得失点の種類']
    if not df.empty and all(col in df.columns for col in required_columns):
    
        try:
            df['ゲーム数'] = pd.to_numeric(df['ゲーム数'], errors='coerce')
            df = df.dropna(subset=['ゲーム数'])
            df['ゲーム数'] = df['ゲーム数'].astype(int)
        except Exception as e:
            st.error(f"「ゲーム数」列の型変換中にエラーが発生しました。データ形式を確認してください: {e}")
            return
            
        total_score_counts = df['得点の種類'].value_counts().to_dict()
        total_score_counts = {k: v for k, v in total_score_counts.items() if k and pd.notna(k)}
        
        df_filtered_misses = df[df['得失点の種類'].isin(['自分のミスで失点', '失点（判断迷う）'])]
        total_miss_counts = df_filtered_misses['失点の種類'].value_counts().to_dict()
        total_miss_counts = {k: v for k, v in total_miss_counts.items() if k and pd.notna(k)}
        
        chart_data_rows = []
        if total_score_counts:
            for score_type, count in sorted(total_score_counts.items(), key=lambda item: item[1], reverse=True):
                chart_data_rows.append({'種別': '得点', '種類': score_type, '数': count})
        else:
            chart_data_rows.append({'種別': '得点', '種類': '（なし）', '数': 0})
        
        if total_miss_counts:
            for miss_type, count in sorted(total_miss_counts.items(), key=lambda item: item[1], reverse=True):
                chart_data_rows.append({'種別': 'ミス', '種類': miss_type, '数': count})
        else:
            chart_data_rows.append({'種別': 'ミス', '種類': '（なし）', '数': 0})
        
        chart_df = pd.DataFrame(chart_data_rows)
        
        df_scores = chart_df[chart_df['種別'] == '得点'].copy()
        if not df_scores.empty and df_scores['数'].sum() > 0:
            fig_pie_score = px.pie(
                df_scores, 
                values='数', 
                names='種類', 
                title='得点種類の割合',
                hole=0.3,
                category_orders={'種類': df_scores['種類'].tolist()}
            )
            fig_pie_score.update_traces(
                textinfo='label+value',
                textposition='inside',
                hovertemplate="<b>%{label}</b><br>件数: %{value}件<br>割合: %{percent}<extra></extra>"
            )
            st.plotly_chart(fig_pie_score, use_container_width=True)
        else:
            st.info("得点に関するデータがありません (全ゲーム合計)")
        
        st.subheader('得点種類の詳細')
        if not df_scores.empty and df_scores['数'].sum() > 0:
            for score_type in df_scores['種類'].tolist():
                with st.expander(f"得点: **{score_type}**"):
                    filtered_df_scores = df[df['得点の種類'] == score_type].copy()
                    
                    if not filtered_df_scores.empty:
                        st.markdown(f"##### 詳細 ({len(filtered_df_scores)}件)")
                        
                        def format_youtube_link(row):
                            if pd.notna(row['YouTubeリンク']):
                                return f"<a href='{row['YouTubeリンク']}' target='_blank'>{row['開始時刻']}</a>"
                            return row['開始時刻']
                        
                        display_df_scores = filtered_df_scores[['開始時刻', '得点の内容', 'YouTubeリンク']].copy()
                        display_df_scores['開始時刻'] = display_df_scores.apply(format_youtube_link, axis=1)
                        display_df_scores = display_df_scores.drop(columns='YouTubeリンク')

                        st.markdown(
                            display_df_scores.to_html(
                                index=False,
                                escape=False,
                                classes='dataframe table-striped'
                            ),
                            unsafe_allow_html=True
                        )
                    else:
                        st.info(f"'{score_type}'に関するデータは見つかりませんでした。")
        
        st.markdown("---")
        
        df_misses = chart_df[chart_df['種別'] == 'ミス'].copy()
        if not df_misses.empty and df_misses['数'].sum() > 0:
            fig_pie_miss = px.pie(
                df_misses, 
                values='数', 
                names='種類', 
                title='ミス種類の割合',
                hole=0.3,
                category_orders={'種類': df_misses['種類'].tolist()}
            )
            fig_pie_miss.update_traces(
                textinfo='label+value',
                textposition='inside',
                hovertemplate="<b>%{label}</b><br>件数: %{value}件<br>割合: %{percent}<extra></extra>"
            )
            st.plotly_chart(fig_pie_miss, use_container_width=True)
        else:
            st.info("ミスに関するデータがありません (全ゲーム合計)")

        st.subheader('ミス種類の詳細')
        if not df_misses.empty and df_misses['数'].sum() > 0:
            for miss_type in df_misses['種類'].tolist():
                with st.expander(f"ミス: **{miss_type}**"):
                    filtered_df_misses = df[df['失点の種類'] == miss_type].copy()
                    
                    if not filtered_df_misses.empty:
                        st.markdown(f"##### 詳細 ({len(filtered_df_misses)}件)")

                        def format_youtube_link(row):
                            if pd.notna(row['YouTubeリンク']):
                                return f"<a href='{row['YouTubeリンク']}' target='_blank'>{row['開始時刻']}</a>"
                            return row['開始時刻']

                        display_df_misses = filtered_df_misses[['開始時刻', '失点の内容', 'YouTubeリンク']].copy()
                        display_df_misses['開始時刻'] = display_df_misses.apply(format_youtube_link, axis=1)
                        display_df_misses = display_df_misses.drop(columns='YouTubeリンク')
                        
                        st.markdown(
                            display_df_misses.to_html(
                                index=False,
                                escape=False,
                                classes='dataframe table-striped'
                            ),
                            unsafe_allow_html=True
                        )
                    else:
                        st.info(f"'{miss_type}'に関するデータは見つかりませんでした。")
                        
    else:
        st.warning('スプレッドシートの読み込みに失敗したか、必要な列が見つかりませんでした。')

def get_overall_score_miss_analysis_for_ai(df):
    """
    全ゲーム合計の得点・失点の種類別集計をAIに渡すためのMarkdown文字列を生成する
    
    Args:
        df (pd.DataFrame): 試合の得失点データ
        
    Returns:
        str: 分析結果の文字列
    """
    required_columns = ['ゲーム数', '得点の種類', '失点の種類', '開始時刻', '得点の内容', '失点の内容', 'YouTubeリンク', '得失点の種類']
    
    if df.empty or not all(col in df.columns for col in required_columns):
        return "得点・失点の種類別集計データが利用できません。"
    
    # 'ゲーム数' 列の型変換
    try:
        df['ゲーム数'] = pd.to_numeric(df['ゲーム数'], errors='coerce')
        df = df.dropna(subset=['ゲーム数'])
        df['ゲーム数'] = df['ゲーム数'].astype(int)
    except Exception:
        return "「ゲーム数」列の型変換中にエラーが発生しました。"

    # 全体の得点の種類をカウント
    total_score_counts = df['得点の種類'].value_counts().to_dict()
    total_score_counts = {k: v for k, v in total_score_counts.items() if k and pd.notna(k)}

    # '得失点の種類'が'自分のミスで失点'と'失点（判断迷う）'のみに絞り込む
    df_filtered_misses = df[df['得失点の種類'].isin(['自分のミスで失点', '失点（判断迷う）'])]
    total_miss_counts = df_filtered_misses['失点の種類'].value_counts().to_dict()
    total_miss_counts = {k: v for k, v in total_miss_counts.items() if k and pd.notna(k)}

    analysis_text = "## 全ゲーム合計 得点・失点の種類別集計\n\n"

    # 得点に関する分析結果を生成
    analysis_text += "### 得点種類の割合\n"
    if total_score_counts:
        total_scores = sum(total_score_counts.values())
        score_details = []
        for score_type, count in sorted(total_score_counts.items(), key=lambda item: item[1], reverse=True):
            rate = (count / total_scores) * 100
            score_details.append(f"- {score_type}: {count}回 ({rate:.1f}%)")
        analysis_text += "\n".join(score_details)
        analysis_text += "\n\n"

        analysis_text += "### 得点種類の詳細\n"
        for score_type in sorted(total_score_counts.keys()):
            filtered_df_scores = df[df['得点の種類'] == score_type].copy()
            if not filtered_df_scores.empty:
                analysis_text += f"#### 得点: {score_type}\n"
                analysis_text += filtered_df_scores[['開始時刻', '得点の内容']].to_markdown(index=False)
                analysis_text += "\n\n"
    else:
        analysis_text += "得点に関するデータがありません。\n\n"
        
    analysis_text += "---\n\n"

    # ミスに関する分析結果を生成
    analysis_text += "### ミス種類の割合\n"
    if total_miss_counts:
        total_misses = sum(total_miss_counts.values())
        miss_details = []
        for miss_type, count in sorted(total_miss_counts.items(), key=lambda item: item[1], reverse=True):
            rate = (count / total_misses) * 100
            miss_details.append(f"- {miss_type}: {count}回 ({rate:.1f}%)")
        analysis_text += "\n".join(miss_details)
        analysis_text += "\n\n"

        analysis_text += "### ミス種類の詳細\n"
        for miss_type in sorted(total_miss_counts.keys()):
            filtered_df_misses = df_filtered_misses[df_filtered_misses['失点の種類'] == miss_type].copy()
            if not filtered_df_misses.empty:
                analysis_text += f"#### ミス: {miss_type}\n"
                analysis_text += filtered_df_misses[['開始時刻', '失点の内容']].to_markdown(index=False)
                analysis_text += "\n\n"
    else:
        analysis_text += "ミスに関するデータがありません。\n\n"
        
    return analysis_text
