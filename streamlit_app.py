import streamlit as st  # streamlit=1.47.1
import pandas as pd     # pandas=2.3.1
import os, time

from selenium import webdriver  # selenium=4.34.2
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

import shutil
from openpyxl import Workbook, load_workbook    # openpyxl=3.1.5
from openpyxl.styles import PatternFill
from io import BytesIO
import xlsxwriter   # xlsxwriter=3.2.5
import tempfile
#from playwright.sync_api import sync_playwright    #playwright==1.54.0
#--------------------------------------------------------------
long_text1= '''
Go to SMARTS
https://smarts.waterboards.ca.gov/smarts/SwPublicUserMenu.xhtml
Click on “Public User Menu”
Click on “Download NOI Data By Regional Board”
Select your region from the dropdown menu
Click on both “Industrial Application Specific Data” and “Industrial Ad Hoc Reports - Parameter Data”
Data will be downloaded to two separate .txt files, each titled “file”
'''

# Cac Ham Phu --------------------------------------------------
# Ham thu viec doc file txt/cvs dung encoding nao khong gay loi
def check_read_file_txt(filetxt):
    encodings_to_try = ['utf-8', 'utf-8-sig', 'cp1252', 'cp1258', 'utf-16']

    for enc in encodings_to_try:
        try:
            df = pd.read_csv('file.txt', delimiter='\t', encoding=enc)
            print(f"✅ Thành công với encoding: {enc}")
            break
        except Exception as e:
            print(f"❌ {enc}: {e}")

# Ham tai file txt du lieu dang cvs cua cac mien thuoc bang Cali
@st.cache_data
def download_data_smarts(regions):
    #xoa thu muc downloads va tao lai de chi chua 2 file du lieu
    folder_path_cu = 'downloads'
    # Xóa thư mục nếu tồn tại
    if os.path.exists(folder_path_cu):
        shutil.rmtree(folder_path_cu)  # Xóa toàn bộ thư mục và nội dung bên trong

    download_dir = os.path.abspath("downloads")
    os.makedirs(download_dir, exist_ok=True)

    # ✅ CẤU HÌNH CHROME:
    options = webdriver.ChromeOptions()
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "profile.default_content_setting_values.automatic_downloads": 1   # DÒNG QUAN TRỌNG DE TAT THONG BAO
    }
    options.add_experimental_option("prefs", prefs)
    options.add_argument("--headless")  # chạy ẩn trình duyệt

    # ✅ KHỞI TẠO TRÌNH DUYỆT
    driver = webdriver.Chrome(options=options)

    driver.get("https://smarts.waterboards.ca.gov/smarts/SwPublicUserMenu.xhtml")
    print("✅ Vào trang chính")

    WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Download NOI Data By Regional Board"))
    ).click()

    WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) > 1)
    driver.switch_to.window(driver.window_handles[-1])
    print("✅ Đã chuyển sang tab mới")

    links = [
        "Industrial Application Specific Data",
        "Industrial Ad Hoc Reports - Parameter Data"
    ]

    def wait_for_download_and_get_new_file(before_files, timeout=40):
        for _ in range(timeout * 2):
            time.sleep(0.5)
            after_files = set(os.listdir(download_dir))
            new_files = after_files - before_files
            txt_files = [f for f in new_files if f.endswith(".txt")]
            if txt_files:
                return txt_files[0]
        return None
    #---------------------
    region = regions
    print(f"\n🔹 Chọn Region: {region}")
    dropdown = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.NAME, "intDataFileDowloaddataFileForm:intDataDumpSelectOne"))
    )
    Select(dropdown).select_by_visible_text(region)
    time.sleep(3)  # Đợi dropdown load lại
    
    lfile_datai = []

    for j, name in enumerate(links):
        try:
            print(f"📥 Đang click tải: {name}")
            before = set(os.listdir(download_dir))

            link_elem = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.LINK_TEXT, name))
            )
            driver.execute_script("arguments[0].click();", link_elem)

            fname = wait_for_download_and_get_new_file(before)
            if fname:
                # Tạo tên file chuẩn theo Region + tên file
                src = os.path.join(download_dir, fname)
                dst_name = f"{region} - {name}.txt"
                dst_name = dst_name.replace(" ", "_")  # Nếu muốn
                dst = os.path.join(download_dir, dst_name)
                os.rename(src, dst)
                print(f"File đã lưu: {dst}")
                lfile_datai.append(f"{dst}")
            else:
                print("❌ Không tìm thấy file mới sau khi tải")
        except Exception as e:
            print(f"❌ Lỗi khi tải {name} ở Region {region}: {e}")

    driver.quit()
    print("\n🎉 Hoàn tất tải file cho "+region)
    return lfile_datai
    # CHU Y rang neu ten file dat trung voi file da co thi that bai.
# CAC HAM CHINH-----------------------------------------------------
def ThucThiPhan_4():
    return    


@st.cache_data
def Doc_hthi_data(uploaded_file):
    try:
        # Đọc file Excel thành DataFrame
        df = pd.read_excel(uploaded_file, sheet_name='Data')

        # 1. Sắp xếp dữ liệu theo nhiều cấp độ (multi-level sort):
        df_sorted = df.sort_values(
                by=["OLD/NEW", "PARAMETER", "RESULT"],
                ascending=[True, True, False]
        )
        # 2. Lọc dữ liệu có OLD/NEW == 'New':
        df_new = df_sorted[df_sorted["OLD/NEW"] == "New"]
        # 3. Tô màu (highlight) exceedances thì không thể hiển thị trong DataFrame thông thường nhưng có thể dùng:
        # pandas.ExcelWriter + openpyxl để ghi file Excel có màu.
        # Hoặc đơn giản chỉ đánh dấu bằng cột mới "Exceed" = True/False
        # 4. So sánh kết quả với ngưỡng NAL/NEL/TNAL:
        # tao dic chua nguong
        nal_thresholds = {
            "Ammonia": 4.7,
            "Cadmium": 0.0031,
            "Copper": 0.06749,
            # v.v...
        }
        # Rồi kiểm tra:
        def is_exceed(row):
            param = row["PARAMETER"]
            result = row["RESULT"]
            return result > nal_thresholds.get(param, float('inf'))
        
        df_new["EXCEED"] = df_new.apply(is_exceed, axis=1)
        # 5. Ghi chú các facility cần theo dõi → bạn có thể lọc hoặc thêm cột "Flagged" dựa vào danh sách thủ công.


        st.success(f"Đã tải lên: {uploaded_file.name}")
        st.subheader("📄 Dữ liệu từ file:")

        # Bước 3: Hiển thị DataFrame với cuộn dọc (giả lập 3 dòng)
        st.dataframe(df) #, height=120, use_container_width=True)

    except Exception as e:
        st.error(f"Lỗi khi đọc file: {e}")
    
