import streamlit as st  # streamlit=1.47.1
import pandas as pd     # pandas=2.3.1
import os, time

from selenium import webdriver  # selenium=4.34.2
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

import shutil
from openpyxl import Workbook, load_workbook    # openpyxl=3.1.5
from io import BytesIO
import xlsxwriter   # xlsxwriter=3.2.5
import tempfile

#--------------------------------------------------------------

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

def ThucThiPhan_3():
    uploaded_file_data_tracker = st.file_uploader('Upload Data_Tracker_New',type=['xlsx'])
    return    

# ---- phuc vu cho ThucThiPhan_2()----
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
        type=['txt', 'xlsx'],  # Optional: specify allowed file types
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
            st.warning("Hãy đảm bảo đúng 1 file chứa 'industrial_ad_hoc', 1 file .txt còn lại, và 1 file .xlsx để đặt tên")
    else:
        st.info("Vui lòng upload đủ 3 file")
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
        st.write('Nếu không đạt, có thể đến trực tiếp trang sau để tải:')
        st.markdown("[Mở trang SMARTS](https://smarts.waterboards.ca.gov/smarts/SwPublicUserMenu.xhtml)", unsafe_allow_html=True)

#========================= MAIN =====================================================================
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


# Phan tich du lieu
st.subheader('✅ III. Analyze the new data', divider=True)
ThucThiPhan_3()
#-------------------------------------------------------
# 1. Sắp xếp dữ liệu theo nhiều cấp độ (multi-level sort):
#df_sorted = df.sort_values(
#    by=["Old/New", "Parameter", "Result"],
#    ascending=[True, True, False]
#)
# 2. Lọc dữ liệu có Old/New == 'New':
#df_new = df_sorted[df_sorted["Old/New"] == "New"]
# 3. Tô màu (highlight) exceedances thì không thể hiển thị trong DataFrame thông thường nhưng có thể dùng:
# pandas.ExcelWriter + openpyxl để ghi file Excel có màu.
# Hoặc đơn giản chỉ đánh dấu bằng cột mới "Exceed" = True/False
# 4. So sánh kết quả với ngưỡng NAL/NEL/TNAL:
# tao dic chua nguong
# nal_thresholds = {
#    "Ammonia": 4.7,
#    "Cadmium": 0.0031,
#    "Copper": 0.06749,
#    # v.v...
#}
# Rồi kiểm tra:
#def is_exceed(row):
#    param = row["Parameter"]
#    result = row["Result"]
#    return result > nal_thresholds.get(param, float('inf'))
# df_new["Exceed"] = df_new.apply(is_exceed, axis=1)
# 5. Ghi chú các facility cần theo dõi → bạn có thể lọc hoặc thêm cột "Flagged" dựa vào danh sách thủ công.


# Do thi hoa du lieu
st.subheader('✅ IV. Visualize the data', divider=True)
ThucThiPhan_4()

st.markdown("[Mở trang SMARTS](https://smarts.waterboards.ca.gov/smarts/SwPublicUserMenu.xhtml)", unsafe_allow_html=True)
