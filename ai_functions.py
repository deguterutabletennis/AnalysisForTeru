import streamlit as st
import google.generativeai as genai
import time 

model = genai.GenerativeModel('gemini-1.5-flash')

# --- ユーザーが選択した分析項目とそれに対応するデータを取得する関数 ---
def get_ai_analysis_data(analysis_type, df, tactic_option=None):
    if analysis_type == 'coach':
        # 'コメント・課題'
        return df[['コメント・課題']].to_markdown(index=False)
            
    return ""

# --- AIにプロンプトを送信する関数 ---
def generate_ai_response(prompt_text):
    if st.session_state.gemini_ready:
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt_text)
            st.session_state.ai_response = response.text
        except Exception as e:
            st.error(f"AIとの通信中にエラーが発生しました。詳細: {e}")
            st.session_state.ai_response = "エラーが発生しました。"
    else:
        st.warning("AI機能が利用できません。APIキー設定を確認してください。")
        st.session_state.ai_response = "APIキーが設定されていません。"
