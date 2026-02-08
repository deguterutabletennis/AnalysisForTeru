import streamlit as st
import os
import toml # tomlが secrets.toml の読み込みに使われている可能性
import google.generativeai as genai

# Streamlit Cloud環境か、ローカル環境かを判断
# Streamlit Cloudはst.secretsが存在するため、この判定が可能
is_streamlit_cloud = "GEMINI_API_KEY" in st.secrets # または別のキーで判定

if is_streamlit_cloud:
    try:
        # Streamlit Cloudではst.secretsから直接読み込む
        api_key = st.secrets.get("google_api_key")
        if api_key is None:
            # セクション形式で保存されている場合
            api_key = st.secrets.gemini.google_api_key

        genai.configure(api_key=api_key)
        st.session_state.gemini_ready = True
    except Exception as e:
        st.session_state.gemini_ready = False
        st.error(f"Streamlit CloudでのAPIキー設定中にエラーが発生しました: {e}")
        st.info("Streamlit CloudのSecrets設定を確認してください。")

else:
    # ローカル環境ではsecrets.tomlを直接読み込む
    secrets_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), ".streamlit", "secrets.toml"
    )
    try:
        secrets = toml.load(secrets_path)
        api_key = secrets.get("google_api_key")
        if api_key is None:
            api_key = secrets.get("gemini", {}).get("google_api_key")

        if api_key:
            genai.configure(api_key=api_key)
            st.session_state.gemini_ready = True
        else:
            st.session_state.gemini_ready = False
            st.error("ローカル環境のsecrets.tomlにGoogle APIキーが見つかりません。")
            st.info("secrets.tomlに 'google_api_key = \"YOUR_API_KEY\"' または '[gemini]\\ngoogle_api_key = \"YOUR_API_KEY\"' の形式で設定してください。")
    except FileNotFoundError:
        st.session_state.gemini_ready = False
        st.error("ローカル環境の .streamlit/secrets.toml が見つかりません。")
    except Exception as e:
        st.session_state.gemini_ready = False
        st.error(f"secrets.tomlの読み込み中にエラーが発生しました: {e}")



COMMON_PROMPT_HEADER = """
卓球のルールについて説明します。
# 卓球ルール
卓球は5ゲーム制で3ゲーム先取した選手が勝利となります。
1ゲームは11点先取で10-10になったら2点差をつけた方がゲームを取ります。
サーブは2本交代。10-10になったら1本交代。

# データ定義
以下のデータは、卓球の試合に関する得点・失点情報です。各カラムの意味は以下の通りです。
- **ゲーム数**: 何ゲーム目を示す。1から5ゲーム目まである。
- **自分の得点**:ゲームの中での自分の得点
- **相手の得点**:ゲームの中での相手の得点
- **得失点の種類**:得点の種類（自分のプレーで得点、相手のミスで得点、得点（判断迷う））と失点の種類（相手のプレーで失点、自分のミスで失点、失点（判断迷う））
- **得点者**:ラリーでどちらが得点したかを示す（例：自分、相手）
- **誰のサーブか**: 「自分」か「相手」どちらのサーブから始まったかを示す。
- **サーブの種類**: サーブの種類（例: 順横、巻込み、YGサーブ、バック）
- **サーブのコース**: サーブを打ったコース（例: フォア前、バック前、ミドル前、バックロング、フォアロング）
- **サーブの質**: サーブの良し悪し（例: 良い、普通、悪い、少し浮いた、浮いた、ミス）
- **レシーブの種類**: サーブに対するレシーブの種類（例: バックチキータ、フォアストップ、バックドライブ、バックツッツキ）
- **レシーブのコース**: レシーブを返したコース（例: フォア前、バック(正面)、フォア、ミドル）
- **レシーブの質**: レシーブの良し悪し（例: 良い、普通、少し浮いた、ミス）
- **得点の種類**: 自分の得点につながったプレーの種類（例: フォアハンドドライブ、サービスエース、バックドライブ）
- **得点の内容**: 得点の詳細（例: 「フォアドライブが決まった」、「相手のレシーブミス」）
- **失点の種類**: 自分の失点につながったプレーの種類（例: サービスミス、バックハンドミス）
- **失点の内容**: 自分の失点の詳細（例: 「サーブがネットにかかった」、「バックハンドがオーバーした」）
- **３球目の種類**:ラリーの３球目の種類（例: フォアドライブ、フォアストップ、バックドライブ、バックツッツキ）
- **３球目のコース**:３球目を返したコース（例: フォア前、バック(正面)、フォア、ミドル、バック）
- **３球目の質**:３球目の良し悪し（例: 良い、普通、少し浮いた、ミス）
- **４球目の種類**:ラリーの４球目の種類（例: フォアドライブ、フォアストップ、バックドライブ、バックツッツキ）
- **４球目のコース**:４球目を返したコース（例: フォア前、バック(正面)、フォア、ミドル、バック）
- **４球目の質**:４球目の良し悪し（例: 良い、普通、少し浮いた、ミス）
- **５球目の種類**:ラリーの５球目の種類（例: フォアドライブ、フォアストップ、バックドライブ、バックツッツキ）
- **５球目のコース**:５球目を返したコース（例: フォア前、バック(正面)、フォア、ミドル、バック）
- **５球目の質**:５球目の良し悪し（例: 良い、普通、少し浮いた、ミス）
- **６球目の種類**:ラリーの６球目の種類（例: フォアドライブ、フォアストップ、バックドライブ、バックツッツキ）
- **６球目のコース**:６球目を返したコース（例: フォア前、バック(正面)、フォア、ミドル、バック）
- **６球目の質**:６球目の良し悪し（例: 良い、普通、少し浮いた、ミス）
- **７球目以降**:7究明以降のラリーの内容

# どちらがラリーしたかの判断方法
'誰のサーブか'が’自分'、'相手'で最初のサーブ実施者が分かる。
サーブ実施者の反対が、レシーブ実施者となる。
その後、３球目、４球目、５球目、６球目と順番にラリーした人が変わる
"""
