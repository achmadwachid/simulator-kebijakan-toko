# ── Standard Library ──────────────────────────────────────────────────────────
import time
import warnings
warnings.filterwarnings('ignore')

# ── Third-Party ───────────────────────────────────────────────────────────────
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# ── Internal Modules ──────────────────────────────────────────────────────────
from simulation_engine import load_model, run_simulation, generate_narasi, find_optimal_scenario


# =============================================================================
# KONFIGURASI & INISIALISASI
# =============================================================================

st.set_page_config(
    page_title="Simulator Kebijakan Toko",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS Eksternal (termasuk loading screen CSS) ────────────────────────────────
with open("style.css", "r", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── Inisialisasi Session State ────────────────────────────────────────────────
if 'history' not in st.session_state:
    st.session_state['history'] = []

_is_first_load = 'app_initialized' not in st.session_state

_loading = st.empty()

if _is_first_load:
    with _loading.container():
        st.markdown("""
        <div class="loading-overlay">
            <div class="loading-card">
                <div class="loading-spinner"></div>
                <span class="loading-badge">Simulator Kebijakan Toko</span>
                <p class="loading-title">Memuat Model Simulasi</p>
                <p class="loading-subtitle">
                    Menyiapkan model prediksi dan data baseline...<br>
                    Mohon tunggu sebentar.
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ── Load Model ────────────────────────────────────────────────────────────────
paket         = load_model()
model         = paket['model']
baseline_pred = paket['baseline_pred']
baseline      = paket['baseline']

if _is_first_load:
    time.sleep(1)                                  # Tahan loading agar terlihat
    _loading.empty()                               # Hapus loading screen
    st.session_state['app_initialized'] = True     # Tandai app sudah diinisialisasi



# =============================================================================
# UI UTAMA
# =============================================================================

# ── Header Identitas ──────────────────────────────────────────────────────────
st.markdown("""
<div class="identity-bar">
    <div class="judul">Simulator Kebijakan Keuntungan Toko</div>
</div>
""", unsafe_allow_html=True)

st.write("Gunakan slider untuk menguji skenario **'What-If'** secara real-time.")

# ── Panel Kebijakan (Intervensi) — di main content, bukan sidebar ─────────────
with st.expander("Tuas Kebijakan (Intervensi)", expanded=True):
    col_sl1, col_sl2, col_baseline = st.columns([1, 1, 1.2])

    with col_sl1:
        iklan_slider = st.slider(
            "Anggaran Iklan (Juta Rp)",
            min_value=0, max_value=50,
            value=int(baseline['iklan']), step=1
        )

    with col_sl2:
        diskon_slider = st.slider(
            "Besaran Diskon (%)",
            min_value=0, max_value=50,
            value=int(baseline['diskon']), step=1
        )

    with col_baseline:
        st.markdown(
            f"""
            <div class="baseline-box">
                <b>Baseline (Kondisi Saat Ini):</b><br>
                Iklan &nbsp;&nbsp;&nbsp;&nbsp;: Rp {baseline['iklan']:.0f} Juta<br>
                Diskon &nbsp;&nbsp;: {baseline['diskon']:.0f}%<br>
                Keuntungan : Rp <b>{baseline_pred:.2f}</b> Juta
            </div>
            """,
            unsafe_allow_html=True
        )

# ── Simulasi ──────────────────────────────────────────────────────────────────
hasil_pred, delta = run_simulation(model, baseline_pred, iklan_slider, diskon_slider)
delta_pct         = (delta / baseline_pred * 100) if baseline_pred != 0 else 0
efisiensi         = hasil_pred / iklan_slider if iklan_slider > 0 else 0

# ── Struktur Tabs ─────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "Simulasi Utama", 
    "Peta Keuntungan", 
    "Papan Skor"
])

# =============================================================================
# TAB 1: SIMULASI UTAMA
# =============================================================================
with tab1:
    # ── Bagian 1: Metrik ──────────────────────────────────────────────────────
    st.markdown("### <i class='bi bi-bar-chart-fill'></i> Hasil Simulasi", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    col1.metric("Baseline (Kondisi Saat Ini)", f"Rp {baseline_pred:.2f} Jt")
    col2.metric(
        "Prediksi Setelah Intervensi",
        f"Rp {hasil_pred:.2f} Jt",
        f"{delta:+.2f} Jt"
    )

    st.markdown("---")

    # ── Bagian 2: Bar Chart + Narasi ──────────────────────────────────────────
    col_kiri, col_kanan = st.columns([1.1, 1])

    with col_kiri:
        st.markdown(
            "#### <i class='bi bi-graph-up'></i> Perbandingan Baseline vs Intervensi",
            unsafe_allow_html=True
        )
        fig, ax = plt.subplots(figsize=(5, 4))
        skenario = ['Baseline\n(Saat Ini)', 'Intervensi\n(Simulasi)']
        nilai    = [baseline_pred, hasil_pred]
        warna    = ['#1565C0', '#2e7d32' if delta >= 0 else '#c62828']

        bars = ax.bar(skenario, nilai, color=warna, width=0.4, edgecolor='white', linewidth=1.5)
        for bar, val in zip(bars, nilai):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 1,
                f'Rp {val:.2f} Jt',
                ha='center', va='bottom', fontweight='bold', fontsize=10
            )
        ax.axhline(y=baseline_pred, color='#1565C0', linestyle='--',
                   linewidth=1.2, alpha=0.5, label=f'Baseline: {baseline_pred:.2f} Jt')
        ax.set_ylabel('Keuntungan (Juta Rupiah)')
        ax.set_title('Baseline vs Intervensi', fontweight='bold')
        ax.legend(fontsize=8)
        ax.set_ylim(0, max(nilai) * 1.25)
        ax.spines[['top', 'right']].set_visible(False)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col_kanan:
        st.markdown(
            "#### <i class='bi bi-robot'></i> Analisis Skenario",
            unsafe_allow_html=True
        )
        kelas, icon_name, status, narasi = generate_narasi(
            iklan_slider, diskon_slider, hasil_pred, delta, delta_pct, baseline
        )
        st.markdown(f"""
        <div class="ai-card {kelas}">
            <b><i class='bi bi-{icon_name}'></i> Status Skenario: {status}</b><br><br>
            {narasi}
        </div>
        """, unsafe_allow_html=True)


# =============================================================================
# TAB 2: PETA KEUNTUNGAN (HEATMAP + TITIK OPTIMAL)
# =============================================================================
with tab2:
    st.markdown("### <i class='bi bi-map'></i> Peta Keuntungan", unsafe_allow_html=True)
    st.write("Visualisasi seluruh lanskap keuntungan berdasarkan kombinasi Iklan dan Diskon. Titik optimal ditandai dengan bintang.")

    # ── Data dari grid yang sudah ada ─────────────────────────────────────────
    optimal = find_optimal_scenario(model)
    grid_Z  = optimal['grid_Z']   # shape (51, 51) — baris=iklan, kolom=diskon

    # ── Metrik Optimal ────────────────────────────────────────────────────────
    col_o1, col_o2, col_o3 = st.columns(3)
    col_o1.metric("Keuntungan Maksimal", f"Rp {optimal['max_profit']:.2f} Jt")
    col_o2.metric("Iklan Optimal",       f"Rp {optimal['best_iklan']} Jt")
    col_o3.metric("Diskon Optimal",      f"{optimal['best_diskon']}%")

    st.markdown("---")

    # ── Heatmap ───────────────────────────────────────────────────────────────
    fig_hm, ax_hm = plt.subplots(figsize=(9, 6))

    # grid_Z: baris = iklan (0-50), kolom = diskon (0-50)
    # imshow: origin='lower' agar sumbu Y naik ke atas
    im = ax_hm.imshow(
        grid_Z, origin='lower', aspect='auto',
        extent=[0, 50, 0, 50],
        cmap='Blues', interpolation='bilinear'
    )
    cbar = fig_hm.colorbar(im, ax=ax_hm, shrink=0.85, pad=0.02)
    cbar.set_label('Keuntungan (Juta Rupiah)', fontsize=9)

    # Titik Optimal (bintang)
    ax_hm.plot(
        optimal['best_diskon'], optimal['best_iklan'],
        marker='*', markersize=13, color='#FFFFFF',
        markeredgecolor='#111111', markeredgewidth=1.2,
        linestyle='none',
        label=f"Optimal ({optimal['best_iklan']}, {optimal['best_diskon']}%)"
    )

    # Titik Slider saat ini (lingkaran)
    ax_hm.plot(
        diskon_slider, iklan_slider,
        marker='o', markersize=10, color='#FFC107',
        markeredgecolor='#111111', markeredgewidth=1.2,
        linestyle='none',
        label=f"Posisi Slider ({iklan_slider}, {diskon_slider}%)"
    )

    ax_hm.set_xlabel('Diskon (%)', fontsize=10)
    ax_hm.set_ylabel('Iklan (Juta Rupiah)', fontsize=10)
    ax_hm.set_title('Lanskap Keuntungan: Iklan vs Diskon', fontweight='bold')
    ax_hm.legend(loc='upper left', fontsize=8, framealpha=0.9)

    plt.tight_layout()
    st.pyplot(fig_hm)
    plt.close()

    # ── Insight Otomatis ───────────────────────────────────────────────────────
    selisih_optimal = optimal['max_profit'] - hasil_pred
    if selisih_optimal <= 0:
        insight_kelas = "ai-naik"
        insight_icon  = "check-circle-fill"
        insight_teks  = (
            f"Anda sudah berada di <b>titik optimal</b>! "
            f"Keuntungan saat ini <b>Rp {hasil_pred:.2f} Jt</b> adalah yang tertinggi."
        )
    else:
        insight_kelas = "ai-netral"
        insight_icon  = "signpost-split"
        insight_teks  = (
            f"Anda berada <b>Rp {selisih_optimal:.2f} Jt</b> dari titik optimal. "
            f"Untuk mencapainya, ubah iklan ke <b>Rp {optimal['best_iklan']} Jt</b> "
            f"dan diskon ke <b>{optimal['best_diskon']}%</b>."
        )

    st.markdown(f"""
    <div class="ai-card {insight_kelas}">
        <b><i class='bi bi-{insight_icon}'></i> Insight Otomatis</b><br><br>
        {insight_teks}<br><br>
        <small>
            <b><i class='bi bi-info-circle'></i> Cara Membaca Peta:</b>
            Warna biru semakin <b>gelap</b> = keuntungan semakin <b>tinggi</b>.
            <b>Bintang putih</b> = titik optimal, 
            <b>lingkaran kuning</b> = posisi slider Anda saat ini.
        </small>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# TAB 3: PAPAN SKOR
# =============================================================================
with tab3:
    st.markdown("### <i class='bi bi-trophy'></i> Papan Skor Skenario", unsafe_allow_html=True)
    st.write("Simpan skenario yang menurut Anda menarik untuk dibandingkan dengan skenario lain.")
    
    # Form simpan skenario
    with st.form("form_simpan_skenario"):
        col_f1, col_f2 = st.columns([3, 1])
        with col_f1:
            nama_skenario = st.text_input("Nama Skenario", placeholder="Contoh: Promo Akhir Tahun")
        with col_f2:
            st.markdown("<br>", unsafe_allow_html=True)
            submit_btn = st.form_submit_button("Simpan Skenario Saat Ini", use_container_width=True)
            
        if submit_btn:
            if not nama_skenario.strip():
                st.error("Nama skenario tidak boleh kosong!")
            else:
                skenario_baru = {
                    "Nama Skenario": nama_skenario,
                    "Iklan (Jt)": iklan_slider,
                    "Diskon (%)": diskon_slider,
                    "Keuntungan (Jt)": hasil_pred,
                    "Efisiensi": efisiensi
                }
                st.session_state['history'].append(skenario_baru)
                st.success(f"Skenario '{nama_skenario}' berhasil disimpan!")
                
    if st.session_state['history']:
        df_history = pd.DataFrame(st.session_state['history'])
        # Urutkan berdasarkan keuntungan tertinggi
        df_history = df_history.sort_values(by="Keuntungan (Jt)", ascending=False).reset_index(drop=True)
        
        st.markdown("#### <i class='bi bi-award'></i> Peringkat Skenario", unsafe_allow_html=True)
        # Format angka agar lebih rapi
        st.dataframe(
            df_history.style.format({
                "Keuntungan (Jt)": "{:.2f}",
                "Efisiensi": "{:.2f}"
            }).highlight_max(subset=["Keuntungan (Jt)"], color="lightgreen"),
            use_container_width=True
        )
        
        st.markdown("#### <i class='bi bi-bar-chart'></i> Perbandingan Keuntungan", unsafe_allow_html=True)
        fig_bar, ax_bar = plt.subplots(figsize=(8, 4))
        
        # Beri warna emas untuk juara 1, biru untuk yang lain
        colors = ['gold' if i == 0 else '#1565C0' for i in range(len(df_history))]
        
        bars_hist = ax_bar.bar(df_history["Nama Skenario"], df_history["Keuntungan (Jt)"], color=colors)
        ax_bar.set_ylabel("Keuntungan (Juta Rupiah)")
        ax_bar.spines[['top', 'right']].set_visible(False)
        plt.xticks(rotation=45, ha='right')
        
        for bar in bars_hist:
            yval = bar.get_height()
            ax_bar.text(bar.get_x() + bar.get_width()/2, yval + 1, f'{yval:.1f}', ha='center', va='bottom', fontsize=8)
            
        plt.tight_layout()
        st.pyplot(fig_bar)
        plt.close()
        
        st.markdown("#### <i class='bi bi-trash'></i> Manajemen Riwayat", unsafe_allow_html=True)
        col_del1, col_del2 = st.columns([3, 1])
        
        with col_del1:
            skenario_list = [s["Nama Skenario"] for s in st.session_state['history']]
            skenario_to_delete = st.multiselect("Pilih skenario yang ingin dihapus:", skenario_list)
            
        with col_del2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Hapus Terpilih", use_container_width=True):
                if skenario_to_delete:
                    # Filter history: simpan skenario yang TIDAK ada di list skenario_to_delete
                    st.session_state['history'] = [s for s in st.session_state['history'] if s["Nama Skenario"] not in skenario_to_delete]
                    st.rerun()
                else:
                    st.warning("Pilih minimal 1 skenario untuk dihapus.")
                    
        if st.button("Hapus Semua Riwayat"):
            st.session_state['history'] = []
            st.rerun()
    else:
        st.info("Belum ada skenario yang disimpan. Tulis nama skenario dan klik tombol Simpan di atas.")