import streamlit as st
from ai_config import COMMON_PROMPT_HEADER

# データ抽出用関数のインポート
from score_summary import get_score_summary_for_ai
from match_summary import get_match_summary_for_ai
from serve_receive_analysis import get_serve_receive_analysis_for_ai
from serve_win_rate_analysis import get_serve_win_rate_analysis_for_ai
from serve_rate_transition import get_serve_rate_transition_for_ai
from serve_analysis import get_serve_analysis_for_ai
from overall_receive_analysis import get_overall_receive_analysis_for_ai
from overall_score_miss_analysis import get_overall_score_miss_analysis_for_ai
from first_drive_analysis import get_first_drive_analysis_for_ai
from my_first_play_success_rate import get_my_first_play_success_rate_for_ai
from serve_score_pattern import get_serve_score_pattern_for_ai
from serve_loss_pattern import get_serve_loss_pattern_for_ai
from recieve_score_pattern import get_recieve_score_pattern_for_ai
from recieve_loss_pattern import get_recieve_loss_pattern_for_ai
from previous_ball_analysis import get_previous_ball_analysis_for_ai
from consecutive_ball_analysis import get_consecutive_ball_analysis_for_ai
from game_ending_analysis import get_game_ending_analysis_for_ai
from point_breakdown_analysis import get_point_breakdown_analysis_for_ai
from ai_functions import get_ai_analysis_data # '謎の専属コーチ'用

def display_prompt_card(title, prompt):
    """生成されたプロンプトをコピー可能な形式で画面に表示する共通関数"""
    st.subheader(f"💡 {title}")
    st.info("下の枠内のテキストをコピーして、ChatGPTやGeminiなどのAIツールに貼り付けてください。")
    # 言語をmarkdownに指定することで、AIへの指示、表、リストなどが綺麗に表示され、右上にコピーボタンが出ます
    st.code(prompt.strip(), language="markdown")

def run_overall_analysis(df, df_opponents):
    """全体の分析プロンプトを生成して表示する。"""
    summary_data_for_ai = get_score_summary_for_ai(df)
    match_summary_for_ai = get_match_summary_for_ai(df, df_opponents)
    point_breakdown_analysis_for_ai = get_point_breakdown_analysis_for_ai(df)
    serve_receive_analysis_for_ai = get_serve_receive_analysis_for_ai(df)
    serve_win_rate_analysis_for_ai = get_serve_win_rate_analysis_for_ai(df, '自分')
    serve_rate_analysis_for_ai = get_serve_rate_transition_for_ai(df, '自分')
    serve_analysis_for_ai = get_serve_analysis_for_ai(df)
    overall_receive_analysis_for_ai = get_overall_receive_analysis_for_ai(df)
    overall_analysis_for_ai = get_overall_score_miss_analysis_for_ai(df)
    first_drive_analysis_for_ai = get_first_drive_analysis_for_ai(df)
    my_first_play_analysis_for_ai = get_my_first_play_success_rate_for_ai(df)
    serve_pattern_for_ai = get_serve_score_pattern_for_ai(df)
    serve_loss_pattern_for_ai = get_serve_loss_pattern_for_ai(df)
    recieve_pattern_for_ai = get_recieve_score_pattern_for_ai(df)
    recieve_loss_pattern_for_ai = get_recieve_loss_pattern_for_ai(df)
    previous_ball_analysis_for_ai = get_previous_ball_analysis_for_ai(df)
    consecutive_ball_analysis_for_ai = get_consecutive_ball_analysis_for_ai(df)
    game_ending_analysis_for_ai = get_game_ending_analysis_for_ai(df)

    prompt = f"""
{COMMON_PROMPT_HEADER}
あなたは卓球の優秀な卓球クラブのコーチです。あなたのアドバイスで数々の選手を全国レベルへ引き上げています。
得点・失点データから、この選手の全体的な特徴と、その特徴を活かすための戦術を教えてください。

■試合全体のサマリー:
{match_summary_for_ai}

■試合全体の試合の得失点データ:
{summary_data_for_ai}

■試合全体の得失点の傾向データ: 
{point_breakdown_analysis_for_ai}
特にミスの割合やプレーによる得失点の内訳から、選手が改善すべき点や強みについて考察を加えてください。

■サーブ・レシーブ別得失点分析データ:
{serve_receive_analysis_for_ai}

■サーブ種類別の得点率データ:
{serve_win_rate_analysis_for_ai}

■ゲーム別サーブ種類別得点率の推移データ:
{serve_rate_analysis_for_ai}

■自分のサーブ種類別の得点・失点内容分析データ:
{serve_analysis_for_ai}

■相手サーブコース別のレシーブ分析データ:
{overall_receive_analysis_for_ai}

■全ゲーム合計の得点・失点の種類別集計データ:
{overall_analysis_for_ai}

■どちらが先にドライブを仕掛けたかの分析データ:
{first_drive_analysis_for_ai}

■自分が最初に仕掛けたプレーの成功率データ:
{my_first_play_analysis_for_ai}

■自分のサーブで得点したパターンデータ:
{serve_pattern_for_ai}

■自分のサーブで失点したパターンデータ:
{serve_loss_pattern_for_ai}

■自分のレシーブで得点したパターンデータ:
{recieve_pattern_for_ai}

■自分のレシーブで失点したパターンデータ:
{recieve_loss_pattern_for_ai}

■相手の直前コースと自分の打球技術の成功率データ:
{previous_ball_analysis_for_ai}
※相手の直前コースがバックで自分の打球技術がフォアハンド系の場合には、回り込みフォアの技術の成功率（勝負をかけたときの決定率）を示す。

■連続打球成功率データ:
{consecutive_ball_analysis_for_ai}
※相手コースバック → 自分バックハンド系の成功率が高い場合には、バック対バックで主導権を握れている。
※相手コースフォア → 自分フォアハンド系の成功率が高い場合には、フォア対フォアで主導権を握れている。

■ゲーム序盤・中盤と終盤の得点データ:
{game_ending_analysis_for_ai}
"""
    display_prompt_card("全体分析プロンプト", prompt)


