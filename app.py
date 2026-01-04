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

# カスタムCSS（ToDoアプリ風デザイン）
st.markdown("""
<style>
    /* メイン背景グラデーション（緑→青→紫） */
    .stApp {
        background: linear-gradient(135deg, #2d5a4a 0%, #3a6b7c 25%, #4a5a8c 50%, #5a4a7c 75%, #6a4a6c 100%);
    }

    /* サイドバー */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2a4a3a 0%, #3a5a6c 100%);
    }
    [data-testid="stSidebar"] * {
        color: #e0e8e4 !important;
    }

    /* メインコンテンツエリア */
    .main .block-container {
        background: rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 2rem;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }

    /* タイトル */
    h1 {
        color: #e8f0ec !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        font-family: "BIZ UDGothic", "Hiragino Kaku Gothic ProN", "Meiryo", sans-serif !important;
    }

    /* サブテキスト */
    .stMarkdown, p, span, label {
        color: #d0e0d8 !important;
    }

    /* 入力フィールド */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.15) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 12px !important;
        color: #ffffff !important;
        font-size: 16px !important;
    }
    .stTextInput > div > div > input::placeholder {
        color: rgba(255, 255, 255, 0.5) !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #5a9aa8 !important;
        box-shadow: 0 0 10px rgba(90, 154, 168, 0.5) !important;
    }

    /* セレクトボックス */
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.15) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 12px !important;
    }
    .stSelectbox > div > div > div {
        color: #ffffff !important;
    }

    /* スライダー */
    .stSlider > div > div > div > div {
        background: #5a9aa8 !important;
    }

    /* ボタン */
    .stButton > button {
        background: linear-gradient(135deg, #5a9aa8 0%, #4a8a98 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.6rem 1.5rem !important;
        font-weight: bold !important;
        font-size: 16px !important;
        box-shadow: 0 4px 15px rgba(90, 154, 168, 0.4) !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #6aaab8 0%, #5a9aa8 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(90, 154, 168, 0.5) !important;
    }

    /* ダウンロードボタン */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #4a7a6a 0%, #3a6a5a 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: bold !important;
        box-shadow: 0 4px 15px rgba(74, 122, 106, 0.4) !important;
    }
    .stDownloadButton > button:hover {
        background: linear-gradient(135deg, #5a8a7a 0%, #4a7a6a 100%) !important;
    }

    /* プログレスバー */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #5a9aa8 0%, #4a8a98 100%) !important;
        border-radius: 10px !important;
    }

    /* メトリクス */
    [data-testid="stMetricValue"] {
        color: #5aeaaa !important;
        font-size: 2rem !important;
        font-weight: bold !important;
        text-shadow: 0 0 10px rgba(90, 234, 170, 0.3);
    }
    [data-testid="stMetricLabel"] {
        color: #a0c8b8 !important;
    }

    /* データフレーム */
    .stDataFrame {
        background: rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        overflow: hidden !important;
    }
    .stDataFrame [data-testid="stDataFrameResizable"] {
        border-radius: 12px !important;
    }

    /* 成功メッセージ */
    .stSuccess {
        background: rgba(90, 234, 170, 0.2) !important;
        border-left: 4px solid #5aeaaa !important;
        border-radius: 8px !important;
    }

    /* 情報メッセージ */
    .stInfo {
        background: rgba(90, 154, 168, 0.2) !important;
        border-left: 4px solid #5a9aa8 !important;
        border-radius: 8px !important;
    }

    /* 警告メッセージ */
    .stWarning {
        background: rgba(234, 180, 90, 0.2) !important;
        border-left: 4px solid #eab45a !important;
        border-radius: 8px !important;
    }

    /* エラーメッセージ */
    .stError {
        background: rgba(234, 90, 90, 0.2) !important;
        border-left: 4px solid #ea5a5a !important;
        border-radius: 8px !important;
    }

    /* エクスパンダー */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: #e0e8e4 !important;
    }

    /* 区切り線 */
    hr {
        border-color: rgba(255, 255, 255, 0.2) !important;
    }

    /* キャプション */
    .stCaption {
        color: #a0b8b0 !important;
    }

    /* ヘッダー */
    h2, h3 {
        color: #c0e0d0 !important;
    }

    /* divider */
    [data-testid="stMarkdownContainer"] hr {
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent) !important;
        border: none !important;
        height: 1px !important;
    }

    /* ラジオボタン */
    .stRadio > div {
        background: rgba(255, 255, 255, 0.05) !important;
        border-radius: 12px !important;
        padding: 10px !important;
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
            # <br>で分割して最初の部分を商品名として使う
            desc_parts = re.split(r'<br>|<BR>', desc_content)
            if desc_parts:
                product_name = desc_parts[0].strip()
                if product_name and product_name != "FENDI":
                    data["商品名"] = product_name

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
    else:
        st.caption("📝 例: FENDI, GUCCI, PRADA, CHANEL, HERMES, CELINE, LOEWE（大文字推奨）")
        categories = RAGTAG_CATEGORIES

    category_name = st.selectbox(
        "カテゴリ",
        options=list(categories.keys()),
        index=0
    )
    category = categories[category_name]

    if selected_ec == "コメ兵":
        max_pages = st.slider("取得ページ数", 1, 30, 10, help="1ページ約50件")
    else:
        max_pages = st.slider("取得ページ数", 1, 10, 5, help="1ページ約100件")

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
        else:
            base_url = ragtag_build_url(brand_input, category)
            get_urls_func = ragtag_get_product_urls
            get_detail_func = ragtag_get_product_detail

        status_text.text(f"🔗 URL: {base_url}")

        def update_status(msg):
            status_text.text(msg)

        product_urls = get_urls_func(base_url, max_pages, update_status)

        if not product_urls:
            st.error("❌ 商品が見つかりませんでした。ブランド名を確認してください。")
            st.info(f"試したURL: {base_url}")
        else:
            st.info(f"📦 {len(product_urls)}件の商品を発見")

            # RAGTAG は並列処理、コメ兵は順次処理
            if selected_ec == "RAGTAG":
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

                columns = ["ブランド", "商品名", "カテゴリ", "品番", "価格", "参考上代", "ランク", "サイズ", "カラー", "素材", "URL"]
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
    1. **ECサイトを選択**: コメ兵 or RAGTAG
    2. **ブランド名を入力**: 英語・スペースなし（例: `fendi`, `louisvuitton`）
    3. **カテゴリを選択**: 絞り込む場合は選択
    4. **取得ページ数を設定**: 1ページ約50件
    5. **「スクレイピング開始」をクリック**
    6. 完了後「Excelダウンロード」で保存

    ### ブランド名の書き方
    | ブランド | コメ兵 | RAGTAG |
    |----------|--------|--------|
    | フェンディ | `fendi` | `FENDI` |
    | グッチ | `gucci` | `GUCCI` |
    | ルイヴィトン | `louisvuitton` | `LOUISVUITTON` |
    | シャネル | `chanel` | `CHANEL` |
    | エルメス | `hermes` | `HERMES` |
    | プラダ | `prada` | `PRADA` |
    | セリーヌ | `celine` | `CELINE` |
    | ロエベ | `loewe` | `LOEWE` |

    ※RAGTAGは自動で大文字変換されます
    """)

st.divider()
st.caption("⚠️ 利用は自己責任で。robots.txt・利用規約を確認してください。")
