import streamlit as st
import pandas as pd
import plotly.express as px

def display_serve_rate_transition(df, current_player):
    """
    ゲーム別サーブ種類別得点率の推移をStreamlitのUIに表示する関数

    Args:
        df (pd.DataFrame): 試合の得失点データ
        current_player (str): 分析対象のプレイヤー ('自分'または'相手')
    """
    st.subheader(f"{current_player}のゲーム別 サーブ種類別得点率の推移")

    df_serve = df[df['誰のサーブか'] == current_player].copy()

    required_columns = ['誰のサーブか', 'ゲーム数', 'サーブの種類', '得点者']
    if not df_serve.empty and all(col in df_serve.columns for col in required_columns):
        
        df_serve['サーブの種類'] = df_serve['サーブの種類'].astype(str).str.strip()

        serve_keywords = {
            '順横': '順横',
            'YGサーブ': 'YG',
            '巻込み': '巻込み',
            'バックサーブ': 'バック',
            'キックサーブ': 'キック'
        }

        def categorize_serve(serve_type):
            if pd.isna(serve_type) or serve_type == '':
                return 'その他'
            
            for group, keyword in serve_keywords.items():
                if keyword in serve_type:
                    return group
            return 'その他'

        df_serve['サーブ種類（グループ化）'] = df_serve['サーブの種類'].apply(categorize_serve)
        
        total_serves_by_game = df_serve.groupby(['ゲーム数', 'サーブ種類（グループ化）']).size().reset_index(name='総回数')
        points_won_by_game = df_serve[df_serve['得点者'] == current_player].groupby(['ゲーム数', 'サーブ種類（グループ化）']).size().reset_index(name='得点数')

        game_serve_summary = pd.merge(total_serves_by_game, points_won_by_game, 
                                      on=['ゲーム数', 'サーブ種類（グループ化）'], how='left').fillna(0)
        
        game_serve_summary['得点率'] = (game_serve_summary['得点数'] / game_serve_summary['総回数']) * 100

        if not game_serve_summary.empty:
            fig = px.line(game_serve_summary, x='ゲーム数', y='得点率', color='サーブ種類（グループ化）',
                          title=f'{current_player}のゲームごとのサーブ種類別得点率の推移',
                          markers=True, 
                          text='総回数',
                          labels={'ゲーム数':'ゲーム数', '得点率':'得点率 (%)', 'サーブ種類（グループ化）':'サーブの種類'},
                          hover_data=['総回数', '得点数'])
            
            fig.update_layout(xaxis_title="ゲーム数", yaxis_title="得点率 (%)")
            fig.update_xaxes(dtick=1)
            fig.update_traces(textposition='top center')

            config = {'displayModeBar': False, 'staticPlot': True}
            
            st.plotly_chart(fig, use_container_width=True, config=config)
        else:
            st.info("サーブ種類ごとのゲーム別データが不足しているため、グラフを表示できませんでした。")
    else:
        st.warning(f"「誰のサーブか」が「{current_player}」となっているデータが見つからないか、「ゲーム数」, 「サーブの種類」, 「得点者」のいずれかの列が存在しません。")


def get_serve_rate_transition_for_ai(df, current_player):
    """
    ゲーム別サーブ種類別得点率の推移をAIに渡すためのMarkdown文字列を生成する

    Args:
        df (pd.DataFrame): 試合の得失点データ
        current_player (str): 分析対象のプレイヤー ('自分'または'相手')

    Returns:
        str: 分析結果のMarkdown文字列
    """
    df_serve = df[df['誰のサーブか'] == current_player].copy()

    required_columns = ['誰のサーブか', 'ゲーム数', 'サーブの種類', '得点者']
    if df_serve.empty or not all(col in df_serve.columns for col in required_columns):
        return f"{current_player}のゲーム別サーブ種類別得点率の推移データが利用できません。"

    df_serve['サーブの種類'] = df_serve['サーブの種類'].astype(str).str.strip()
    
    serve_keywords = {
        '順横': '順横',
        'YGサーブ': 'YG',
        '巻込み': '巻込み',
        'バックサーブ': 'バック',
        'キックサーブ': 'キック'
    }

    def categorize_serve(serve_type):
        if pd.isna(serve_type) or serve_type == '':
            return 'その他'
        
        for group, keyword in serve_keywords.items():
            if keyword in serve_type:
                return group
        return 'その他'

    df_serve['サーブ種類（グループ化）'] = df_serve['サーブの種類'].apply(categorize_serve)
    
    total_serves_by_game = df_serve.groupby(['ゲーム数', 'サーブ種類（グループ化）']).size().reset_index(name='総回数')
    points_won_by_game = df_serve[df_serve['得点者'] == current_player].groupby(['ゲーム数', 'サーブ種類（グループ化）']).size().reset_index(name='得点数')

    game_serve_summary = pd.merge(total_serves_by_game, points_won_by_game, 
                                  on=['ゲーム数', 'サーブ種類（グループ化）'], how='left').fillna(0)
    
    game_serve_summary['得点率'] = (game_serve_summary['得点数'] / game_serve_summary['総回数']) * 100
    
    game_serve_summary['得点率'] = game_serve_summary['得点率'].round(1).astype(str) + '%'
    game_serve_summary = game_serve_summary[['ゲーム数', 'サーブ種類（グループ化）', '総回数', '得点数', '得点率']]
    
    analysis_text = f"## {current_player}のゲーム別 サーブ種類別得点率の推移\n\n"
    if not game_serve_summary.empty:
        analysis_text += "### 集計データ\n"
        analysis_text += game_serve_summary.to_markdown(index=False)
    else:
        analysis_text += "サーブ種類ごとのゲーム別データが不足しているため、分析できませんでした。\n"
        
    return analysis_text