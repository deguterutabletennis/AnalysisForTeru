import streamlit as st
import os
import pandas as pd
import gspread
from gspread_dataframe import get_as_dataframe
import numpy as np
import datetime
import plotly.express as px
import openpyxl 
import google.generativeai as genai

# --- パスワード設定 ---
def check_password():
    """パスワードが正しいかチェックする関数"""
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if st.session_state["password_correct"]:
        return True

    # パスワード入力画面の表示
    st.title("認証が必要です")
    password = st.text_input("パスワードを入力してください", type="password")
    if st.button("ログイン"):
        if password == "deguchi":  # ← ここに好きなパスワードを設定してください
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("パスワードが違います")
    return False

# ここでチェックを実行。パスワードが違うとこれより下には進みません。
check_password()

from ai_config import COMMON_PROMPT_HEADER

import rally_input_tab
import drive_analysis_tab
from ai_functions import (generate_ai_response,get_ai_analysis_data)
from utils import(time_to_seconds, create_youtube_link, group_serve_type, group_serve_course, group_detailed_serve_course)
from score_summary import(display_score_summary, get_score_summary_for_ai)
from match_summary import(display_match_summary, get_match_summary_for_ai)
from serve_score_pattern import(display_serve_score_pattern, get_serve_score_pattern_for_ai)
from serve_loss_pattern import(display_serve_loss_pattern, get_serve_loss_pattern_for_ai)
from recieve_score_pattern import(display_recieve_score_pattern, get_recieve_score_pattern_for_ai)
from recieve_loss_pattern import(display_recieve_loss_pattern, get_recieve_loss_pattern_for_ai)
from match_data import(display_match_data, get_match_data_for_ai)
from first_drive_analysis import(display_first_drive_analysis, get_first_drive_analysis_for_ai)
from my_first_play_success_rate import(display_my_first_play_success_rate, get_my_first_play_success_rate_for_ai)
from overall_score_miss_analysis import(display_overall_score_miss_analysis, get_overall_score_miss_analysis_for_ai)
from overall_receive_analysis import(display_overall_receive_analysis, get_overall_receive_analysis_for_ai)
from serve_analysis import(display_serve_analysis, get_serve_analysis_for_ai)
from serve_rate_transition import(display_serve_rate_transition, get_serve_rate_transition_for_ai)
from serve_win_rate_analysis import(display_serve_win_rate_analysis, get_serve_win_rate_analysis_for_ai)
from serve_receive_analysis import(display_serve_receive_analysis, get_serve_receive_analysis_for_ai)
from point_breakdown_analysis import(display_point_breakdown_analysis, get_point_breakdown_analysis_for_ai)
from previous_ball_analysis import(display_previous_ball_analysis, get_previous_ball_analysis_for_ai)
from consecutive_ball_analysis import(display_consecutive_ball_analysis, get_consecutive_ball_analysis_for_ai)
from game_ending_analysis import(display_game_ending_analysis, get_game_ending_analysis_for_ai)
from data_loader import load_and_process_data
from serve_court_map import (display_serve_court_map)
from serve_trend_analysis import (display_opponent_serve_sequence_analysis)
from ai_prompts import (
    run_overall_analysis,
    run_scores_analysis,
    run_misses_analysis,
    run_coach_analysis,
    run_serve_tactics_analysis,
    run_receive_tactics_analysis,
    run_rally_tactics_analysis,
    run_match_tactics_analysis,
)


st.set_page_config(layout="wide")

st.title("🏓 卓球データ分析")

df, df_opponents, youtube_video_id = load_and_process_data()

st.write('---')

display_match_summary(df, df_opponents)


st.write("---") # 区切り線

# --- Session Stateの初期化 ---
if "all_rallies" not in st.session_state:
    st.session_state.all_rallies = []

# AI関連のSession State変数をここで初期化
if "gemini_ready" not in st.session_state:
    try:
        google_api_key = st.secrets["gemini"]["google_api_key"]
        genai.configure(api_key=google_api_key)
        st.session_state.gemini_ready = True
    except KeyError:
        st.session_state.gemini_ready = False

if "gemini_api_key" not in st.session_state:
    if st.session_state.gemini_ready:
        st.session_state.gemini_api_key = google_api_key
    else:
        st.session_state.gemini_api_key = ""    