def Ht_CaiMuonXem_0(tepxlsx):
    # 1.Đọc file Excel thành DataFrame
    df = pd.read_excel(tepxlsx, sheet_name='Data')
    # 2. Sắp xếp dữ liệu theo nhiều cấp độ (multi-level sort):
    df_sorted = df.sort_values(
        by=["OLD/NEW", "PARAMETER", "RESULT"],
        ascending=[True, True, False]
    )
    #Dua vao xlsx de xem kq sx
    tepxlsxdexem = "Data_Tracker_3-1.xlsx"
    df_sorted.to_excel(tepxlsxdexem, sheet_name='Datanew', index=False)
    os.startfile(tepxlsxdexem)

#---------------------------------
def Ht_CaiMuonXem_1(uploaded_file):
    uploaded_file = st.file_uploader("Tải lên Data_Tracker_New.xlsx", type=["xlsx"])
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        # Ghi tạm ra file Excel để xử lý openpyxl
        output = BytesIO()
        df.to_excel(output, index=False)
        output.seek(0)

        # Load và tô màu
        wb = load_workbook(output)
        ws = wb.active

        # Tìm vị trí các cột "OLD/NEW" và "COSO"
        header = [cell.value for cell in ws[1]]

        try:
            old_new_col_idx = header.index("OLD/NEW") + 1
            coso_col_idx = header.index("FACILITY_NAME") + 1
        except ValueError as e:
            raise Exception(f"Không tìm thấy cột: {e}")

        # Tô màu vàng cho dòng 'new' thuộc cơ sở 'CS1'
        yellow_fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")

        # Duyệt từng dòng
        for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
            old_new_val = str(row[old_new_col_idx - 1].value).strip().lower() if row[old_new_col_idx - 1].value else ""
            coso_val = str(row[coso_col_idx - 1].value).strip() if row[coso_col_idx - 1].value else ""

            if old_new_val == "old" and coso_val == 'CS1':
                for cell in row:
                    cell.fill = yellow_fill
                # Dòng này được giữ lại
            else:
                # Ẩn dòng không khớp điều kiện
                ws.row_dimensions[row[0].row].hidden = True

        # Lưu file mới
        wb.save("filtered_CS1_new.xlsx")
        os.startfile("filtered_CS1_new.xlsx")

        # Lưu lại và cho phép tải xuống
        #final_output = BytesIO()
        #wb.save(final_output)
        #final_output.seek(0)

        #st.download_button("📥 Tải file đã tô màu", final_output, "T_to_mau.xlsx")

def ThucThiPhan_3():
    # Bước 1: Upload fle Data_Tracker_New.xlsx
    uploaded_file = st.file_uploader('Upload Data_Tracker_New.xlsx',type=['xlsx'])
    # Bước 2: Nếu có file, test chon header, sau nay bò
    if uploaded_file is not None and "Data_Tracker_New" in uploaded_file.name :
        df = pd.read_excel(uploaded_file, nrows=0)
        headers = df.columns.tolist()
        headers = st.multiselect("Choose headers",  headers,)
        if headers:
            # in header cuoi vua chon
            st.write(headers[-1])

    # Bước 3 : chay ham chon trong menu
    # list cac viec va  ham
    op_listCaiMuonXem = {
        "Cột OLD/NEW có giá trị new": Ht_CaiMuonXem_0,
        "Cột OLD/NEW có giá trị old": Ht_CaiMuonXem_1
    }
    # menu chon ham/viec
    viec_chon = st.selectbox(
        "Chon cai ban muon xem", 
        (op_listCaiMuonXem.keys()),
        index=None,
        placeholder="Chon hien thi...",
    )
    # chay ham da chon
    if viec_chon:
        # chay ham tuong ung voi key chon_with_viec, ham nay co ten la gia tri cua key do, 
        # them () de chay ham, tham so la file excel da tai len
        op_listCaiMuonXem[viec_chon](uploaded_file)   # 👉 Gọi hàm tuong ung
        st.write("Xong phan 3")

# ---- phuc vu cho ThucThiPhan_2()------------------
@st.cache_data
def Combined_to_data_tracker(uploaded_tracker):
    try:
        # Read input files
        sheet1 = pd.read_excel(uploaded_tracker, sheet_name='Sheet1', header=None, dtype=str)
        sheet2 = pd.read_excel(uploaded_tracker, sheet_name='Sheet2', dtype=str)
        df_tracker = pd.read_excel(uploaded_tracker, sheet_name='Data', dtype=str)

        # Clean Sheet1
        cols_to_delete = list(range(15, 28)) + list(range(31, 38)) + [0, 4, 5, 6, 7, 11]
        # Chỉ lấy các chỉ số cột cần xóa, nhưng phải nhỏ hơn num_cols
        num_cols = sheet1.shape[1]
        cols_to_delete = [col for col in cols_to_delete if col < num_cols]
        sheet1_cleaned = sheet1.drop(sheet1.columns[cols_to_delete], axis=1)

        sheet1_cleaned.columns = sheet1_cleaned.iloc[0]
        sheet1_cleaned = sheet1_cleaned[1:]

        # Reorder columns
        cols = list(sheet1_cleaned.columns)
        if 'WDID' in cols and 'APP_ID' in cols:
            cols.remove('WDID')
            cols.insert(cols.index('APP_ID'), 'WDID')
        if 'FACILITY_NAME' in cols and 'OPERATOR_NAME' in cols:
            cols.remove('FACILITY_NAME')
            cols.insert(cols.index('OPERATOR_NAME'), 'FACILITY_NAME')
        sheet1_cleaned = sheet1_cleaned[cols]


        # Clean Sheet2 and merge SIC data
        sheet2_cleaned = sheet2.drop(sheet2.columns[2:8], axis=1)
        sheet2_cleaned = sheet2_cleaned.iloc[:, :5]  # Chỉ lấy 5 cột đầu tiên
        sheet2_cleaned.columns = ['A', 'APP_ID', 'PRIMARY_SIC', 'SECONDARY_SIC', 'TERTIARY_SIC']
        sheet2_cleaned = sheet2_cleaned[['APP_ID', 'PRIMARY_SIC', 'SECONDARY_SIC', 'TERTIARY_SIC']]
        merged = pd.merge(sheet1_cleaned, sheet2_cleaned, on='APP_ID', how='left')
        merged = merged.rename(columns={'PRIMARY_SIC': '1', 'SECONDARY_SIC': '2', 'TERTIARY_SIC': '3'})
        merged['2'] = merged['2'].replace('0', pd.NA)
        merged['3'] = merged['3'].replace('0', pd.NA)
        merged['OLD/NEW'] = 'new'

        # Add "Old" tag to tracker and combine
        df_tracker['OLD/NEW'] = 'old'
        df_combined = pd.concat([df_tracker, merged], ignore_index=True)

        # Export to Excel in-memory
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_combined.to_excel(writer, sheet_name='Data', index=False)
        output.seek(0)
        return output 
    except Exception as e:
        st.error(f"⚠️ An error occurred: {e}")


