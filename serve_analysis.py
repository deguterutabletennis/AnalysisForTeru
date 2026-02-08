import streamlit as st
import pandas as pd

def display_serve_analysis(df):
    """
    サーブ種類別の得点・失点内容分析をStreamlitのUIに表示する関数
    
    Args:
        df (pd.DataFrame): 試合の得失点データ
    """
    st.write("---")
    st.subheader("サーブ種類別の得点・失点内容分析")

    df_my_serve = df[df['誰のサーブか'] == '自分'].copy()

    required_columns = ['誰のサーブか', 'サーブの種類', '得点者', '得点の種類', '得点の内容', '失点の種類', '失点の内容', 'サーブのコース']
    if not df.empty and all(col in df.columns for col in required_columns):
        if not df_my_serve.empty:
            serve_groups = {
                'YGサーブ': ['YGサーブ', 'YGサーブ下', 'YGサーブ上'],
                '巻込み': ['巻込み', '巻込み上', '巻込み下'],
                '順横': ['順横', '順横上', '順横下'],
                'バック': ['バック', 'バック上', 'バック下'],
                'キックサーブ': ['キックサーブ'],
            }
            
            existing_serve_types = df_my_serve['サーブの種類'].astype(str).str.strip().unique()
            
            available_groups = {}
            all_grouped_types = []
            for group_name, types in serve_groups.items():
                if any(t in existing_serve_types for t in types):
                    available_groups[group_name] = types
                    all_grouped_types.extend(types)
            
            other_serves = sorted(list(set(existing_serve_types) - set(all_grouped_types)))
            if other_serves:
                available_groups['その他'] = other_serves
            
            group_options = list(available_groups.keys())
            
            if not group_options:
                st.warning("データに有効なサーブの種類が見つかりませんでした。")
                return
                
            selected_group = st.selectbox("分析したいサーブのグループを選択してください:", group_options)
            
            selected_serve_types = available_groups.get(selected_group, [])
            df_filtered_by_serve = df_my_serve[df_my_serve['サーブの種類'].isin(selected_serve_types)]

            if not df_filtered_by_serve.empty:
                valid_courses = df_filtered_by_serve['サーブのコース'].dropna().unique()
                valid_courses = [c for c in valid_courses if c is not None and c == c]
                course_options = ['すべて'] + sorted(list(valid_courses))
                selected_course = st.selectbox("分析したいコースを選択してください:", course_options)
            else:
                st.warning("選択されたサーブのグループのデータが見つかりませんでした。")
                return

            df_filtered = df_filtered_by_serve.copy()
            if selected_course != 'すべて':
                df_filtered = df_filtered[df_filtered['サーブのコース'] == selected_course]
            
            display_title = f"『{selected_group}』"
            if selected_course != 'すべて':
                display_title += f"（コース: {selected_course}）"

            if not df_filtered.empty:
                # --- 得点内容の表示 ---
                st.markdown(f"#### 得点の内容")
                df_points = df_filtered[df_filtered['得点者'] == '自分']
                if not df_points.empty:
                    with st.expander(f"得点 ({len(df_points)}回) の詳細を見る"):
                        display_columns = ['開始時刻', '得点の種類', '得点の内容']
                        html_display_df = df_points[display_columns + ['YouTubeリンク']].copy()

                        def format_youtube_link_for_html(row):
                            if 'YouTubeリンク' in row and pd.notna(row['YouTubeリンク']):
                                return f"<a href='{row['YouTubeリンク']}' target='_blank'>{row['開始時刻']}</a>"
                            return row['開始時刻']

                        if 'YouTubeリンク' in df_points.columns:
                            html_display_df['開始時刻'] = html_display_df.apply(format_youtube_link_for_html, axis=1)
                            html_display_df = html_display_df.drop(columns='YouTubeリンク')

                        st.markdown(
                            html_display_df.to_html(
                                index=False, 
                                escape=False,
                                classes='dataframe table-striped'
                            ),
                            unsafe_allow_html=True
                        )
                else:
                    st.info(f"{display_title} で得点したデータはありません。")

                # --- 失点内容の表示 ---
                st.markdown(f"#### 失点の内容")
                df_misses = df_filtered[df_filtered['得点者'] == '相手']
                if not df_misses.empty:
                    with st.expander(f"失点 ({len(df_misses)}回) の詳細を見る"):
                        display_columns = ['開始時刻', '失点の種類', '失点の内容']
                        html_display_df = df_misses[display_columns + ['YouTubeリンク']].copy()

                        def format_youtube_link_for_html(row):
                            if 'YouTubeリンク' in row and pd.notna(row['YouTubeリンク']):
                                return f"<a href='{row['YouTubeリンク']}' target='_blank'>{row['開始時刻']}</a>"
                            return row['開始時刻']
                        
                        if 'YouTubeリンク' in df_misses.columns:
                            html_display_df['開始時刻'] = html_display_df.apply(format_youtube_link_for_html, axis=1)
                            html_display_df = html_display_df.drop(columns='YouTubeリンク')

                        st.markdown(
                            html_display_df.to_html(
                                index=False,
                                escape=False,
                                classes='dataframe table-striped'
                            ),
                            unsafe_allow_html=True
                        )
                else:
                    st.info(f"{display_title} で失点したデータはありません。")
            else:
                st.warning("選択されたサーブのグループとコースの組み合わせのデータが見つかりませんでした。")
        else:
            st.warning("「誰のサーブか」が「自分」となっているデータが見つかりません。")
    else:
        st.warning('スプレッドシートの読み込みに失敗したか、必要な列が見つかりませんでした。')

