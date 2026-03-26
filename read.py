import streamlit as st
import re
import random
from gtts import gTTS
import io
import os

# --- 1. 頁面配置與自適應 CSS ---
# 將分頁標題設定為「菁英朗讀訓練」
st.set_page_config(page_title="菁英朗讀訓練", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>

  /*  st.title("菁英朗讀訓練") 的字型大小與樣式設定 */
    h1 {
        font-size: 2.5rem !important; /* 你可以調整這個數值，rem 是相對單位，32px 約為 2rem */
        font-weight: 800 !important;
        color: #43A047; /* 你也可以指定顏色 */
        text-align: left; /* 讓標題置中，手機看會更美觀 */
        padding-bottom: 20px;
    }
    
    /* 詞卡：自適應深淺色模式變數 */
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
    
    /* 按鈕樣式優化 */
    .stButton > button {
        width: 100%;
        padding: 0.5rem 0.2rem !important;
        font-size: 0.9rem !important;
        border-radius: 8px;
    }

    /* 中文翻譯框：使用透明度綠色確保全模式清晰 */
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

# --- 2. 全域生詞主字典 (MASTER_DICT) ---
# 所有的文章生詞翻譯都集中在這裡，方便統一管理
MASTER_DICT = {
    "Mahakakerem": "傍晚/天快黑時", "matengil": "聽見/聽到", "tanikay": "蟬", "satapang": "開始", 
    "afesa’": "響亮/嘶鳴", "makaleng": "清亮/嘹亮", "matenes": "很久", "mafana’ay": "會/明白", 
    "misalof": "修理/修正", "safangcal": "變美/變好", "madodem": "變暗/陰暗", "kakarayan": "天空", 
    "masadak": "出現/出來", "tengilen": "聽", "malingaday": "耕作的人/農夫", "lomowad": "起床/出發", 
    "talakatayalan": "工作的地方", "tangasa": "到達", "micelem": "沒入/落山", "minokay": "回家", 
    "pahanhan": "休息", "mi’orongto": "扛著", "malalitemoh": "相遇/遇見", "malalicay": "交談/聊天", 
    "masasipalemed": "互相祝福", "makadofah": "豐富/豐收", "kinaira": "產量/獲收", "mihecaan": "年度/年", 
    "pali’ayaw": "預備/準備", "tatayalen": "要做的工作", "masinanotay": "整潔的", "damsayay": "溫暖/親切", 
    "fangcalay": "美麗的/好的", "niyaro’": "部落", "macelak": "盛開/綻放", "masafaeloh": "全新的/變新", 
    "masanek": "氣味/聞起來", "rengorengosan": "草叢", "ngalengalef": "更加/越發", "pasenengay": "誇耀/自豪", 
    "masinanot": "整潔/有條理", "pahinoker": "平靜/安靜", "palapalaan": "大地/荒野", "sacikacikay": "跑來跑去", 
    "pawalian": "曬穀場", "malawla": "嬉戲/玩耍", "mato’asay": "長者/老人", "mahaholol": "聊天/聚談", 
    "pakimad": "講故事", "fafahiyan": "女性/婦女", "mitapid": "縫補/編織", "macicihay": "破舊的", 
    "miparpar": "鋪開/攤開", "pinawali": "曝曬", "lipahak": "快樂", "lihaday": "安詳/自在", 
    "katenes": "很久", "kafahalan": "突然/深夜", "cecacecay": "一個接一個", "lahedaw": "消失/不見", 
    "ades’es": "吵雜/喧鬧", "talalemed": "入夢/幸運", "mafoti’": "睡覺", "widawidan": "稻穗", 
    "manengneng": "看見/看到", "taengad": "天亮/黎明", "sakatayal": "工具/器具", "mililis": "沿著邊緣", 
    "misatapang": "開始(做)", "conihal": "放晴/太陽出來", "matiyaay": "像是...一樣", "rarawraw": "喧嘩/吵鬧", 
    "mitiliday": "學生/讀書的人", "talapitilidan": "學校", "satapangan": "開始/起頭"
}

# --- 3. 文章數據庫 (ARTICLES) ---
ARTICLES = {
    "Dadaya no niyaro’": {
        "raw_text": """（Mahakakerem ko romi’ad, matengil to ko soni no tanikay,）（ satapang saho sa afesa’ sa makaleng ko soni, ）（matenes to mato mafana’ay a misalof to soni,safangcal sato a matengil. ）（Yo madodem to ko kakarayan masadak to ko fo’is,）（ mato sonol sanay to ko soni, sa fangcal sato a tengilen.）\n\n（O malingaday a maemin, sadak saho ko cidal lomowad to talakatayalan, ）（tangasa sa micelem ko cidal ta minokay a pahanhan, ）（deng to no romi’ad sa, mi’orongto to pitaw malalitemoh i rihi’ no facal sedi sa matatawa a malalicay,）（ masasipalemed, ko nanay makadofah ko kinaira toni a mihecaan ato pali’ayaw to saki no dafak a tatayalen. ）（Tada masinanotay, damsayay, fangcalay a niyaro’ koni.）\n\n（Masadak to ko folad, seriw seriw sa ko fali,）（ nengneng han ko lawac no lalan macelak to ko hana. ）（Mato maemin masafaeloh masanek ko fali nona pala, seriw seriw sa nai rengorengosan. ）（Tengil han to ko soni no tanikay ngalengalef saan mato pasenengay, ）（masinanot mato pahinoker sanay to tona palapalaan a masoni.）\n\n（Sacikacikay sa i pawalian to panay a malawla ko wawa, ）（o mato’asay sa maro’ i falaw mahaholol, pakimad. ）（O fafahiyan sa i, mitapid to macicihay a riko’, roma i, miparpar to pinawali a padaka. ）（Talacowa caay ka samaan ko ’orip i niyaro’,）（ nika nengneng han ko tamdaw maemin lipahak lihaday makadofah ko ’orip.）\n\n（Mato caho katenes ko ’aro, kafahalan sa o tenok to no lafii, ）（tengil han cecacecay to ko soni, lahedaw sato ko soni no tanikay, ）（o folad mamicelem to, polong no hekal maemin to awa to ko ades’es no soni. ）（talalemed to ko tamdamdaw a mafoti’, patedi han no folad ko widawidan no panay,）（ seriw seriw han no fali sa matiya sa o tapelik no riyar a manengneng.）\n\n（Caho ka taengad ko romi’ad, mi’orong to to sakatayal mililis to rihi’ no omah ko malingaday, ）（misatapang to malingad a matayal. ）（Caho caho katenes conihal to ko wali masadak to ko matiyaay o lamal a cidal patedi to hekal, ）（sa maliemi sato ko o’ol i rengorengosan ato i papah no kilang a manengneng. ）（Satapang to rarawraw ko tamdaw no niyaro’, ）（o mitiliday sa matatawatawa to i lalan talapitilidan,）（ o satapangan to no niyaro’ koni a romi’ad.）""",
        "sent_trans": [
            "傍晚時分，聽見了蟬鳴聲，", "起初聲音斷斷續續，", "久了似乎熟練了鳴叫，變得悅耳。", 
            "當天空變暗星星出現，", "聲音像是順流而下般好聽。",
            "耕作的人，太陽剛出來就起床去工作，", "直到夕陽西下才回家休息，",
            "整天辛苦工作，扛著鋤頭在田埂邊相遇，說笑聊天，", "互相祝福，希望今年產量豐收，也為明天的工作預備。", "這是一個整潔、溫馨、美麗的部落。",
            "月亮出來了，涼風徐徐，", "看那路邊花朵盛開。", "大地似乎充滿了清新的氣息，從草叢中傳來陣陣涼風。",
            "聽那蟬鳴聲更加響亮，彷彿在誇耀，", "像是讓這片大地平靜下來般鳴叫著。",
            "孩子們在曬穀場跑來跑去玩耍，", "長者坐在走廊聊天、講故事。", "婦女們在縫補破舊的衣服，或者在整理曝曬的乾菜。",
            "雖然部落生活簡單，", "但看每個人都過得快樂安詳、生活充實。",
            "坐沒多久，突然到了深夜，", "聽見聲音一個個消失，蟬鳴聲不見了，", "月亮要下山了，全世界靜悄悄。",
            "人們進入夢鄉，月光照在稻穗上，", "微風吹過像海浪波動。",
            "天還沒亮，農夫扛著工具沿著田邊出發工作。沒多久太陽出來，草地露珠閃亮。部落開始喧鬧，學生走在路上，這是部落一天的開始。"
        ]
    },
    "文章二：名稱預留": {"raw_text": "（內容預留...）", "sent_trans": []},
    "文章三：名稱預留": {"raw_text": "（內容預留...）", "sent_trans": []},
    "文章四：名稱預留": {"raw_text": "（內容預留...）", "sent_trans": []},
    "文章五：名稱預留": {"raw_text": "（內容預留...）", "sent_trans": []}
}

# --- 4. 核心邏輯函數 ---
def count_syllables(word):
    return len(re.findall(r'[aeiouAEIOU]', word))

def extract_dynamic_vocab(text):
    clean_text = re.sub(r'[（）]', '', text)
    words = re.findall(r"\b\w+’?\b", clean_text)
    # 篩選條件：3音節以上 且 存在於主字典中
    vocab = [w for w in set(words) if count_syllables(w) >= 3 and w in MASTER_DICT]
    return sorted(vocab)

def speak(text):
    try:
        tts = gTTS(text=text, lang='it')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        return fp
    except: return None

def get_audio_source(text, type="word", index=0, article_name=""):
    # 1. 將文章名稱轉換為安全的資料夾路徑 (移除空格與特殊符號)
    safe_folder = article_name.replace(" ", "_").replace("’", "").replace("'", "")
    
    # 2. 設定檢查路徑
    if type == "word":
        # 檔名範例：audio/Dadaya_no_niyaro/words/tanikay.mp3
        local_path = f"audio/{safe_folder}/words/{text}.mp3"
    else:
        # 檔名範例：audio/Dadaya_no_niyaro/sentences/s0.mp3
        local_path = f"audio/{safe_folder}/sentences/s{index}.mp3"

    # 3. 檢查檔案是否存在
    if os.path.exists(local_path):
        return local_path  # 優先回傳自錄音檔路徑
    
    # 4. 備援方案：如果沒錄音，則使用 AI 發音 (gTTS)
    try:
        tts = gTTS(text=text, lang='it')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        return fp
    except:
        return None

# --- 5. 側邊欄文章選擇 ---
st.sidebar.title("📚 文章選讀")
selected_title = st.sidebar.selectbox("請選擇練習文章：", list(ARTICLES.keys()))

# 切換文章時重置生詞與狀態
if 'current_article' not in st.session_state or st.session_state.current_article != selected_title:
    st.session_state.current_article = selected_title
    st.session_state.dynamic_vocab = extract_dynamic_vocab(ARTICLES[selected_title]["raw_text"])
    st.session_state.w_idx = 0
    st.session_state.w_flip = False

current_data = ARTICLES[selected_title]
word_list = st.session_state.dynamic_vocab

# --- 6. App 主頁面 ---
st.title("菁英朗讀訓練") # App 內顯主標題

tabs = st.tabs(["🎴 生詞詞卡", "📏 單句朗讀", "📄 段落練習"])

# --- Tab 1: 生詞詞卡 (動態提取) ---
with tabs[0]:
    if not word_list:
        st.warning("本篇文章中目前未偵測到 3 音節以上且已定義翻譯的生詞。")
    else:
        curr_w = word_list[st.session_state.w_idx]
        # 翻轉邏輯：顯示字典內的中文翻譯 或 原文
        display = MASTER_DICT[curr_w] if st.session_state.w_flip else curr_w
        
        st.markdown(f'<div class="word-card"><h2>{display}</h2><p style="color:gray;">{st.session_state.w_idx+1}/{len(word_list)}</p></div>', unsafe_allow_html=True)
        
        cols = st.columns([1, 1, 1, 1, 1.2]) 
        if cols[0].button("⬅️ 往前"):
            st.session_state.w_idx = (st.session_state.w_idx - 1) % len(word_list)
            st.session_state.w_flip = False
            st.rerun()
        if cols[1].button("🔊 播放"):
            audio = speak(curr_w)
            if audio: st.audio(audio)
        if cols[2].button("➡️ 向後"):
            st.session_state.w_idx = (st.session_state.w_idx + 1) % len(word_list)
            st.session_state.w_flip = False
            st.rerun()
        if cols[3].button("🔀 隨機"):
            random.shuffle(st.session_state.dynamic_vocab)
            st.session_state.w_idx = 0
            st.rerun()
        if cols[4].button("🔄 翻轉/中文"):
            st.session_state.w_flip = not st.session_state.w_flip
            st.rerun()

# --- Tab 2: 單句朗讀訓練 (順序：原文 -> 翻譯框 -> 按鈕 -> 功能列) ---
with tabs[1]:
    st.subheader("單句朗讀")
    sents = re.findall(r'（(.*?)）', current_data["raw_text"], re.DOTALL)
    for i, s in enumerate(sents):
        s = s.strip()
        with st.container():
            # 1. 阿美語原文
            st.info(s)
            
            # 2. 中文翻譯框 (展開時顯示)
            show_key = f"s_cn_{selected_title}_{i}"
            if st.session_state.get(show_key, False):
                trans = current_data["sent_trans"][i] if i < len(current_data["sent_trans"]) else "（翻譯內容更新中）"
                st.markdown(f'<div class="cn-text-box">{trans}</div>', unsafe_allow_html=True)
            
            # 3. 顯示中文按鈕 (位於中文翻譯框下方)
            if st.button("顯示/隱藏中文翻譯", key=f"btn_s_{selected_title}_{i}"):
                st.session_state[show_key] = not st.session_state.get(show_key, False)
                st.rerun()
                
            # 4. 播放與評分列
            c1, c2 = st.columns([1, 2])
            if c1.button("🔊 播放句子", key=f"play_s_{selected_title}_{i}"):
                audio = speak(s)
                if audio: st.audio(audio)
            c2.radio("評分", ["未通過", "待加強", "通過"], key=f"chk_s_{selected_title}_{i}", horizontal=True, label_visibility="collapsed")
            st.divider()

# --- Tab 3: 段落練習 ---
with tabs[2]:
    st.subheader("段落練習")
    paras_list = [p.strip() for p in current_data["raw_text"].split('\n\n') if p.strip()]
    
    for i, p in enumerate(paras_list):
        clean_p = re.sub(r'[（）]', '', p)
        with st.expander(f"第 {i+1} 段", expanded=True):
            st.write(clean_p)
            c1, c2 = st.columns([1, 2])
            if c1.button("🔊 播放全段", key=f"play_p_{selected_title}_{i}"):
                audio = speak(clean_p)
                if audio: st.audio(audio)
            c2.radio("段落評分", ["未通過", "待加強", "通過"], key=f"chk_p_{selected_title}_{i}", horizontal=True, label_visibility="collapsed")