def run_scores_analysis(df, df_opponents):
    """得点源の強化プロンプトを生成して表示する。"""
    summary_data_for_ai = get_score_summary_for_ai(df)
    match_summary_for_ai = get_match_summary_for_ai(df, df_opponents)
    serve_receive_analysis_for_ai = get_serve_receive_analysis_for_ai(df)
    serve_win_rate_analysis_for_ai = get_serve_win_rate_analysis_for_ai(df, '自分')
    serve_rate_analysis_for_ai = get_serve_rate_transition_for_ai(df, '自分')
    serve_analysis_for_ai = get_serve_analysis_for_ai(df)
    overall_receive_analysis_for_ai = get_overall_receive_analysis_for_ai(df)
    overall_analysis_for_ai = get_overall_score_miss_analysis_for_ai(df)
    serve_pattern_for_ai = get_serve_score_pattern_for_ai(df)
    recieve_pattern_for_ai = get_recieve_score_pattern_for_ai(df)

    prompt = f"""
{COMMON_PROMPT_HEADER}
あなたは卓球の優秀なコーチです。あなたのアドバイスで数々の選手を全国レベルへ引き上げています。
得点データから、この選手の得点源を強化するための練習を３つ教えてください。

■試合全体のサマリー:
{match_summary_for_ai}

■試合全体の試合の得失点データ:
{summary_data_for_ai}

■サーブ・レシーブ別得失点分析データ:
{serve_receive_analysis_for_ai}

■サーブ種類別の得点率データ:
{serve_win_rate_analysis_for_ai}

■ゲーム別サーブ種類別得点率の推移データ:
{serve_rate_analysis_for_ai}

■自分のサーブ種類別の得点・失点内容分析データ:
{serve_analysis_for_ai}

■相手サーブコース別のレシーブ分析データ:
{overall_receive_analysis_for_ai}

■全ゲーム合計の得点・失点の種類別集計データ:
{overall_analysis_for_ai}

■自分のサーブで得点したパターンデータ:
{serve_pattern_for_ai}

■自分のレシーブで得点したパターンデータ:
{recieve_pattern_for_ai}
"""
    display_prompt_card("得点源強化プロンプト", prompt)


