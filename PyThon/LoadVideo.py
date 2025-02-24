from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from tqdm import tqdm 
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import requests
from pydub import AudioSegment
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

# ===== Cấu hình Chrome Driver =====
options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# ===== Cấu hình đường dẫn FFMPEG =====
FFMPEG_PATH = os.path.join(os.getcwd(), "ffmpeg", "bin", "ffmpeg.exe")
FFPROBE_PATH = os.path.join(os.getcwd(), "ffmpeg", "bin", "ffprobe.exe")
AudioSegment.converter = FFMPEG_PATH
AudioSegment.ffprobe = FFPROBE_PATH

# ===== Đọc file link TikTok =====
file_path = os.path.join(os.getcwd(), "Link", "LinkTikTok.txt")
with open(file_path, "r", encoding="utf-8") as file:
    lines = file.readlines()

data = {}
current_name = None
for line in lines:
    line = line.strip()
    if not line:
        continue
    if not line.startswith("https"):
        current_name = line
        data[current_name] = []
    else:
        data[current_name].append(line)

# ===== Thư mục lưu video & MP3 =====
download_folder = os.path.join(os.getcwd(), "Downloaded_Videos")
os.makedirs(download_folder, exist_ok=True)
mp3_folder = os.path.join(os.getcwd(), "Converted_Audio")
os.makedirs(mp3_folder, exist_ok=True)

def download_tiktok_video(link, name, index):
    driver.get("https://snaptik.app/vn2")
    
    try:
        input_box = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "url")))
        input_box.clear()
        input_box.send_keys(link)
        input_box.send_keys(Keys.RETURN)

        # Chờ nút tải xuống xuất hiện
        download_button = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "download-file")))
        download_url = download_button.get_attribute("href")

        # Định dạng tên file
        file_name = f"{name} {index+1}.mp4"
        file_path = os.path.join(download_folder, file_name)

        # Gửi request tải file
        response = requests.get(download_url, stream=True)
        total_size = int(response.headers.get("content-length", 0))  # Lấy kích thước file

        if response.status_code == 200:
            with open(file_path, "wb") as file, tqdm(
                desc=f"📥 Đang tải {file_name}",
                total=total_size,
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
            ) as bar:
                for chunk in response.iter_content(chunk_size=1024):
                    file.write(chunk)
                    bar.update(len(chunk))  # Cập nhật tiến trình tải
            print(f"✅ Tải xong: {file_name}")
        else:
            print(f"❌ Lỗi khi tải {file_name}")

    except Exception as e:
        print(f"⚠️ Lỗi khi tải {link}: {e}")
        
def convert_video_to_mp3():
    print("🔄 Đang chuyển đổi video sang MP3...")
    for file_name in os.listdir(download_folder):
        if file_name.endswith(".mp4"):
            video_path = os.path.join(download_folder, file_name)
            mp3_path = os.path.join(mp3_folder, file_name.replace(".mp4", ".mp3"))
            try:
                audio = AudioSegment.from_file(video_path, format="mp4")
                audio.export(mp3_path, format="mp3")
                print(f"🎵 Đã chuyển: {file_name} -> {mp3_path}")
            except Exception as e:
                print(f"❌ Lỗi khi chuyển {file_name}: {e}")

def fix_audio():
    print("🔄 Đang xử lý âm thanh...")
    for file_name in os.listdir(mp3_folder):
        if file_name.endswith(".mp3"):
            audio_path = os.path.join(mp3_folder, file_name)
            try:
                audio = AudioSegment.from_file(audio_path, format="mp3")
                
                # Áp dụng fade in 3s, fade out 3s
                audio = audio.fade_in(3000).fade_out(3000)
                
                # Chuẩn hóa âm lượng
                change_dB = -10 - audio.dBFS  # Giữ mức -1 dBFS để tránh vỡ âm
                audio = audio.apply_gain(change_dB)
                
                # Xuất file đã fix
                audio.export(audio_path, format="mp3")
                print(f"✅ Đã xử lý: {file_name}")
            except Exception as e:
                print(f"❌ Lỗi khi xử lý {file_name}: {e}")

def main():
    while True:
        print("\n📌 CHỌN CHỨC NĂNG:")
        print("1 - Tải video TikTok")
        print("2 - Chuyển đổi video sang MP3")
        print("3 - Fix âm thanh (fade in/out + chuẩn hóa)")
        print("0 - Thoát")
        choice = input("Nhập lựa chọn (0/1/2/3): ")
        
        if choice == "1":
            #driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
            for name, links in data.items():
                for i, link in enumerate(links):
                    download_tiktok_video(link, name, i)
            driver.quit()
            print("✅ Hoàn tất tải video!")
        
        elif choice == "2":
            convert_video_to_mp3()
            print("✅ Hoàn tất chuyển đổi MP3!")
        
        elif choice == "3":
            fix_audio()
            print("✅ Hoàn tất xử lý âm thanh!")
        
        elif choice == "0":
            print("👋 Thoát chương trình.")
            break
        else:
            print("❌ Lựa chọn không hợp lệ!")

if __name__ == "__main__":
    main()