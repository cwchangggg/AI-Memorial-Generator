# AI Memorial Video Generator 哀悼影片生成平台

An AI-powered web application for generating personalized memorial tribute videos from voice and text.  
一個透過 AI 技術，將聲音與文字轉換成個人化哀悼影片的網頁應用程式。

---
## How to use

- Fill in your tribute message

- Upload a voice file (.wav / .mp3)

- Click "Generate Video" and watch real-time progress and result

- 個人化追思文字

- 上傳聲音檔（.wav / .mp3）

- 點擊「生成影片」，並即時觀看進度與結果

---
## Installation 安裝方式

### 1. Clone the repository 複製專案
```bash
git clone https://github.com/cwchangggg/AI-Memorial-Generator
cd AI-Memorial-Generator
```

### 2. Set up environment 建立環境
```bash
conda create -n memorial_env python=3.10
conda activate memorial_env
pip install -r requirements.txt
```

### 3. Setup media folder 建立媒體資料夾
```bash
mkdir media
```
### 4. Run Django server 執行伺服器
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser   # optional
python manage.py runserver
```
Then open your browser and visit:
http://127.0.0.1:8000 

---
## Model Pipeline Instructions 模型流程與接入說明

### Modify `memorial/utils.py`: `run_pipeline_models()`  

```python
def run_pipeline_models(text: str, audio_path: str, video_path: str):
    """
    接收使用者輸入的文字與聲音，合成出一段影片。
    Generates a memorial video based on user-provided text and voice.
    """
	...
    yield video_path  # Return video 回傳影片路徑給前端
```

---
 
- Integrate your video generation logic inside run_pipeline_models().
- Use yield "message" in each generation stage to send live progress updates to the frontend.
- Finally, use yield video_path to allow the frontend to display the finished video.
- 請將你的影片生成模型或腳本整合進 run_pipeline_models()。
- 每一個生成階段可以使用 yield "訊息" 回傳給前端即時顯示進度。
- 結束時 yield video_path，這樣前端才能播放影片。

---
