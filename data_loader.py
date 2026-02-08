import streamlit as st
import os
import pandas as pd
from utils import (time_to_seconds, create_youtube_link)

def load_and_process_data():
    """
    Excelファイルを読み込み、必要なデータ処理を行う。
    処理されたDataFrameとYouTube動画IDを返す。
    """
    excel_files = sorted([f for f in os.listdir('.') if f.endswith('.xlsx')]) #
    if not excel_files:
        st.error("エラー: Excelファイルが見つかりません。リポジトリに.xlsxファイルをアップロードしてください。") #
        st.stop() #

    selected_file = st.selectbox("分析する試合データを選択してください", excel_files) #

    df = pd.DataFrame() #
    youtube_video_id = None #

    try:
        df_opponents = pd.read_excel(selected_file, sheet_name='対戦者', header=0) #
        df_opponents = df_opponents.dropna(how='all') #
        df_opponents.columns = df_opponents.columns.str.strip() #

        if 'Youtube Id' in df_opponents.columns: #
            youtube_video_id = df_opponents.loc[0, 'Youtube Id'] #
        else:
            st.error("エラー: 「対戦者」シートに「Youtube Id」列が見つかりません。") #
            st.stop() #

        df = pd.read_excel(selected_file, sheet_name='試合分析', header=0, usecols=lambda x: x not in ['Unnamed: 0']) #
        df = df.dropna(how='all') #
        df.columns = df.columns.str.strip() #

        if '開始時刻' in df.columns: #
            df['開始時刻_秒'] = df['開始時刻'].astype(str).apply(time_to_seconds) #
            df['YouTubeリンク'] = df.apply(lambda row: create_youtube_link(youtube_video_id, row['開始時刻_秒']), axis=1) #
        else:
            st.error("「開始時刻」列が見つかりませんでした。スプレッドシートを確認してください。") #
            df['YouTubeリンク'] = "#" #

        return df, df_opponents, youtube_video_id

    except FileNotFoundError:
        st.error(f"エラー: Excelファイル '{selected_file}' が見つかりません。") #
        st.stop() #
    except KeyError:
        st.error(f"エラー: Excelファイル '{selected_file}' 内にシート名 '試合分析' または '対戦者' が見つかりません。") #
        st.stop() #
    except Exception as e:
        st.error(f"ファイルの読み込み中に予期せぬエラーが発生しました: {e}") #
        st.info("ファイルが破損していないか、また `openpyxl` が `requirements.txt` に含まれているか確認してください。") #
        st.stop() #