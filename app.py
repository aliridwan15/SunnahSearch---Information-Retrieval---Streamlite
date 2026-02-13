import streamlit as st
import pandas as pd
from rank_bm25 import BM25Okapi
import re
import math
import os

# ==========================================
# 1. KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(
    page_title="Sunnah Search Engine",
    page_icon="🕌",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# State Management
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Beranda"

def set_page(page):
    st.session_state.current_page = page

# ==========================================
# 2. CSS DINAMIS (AUTO DARK/LIGHT MODE)
# ==========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css');

/* --- VARIABEL WARNA (CSS VARIABLES) --- */
/* Default Light Mode */
:root {
    --bg-body: #f8fafc;
    --bg-card: #ffffff;
    --text-primary: #1e293b;
    --text-secondary: #64748b;
    --border-color: #e2e8f0;
    --header-bg: #064e3b;
    --header-text: #ffffff;
    --accent-color: #059669;
    --accent-hover: #047857;
    --highlight-bg: #ecfdf5;
}

/* Dark Mode Detect */
@media (prefers-color-scheme: dark) {
    :root {
        --bg-body: #0f172a;
        --bg-card: #1e293b;
        --text-primary: #f1f5f9;
        --text-secondary: #94a3b8;
        --border-color: #334155;
        --header-bg: #022c22;
        --header-text: #ffffff;
        --accent-color: #10b981;
        --accent-hover: #059669;
        --highlight-bg: #134e4a;
    }
}

/* --- RESET & FONT --- */
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
    color: var(--text-primary);
    background-color: var(--bg-body);
}

/* --- HEADER FIXED --- */
.custom-header {
    background-color: var(--header-bg);
    height: 80px;
    width: 100%;
    position: fixed;
    top: 0;
    left: 0;
    z-index: 999;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 2rem;
}
.header-spacer { height: 100px; }

/* Logo & User Badge */
.brand-text { font-size: 1.25rem; font-weight: 700; color: var(--header-text); letter-spacing: 0.025em; }
.user-badge {
    background-color: rgba(255, 255, 255, 0.1); 
    padding: 0.5rem 1rem; 
    border-radius: 0.5rem; 
    border: 1px solid rgba(255, 255, 255, 0.2); 
    text-align: right; 
    font-size: 0.8rem;
    color: var(--header-text);
}

/* --- NAVIGASI TAB (DI BAWAH HEADER) --- */
.nav-container {
    display: flex;
    justify-content: center;
    gap: 1rem;
    margin-bottom: 2rem;
}
/* Tombol Navigasi Streamlit Custom Style */
div.stButton > button {
    border: 1px solid var(--border-color);
    background-color: var(--bg-card);
    color: var(--text-primary);
    border-radius: 0.5rem;
    padding: 0.5rem 2rem;
    font-weight: 600;
    width: 100%;
    transition: all 0.2s;
}
div.stButton > button:hover {
    border-color: var(--accent-color);
    color: var(--accent-color);
}
/* Tombol Primary (Cari) */
div.stButton > button[kind="primary"] {
    background-color: var(--accent-color);
    color: white;
    border: none;
}
div.stButton > button[kind="primary"]:hover {
    background-color: var(--accent-hover);
    color: white;
}

/* --- CARDS --- */
.search-card, .result-card, .about-container {
    background-color: var(--bg-card);
    border-radius: 1rem;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    border: 1px solid var(--border-color);
    overflow: hidden;
    margin-bottom: 2rem;
    max-width: 1000px;
    margin-left: auto; margin-right: auto;
}

.search-header { 
    background-color: var(--highlight-bg); 
    padding: 2rem; 
    text-align: center; 
    border-bottom: 1px solid var(--border-color); 
}
.search-title { 
    font-family: 'Amiri', serif; 
    font-size: 2.2rem; 
    font-weight: 700; 
    color: var(--accent-color); 
    margin-bottom: 0.25rem; 
}
.search-subtitle { color: var(--text-secondary); font-size: 0.9rem; }
.search-body, .card-body { padding: 2rem; }

