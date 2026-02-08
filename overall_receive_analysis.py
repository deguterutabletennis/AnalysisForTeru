import streamlit as st
import pandas as pd

def display_overall_receive_analysis(df):
    """
    相手サーブコース別のレシーブ分析結果をStreamlitのUIに表示する関数
    
    Args:
        df (pd.DataFrame): 試合の得失点データ
    """
    st.write("---")
    st.subheader("相手サーブコース別のレシーブ分析（全体）")

    df_my_receive = df[(df['誰のサーブか'] == '相手') & 
                       (df['サーブのコース'].notna()) &
                       (df['レシーブの種類'].notna())].copy()

    if not df_my_receive.empty and '得点者' in df_my_receive.columns:
        
        df_my_receive['ラリー継続'] = df_my_receive['６球目の種類'].notna()
        
        total_receives_table = pd.pivot_table(
            df_my_receive,
            index='サーブのコース',
            columns='レシーブの種類',
            values='得点者',
            aggfunc='count',
            fill_value=0,
            margins=True
        )

        points_won_table = pd.pivot_table(
            df_my_receive[df_my_receive['得点者'] == '自分'],
            index='サーブのコース',
            columns='レシーブの種類',
            values='得点者',
            aggfunc='count',
            fill_value=0,
            margins=True
        )
        
        rally_continued_but_lost_df = df_my_receive[(df_my_receive['ラリー継続'] == True) & (df_my_receive['得点者'] == '相手')]
        rally_continued_table = pd.pivot_table(
            rally_continued_but_lost_df,
            index='サーブのコース',
            columns='レシーブの種類',
            values='得点者',
            aggfunc='count',
            fill_value=0,
            margins=True
        )
        
        points_won_table = points_won_table.reindex(columns=total_receives_table.columns, index=total_receives_table.index, fill_value=0)
        rally_continued_table = rally_continued_table.reindex(columns=total_receives_table.columns, index=total_receives_table.index, fill_value=0)

        rate_table = (points_won_table / total_receives_table) * 100
        points_and_rally_rate_table = ((points_won_table + rally_continued_table) / total_receives_table) * 100
        
        summary_data = []
        receive_types = [col for col in total_receives_table.columns if col != 'All']
        
        for course in total_receives_table.index:
            for receive_type in receive_types + ['All']:
                total = total_receives_table.loc[course, receive_type]
                points = points_won_table.loc[course, receive_type]
                rally = rally_continued_table.loc[course, receive_type]
                win_rate = rate_table.loc[course, receive_type]
                win_and_rally_rate = points_and_rally_rate_table.loc[course, receive_type]

                if total > 0:
                    win_rate_str = f"{win_rate:.1f}%" if pd.notna(win_rate) else "-"
                    win_and_rally_rate_str = f"{win_and_rally_rate:.1f}%" if pd.notna(win_and_rally_rate) else "-"

                    summary_data.append({
                        'コース': '総合計' if course == 'All' else course,
                        'レシーブの種類': '総合計' if receive_type == 'All' else receive_type,
                        '得点数': int(points),
                        'ラリー継続数': int(rally),
                        '総回数': int(total),
                        '得点率': win_rate_str,
                        '得点・ラリー率': win_and_rally_rate_str
                    })
        
        display_df = pd.DataFrame(summary_data)
        display_df = display_df.replace({'コース': {'All': '総合計'}, 'レシーブの種類': {'All': '総合計'}})

        def sort_key(label):
            label_str = str(label)
            if 'バック' in label_str: return 0
            elif 'ミドル' in label_str: return 1
            elif 'フォア' in label_str: return 2
            else: return 3
                
        sorted_course_indices = sorted([c for c in display_df['コース'].unique() if c != '総合計'], key=sort_key)
        sorted_receive_types = sorted([rt for rt in display_df['レシーブの種類'].unique() if rt != '総合計'])

        sorted_courses = sorted_course_indices + ['総合計']
        sorted_receive_types_all = sorted_receive_types + ['総合計']
        
        display_df['コース'] = pd.Categorical(display_df['コース'], sorted_courses, ordered=True)
        display_df['レシーブの種類'] = pd.Categorical(display_df['レシーブの種類'], sorted_receive_types_all, ordered=True)
        display_df = display_df.sort_values(['コース', 'レシーブの種類'])

        st.subheader("全体サマリー")
        total_summary_df = display_df[display_df['コース'] == '総合計']
        total_summary_df_filtered = total_summary_df.set_index('レシーブの種類').drop(columns='コース')
        st.table(total_summary_df_filtered)
        st.info("得点・ラリー率: (得点数 + ラリー継続数) / 総回数 ※ラリーは５球目まで続いた後の失点数")
        
        st.markdown("---")

        st.subheader("サーブコース別の詳細")
        
        for course_name in sorted_course_indices:
            with st.expander(f"コース: {course_name}"):
                course_data = display_df[display_df['コース'] == course_name]
                course_data_filtered = course_data.set_index('レシーブの種類').drop(columns='コース')
                st.table(course_data_filtered)

        st.info("得点・ラリー率: (得点数 + ラリー継続数) / 総回数")

        df_back_receive = df_my_receive[df_my_receive['レシーブの種類'].str.contains('バック', na=False)]
        back_receive_total = len(df_back_receive)
        back_receive_points = (df_back_receive['得点者'] == '自分').sum()
        back_rally_continued = len(df_back_receive[(df_back_receive['ラリー継続'] == True) & (df_back_receive['得点者'] == '相手')])
        
        back_receive_rate = (back_receive_points / back_receive_total) * 100 if back_receive_total > 0 else 0
        back_win_and_rally_rate = ((back_receive_points + back_rally_continued) / back_receive_total) * 100 if back_receive_total > 0 else 0

        df_fore_receive = df_my_receive[df_my_receive['レシーブの種類'].str.contains('フォア', na=False)]
        fore_receive_total = len(df_fore_receive)
        fore_receive_points = (df_fore_receive['得点者'] == '自分').sum()
        fore_rally_continued = len(df_fore_receive[(df_fore_receive['ラリー継続'] == True) & (df_fore_receive['得点者'] == '相手')])

        fore_receive_rate = (fore_receive_points / fore_receive_total) * 100 if fore_receive_total > 0 else 0
        fore_win_and_rally_rate = ((fore_receive_points + fore_rally_continued) / fore_receive_total) * 100 if fore_receive_total > 0 else 0

        st.markdown("---")
        if back_receive_total > 0:
            st.markdown(f"**バックハンドレシーブ:**")
            st.markdown(f"- **得点率:** {back_receive_rate:.1f}% ({back_receive_points}/{back_receive_total})")
            st.markdown(f"- **得点・ラリー率:** {back_win_and_rally_rate:.1f}% ({back_receive_points + back_rally_continued}/{back_receive_total})")
        else:
            st.info("バックハンドレシーブのデータが見つかりませんでした。")
            
        if fore_receive_total > 0:
            st.markdown(f"**フォアハンドレシーブ:**")
            st.markdown(f"- **得点率:** {fore_receive_rate:.1f}% ({fore_receive_points}/{fore_receive_total})")
            st.markdown(f"- **得点・ラリー率:** {fore_win_and_rally_rate:.1f}% ({fore_receive_points + fore_rally_continued}/{fore_receive_total})")
        else:
            st.info("フォアハンドレシーブのデータが見つかりませんでした。")

    else:
        st.warning("「誰のサーブか」が「相手」となっているデータ、または「サーブのコース」,「レシーブの種類」,「得点者」のいずれかの列が存在しません。")