def run_misses_analysis(df, df_opponents):
    """失点パターンの改善プロンプトを生成して表示する。"""
    summary_data_for_ai = get_score_summary_for_ai(df)
    match_summary_for_ai = get_match_summary_for_ai(df, df_opponents)
    serve_receive_analysis_for_ai = get_serve_receive_analysis_for_ai(df)
    serve_win_rate_analysis_for_ai = get_serve_win_rate_analysis_for_ai(df, '自分')
    serve_rate_analysis_for_ai = get_serve_rate_transition_for_ai(df, '自分')
    serve_analysis_for_ai = get_serve_analysis_for_ai(df)
    overall_receive_analysis_for_ai = get_overall_receive_analysis_for_ai(df)
    overall_analysis_for_ai = get_overall_score_miss_analysis_for_ai(df)
    first_drive_analysis_for_ai = get_first_drive_analysis_for_ai(df)
    my_first_play_analysis_for_ai = get_my_first_play_success_rate_for_ai(df)
    serve_loss_pattern_for_ai = get_serve_loss_pattern_for_ai(df)
    recieve_loss_pattern_for_ai = get_recieve_loss_pattern_for_ai(df)

    prompt = f"""
{COMMON_PROMPT_HEADER}
あなたは卓球の優秀なコーチです。あなたのアドバイスで数々の選手を全国レベルへ引き上げています。
失点データから、この選手の失点源を改善するための練習を３つ教えてください。

■試合全体のサマリー:
{match_summary_for_ai}

■試合全体の試合の得失点データ:
{summary_data_for_ai}

■サーブ・レシーブ別得失点分析データ:
{serve_receive_analysis_for_ai}

■サーブ種類別の得点率データ:
{serve_win_rate_analysis_for_ai}

■ゲーム別サーブ種類別得点率の推移データ:
{serve_rate_analysis_for_ai}

■自分のサーブ種類別の得点・失点内容分析データ:
{serve_analysis_for_ai}

■相手サーブコース別のレシーブ分析データ:
{overall_receive_analysis_for_ai}

■全ゲーム合計の得点・失点の種類別集計データ:
{overall_analysis_for_ai}

■どちらが先にドライブを仕掛けたかの分析データ:
{first_drive_analysis_for_ai}

■自分が最初に仕掛けたプレーの成功率データ:
{my_first_play_analysis_for_ai}

■自分のサーブで失点したパターンデータ:
{serve_loss_pattern_for_ai}

■自分のレシーブで失点したパターンデータ:
{recieve_loss_pattern_for_ai}
"""
    display_prompt_card("失点改善プロンプト", prompt)


def run_coach_analysis(df, df_opponents):
    """謎の専属コーチの分析プロンプトを生成して表示する。"""
    data_to_analyze = get_ai_analysis_data('coach', df)
    match_summary_for_ai = get_match_summary_for_ai(df, df_opponents)
    prompt = f"""
{COMMON_PROMPT_HEADER}
あなたは卓球の選手の父親兼コーチです。でも父親と分からないように謎のコーチを演じてください。
コメントの一覧は父親が息子のプレーを見て感じたことを書いたものです。
選手に寄り添った言葉で、今後のモチベーション向上につながるような温かいアドバイスを２００文字程度でお願いします。

■試合全体のサマリー:
{match_summary_for_ai}

■専属コーチからのコメント:
{data_to_analyze}
"""
    display_prompt_card("謎のコーチ分析プロンプト", prompt)


def run_serve_tactics_analysis(df, df_opponents):
    """サーブ戦術分析プロンプトを生成して表示する。"""
    summary_data_for_ai = get_score_summary_for_ai(df)
    match_summary_for_ai = get_match_summary_for_ai(df, df_opponents)
    serve_receive_analysis_for_ai = get_serve_receive_analysis_for_ai(df)
    serve_win_rate_analysis_for_ai = get_serve_win_rate_analysis_for_ai(df, '自分')
    serve_rate_analysis_for_ai = get_serve_rate_transition_for_ai(df, '自分')
    serve_analysis_for_ai = get_serve_analysis_for_ai(df)
    overall_analysis_for_ai = get_overall_score_miss_analysis_for_ai(df)
    serve_pattern_for_ai = get_serve_score_pattern_for_ai(df)
    serve_loss_pattern_for_ai = get_serve_loss_pattern_for_ai(df)
    prompt = f"""
{COMMON_PROMPT_HEADER}
あなたは卓球の優秀なコーチです。サーブの戦術を分析し、得意パターンと苦手なパターンを教えてあげてください。

■試合全体のサマリー:
{match_summary_for_ai}

■試合全体の試合の得失点データ:
{summary_data_for_ai}

■サーブ・レシーブ別得失点分析データ:
{serve_receive_analysis_for_ai}

■サーブ種類別の得点率データ:
{serve_win_rate_analysis_for_ai}

■ゲーム別サーブ種類別得点率の推移データ:
{serve_rate_analysis_for_ai}

■自分のサーブ種類別の得点・失点内容分析データ:
{serve_analysis_for_ai}

■全ゲーム合計の得点・失点の種類別集計データ:
{overall_analysis_for_ai}

■自分のサーブで得点したパターンデータ:
{serve_pattern_for_ai}

■自分のサーブで失点したパターンデータ:
{serve_loss_pattern_for_ai}
"""
    display_prompt_card("サーブ戦術分析プロンプト", prompt)