/* --- RESULT ITEM --- */
.result-card { padding: 1.5rem; transition: transform 0.2s; }
.result-card:hover { transform: translateY(-2px); border-color: var(--accent-color); }

.card-header { 
    display: flex; justify-content: space-between; align-items: center; 
    border-bottom: 1px solid var(--border-color); 
    padding-bottom: 0.75rem; margin-bottom: 1rem; 
}
.perawi-badge { 
    background-color: var(--highlight-bg); 
    color: var(--accent-color); 
    padding: 4px 8px; border-radius: 6px; 
    font-weight: 700; font-size: 0.875rem; 
    display: flex; align-items: center; gap: 6px; 
}

.arab-text {
    font-family: 'Amiri', serif;
    font-size: 1.75rem;
    line-height: 2.2;
    text-align: right;
    direction: rtl;
    color: var(--text-primary);
    margin-bottom: 1rem;
    background-color: var(--bg-body); /* Sedikit beda dari card */
    padding: 1rem;
    border-right: 4px solid var(--accent-color);
    border-radius: 0.5rem;
}
.terjemahan-text { font-size: 1rem; color: var(--text-secondary); line-height: 1.6; }

/* --- FOOTER --- */
.footer { 
    text-align: center; padding: 2rem; 
    color: var(--text-secondary); font-size: 0.8rem; 
    margin-top: 3rem; border-top: 1px solid var(--border-color); 
}

