import streamlit as st
import pandas as pd
from rank_bm25 import BM25Okapi
import re
import math
import os

# ==========================================
# 1. KONFIGURASI HALAMAN & CSS
# ==========================================
st.set_page_config(
    page_title="Sunnah Search Engine",
    page_icon="🕌",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS agar tampilannya mirip desain HTML/Tailwind sebelumnya
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Plus+Jakarta+Sans:wght@400;600&display=swap');
    
    /* Global Font */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Judul Utama */
    h1 {
        color: #047857 !important; /* Emerald Green */
    }

    /* Kartu Hadits */
    .hadith-card {
        background-color: white;
        padding: 25px;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s;
    }
    .hadith-card:hover {
        border-color: #10b981;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    
    /* Teks Arab */
    .hadith-arab {
        font-family: 'Amiri', serif;
        font-size: 26px;
        direction: rtl;
        text-align: right;
        line-height: 2.4;
        color: #1f2937;
        margin-bottom: 20px;
        background-color: #f9fafb;
        padding: 15px;
        border-right: 5px solid #059669;
        border-radius: 8px;
    }
    
    /* Terjemahan */
    .hadith-terjemahan {
        font-size: 16px;
        color: #4b5563;
        line-height: 1.7;
        font-style: italic;
    }
    
    /* Badge Perawi */
    .perawi-badge {
        background-color: #d1fae5;
        color: #065f46;
        padding: 5px 10px;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        margin-bottom: 10px;
    }
    
    /* Badge Score */
    .score-badge {
        background-color: #f3f4f6;
        color: #6b7280;
        font-size: 11px;
        padding: 2px 6px;
        border-radius: 4px;
        margin-left: 8px;
        border: 1px solid #e5e7eb;
    }
    
    /* Pagination Buttons */
    .stButton button {
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. LOGIKA BACKEND (BM25 ENGINE)
# ==========================================
# Class ini sama persis dengan yang di Flask, tapi kita taruh di satu file
class BM25Engine:
    def __init__(self, csv_path):
        try:
            self.df = pd.read_csv(csv_path)
            # Pastikan kolom tidak NaN
            self.df['Arab'] = self.df['Arab'].fillna('')
            self.df['Terjemahan'] = self.df['Terjemahan'].fillna('')
            self.df['Perawi'] = self.df['Perawi'].fillna('')
            # Bersihkan nama perawi untuk filter
            self.df['Perawi_Cleaned'] = self.df['Perawi'].astype(str).apply(lambda x: re.sub(r'[^a-zA-Z\s]', '', x).strip())

            # Tokenisasi
            self.corpus_arab = [str(x).lower().split() for x in self.df['Arab']]
            self.corpus_terjemahan = [str(x).lower().split() for x in self.df['Terjemahan']]
            
            # Init BM25
            self.bm25_arab = BM25Okapi(self.corpus_arab)
            self.bm25_terjemahan = BM25Okapi(self.corpus_terjemahan)

            self.unique_perawi_names = sorted(self.df['Perawi_Cleaned'].dropna().unique().tolist())
        except Exception as e:
            st.error(f"Gagal inisialisasi engine: {e}")
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
            results.append({
                'Perawi': row['Perawi'],
                'Arab': row['Arab'],
                'Terjemahan': row['Terjemahan'],
                'score': None 
            })
        if limit and limit != 'all':
            return results[:int(limit)]
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
        if limit and limit != 'all':
            results_with_scores = results_with_scores[:int(limit)]
            
        final = []
        for score, idx in results_with_scores:
            final.append({
                'Perawi': self.df.loc[idx, 'Perawi'],
                'Arab': self.df.loc[idx, 'Arab'],
                'Terjemahan': self.df.loc[idx, 'Terjemahan'],
                'score': round(score, 2)
            })
        return final

# ==========================================
# 3. LOAD DATA (CACHED)
# ==========================================
@st.cache_resource
def load_engine():
    # Pastikan file Sunnah.csv ada di sebelah app.py
    file_path = "Sunnah.csv" 
    if not os.path.exists(file_path):
        st.error("⚠️ File 'Sunnah.csv' tidak ditemukan. Upload file CSV ke repository/folder yang sama.")
        return None
    return BM25Engine(file_path)

engine = load_engine()

# ==========================================
# 4. FRONTEND STREAMLIT
# ==========================================

# --- Header ---
col_logo, col_title = st.columns([1, 5])
with col_logo:
    # Ganti URL gambar logo jika ingin custom
    st.image("https://cdn-icons-png.flaticon.com/512/4358/4358667.png", width=70)
with col_title:
    st.title("SunnahSearch")
    st.markdown("Mesin Pencari Hadits berbasis **Information Retrieval (BM25)**")

st.markdown("---")

# --- Sidebar ---
with st.sidebar:
    st.header("Tentang Aplikasi")
    st.info("""
    **SunnahSearch** adalah sistem temu kembali informasi untuk mencari hadits shahih.
    
    **Fitur:**
    - Pencarian Teks (Arab/Indo)
    - Filter Perawi
    - Algoritma Okapi BM25
    """)
    st.markdown("**Pengembang:**")
    st.markdown("Ali Ridwan Nurhasan")
    st.markdown("230411100154")

# --- Form Pencarian ---
if engine:
    # Container Form
    with st.container():
        # Pilih Tipe Search
        col_type, col_limit = st.columns([2, 1])
        with col_type:
            search_type = st.radio(
                "Tipe Pencarian",
                ('general', 'perawi_only', 'combined'),
                format_func=lambda x: {
                    'general': '🔍 Pencarian Umum',
                    'perawi_only': '👤 Perawi Spesifik',
                    'combined': '🔗 Kombinasi (Teks & Perawi)'
                }[x],
                horizontal=True
            )
        
        with col_limit:
            limit_option = st.selectbox("Jumlah Hasil per Halaman", ["10", "15", "25", "Semua"], index=1)

        # Input Query & Dropdown Perawi (Kondisional)
        col_input1, col_input2 = st.columns([2, 1])
        
        query = ""
        selected_perawi = None

        with col_input1:
            if search_type != 'perawi_only':
                query = st.text_input("Kata Kunci Pencarian", placeholder="Contoh: puasa, zakat, shalat...")
            else:
                st.info("Pencarian berdasarkan nama perawi saja.")

        with col_input2:
            if search_type in ['perawi_only', 'combined']:
                selected_perawi = st.selectbox("Pilih Nama Perawi", engine.unique_perawi_names)
        
        # Tombol Cari (Gunakan Session State untuk reset halaman)
        if 'page_number' not in st.session_state:
            st.session_state.page_number = 1
            
        search_clicked = st.button("🚀 Cari Hadits", type="primary", use_container_width=True)

    # --- Logika Search & Hasil ---
    if search_clicked:
        st.session_state.page_number = 1 # Reset ke halaman 1 tiap kali cari baru
        
    # Tentukan Limit
    limit_val = 'all' if limit_option == "Semua" else int(limit_option)
    
    # Eksekusi Pencarian
    results = []
    if search_type == 'general' and query:
        results = engine.search_general(query, limit='all')
    elif search_type == 'perawi_only' and selected_perawi:
        results = engine.get_hadiths_by_perawi_exact(selected_perawi, limit='all')
    elif search_type == 'combined' and query and selected_perawi:
        results = engine.search_within_perawi(query, selected_perawi, limit='all')

    # --- Tampilan Hasil ---
    if results:
        total_results = len(results)
        
        # Logika Pagination Manual
        if limit_val == 'all':
            current_limit = total_results
            total_pages = 1
            start_idx = 0
            end_idx = total_results
        else:
            current_limit = limit_val
            total_pages = math.ceil(total_results / current_limit)
            
            if st.session_state.page_number > total_pages:
                st.session_state.page_number = 1
                
            start_idx = (st.session_state.page_number - 1) * current_limit
            end_idx = start_idx + current_limit

        # Slice Data
        paginated_results = results[start_idx:end_idx]

        st.success(f"Ditemukan **{total_results}** hadits. (Halaman {st.session_state.page_number}/{total_pages})")

        # Loop Tampilkan Card HTML
        for res in paginated_results:
            score_html = f"<span class='score-badge'>BM25: {res['score']}</span>" if res['score'] else ""
            
            st.markdown(f"""
            <div class="hadith-card">
                <div class="perawi-badge">
                    <span>👤 Riwayat: {res['Perawi']}</span>
                    {score_html}
                </div>
                <div class="hadith-arab">{res['Arab']}</div>
                <div class="hadith-terjemahan">
                    "{res['Terjemahan']}"
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Navigasi Pagination
        if total_pages > 1:
            st.markdown("---")
            col_prev, col_page, col_next = st.columns([1, 2, 1])
            
            with col_prev:
                if st.session_state.page_number > 1:
                    if st.button("⬅️ Sebelumnya"):
                        st.session_state.page_number -= 1
                        st.rerun()
            
            with col_page:
                st.markdown(f"<p style='text-align:center; padding-top:10px;'>Halaman <b>{st.session_state.page_number}</b> dari {total_pages}</p>", unsafe_allow_html=True)
            
            with col_next:
                if st.session_state.page_number < total_pages:
                    if st.button("Selanjutnya ➡️"):
                        st.session_state.page_number += 1
                        st.rerun()
                        
    elif search_clicked:
        st.warning("Tidak ada hasil ditemukan. Coba kata kunci lain.")
    
    elif not query and not selected_perawi:
        st.info("👋 Silakan masukkan kata kunci di atas untuk memulai.")
