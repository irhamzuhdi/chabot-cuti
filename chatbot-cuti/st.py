import streamlit as st
from datetime import datetime, timedelta
import time

# Konfigurasi halaman
st.set_page_config(
    page_title="Chatbot Cuti & Izin Sakit",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS untuk tampilan lebih menarik
st.markdown("""
<style>
    /* Background gradient */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Chat container */
    .main .block-container {
        padding-top: 2rem;
        max-width: 1200px;
    }
    
    /* Custom card style */
    .custom-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    
    /* Metric cards */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        color: #667eea;
        font-weight: bold;
    }
    
    /* Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    /* Chat input */
    .stChatInput>div>div {
        border-radius: 25px;
        background: white;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* Headers */
    h1 {
        color: white;
        text-align: center;
        padding: 20px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        backdrop-filter: blur(10px);
    }
    
    h2, h3 {
        color: white;
    }
    
    /* Info box */
    .info-box {
        background: rgba(255, 255, 255, 0.95);
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 10px 0;
    }
    
    /* Welcome message */
    .welcome-box {
        background: white;
        padding: 30px;
        border-radius: 20px;
        text-align: center;
        margin: 20px 0;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
    }
    
    .welcome-box h2 {
        color: #667eea;
        margin-bottom: 15px;
    }
    
    .welcome-box p {
        color: #666;
        font-size: 1.1rem;
        line-height: 1.6;
    }
    
    /* Feature cards */
    .feature-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        transition: all 0.3s;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
    }
    
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 10px;
    }
    
    .feature-title {
        color: #667eea;
        font-size: 1.3rem;
        font-weight: bold;
        margin-bottom: 8px;
    }
    
    .feature-desc {
        color: #666;
        font-size: 0.95rem;
    }
</style>
""", unsafe_allow_html=True)

# Inisialisasi session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "step" not in st.session_state:
    st.session_state.step = "greeting"
if "leave_data" not in st.session_state:
    st.session_state.leave_data = {}
if "submissions" not in st.session_state:
    st.session_state.submissions = []
if "show_welcome" not in st.session_state:
    st.session_state.show_welcome = True

# Fungsi untuk menyimpan data pengajuan
def save_submission(data):
    submission = {
        "id": len(st.session_state.submissions) + 1,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        **data
    }
    st.session_state.submissions.append(submission)
    return submission["id"]

# Fungsi untuk menghitung hari kerja
def calculate_working_days(start_date, end_date):
    delta = end_date - start_date
    working_days = 0
    for i in range(delta.days + 1):
        day = start_date + timedelta(days=i)
        if day.weekday() < 5:
            working_days += 1
    return working_days

# Fungsi respons bot
def get_bot_response(user_message):
    user_lower = user_message.lower()
    
    if any(word in user_lower for word in ["cuti", "libur", "leave"]):
        st.session_state.step = "leave_type"
        st.session_state.leave_data["type"] = "cuti"
        st.session_state.show_welcome = False
        return """✨ **Pengajuan Cuti**

Silakan pilih jenis cuti yang Anda inginkan:

1️⃣ **Cuti Tahunan** - Cuti reguler yang menjadi hak karyawan
2️⃣ **Cuti Mendesak** - Untuk keperluan mendadak/darurat
3️⃣ **Cuti Besar** - Cuti untuk jangka waktu panjang

💬 Ketik nomor pilihan Anda (1/2/3)"""
    
    elif any(word in user_lower for word in ["sakit", "sick", "izin sakit"]):
        st.session_state.step = "sick_duration"
        st.session_state.leave_data["type"] = "izin_sakit"
        st.session_state.show_welcome = False
        return """🏥 **Pengajuan Izin Sakit**

Berapa hari Anda memerlukan izin sakit?

💬 Contoh: ketik "2 hari" atau "3"""
    
    elif st.session_state.step == "leave_type":
        if "1" in user_message or "tahunan" in user_lower:
            st.session_state.leave_data["leave_type"] = "Cuti Tahunan"
        elif "2" in user_message or "mendesak" in user_lower:
            st.session_state.leave_data["leave_type"] = "Cuti Mendesak"
        elif "3" in user_message or "besar" in user_lower:
            st.session_state.leave_data["leave_type"] = "Cuti Besar"
        else:
            return "❌ Mohon pilih nomor 1, 2, atau 3 untuk jenis cuti."
        
        st.session_state.step = "leave_start_date"
        return f"""✅ Anda memilih: **{st.session_state.leave_data['leave_type']}**

📅 Kapan tanggal **mulai** cuti Anda?

💬 Format: DD/MM/YYYY
📝 Contoh: 15/12/2024"""
    
    elif st.session_state.step == "leave_start_date":
        try:
            start_date = datetime.strptime(user_message.strip(), "%d/%m/%Y")
            st.session_state.leave_data["start_date"] = start_date
            st.session_state.step = "leave_end_date"
            return f"""✅ Tanggal mulai: **{start_date.strftime('%d %B %Y')}**

📅 Kapan tanggal **selesai** cuti Anda?

💬 Format: DD/MM/YYYY"""
        except:
            return "❌ Format tanggal salah. Mohon gunakan format DD/MM/YYYY\n📝 Contoh: 15/12/2024"
    
    elif st.session_state.step == "leave_end_date":
        try:
            end_date = datetime.strptime(user_message.strip(), "%d/%m/%Y")
            start_date = st.session_state.leave_data["start_date"]
            
            if end_date < start_date:
                return "❌ Tanggal selesai tidak boleh lebih awal dari tanggal mulai.\n\n📅 Silakan masukkan tanggal selesai yang benar."
            
            st.session_state.leave_data["end_date"] = end_date
            working_days = calculate_working_days(start_date, end_date)
            st.session_state.leave_data["duration"] = working_days
            st.session_state.step = "leave_reason"
            
            return f"""✅ Tanggal selesai: **{end_date.strftime('%d %B %Y')}**
⏱️ Durasi: **{working_days} hari kerja**

📝 Apa **alasan** cuti Anda?
💬 Jelaskan secara singkat."""
        except:
            return "❌ Format tanggal salah. Mohon gunakan format DD/MM/YYYY"
    
    elif st.session_state.step == "sick_duration":
        try:
            days = int(''.join(filter(str.isdigit, user_message)))
            st.session_state.leave_data["duration"] = days
            st.session_state.step = "sick_start_date"
            return f"""✅ Durasi izin sakit: **{days} hari**

📅 Mulai tanggal berapa?

💬 Format: DD/MM/YYYY
📝 Contoh: 15/12/2024"""
        except:
            return "❌ Mohon masukkan jumlah hari dengan benar.\n📝 Contoh: '2 hari' atau '3'"
    
    elif st.session_state.step == "sick_start_date":
        try:
            start_date = datetime.strptime(user_message.strip(), "%d/%m/%Y")
            days = st.session_state.leave_data["duration"]
            end_date = start_date + timedelta(days=days-1)
            
            st.session_state.leave_data["start_date"] = start_date
            st.session_state.leave_data["end_date"] = end_date
            st.session_state.step = "sick_reason"
            
            return f"""✅ Tanggal mulai: **{start_date.strftime('%d %B %Y')}**
✅ Tanggal selesai: **{end_date.strftime('%d %B %Y')}**

🏥 Apa **keluhan/penyakit** Anda?
💬 Jelaskan secara singkat."""
        except:
            return "❌ Format tanggal salah. Mohon gunakan format DD/MM/YYYY"
    
    elif st.session_state.step in ["leave_reason", "sick_reason"]:
        st.session_state.leave_data["reason"] = user_message
        st.session_state.step = "contact"
        return """✅ Alasan sudah dicatat.

📞 Nomor telepon yang bisa dihubungi?

💬 Contoh: 08123456789"""
    
    elif st.session_state.step == "contact":
        st.session_state.leave_data["contact"] = user_message
        st.session_state.step = "confirmation"
        
        data = st.session_state.leave_data
        leave_type = "Izin Sakit" if data["type"] == "izin_sakit" else data.get("leave_type", "Cuti")
        
        summary = f"""
📋 **RINGKASAN PENGAJUAN**

┌─────────────────────────────────┐
│ **Jenis:** {leave_type}
│ **Tanggal Mulai:** {data['start_date'].strftime('%d %B %Y')}
│ **Tanggal Selesai:** {data['end_date'].strftime('%d %B %Y')}
│ **Durasi:** {data['duration']} hari {"kerja" if data["type"] == "cuti" else ""}
│ **Alasan:** {data['reason']}
│ **Kontak:** {data['contact']}
└─────────────────────────────────┘

❓ Apakah data sudah benar?

💬 Ketik **"Ya"** untuk submit atau **"Tidak"** untuk mengulang."""
        return summary
    
    elif st.session_state.step == "confirmation":
        if "ya" in user_lower or "benar" in user_lower or "ok" in user_lower:
            submission_id = save_submission(st.session_state.leave_data)
            st.session_state.step = "greeting"
            st.session_state.leave_data = {}
            
            return f"""🎉 **PENGAJUAN BERHASIL!**

┌─────────────────────────────────┐
│ 📌 Nomor Pengajuan: **#{submission_id:03d}**
│ ⏳ Status: **Menunggu Persetujuan**
│ 📅 Tanggal: {datetime.now().strftime('%d %B %Y, %H:%M')}
└─────────────────────────────────┘

✅ Pengajuan Anda telah dikirim ke atasan. 
📧 Anda akan menerima notifikasi setelah disetujui.

Terima kasih! 😊

💬 Ada yang bisa saya bantu lagi?"""
        else:
            st.session_state.step = "greeting"
            st.session_state.leave_data = {}
            return "❌ Pengajuan dibatalkan.\n\n💬 Silakan mulai dari awal dengan mengetik 'cuti' atau 'izin sakit'."
    
    elif any(word in user_lower for word in ["halo", "hai", "hi", "hello"]):
        st.session_state.show_welcome = False
        return """👋 **Halo! Selamat datang di Chatbot Cuti & Izin Sakit**

Saya siap membantu Anda untuk:

📅 **Mengajukan Cuti** (Tahunan/Mendesak/Besar)
🏥 **Mengajukan Izin Sakit**
📊 **Melihat Riwayat Pengajuan**

💬 Apa yang ingin Anda ajukan hari ini?"""
    
    elif "riwayat" in user_lower or "history" in user_lower or "status" in user_lower:
        if not st.session_state.submissions:
            return "📭 Anda belum memiliki riwayat pengajuan.\n\n💬 Ketik 'cuti' atau 'sakit' untuk membuat pengajuan baru."
        
        history = "📊 **RIWAYAT PENGAJUAN**\n\n"
        for sub in st.session_state.submissions[-5:]:
            leave_type = "Izin Sakit" if sub["type"] == "izin_sakit" else sub.get("leave_type", "Cuti")
            history += f"┌─────────────────────────────────┐\n"
            history += f"│ 📌 **#{sub['id']:03d}** - {leave_type}\n"
            history += f"│ 📅 {sub['start_date'].strftime('%d/%m/%Y')} - {sub['end_date'].strftime('%d/%m/%Y')}\n"
            history += f"│ ⏱️ {sub['timestamp']}\n"
            history += f"└─────────────────────────────────┘\n\n"
        
        return history
    
    elif "bantuan" in user_lower or "help" in user_lower:
        return """❓ **PANDUAN PENGGUNAAN**

📝 **Cara menggunakan chatbot:**

1️⃣ Ketik **"cuti"** untuk mengajukan cuti
2️⃣ Ketik **"sakit"** untuk izin sakit
3️⃣ Ketik **"riwayat"** untuk melihat pengajuan
4️⃣ Ikuti instruksi yang diberikan chatbot

💡 **Tips:**
• Gunakan format tanggal DD/MM/YYYY
• Pastikan data sudah benar sebelum konfirmasi
• Simpan nomor pengajuan untuk tracking

📞 Untuk pertanyaan lebih lanjut, hubungi HR dept."""
    
    else:
        return """🤔 Maaf, saya tidak mengerti pesan Anda.

Silakan pilih:
• 📅 **"cuti"** - Untuk mengajukan cuti
• 🏥 **"sakit"** - Untuk izin sakit
• 📊 **"riwayat"** - Untuk melihat pengajuan
• ❓ **"bantuan"** - Untuk panduan lengkap"""

# Layout utama
st.title("🤖 Chatbot Cuti & Izin Sakit")

# Welcome screen
if st.session_state.show_welcome and len(st.session_state.messages) == 0:
    st.markdown("""
    <div class="welcome-box">
        <h2>👋 Selamat Datang!</h2>
        <p>Sistem pengajuan cuti dan izin sakit yang mudah dan cepat.<br>
        Cukup chat dengan bot kami untuk mengajukan permohonan Anda.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📅</div>
            <div class="feature-title">Cuti Fleksibel</div>
            <div class="feature-desc">Ajukan cuti tahunan, mendesak, atau cuti besar dengan mudah</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🏥</div>
            <div class="feature-title">Izin Sakit</div>
            <div class="feature-desc">Proses izin sakit cepat tanpa ribet dengan surat dokter</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <div class="feature-title">Tracking Mudah</div>
            <div class="feature-desc">Pantau status pengajuan Anda secara real-time</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.info("💬 **Mulai dengan mengetik 'cuti' atau 'sakit' di chat box di bawah!**")

col1, col2 = st.columns([2.5, 1])

with col1:
    # Tampilkan chat history
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("💬 Ketik pesan Anda di sini..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Mengetik..."):
                time.sleep(0.5)
                response = get_bot_response(prompt)
                st.markdown(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

with col2:
    st.markdown("### 📊 Statistik")
    
    st.metric("📝 Total Pengajuan", len(st.session_state.submissions))
    
    if st.session_state.submissions:
        cuti_count = sum(1 for s in st.session_state.submissions if s["type"] == "cuti")
        sakit_count = sum(1 for s in st.session_state.submissions if s["type"] == "izin_sakit")
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("📅 Cuti", cuti_count)
        with col_b:
            st.metric("🏥 Sakit", sakit_count)
    
    st.markdown("---")
    st.markdown("### ⚡ Quick Actions")
    
    if st.button("📅 Ajukan Cuti", use_container_width=True, type="primary"):
        st.session_state.messages.append({"role": "user", "content": "cuti"})
        st.rerun()
    
    if st.button("🏥 Izin Sakit", use_container_width=True, type="primary"):
        st.session_state.messages.append({"role": "user", "content": "izin sakit"})
        st.rerun()
    
    if st.button("📊 Lihat Riwayat", use_container_width=True):
        st.session_state.messages.append({"role": "user", "content": "riwayat"})
        st.rerun()
    
    st.markdown("---")
    
    if st.button("🗑️ Hapus Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.step = "greeting"
        st.session_state.leave_data = {}
        st.session_state.show_welcome = True
        st.rerun()
    
    st.markdown("---")
    st.caption("💡 Ketik 'bantuan' untuk panduan")
    st.caption("⏰ " + datetime.now().strftime("%H:%M:%S"))