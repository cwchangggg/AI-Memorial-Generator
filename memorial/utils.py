import time

def run_pipeline_models(text, audio_path, video_path):
    
    yield f"開始生成：{text}"
    time.sleep(1)
    yield "模擬：分析音訊..."
    time.sleep(1)
    yield "模擬：生成影片中..."
    time.sleep(2)
    yield video_path
    