def get_overall_receive_analysis_for_ai(df):
    """
    相手サーブコース別のレシーブ分析結果をAIに渡すためのMarkdown文字列を生成する
    
    Args:
        df (pd.DataFrame): 試合の得失点データ
        
    Returns:
        str: 分析結果の文字列
    """
    df_my_receive = df[(df['誰のサーブか'] == '相手') & 
                       (df['サーブのコース'].notna()) &
                       (df['レシーブの種類'].notna())].copy()

    if df_my_receive.empty or '得点者' not in df_my_receive.columns:
        return "相手サーブコース別のレシーブ分析データが利用できません。"

    df_my_receive['ラリー継続'] = df_my_receive['６球目の種類'].notna()
    
    total_receives_table = pd.pivot_table(
        df_my_receive,
        index='サーブのコース',
        columns='レシーブの種類',
        values='得点者',
        aggfunc='count',
        fill_value=0,
        margins=True
    )

    points_won_table = pd.pivot_table(
        df_my_receive[df_my_receive['得点者'] == '自分'],
        index='サーブのコース',
        columns='レシーブの種類',
        values='得点者',
        aggfunc='count',
        fill_value=0,
        margins=True
    )
    
    rally_continued_but_lost_df = df_my_receive[(df_my_receive['ラリー継続'] == True) & (df_my_receive['得点者'] == '相手')]
    rally_continued_table = pd.pivot_table(
        rally_continued_but_lost_df,
        index='サーブのコース',
        columns='レシーブの種類',
        values='得点者',
        aggfunc='count',
        fill_value=0,
        margins=True
    )
    
    points_won_table = points_won_table.reindex(columns=total_receives_table.columns, index=total_receives_table.index, fill_value=0)
    rally_continued_table = rally_continued_table.reindex(columns=total_receives_table.columns, index=total_receives_table.index, fill_value=0)

    rate_table = (points_won_table / total_receives_table) * 100
    points_and_rally_rate_table = ((points_won_table + rally_continued_table) / total_receives_table) * 100
    
    summary_data = []
    receive_types = [col for col in total_receives_table.columns if col != 'All']
    
    for course in total_receives_table.index:
        for receive_type in receive_types + ['All']:
            total = total_receives_table.loc[course, receive_type]
            points = points_won_table.loc[course, receive_type]
            rally = rally_continued_table.loc[course, receive_type]
            win_rate = rate_table.loc[course, receive_type]
            win_and_rally_rate = points_and_rally_rate_table.loc[course, receive_type]

            if total > 0:
                summary_data.append({
                    'コース': '総合計' if course == 'All' else course,
                    'レシーブの種類': '総合計' if receive_type == 'All' else receive_type,
                    '得点数': int(points),
                    'ラリー継続数': int(rally),
                    '総回数': int(total),
                    '得点率': f"{win_rate:.1f}%" if pd.notna(win_rate) else "-",
                    '得点・ラリー率': f"{win_and_rally_rate:.1f}%" if pd.notna(win_and_rally_rate) else "-"
                })
    
    display_df = pd.DataFrame(summary_data)
    
    def sort_key(label):
        label_str = str(label)
        if 'バック' in label_str: return 0
        elif 'ミドル' in label_str: return 1
        elif 'フォア' in label_str: return 2
        else: return 3
            
    sorted_course_indices = sorted([c for c in display_df['コース'].unique() if c != '総合計'], key=sort_key)
    sorted_receive_types = sorted([rt for rt in display_df['レシーブの種類'].unique() if rt != '総合計'])

    sorted_courses = sorted_course_indices + ['総合計']
    sorted_receive_types_all = sorted_receive_types + ['総合計']
    
    display_df['コース'] = pd.Categorical(display_df['コース'], sorted_courses, ordered=True)
    display_df['レシーブの種類'] = pd.Categorical(display_df['レシーブの種類'], sorted_receive_types_all, ordered=True)
    display_df = display_df.sort_values(['コース', 'レシーブの種類'])

    analysis_text = "## 相手サーブコース別のレシーブ分析\n"
    analysis_text += "### 全体サマリー\n"
    analysis_text += "※得点・ラリー率: (得点数 + ラリー継続数) / 総回数。ラリー継続は５球目以降のラリーで失点した場合。\n"
    total_summary_df = display_df[display_df['コース'] == '総合計'].set_index('レシーブの種類').drop(columns='コース')
    analysis_text += total_summary_df.to_markdown() + "\n\n"

    analysis_text += "### サーブコース別の詳細\n"
    for course_name in sorted_course_indices:
        course_data = display_df[display_df['コース'] == course_name].set_index('レシーブの種類').drop(columns='コース')
        analysis_text += f"#### コース: {course_name}\n"
        analysis_text += course_data.to_markdown() + "\n\n"

    df_back_receive = df_my_receive[df_my_receive['レシーブの種類'].str.contains('バック', na=False)]
    back_receive_total = len(df_back_receive)
    back_receive_points = (df_back_receive['得点者'] == '自分').sum()
    back_rally_continued = len(df_back_receive[(df_back_receive['ラリー継続'] == True) & (df_back_receive['得点者'] == '相手')])
    back_receive_rate = (back_receive_points / back_receive_total) if back_receive_total > 0 else 0
    back_win_and_rally_rate = ((back_receive_points + back_rally_continued) / back_receive_total) if back_receive_total > 0 else 0
    
    if back_receive_total > 0:
        analysis_text += f"### バックハンドレシーブ\n"
        analysis_text += f"- 得点率: {back_receive_rate:.1%} ({back_receive_points}/{back_receive_total})\n"
        analysis_text += f"- 得点・ラリー率: {back_win_and_rally_rate:.1%} ({back_receive_points + back_rally_continued}/{back_receive_total})\n\n"

    df_fore_receive = df_my_receive[df_my_receive['レシーブの種類'].str.contains('フォア', na=False)]
    fore_receive_total = len(df_fore_receive)
    fore_receive_points = (df_fore_receive['得点者'] == '自分').sum()
    fore_rally_continued = len(df_fore_receive[(df_fore_receive['ラリー継続'] == True) & (df_fore_receive['得点者'] == '相手')])
    fore_receive_rate = (fore_receive_points / fore_receive_total) if fore_receive_total > 0 else 0
    fore_win_and_rally_rate = ((fore_receive_points + fore_rally_continued) / fore_receive_total) if fore_receive_total > 0 else 0
    
    if fore_receive_total > 0:
        analysis_text += f"### フォアハンドレシーブ\n"
        analysis_text += f"- 得点率: {fore_receive_rate:.1%} ({fore_receive_points}/{fore_receive_total})\n"
        analysis_text += f"- 得点・ラリー率: {fore_win_and_rally_rate:.1%} ({fore_receive_points + fore_rally_continued}/{fore_receive_total})\n"

    return analysis_text
