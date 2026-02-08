import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# --- 卓球台のマップを描画する関数 ---
def draw_court_map(df, title, player_to_analyze, df_opponents):
    opponent_handedness = None
    if not df_opponents.empty and '相手の戦型' in df_opponents.columns:
        opponent_style_val = df_opponents['相手の戦型'].iloc [0]
        if isinstance(opponent_style_val, str) and len(opponent_style_val) > 0:
            opponent_handedness = opponent_style_val [0]

    table_width = 360 # 上部の画像の幅に近い値を設定
    table_height = 600
    net_position = table_height / 2

    fig = go.Figure()

    # 卓球台の背景を生成
    fig.add_shape(
        type="rect",
        x0=0, y0=0, x1=table_width, y1=table_height,
        line=dict(color="white", width=2),
        fillcolor="darkblue",
        layer="below"
    )
    fig.add_shape(
        type="line",
        x0=0, y0=net_position, x1=table_width, y1=net_position,
        line=dict(color="white", width=2),
        layer="below"
    )
    fig.add_shape(
        type="line",
        x0=table_width / 2, y0=0, x1=table_width / 2, y1=table_height,
        line=dict(color="white", width=1),
        layer="below"
    )

    x_back = 70
    x_middle = 180
    x_fore = 290
    
    y_position = table_height * 0.85 if player_to_analyze == '自分' else table_height * 0.15
    
    if player_to_analyze == '自分':
        if opponent_handedness == '右':
            course_to_coord = {
                'フォア': (table_width - x_fore, y_position),
                'ミドル': (table_width - x_middle, y_position),
                'バック': (table_width - x_back, y_position),
            }
        else:
            course_to_coord = {
                'フォア': (x_fore, y_position),
                'ミドル': (x_middle, y_position),
                'バック': (x_back, y_position),
            }
    else:
        course_to_coord = {
            'フォア': (x_fore, y_position),
            'ミドル': (x_middle, y_position),
            'バック': (x_back, y_position),
        }

    if not df.empty:
        def group_course(course_str):
            if pd.notna(course_str):
                if 'フォア' in course_str:
                    return 'フォア'
                elif 'ミドル' in course_str:
                    return 'ミドル'
                elif 'バック' in course_str:
                    return 'バック'
            return None

        df['course_group'] = df['コース'].apply(group_course)
        
        grouped_data = df.groupby('course_group').agg(
            count=('コース', 'size'),
            miss_count=('ミス', 'sum')
        ).reset_index()
        
        grouped_data.columns = ['コース', 'count', 'miss_count']
        
        total_drives = grouped_data['count'].sum()
        if total_drives == 0:
            st.info("分析対象のドライブがありません。")
            return
            
        grouped_data['percentage'] = (grouped_data['count'] / total_drives) * 100
        
        grouped_data['miss_percentage'] = (grouped_data['miss_count'] / grouped_data['count']) * 100
        grouped_data['miss_percentage'] = grouped_data['miss_percentage'].fillna(0)

        if player_to_analyze == '相手':
            desired_order = ['バック', 'ミドル', 'フォア']
            grouped_data['コース'] = pd.Categorical(grouped_data['コース'], categories=desired_order, ordered=True)
            grouped_data = grouped_data.sort_values('コース')

        max_percentage = grouped_data['percentage'].max() if grouped_data['percentage'].max() > 0 else 1
        
        default_pie_size = 160 # 円グラフのデフォルトサイズを調整
        size_scale_factor = default_pie_size / max(1, max_percentage)

        plot_data_text = []

        for index, row in grouped_data.iterrows():
            course = row['コース']
            if course in course_to_coord:
                x, y = course_to_coord [course]
                
                total_count = row['count']
                miss_count = row['miss_count']
                success_count = total_count - miss_count
                
                pie_diameter_in_pixels = row['percentage'] * size_scale_factor
                pie_radius = pie_diameter_in_pixels / 2
                
                domain_x_start = max(0.0, (x - pie_radius) / table_width)
                domain_x_end = min(1.0, (x + pie_radius) / table_width)
                domain_y_start = max(0.0, (y - pie_radius) / table_height)
                domain_y_end = min(1.0, (y + pie_radius) / table_height)
                
                labels = ['成功', 'ミス']
                values = [success_count, miss_count]
                
                if sum(values) == 0:
                    continue

                fig.add_trace(go.Pie(
                    labels=labels,
                    values=values,
                    name=course,
                    hole=0,
                    marker_colors=['lightblue', 'lightcoral'], # ミスを薄めのオレンジに変更
                    textinfo='percent+label',
                    textfont=dict(color='black', size=16),
                    hovertemplate=f"<b>{course}</b><br>%{{label}}:<br>本数: %{{value}}<br>割合: %{{percent}}<extra></extra>",
                    domain=dict(x=[domain_x_start, domain_x_end], 
                                y=[domain_y_start, domain_y_end])
                ))

                plot_data_text.append({
                    'x': x,
                    'y': y,
                    'course': course,
                    'count': total_count,
                    'percentage': row['percentage']
                })
        
        df_plot_text = pd.DataFrame(plot_data_text)

        if not df_plot_text.empty:
            fig.add_trace(go.Scatter(
                x=df_plot_text['x'],
                y=df_plot_text['y'],
                mode='text',
                text=[f"({int(row['count'])}本)" for index, row in df_plot_text.iterrows()],
                textfont=dict(color='white', size=28),
                textposition="middle center",
                hovertemplate="<extra></extra>",
                showlegend=False
            ))
            
    fig.update_layout(
        title=None,
        xaxis=dict(range=[0, table_width], showgrid=False, zeroline=False, visible=False),
        yaxis=dict(range=[table_height, 0], showgrid=False, zeroline=False, visible=False),
        autosize=False,
        width=table_width,
        height=table_height,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False
    )
    # グラフの操作を無効にするための設定
    config = {
        'staticPlot': True
    }
    st.plotly_chart(fig, use_container_width=False, config=config)