def get_serve_analysis_for_ai(df):
    """
    自分のサーブ種類別の得点・失点内容分析結果をAIに渡すためのMarkdown文字列を生成する
    
    Args:
        df (pd.DataFrame): 試合の得失点データ
        
    Returns:
        str: 分析結果のMarkdown文字列
    """
    df_my_serve = df[df['誰のサーブか'] == '自分'].copy()

    required_columns = ['誰のサーブか', 'サーブの種類', '得点者', '得点の種類', '得点の内容', '失点の種類', '失点の内容', 'サーブのコース']
    if df.empty or not all(col in df.columns for col in required_columns):
        return "サーブ種類別の得点・失点内容分析データが利用できません。"

    if df_my_serve.empty:
        return "「誰のサーブか」が「自分」となっているデータが見つかりません。"

    serve_groups = {
        'YGサーブ': ['YGサーブ', 'YGサーブ下', 'YGサーブ上'],
        '巻込み': ['巻込み', '巻込み上', '巻込み下'],
        '順横': ['順横', '順横上', '順横下'],
        'バック': ['バック', 'バック上', 'バック下'],
        'キックサーブ': ['キックサーブ'],
    }
    
    existing_serve_types = df_my_serve['サーブの種類'].astype(str).str.strip().unique()
    available_groups = {}
    all_grouped_types = []
    for group_name, types in serve_groups.items():
        if any(t in existing_serve_types for t in types):
            available_groups[group_name] = types
            all_grouped_types.extend(types)
    
    other_serves = sorted(list(set(existing_serve_types) - set(all_grouped_types)))
    if other_serves:
        available_groups['その他'] = other_serves
        
    if not available_groups:
        return "データに有効なサーブの種類が見つかりませんでした。"
    
    analysis_text = "## サーブ種類別の得点・失点内容分析\n\n"

    for group_name, types in available_groups.items():
        df_group = df_my_serve[df_my_serve['サーブの種類'].isin(types)]
        
        valid_courses = sorted(list(df_group['サーブのコース'].dropna().unique()))
        
        for course in ['すべて'] + valid_courses:
            df_filtered = df_group.copy()
            if course != 'すべて':
                df_filtered = df_filtered[df_filtered['サーブのコース'] == course]

            if df_filtered.empty:
                continue

            display_title = f"### サーブグループ: {group_name}"
            if course != 'すべて':
                display_title += f" (コース: {course})"
            
            analysis_text += f"{display_title}\n\n"

            df_points = df_filtered[df_filtered['得点者'] == '自分']
            if not df_points.empty:
                analysis_text += f"#### 得点内容 (合計 {len(df_points)}回)\n"
                # 得点の種類ごとの集計と詳細
                point_summary = df_points['得点の種類'].value_counts().to_markdown()
                analysis_text += point_summary + "\n\n"
                
                # 詳細のMarkdownテーブルを生成
                points_details = df_points[['開始時刻', '得点の種類', '得点の内容']]
                analysis_text += "##### 詳細リスト\n"
                analysis_text += points_details.to_markdown(index=False) + "\n\n"
            else:
                analysis_text += "#### 得点内容\n"
                analysis_text += "得点したデータはありません。\n\n"

            df_misses = df_filtered[df_filtered['得点者'] == '相手']
            if not df_misses.empty:
                analysis_text += f"#### 失点内容 (合計 {len(df_misses)}回)\n"
                # 失点の種類ごとの集計と詳細
                miss_summary = df_misses['失点の種類'].value_counts().to_markdown()
                analysis_text += miss_summary + "\n\n"

                # 詳細のMarkdownテーブルを生成
                miss_details = df_misses[['開始時刻', '失点の種類', '失点の内容']]
                analysis_text += "##### 詳細リスト\n"
                analysis_text += miss_details.to_markdown(index=False) + "\n\n"
            else:
                analysis_text += "#### 失点内容\n"
                analysis_text += "失点したデータはありません。\n\n"
            
            analysis_text += "---\n\n"
            
    return analysis_text
