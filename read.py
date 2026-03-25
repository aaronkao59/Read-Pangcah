import streamlit as st
import re
import random
from gtts import gTTS
import io
import os

# --- 1. 頁面配置與自適應 CSS ---
st.set_page_config(page_title="菁英朗讀訓練機", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    /* 詞卡：自適應深淺色模式 */
    .word-card {
        border: 2px solid #4CAF50;
        border-radius: 15px;
        padding: 30px 10px;
        text-align: center;
        background-color: var(--secondary-bg-color); 
        color: var(--text-color);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        margin-bottom: 20px;
        min-height: 120px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    .stButton > button {
        width: 100%;
        padding: 0.5rem 0.2rem !important;
        font-size: 0.9rem !important;
        border-radius: 8px;
    }
    .cn-text-box {
        color: var(--text-color);
        background-color: rgba(76, 175, 80, 0.15); 
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #4CAF50;
        margin: 10px 0;
        line-height: 1.6;
        font-size: 0.95rem;
    }
    [data-testid="column"] { padding: 0 2px !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. 五篇文章數據庫 ---
# 這裡建議將所有文章資訊封裝在一個大字典裡
ARTICLES = {
    "Dadaya no niyaro’": {
        "raw_text": """（Mahakakerem ko romi’ad, matengil to ko soni no tanikay,）（ satapang saho sa afesa’ sa makaleng ko soni, ）（matenes to mato mafana’ay a misalof to soni,safangcal sato a matengil. ）（Yo madodem to ko kakarayan masadak to ko fo’is,）（ mato sonol sanay to ko soni, sa fangcal sato a tengilen.）\n\n（O malingaday a maemin, sadak saho ko cidal lomowad to talakatayalan, ）（tangasa sa micelem ko cidal ta minokay a pahanhan, ）（deng to no romi’ad sa, mi’orongto to pitaw malalitemoh i rihi’ no facal sedi sa matatawa a malalicay,）（ masasipalemed, ko nanay makadofah ko kinaira toni a mihecaan ato pali’ayaw to saki no dafak a tatayalen. ）（Tada masinanotay, damsayay, fangcalay a niyaro’ koni.）\n\n（Masadak to ko folad, seriw seriw sa ko fali,）（ nengneng han ko lawac no lalan macelak to ko hana. ）（Mato maemin masafaeloh masanek ko fali nona pala, seriw seriw sa nai rengorengosan. ）（Tengil han to ko soni no tanikay ngalengalef saan mato pasenengay, ）（masinanot mato pahinoker sanay to tona palapalaan a masoni.）\n\n（Sacikacikay sa i pawalian to panay a malawla ko wawa, ）（o mato’asay sa maro’ i falaw mahaholol, pakimad. ）（O fafahiyan sa i, mitapid to macicihay a riko’, roma i, miparpar to pinawali a padaka. ）（Talacowa caay ka samaan ko ’orip i niyaro’,）（ nika nengneng han ko tamdaw maemin lipahak lihaday makadofah ko ’orip.）\n\n（Mato caho katenes ko ’aro, kafahalan sa o tenok to no lafii, ）（tengil han cecacecay to ko soni, lahedaw sato ko soni no tanikay, ）（o folad mamicelem to, polong no hekal maemin to awa to ko ades’es no soni. ）（talalemed to ko tamdamdaw a mafoti’, patedi han no folad ko widawidan no panay,）（ seriw seriw han no fali sa matiya sa o tapelik no riyar a manengneng.）\n\n（Caho ka taengad ko romi’ad, mi’orong to to sakatayal mililis to rihi’ no omah ko malingaday, ）（misatapang to malingad a matayal. ）（Caho caho katenes conihal to ko wali masadak to ko matiyaay o lamal a cidal patedi to hekal, ）（sa maliemi sato ko o’ol i rengorengosan ato i papah no kilang a manengneng. ）（Satapang to rarawraw ko tamdaw no niyaro’, ）（o mitiliday sa matatawatawa to i lalan talapitilidan,）（ o satapangan to no niyaro’ koni a romi’ad.）""",
        "sent_trans": ["傍晚時分，聽見了蟬鳴聲，", "起初聲音斷斷續續，", "久了似乎熟練了鳴叫，變得悅耳。", "當天空變暗星星出現，", "聲音像是順流而下般好聽。", "耕作的人，太陽剛出來就起床去工作，", "直到夕陽西下才回家休息，", "整天辛苦工作，扛著鋤頭在田埂邊相遇，說笑聊天，", "互相祝福，希望今年產量豐收，也為明天的工作預備。", "這是一個整潔、溫馨、美麗的部落。", "月亮出來了，涼風徐徐，", "看那路邊花朵盛開。", "大地似乎充滿了清新的氣息，從草叢中傳來陣陣涼風。", "聽那蟬鳴聲更加響亮，彷彿在誇耀，", "像是讓這片大地平靜下來般鳴叫著。", "孩子們在曬穀場跑來跑去玩耍，", "長者坐在走廊聊天、講故事。", "婦女們在縫補破舊的衣服，或者在整理曝曬的乾菜。", "雖然部落生活簡單，", "但看每個人都過得快樂安詳、生活充實。", "坐沒多久，突然到了深夜，", "聽見聲音一個個消失，蟬鳴聲不見了，", "月亮要下山了，全世界靜悄悄。", "人們進入夢鄉，月光照在稻穗上，", "微風吹過像海浪波動。", "天還沒亮，農夫出發工作。", "太陽照耀大地。", "露珠閃閃發亮。", "部落開始喧鬧。", "這是部落一天的開始。"],
        "para_trans": ["傍晚蟬鳴悅耳，星空降臨。", "農夫勤奮工作，部落溫馨美麗。", "月夜花開，大地清涼安靜。", "族人生活簡單快樂，各司其職。", "深夜萬物靜寂，入夢安眠。", "黎明再次來臨，開啟新的一天。"]
    },
    "第二篇文章名稱": {"raw_text": "（內容預留...）", "sent_trans": ["..."], "para_trans": ["..."]},
    "第三篇文章名稱": {"raw_text": "（內容預留...）", "sent_trans": ["..."], "para_trans": ["..."]},
    "第四篇文章名稱": {"raw_text": "（內容預留...）", "sent_trans": ["..."], "para_trans": ["..."]},
    "第五篇文章名稱": {"raw_text": "（內容預留...）", "sent_trans": ["..."], "para_trans": ["..."]}
}

# --- 3. 初始化與側邊欄切換 ---
st.sidebar.title("📚 文章選擇")
selected_title = st.sidebar.selectbox("請選擇練習文章：", list(ARTICLES.keys()))

# 當更換文章時，重置所有狀態
if 'last_article' not in st.session_state or st.session_state.last_article != selected_title:
    st.session_state.last_article = selected_title
    st.session_state.w_idx = 0
    st.session_state.w_flip = False
    # 這裡可以根據文章動態生成生詞表 (略，假設使用同一個 translation_map 或根據內容提取)

# 載入當前文章數據
current_data = ARTICLES[selected_title]

# --- 4. 功能函數 ---
def get_audio_source(text, type="word", index=0, article=""):
    # 物理路徑：audio/文章名/類別/檔名.mp3
    safe_title = article.replace(" ", "_")
    if type == "word":
        path = f"audio/{safe_title}/words/{text}.mp3"
    else:
        path = f"audio/{safe_title}/sentences/s{index}.mp3"
    
    if os.path.exists(path): return path
    try:
        tts = gTTS(text=text, lang='it')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        return fp
    except: return None

# --- 5. App 介面實作 ---
st.title(f"🎙️ {selected_title}")
tab_list = ["🎴 生詞詞卡", "📏 單句朗讀訓練", "📄 段落練習"]
tabs = st.tabs(tab_list)

# --- Tab 1: 生詞詞卡 ---
with tabs[0]:
    # 這裡我們仍使用您之前的詞彙字典，您可以根據每篇文章擴充它
    word_list = sorted(list(translation_map.keys())) # 假設 translation_map 已定義在上方
    curr_w = word_list[st.session_state.w_idx]
    display = translation_map[curr_w] if st.session_state.w_flip else curr_w
    
    st.markdown(f'<div class="word-card"><h2>{display}</h2><p>{st.session_state.w_idx+1}/{len(word_list)}</p></div>', unsafe_allow_html=True)
    
    cols = st.columns([1, 1, 1, 1, 1.2])
    if cols[0].button("⬅️ 往前", key="prev"):
        st.session_state.w_idx = (st.session_state.w_idx - 1) % len(word_list)
        st.session_state.w_flip = False
        st.rerun()
    if cols[1].button("🔊 發音", key="play_w"):
        src = get_audio_source(curr_w, "word", article=selected_title)
        if src: st.audio(src)
    if cols[2].button("➡️ 向後", key="next"):
        st.session_state.w_idx = (st.session_state.w_idx + 1) % len(word_list)
        st.session_state.w_flip = False
        st.rerun()
    if cols[3].button("🔀 隨機", key="rand"):
        random.shuffle(word_list)
        st.rerun()
    if cols[4].button("🔄 翻轉/中文", key="flip"):
        st.session_state.w_flip = not st.session_state.w_flip
        st.rerun()

# --- Tab 2: 單句朗讀訓練 ---
with tabs[1]:
    sents = re.findall(r'（(.*?)）', current_data["raw_text"], re.DOTALL)
    for i, s in enumerate(sents):
        s = s.strip()
        with st.container():
            st.info(s)
            # 展開中文框
            if st.session_state.get(f"s_cn_show_{selected_title}_{i}", False):
                cn_text = current_data["sent_trans"][i] if i < len(current_data["sent_trans"]) else "無翻譯"
                st.markdown(f'<div class="cn-text-box">{cn_text}</div>', unsafe_allow_html=True)
            
            # 顯示中文按鈕 (在中文框下方)
            if st.button("顯示/隱藏中文翻譯", key=f"btn_s_{selected_title}_{i}"):
                key = f"s_cn_show_{selected_title}_{i}"
                st.session_state[key] = not st.session_state.get(key, False)
                st.rerun()
            
            # 播放與評分列
            c1, c2 = st.columns([1, 2])
            if c1.button("🔊 播放", key=f"p_s_{selected_title}_{i}"):
                src = get_audio_source(s, "sent", index=i, article=selected_title)
                if src: st.audio(src)
            c2.radio("評分", ["未通過", "待加強", "通過"], key=f"chk_s_{selected_title}_{i}", horizontal=True, label_visibility="collapsed")
            st.divider()

# --- Tab 3: 段落練習 ---
with tabs[2]:
    paras = [p.strip() for p in current_data["raw_text"].split('\n\n') if p.strip()]
    for i, p in enumerate(paras):
        clean_p = re.sub(r'[（）]', '', p)
        with st.expander(f"第 {i+1} 段", expanded=True):
            st.write(clean_p)
            c1, c2 = st.columns([1, 2])
            if c1.button("🔊 播放全段", key=f"p_p_{selected_title}_{i}"):
                # 這裡調用 gTTS 播放全段
                tts = gTTS(text=clean_p, lang='it')
                fp = io.BytesIO()
                tts.write_to_fp(fp)
                st.audio(fp)
            c2.radio("評分", ["未通過", "待加強", "通過"], key=f"chk_p_{selected_title}_{i}", horizontal=True, label_visibility="collapsed")
