def display_score_summary(df):
    """
    得失点合計と内訳のUIをモバイルフレンドリーな形式で表示する
    """
    if df.empty or '得失点の種類' not in df.columns or 'ゲーム数' not in df.columns:
        st.warning('スプレッドシートの読み込みに失敗したか、必要な列が見つかりませんでした。')
        return

    st.header('得失点合計と内訳')

    # 得点と失点の種類を定義
    score_types = ['自分のプレーで得点', '相手のミスで得点', '得点（判断迷う）']
    loss_types = ['相手のプレーで失点', '自分のミスで失点', '失点（判断迷う）']

    # 各カテゴリに対応する得点・失点の種類をマッピング
    category_mapping = {
        '自分/相手のプレー': { 'score': '自分のプレーで得点', 'loss': '相手のプレーで失点' },
        '相手/自分のミス': { 'score': '相手のミスで得点', 'loss': '自分のミスで失点' },
        '判断迷う': { 'score': '得点（判断迷う）', 'loss': '失点（判断迷う）' }
    }

    try:
        df['ゲーム数'] = pd.to_numeric(df['ゲーム数'], errors='coerce')
        df = df.dropna(subset=['ゲーム数'])
        df['ゲーム数'] = df['ゲーム数'].astype(int)
    except Exception as e:
        st.error(f"「ゲーム数」列の型変換中にエラーが発生しました。データ形式を確認してください: {e}")
        return

    unique_game_numbers = sorted(df['ゲーム数'].unique())
    
    if not unique_game_numbers:
        st.warning("「ゲーム数」列に有効なデータが見つかりませんでした。")
        return

    final_summary_rows = []
    total_score_overall = 0
    total_loss_overall = 0
    total_player_play_score, total_player_play_loss = 0, 0
    total_opponent_mistake_score, total_opponent_mistake_loss = 0, 0
    total_confusing_score, total_confusing_loss = 0, 0

    for game_num in unique_game_numbers:
        df_game = df[df['ゲーム数'] == game_num]
        score_data = {s_type: df_game[df_game['得失点の種類'] == s_type].shape[0] for s_type in score_types}
        total_score = sum(score_data.values())
        loss_data = {l_type: df_game[df_game['得失点の種類'] == l_type].shape[0] for l_type in loss_types}
        total_loss = sum(loss_data.values())

        player_play_score = score_data.get(category_mapping['自分/相手のプレー']['score'], 0)
        opponent_mistake_score = score_data.get(category_mapping['相手/自分のミス']['score'], 0)
        confusing_score = score_data.get(category_mapping['判断迷う']['score'], 0)
        player_play_loss = loss_data.get(category_mapping['自分/相手のプレー']['loss'], 0)
        opponent_mistake_loss = loss_data.get(category_mapping['相手/自分のミス']['loss'], 0)
        confusing_loss = loss_data.get(category_mapping['判断迷う']['loss'], 0)

        def safe_rate(count, total):
            return f"{count / total * 100:.1f}" if total > 0 else "0.0"

        final_summary_rows.append({
            'ゲーム数': game_num, '種類': '得点', '合計': total_score,
            '自分/相手のプレー': player_play_score, '相手/自分のミス': opponent_mistake_score, '判断迷う': confusing_score,
            '自分/相手のプレー 率 (%)': safe_rate(player_play_score, total_score),
            '相手/自分のミス 率 (%)': safe_rate(opponent_mistake_score, total_score),
            '判断迷う 率 (%)': safe_rate(confusing_score, total_score)
        })
        final_summary_rows.append({
            'ゲーム数': game_num, '種類': '失点', '合計': total_loss,
            '自分/相手のプレー': player_play_loss, '相手/自分のミス': opponent_mistake_loss, '判断迷う': confusing_loss,
            '自分/相手のプレー 率 (%)': safe_rate(player_play_loss, total_loss),
            '相手/自分のミス 率 (%)': safe_rate(opponent_mistake_loss, total_loss),
            '判断迷う 率 (%)': safe_rate(confusing_loss, total_loss)
        })

        total_score_overall += total_score
        total_loss_overall += total_loss
        total_player_play_score += player_play_score
        total_player_play_loss += player_play_loss
        total_opponent_mistake_score += opponent_mistake_score
        total_opponent_mistake_loss += opponent_mistake_loss
        total_confusing_score += confusing_score
        total_confusing_loss += confusing_loss

    final_summary_df = pd.DataFrame(final_summary_rows)
    
    # Total行を追加
    total_score_row = {
        'ゲーム数': 'Total', '種類': '得点', '合計': total_score_overall,
        '自分/相手のプレー': total_player_play_score, '相手/自分のミス': total_opponent_mistake_score, '判断迷う': total_confusing_score,
        '自分/相手のプレー 率 (%)': safe_rate(total_player_play_score, total_score_overall),
        '相手/自分のミス 率 (%)': safe_rate(total_opponent_mistake_score, total_score_overall),
        '判断迷う 率 (%)': safe_rate(total_confusing_score, total_score_overall)
    }
    total_loss_row = {
        'ゲーム数': 'Total', '種類': '失点', '合計': total_loss_overall,
        '自分/相手のプレー': total_player_play_loss, '相手/自分のミス': total_opponent_mistake_loss, '判断迷う': total_confusing_loss,
        '自分/相手のプレー 率 (%)': safe_rate(total_player_play_loss, total_loss_overall),
        '相手/自分のミス 率 (%)': safe_rate(total_opponent_mistake_loss, total_loss_overall),
        '判断迷う 率 (%)': safe_rate(total_confusing_loss, total_loss_overall)
    }
    
    final_summary_df = pd.concat([
        final_summary_df,
        pd.DataFrame([total_score_row, total_loss_row])
    ], ignore_index=True)
    
    # 'ゲーム数' 列を文字列型に変換して、'Total'を含むことができるようにする
    final_summary_df['ゲーム数'] = final_summary_df['ゲーム数'].astype(str)

    # 全体の合計得失点数を表示
    st.subheader("試合全体の得失点合計")
    total_df = final_summary_df[final_summary_df['ゲーム数'] == 'Total'].set_index('種類')
    
    col_score_total, col_loss_total = st.columns(2)
    with col_score_total:
        st.markdown("##### 得点合計")
        st.table(total_df[['合計', '自分/相手のプレー', '相手/自分のミス', '判断迷う']].loc[['得点']])
    with col_loss_total:
        st.markdown("##### 失点合計")
        st.table(total_df[['合計', '自分/相手のプレー', '相手/自分のミス', '判断迷う']].loc[['失点']])
    
    st.markdown("---")
    
    # ゲームごとの詳細をアコーディオンで表示
    st.subheader("ゲームごとの詳細")
    for game_num in unique_game_numbers:
        with st.expander(f"ゲーム {game_num} の詳細を見る"):
            game_df = final_summary_df[final_summary_df['ゲーム数'] == str(game_num)].set_index('種類')
            
            col_game_score, col_game_loss = st.columns(2)
            with col_game_score:
                st.markdown("##### 得点")
                st.table(game_df[['合計', '自分/相手のプレー', '相手/自分のミス', '判断迷う']].loc[['得点']])
            with col_game_loss:
                st.markdown("##### 失点")
                st.table(game_df[['合計', '自分/相手のプレー', '相手/自分のミス', '判断迷う']].loc[['失点']])