@st.cache_data
def Txt_to_data_tracker(df1, df2, df_data):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df1.to_excel(writer, sheet_name="Sheet1", index=False)
        df2.to_excel(writer, sheet_name="Sheet2", index=False)
        df_data.to_excel(writer, sheet_name="Data", index=False)
    output.seek(0)
    return output
     



# -----------------
def ThucThiPhan_2():    
    uploaded_files = st.file_uploader(
        'Upload your files',
        type=['txt', 'xlsx'],  
        accept_multiple_files=True
    )
    if uploaded_files and len(uploaded_files) == 3:
        # Phân loại file theo đuôi và tên
        uploaded_f1 = next((f for f in uploaded_files if "industrial_ad_hoc" in f.name.lower()), None)
        uploaded_f3 = next((f for f in uploaded_files if f.name.lower().endswith(".xlsx")), None)
        # f2 là file .txt còn lại (không phải f1)
        uploaded_f2 = next((f for f in uploaded_files if f != uploaded_f1 and f.name.lower().endswith(".txt")), None)

        if uploaded_f1 and uploaded_f2 and uploaded_f3:
            try:
                df1 = pd.read_csv(uploaded_f1, sep='\t', encoding='cp1252')
                df2 = pd.read_csv(uploaded_f2, sep='\t', encoding='cp1252')
                df_data = pd.read_excel(uploaded_f3, sheet_name="Data")  # Chỉ đọc sheet "Data"
            except Exception as e:
                st.error(f"⚠️ Lỗi khi đọc file: {e}")
                st.stop()
            # Dua 2 txt vao excel Data_Tracker.xlsx tu 3 file tai len
            # va tra ve file ao data_tracker_upload da chua them 2 txt   
            data_tracker_upload = Txt_to_data_tracker(df1, df2,df_data)

            # Xu li 2 sheet txt tren data_tracker_upload append vao Data sheet
            # va tra ve tep  Data_Tracker_New de download
            Data_Tracker_New = Combined_to_data_tracker(data_tracker_upload)    

            st.success("✅ Đã tạo Data_Tracker_New.xlsx tu 3 file tai len.")
            st.download_button(
                label="📥 Tải xuống file Excel mới: Data_Tracker_New.xlsx",
                data=Data_Tracker_New,
                file_name="Data_Tracker_New.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning('Hãy đảm bảo đúng file "...Industrial_Application...txt", file "...Industrial_ad_hoc...txt", và file "Data_tracker.xlsx" ')
    else:
        st.info('Vui lòng upload đủ 3 file: "...Industrial_Application...txt", "...Industrial_Ad_Hoc...txt", và "Data_tracker.xlsx" ')
    return

#-------------------
def ThucThiPhan_1():
    # cac vung de chon
    regions = st.selectbox("Select a Region:", 
                ("Region 1 - North Coast",
                "Region 2 - San Francisco Bay",
                "Region 3 - Central Coast",
                "Region 4 - Los Angeles",
                "Region 5F - Fresno",
                "Region 5R - Redding",
                "Region 5S - Sacramento",
                "Region 6A - South Lake Tahoe",
                "Region 6B - Victorville",
                "Region 7 - Colorado River Basin",
                "Region 8 - Santa Ana",
                "Region 9 - San Diego"),
                index=None,
                placeholder="No selected Region",
                )
    #neu mot vung duoc chon thi lam
    LOI='OK'
    if regions:
        placeholder_1 = st.empty()
        placeholder_1.write('Wait for downloading 2 files of ' + regions)
        #thuc thi ham download_data_smarts(regions) va tra ve list cac file da tai 
        try :
            lfile_datai = download_data_smarts(regions)
            placeholder_1.write('Downloaded files:')
            st.write(lfile_datai)
        except:
            LOI='LOI'
            placeholder_1.write('Tai file không đạt!')
    if LOI == 'LOI':
        st.write('Nếu không đạt, mở trực tiếp trang sau làm theo các bước để tải:')
        st.markdown("1-[Open Page SMARTS](https://smarts.waterboards.ca.gov/smarts/SwPublicUserMenu.xhtml)", unsafe_allow_html=True)
        st.write('2-Click on “Download NOI Data By Regional Board”')
        st.write('3-Select your region from the dropdown menu')
        st.write('4-Click on both “Industrial Application Specific Data” and “Industrial Ad Hoc Reports - Parameter Data”')
        st.write('5-Data will be downloaded to two separate .txt files, each titled “file”')
        st.write('6-Nên đổi tên 2 file thành Industrial_Application_Specific_Data và Industrial_Ad_Hoc_Reports_-_Parameter_Data rồi chép vào thư mục riêng của bạn để dễ làm việc ở các bước sau.')

def vote(item):
    st.write(f"Why is {item} your favorite?")
    reason = st.text_input("Because...")

#========================= MAIN =====================================================================
with st.sidebar:
    st.header('Lập trình theo tài liệu này:')
    # Đọc nội dung file Markdown
    with open("hd-lam-app-cho-thong.md", "r", encoding="utf-8") as f:
        md_content = f.read()
    st.markdown(md_content, unsafe_allow_html=True)
    #    with st.popover("Phần I: Download the data"):
    #scrolling_box = (f"""
    #            <div style='overflow-y: auto; height: 300px; 
    #            border: 1px solid lightgray; padding: 10px'>{md_content}</div>
    #            """)
    #popover.markdown(scrolling_box, unsafe_allow_html=True)

# TIEU DE APP
st.header('🏷️Trình hỗ trợ quản lý môi trường nước')

# PHAN 1: TAI FILES TXT DU LIEU DAT VAO EXCEL
#--------------------------------------------
st.subheader('✅ I. Download the data', divider=True)
ThucThiPhan_1()

# Them data moi vao trinh theo doi
#---------------------------------
st.subheader('✅ II. Add the new data to your tracker', divider=True)
ThucThiPhan_2()

long_text= '''
A.
Go to SMARTS
https://smarts.waterboards.ca.gov/smarts/SwPublicUserMenu.xhtml

B.
Đưa Sheet2 về định dạng phù hợp với trình theo dõi của bạn
Sao chép (CTRL+C) và dán (CTRL+V) toàn bộ tệp văn bản "Dữ liệu Ứng dụng Công nghiệp Cụ thể" vào ô đầu tiên trong Sheet2 (A1).
Nhấp vào Hàng 1 (hàng tiêu đề), chuyển đến tab "Dữ liệu" trong Excel và nhấp vào nút "Lọc".
Nhấp vào Cột B (cột ID Ứng dụng), chuyển đến tab "Trang chủ" trong Excel và từ nút "Định dạng Điều kiện", nhấp vào "Đánh dấu Quy tắc Ô" rồi chọn "Giá trị Trùng lặp" từ menu thả xuống hiện ra. Nhấn "OK" trên hộp văn bản hiện ra.
Đi đến menu thả xuống của Cột B và nhấp vào "Lọc theo màu", sau đó chọn hộp màu. Thao tác này sẽ chỉ hiển thị các hàng trùng lặp.
Nhấp vào menu thả xuống của Cột D (cột trạng thái) và bỏ chọn "Đang hoạt động" để chỉ hiển thị các hàng có trạng thái khác "Đang hoạt động".
Xóa tất cả các hàng đang hiển thị.
Trong tab "Dữ liệu" trong Excel, nhấn "Xóa" để xem các hàng còn lại.
Sắp xếp lại các cột và xóa các cột thừa cho phù hợp với trình theo dõi của bạn.
Xóa các cột từ AF (Tên nguồn nước tiếp nhận) đến AL (cột ngoài cùng bên phải có văn bản)
Xóa các cột từ P (Vĩ độ cơ sở) đến AB (Tỷ lệ phần trăm không thấm nước của vị trí)
Xóa đồng thời các cột A, E-H và L.
Di chuyển cột B (WDID) sang trái Cột A (ID ứng dụng). Di chuyển cột E (Tên cơ sở) sang trái Cột D (Tên người vận hành).
Sau khi sắp xếp lại, các cột trong Sheet2 sẽ trông như sau: A – WDID; B – ID ứng dụng; C – Trạng thái; D – Tên cơ sở; E – Tên người vận hành; F – Địa chỉ; G – Thành phố; H – Tiểu bang; I – Mã bưu chính; J – SIC chính; K – SIC phụ; L – SIC thứ ba

C.
Đưa Sheet1 về định dạng phù hợp với trình theo dõi của bạn
Sao chép (CTRL+C) và dán (CTRL+V) toàn bộ tệp văn bản "Báo cáo Ad Hoc Công nghiệp - Dữ liệu Tham số" vào ô đầu tiên trong Sheet1 (A1).
Vào tab "Dữ liệu" trong Excel, nhấp vào nút "Xóa Trùng lặp" và nhấn "OK" trên hộp thoại hiện ra.
Trong cột B (WDID), hãy lọc các kết quả hiển thị "4 56" (lưu ý khoảng cách giữa 4 và 56), sau đó xóa tất cả các hàng hiển thị. "4 56" là mã quận của WDID đối với quận Ventura, do đó chúng tôi sẽ không nhắm mục tiêu đến bất kỳ cơ sở nào trong số đó.
Trong tab "Dữ liệu" trong Excel, nhấn "Xóa" để xem các hàng còn lại.
Xóa tất cả các cột không có trong trình theo dõi của bạn (các cột A, J, K, U, X và Y).
Sau khi xóa các cột này, các cột Sheet1 sẽ trông như sau: A – WDID; B – App ID; C – Trạng thái; D – Tên cơ sở; E – Tên nhà điều hành; F – Địa chỉ; G – Thành phố; H – Tiểu bang; I – Mã bưu chính; J – SIC chính; K – SIC phụ; L – SIC bậc ba

D.
Filter Sheet1 chỉ dành cho dữ liệu mẫu mới
Nhấp chuột phải vào Cột B (Mã ứng dụng) và nhấn "insert", thao tác này sẽ chèn một cột trống sang bên trái.
Trong ô trống đầu tiên (B2), hãy nhập công thức sau rồi nhấn enter: =VLOOKUP(J2,Data!O:P,2,FALSE)
Nếu bạn di chuyển chuột đến góc dưới bên phải của ô B2, bạn sẽ thấy con trỏ dấu cộng màu trắng chuyển thành dấu cộng màu đen mỏng. Khi đó, hãy nhấp đúp chuột và Excel sẽ điền công thức cho phần còn lại của cột.
Sau đó, nhấp vào cột, nhấn CTRL+C để sao chép, rồi nhấp chuột phải và trong mục "tùy chọn dán", hãy nhấp vào biểu tượng có chữ "123" nhỏ ở góc, thao tác này sẽ chỉ dán kết quả thay vì công thức.
Sắp xếp cột B từ nhỏ đến lớn, sau đó từ danh sách thả xuống của Cột B hiển thị tất cả các số, cuộn xuống cuối trang và bỏ chọn "Không áp dụng". Thao tác này sẽ chỉ hiển thị các ô có số.
Xóa tất cả các hàng đang hiển thị.
Trong tab “Dữ liệu” trong Excel, nhấn “Xóa” để xem các hàng còn lại.

E.
Kiểm tra xem các tiện ích trong Sheet1 có đang hoạt động không.
Trong ô B2 của Sheet1, xóa "N/A" và nhập công thức sau, rồi nhấn Enter: =VLOOKUP(C2,Sheet2!B:D,2,FALSE)
Nếu bạn di chuyển chuột đến góc dưới bên phải của ô B2, bạn sẽ thấy con trỏ dấu cộng màu trắng chuyển thành dấu cộng màu đen mỏng. Khi đó, hãy nhấp đúp chuột và Excel sẽ điền công thức cho phần còn lại của cột.
Sau đó, nhấp vào cột, nhấn CTRL+C để sao chép, rồi nhấp chuột phải và trong mục "tùy chọn dán", nhấp vào biểu tượng có chữ "123" nhỏ ở góc, biểu tượng này sẽ chỉ dán kết quả thay vì công thức.
Sắp xếp cột B theo thứ tự từ A đến Z, sau đó từ danh sách thả xuống của Cột B hiển thị các tùy chọn trạng thái, bỏ chọn "đang hoạt động". Thao tác này sẽ chỉ hiển thị các ô là tiện ích không hoạt động.
Xóa tất cả các hàng đang hiển thị.
Trong tab "Dữ liệu" trong Excel, nhấn "Xóa" để xem các hàng còn lại.

F.
Chọn các thông số cần theo dõi trong Sheet1
Trong Sheet1, xóa Cột B.
Nhấp chuột phải vào cột N (cột thông số) và nhấn Insert, thao tác này sẽ chèn một cột trống bên trái cột N.
Từ menu thả xuống của cột thông số (bây giờ sẽ là cột O), hãy nhấp vào hộp kiểm bên cạnh "(Select All") để bỏ chọn tất cả các thông số. Sau đó, hãy xem qua và đánh dấu vào từng thông số bạn muốn có trong trình theo dõi, rồi nhấn "OK".
Các thông số mà LAW đã theo dõi cho đến nay như sau (có thể bổ sung thêm thông số tùy theo nhu cầu cụ thể của từng cơ sở): Nhôm; Amoniac; Asen; Nhu cầu oxy sinh hóa (BOD); Cadimi; Nhu cầu oxy hóa học (COD); Đồng; Xyanua; E. coli; Enterococci MPN; Coliform phân; Sắt; Chì; Magiê; Thủy ngân; Niken; Nitrat; Nitrit; Nitrit cộng Nitrat (N+N); Dầu mỡ (O&G); pH; Phốt pho; Selen; Bạc; Tổng Coliform; Tổng chất rắn lơ lửng (TSS); Kẽm
Trong ô trống đầu tiên của cột N (cột trống được chèn bên trái cột tham số), hãy viết từ "keep", nhấp vào ô, sau đó điền từ đó vào tất cả các ô khác hiển thị bằng cách nhấp đúp vào góc dưới bên phải khi bạn thấy dấu cộng màu đen mỏng.
Trong tab "Dữ liệu" trong Excel, nhấn "Xóa" để xem các hàng còn lại.
Sắp xếp cột N (cột có từ "keep") theo thứ tự từ A đến Z và bỏ chọn "keep" trong danh sách thả xuống để chỉ còn lại các hàng không có dữ liệu.
Xóa tất cả các hàng đang hiển thị.
Trong tab "Dữ liệu" trong Excel, nhấn "Xóa" để xem các hàng còn lại.
Xóa cột N (cột có từ "keep")
Nhấp chuột phải vào cột O ("RESULT_QUALIFIER") và nhấp vào "insert" để chèn một cột trống vào bên trái cột O.
Nhấp vào cột N (cột tham số), sau đó trong tab "Dữ liệu" trong Excel, nhấp vào "chuyển đổi văn bản thành cột".
Đảm bảo rằng tùy chọn "delimited" được chọn rồi nhấp vào "Next".
Trong hộp tiếp theo, hãy đảm bảo chỉ chọn "comma" (dấu phẩy) rồi nhấp vào "finish" (không phải "next"). Thao tác này sẽ đưa tất cả dữ liệu sau dấu phẩy (ví dụ: "dissolved", "total" hoặc "total recoverable") vào cột O và chỉ để lại tên tham số trong cột N.

G.
Đảm bảo tất cả các mẫu trong Sheet1 đều được định dạng "mg/L" chứ không phải "ug/L".
Trong Sheet1, sắp xếp cột R (Đơn vị) theo thứ tự từ A đến Z.
Trong menu thả xuống của cột R, bỏ chọn tất cả và chỉ nhấp vào ug/L (nếu không có ô nào, hãy bỏ qua phần còn lại của bước này).
Trong ô trống đầu tiên bên phải cột Giới hạn Báo cáo (là Cột T), hãy viết công thức sau: =[ô đầu tiên trong cột Q (Kết quả)]/1000.
Khi con trỏ ở góc dưới bên phải của ô nơi bạn đã viết công thức đó chuyển thành dấu cộng màu đen mảnh, hãy nhấp và kéo ba cột sang phải (tức là sẽ có bốn ô trong hàng đó có chữ viết bên trong).
Sau đó, với cả bốn ô này được tô sáng, hãy nhấp vào dấu cộng màu đen mảnh ở góc dưới bên phải của ô cho đến hết bên phải để điền vào bốn cột này cho các ô còn lại.
Không nhấp, hãy nhấn CTRL+C để sao chép tất cả các ô mới được điền này, sau đó nhấp chuột phải vào ô đầu tiên hiển thị trong cột Q (ô được viết trong (công thức ở trên) và trong mục "tùy chọn dán", hãy nhấn vào biểu tượng có chữ "123" nhỏ ở góc, biểu tượng này sẽ chỉ dán câu trả lời thay vì công thức.
Sau đó, trong ô đầu tiên hiển thị ở cột R (đơn vị), hãy nhập "mg/L" và điền vào các hàng còn lại bằng dấu cộng màu đen mỏng ở góc dưới bên phải của ô đó.
Xóa các cột U-X (các cột bổ sung mà bạn đã tạo)
Trong tab "Dữ liệu" trong Excel, hãy nhấn "Xóa" để quay lại tất cả dữ liệu.

H.
Thêm thông tin cơ sở từ Sheet2 vào Sheet1
Trong Sheet2, xóa Cột C sao cho cột ID ứng dụng nằm ngay bên trái cột tên cơ sở.
Sau khi thực hiện thao tác này, các cột sẽ trông như sau: A – WDID; B – ID ứng dụng; C – Tên cơ sở; D – Tên người vận hành; E – Địa chỉ; F – Thành phố; G – Tiểu bang; H – Mã bưu chính; I – SIC chính; J – SIC phụ; K – SIC thứ ba.
Trong Sheet1, chèn 6 cột vào bên trái cột C (Năm báo cáo).

Trong ô C2, hãy nhập công thức sau và nhấn enter: =VLOOKUP($B2,Sheet2!$B:$Z,COLUMN(B:B),FALSE)
Khi con trỏ ở góc dưới bên phải của ô nơi bạn đã nhập công thức chuyển thành dấu cộng màu đen mảnh, hãy nhấp và kéo nó để điền vào tất cả các cột trống bên phải (tức là sẽ có 6 ô trong hàng đó có chữ viết).
Sau đó, với tất cả 6 ô này được tô sáng, hãy nhấp vào dấu cộng màu đen mảnh ở góc dưới bên phải của ô cho đến hết bên phải để điền vào 6 cột này cho các hàng còn lại.
Không nhấp, hãy nhấn CTRL+C để sao chép tất cả các ô mới được điền, sau đó nhấp chuột phải vào ô C2 (ô mà bạn đã nhập công thức ở trên ban đầu) và trong mục "tùy chọn dán", hãy nhấp vào biểu tượng có chữ "123" nhỏ ở góc, biểu tượng này sẽ chỉ dán kết quả thay vì công thức.

I.
Thêm Mã SIC từ Sheet2 vào Sheet1
Trong Sheet2, xóa các cột C-H sao cho cột ID ứng dụng nằm ngay bên trái cột mã SIC chính.
Sau khi thực hiện thao tác này, các cột sẽ trông như sau: A – WDID; B – App ID; C – SIC chính; D – SIC phụ; E – SIC bậc ba
Trong Sheet1, tại hàng tiêu đề của ba cột ngay bên phải cột vừa điền cuối cùng (có thể là các cột AA-AC), hãy viết lần lượt 1, 2 và 3.
Nhấp vào Hàng 1 (hàng tiêu đề), chuyển đến tab "Dữ liệu" trong Excel và nhấp đúp vào nút "Bộ lọc". Thao tác này sẽ tắt và bật lại các bộ lọc, bao gồm cả 3 cột mới.
Trong ô AA2, hãy nhập công thức sau và nhấn enter: =VLOOKUP($B2,Sheet2!$B:$Z,COLUMN(B:B),FALSE)
Khi con trỏ ở góc dưới bên phải của ô nơi bạn đã viết công thức đó chuyển thành dấu cộng màu đen mảnh, hãy nhấp và kéo nó để điền vào tất cả các cột trống bên phải (tức là sẽ có 3 ô trong hàng đó có chữ viết).
Sau đó, với cả 3 ô này được tô sáng, hãy nhấp vào dấu cộng màu đen mảnh ở góc dưới bên phải của ô cho đến hết bên phải để điền vào 3 cột này cho phần còn lại. hàng
Không cần nhấp, hãy nhấn CTRL+C để sao chép tất cả các ô vừa điền, sau đó nhấp chuột phải vào ô AA2 (ô mà bạn đã viết công thức trên ban đầu) và trong mục "tùy chọn dán", hãy nhấp vào biểu tượng có chữ "123" nhỏ ở góc, biểu tượng này sẽ chỉ dán câu trả lời thay vì công thức.
Trong danh sách thả xuống của cột AC (được gắn nhãn là "3" cho mã SIC bậc ba), hãy đảm bảo chỉ chọn ô "0"
Bôi đen tất cả các ô trong cột đó, nhấp chuột phải và nhấp vào "xóa nội dung".
Trong tab "Dữ liệu" trong Excel, hãy nhấn "Xóa" để quay lại tất cả dữ liệu.
Trong danh sách thả xuống của cột AB (được gắn nhãn là "2" cho mã SIC bậc hai), hãy đảm bảo chỉ chọn ô "0"
Bôi đen tất cả các ô trong cột đó, nhấp chuột phải và nhấp vào "xóa nội dung".
Trong tab "Dữ liệu" trong Excel, hãy nhấn "Xóa" để quay lại tất cả dữ liệu.

J.
Kết hợp dữ liệu mới từ Sheet1 vào Data tracker hiện có
Dữ liệu mới giờ đã sẵn sàng để dán vào Data tracker chính, nhưng trước tiên bạn cần đảm bảo không còn bất kỳ công thức nào có thể làm hỏng dữ liệu.
Trong tab "Trang chủ" trong Excel, nhấp vào "Tìm & Chọn" và nhấp vào "Công thức". Nếu thông báo không có công thức nào, bạn có thể tiếp tục. Nếu tìm thấy công thức, chỉ cần nhấn CTRL+A để chọn tất cả, sau đó sao chép (CTRL+C) và dán (CTRL+V) các giá trị (có số "123" nhỏ ở góc) để xóa tất cả các công thức).

Trong Sheet chính có tên "Dữ liệu", hãy chuyển đến cột "Cũ/Mới" và nhấp vào ô ở hàng 2. Đảm bảo ô đó hiển thị "Cũ", sau đó dùng con trỏ chuột có dấu cộng màu đen mỏng, nhấp đúp để điền vào các hàng còn lại.

Bây giờ, quay lại Sheet1, sao chép (CTRL+C) tất cả các hàng (trừ hàng tiêu đề) và dán (CTRL+V) chúng vào hàng mở đầu tiên ở cuối trang Dữ liệu.
Bôi đen và sao chép (CTRL+C) các ô đã điền ở hàng cuối cùng của dữ liệu cũ (hàng bạn vừa dán bên dưới), sau đó di chuyển xuống hàng cuối cùng của dữ liệu mới và nhấp vào ô ở cột ngoài cùng bên phải (cột mã SIC bậc ba) trong khi giữ phím SHIFT để bôi đen tất cả các ô mới. Nhấp chuột phải và trong mục "tùy chọn dán", nhấn vào biểu tượng có hình cọ vẽ nhỏ và dấu phần trăm, biểu tượng này sẽ chỉ dán định dạng.
Sau đó, trong cột "Cũ/Mới", hãy viết "mới" vào hàng đầu tiên của dữ liệu mới và dùng con trỏ có dấu cộng màu đen mỏng, nhấp đúp để điền vào các hàng còn lại.
Bạn có thể cần định dạng lại Đường viền trên các ô sau khi tải dữ liệu mới lên để đảm bảo định dạng phù hợp với các mục dữ liệu cũ hơn và trông đẹp mắt hơn.
Để thực hiện việc này, hãy nhấp vào Cột A, và trong khi giữ phím SHIFT, hãy nhấp vào Cột AD (thao tác này sẽ làm nổi bật tất cả các ô đã điền trong trang tính). Sau đó, ở đầu trang tính, hãy nhấp vào tab "Trang chủ" và đi đến hộp Ô gần bên phải, nhấp vào menu thả xuống Định dạng, sau đó nhấp vào tùy chọn "Định dạng Ô" ở cuối.

Trong hộp bật lên, hãy nhấp vào tab Đường viền và bạn sẽ thấy một biểu đồ ở phía bên phải hiển thị bốn ô mẫu có chữ "Văn bản" trong đó. Ở bên trái của biểu đồ đó, hãy nhấp vào các biểu tượng đường viền Trên, Giữa và Dưới. Bây giờ, biểu đồ sẽ hiển thị một đường liền ở trên cùng, giữa và dưới cùng của các ô mẫu. Sau đó, nhấp vào "Ok" để xác nhận những thay đổi này.

Cuối cùng, hãy bỏ chọn tất cả các cột và bây giờ hãy nhấp vào Cột AD để chỉ làm nổi bật cột đó. Đây sẽ là cột ngoài cùng bên phải có văn bản (được chỉ định là Cũ/Mới). Sau khi cột đó được tô sáng, hãy chuyển đến tab "Trang chủ" và tìm hộp Phông chữ ở bên trái, nhấp vào menu thả xuống biểu tượng Đường viền và chọn Đường viền phải.
Dữ liệu hiện đã sẵn sàng để xem lại, vì vậy hãy xóa Sheet1 và Sheet2 và đảm bảo lưu.

'''


# Phan II phai lam cac viec sau:
#####################################################################################################################################################################################################################################################################
# Bước                                                                    | Giải thích                                                                                                                                                                              |
# ----------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
# **1. Create 2 new sheets**                                              | Trong file Excel đang có (`SMARTS data tracker.xlsx`), tạo 2 sheet mới bằng nút `+`. Bạn có thể đặt tên là `Sheet1`, `Sheet2` hoặc tên có nghĩa hơn (ví dụ: `NewData`, `FacilityInfo`). |
# **2. Get Sheet2 into the proper format**                                | Chuẩn hóa dữ liệu trong `Sheet2` để phù hợp với định dạng theo dõi hiện tại. Có thể bao gồm: đổi tên cột, định dạng ngày, xử lý trống...                                                |
# **3. Get Sheet1 into the proper format**                                | Làm tương tự với `Sheet1` — chuẩn hóa dữ liệu mẫu, có thể gồm tên cột, đơn vị, định dạng mã cơ sở, ngày lấy mẫu...                                                                      |
# **4. Filter Sheet1 for only new sample data**                           | Lọc `Sheet1` để chỉ giữ lại dữ liệu mới (chưa có trong tracker). Có thể dùng cột "Sample Date" hoặc "Entry Date" để xác định mới/cũ.                                                    |
# **5. Check if facilities in Sheet1 are active**                         | Kiểm tra xem các cơ sở trong `Sheet1` còn hoạt động hay không (so với danh sách cơ sở đang hoạt động). Có thể dựa vào cột "Status" hoặc tra cứu chéo từ `Sheet2`.                       |
# **6. Choose the parameters to track in Sheet1**                         | Chọn những thông số môi trường cần theo dõi (ví dụ: pH, TSS, Oil & Grease...), không cần giữ tất cả.                                                                                    |
# **7. Make sure all the samples in Sheet1 are in “mg/L” and not “ug/L”** | Chuyển đổi đơn vị đo: nếu có dòng nào đang ở "µg/L" (microgram), chuyển về "mg/L" (milligram) cho đồng nhất. Thường chia giá trị cho 1,000.                                             |
# **8. Add facility information from Sheet2 into Sheet1**                 | Dùng `Sheet2` để bổ sung thông tin cơ sở (tên, địa chỉ, v.v.) vào `Sheet1`. Có thể dùng `VLOOKUP` hoặc `merge` theo `Facility ID`.                                                      |
# **9. Add in SIC Codes from Sheet2 into Sheet1**                         | Thêm mã ngành (SIC code) từ `Sheet2` vào `Sheet1`, cũng theo `Facility ID`.                                                                                                             |
# **10. Combine new data from Sheet1 into existing Data tracker**         | Gộp (append) dữ liệu đã xử lý trong `Sheet1` vào sheet `Data` gốc trong tracker. Đảm bảo không thêm trùng dòng đã có trước đó.                                                          |
#####################################################################################################################################################################################################################################################################

def Ht_Data_tquat(outputIo):
    st.write('Ht_Data_tquat')
    wb = load_workbook(outputIo)
    ws = wb.active
    # xu li wb, ws o day
    # roi save ra file excel de xem
    tepsave = "Data_0.xlsx"
    wb.save(tepsave)
    os.startfile(tepsave)
    return 

def Ht_Data_sxep(outputIo):
    st.write('Ht_Data_sxep')
    wb = load_workbook(outputIo)
    ws = wb.active
    # xu li wb, ws o day
    # roi save ra file excel de xem
    tepsave = "Data_1.xlsx"
    wb.save(tepsave)
    os.startfile(tepsave)
    return 

def Ht_Data_new(outputIo):
    st.write('Ht_Data_new')
    wb = load_workbook(outputIo)
    ws = wb.active
    # xu li wb, ws o day
    # roi save ra file excel de xem
    tepsave = "Data_2.xlsx"
    wb.save(tepsave)
    os.startfile(tepsave)
    return 

def Ht_Data_old(outputIo):
    st.write('Ht_Data_old')
    wb = load_workbook(outputIo)
    ws = wb.active
    # xu li wb, ws o day
    # roi save ra file excel de xem
    tepsave = "Data_3.xlsx"
    wb.save(tepsave)
    os.startfile(tepsave)
    return 

def Ht_Data_max(outputIo):
    st.write('Ht_Data_max')
    wb = load_workbook(outputIo)
    ws = wb.active
    # xu li wb, ws o day
    # roi save ra file excel de xem
    tepsave = "Data_0.xlsx"
    wb.save(tepsave)
    os.startfile(tepsave)
    return 




# Phan tich du lieu---------------------------------------
st.subheader('✅ III. Analyze the new data', divider=True)
uploaded_file = st.file_uploader("Tải lên file: Data_Tracker_New.xlsx", type=["xlsx"])

if uploaded_file:
    # Doc file da tai len de ghi du lieu o sheet Data vao df 
    df = pd.read_excel(uploaded_file, sheet_name="Data")

    # dung df ghi tạm ra file Excel dat ten la output để xử lý bằng openpyxl
    output = BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)

    # lap menu cac ham xu li tep output 
    op_listCaiMuonXem = {
        "0). Xem tổng quát tệp  Data_Tracker": Ht_Data_tquat, 
        "1). Sắp xếp theo 3 cột": Ht_Data_sxep,
        "2). Cột OLD/NEW có giá trị new": Ht_Data_new,
        "3). Cột OLD/NEW có giá trị old": Ht_Data_old,
        "4). So sánh giá trị max giữa các cơ sở": Ht_Data_max 
    }
    # menu chon ham/viec
    viec_chon = st.selectbox(
        "Chọn hàm xử lí Data với kiểu hiển thị", 
        (op_listCaiMuonXem.keys()),
        index=None,
        placeholder="Chon hien thi...",
    )
    # chay ham da chon
    if viec_chon:
        # chay ham tuong ung voi key chon_with_viec, ham nay co ten la gia tri cua key do, 
        # them () de chay ham, tham so la file excel da tai len
        op_listCaiMuonXem[viec_chon](output)   # 👉 Gọi hàm tuong ung



