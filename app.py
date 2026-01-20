import streamlit as st
import google.generativeai as genai
import json
import os
import urllib.parse
import pandas as pd
import altair as alt

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
        ["一般人", "インフルエンサー", "公式垢", "就活生"],
        horizontal=True
    )
    
    user_age = st.number_input(
        "年齢",
        min_value=0,
        max_value=120,
        value=30,
        step=1
    )
    
    post_text = st.text_area(
        "投稿テキスト",
        height=150,
        placeholder="ここにX(Twitter)への投稿内容を入力してください..."
    )
    
    with st.expander("詳細オプション：AIにあなたのことを教える"):
        user_profile = st.text_area(
            "プロフィール（自由記述）",
            placeholder="例: IT企業勤務。趣味はラーメン巡り。"
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
                    model = genai.GenerativeModel("gemini-2.5-flash")
                    
                    prompt = f"""
                    あなたはSNS（特にX/Twitter）における「炎上リスク判定」のプロフェッショナルです。
                    以下の投稿を入力とし、4つの異なる視点（キャラクター）から辛口で分析を行ってください。
                    加えて、日本国内の地域ごとの文化摩擦（関東vs関西、食文化、方言など）についても分析してください。
                    
                    【入力情報】
                    - 投稿者属性: {user_type}
                    - 年齢: {user_age}歳
                    - 投稿テキスト: {post_text}
                    - プロフィール詳細: {user_profile}
                    - 過去の炎上経験: {"あり" if has_history else "なし"}
                    
                    【分析要件】
                    年齢は炎上リスク判定において重要な要素です。若年層と高年層で求められる表現や言葉遣いが異なり、
                    年齢に不相応な表現は炎上のリスクを高める傾向があります。年齢を考慮した上で、以下の4つの視点でリスクを評価し、コメントしてください。
                                        評価は0から5の整数で行い、0は炎上要素が全くない場合に使用してください。
                    1. 【学級委員長】: マナー・倫理観・社会通念上の正しさ基準。真面目な口調。
                    2. 【京都の老舗女将】: 特有の「いけず」な視点。京都弁で、遠回しだが強烈な皮肉。
                    3. 【クソリプおじさん】: 頼んでもいないアドバイス、自分語り、上から目線の説教。「FF外から失礼します」等。
                    4. 【特定班】: 写真やテキストからの個人情報特定、場所特定のリスク。
                    
                    ※「公式垢」の場合は、些細な表現でもリスク判定を厳しく跳ね上げてください。
                    
                    【言語判定】
                    投稿テキストの言語を自動判定してください。主に日本語、英語、その他の言語が対象です。
                    言語に基づいて、以下の地域での炎上リスクを評価します。

                    【地域分析要件】
                    投稿内容が以下の主要な地域/圏域で反感を買う可能性を分析してください。
                    言語判定と投稿内容に基づいて、適切な地域を優先的に分析してください。
                    
                    - 【日本】: 日本国内での文化摩擦（関東vs関西、食文化、方言など）。日本語投稿が対象。
                    - 【アジア】: アジア太平洋地域での文化的反感。言語に関わらず政治的・文化的問題が対象。
                    - 【アメリカ】: 英語圏、特に米国での反感。人種問題、政治的立場、文化的違いなど。
                    - 【ヨーロッパ】: EU圏での反感。ナチス・差別・規制に敏感。GDPR等の規制も配慮。
                    - 【グローバル】: 上記以外の地域または普遍的な問題（環境問題、人権など）。
                    
                    【出力形式】
                    必ず以下のJSONフォーマットのみを出力してください。Markdownのコードブロック(```json)は不要です。
                    {{
                        "total_score": (0〜100の整数。100が高リスク),
                        "detected_language": ("日本語", "英語", "その他" など),
                        "critiques": {{
                            "class_rep": {{ "rating": (0〜5の整数。0は炎上要素なし), "comment": "..." }},
                            "kyoto_okami": {{ "rating": (0〜5の整数。0は炎上要素なし), "comment": "..." }},
                            "reply_ojisan": {{ "rating": (0〜5の整数。0は炎上要素なし), "comment": "..." }},
                            "doxing_team": {{ "rating": (0〜5の整数。0は炎上要素なし), "comment": "..." }}
                        }},
                        "regional_analysis": [
                            {{ "region": "日本", "risk_score": (0〜100), "reason": "..." }},
                            {{ "region": "アジア", "risk_score": (0〜100), "reason": "..." }},
                            {{ "region": "アメリカ", "risk_score": (0〜100), "reason": "..." }},
                            {{ "region": "ヨーロッパ", "risk_score": (0〜100), "reason": "..." }},
                            {{ "region": "グローバル", "risk_score": (0〜100), "reason": "..." }}
                        ],
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

                    # 評価の正規化（0〜5）と総合スコア再計算
                    critiques = result.get("critiques", {})
                    critique_keys = ["class_rep", "kyoto_okami", "reply_ojisan", "doxing_team"]

                    def normalize_rating(val):
                        try:
                            return max(0, min(5, int(val)))
                        except Exception:
                            return 0

                    normalized_ratings = []
                    for key in critique_keys:
                        rating = normalize_rating(critiques.get(key, {}).get("rating", 0))
                        # critiques内に整形済みのratingを戻して後段表示でも使用
                        if key not in critiques:
                            critiques[key] = {}
                        critiques[key]["rating"] = rating
                        normalized_ratings.append(rating)

                    rating_based_score = round((sum(normalized_ratings) / len(normalized_ratings)) * 20) if normalized_ratings else 0

                    raw_total_score = result.get("total_score")
                    if raw_total_score is None:
                        score = rating_based_score
                    else:
                        try:
                            clamped = max(0, min(100, int(raw_total_score)))
                        except Exception:
                            clamped = rating_based_score
                        # モデル出力を尊重しつつ、0-5評価から計算したスコアとも整合
                        score = max(clamped, rating_based_score)

                    # 5. 結果表示
                    st.subheader(f"判定結果: 炎上リスク {score}%")
                    
                    # スコアに応じたカラーリング
                    bar_color = "red" if score >= 80 else "orange" if score >= 50 else "green"
                    st.progress(score / 100)

                    # 地域別リスク可視化
                    st.subheader("🗺️ 地域別炎上リスク")
                    regional_data = result.get("regional_analysis", [])
                    
                    if regional_data:
                        try:
                            # データの整形
                            regions = [item["region"] for item in regional_data]
                            scores = [item["risk_score"] for item in regional_data]
                            
                            df_regional = pd.DataFrame({"地域": regions, "リスクスコア": scores})
                            
                            # Altairでグラフを作成してY軸を0-100に固定
                            chart = alt.Chart(df_regional).mark_bar().encode(
                                x=alt.X('地域:N', axis=alt.Axis(labelAngle=0)),
                                y=alt.Y('リスクスコア:Q', scale=alt.Scale(domain=[0, 100]))
                            ).properties(height=400)
                            
                            st.altair_chart(chart, use_container_width=True)
                            
                            # 高リスク地域の警告
                            for item in regional_data:
                                if item.get("risk_score", 0) >= 60:
                                    st.warning(f"⚠️ **{item['region']}** 警戒: {item['reason']}")
                        except Exception as e:
                            st.error(f"地域分析の表示中にエラーが発生しました: {e}")
                    
                    # 詳細カード表示
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
                    encoded_text = urllib.parse.quote(share_text)
                    encoded_url = urllib.parse.quote("https://enjouchecker.streamlit.app/")
                    share_url = f"https://x.com/intent/tweet?text={encoded_text}&url={encoded_url}"
                    
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

