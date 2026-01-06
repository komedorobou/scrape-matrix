import streamlit as st
import requests
from bs4 import BeautifulSoup
import time
import random
import re
import pandas as pd
from datetime import datetime
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor, as_completed

# ページ設定
st.set_page_config(
    page_title="ブランドECスクレイパー",
    page_icon="👜",
    layout="wide"
)

# カスタムCSS（グラスモーフィズム＋アニメーション）
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&display=swap');

    /* Material Iconsの文字化け対策 */
    .material-symbols-outlined,
    .material-symbols-rounded,
    [class*="material-symbols"],
    span[data-testid="stIconMaterial"] {
        font-size: 0 !important;
        visibility: hidden !important;
        display: none !important;
    }

    /* サイドバー開閉ボタンを非表示にして代わりにシンプルに */
    button[kind="header"] {
        display: none !important;
    }

    /* ヘッダーバー（上部の暗い部分）を淡く */
    header[data-testid="stHeader"] {
        background: linear-gradient(135deg, rgba(200, 220, 230, 0.9), rgba(220, 200, 220, 0.9)) !important;
        backdrop-filter: blur(10px) !important;
    }
    header[data-testid="stHeader"] * {
        color: #3a5a5a !important;
    }

    /* ツールバー（右上のメニュー） */
    [data-testid="stToolbar"] {
        background: transparent !important;
    }
    [data-testid="stToolbar"] button {
        color: #4a6a6a !important;
    }

    /* デコレーション（上部のライン）も淡く */
    [data-testid="stDecoration"] {
        background: linear-gradient(90deg, #8ac8d8, #c8a8c8, #a8c8b8) !important;
    }

    /* アニメーション定義 */
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.02); }
    }
    @keyframes shimmer {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }

    /* メイン背景（アニメーショングラデーション） */
    .stApp {
        background: linear-gradient(-45deg, #7ab8a8, #8ac8d8, #a8b8d8, #c8a8c8, #d8a8b8, #b8c8a8);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
    }

    /* サイドバー（グラスモーフィズム）- 幅を広げる */
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.25) !important;
        backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.3) !important;
        min-width: 350px !important;
        width: 350px !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        width: 350px !important;
        padding: 2rem 1.5rem !important;
    }
    [data-testid="stSidebar"] * {
        color: #2a3a3a !important;
    }

    /* サイドバーのヘッダー */
    [data-testid="stSidebar"] h3 {
        font-size: 1.3rem !important;
        font-weight: 700 !important;
        margin-bottom: 1rem !important;
        padding-bottom: 0.5rem !important;
        border-bottom: 2px solid rgba(138, 200, 216, 0.5) !important;
    }

    /* メインコンテンツエリア（グラスカード） */
    .main .block-container {
        background: rgba(255, 255, 255, 0.4);
        border-radius: 24px;
        padding: 2rem;
        backdrop-filter: blur(20px);
        box-shadow:
            0 8px 32px rgba(0, 0, 0, 0.1),
            inset 0 0 0 1px rgba(255, 255, 255, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.3);
        animation: fadeInUp 0.6s ease-out;
    }

    /* タイトル */
    h1 {
        color: #2a4a4a !important;
        font-family: 'Noto Sans JP', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: 2px;
        background: linear-gradient(135deg, #4a8a8a, #6a9ab8, #8a7aa8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    /* サブテキスト */
    .stMarkdown, p, span, label {
        color: #3a5a5a !important;
        font-family: 'Noto Sans JP', sans-serif !important;
    }

    /* 入力フィールド（グラス風） */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.85) !important;
        border: 2px solid rgba(138, 200, 216, 0.4) !important;
        border-radius: 12px !important;
        color: #1a3a3a !important;
        font-size: 18px !important;
        font-weight: 500 !important;
        padding: 14px 18px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
    }
    .stTextInput > div > div > input::placeholder {
        color: #7a9a9a !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #6ab8d8 !important;
        background: rgba(255, 255, 255, 0.95) !important;
        box-shadow: 0 0 20px rgba(138, 200, 216, 0.5), 0 4px 12px rgba(0, 0, 0, 0.1) !important;
        transform: translateY(-2px);
    }

    /* 入力フィールドのラベル */
    .stTextInput label {
        font-size: 15px !important;
        font-weight: 600 !important;
        color: #2a4a4a !important;
        margin-bottom: 6px !important;
    }

    /* セレクトボックス */
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.85) !important;
        border: 2px solid rgba(138, 200, 216, 0.4) !important;
        border-radius: 12px !important;
        transition: all 0.3s ease !important;
    }
    .stSelectbox > div > div:hover {
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1) !important;
        border-color: #6ab8d8 !important;
    }
    .stSelectbox label {
        font-size: 15px !important;
        font-weight: 600 !important;
        color: #2a4a4a !important;
    }

    /* スライダー */
    .stSlider > div > div > div > div {
        background: linear-gradient(90deg, #8ac8d8, #a8d8e8) !important;
        border-radius: 10px !important;
    }

    /* メインボタン（光沢アニメーション） */
    .stButton > button {
        background: linear-gradient(135deg, #8ac8d8 0%, #7ab8c8 50%, #8ac8d8 100%) !important;
        background-size: 200% 200% !important;
        color: #1a3a3a !important;
        border: none !important;
        border-radius: 16px !important;
        padding: 14px 28px !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        font-family: 'Noto Sans JP', sans-serif !important;
        box-shadow:
            0 4px 15px rgba(138, 200, 216, 0.4),
            inset 0 1px 0 rgba(255, 255, 255, 0.4) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        position: relative;
        overflow: hidden;
    }
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
        transition: left 0.5s ease;
    }
    .stButton > button:hover {
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow:
            0 8px 25px rgba(138, 200, 216, 0.5),
            inset 0 1px 0 rgba(255, 255, 255, 0.5) !important;
        background-position: 100% 100% !important;
    }
    .stButton > button:hover::before {
        left: 100%;
    }
    .stButton > button:active {
        transform: translateY(-1px) scale(0.98) !important;
    }

    /* ダウンロードボタン */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #7ac8a8 0%, #6ab898 100%) !important;
        color: #1a3a2a !important;
        border: none !important;
        border-radius: 16px !important;
        font-weight: 700 !important;
        font-family: 'Noto Sans JP', sans-serif !important;
        box-shadow: 0 4px 15px rgba(106, 184, 152, 0.4) !important;
        transition: all 0.3s ease !important;
    }
    .stDownloadButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 25px rgba(106, 184, 152, 0.5) !important;
    }

    /* プログレスバー（光沢） */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #7ab8c8, #8ac8d8, #9ad8e8, #8ac8d8) !important;
        background-size: 200% 100% !important;
        animation: shimmer 2s linear infinite !important;
        border-radius: 10px !important;
    }

    /* メトリクスカード */
    [data-testid="stMetricValue"] {
        color: #3a8a7a !important;
        font-size: 2.2rem !important;
        font-weight: 700 !important;
        font-family: 'Noto Sans JP', sans-serif !important;
    }
    [data-testid="stMetricLabel"] {
        color: #5a7a7a !important;
        font-weight: 500 !important;
    }

    /* データフレーム（グラスカード） */
    .stDataFrame {
        background: rgba(255, 255, 255, 0.5) !important;
        border-radius: 16px !important;
        overflow: hidden !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08) !important;
        border: 1px solid rgba(255, 255, 255, 0.6) !important;
    }

    /* アラートメッセージ（グラス風） */
    .stSuccess {
        background: rgba(122, 200, 168, 0.25) !important;
        backdrop-filter: blur(10px) !important;
        border-left: 4px solid #6ac898 !important;
        border-radius: 12px !important;
        animation: fadeInUp 0.4s ease-out !important;
    }
    .stInfo {
        background: rgba(138, 200, 216, 0.25) !important;
        backdrop-filter: blur(10px) !important;
        border-left: 4px solid #7ac8e8 !important;
        border-radius: 12px !important;
        animation: fadeInUp 0.4s ease-out !important;
    }
    .stWarning {
        background: rgba(232, 200, 140, 0.25) !important;
        backdrop-filter: blur(10px) !important;
        border-left: 4px solid #e8c878 !important;
        border-radius: 12px !important;
    }
    .stError {
        background: rgba(232, 160, 160, 0.25) !important;
        backdrop-filter: blur(10px) !important;
        border-left: 4px solid #e89898 !important;
        border-radius: 12px !important;
    }

    /* エクスパンダー */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.4) !important;
        border-radius: 12px !important;
        color: #3a5a5a !important;
        transition: all 0.3s ease !important;
    }
    .streamlit-expanderHeader:hover {
        background: rgba(255, 255, 255, 0.6) !important;
    }

    /* ヘッダー */
    h2, h3 {
        color: #3a6a6a !important;
        font-family: 'Noto Sans JP', sans-serif !important;
    }

    /* ラジオボタン（カード風） */
    .stRadio > div {
        background: rgba(255, 255, 255, 0.7) !important;
        border-radius: 16px !important;
        padding: 16px !important;
        border: 2px solid rgba(138, 200, 216, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    .stRadio > div:hover {
        background: rgba(255, 255, 255, 0.85) !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
        border-color: #8ac8d8 !important;
    }
    .stRadio label {
        font-size: 15px !important;
        font-weight: 600 !important;
        color: #2a4a4a !important;
    }
    .stRadio > div > div > label {
        font-size: 16px !important;
        font-weight: 500 !important;
        padding: 8px 12px !important;
        border-radius: 10px !important;
        transition: all 0.2s ease !important;
    }
    .stRadio > div > div > label:hover {
        background: rgba(138, 200, 216, 0.2) !important;
    }

    /* キャプション（ヘルプテキスト） */
    .stCaption, small, .element-container small {
        font-size: 13px !important;
        color: #4a6a6a !important;
        background: rgba(255, 255, 255, 0.5) !important;
        padding: 8px 12px !important;
        border-radius: 8px !important;
        display: inline-block !important;
        margin-top: 4px !important;
    }

    /* ディバイダー */
    hr {
        border: none !important;
        height: 2px !important;
        background: linear-gradient(90deg, transparent, rgba(138, 200, 216, 0.5), transparent) !important;
        margin: 1.5rem 0 !important;
    }

    /* スライダーのラベル */
    .stSlider label {
        font-size: 15px !important;
        font-weight: 600 !important;
        color: #2a4a4a !important;
    }

    /* スライダーの値表示 */
    .stSlider [data-testid="stTickBarMin"],
    .stSlider [data-testid="stTickBarMax"] {
        font-weight: 600 !important;
        color: #3a5a5a !important;
    }

    /* スクロールバー */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(138, 200, 216, 0.5);
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(138, 200, 216, 0.7);
    }

    /* ヘルプアイコン（？マーク）を非表示 */
    .stTooltipIcon {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

# 定数
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

# EC設定
EC_SITES = {
    "コメ兵": {
        "base_url": "https://komehyo.jp",
        "icon": "🏪"
    },
    "RAGTAG": {
        "base_url": "https://www.ragtag.jp",
        "icon": "👔"
    },
    "トレファク": {
        "base_url": "https://www.trefac.jp",
        "icon": "🏷️"
    }
}

# カテゴリ定義
KOMEHYO_CATEGORIES = {
    "全カテゴリ": "",
    "ブランドバッグ": "brandbag",
    "ブランド財布・小物": "brandwallet-accessories",
    "レディースファッション": "fashion-ladies",
    "メンズファッション": "fashion-mens",
    "時計レディース": "watch-ladies",
    "時計メンズ": "watch-mens",
}

RAGTAG_CATEGORIES = {
    "全カテゴリ": "",
    "メンズ": "men",
    "レディース": "women",
}

TREFAC_CATEGORIES = {
    "全カテゴリ": "",
    "メンズ": "t1",
    "レディース": "t2",
}

# session_stateの初期化
if 'results_df' not in st.session_state:
    st.session_state.results_df = None
if 'brand_name' not in st.session_state:
    st.session_state.brand_name = ""
if 'scraping_done' not in st.session_state:
    st.session_state.scraping_done = False
if 'selected_ec' not in st.session_state:
    st.session_state.selected_ec = "コメ兵"


# ===== コメ兵用関数 =====
def komehyo_build_url(brand, category):
    """コメ兵: 検索URLを構築"""
    base_url = EC_SITES["コメ兵"]["base_url"]
    brand_clean = brand.lower().strip().replace(" ", "")
    if category:
        return f"{base_url}/{category}/{brand_clean}/"
    else:
        return f"{base_url}/{brand_clean}/"


def komehyo_get_product_urls(base_url, max_pages, progress_callback=None):
    """コメ兵: 商品URLを全ページから取得"""
    urls = []
    page = 1

    while page <= max_pages:
        url = f"{base_url}?page={page}"

        if progress_callback:
            progress_callback(f"📄 ページ {page} の商品リストを取得中...")

        try:
            res = requests.get(url, headers=HEADERS, timeout=30)
            if res.status_code != 200:
                break

            soup = BeautifulSoup(res.text, 'html.parser')

            links = soup.select('a[href*="/product/"]')
            new_urls = []
            for a in links:
                href = a.get('href', '')
                if '/product/' in href:
                    full_url = EC_SITES["コメ兵"]["base_url"] + href if href.startswith('/') else href
                    new_urls.append(full_url)

            new_urls = list(set(new_urls))

            if not new_urls:
                break

            before_count = len(urls)
            urls.extend(new_urls)
            urls = list(set(urls))

            if len(urls) == before_count:
                break

            page += 1
            time.sleep(random.uniform(0.5, 1.0))

        except Exception as e:
            break

    return urls


def komehyo_get_product_detail(url):
    """コメ兵: 商品詳細を取得"""
    try:
        res = requests.get(url, headers=HEADERS, timeout=30)
        soup = BeautifulSoup(res.text, 'html.parser')

        data = {"URL": url}

        h1 = soup.find('h1')
        data["商品名"] = h1.get_text(strip=True) if h1 else ""

        price_el = soup.select_one('[class*="price"]')
        if price_el:
            price_text = price_el.get_text()
            match = re.search(r'[￥¥]([\d,]+)', price_text)
            if match:
                data["価格"] = int(match.group(1).replace(',', ''))

        rows = soup.select('tr')
        for row in rows:
            th = row.find('th')
            td = row.find('td')
            if th and td:
                key = th.get_text(strip=True)
                val = td.get_text(strip=True).split('\n')[0].strip()

                if key == "品番型式":
                    data["品番"] = val
                elif key == "商品ランク":
                    rank_match = re.search(r'(新品|未使用品|中古品[SABC])', val)
                    if rank_match:
                        data["ランク"] = rank_match.group(1)
                elif key == "カラー":
                    data["カラー"] = val
                elif key == "素材":
                    data["素材"] = val
                elif key == "ブランド":
                    data["ブランド"] = val
                elif key == "参考上代":
                    ref_match = re.search(r'[￥¥]([\d,]+)', val)
                    if ref_match:
                        data["参考上代"] = int(ref_match.group(1).replace(',', ''))

        return data

    except Exception as e:
        return None


# ===== RAGTAG用関数 =====
def ragtag_build_url(brand, category):
    """RAGTAG: 検索URLを構築"""
    base_url = EC_SITES["RAGTAG"]["base_url"]
    # 検索URL形式: https://www.ragtag.jp/search?fr=FENDI
    brand_clean = brand.upper().strip().replace(" ", "")
    return f"{base_url}/search?fr={brand_clean}"


def ragtag_get_product_urls(base_url, max_pages, progress_callback=None):
    """RAGTAG: 商品URLを全ページから取得"""
    urls = []
    page = 1

    while page <= max_pages:
        # ページネーション: &page=2, &page=3...
        url = f"{base_url}&page={page}" if page > 1 else base_url

        if progress_callback:
            progress_callback(f"📄 ページ {page} の商品リストを取得中...")

        try:
            res = requests.get(url, headers=HEADERS, timeout=30)
            if res.status_code != 200:
                break

            soup = BeautifulSoup(res.text, 'html.parser')

            # RAGTAGの商品リンクを取得（/item/ を含むリンク）
            all_links = soup.find_all('a', href=True)
            new_urls = []
            for a in all_links:
                href = a.get('href', '')
                if '/item/' in href:
                    if href.startswith('http'):
                        full_url = href
                    elif href.startswith('/'):
                        full_url = EC_SITES["RAGTAG"]["base_url"] + href
                    else:
                        full_url = EC_SITES["RAGTAG"]["base_url"] + '/' + href
                    new_urls.append(full_url)

            new_urls = list(set(new_urls))

            if not new_urls:
                break

            before_count = len(urls)
            urls.extend(new_urls)
            urls = list(set(urls))

            if len(urls) == before_count:
                break

            page += 1
            time.sleep(random.uniform(0.5, 1.0))

        except Exception as e:
            break

    return urls


def ragtag_get_product_detail(url):
    """RAGTAG: 商品詳細を取得"""
    try:
        res = requests.get(url, headers=HEADERS, timeout=30)
        soup = BeautifulSoup(res.text, 'html.parser')

        data = {"URL": url}

        # ブランド名
        brand_el = soup.select_one('.item-detail-info__name-brand')
        if brand_el:
            brand_text = brand_el.get_text(strip=True).split('\n')[0].strip()
            data["ブランド"] = brand_text

        # カテゴリ
        cat_el = soup.select_one('.item-detail-info__category-list')
        if cat_el:
            data["カテゴリ"] = cat_el.get_text(strip=True).replace('\n', '').replace(' ', '')

        # 価格
        price_el = soup.select_one('.item-detail-info__price')
        if price_el:
            price_text = price_el.get_text(strip=True).replace(',', '')
            match = re.search(r'(\d+)', price_text)
            if match:
                data["価格"] = int(match.group(1))

        # カラー
        color_el = soup.select_one('.item-detail-info__sku-color-name')
        if color_el:
            data["カラー"] = color_el.get_text(strip=True)

        # コンディション・サイズ（正規表現でテキストから抽出）
        page_text = soup.get_text()

        cond_match = re.search(r'コンディション\s*[:：]\s*(\w+)', page_text)
        if cond_match:
            data["ランク"] = cond_match.group(1)

        size_match = re.search(r'サイズ\s*[:：]\s*([^\s]+)', page_text)
        if size_match:
            data["サイズ"] = size_match.group(1)

        # 商品名（metaのdescriptionから取得）
        # 例: "ズッカ柄  <br>ショルダーバッグ" や "バイザウェイ ミニ ハンドバッグ"
        meta_desc = soup.select_one('meta[name="description"]')
        if meta_desc:
            desc_content = meta_desc.get('content', '')
            # <br>で分割して商品名を探す
            desc_parts = re.split(r'<br>|<BR>', desc_content)
            for part in desc_parts:
                part = part.strip()
                # 適切な長さ（2〜30文字）で、説明文っぽくないものを採用
                if part and 2 <= len(part) <= 30:
                    # 除外パターン: ブランド名のみ、「の商品」「公式」「通販」などを含む
                    if not re.search(r'(の商品|公式|通販|買取|販売|サイト|RAGTAG|ラグタグ|送料)', part):
                        if part not in ["FENDI", "GUCCI", "PRADA", "CHANEL", "HERMES", "CELINE", "LOEWE"]:
                            data["商品名"] = part
                            break

        # 品番（metaのdescriptionから抽出）
        # 例: 7VA114, 8BL135 など（数字とアルファベット両方含む5文字以上）
        if meta_desc:
            desc_content = meta_desc.get('content', '')
            # 品番パターン: アルファベットと数字の両方を含む5-10文字
            candidates = re.findall(r'\b[A-Z0-9]{5,10}\b', desc_content)
            for candidate in candidates:
                # FENDIなどブランド名は除外、数字とアルファベット両方含むものを採用
                has_digit = any(c.isdigit() for c in candidate)
                has_alpha = any(c.isalpha() for c in candidate)
                if has_digit and has_alpha and candidate not in ["FENDI", "GUCCI", "PRADA", "CHANEL", "HERMES", "CELINE", "LOEWE"]:
                    data["品番"] = candidate
                    break

        return data

    except Exception as e:
        return None


# ===== トレファク用関数 =====
def trefac_build_url(brand, category):
    """トレファク: 検索URLを構築"""
    base_url = EC_SITES["トレファク"]["base_url"]
    brand_clean = brand.strip()
    return f"{base_url}/store/search_result.html?q={brand_clean}"


def trefac_get_product_urls(base_url, max_pages, progress_callback=None):
    """トレファク: 商品URLを全ページから取得"""
    urls = []
    page = 1

    while page <= max_pages:
        # ページネーション: &page=2, &page=3...
        url = f"{base_url}&page={page}" if page > 1 else base_url

        if progress_callback:
            progress_callback(f"📄 ページ {page} の商品リストを取得中...")

        try:
            res = requests.get(url, headers=HEADERS, timeout=30)
            if res.status_code != 200:
                break

            soup = BeautifulSoup(res.text, 'html.parser')

            # トレファクの商品リンク: /store/{数字16桁}/c{数字}/ パターン
            all_links = soup.find_all('a', href=True)
            new_urls = []
            for a in all_links:
                href = a.get('href', '')
                if re.search(r'/store/\d{10,}/', href):
                    if href.startswith('http'):
                        full_url = href
                    elif href.startswith('/'):
                        full_url = EC_SITES["トレファク"]["base_url"] + href
                    else:
                        full_url = EC_SITES["トレファク"]["base_url"] + '/' + href
                    new_urls.append(full_url)

            new_urls = list(set(new_urls))

            if not new_urls:
                break

            before_count = len(urls)
            urls.extend(new_urls)
            urls = list(set(urls))

            if len(urls) == before_count:
                break

            page += 1
            time.sleep(random.uniform(0.5, 1.0))

        except Exception as e:
            break

    return urls


def trefac_get_product_detail(url):
    """トレファク: 商品詳細を取得"""
    try:
        res = requests.get(url, headers=HEADERS, timeout=30)
        soup = BeautifulSoup(res.text, 'html.parser')

        data = {"URL": url}

        # 品番（URLから商品IDを抽出）
        # URL形式: /store/3050004189345460/c3636967/
        id_match = re.search(r'/store/(\d{10,})/', url)
        if id_match:
            data["品番"] = id_match.group(1)

        # 価格
        price_el = soup.select_one('.gdprice_main')
        if price_el:
            price_text = price_el.get_text(strip=True).replace(',', '')
            match = re.search(r'(\d+)', price_text)
            if match:
                data["価格"] = int(match.group(1))

        # 属性テーブルから取得（ブランド、性別、カテゴリ、コンディション、付属品）
        attr_rows = soup.select('.gddescription_attr_row')
        for row in attr_rows:
            head = row.select_one('.gddescription_attr_head')
            data_el = row.select_one('.gddescription_attr_data')
            if head and data_el:
                key = head.get_text(strip=True)
                val = data_el.get_text(strip=True).replace('\n', ' ')

                if 'ブランド' in key:
                    data["ブランド"] = val.split()[0] if val else ""
                elif '性別' in key:
                    data["性別"] = val
                elif 'カテゴリ' in key:
                    data["カテゴリ"] = val.replace('>', ' > ').strip()
                elif 'コンディション' in key:
                    # ★★★☆☆☆（やや傷や汚れがあり）→ ★数をカウント
                    stars = val.count('★')
                    data["ランク"] = f"★{stars}"
                elif '付属品' in key:
                    data["付属品"] = val

        # 詳細テーブルから取得（アイテム名、カラー、素材、製造国）
        detail_rows = soup.select('.gddescription_detail_row')
        for row in detail_rows:
            head = row.select_one('.gddescription_detail_head')
            data_el = row.select_one('.gddescription_detail_data')
            if head and data_el:
                key = head.get_text(strip=True)
                val = data_el.get_text(strip=True).replace('\n', ' ')[:100]

                if 'アイテム名' in key:
                    data["商品名"] = val
                elif 'カラー' in key:
                    data["カラー"] = val
                elif '素材' in key:
                    data["素材"] = val
                elif '製造国' in key:
                    data["製造国"] = val
                elif 'サイズ' in key and 'サイズ' not in data:
                    data["サイズ"] = val

        return data

    except Exception as e:
        return None


def get_products_parallel(urls, get_detail_func, max_workers=10, progress_callback=None):
    """並列処理で商品詳細を取得"""
    results = []
    total = len(urls)
    completed = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(get_detail_func, url): url for url in urls}

        for future in as_completed(futures):
            data = future.result()
            if data:
                results.append(data)

            completed += 1
            if progress_callback:
                progress_callback(completed, total)

    return results


def to_excel(df):
    """DataFrameをExcelバイナリに変換"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='データ')
    return output.getvalue()


# タイトル
st.title("👜 ブランドECスクレイパー")
st.caption("ECサイトとブランドを選んで商品データを取得")

# サイドバー
with st.sidebar:
    st.markdown("### 🏬 ECサイト選択")

    selected_ec = st.radio(
        "スクレイピング先",
        options=list(EC_SITES.keys()),
        format_func=lambda x: f"{EC_SITES[x]['icon']} {x}",
        horizontal=True
    )
    st.session_state.selected_ec = selected_ec

    st.divider()

    st.markdown("### 🔧 検索条件")

    brand_input = st.text_input(
        "ブランド名（英語）",
        value="fendi",
        help="スペースなしの英語で入力"
    )

    if selected_ec == "コメ兵":
        st.caption("📝 例: fendi, gucci, prada, chanel, hermes, celine, loewe, louisvuitton")
        categories = KOMEHYO_CATEGORIES
    elif selected_ec == "RAGTAG":
        st.caption("📝 例: FENDI, GUCCI, PRADA, CHANEL, HERMES, CELINE, LOEWE（大文字推奨）")
        categories = RAGTAG_CATEGORIES
    else:  # トレファク
        st.caption("📝 例: fendi, gucci, prada, chanel, hermes, celine, loewe")
        categories = TREFAC_CATEGORIES

    category_name = st.selectbox(
        "カテゴリ",
        options=list(categories.keys()),
        index=0
    )
    category = categories[category_name]

    if selected_ec == "コメ兵":
        max_pages = st.slider("取得ページ数", 1, 30, 10, help="1ページ約50件")
    elif selected_ec == "RAGTAG":
        max_pages = st.slider("取得ページ数", 1, 10, 5, help="1ページ約100件")
    else:  # トレファク
        max_pages = st.slider("取得ページ数", 1, 10, 5, help="1ページ約90件")

    st.divider()

    scrape_button = st.button("🔍 スクレイピング開始", type="primary", use_container_width=True)

    # 結果クリアボタン
    if st.session_state.scraping_done:
        if st.button("🗑️ 結果をクリア", use_container_width=True):
            st.session_state.results_df = None
            st.session_state.scraping_done = False
            st.session_state.brand_name = ""
            st.rerun()


# メイン処理
if scrape_button:
    if not brand_input:
        st.warning("⚠️ ブランド名を入力してください")
    else:
        progress_bar = st.progress(0)
        status_text = st.empty()

        # EC別に処理を分岐
        if selected_ec == "コメ兵":
            base_url = komehyo_build_url(brand_input, category)
            get_urls_func = komehyo_get_product_urls
            get_detail_func = komehyo_get_product_detail
        elif selected_ec == "RAGTAG":
            base_url = ragtag_build_url(brand_input, category)
            get_urls_func = ragtag_get_product_urls
            get_detail_func = ragtag_get_product_detail
        else:  # トレファク
            base_url = trefac_build_url(brand_input, category)
            get_urls_func = trefac_get_product_urls
            get_detail_func = trefac_get_product_detail

        status_text.text(f"🔗 URL: {base_url}")

        def update_status(msg):
            status_text.text(msg)

        product_urls = get_urls_func(base_url, max_pages, update_status)

        if not product_urls:
            st.error("❌ 商品が見つかりませんでした。ブランド名を確認してください。")
            st.info(f"試したURL: {base_url}")
        else:
            st.info(f"📦 {len(product_urls)}件の商品を発見")

            # RAGTAG・トレファク は並列処理、コメ兵は順次処理
            if selected_ec in ["RAGTAG", "トレファク"]:
                status_text.text("🚀 並列処理で詳細取得中...")

                def update_progress(completed, total):
                    progress_bar.progress(completed / total)
                    status_text.text(f"🚀 [{completed}/{total}] 並列取得中...")

                results = get_products_parallel(product_urls, get_detail_func, max_workers=10, progress_callback=update_progress)
            else:
                # コメ兵は順次処理（サーバー負荷考慮）
                results = []
                total = len(product_urls)

                for i, url in enumerate(product_urls):
                    status_text.text(f"🔄 [{i+1}/{total}] 商品詳細を取得中...")
                    progress_bar.progress((i + 1) / total)

                    data = get_detail_func(url)
                    if data:
                        results.append(data)

                    time.sleep(random.uniform(0.3, 0.7))

            status_text.text("✅ 完了！")
            progress_bar.progress(1.0)

            if results:
                df = pd.DataFrame(results)

                columns = ["ブランド", "商品名", "カテゴリ", "品番", "価格", "参考上代", "ランク", "サイズ", "カラー", "素材", "性別", "製造国", "付属品", "URL"]
                df = df[[c for c in columns if c in df.columns]]

                # session_stateに保存
                st.session_state.results_df = df
                st.session_state.brand_name = brand_input
                st.session_state.scraping_done = True

                st.rerun()
            else:
                st.warning("⚠️ 商品詳細の取得に失敗しました")


# 結果表示（session_stateから）
if st.session_state.scraping_done and st.session_state.results_df is not None:
    df = st.session_state.results_df

    st.success(f"✅ {len(df)}件の商品データを取得しました")

    # 統計
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("取得件数", f"{len(df)}件")
    with col2:
        if "価格" in df.columns and df["価格"].notna().any():
            st.metric("平均価格", f"¥{df['価格'].mean():,.0f}")
    with col3:
        if "価格" in df.columns and df["価格"].notna().any():
            st.metric("最安値", f"¥{df['価格'].min():,.0f}")
    with col4:
        if "価格" in df.columns and df["価格"].notna().any():
            st.metric("最高値", f"¥{df['価格'].max():,.0f}")

    st.dataframe(df, use_container_width=True, height=400)

    # Excel出力
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ec_name = st.session_state.selected_ec.lower().replace(" ", "")
    filename = f"{ec_name}_{st.session_state.brand_name}_{timestamp}.xlsx"

    excel_data = to_excel(df)
    st.download_button(
        label="📥 Excelダウンロード",
        data=excel_data,
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.xlsx",
        use_container_width=True
    )


# 使い方
with st.expander("📖 使い方"):
    st.markdown("""
    ### 使い方
    1. **ECサイトを選択**: コメ兵 / RAGTAG / トレファク
    2. **ブランド名を入力**: 英語・スペースなし（例: `fendi`, `louisvuitton`）
    3. **カテゴリを選択**: 絞り込む場合は選択
    4. **取得ページ数を設定**: 1ページ約50〜90件
    5. **「スクレイピング開始」をクリック**
    6. 完了後「Excelダウンロード」で保存

    ### ブランド名の書き方
    | ブランド | コメ兵 | RAGTAG | トレファク |
    |----------|--------|--------|------------|
    | フェンディ | `fendi` | `FENDI` | `fendi` |
    | グッチ | `gucci` | `GUCCI` | `gucci` |
    | ルイヴィトン | `louisvuitton` | `LOUISVUITTON` | `louis vuitton` |
    | シャネル | `chanel` | `CHANEL` | `chanel` |
    | エルメス | `hermes` | `HERMES` | `hermes` |
    | プラダ | `prada` | `PRADA` | `prada` |
    | セリーヌ | `celine` | `CELINE` | `celine` |
    | ロエベ | `loewe` | `LOEWE` | `loewe` |

    ※RAGTAGは自動で大文字変換されます
    """)

st.divider()
st.caption("⚠️ 利用は自己責任で。robots.txt・利用規約を確認してください。")