def run_receive_tactics_analysis(df, df_opponents):
    """レシーブ戦術分析プロンプトを生成して表示する。"""
    summary_data_for_ai = get_score_summary_for_ai(df)
    match_summary_for_ai = get_match_summary_for_ai(df, df_opponents)
    overall_receive_analysis_for_ai = get_overall_receive_analysis_for_ai(df)
    overall_analysis_for_ai = get_overall_score_miss_analysis_for_ai(df)
    serve_receive_analysis_for_ai = get_serve_receive_analysis_for_ai(df)
    recieve_pattern_for_ai = get_recieve_score_pattern_for_ai(df)
    recieve_loss_pattern_for_ai = get_recieve_loss_pattern_for_ai(df)
    prompt = f"""
{COMMON_PROMPT_HEADER}
あなたは卓球の優秀なコーチです。レシーブの戦術を分析し、得意パターンと苦手なパターンを教えてあげてください。

■試合全体のサマリー:
{match_summary_for_ai}

■試合全体の試合の得失点データ:
{summary_data_for_ai}

■サーブ・レシーブ別得失点分析データ:
{serve_receive_analysis_for_ai}

■相手サーブコース別のレシーブ分析データ:
{overall_receive_analysis_for_ai}

■自分のレシーブで得点したパターンデータ:
{recieve_pattern_for_ai}

■自分のレシーブで失点したパターンデータ:
{recieve_loss_pattern_for_ai}
"""
    display_prompt_card("レシーブ戦術分析プロンプト", prompt)


def run_rally_tactics_analysis(df, df_opponents):
    """ラリー戦術分析プロンプトを生成して表示する。"""
    match_summary_for_ai = get_match_summary_for_ai(df, df_opponents)
    previous_ball_analysis_for_ai = get_previous_ball_analysis_for_ai(df)
    consecutive_ball_analysis_for_ai = get_consecutive_ball_analysis_for_ai(df)

    prompt = f"""
{COMMON_PROMPT_HEADER}
あなたは卓球の優秀なコーチです。ラリーの戦術を分析してください。バック対バックで主導権を握れているのか、フォア対フォアで打ち勝っているのか。

■試合全体のサマリー:
{match_summary_for_ai}

■相手の直前コースと自分の打球技術の成功率データ:
{previous_ball_analysis_for_ai}
※相手の直前コースがバックで自分の打球技術がフォアハンド系の場合には、回り込みフォアの技術の成功率（勝負をかけたときの決定率）を示す。

■連続打球成功率データ:
{consecutive_ball_analysis_for_ai}
※相手コースバック → 自分バックハンド系の成功率が高い場合には、バック対バックで主導権を握れている。
※相手コースフォア → 自分フォアハンド系の成功率が高い場合には、フォア対フォアで主導権を握れている。
"""
    display_prompt_card("ラリー戦術分析プロンプト", prompt)


def run_match_tactics_analysis(df, df_opponents):
    """試合運び(戦術)分析プロンプトを生成して表示する。"""
    match_summary_for_ai = get_match_summary_for_ai(df, df_opponents)
    game_ending_analysis_for_ai = get_game_ending_analysis_for_ai(df)
    prompt = f"""
{COMMON_PROMPT_HEADER}
あなたは卓球の優秀なコーチです。試合運び(戦術)を分析してください。

■試合全体のサマリー:
{match_summary_for_ai}

分析観点１：試合終盤での得点率
分析観点２：試合終盤でのサーブの選択の評価。
　これまで得点率の高かったサーブを選択しているか（成功率は60%を越えているか）。
　今まで選択していないプレーで得点を狙っているか。相手の意表を突くサーブで仕掛けたか。
　どちらが良いか判断は難しいが、意図があるサーブを選択しているか評価してください。

分析観点３：得点と失点の内容から終盤の傾向を分析。
（例：相手が勝負をしかけてきて対応できなかった。自分のミスで崩れた。自分が勝負をかけて勝利。相手がミスで崩れた等）

■ゲーム序盤・中盤と終盤の得点データ:
{game_ending_analysis_for_ai}
"""
    display_prompt_card("試合運び分析プロンプト", prompt)