# --- データを抽出・集計するコアロジック ---
def find_forehand_drives(all_rallies_df, player_to_analyze):
    """
    指定された選手（自分または相手）の最初のフォアドライブを抽出し、集計する。
    Args:
        all_rallies_df (pd.DataFrame): 全ラリーデータ。
        player_to_analyze (str): '自分'または'相手'。
    Returns:
        tuple: (フォアサイドからのドライブデータ, 回り込みドライブデータ)
    """
    forehand_drives = []
    round_drives = []
    
    # カラム名のマッピング（入力タブのキー名と合わせる）
    ball_type_map = {
        1: 'サーブの種類', 2: 'レシーブの種類', 3: '３球目の種類',
        4: '４球目の種類', 5: '５球目の種類', 6: '６球目の種類'
    }
    ball_course_map = {
        1: 'サーブのコース', 2: 'レシーブのコース', 3: '３球目のコース',
        4: '４球目のコース', 5: '５球目のコース', 6: '６球目のコース'
    }
    ball_quality_map = {
        1: 'サーブの質', 2: 'レシーブの質',
        3: '３球目の質', 4: '４球目の質',
        5: '５球目の質', 6: '６球目の質',
    }

    for index, rally in all_rallies_df.iterrows():
        found_first_drive = False
        for i in range(1, 7):
            if found_first_drive:
                break
            
            ball_type_col = ball_type_map.get(i)
            ball_course_col = ball_course_map.get(i)
            ball_quality_col = ball_quality_map.get(i)

            if ball_type_col in rally and pd.notna(rally[ball_type_col]) and 'フォアドライブ' in rally[ball_type_col]:
                
                is_my_drive = False
                if (rally.get('誰のサーブか') == '自分' and i % 2 != 0) or \
                   (rally.get('誰のサーブか') == '相手' and i % 2 == 0):
                    is_my_drive = True
                
                if (player_to_analyze == '自分' and is_my_drive) or \
                   (player_to_analyze == '相手' and not is_my_drive):
                    
                    prev_course = None
                    if i > 1:
                        prev_ball_course_col = ball_course_map.get(i-1)
                        if prev_ball_course_col in rally and pd.notna(rally[prev_ball_course_col]):
                            prev_course = rally[prev_ball_course_col]
                    
                    drive_course = rally.get(ball_course_col)

                    is_miss = 0
                    if ball_quality_col in rally and rally[ball_quality_col] == 'ミス':
                        is_miss = 1

                    # コースの入力がある場合のみ分析対象とする
                    if pd.notna(prev_course) and pd.notna(drive_course):
                        found_first_drive = True
                        # 'バック'が含まれる場合は回り込みドライブとして判定
                        if 'バック' in prev_course:
                            round_drives.append({
                                'コース': drive_course,
                                '球数': i,
                                '前のコース': prev_course,
                                'ミス' : is_miss
                            })
                        # 'フォア'または'ミドル'が含まれる場合はフォアサイドからのドライブと判定
                        elif 'フォア' in prev_course or 'ミドル' in prev_course:
                            forehand_drives.append({
                                'コース': drive_course,
                                '球数': i,
                                '前のコース': prev_course,
                                'ミス' : is_miss
                            })
    
    # データをDataFrameに変換
    forehand_df = pd.DataFrame(forehand_drives)
    round_df = pd.DataFrame(round_drives)

    return forehand_df, round_df