/* Hide Streamlit components */
#MainMenu, header, footer {visibility: hidden;}
.block-container { padding-top: 0; padding-bottom: 5rem; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. BACKEND LOGIC (BM25)
# ==========================================
class BM25Engine:
    def __init__(self, csv_path):
        try:
            self.df = pd.read_csv(csv_path)
            self.df['Arab'] = self.df['Arab'].fillna('')
            self.df['Terjemahan'] = self.df['Terjemahan'].fillna('')
            self.df['Perawi'] = self.df['Perawi'].fillna('')
            self.df['Perawi_Cleaned'] = self.df['Perawi'].astype(str).apply(lambda x: re.sub(r'[^a-zA-Z\s]', '', x).strip())

            self.corpus_arab = [str(x).lower().split() for x in self.df['Arab']]
            self.corpus_terjemahan = [str(x).lower().split() for x in self.df['Terjemahan']]
            
            self.bm25_arab = BM25Okapi(self.corpus_arab)
            self.bm25_terjemahan = BM25Okapi(self.corpus_terjemahan)

            self.unique_perawi_names = sorted(self.df['Perawi_Cleaned'].dropna().unique().tolist())
        except Exception as e:
            st.error(f"Error initializing engine: {e}")
            raise 

    def search_general(self, query, limit=None):
        tokenized_query = str(query).lower().split()
        if not tokenized_query: return []
        scores_arab = self.bm25_arab.get_scores(tokenized_query)
        scores_terjemahan = self.bm25_terjemahan.get_scores(tokenized_query)
        overall_scores = [s_a + s_t for s_a, s_t in zip(scores_arab, scores_terjemahan)]
        results_with_scores = [(overall_scores[i], i) for i in range(len(overall_scores)) if overall_scores[i] > 0]
        results_with_scores.sort(key=lambda x: x[0], reverse=True)
        return self._format_results(results_with_scores, limit)

    def get_hadiths_by_perawi_exact(self, perawi_name, limit=None): 
        if not perawi_name: return []
        filtered_df = self.df[self.df['Perawi_Cleaned'] == perawi_name]
        results = []
        for index, row in filtered_df.iterrows():
            results.append({'Perawi': row['Perawi'], 'Arab': row['Arab'], 'Terjemahan': row['Terjemahan'], 'score': None})
        if limit and limit != 'all': return results[:int(limit)]
        return results

    def search_within_perawi(self, query, perawi_name, limit=None):
        if not query or not perawi_name: return []
        filtered_df = self.df[self.df['Perawi_Cleaned'] == perawi_name]
        if filtered_df.empty: return []
        temp_arab = [str(x).lower().split() for x in filtered_df['Arab']]
        temp_terjemahan = [str(x).lower().split() for x in filtered_df['Terjemahan']]
        if not temp_arab: return []
        temp_bm25_a = BM25Okapi(temp_arab)
        temp_bm25_t = BM25Okapi(temp_terjemahan)
        q_tok = str(query).lower().split()
        scores = [sa + st for sa, st in zip(temp_bm25_a.get_scores(q_tok), temp_bm25_t.get_scores(q_tok))]
        orig_indices = filtered_df.index.tolist()
        results_with_scores = [(scores[i], orig_indices[i]) for i in range(len(scores)) if scores[i] > 0]
        results_with_scores.sort(key=lambda x: x[0], reverse=True)
        return self._format_results(results_with_scores, limit)

    def _format_results(self, results_with_scores, limit):
        if limit and limit != 'all': results_with_scores = results_with_scores[:int(limit)]
        final = []
        for score, idx in results_with_scores:
            final.append({'Perawi': self.df.loc[idx, 'Perawi'], 'Arab': self.df.loc[idx, 'Arab'], 'Terjemahan': self.df.loc[idx, 'Terjemahan'], 'score': round(score, 2)})
        return final

@st.cache_resource
def load_engine():
    file_path = "Sunnah.csv" 
    if not os.path.exists(file_path):
        st.error("⚠️ File 'Sunnah.csv' tidak ditemukan.")
        return None
    return BM25Engine(file_path)

engine = load_engine()

# ==========================================
# 4. HEADER & NAVIGASI (FIXED)
# ==========================================

# A. Header HTML Fixed
st.markdown("""
<div class="custom-header">
    <div class="logo-section">
        <div style="background:rgba(255,255,255,0.1); padding:8px; border-radius:50%; display:flex;">
            <i class="fas fa-mosque" style="font-size:1.5rem; color:white;"></i>
        </div>
        <span class="brand-text">Sunnah<span class="brand-highlight" style="color:#34d399;">Search</span></span>
    </div>
    <div class="user-badge">
        <div style="font-weight:700;">Ali Ridwan Nurhasan</div>
        <div style="font-family:monospace; opacity:0.8;">230411100154</div>
    </div>
</div>
<div class="header-spacer"></div>
""", unsafe_allow_html=True)

# B. Menu Navigasi (Tab Style di bawah Header)
# Kita gunakan kolom agar tombol berada di tengah dan rapi
col_pad_l, col_nav_home, col_nav_about, col_pad_r = st.columns([2, 1, 1, 2])

with col_nav_home:
    # Jika halaman aktif Beranda, kita kasih visual beda (via CSS active state, tapi di Streamlit logicnya tombol disable atau biasa)
    if st.button("🏠 Beranda", key="nav_home", use_container_width=True, type="primary" if st.session_state.current_page=="Beranda" else "secondary"):
        set_page("Beranda")
        st.rerun()

with col_nav_about:
    if st.button("ℹ️ Tentang", key="nav_about", use_container_width=True, type="primary" if st.session_state.current_page=="Tentang" else "secondary"):
        set_page("Tentang")
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True) 

# ==========================================
# 5. LOGIKA HALAMAN UTAMA
# ==========================================

