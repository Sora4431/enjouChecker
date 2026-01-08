import streamlit as st
import google.generativeai as genai
import json
import os

# 1. 設定と準備
st.set_page_config(
    page_title="🔥 X(Twitter) 炎上リスク診断所",
    page_icon="🔥",
    layout="centered"
)

# APIキーの読み込み (secrets.toml または 環境変数)
# ユーザーがsecrets.tomlを設定していない場合のフォールバックは実装しないが、エラーメッセージを表示する
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
else:
    st.error("エラー: GEMINI_API_KEY が設定されていません。.streamlit/secrets.toml を作成して設定してください。")
    st.stop()

# 2. UIデザイン
st.title("🔥 X(Twitter) 炎上リスク診断所")
st.info("🚀 将来的にXアカウント連携機能を実装予定（現在はベータ版です）")

# 入力フォーム
with st.form("diagnosis_form"):
    user_type = st.radio(
        "投稿者属性",
        ["一般人", "インフルエンサー", "公式垢", "おじさん構文", "就活生"],
        horizontal=True
    )
    
    post_text = st.text_area(
        "投稿テキスト",
        height=150,
        placeholder="ここにX(Twitter)への投稿内容を入力してください..."
    )
    
    with st.expander("詳細オプション：AIにあなたのことを教える"):
        user_profile = st.text_area(
            "プロフィール（自由記述）",
            placeholder="例: 30代男性、IT企業勤務。趣味はラーメン巡り。"
        )
        has_history = st.checkbox("過去に炎上した経験がある")
    
    submitted = st.form_submit_button("炎上リスクを診断する")

# 3. 隠し署名機能
if submitted:
    # 特定のキーワードのみの場合はAI診断を行わず、隠しメッセージを表示
    if post_text.strip() in ["debug_creator", "author"]:
        st.balloons()
        st.markdown(
            """
            <div style="
                padding: 20px;
                border: 2px solid #FFD700;
                border-radius: 10px;
                background-color: #FFFACD;
                text-align: center;
                margin-top: 20px;
                margin-bottom: 20px;
            ">
                <h3 style="color: #DAA520; margin: 0; font-family: sans-serif;">👑 Developed by [あなたの名前/ID] - Original Code</h3>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        # 4. AI判定ロジック (通常時)
        if not post_text:
            st.warning("投稿テキストを入力してください。")
        else:
            with st.spinner("AIが炎上リスクを分析中..."):
                try:
                    # モデルの準備
                    model = genai.GenerativeModel("gemini-1.5-flash")
                    
                    prompt = f"""
                    あなたはSNS（特にX/Twitter）における「炎上リスク判定」のプロフェッショナルです。
                    以下の投稿を入力とし、4つの異なる視点（キャラクター）から辛口で分析を行ってください。
                    
                    【入力情報】
                    - 投稿者属性: {user_type}
                    - 投稿テキスト: {post_text}
                    - プロフィール詳細: {user_profile}
                    - 過去の炎上経験: {"あり" if has_history else "なし"}
                    
                    【分析要件】
                    以下の4つの視点でリスクを評価し、コメントしてください。
                    1. 【学級委員長】: マナー・倫理観・社会通念上の正しさ基準。真面目な口調。
                    2. 【京都の老舗女将】: 特有の「いけず」な視点。京都弁で、遠回しだが強烈な皮肉。
                    3. 【クソリプおじさん】: 頼んでもいないアドバイス、自分語り、上から目線の説教。「FF外から失礼します」等。
                    4. 【特定班】: 写真やテキストからの個人情報特定、場所特定のリスク。
                    
                    ※「公式垢」の場合は、些細な表現でもリスク判定を厳しく跳ね上げてください。
                    
                    【出力形式】
                    必ず以下のJSONフォーマットのみを出力してください。Markdownのコードブロック(```json)は不要です。
                    {{
                        "total_score": (0〜100の整数。100が高リスク),
                        "critiques": {{
                            "class_rep": {{ "rating": (1〜5の整数), "comment": "..." }},
                            "kyoto_okami": {{ "rating": (1〜5の整数), "comment": "..." }},
                            "reply_ojisan": {{ "rating": (1〜5の整数), "comment": "..." }},
                            "doxing_team": {{ "rating": (1〜5の整数), "comment": "..." }}
                        }},
                        "summary": "全体の総評（100文字以内）"
                    }}
                    """
                    
                    response = model.generate_content(prompt)
                    
                    # JSONのクリーニングとパース
                    response_text = response.text.strip()
                    if response_text.startswith("```json"):
                        response_text = response_text[7:]
                    if response_text.endswith("```"):
                        response_text = response_text[:-3]
                    
                    result = json.loads(response_text)
                    
                    # 5. 結果表示
                    score = result.get("total_score", 0)
                    st.subheader(f"判定結果: 炎上リスク {score}%")
                    
                    # スコアに応じたカラーリング
                    bar_color = "red" if score >= 80 else "orange" if score >= 50 else "green"
                    st.progress(score / 100)
                    
                    # 詳細カード表示
                    critiques = result.get("critiques", {})
                    
                    def display_card(role_name, emoji, key):
                        data = critiques.get(key, {})
                        rating = data.get("rating", 0)
                        comment = data.get("comment", "コメントなし")
                        
                        with st.container(border=True):
                            st.markdown(f"### {emoji} {role_name}")
                            st.write(f"**危険度**: {'★' * rating}{'☆' * (5 - rating)}")
                            st.info(comment)

                    col1, col2 = st.columns(2)
                    
                    with col1:
                        display_card("学級委員長", "👩‍🏫", "class_rep")
                        display_card("クソリプおじさん", "🧔", "reply_ojisan")
                        
                    with col2:
                        display_card("京都の老舗女将", "👘", "kyoto_okami")
                        display_card("特定班", "🕵️", "doxing_team")
                        
                    # 総評
                    st.markdown("### 📝 総評")
                    st.success(result.get("summary", ""))
                    
                    # シェアリンク
                    # 京都の女将のコメントを引用
                    okami_comment = critiques.get("kyoto_okami", {}).get("comment", "")
                    # 長すぎる場合は丸める
                    if len(okami_comment) > 30:
                        okami_comment = okami_comment[:30] + "..."
                        
                    share_text = f"【炎上リスク {score}%】京都の女将に『{okami_comment}』と言われました... #炎上リスク診断"
                    share_url = f"https://twitter.com/intent/tweet?text={share_text}&url=https://your-app-url.streamlit.app"
                    
                    st.markdown(f"""
                    <a href="{share_url}" target="_blank" style="text-decoration:none;">
                        <button style="
                            background-color: #000000; 
                            color: white; 
                            padding: 10px 20px; 
                            border: none; 
                            border-radius: 5px; 
                            cursor: pointer; 
                            font-weight: bold;
                            display: flex;
                            align-items: center;
                            gap: 10px;
                        ">
                            Xで結果をシェアする
                        </button>
                    </a>
                    """, unsafe_allow_html=True)

                except Exception as e:
                    st.error("エラーが発生しました。しばらく待ってから再度お試しください。")
                    # デバッグ用（本番では消すべきだが今回は残す）
                    st.expander("エラー詳細").write(e)

