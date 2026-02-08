import streamlit as st
import os
import pandas as pd
import datetime
import io

def display_common_data_and_video_settings():
    """
    試合共通データと動画表示設定のセクションを管理する関数。
    この関数はラリー入力フォームとは独立して動作する。
    """
    with st.expander("試合共通データを入力/編集", expanded=True):
        st.write("スプレッドシートの「対戦者」シートに出力される項目です。")
        col_common1, col_common2, col_common3, col_common4, col_common5 = st.columns(5)
        with col_common1:
            my_styles = ["右シェーク裏裏ドライブ型", "左シェーク裏裏ドライブ型", "右シェーク表裏ドライブ型", "左シェーク表裏ドライブ型", "右ペン表ソフト速攻型", "左ペン表ソフト速攻型", "右ペン粒高守備型", "左ペン粒高守備型", "その他"]
            st.selectbox("自分の戦型", my_styles, key="my_style_select")
        with col_common2:
            st.text_input("所属", key="affiliation_input")
        with col_common3:
            st.text_input("対戦相手名", key="opponent_name_input")
        with col_common4:
            opponent_styles = ["右シェーク裏裏ドライブ型", "左シェーク裏裏ドライブ型", "右シェーク表裏ドライブ型", "左シェーク表裏ドライブ型", "右ペン表ソフト速攻型", "左ペン表ソフト速攻型", "右ペン粒高守備型", "左ペン粒高守備型", "その他"]
            st.selectbox("相手の戦型", opponent_styles, key="opponent_style_select")
        with col_common5:
            st.text_input("Youtube Id", key="youtube_id")

    with st.expander("🎥 動画表示設定", expanded=False):
        st.write("ラリーデータの入力補助のために動画を表示できます。")
        st.text_input("動画ファイルのローカルパスを入力してください (例: C:/Users/YourName/Videos/match.mp4)", key="video_path_input_rallytab")
        st.slider("動画の幅を調整 (px)", min_value=200, max_value=1200, step=50, key="video_width_slider_rallytab")

    if st.session_state.video_path_input_rallytab and os.path.exists(st.session_state.video_path_input_rallytab):
        st.video(st.session_state.video_path_input_rallytab, format="video/mp4", width=st.session_state.video_width_slider_rallytab)
    else:
        if st.expander("🎥 動画表示設定").expanded:
            st.warning("有効な動画ファイルパスを入力してください。")