if st.session_state.current_page == "Beranda":
    # ---------------- UI BERANDA (SEARCH) ----------------
    
    st.markdown('<div class="search-card">', unsafe_allow_html=True)
    st.markdown("""
        <div class="search-header">
            <div class="search-title">Pencarian Hadits</div>
            <div class="search-subtitle">Temukan referensi sunnah dengan mudah dan cepat</div>
        </div>
        <div class="search-body">
    """, unsafe_allow_html=True)

    if engine:
        query = st.text_input("Kata Kunci", placeholder="Ketik kata kunci (misal: shalat, puasa)...", label_visibility="collapsed")
        
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("<div style='font-size:0.75rem; font-weight:700; margin-bottom:5px; text-transform:uppercase; color:var(--text-secondary);'>Tipe Pencarian</div>", unsafe_allow_html=True)
            search_type = st.selectbox("Type", ('general', 'perawi_only', 'combined'), format_func=lambda x: {'general': '🔎 Pencarian Umum', 'perawi_only': '👤 Perawi Spesifik', 'combined': '🔗 Kombinasi'}[x], label_visibility="collapsed")

        with c2:
            st.markdown("<div style='font-size:0.75rem; font-weight:700; margin-bottom:5px; text-transform:uppercase; color:var(--text-secondary);'>Nama Perawi</div>", unsafe_allow_html=True)
            perawi_options = ["-- Pilih Perawi --"] + engine.unique_perawi_names
            disabled_perawi = search_type == 'general'
            selected_perawi_raw = st.selectbox("Perawi", perawi_options, disabled=disabled_perawi, label_visibility="collapsed")
            selected_perawi = None if selected_perawi_raw == "-- Pilih Perawi --" else selected_perawi_raw

        with c3:
            st.markdown("<div style='font-size:0.75rem; font-weight:700; margin-bottom:5px; text-transform:uppercase; color:var(--text-secondary);'>Jumlah Hasil</div>", unsafe_allow_html=True)
            limit_option = st.selectbox("Limit", ["5", "15", "30", "50", "Semua"], index=1, label_visibility="collapsed")

        st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
        
        # Tombol Cari (Primary)
        if 'page_number' not in st.session_state: st.session_state.page_number = 1
        search_clicked = st.button("CARI HADITS SEKARANG", type="primary")

    st.markdown("</div></div>", unsafe_allow_html=True)

    # Logic Search
    if search_clicked: st.session_state.page_number = 1
    results = []
    limit_val = 'all' if limit_option == "Semua" else int(limit_option)

    if engine:
        if search_type == 'general' and query:
            results = engine.search_general(query, limit='all')
        elif search_type == 'perawi_only' and selected_perawi:
            results = engine.get_hadiths_by_perawi_exact(selected_perawi, limit='all')
        elif search_type == 'combined' and query and selected_perawi:
            results = engine.search_within_perawi(query, selected_perawi, limit='all')

    # Display Results
    if results:
        total_results = len(results)
        if limit_val == 'all':
            current_limit = total_results; total_pages = 1; start_idx = 0; end_idx = total_results
        else:
            current_limit = limit_val
            total_pages = math.ceil(total_results / current_limit)
            if st.session_state.page_number > total_pages: st.session_state.page_number = 1
            start_idx = (st.session_state.page_number - 1) * current_limit
            end_idx = start_idx + current_limit

        paginated_results = results[start_idx:end_idx]

        st.markdown(f"""
        <div style="max-width:1000px; margin:0 auto 1.5rem auto; display:flex; justify-content:space-between; align-items:center; border-left:4px solid var(--accent-color); padding-left:1rem;">
            <h2 style="font-size:1.5rem; font-weight:700; margin:0;">Hasil Pencarian</h2>
            <span style="background:var(--bg-card); padding:4px 10px; border-radius:20px; font-size:0.85rem; font-weight:600; border:1px solid var(--border-color);">{total_results} ditemukan</span>
        </div>
        """, unsafe_allow_html=True)

        for res in paginated_results:
            score_html = f'<span style="background:var(--bg-body); border:1px solid var(--border-color); padding:2px 8px; border-radius:4px; font-size:0.75rem; color:var(--text-secondary);">Relevansi: {res["score"]}</span>' if res['score'] else ""
            
            # CARD RESULT
            st.markdown(f"""
<div class="result-card">
<div class="card-header">
<div class="perawi-badge"><i class="fas fa-user-edit"></i> {res['Perawi']}</div>
{score_html}
</div>
<div class="arab-text">{res['Arab']}</div>
<div class="terjemahan-text">
<strong style="color:var(--accent-color);">Terjemahan:</strong><br>
"{res['Terjemahan']}"
</div>
</div>
""", unsafe_allow_html=True)

        # Pagination
        if total_pages > 1:
            c1, c2, c3 = st.columns([1,2,1])
            with c1:
                if st.session_state.page_number > 1:
                    if st.button("⬅️ Sebelumnya"): st.session_state.page_number -= 1; st.rerun()
            with c2:
                st.markdown(f"<div style='text-align:center; margin-top:10px; font-weight:600;'>Halaman {st.session_state.page_number} dari {total_pages}</div>", unsafe_allow_html=True)
            with c3:
                if st.session_state.page_number < total_pages:
                    if st.button("Selanjutnya ➡️"): st.session_state.page_number += 1; st.rerun()

    elif search_clicked:
        st.markdown("""
        <div style="background: var(--bg-card); padding: 4rem; text-align: center; border-radius: 1rem; border: 1px dashed var(--border-color); max-width:800px; margin:2rem auto;">
            <div style="color:var(--border-color); font-size:3rem; margin-bottom:1rem;"><i class="fas fa-search"></i></div>
            <h3 style="font-weight: 700; font-size:1.5rem;">Tidak ada hasil ditemukan</h3>
            <p style="color: var(--text-secondary);">Silakan coba kata kunci lain atau periksa ejaan Anda.</p>
        </div>
        """, unsafe_allow_html=True)