def get_score_summary_for_ai(df):
    """
    試合の得失点合計と内訳をMarkdown形式の文字列として生成する
    """
    if df.empty or '得失点の種類' not in df.columns or 'ゲーム数' not in df.columns:
        return "試合結果のサマリーデータが利用できません。"

    # 得点と失点の種類を定義
    score_types = ['自分のプレーで得点', '相手のミスで得点', '得点（判断迷う）']
    loss_types = ['相手のプレーで失点', '自分のミスで失点', '失点（判断迷う）']

    # 各カテゴリに対応する得点・失点の種類をマッピング
    category_mapping = {
        '自分/相手のプレー': { 'score': '自分のプレーで得点', 'loss': '相手のプレーで失点' },
        '相手/自分のミス': { 'score': '相手のミスで得点', 'loss': '自分のミスで失点' },
        '判断迷う': { 'score': '得点（判断迷う）', 'loss': '失点（判断迷う）' }
    }

    try:
        df['ゲーム数'] = pd.to_numeric(df['ゲーム数'], errors='coerce')
        df = df.dropna(subset=['ゲーム数'])
        df['ゲーム数'] = df['ゲーム数'].astype(int)
    except Exception:
        return "試合結果のサマリーデータ生成中にエラーが発生しました。"

    unique_game_numbers = sorted(df['ゲーム数'].unique())
    if not unique_game_numbers:
        return "試合結果のサマリーデータが利用できません。"

    final_summary_rows = []
    total_score_overall = 0
    total_loss_overall = 0
    total_player_play_score, total_player_play_loss = 0, 0
    total_opponent_mistake_score, total_opponent_mistake_loss = 0, 0
    total_confusing_score, total_confusing_loss = 0, 0

    for game_num in unique_game_numbers:
        df_game = df[df['ゲーム数'] == game_num]
        score_data = {s_type: df_game[df_game['得失点の種類'] == s_type].shape[0] for s_type in score_types}
        total_score = sum(score_data.values())
        loss_data = {l_type: df_game[df_game['得失点の種類'] == l_type].shape[0] for l_type in loss_types}
        total_loss = sum(loss_data.values())

        player_play_score = score_data.get(category_mapping['自分/相手のプレー']['score'], 0)
        opponent_mistake_score = score_data.get(category_mapping['相手/自分のミス']['score'], 0)
        confusing_score = score_data.get(category_mapping['判断迷う']['score'], 0)
        player_play_loss = loss_data.get(category_mapping['自分/相手のプレー']['loss'], 0)
        opponent_mistake_loss = loss_data.get(category_mapping['相手/自分のミス']['loss'], 0)
        confusing_loss = loss_data.get(category_mapping['判断迷う']['loss'], 0)

        total_score_overall += total_score
        total_loss_overall += total_loss
        total_player_play_score += player_play_score
        total_player_play_loss += player_play_loss
        total_opponent_mistake_score += opponent_mistake_score
        total_opponent_mistake_loss += opponent_mistake_loss
        total_confusing_score += confusing_score
        total_confusing_loss += confusing_loss
    
    # 最終的な集計をDataFrameにまとめる
    final_summary_df = pd.DataFrame([
        {
            '種類': '得点', '合計': total_score_overall,
            'プレーでの得点': total_player_play_score,
            '相手ミスでの得点': total_opponent_mistake_score,
            '判断迷う得点': total_confusing_score
        },
        {
            '種類': '失点', '合計': total_loss_overall,
            'プレーでの失点': total_player_play_loss,
            '自分のミスでの失点': total_opponent_mistake_loss,
            '判断迷う失点': total_confusing_loss
        }
    ])

    # AIに渡すためのMarkdown形式に変換
    summary_markdown = final_summary_df.to_markdown(index=False)
    
    return f"試合全体の得失点合計と内訳:\n\n{summary_markdown}"
