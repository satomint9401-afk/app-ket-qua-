import streamlit as st
import collections

# Cấu hình trang Web
st.set_page_config(page_title="Phân Tích Thuật Toán Sicbo", page_icon="🎲", layout="wide")

st.title("🎲 HỆ THỐNG PHÂN TÍCH & GIÁM SÁT ĐIỂM GIAM SICBO")
st.caption("Ứng dụng phân tích dữ liệu xúc xắc chạy trên trình duyệt Web")

# Khởi tạo bộ lưu trữ Session (Giữ dữ liệu khi người dùng nhập nhiều phiên)
if "lich_su_diem" not in st.session_state:
    st.session_state.lich_su_diem = []
if "lich_su_bo_so" not in st.session_state:
    st.session_state.lich_su_bo_so = []
if "tong_so_phien" not in st.session_state:
    st.session_state.tong_so_phien = 0
if "phien_xuat_hien_gan_nhat_tong" not in st.session_state:
    st.session_state.phien_xuat_hien_gan_nhat_tong = {i: -1 for i in range(3, 19)}
if "thong_ke_tong" not in st.session_state:
    st.session_state.thong_ke_tong = collections.Counter()
if "logs" not in st.session_state:
    st.session_state.logs = []

# --- GIAO DIỆN NHẬP DỮ LIỆU ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📌 Nhập Kết Quả Phiên Mới")
    
    with st.form("form_nhap", clear_on_submit=True):
        input_user = st.text_input("Nhập 3 mặt xúc xắc (VD: 4,4,2 hoặc 6,1,5):", placeholder="4,4,2")
        btn_submit = st.form_submit_button("🔥 PHÂN TÍCH KẾT QUẢ", use_container_width=True)

    if st.button("🗑️ Xóa dữ liệu / Làm mới hệ thống"):
        st.session_state.lich_su_diem = []
        st.session_state.lich_su_bo_so = []
        st.session_state.tong_so_phien = 0
        st.session_state.phien_xuat_hien_gan_nhat_tong = {i: -1 for i in range(3, 19)}
        st.session_state.thong_ke_tong = collections.Counter()
        st.session_state.logs = []
        st.success("Đã xóa toàn bộ lịch sử!")
        st.rerun()

# --- XỬ LÝ LOGIC PHÂN TÍCH ---
if btn_submit and input_user:
    try:
        bo_so = [int(num.strip()) for num in input_user.split(",")]
        if len(bo_so) != 3 or any(n < 1 or n > 6 for n in bo_so):
            st.error("❌ Dữ liệu không hợp lệ! Vui lòng nhập đúng 3 mặt xúc xắc từ 1 đến 6.")
        else:
            st.session_state.tong_so_phien += 1
            bo_so.sort(reverse=True)
            tong_diem = sum(bo_so)
            ket_qua = "TÀI" if tong_diem >= 11 else "XỈU"

            # Lưu vào bộ nhớ
            st.session_state.lich_su_diem.append(tong_diem)
            st.session_state.lich_su_bo_so.append(bo_so)
            st.session_state.thong_ke_tong[tong_diem] += 1
            st.session_state.phien_xuat_hien_gan_nhat_tong[tong_diem] = st.session_state.tong_so_phien

            str_bo_so = "-".join(map(str, bo_so))
            
            # Phân tích Bão/Kép
            is_bao = (bo_so[0] == bo_so[1] == bo_so[2])
            is_kep = (bo_so[0] == bo_so[1] or bo_so[1] == bo_so[2]) and not is_bao

            msg_status = f" Phiên #{st.session_state.tong_so_phien}: Kết quả **{str_bo_so}** | Tổng **{tong_diem}** ({ket_qua})"
            if is_bao:
                msg_status += f" ⚡ **CẢNH BÁO NỔ BÃO {str_bo_so}!**"
            elif is_kep:
                msg_status += f" 🔗 **Cặp kép {bo_so[1]}-{bo_so[1]}**"
            
            st.session_state.logs.insert(0, msg_status)

    except ValueError:
        st.error("❌ Lỗi định dạng! Nhập theo dạng: số,số,số (Ví dụ: 5,2,6).")

# --- HIỂN THỊ BÁO CÁO TRÊN WEB ---
with col2:
    st.subheader("📊 Bảng Thống Kê & Giám Sát Điểm Giam")
    
    if st.session_state.tong_so_phien > 0:
        # Metrics tổng quan
        c1, c2, c3 = st.columns(3)
        c1.metric("Tổng số phiên", f"{st.session_state.tong_so_phien}")
        
        tong_nhieu_nhat = st.session_state.thong_ke_tong.most_common(1)[0]
        c2.metric("Tổng ra nhiều nhất", f"Tổng {tong_nhieu_nhat[0]}", f"{tong_nhieu_nhat[1]} lần")

        # Tính danh sách điểm giam
        danh_sach_giam = []
        for t in range(3, 19):
            lan_cuoi = st.session_state.phien_xuat_hien_gan_nhat_tong[t]
            so_phien_giam = st.session_state.tong_so_phien if lan_cuoi == -1 else st.session_state.tong_so_phien - lan_cuoi
            danh_sach_giam.append((t, so_phien_giam))
        danh_sach_giam.sort(key=lambda x: x[1], reverse=True)

        top_giam_diem, top_giam_so_phien = danh_sach_giam[0]
        c3.metric("Tổng bị giam sâu nhất", f"Tổng {top_giam_diem}", f"{top_giam_so_phien} phiên chưa ra")

        # Cảnh báo nghi ngờ
        if top_giam_so_phien >= 8:
            st.warning(f"⚠️ **CẢNH BÁO MẠNH:** Tổng **[{top_giam_diem}]** đã bị giam **{top_giam_so_phien} phiên** liên tiếp. Thuật toán có khả năng cao chuẩn bị xả nén mốc này!")

        st.write("---")
        st.write("📋 **Top 5 tổng điểm bị giam lâu nhất:**")
        cols_giam = st.columns(5)
        for idx, (t, g) in enumerate(danh_sach_giam[:5]):
            cols_giam[idx].info(f"**Tổng {t}**\n\nGiam: {g} phiên")

        # Lịch sử phiên
        st.write("📜 **Lịch sử các phiên vừa nhập:**")
        for log in st.session_state.logs[:10]:
            st.markdown(f"- {log}")
    else:
        st.info("Hãy nhập kết quả phiên đầu tiên ở bên trái để bắt đầu phân tích.")
