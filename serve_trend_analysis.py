import streamlit as st
import pandas as pd
import plotly.express as px
from utils import group_serve_type, group_detailed_serve_course

def display_opponent_serve_sequence_analysis(df, df_opponents):
    """
    相手のサーブ1本目と2本目の傾向を分析し、表示する関数。
    """
    st.write("---")
    st.subheader("相手のサーブシーケンス分析 (10-10以前)")
    
    # 必要な列の存在を確認
    required_cols = ['ゲーム数', '誰のサーブか', '自分の得点', '相手の得点', 'サーブの種類', 'サーブのコース']
    if not all(col in df.columns for col in required_cols):
        st.warning(f"分析に必要なデータ列が見つかりません: {', '.join(required_cols)}。データを確認してください。")
        return
    
    # 10-10未満の相手のサーブに限定
    df_serve = df[(df['誰のサーブか'] == '相手') & (df['自分の得点'] < 10) & (df['相手の得点'] < 10)].copy()

    if df_serve.empty:
        st.info("分析対象となるデータがありません（10-10未満の相手のサーブ）。")
        return

    # 1本目と2本目のサーブを判定
    df_serve['サーブシーケンス'] = df_serve.groupby(['ゲーム数', '得点者']).cumcount() % 2
    df_serve['サーブシーケンス'] = df_serve['サーブシーケンス'].replace({0: '1本目', 1: '2本目'})

    # --- 1. サーブのコースと種類ごとの構成比を円グラフで表示 ---
    st.markdown("##### 1本目 vs 2本目 サーブ構成比")
    col1, col2 = st.columns(2)

    # 1本目のサーブデータ
    df_first_serve = df_serve[df_serve['サーブシーケンス'] == '1本目']
    # 2本目のサーブデータ
    df_second_serve = df_serve[df_serve['サーブシーケンス'] == '2本目']
    
    # 円グラフの並び順を定義
    course_order = ['フォア前', 'ミドル前', 'バック前', 'フォアサイド', 'バックサイド', 'フォアロング', 'ミドルロング', 'バックロング']

    with col1:
        # コース構成比
        if not df_first_serve.empty:
            df_first_serve['コースグループ'] = df_first_serve['サーブのコース'].apply(group_detailed_serve_course)
            course_counts_1st = df_first_serve['コースグループ'].value_counts().reset_index()
            course_counts_1st.columns = ['コース', '本数']
            fig1 = px.pie(course_counts_1st, values='本数', names='コース', title='1本目のサーブコース', category_orders={'コース': course_order})
            fig1.update_traces(textinfo='percent+label')
            st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        if not df_second_serve.empty:
            df_second_serve['コースグループ'] = df_second_serve['サーブのコース'].apply(group_detailed_serve_course)
            course_counts_2nd = df_second_serve['コースグループ'].value_counts().reset_index()
            course_counts_2nd.columns = ['コース', '本数']
            fig2 = px.pie(course_counts_2nd, values='本数', names='コース', title='2本目のサーブコース', category_orders={'コース': course_order})
            fig2.update_traces(textinfo='percent+label')
            st.plotly_chart(fig2, use_container_width=True)
    
    col3, col4 = st.columns(2)
    with col3:
        # 種類構成比
        if not df_first_serve.empty:
            df_first_serve['サーブグループ'] = df_first_serve['サーブの種類'].apply(group_serve_type)
            type_counts_1st = df_first_serve['サーブグループ'].value_counts().reset_index()
            type_counts_1st.columns = ['種類', '本数']
            fig3 = px.pie(type_counts_1st, values='本数', names='種類', title='1本目のサーブ種類')
            fig3.update_traces(textinfo='percent+label')
            st.plotly_chart(fig3, use_container_width=True)

    with col4:
        if not df_second_serve.empty:
            df_second_serve['サーブグループ'] = df_second_serve['サーブの種類'].apply(group_serve_type)
            type_counts_2nd = df_second_serve['サーブグループ'].value_counts().reset_index()
            type_counts_2nd.columns = ['種類', '本数']
            fig4 = px.pie(type_counts_2nd, values='本数', names='種類', title='2本目のサーブ種類')
            fig4.update_traces(textinfo='percent+label')
            st.plotly_chart(fig4, use_container_width=True)

    # --- 2. 変化の割合を計算 ---
    st.markdown("##### 1本目から2本目への変化率")
    if not df_serve.empty:
        # 連続するサーブのペアを作成
        # df_serve = df_serve.sort_values(['ゲーム数', '開始時刻']).reset_index(drop=True) # `開始時刻`列がないためコメントアウト
        df_serve['rally_id'] = df_serve.groupby('ゲーム数').cumcount()
        df_serve = df_serve.sort_values(['ゲーム数', 'rally_id']).reset_index(drop=True)
        
        # 1本目と2本目でコースが同じか判定
        df_serve['same_course'] = df_serve['サーブのコース'] == df_serve['サーブのコース'].shift(1)
        # 1本目と2本目で種類が同じか判定
        df_serve['same_type'] = df_serve['サーブの種類'] == df_serve['サーブの種類'].shift(1)

        # 2本目のサーブデータのみを抽出し、有効なペアに限定
        df_sequence_analysis = df_serve[
            (df_serve['サーブシーケンス'] == '2本目') &
            (df_serve['ゲーム数'] == df_serve['ゲーム数'].shift(1)) &
            (df_serve['誰のサーブか'] == df_serve['誰のサーブか'].shift(1))
        ]

        if not df_sequence_analysis.empty:
            total_sequences = len(df_sequence_analysis)
            same_course_count = df_sequence_analysis['same_course'].sum()
            same_type_count = df_sequence_analysis['same_type'].sum()
            
            # 変化の確率を計算
            course_change_rate = 100 * (total_sequences - same_course_count) / total_sequences if total_sequences > 0 else 0
            type_change_rate = 100 * (total_sequences - same_type_count) / total_sequences if total_sequences > 0 else 0

            st.write(f"**合計サーブペア数**: {total_sequences}本")
            st.markdown(f"**サーブのコースを変える確率**: `{course_change_rate:.1f}%`")
            st.markdown(f"**サーブの種類を変える確率**: `{type_change_rate:.1f}%`")
        else:
            st.info("1本目と2本目のサーブペアがありません。")