# メイン画面を「データ分析結果」と「AIコーチング」のタブに分割
tab_analysis, tab_opponent, tab_ai_coach, tab_rally_input = st.tabs(["📊 データ分析結果", "🧐相手の傾向", "🤖AIコーチング", "🏓ラリー入力"])

with tab_analysis:
    st.session_state.current_selected_tab_name = "📊 データ分析結果"
    # --- 得失点合計と内訳 ---
    display_point_breakdown_analysis(df)

    # --- サーブ・レシーブ別 得失点分析 ---
    display_serve_receive_analysis(df)

    # --- サーブ別得点率の分析 ---
    display_serve_win_rate_analysis(df,'自分')

    # --- サーブコースの分析 ---
    col1, col2 = st.columns(2)
    with col1:
        display_serve_court_map(df, df_opponents, '自分', 'all') # 自分のサーブを表示        
    with col2:
        display_serve_court_map(df, df_opponents, '自分', 'game_ending') # 自分のサーブを表示

    # --- ゲーム別 サーブ種類別得点率の推移 ---
    display_serve_rate_transition(df, '自分')

    # --- サーブ種類別の得点・失点内容分析 ---
    display_serve_analysis(df)


    # --- 相手サーブコース別のレシーブ分析（全体） ---
    display_overall_receive_analysis(df)

    # --- 全ゲーム合計 得点・失点の種類別集計（円グラフ） ---
    display_overall_score_miss_analysis(df)

    # --- どちらが先にドライブを仕掛けたかの分析 ---
    st.write("---")
    display_first_drive_analysis(df)
    # --- 自分が最初に仕掛けたプレーの成功率分析 ---
    display_my_first_play_success_rate(df)

    # --- 相手の直前コースと自分の打球技術の成功率の関連性 ---
    display_previous_ball_analysis(df)

    # ---  同じ組み合わせでの連続打球成功率分析 ---
    display_consecutive_ball_analysis(df)

    # 2つのカラムを作成
    col3, col4 = st.columns(2)
    with col3:
        st.write("---")
        st.markdown("##### 自分のフォアドライブ分析")
        if not df.empty:
            # dfを利用してドライブデータを抽出
            my_forehand_df, my_round_df = drive_analysis_tab.find_forehand_drives(df, '自分')

            # フォア側からのフォアドライブ (自分)
            st.markdown("###### フォア側からのフォアドライブ")
            if not my_forehand_df.empty:
                drive_analysis_tab.draw_court_map(my_forehand_df, "フォア側からのフォアドライブ", '自分', df_opponents)
            else:
                st.info("データがありません。")

        else:
            st.warning("ラリー入力タブでデータを追加してください。")

        st.markdown("##### 自分のバックドライブ分析")
        if not df.empty:
            my_backhand_df = drive_analysis_tab.find_backhand_drives(df, '自分')
            if not my_backhand_df.empty:
                drive_analysis_tab.draw_court_map(my_backhand_df, "バックドライブ", '自分', df_opponents)
            else:
                st.info("データがありません。")
        else:
            st.warning("ラリー入力タブでデータを追加してください。")

        st.markdown("---") # 区切り線

    with col4:
        st.write("---")
        st.markdown("##### 自分のフォアドライブ分析")
        if not df.empty:
            st.markdown("###### 回り込みフォアドライブ")
            if not my_round_df.empty:
                drive_analysis_tab.draw_court_map(my_round_df, "回り込みフォアドライブ", '自分', df_opponents)
            else:
                st.info("データがありません。")
        else:
            st.warning("ラリー入力タブでデータを追加してください。")            

    # ---  ゲーム終盤の分析  ---
    display_game_ending_analysis(df)

    # --- 相手サーブコース別のレシーブ分析（全体） ---
    st.write("---")
    st.subheader("各種データ集")
    # --- サーブ時の得点パターン一覧 ---
    display_serve_score_pattern(df)
    # --- サーブ時の失点パターン一覧 ---
    display_serve_loss_pattern(df)
    # --- レシーブ時の得点パターン一覧 ---
    display_recieve_score_pattern(df)
    # --- レシーブ時の失点パターン一覧 ---
    display_recieve_loss_pattern(df)

    # --- 試合の全データ一覧 ---
    display_match_data(df)

    