def display_rally_input_tab():
    """
    ラリー入力タブのUIとロジックを表示する関数。
    """
    st.subheader("🏓 ラリー入力ツール")
    st.write("試合動画を見ながらラリーデータを入力・コメントできます。")

    # --- カスタムCSSの追加 ---
    st.markdown("""
        <style>
        /* 一般的なテキスト入力と数値入力（ゲーム数、得点など） */
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stDateInput > div > div > input {
            border: 1px solid #ccc; /* 薄いグレーの枠線 */
            border-radius: 5px; /* 角を少し丸くする */
            padding: 8px 12px; /* パディングでテキストとの間にスペースを設ける */
        }
        /* フォーカス時のスタイル */
        .stTextInput > div > div > input:focus,
        .stNumberInput > div > div > input:focus,
        .stDateInput > div > div > input:focus {
            border-color: #4CAF50; /* フォーカス時に緑色の枠線 */
            outline: none; /* デフォルトのアウトラインを削除 */
            box-shadow: 0 0 0 0.1rem rgba(76, 175, 80, 0.25); /* 軽い影 */
        }

        /* セレクトボックスのスタイル調整 */
        .stSelectbox > div > div {
            border: 1px solid #ccc; /* 薄いグレーの枠線 */
            border-radius: 5px; /* 角を少し丸くする */
            padding: 0;
        }

        /* セレクトボックスの内部要素（表示テキスト部分） */
        .stSelectbox > div > div > div[data-baseweb="select"] > div:first-child {
            padding: 8px 12px; /* テキスト部分にパディング */
            border-radius: 5px; /* 角を丸くする */
        }

        /* セレクトボックスのフォーカス時のスタイル */
        .stSelectbox > div > div:focus-within {
            border-color: #4CAF50; /* フォーカス時に緑色の枠線 */
            box-shadow: 0 0 0 0.1rem rgba(76, 175, 80, 0.25); /* 軽い影 */
            outline: none; /* デフォルトのアウトラインを削除 */
        }
        
        /* 得点者ラベルのパディング調整 */
        .st-emotion-cache-p5m9d2 {
            padding-top: 1.5rem;
        }
        </style>
        """, unsafe_allow_html=True)

    # --- Session Stateの初期化 (すべての初期化を冒頭に集約) ---
    if "all_rallies" not in st.session_state:
        st.session_state.all_rallies = []
    
    initial_form_keys = {
        'rally_start_time_input': "00:00:00",
        'rally_end_time_input': "00:00:00",
        'game_number_input': 1,
        'my_score_input': 0,
        'opponent_score_input': 0,
        'score_loss_type_input': "",
        'serve_player_input': "自分",
        'ball1_type_input': "", 'ball1_course_input': "", 'ball1_quality_input': "",
        'ball2_type_input': "", 'ball2_course_input': "", 'ball2_quality_input': "",
        'ball3_type_input': "", 'ball3_course_input': "", 'ball3_quality_input': "",
        'ball4_type_input': "", 'ball4_course_input': "", 'ball4_quality_input': "",
        'ball5_type_input': "", 'ball5_course_input': "", 'ball5_quality_input': "",
        'ball6_type_input': "", 'ball6_course_input': "", 'ball6_quality_input': "",
        'ball7_onwards_input': "", 'point_tech_type_select': "", 'point_content_input': "",
        'loss_tech_type_select': "", 'loss_content_input': "", 'comment_issue_input': "",
    }

    if 'is_initialized' not in st.session_state:
        st.session_state.editing_rally_index = None
        st.session_state.editing_rally_data = {}
        st.session_state.should_reset_form = False
        
        for key, value in initial_form_keys.items():
            if key not in st.session_state:
                st.session_state[key] = value

        st.session_state.is_initialized = True
    
    # === 修正箇所 1: should_reset_form のロジックを修正 ===
    if st.session_state.should_reset_form:
        # フォーム送信後のリセット
        if st.session_state.get('reset_type') == 'submit':
            my_score = st.session_state.my_score_input
            opponent_score = st.session_state.opponent_score_input
            previous_server = st.session_state.serve_player_input
            next_server = previous_server

            if my_score >= 10 and opponent_score >= 10:
                if (my_score + opponent_score) % 2 == 0:
                    next_server = "相手" if previous_server == "自分" else "自分"
            else:
                if (my_score + opponent_score) % 2 == 0:
                    next_server = "相手" if previous_server == "自分" else "自分"
            
            # Session Stateの値を次のラリーの初期値で更新
            st.session_state.my_score_input = my_score
            st.session_state.opponent_score_input = opponent_score
            st.session_state.serve_player_input = next_server
            
            # フォーム内の項目を初期化
            for key in [k for k in initial_form_keys if k not in ['rally_start_time_input', 'rally_end_time_input', 'game_number_input', 'my_score_input', 'opponent_score_input', 'serve_player_input']]:
                st.session_state[key] = initial_form_keys[key]
        
        # 全データクリア後のリセット
        elif st.session_state.get('reset_type') == 'clear_all':
            for key, value in initial_form_keys.items():
                st.session_state[key] = value

        st.session_state.should_reset_form = False
        st.session_state.reset_type = None # リセットタイプをクリア
        st.rerun()

    # 編集モードの場合、フォームの値を編集対象のラリーデータで上書き
    if st.session_state.editing_rally_index is not None and st.session_state.editing_rally_data:
        editing_data = st.session_state.editing_rally_data
        
        for key, value in editing_data.items():
            session_key = {
                "開始時刻": "rally_start_time_input",
                "終了時刻": "rally_end_time_input",
                "ゲーム数": "game_number_input",
                "自分の得点": "my_score_input",
                "相手の得点": "opponent_score_input",
                "得失点の種類": "score_loss_type_input",
                "誰のサーブか": "serve_player_input",
                "サーブの種類": "ball1_type_input",
                "サーブのコース": "ball1_course_input",
                "サーブの質": "ball1_quality_input",
                "レシーブの種類": "ball2_type_input",
                "レシーブのコース": "ball2_course_input",
                "レシーブの質": "ball2_quality_input",
                "３球目の種類": "ball3_type_input",
                "３球目のコース": "ball3_course_input",
                "３球目の質": "ball3_quality_input",
                "４球目の種類": "ball4_type_input",
                "４球目のコース": "ball4_course_input",
                "４球目の質": "ball4_quality_input",
                "５球目の種類": "ball5_type_input",
                "５球目のコース": "ball5_course_input",
                "５球目の質": "ball5_quality_input",
                "６球目の種類": "ball6_type_input",
                "６球目のコース": "ball6_course_input",
                "６球目の質": "ball6_quality_input",
                "７球目以降": "ball7_onwards_input",
                "得点の種類": "point_tech_type_select",
                "得点の内容": "point_content_input",
                "失点の種類": "loss_tech_type_select",
                "失点の内容": "loss_content_input",
                "コメント・課題": "comment_issue_input"
            }.get(key)
            if session_key:
                # 編集モードではウィジェットに値を直接設定するため、エラーは発生しない
                st.session_state[session_key] = value

        st.session_state.editing_rally_data = {}
        st.rerun()

    # 球種、コース、質の選択肢
    service_types = ["YGサーブ", "YGサーブ上","YGサーブ下","巻込み","巻込み上","巻込み下", 
                     "順横", "順横下", "順横上", "バック", "バック上", "バック下", "キックサーブ", "その他", ""]
    common_tech_types = ["バックドライブ", "バックツッツキ", "バックチキータ", "バックフリック", "バックストップ", "バックブロック",
                   "フォアドライブ", "フォアツッツキ", "フォアフリック", "フォアストップ", "フォア流し", "フォアブロック","フォアスマッシュ", "バックスマッシュ", "ロビング", "その他", ""]
    serve_course_types = ["フォア前", "ミドル前", "バック前", "バックサイド", "フォアサイド", "フォアロング", "ミドルロング", "バックロング", "その他", ""]
    course_types = ["フォア前", "ミドル前", "バック前", "バックサイド", "フォア", "バック", "ミドル", "バック(正面)", "フォアサイド", "その他", ""]
    serve_quality_types = ["良い", "普通", "少し浮いた", "浮いた", "ミス", "台から出てる", ""]
    quality_types = ["良い", "普通", "少し浮いた", "浮いた", "強打", "プッシュ気味", "ループ", "合わせた", "ネットイン", "エッジ", "ミス", ""]
    score_loss_types = ["自分のプレーで得点", "相手のプレーで失点", "相手のミスで得点", "自分のミスで失点", "失点（判断迷う）", "得点（判断迷う）", ""]
    server_types = ["自分", "相手"]
    outcome_tech_types = ["バックドライブ", "フォアドライブ", "サービスエース", "バックチキータ", "フォアフリック", "バックフリック", 
                          "フォアストップ", "バックストップ", "フォアブロック", "バックブロック", "フォアツッツキ", "バックツッツキ", "フォア流し", 
                          "フォアスマッシュ", "バックスマッシュ", "ロビング", "サーブミス", "レシーブミス", "ラリー勝ち", "ラリー負け","相手のプレー", "相手のミス", "その他", ""]
    
    # --- 試合共通データと動画表示設定 ---
    display_common_data_and_video_settings()
    
    st.markdown("---")
    
    # --- ラリー詳細データ入力 ---
    st.subheader("📝 ラリー詳細データ入力")

    with st.form(key='rally_input_form'):
        current_rally_no = len(st.session_state.all_rallies) + 1
        
        if st.session_state.editing_rally_index is not None:
            display_rally_no = st.session_state.all_rallies[st.session_state.editing_rally_index].get('ラリーNo', 'N/A')
            st.markdown(f"**編集中のラリーNo:** {display_rally_no}")
        else:
            st.markdown(f"**ラリーNo (新規入力):** {current_rally_no}")
        
        st.markdown("---")

        col_time_start, col_time_end, col_game, col_my_score, col_opponent_score = st.columns([1, 1, 0.7, 0.7, 0.7])
        with col_time_start:
            st.text_input("開始時刻", key="rally_start_time_input")
        with col_time_end:
            st.text_input("終了時刻", key="rally_end_time_input")
        with col_game:
            st.number_input("ゲーム数", min_value=1, key="game_number_input")
        with col_my_score:
            st.number_input("自分の得点", min_value=0, key="my_score_input")
        with col_opponent_score:
            st.number_input("相手の得点", min_value=0, key="opponent_score_input")

        col_score_loss_type, col_scorer, col_serve_player, col_reset = st.columns([1, 0.7, 0.7, 0.3])
        with col_score_loss_type:
            st.selectbox("得失点の種類", score_loss_types, key="score_loss_type_input")
        with col_scorer:
            scorer = "不明"
            if st.session_state.score_loss_type_input in ["自分のプレーで得点", "相手のミスで得点", "得点（判断迷う）"]:
                scorer = "自分"
            elif st.session_state.score_loss_type_input in ["相手のプレーで失点", "自分のミスで失点", "失点（判断迷う）"]:
                scorer = "相手"
            st.markdown(f"**得点者:** {scorer}")
        with col_serve_player:
            st.selectbox("誰のサーブか", server_types, key="serve_player_input")
        st.markdown("---")

        col_b1t, col_b1c, col_b1q, col_b2t, col_b2c, col_b2q = st.columns(6)
        with col_b1t:
            st.selectbox("サーブの種類", service_types, key="ball1_type_input")
        with col_b1c:
            st.selectbox("サーブのコース", serve_course_types, key="ball1_course_input")
        with col_b1q:
            st.selectbox("サーブの質", serve_quality_types, key="ball1_quality_input")
        with col_b2t:
            st.selectbox("レシーブの種類", common_tech_types, key="ball2_type_input")
        with col_b2c:
            st.selectbox("レシーブのコース", course_types, key="ball2_course_input")
        with col_b2q:
            st.selectbox("レシーブの質", quality_types, key="ball2_quality_input")

        col_b3t, col_b3c, col_b3q, col_b4t, col_b4c, col_b4q = st.columns(6)
        with col_b3t:
            st.selectbox("３球目の種類", common_tech_types, key="ball3_type_input")
        with col_b3c:
            st.selectbox("３球目のコース", course_types, key="ball3_course_input")
        with col_b3q:
            st.selectbox("３球目の質", quality_types, key="ball3_quality_input")
        with col_b4t:
            st.selectbox("４球目の種類", common_tech_types, key="ball4_type_input")
        with col_b4c:
            st.selectbox("４球目のコース", course_types, key="ball4_course_input")
        with col_b4q:
            st.selectbox("４球目の質", quality_types, key="ball4_quality_input")

        col_b5t, col_b5c, col_b5q, col_b6t, col_b6c, col_b6q = st.columns(6)
        with col_b5t:
            st.selectbox("５球目の種類", common_tech_types, key="ball5_type_input")
        with col_b5c:
            st.selectbox("５球目のコース", course_types, key="ball5_course_input")
        with col_b5q:
            st.selectbox("５球目の質", quality_types, key="ball5_quality_input")
        with col_b6t:
            st.selectbox("６球目の種類", common_tech_types, key="ball6_type_input")
        with col_b6c:
            st.selectbox("６球目のコース", course_types, key="ball6_course_input")
        with col_b6q:
            st.selectbox("６球目の質", quality_types, key="ball6_quality_input")

        st.text_input("７球目以降 (自由記述)", key="ball7_onwards_input")

        col_point_tech, col_point_content = st.columns([0.5, 2]) 
        with col_point_tech:
            st.selectbox("得点の種類", outcome_tech_types, key="point_tech_type_select")
        with col_point_content:
            st.text_input("得点の内容 (自由記述)", key="point_content_input")

        col_loss_tech, col_loss_content = st.columns([0.5, 2])
        with col_loss_tech:
            st.selectbox("失点の種類", outcome_tech_types, key="loss_tech_type_select")
        with col_loss_content:
            st.text_input("失点の内容 (自由記述)", key="loss_content_input")

        st.text_input("コメント・課題 (フリー入力)", key="comment_issue_input")

        st.markdown("---")

        if st.session_state.editing_rally_index is not None:
            save_button_label = "ラリーデータを更新"
            current_rally_no_for_data = st.session_state.all_rallies[st.session_state.editing_rally_index].get('ラリーNo', 'N/A')
        else:
            save_button_label = "ラリーデータを保存"
            current_rally_no_for_data = len(st.session_state.all_rallies) + 1

        submitted = st.form_submit_button(save_button_label, use_container_width=True)
        
        if submitted:
            current_rally_data = {
                "ラリーNo": current_rally_no_for_data,
                "自分の戦型": st.session_state.my_style_select,
                "所属": st.session_state.affiliation_input,
                "対戦相手名": st.session_state.opponent_name_input,
                "相手の戦型": st.session_state.opponent_style_select,
                "Youtube Id": st.session_state.youtube_id,
                "開始時刻": st.session_state.rally_start_time_input,
                "終了時刻": st.session_state.rally_end_time_input,
                "ゲーム数": st.session_state.game_number_input,
                "自分の得点": st.session_state.my_score_input,
                "相手の得点": st.session_state.opponent_score_input,
                "得失点の種類": st.session_state.score_loss_type_input,
                "得点者": scorer,
                "誰のサーブか": st.session_state.serve_player_input,
                "サーブの種類": st.session_state.ball1_type_input,
                "サーブのコース": st.session_state.ball1_course_input,
                "サーブの質": st.session_state.ball1_quality_input,
                "レシーブの種類": st.session_state.ball2_type_input,
                "レシーブのコース": st.session_state.ball2_course_input,
                "レシーブの質": st.session_state.ball2_quality_input,
                "３球目の種類": st.session_state.ball3_type_input,
                "３球目のコース": st.session_state.ball3_course_input,
                "３球目の質": st.session_state.ball3_quality_input,
                "４球目の種類": st.session_state.ball4_type_input,
                "４球目のコース": st.session_state.ball4_course_input,
                "４球目の質": st.session_state.ball4_quality_input,
                "５球目の種類": st.session_state.ball5_type_input,
                "５球目のコース": st.session_state.ball5_course_input,
                "５球目の質": st.session_state.ball5_quality_input,
                "６球目の種類": st.session_state.ball6_type_input,
                "６球目のコース": st.session_state.ball6_course_input,
                "６球目の質": st.session_state.ball6_quality_input,
                "７球目以降": st.session_state.ball7_onwards_input,
                "得点の種類": st.session_state.point_tech_type_select,
                "得点の内容": st.session_state.point_content_input,
                "失点の種類": st.session_state.loss_tech_type_select,
                "失点の内容": st.session_state.loss_content_input,
                "コメント・課題": st.session_state.comment_issue_input,
            }

            if st.session_state.editing_rally_index is not None:
                st.session_state.all_rallies[st.session_state.editing_rally_index] = current_rally_data
                st.success(f"ラリー {current_rally_no_for_data} が更新されました！")
                st.session_state.editing_rally_index = None
            else:
                st.session_state.all_rallies.append(current_rally_data)
                st.success(f"ラリーデータが保存されました！ (現在のラリー数: {len(st.session_state.all_rallies)})")
            
            # === 修正箇所 2: リセットタイプをセットして reran() ===
            st.session_state.should_reset_form = True
            st.session_state.reset_type = 'submit'
            st.rerun()
    
    st.markdown("---")
    
    st.subheader("🔍 ラリーIDを指定して編集・削除")
    col_load_id, col_load_button, col_delete_button = st.columns([0.2, 0.4, 0.4])
    with col_load_id:
        rally_id_to_load = st.number_input("ラリーNo", min_value=1, key="rally_id_to_load_input", value=st.session_state.get('rally_id_to_load_input', 1))
    
    with col_load_button:
        st.write("")
        st.write("")
        if st.button("ロードして編集", key="load_rally_by_id_button"):
            found_rally = None
            found_index = -1
            for idx, rally_data in enumerate(st.session_state.all_rallies):
                if rally_data.get("ラリーNo") == rally_id_to_load:
                    found_rally = rally_data
                    found_index = idx
                    break
            
            if found_rally:
                st.session_state.editing_rally_index = found_index
                st.session_state.editing_rally_data = found_rally
                st.session_state.should_reset_form = False
                st.rerun()
            else:
                st.warning(f"ラリーNo {rally_id_to_load} が見つかりませんでした。")

    with col_delete_button:
        st.write("")
        st.write("")
        if st.button("ラリーを削除", key="delete_rally_by_id_button"):
            found_rally = None
            found_index = -1
            for idx, rally_data in enumerate(st.session_state.all_rallies):
                if rally_data.get("ラリーNo") == rally_id_to_load:
                    found_rally = rally_data
                    found_index = idx
                    break
            
            if found_rally:
                del st.session_state.all_rallies[found_index]
                st.success(f"ラリーNo {rally_id_to_load} を削除しました。")
                for i, rally in enumerate(st.session_state.all_rallies):
                    rally["ラリーNo"] = i + 1
                
                st.session_state.editing_rally_index = None
                st.session_state.editing_rally_data = {}
                # === 修正箇所 3: リセットタイプをセットして reran() ===
                st.session_state.should_reset_form = True
                st.session_state.reset_type = 'clear_all'
                st.rerun()
            else:
                st.warning(f"ラリーNo {rally_id_to_load} が見つかりませんでした。")

    st.markdown("---")
    
    st.markdown("#### 📊 入力済みラリーデータ")
    if st.session_state.all_rallies:
        df = pd.DataFrame(st.session_state.all_rallies)
        
        display_columns = [
            "ラリーNo", "開始時刻", "終了時刻", "自分の戦型", "相手の戦型","ゲーム数", "自分の得点", "相手の得点",
            "得失点の種類", "得点者", "誰のサーブか",
            "サーブの種類", "サーブのコース", "サーブの質",
            "レシーブの種類", "レシーブのコース", "レシーブの質",
            "３球目の種類", "３球目のコース", "３球目の質",
            "４球目の種類", "４球目のコース", "４球目の質",
            "５球目の種類", "５球目のコース", "５球目の質",
            "６球目の種類", "６球目のコース", "６球目の質",
            "７球目以降", "得点の種類", "得点の内容", "失点の種類", "失点の内容",
            "コメント・課題"
        ]
        
        valid_display_columns = [col for col in display_columns if col in df.columns]
        st.dataframe(df[valid_display_columns], use_container_width=True, height=300)

        col_download1, col_download2, col_download3 = st.columns(3)
        with col_download1:
            file_name = st.text_input("ダウンロードファイル名", f"ラリー分析_{datetime.date.today()}.xlsx")
        
        df_display = df[valid_display_columns]
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_display.to_excel(writer, sheet_name="試合分析", index=False)
            
            opp_df = pd.DataFrame([{
                "所属": st.session_state.affiliation_input,
                "名前": st.session_state.opponent_name_input,
                "Youtube Id": st.session_state.youtube_id,
                "相手の戦型": st.session_state.opponent_style_select,
                "自分の戦型": st.session_state.my_style_select
            }])
            opp_df.to_excel(writer, sheet_name="対戦者", index=False)

        output.seek(0)
        with col_download2:
            st.download_button(
                label="📥 Excelファイルをダウンロード",
                data=output,
                file_name=file_name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                help="入力したすべてのラリーデータをExcel形式でダウンロードします。"
            )

        with col_download3:
            if st.button("🗑️ 全データをクリア", help="すべての入力済みデータを削除します。元に戻せません。"):
                st.session_state.all_rallies = []
                st.session_state.editing_rally_index = None
                st.session_state.editing_rally_data = {}
                
                # === 修正箇所 4: 直接的な代入を削除し、フラグを立てるのみに ===
                # for key, value in initial_form_keys.items():
                #     st.session_state[key] = value
                
                st.session_state.should_reset_form = True
                st.session_state.reset_type = 'clear_all'
                st.success("すべてのラリーデータとフォームがクリアされました。")
                st.rerun()