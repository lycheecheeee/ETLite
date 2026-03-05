import requests
import os
import time

API_KEY = "sk-o0sqn7wHhgsSqHoNW0j58q0f0vwcms9"  # ⚠️ 記得換

# ── 六個主持設定（用 pitch + speed 造唔同聲線效果）────────
HOSTS = {
    "mina":     {"name": "Mina（新聞主播）",   "speed": 1.05, "pitch":  3, "enhance": True},
    "zicheng":  {"name": "子誠（智者派）",      "speed": 0.92, "pitch": -4, "enhance": True},
    "haifeng":  {"name": "海峰（鬼馬派）",      "speed": 1.12, "pitch":  1, "enhance": True},
    "ray":      {"name": "Ray（教學型）",       "speed": 0.88, "pitch": -2, "enhance": True},
    "vee":      {"name": "Vee（訪談型）",       "speed": 0.96, "pitch":  4, "enhance": True},
    "lianwu":   {"name": "聯武（療癒派）",      "speed": 0.78, "pitch": -5, "enhance": True},
}

# ── 每個主持嘅試音句子 ────────────────────────────────────
HOST_LINES = {
    "mina":    "各位聽眾好，我係Mina，歡迎收聽etnet Radio。以下係今日最新財經快訊。",
    "zicheng": "大家好，我係子誠。今日恒指走勢頗為波動，背後有幾個值得大家留意嘅訊號。",
    "haifeng": "哇，午市到喇！我係海峰，嚟幫大家急救一下個portfolio先！今日科技股勁爆！",
    "ray":     "大家好，我係Ray。今日財富學堂，我哋嚟講一個概念：點解加息會令樓價下跌？",
    "vee":     "大家好，我係Vee，歡迎嚟到投資者會客室。今晚我哋有一位非常特別嘅嘉賓。",
    "lianwu":  "夜深咗，各位投資者，今日辛苦晒。放低今日嘅得失，好好休息，明天又係新嘅開始。",
}

# ── 對話示範（子誠 × Mina）────────────────────────────────
DIALOGUE = [
    ("zicheng", "大家好，我係子誠，歡迎收聽etnet Radio實戰交易廳。今日恒指跌咗八十九點，但我留意到一個有趣嘅現象。"),
    ("mina",    "子誠，你係咪話科技股逆市升嗰件事？"),
    ("zicheng", "係呀Mina，你都留意到。騰訊升咗兩個百分點，阿里升接近三個百分點，背後係美聯儲嗰個信號撐住。"),
    ("mina",    "對，鮑威爾昨晚表示通脹數據改善，下半年或具備減息條件，消息一出，科技股即時受惠。"),
    ("zicheng", "嗯，但我要提醒大家，減息係或具備條件，唔係確認，中間仲有好多變數。"),
    ("mina",    "咁子誠你點睇下半場走勢？"),
    ("zicheng", "我會分兩種情況睇。如果下周CPI數據繼續向好，恒指有望收復二萬一千五百點。"),
    ("mina",    "但如果數據差過預期，就要小心跌穿二萬一千點？"),
    ("zicheng", "你講咗我想講嘅。所以今日建議唔好追高，守住現有倉位，靜待數據先。"),
    ("mina",    "好實用嘅建議。你而家收聽緊etnet Radio，眼觀大市，耳聽玄機。"),
]

def synthesize(text, host_id, filename):
    h = HOSTS[host_id]
    print(f"  合成中：{h['name']} — {text[:25]}...")
    resp = requests.post(
        "https://cantonese.ai/api/tts",
        json={
            "api_key": "sk-o0sqn7wHhgsSqHoNW0j58q0f0vwcms9",
            "text": text,
            "language": "cantonese",
            "speed": h["speed"],
            "pitch": h["pitch"],
            "output_extension": "mp3",
            "should_enhance": h["enhance"],
        },
        timeout=30,
    )
    if resp.status_code == 200:
        with open(filename, "wb") as f:
            f.write(resp.content)
        print(f"  ✅ 儲存：{filename}")
        return True
    else:
        print(f"  ❌ 失敗 ({resp.status_code}): {resp.text[:80]}")
        return False

# ── 第一部分：六個主持試音 ────────────────────────────────
print("="*50)
print("第一部分：六個主持試音")
print("="*50)
os.makedirs("hosts", exist_ok=True)
for hid, line in HOST_LINES.items():
    synthesize(line, hid, f"hosts/{hid}_sample.mp3")
    time.sleep(0.5)

print()

# ── 第二部分：子誠 × Mina 對話 ───────────────────────────
print("="*50)
print("第二部分：對話版（子誠 × Mina）")
print("="*50)
os.makedirs("dialogue", exist_ok=True)
segment_files = []
for idx, (hid, text) in enumerate(DIALOGUE):
    fname = f"dialogue/{idx:02d}_{hid}.mp3"
    ok = synthesize(text, hid, fname)
    if ok:
        segment_files.append(fname)
    time.sleep(0.5)

# ── 第三部分：用 ffmpeg 拼接對話 ─────────────────────────
print()
print("="*50)
print("第三部分：拼接對話音頻")
print("="*50)

import subprocess, shutil

if shutil.which("ffmpeg"):
    # 寫 concat list
    with open("dialogue/concat.txt", "w") as f:
        for sf in segment_files:
            f.write(f"file '../{sf}'\n")
    result = subprocess.run([
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", "dialogue/concat.txt",
        "-acodec", "libmp3lame", "-ab", "128k",
        "etnet_radio_dialogue_demo.mp3"
    ], capture_output=True)
    if result.returncode == 0:
        print("✅ 對話拼接完成：etnet_radio_dialogue_demo.mp3")
        print("   打開呢個檔案，聽下完整對話！")
    else:
        print("⚠️  ffmpeg 拼接失敗，但個別片段已儲存喺 dialogue/ 資料夾")
        print("   你可以逐個聽 dialogue/ 入面嘅 mp3")
else:
    print("⚠️  未裝 ffmpeg，跳過拼接")
    print("   個別片段已儲存喺 dialogue/ 資料夾，逐個聽都得")
    print()
    print("   裝 ffmpeg 方法：")
    print("   1. 去 https://ffmpeg.org/download.html 下載")
    print("   2. 或者 PowerShell 打：winget install ffmpeg")

print()
print("完成！")
print("📁 hosts/        — 六個主持試音")
print("📁 dialogue/     — 逐句對話片段")
print("🎙️  etnet_radio_dialogue_demo.mp3 — 完整對話（如有ffmpeg）")
