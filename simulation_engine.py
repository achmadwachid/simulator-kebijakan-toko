import joblib
import numpy as np
import streamlit as st
from typing import Tuple

# ── Konstanta ─────────────────────────────────────────────────────────────────
DELTA_SIGNIFIKAN = 5.0   # Ambang batas perubahan keuntungan yang dianggap signifikan (Juta Rp)


@st.cache_resource(show_spinner=False)
def load_model() -> dict:
    """
    Memuat model ML beserta data baseline dari file .pkl.
    show_spinner=False mematikan indikator 'Running...' bawaan Streamlit.

    Returns:
        dict: Berisi 'model', 'baseline_pred', dan 'baseline'.
    """
    return joblib.load('model_simulator.pkl')


def run_simulation(
    model, baseline_pred: float,
    new_iklan: float, new_diskon: float
) -> Tuple[float, float]:
    """
    Menjalankan simulasi prediksi keuntungan.

    Args:
        model: Objek model machine learning.
        baseline_pred (float): Nilai prediksi baseline.
        new_iklan (float): Anggaran iklan dari input user.
        new_diskon (float): Besaran diskon dari input user.

    Returns:
        Tuple[float, float]: (prediksi_akhir, delta_dari_baseline)
    """
    intervention_input = np.array([[new_iklan, new_diskon]])
    prediction         = model.predict(intervention_input)[0]
    delta_y            = prediction - baseline_pred
    return prediction, delta_y


def generate_narasi(
    iklan: float, diskon: float, hasil: float,
    delta: float, delta_pct: float, baseline: dict
) -> Tuple[str, str, str, str]:
    """
    Menghasilkan narasi rekomendasi berbasis aturan (rule-based).
    Mengembalikan data murni — tidak mengandung markup HTML/ikon.
    Formatting HTML dilakukan di layer UI (app.py).

    Args:
        iklan (float): Anggaran iklan saat simulasi.
        diskon (float): Persentase diskon saat simulasi.
        hasil (float): Nilai prediksi keuntungan akhir.
        delta (float): Selisih keuntungan dengan baseline.
        delta_pct (float): Persentase perubahan dari baseline.
        baseline (dict): Nilai awal iklan dan diskon.

    Returns:
        Tuple[str, str, str, str]:
            css_class, icon_name (Bootstrap Icons), status_label, teks_narasi
    """
    iklan_base  = baseline['iklan']
    diskon_base = baseline['diskon']

    iklan_ket  = "dinaikkan" if iklan  > iklan_base  else ("diturunkan" if iklan  < iklan_base  else "tidak diubah")
    diskon_ket = "dinaikkan" if diskon > diskon_base else ("diturunkan" if diskon < diskon_base else "tidak diubah")

    if delta > DELTA_SIGNIFIKAN:
        return (
            "ai-naik",
            "graph-up-arrow",
            "MENGUNTUNGKAN",
            f"Skenario ini <b>sangat disarankan</b> untuk diterapkan. "
            f"Anggaran iklan yang {iklan_ket} menjadi <b>Rp {iklan:.0f} Juta</b> "
            f"dan diskon yang {diskon_ket} menjadi <b>{diskon:.0f}%</b> "
            f"menghasilkan proyeksi keuntungan <b>Rp {hasil:.2f} Juta</b>, "
            f"meningkat <b>Rp {delta:.2f} Juta ({delta_pct:.1f}%)</b> dari baseline. "
            f"Strategi iklan agresif terbukti efektif mendorong pendapatan."
        )

    if 0 < delta <= DELTA_SIGNIFIKAN:
        return (
            "ai-naik",
            "hand-thumbs-up-fill",
            "SEDIKIT MENGUNTUNGKAN",
            f"Skenario ini memberikan <b>peningkatan kecil</b> sebesar "
            f"<b>Rp {delta:.2f} Juta ({delta_pct:.1f}%)</b>. "
            f"Dengan iklan <b>Rp {iklan:.0f} Juta</b> dan diskon <b>{diskon:.0f}%</b>, "
            f"hasilnya positif namun belum optimal. "
            f"Pertimbangkan menaikkan anggaran iklan lebih lanjut untuk hasil maksimal."
        )

    if delta == 0:
        return (
            "ai-netral",
            "dash-circle",
            "TIDAK BERUBAH",
            f"Skenario ini menghasilkan keuntungan yang <b>sama persis</b> dengan baseline. "
            f"Tidak ada manfaat tambahan dari perubahan ini."
        )

    if -DELTA_SIGNIFIKAN <= delta < 0:
        return (
            "ai-turun",
            "exclamation-triangle-fill",
            "SEDIKIT MERUGIKAN",
            f"Skenario ini menurunkan keuntungan sebesar "
            f"<b>Rp {abs(delta):.2f} Juta ({abs(delta_pct):.1f}%)</b>. "
            f"Diskon <b>{diskon:.0f}%</b> terlalu tinggi sehingga menggerus margin. "
            f"Coba kurangi diskon atau naikkan anggaran iklan untuk mengimbanginya."
        )

    return (
        "ai-turun",
        "x-octagon-fill",
        "TIDAK DISARANKAN",
        f"Skenario ini <b>sangat tidak disarankan</b>. "
        f"Penurunan keuntungan sebesar <b>Rp {abs(delta):.2f} Juta ({abs(delta_pct):.1f}%)</b> "
        f"cukup signifikan. Kombinasi iklan <b>Rp {iklan:.0f} Juta</b> dan diskon "
        f"<b>{diskon:.0f}%</b> tidak efisien. Kembalikan ke kondisi mendekati baseline."
    )

# ── Fitur: Pencarian Optimal ────────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def _get_all_predictions(_model) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Menghitung prediksi untuk seluruh 2.601 kombinasi (51 iklan x 51 diskon).
    Disimpan dalam cache agar pencarian optimal instan.
    """
    iklan_vals = np.arange(51)
    diskon_vals = np.arange(51)
    
    # Buat grid 2D
    I, D = np.meshgrid(iklan_vals, diskon_vals, indexing='ij')
    
    # Flatten untuk diprediksi model sekaligus
    X_grid = np.column_stack((I.ravel(), D.ravel()))
    preds = _model.predict(X_grid)
    
    # Reshape kembali ke matriks 51x51
    Z = preds.reshape(51, 51)
    
    return I, D, Z


def find_optimal_scenario(model) -> dict:
    """Mencari kombinasi dengan profit maksimal."""
    I, D, Z = _get_all_predictions(model)
    max_idx = np.unravel_index(np.argmax(Z, axis=None), Z.shape)
    
    return {
        'best_iklan': I[max_idx],
        'best_diskon': D[max_idx],
        'max_profit': Z[max_idx],
        'grid_I': I,
        'grid_D': D,
        'grid_Z': Z
    }