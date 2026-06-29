def run_pipeline_backend(audio_path: str, model_name: str):
    output_txt_path = "/home/haohao/BreezyVoice/txt/output.txt"
    output_audio = "/home/haohao/SyncTalk/demo/output_audio.wav"
    video_path = f"/home/haohao/SyncTalk/model/{model_name}/results/ngp_ep0019_audio.mp4"
    data = f"/home/haohao/SyncTalk/data/{model_name}"
    model = f"/home/haohao/SyncTalk/model/{model_name}"

    timings = []

    if not audio_path or not os.path.exists(audio_path):
        yield "找不到音訊檔案，請重新上傳"
        return

    # Step 1: 啟動 Ollama + RAG
    yield "開始生成回應文字"

    try:
        subprocess.check_output(["pgrep", "-f", "ollama serve"])
    except subprocess.CalledProcessError:
        subprocess.Popen(["ollama", "serve"])
        time.sleep(2)

    t0 = time.time()
    try:
        run_conda_script("rag", "python rag_ollama_cn_last.py", "/home/haohao/RAG")
    except subprocess.CalledProcessError as e:
        yield f"RAG 模型執行錯誤：{e}"
        return

    timeout = 20
    waited = 0
    while not os.path.exists(output_txt_path) and waited < timeout:
        time.sleep(0.5)
        waited += 0.5

    if not os.path.exists(output_txt_path):
        yield "RAG 模型未成功生成 output.txt"
        return

    t1 = time.time()
    timings.append(t1 - t0)
    yield "文字生成完成"

    with open(output_txt_path, "r", encoding="utf-8") as f:
        text = f.read().strip()

    # Step 2: 語音合成
    yield "語音合成中"

    t2 = time.time()
    breezy_cmd = f'''python /home/haohao/BreezyVoice/single_inference.py \
    --content_to_synthesize "{text}" \
    --speaker_prompt_audio_path "{audio_path}" \
    --output_path "{output_audio}"'''

    try:
        run_conda_script("breezyvoice", breezy_cmd)
    except subprocess.CalledProcessError as e:
        yield f"語音模型執行錯誤：{e}"
        return

    t3 = time.time()
    timings.append(t3 - t2)
    yield "語音合成完成"

    # Step 3: 臉部動畫
    yield "臉部動畫生成中"

    face_cmd = f'''python main.py "{data}" \
    --workspace "{model}" \
    -O --test --test_train \
    --asr_model ave \
    --portrait \
    --aud {output_audio}'''

    t4 = time.time()
    try:
        run_conda_script("synctalk", face_cmd, "/home/haohao/SyncTalk")
    except subprocess.CalledProcessError as e:
        yield f"臉部動畫執行錯誤：{e}"
        return

    t5 = time.time()
    timings.append(t5 - t4)
    yield "臉部動畫完成"

    yield f"完成|{video_path}"  # 前端可以用 | 分隔回應與影片路徑

    for path in [output_audio, output_txt_path]:
        try:
            os.remove(path)
        except:
            pass