with tab_opponent:
    st.session_state.current_selected_tab_name = "🧐相手の傾向"
    # --- サーブ別得点率の分析 ---
    display_serve_win_rate_analysis(df,'相手')

    # 2つのカラムを作成
    col1, col2 = st.columns(2)

    with col1:
        st.write("---")
        display_serve_court_map(df, df_opponents, '相手', 'all') # 相手のサーブを表示
        st.markdown("---") # 区切り線

    with col2:
        st.write("---")
        display_serve_court_map(df, df_opponents, '相手', 'game_ending') # 相手のサーブを表示
        st.markdown("---") # 区切り線

    # 2つのカラムを作成
    col3, col4 = st.columns(2)
    with col3:
        st.markdown("##### 相手のフォアドライブ分析")
        if not df.empty:
            # dfを利用してドライブデータを抽出
            opp_forehand_df, opp_round_df = drive_analysis_tab.find_forehand_drives(df, '相手')
            
            # フォア側からのフォアドライブ (相手)
            st.markdown("###### フォア側からのフォアドライブ")
            if not opp_forehand_df.empty:
                drive_analysis_tab.draw_court_map(opp_forehand_df, "フォア側からのフォアドライブ", '相手', df_opponents)
            else:
                st.info("データがありません。")

            st.markdown("###### 回り込みフォアドライブ")
            if not opp_round_df.empty:
                drive_analysis_tab.draw_court_map(opp_round_df, "回り込みフォアドライブ", '相手', df_opponents)
            else:
                st.info("データがありません。")
        else:
            st.warning("ラリー入力タブでデータを追加してください。")

    with col4:
        st.markdown("---") # 区切り線
        st.markdown("##### 相手のバックドライブ分析")
        if not df.empty:
            opp_backhand_df = drive_analysis_tab.find_backhand_drives(df, '相手')
            if not opp_backhand_df.empty:
                drive_analysis_tab.draw_court_map(opp_backhand_df, "バックドライブ", '相手', df_opponents)
            else:
                st.info("データがありません。")
        else:
            st.warning("ラリー入力タブでデータを追加してください。")

    # --- ゲーム別 サーブ種類別得点率の推移 ---
    st.write("---")
    display_serve_rate_transition(df, '相手')

    display_opponent_serve_sequence_analysis(df, df_opponents)


with tab_ai_coach:
    st.session_state.current_selected_tab_name = "🤖 AIコーチング"
    st.subheader("データが語る、あなたの潜在能力。AIコーチが成長への最短ルートを照らします。")
    if st.session_state.gemini_ready:
        # 2つのカラムに分けてボタンを配置
        col1, col2 = st.columns(2)

        with col1:
            if st.button("全体的な分析", key="ai_overall"):
                run_overall_analysis(df, df_opponents) # 関数呼び出しに置き換え

            if st.button("得点源の強化", key="ai_scores"):
                run_scores_analysis(df, df_opponents) # 関数呼び出しに置き換え

            if st.button("失点パターンの改善", key="ai_misses"):
                run_misses_analysis(df, df_opponents) # 関数呼び出しに置き換え

            if st.button("謎の専属コーチの分析を実行", key="ai_coach"):
                run_coach_analysis(df, df_opponents) # 関数呼び出しに置き換え
        with col2:
            if st.button("サーブ戦術を分析", key="ai_serve"):
                run_serve_tactics_analysis(df, df_opponents) # 関数呼び出しに置き換え

            if st.button("レシーブ戦術を分析", key="ai_recieve"):
                run_receive_tactics_analysis(df, df_opponents) # 関数呼び出しに置き換え

            if st.button("ラリー戦術を分析", key="ai_rally"):
                run_rally_tactics_analysis(df, df_opponents) # 関数呼び出しに置き換え

            if st.button("試合運び(戦術)を分析", key="ai_tactics"):
                run_match_tactics_analysis(df, df_opponents) # 関数呼び出しに置き換え

        st.markdown("---")
        st.subheader("AIからの回答")
        if "ai_response" in st.session_state:
            st.markdown(st.session_state.ai_response)
    else:
        st.warning("AI機能を利用するには、APIキーを正しく設定してください。")

with tab_rally_input:
    st.session_state.current_selected_tab_name = "ラリー入力"
    rally_input_tab.display_rally_input_tab()

