import subprocess
import os
import time

# === Conda 初始化 ===
CONDA_PATH = os.path.expanduser("~/anaconda3/etc/profile.d/conda.sh")

def run_conda_script(env_name, command, workdir=None):
    cd_cmd = f"cd {workdir}" if workdir else ""
    full_cmd = f'''
    source {CONDA_PATH}
    conda activate {env_name}
    {cd_cmd}
    {command}
    '''
    subprocess.run(["bash", "-c", full_cmd], check=True)

def run_conda_background(env_name, command, workdir=None):
    cd_cmd = f"cd {workdir}" if workdir else ""
    full_cmd = f'''
    source {CONDA_PATH}
    conda activate {env_name}
    {cd_cmd}
    {command} &
    '''
    return subprocess.Popen(["bash", "-c", full_cmd])

# 計時容器
timings = []

# === Step 1：RAG 模型（Ollama + rag_ollama_cn_last.py）===
print("啟動 Ollama + RAG 模型...")

# (1) 檢查 ollama 是否已啟動
try:
    subprocess.check_output(["pgrep", "-f", "ollama serve"])
    print("Ollama 已啟動，略過啟動")
except subprocess.CalledProcessError:
    print("尚未啟動 Ollama，啟動中...")
    ollama_proc = subprocess.Popen(["ollama", "serve"])
    time.sleep(2)  # 稍等伺服器啟動

# (2) 執行 rag_ollama_cn_last.py
t0 = time.time()
try:
    run_conda_script(
        env_name="rag",
        command="python rag_ollama_cn_last.py",
        workdir="/home/haohao/RAG"
    )
except subprocess.CalledProcessError as e:
    print(f"RAG 模型執行錯誤：{e}")
    exit(1)

# (3) 等待 output.txt 生成
output_txt_path = "/home/haohao/BreezyVoice/txt/output.txt"
print("等待 output.txt 生成...")
timeout = 20
waited = 0
while not os.path.exists(output_txt_path) and waited < timeout:
    time.sleep(0.5)
    waited += 0.5

if not os.path.exists(output_txt_path):
    print("❌ output.txt 未生成，終止流程。")
    exit(1)

t1 = time.time()
print("✅ output.txt 已生成")
timings.append(t1 - t0)

# === Step 2：語音模型 ===
with open(output_txt_path, "r", encoding="utf-8") as f:
    text = f.read().strip()

print("啟動聲音模型 breezyvoice")
speaker_audio = "/home/haohao/BreezyVoice/data/self_28s.wav"
output_audio = "/home/haohao/SyncTalk/demo/output_audio.wav"

t2 = time.time()
breezy_cmd = f'''python /home/haohao/BreezyVoice/single_inference.py \
--content_to_synthesize "{text}" \
--speaker_prompt_audio_path "{speaker_audio}" \
--output_path "{output_audio}"'''

run_conda_script(
    env_name="breezyvoice",
    command=breezy_cmd
)
t3 = time.time()
timings.append(t3 - t2)
print("語音合成完成，輸出檔案：", output_audio)

# === Step 3：臉部模型 ===
print("啟動臉部模型 synctalk")
audio_for_face = output_audio
synctalk_workdir = "/home/haohao/SyncTalk"

face_cmd = f'''python main.py data/self_video_GFP \
--workspace model/self_video_GFP \
-O --test --test_train \
--asr_model ave \
--portrait \
--aud {audio_for_face}'''

t4 = time.time()
run_conda_script(
    env_name="synctalk",
    command=face_cmd,
    workdir=synctalk_workdir
)
t5 = time.time()
timings.append(t5 - t4)
print("臉部動畫完成")

# === 輸出總計時結果 ===
print("每個階段耗時（秒）：", timings)
print("總時間（秒）：", sum(timings))

# === 清除中繼檔案 ===
try:
    os.remove("/home/haohao/SyncTalk/demo/output_audio.wav")
    print("已刪除音檔：/home/haohao/SyncTalk/demo/output_audio.wav")
except FileNotFoundError:
    print("找不到音檔（可能已被刪除）")

try:
    os.remove("/home/haohao/BreezyVoice/txt/output.txt")
    print("已刪除文字檔：/home/haohao/BreezyVoice/txt/output.txt")
except FileNotFoundError:
    print("找不到文字檔（可能已被刪除）")