elif st.session_state.current_page == "Tentang":
    # ---------------- UI TENTANG (ABOUT) ----------------
    st.markdown("""
<div class="about-container">
<div style="text-align:center; margin-bottom:2rem;">
<h1 style="font-family:'Amiri', serif; font-size:2.5rem; color:var(--accent-color);">Tentang Aplikasi</h1>
<p style="color:var(--text-secondary);">Sistem Temu Kembali Informasi Hadits</p>
</div>
<div style="line-height:1.8; color:var(--text-primary);">
<p style="margin-bottom:1.5rem;">
Aplikasi ini dikembangkan sebagai bagian dari tugas mata kuliah <strong>Information Retrieval</strong>. Tujuannya adalah membantu pengguna mencari dan menjelajahi hadits-hadits shahih dari berbagai sumber terpercaya dengan cepat dan akurat.
</p>
<div style="background:var(--bg-body); border:1px solid var(--border-color); padding:1.5rem; border-radius:0.75rem; display:flex; gap:1rem; align-items:center; margin-bottom:2rem;">
<div style="background:var(--highlight-bg); color:var(--accent-color); padding:10px; border-radius:50%; width:50px; height:50px; display:flex; align-items:center; justify-content:center; flex-shrink:0;">
<i class="fas fa-database" style="font-size:1.2rem;"></i>
</div>
<div>
<h4 style="margin:0; font-weight:bold;">Sumber Data</h4>
<p style="margin:0; font-size:0.9rem; color:var(--text-secondary);">Dataset diambil dari <a href="https://www.kaggle.com/datasets/ronnieaban/sunnah" target="_blank" style="color:var(--accent-color); text-decoration:none; font-weight:600;">Kaggle Sunnah Dataset</a>, mencakup teks Arab, terjemahan Indonesia, dan metadata perawi.</p>
</div>
</div>
<div style="background:var(--bg-body); border:1px solid var(--border-color); padding:1.5rem; border-radius:0.75rem; display:flex; gap:1rem; align-items:center;">
<div style="background:#dbeafe; color:#2563eb; padding:10px; border-radius:50%; width:50px; height:50px; display:flex; align-items:center; justify-content:center; flex-shrink:0;">
<i class="fas fa-cogs" style="font-size:1.2rem;"></i>
</div>
<div>
<h4 style="margin:0; font-weight:bold;">Algoritma BM25</h4>
<p style="margin:0; font-size:0.9rem; color:var(--text-secondary);">Menggunakan metode <em>Okapi BM25</em> untuk perangkingan relevansi, memastikan hasil pencarian yang muncul adalah yang paling sesuai dengan kata kunci Anda.</p>
</div>
</div>
</div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 6. FOOTER
# ==========================================
st.markdown("""
<div class="footer">
    Made with <span style="color:#ef4444;">&hearts;</span> by <strong>Ali Ridwan Nurhasan</strong> (230411100154) <br>
    Information Retrieval Project &copy; 2025
</div>
""", unsafe_allow_html=True)