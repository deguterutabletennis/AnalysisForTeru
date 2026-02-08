import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import group_detailed_serve_course, group_serve_type

def display_serve_court_map(df, df_opponents, current_server_type, phase):
    """
    卓球台に見立てた長方形の背景上に、サーブコースの割合を円の大きさで視覚的に表示する。
    Args:
        df (pd.DataFrame): サーブデータ。
        df_opponents (pd.DataFrame): 相手選手情報 (AI分析用)。
        current_server_type (str): '自分'または'相手'。
        phase (str): 分析対象のゲームフェーズ ('all', 'early_middle', 'game_ending')
    """
    # 必要な列の存在を確認
    required_cols = ['サーブのコース', 'サーブの種類', '誰のサーブか', '自分の得点', '相手の得点', '得点者']
    if not all(col in df.columns for col in required_cols):
        missing_cols = [col for col in required_cols if col not in df.columns]
        st.warning(f"サーブ分析に必要なデータ列が見つかりません: {', '.join(missing_cols)}。データを確認してください。")
        return

    df = df.copy()
    
    # ゲームのフェーズを判定する関数
    def get_game_phase(row):
        my_score = row['自分の得点']
        opponent_score = row['相手の得点']
        
        # ラリー開始時点のスコアで終盤を判定
        rally_start_my_score = my_score - 1 if row['得点者'] == '自分' else my_score
        rally_start_opponent_score = opponent_score - 1 if row['得点者'] == '相手' else opponent_score
        
        # スコアが0未満になることはないため補正
        rally_start_my_score = max(0, rally_start_my_score)
        rally_start_opponent_score = max(0, rally_start_opponent_score)

        if rally_start_my_score >= 8 and rally_start_opponent_score >= 8:
            return '終盤'
        else:
            return '序盤・中盤'

    # データフレームにゲームフェーズ列を追加
    df['ゲームフェーズ'] = df.apply(get_game_phase, axis=1)

    # フェーズに基づいてデータフレームをフィルタリング
    if phase == 'early_middle':
        df_filtered_by_phase = df[df['ゲームフェーズ'] == '序盤・中盤']
    elif phase == 'game_ending':
        df_filtered_by_phase = df[df['ゲームフェーズ'] == '終盤']
    else: # phase == 'all'
        df_filtered_by_phase = df
    
    # サーブのサーバーでフィルタリング
    filtered_by_server_type_df = df_filtered_by_phase[df_filtered_by_phase['誰のサーブか'] == current_server_type].copy()

    # 相手の利き腕を判定
    opponent_handedness = None
    if not df_opponents.empty and '相手の戦型' in df_opponents.columns:
        opponent_style_val = df_opponents['相手の戦型'].iloc[0]
        if isinstance(opponent_style_val, str) and len(opponent_style_val) > 0:
            opponent_handedness = opponent_style_val[0]

    # フィルタリング後のDataFrameを使用してコース分布を計算
    filtered_by_server_type_df['詳細サーブコースグループ'] = filtered_by_server_type_df['サーブのコース'].apply(group_detailed_serve_course)
    serve_counts = filtered_by_server_type_df['詳細サーブコースグループ'].value_counts()
    total_serves = serve_counts.sum()

    if total_serves == 0:
        st.info("選択された期間のデータがありません。")
        return

    serve_percentages = (serve_counts / total_serves * 100).round(1)
    
    # 卓球台の描画とデータのプロット
    table_width = 360
    table_height = 600
    x_back, x_middle, x_fore = 70, 180, 290

    my_serve_coords_default = {
        'バックロング': {'x': x_back, 'y': 70}, 
        'ミドルロング': {'x': x_middle, 'y': 70},
        'フォアロング': {'x': x_fore, 'y': 70}, 
        'バック前':    {'x': x_back, 'y': 220},
        'ミドル前':    {'x': x_middle, 'y': 220},
        'フォア前':    {'x': x_fore, 'y': 220},
    }
    my_serve_coords_right_opponent = {
        'バックロング': {'x': x_fore, 'y': 70},
        'ミドルロング': {'x': x_middle, 'y': 70},
        'フォアロング': {'x': x_back, 'y': 70},
        'バック前':    {'x': x_fore, 'y': 220},
        'ミドル前':    {'x': x_middle, 'y': 220},
        'フォア前':    {'x': x_back, 'y': 220},
    }
    opponent_serve_coords = {
        'バックロング': {'x': x_back, 'y': 530},
        'ミドルロング': {'x': x_middle, 'y': 530},
        'フォアロング': {'x': x_fore, 'y': 530},
        'バック前':    {'x': x_back, 'y': 380},
        'ミドル前':    {'x': x_middle, 'y': 380},
        'フォア前':    {'x': x_fore, 'y': 380},
    }
    current_serve_area_coords = my_serve_coords_default
    if current_server_type == '自分':
        current_serve_area_coords = my_serve_coords_right_opponent if opponent_handedness == '右' else my_serve_coords_default
    else:
        current_serve_area_coords = opponent_serve_coords

    fig = go.Figure()
    fig.add_shape(type="rect", xref="x", yref="y", x0=0, y0=0, x1=table_width, y1=table_height, fillcolor="darkblue", line=dict(color="white", width=2), layer="below", opacity=1.0)
    fig.add_shape(type="line", xref="x", yref="y", x0=table_width / 2, y0=0, x1=table_width / 2, y1=table_height, line=dict(color="white", width=1), layer="below")
    fig.add_shape(type="line", xref="x", yref="y", x0=0, y0=table_height / 2, x1=table_width, y1=table_height / 2, line=dict(color="white", width=1), layer="below")

    plotting_order = []
    if current_server_type == '自分':
        plotting_order = ['フォアロング', 'ミドルロング', 'バックロング', 'フォア前', 'ミドル前', 'バック前'] if opponent_handedness == '右' else ['バックロング', 'ミドルロング', 'フォアロング', 'バック前', 'ミドル前', 'フォア前']
    else:
        plotting_order = ['バックロング', 'ミドルロング', 'フォアロング', 'バック前', 'ミドル前', 'フォア前']

    plot_data = []
    for area in plotting_order:
        percentage = serve_percentages.get(area, 0.0)
        count = serve_counts.get(area, 0)
        if area in current_serve_area_coords:
            coords = current_serve_area_coords[area]
            plot_data.append({'area': area, 'percentage': percentage, 'count': count, 'x': coords['x'], 'y': coords['y']})

    df_plot = pd.DataFrame(plot_data)
    if not df_plot.empty:
        max_percentage = 50
        size_scale = 130
        df_plot['circle_size'] = df_plot['percentage'].apply(lambda p: max(1, min(p, max_percentage) / max_percentage * size_scale))

        fig.add_trace(go.Scatter(
            x=df_plot['x'], y=df_plot['y'], mode='markers+text',
            marker=dict(size=df_plot['circle_size'], color='lightblue', opacity=0.7, sizemode='diameter'),
            text=[f"<b>{row['area']}</b><br>{row['percentage']:.1f}%<br>({int(row['count'])}本)" for index, row in df_plot.iterrows()],
            textfont=dict(color='white', size=12), textposition="middle center", hovertemplate="<b>%{text}</b><extra></extra>"
        ))
    
    phase_title_map = {
        'all': '試合全体',
        'early_middle': '序盤・中盤',
        'game_ending': '終盤 (8-8以降)'
    }
    
    fig.update_layout(
        title=f'{current_server_type}のサーブコース分布 ({phase_title_map.get(phase, "")})',
        xaxis=dict(range=[0, table_width], showgrid=False, zeroline=False, visible=False),
        yaxis=dict(range=[table_height, 0], showgrid=False, zeroline=False, visible=False),
        height=(table_height + 50) * 0.9, width=(table_width + 50) * 0.9,
        margin=dict(l=0, r=0, t=30, b=0),
    )

    config = {'staticPlot': True}
    
    # ここに一意のキーを追加
    key = f"serve_court_map_{current_server_type}_{phase}"
    st.plotly_chart(fig, use_container_width=False, config=config, key=key)