# --- データを抽出・集計するコアロジック ---
def find_backhand_drives(all_rallies_df, player_to_analyze):
    """
    指定された選手（自分または相手）の最初のバックドライブを抽出し、集計する。
    Args:
        all_rallies_df (pd.DataFrame): 全ラリーデータ。
        player_to_analyze (str): '自分'または'相手'。
    Returns:
        tuple: (バックハンドのドライブデータ)
    """
    backhand_drives = []
    
    # カラム名のマッピング（入力タブのキー名と合わせる）
    ball_type_map = {
        1: 'サーブの種類', 2: 'レシーブの種類', 3: '３球目の種類',
        4: '４球目の種類', 5: '５球目の種類', 6: '６球目の種類'
    }
    ball_course_map = {
        1: 'サーブのコース', 2: 'レシーブのコース', 3: '３球目のコース',
        4: '４球目のコース', 5: '５球目のコース', 6: '６球目のコース'
    }
    ball_quality_map = {
        1: 'サーブの質', 2: 'レシーブの質',
        3: '３球目の質', 4: '４球目の質',
        5: '５球目の質', 6: '６球目の質',
    }
    for index, rally in all_rallies_df.iterrows():
        found_first_drive = False
        for i in range(1, 7):
            if found_first_drive:
                break
            
            ball_type_col = ball_type_map.get(i)
            ball_course_col = ball_course_map.get(i)
            ball_quality_col = ball_quality_map.get(i)

            if ball_type_col in rally and pd.notna(rally[ball_type_col]) and 'バックドライブ' in rally[ball_type_col]:
                
                is_my_drive = False
                if (rally.get('誰のサーブか') == '自分' and i % 2 != 0) or \
                   (rally.get('誰のサーブか') == '相手' and i % 2 == 0):
                    is_my_drive = True
                
                if (player_to_analyze == '自分' and is_my_drive) or \
                   (player_to_analyze == '相手' and not is_my_drive):
                    
                    is_miss = 0
                    if ball_quality_col in rally and rally[ball_quality_col] == 'ミス':
                        is_miss = 1
                    
                    drive_course = rally.get(ball_course_col)

                    # コースの入力がある場合のみ分析対象とする
                    if pd.notna(drive_course):
                        found_first_drive = True
                        backhand_drives.append({
                            'コース': drive_course,
                            '球数': i,
                            'ミス' : is_miss
                        })
    
    # データをDataFrameに変換
    backhand_df = pd.DataFrame(backhand_drives)

    return backhand_df