bien='''

def Ht_CaiMuonXem_0():
    
    #B1: tai len file Data_Tracker_New
    #uploaded_tracker = "Data_Tracker_New.xlsx"
    #df = pd.read_excel("Data_Tracker_New.xlsx", sheet_name='Data', dtype=str)

    uploaded_file = st.file_uploader('Upload Data_Tracker_New',type=['xlsx'])
    #B2: xu li file
    if uploaded_file is not None and "Data_Tracker_New" in uploaded_file.name :
        # 1.Đọc file Excel thành DataFrame
        df = pd.read_excel(uploaded_file, sheet_name='Data')
        # 2. Sắp xếp dữ liệu theo nhiều cấp độ (multi-level sort):
        df_sorted = df.sort_values(
            by=["OLD/NEW", "PARAMETER", "RESULT"],
            ascending=[True, True, False]
        )
        #Dua vao xlsx de xem kq sx
        tepxlsx = "Data_Tracker_3-1.xlsx"
        df_sorted.to_excel(tepxlsx, sheet_name='Datanew', index=False)
        os.startfile(tepxlsx)

    return    

    return "Ht_CaiMuonXem_0"

def Ht_CaiMuonXem_1():
    return "Ht_CaiMuonXem_1"

#----------------------



listCaiMuonXem = {
    "Cột OLD/NEW có giá trị new": CaiMuonXem0,
    "Cột OLD/NEW có giá trị old": CaiMuonXem1
}

chon_with_viec = st.multiselect("Chon cai ban muon xem", listCaiMuonXem.keys())
# chon_with_viec duoc tra ve la 1 key cua listCaiMuonXem
if chon_with_viec:
    # chay ham tuong ung voi key chon_with_viec, ham nay co ten la gia tri cua key do, them () de chay ham
    listCaiMuonXem[chon_with_viec]()   # 👉 Gọi hàm tuong ung




# Trong tab "Dữ liệu" trong Excel, hãy tô sáng toàn bộ trang tính và nhấn "Sắp xếp".
# Trong hộp thoại hiện ra, bạn sẽ muốn sắp xếp theo nhiều cấp độ như sau:
# Sắp xếp theo "OLD/NEW" từ A đến Z
# Sau đó theo "Tham số" từ A đến Z
# Sau đó theo "Kết quả" từ lớn nhất đến nhỏ nhất
# Sau khi nhập ba hướng này, hãy nhấp vào "Ok" để xác nhận các thay đổi.

Trong danh sách thả xuống cột "Cũ/Mới", chỉ chọn "Mới" để xem kết quả mới.
Trước khi bắt đầu tô sáng các ô, hãy chuyển đến danh sách thả xuống của cột C (tên cơ sở) và ghi lại bất kỳ cơ sở nào bạn muốn xem xét bất kể mẫu mới có sạch hay không (ví dụ: các cơ sở bạn đang nhắm mục tiêu hoặc đang kiện tụng, hoặc đang trong chương trình tuân thủ của bạn).
Xác định các điểm vượt quá
Trước tiên, bạn phải tìm ra giới hạn xả thải áp dụng cho các cơ sở trong khu vực của mình để biết ngưỡng nào cần làm nổi bật các điểm vượt quá trong bảng Dữ liệu.
IGP có các Mức Hành động Số (NAL) áp dụng cho tất cả các cơ sở, tính theo mức trung bình hàng năm hoặc mức tối đa tức thời.
NAL trung bình hàng năm: Nhôm – 0,75 mg/L; Amoniac – 2,14 mg/L; Asen – 0,15 mg/L; BOD – 30 mg/L; Cadimi – 0,0053 mg/L; COD – 120 mg/L; Đồng – 0,0332 mg/L; Xyanua – 0,022 mg/L; Sắt – 1,0 mg/L; Chì – 0,262 mg/L; Magiê – 0,064 mg/L; Thủy ngân – 0,0014 mg/L; Niken – 1,02 mg/L; N+N – 0,68 mg/L; Dầu và Khí – 15 mg/L; Phốt pho – 2,0 mg/L; Selen – 0,005 mg/L; Bạc – 0,0183 mg/L; TSS – 100 mg/L; Kẽm – 0,26 mg/L
Nồng độ tối đa tức thời (NAL): Dầu và Nước – 25 mg/L; pH – nhỏ hơn 6,0 hoặc lớn hơn 9,0; TSS – 400 mg/L
Sau đó, bạn sẽ cần tra cứu các Mức Hành động Số (TNAL) và/hoặc Giới hạn Nước thải Số (NEL) liên quan đến TMDL cụ thể áp dụng trong khu vực của bạn.
NAL thường được tính theo giá trị trung bình hàng năm hoặc giá trị tối đa tức thời.
NEL thường được tính theo giá trị tối đa tức thời, với vi phạm được định nghĩa là hai hoặc nhiều lần vượt quá tại cùng một điểm xả thải trong cùng một năm báo cáo.
Sau đó, dựa trên NAL/NEL/TNAL, v.v., hãy xem xét và đánh dấu các mẫu vượt quá giới hạn tương ứng, đồng thời ghi lại tên của bất kỳ cơ sở nào bạn muốn xem xét thêm trong quá trình thực hiện.
Khi đánh dấu các mẫu vượt quá giới hạn, hãy chọn tất cả các ô trong một hàng, nhưng không chọn toàn bộ hàng. Việc đánh dấu toàn bộ hàng sẽ làm cho toàn bộ hàng (kể cả các ô chưa điền ở bên phải cột cuối cùng có văn bản, tức là Cột AD) được đánh dấu, và điều này sẽ trông kỳ lạ nếu bạn lọc hoặc sắp xếp lại các ô.
Hãy đảm bảo viết lời giải thích cho tài liệu tham khảo của riêng bạn trong trang "Giải thích" để bạn có thể nhớ lại cách bạn đã làm (ví dụ: chúng tôi đánh dấu tất cả các cơ sở dựa trên NEL của Sông LA để đơn giản hóa, mặc dù NEL không áp dụng cho mọi cơ sở; chúng tôi sử dụng NEL amoniac thấp nhất trong số nhiều NEL để đánh dấu, v.v.)

Ngưỡng của LAW để đánh dấu các trường hợp vượt quá TNAL/NEL tức thời như sau: 
Amoniac – 4,7 mg/L; 
Cadimi – 0,0031 mg/L; 
Đồng – 0,06749 mg/L; 
E. coli – 400/100 mL; 
Enterococci MPN – 104/100 mL; 
Coliform phân – 400/100 mL; 
Chì – 0,094 mg/L; 
Nitrat – 1,0 mg/L; 
Nitrit – 1,0 mg/L; 
N+N – 1,0 mg/L; 
Tổng Coliform – 10000/100 mL; 
Kẽm – 0,159 mg/L
Sau khi đã đánh dấu tất cả dữ liệu mới, trong tab "Dữ liệu" của Excel, hãy nhấn "Xóa" để quay lại tất cả dữ liệu.

Xem xét kỹ hơn một cơ sở cụ thể
Bây giờ bạn đã có danh sách các cơ sở cần xem xét, đây là cách sắp xếp Excel để dễ dàng xem xét từng cơ sở.

Trong tab "Dữ liệu" của Excel, hãy nhấn "Sắp xếp".

Trong hộp thoại hiện ra, bạn sẽ muốn sắp xếp theo nhiều cấp độ như sau:
Sắp xếp theo "WDID" từ A đến Z
Sau đó theo "Năm báo cáo" từ nhỏ đến lớn
Sau đó theo "Tham số" từ A đến Z
Sau đó theo "Kết quả" từ lớn đến nhỏ

Giờ đây, bạn có thể sắp xếp theo cơ sở cụ thể đó bằng cách sử dụng WDID, ID ứng dụng hoặc Tên cơ sở của họ
Kiểm tra xem cơ sở nào nằm trong báo cáo thường niên về việc lấy mẫu tất cả các QSE
Tải xuống dữ liệu báo cáo thường niên từ SMARTS
Vào SMARTS và nhấp vào "Menu Người dùng Công khai", sau đó nhấp vào "Tải xuống Dữ liệu NOI Theo Hội đồng Khu vực"
Chọn khu vực của bạn từ menu thả xuống, sau đó nhấp vào "Báo cáo Thường niên Công nghiệp". Dữ liệu sẽ được tải xuống dưới dạng tệp .txt có tên là "tệp".
Tạo một trang tính mới trong trình theo dõi SMARTS của bạn, bây giờ có thể được gắn nhãn là Sheet3 (nếu chưa được gắn nhãn là Sheet3, bạn nên đổi tên thành Sheet3 cho mục đích của hướng dẫn này).
Sao chép (CTRL+C) và dán (CTRL+V) toàn bộ tệp văn bản "Báo cáo thường niên ngành" vào ô đầu tiên trong Sheet3 (A1).
Chuyển Sheet3 sang định dạng phù hợp với trình theo dõi của bạn.
Để sắp xếp lại hai cột đầu tiên, hãy cắt (CTRL+X) Cột B (WDID) và nhấp vào Cột A (ID ứng dụng), sau đó nhấp chuột phải và chọn "Cắt ô đã sao chép".
Xóa Cột L (Câu trả lời cho Câu hỏi 4) đến Cột AF (Câu trả lời cho Câu hỏi TMDL). Sau đó, xóa Cột E (Khu vực) đến Cột I (Giải thích cho Câu hỏi 2).
Sau khi thực hiện thao tác này, các cột sẽ trông như sau: A – WDID; B – ID ứng dụng; C – ID báo cáo; D – Năm báo cáo; E – Câu trả lời cho Câu hỏi 3; F – Giải thích cho Câu hỏi 3.
Tô sáng
'''
#-------------------------------------------------------


# Do thi hoa du lieu
st.subheader('✅ IV. Visualize the data', divider=True)
ThucThiPhan_4()
