#!/usr/bin/env python3
"""
etnet Radio — 雙主持對話 Podcast Pipeline v2
=============================================
流程：etnet RSS → GPT-4o 生成對話稿 → 分拆句子
      → cantonese.ai 逐句合成 → ffmpeg 拼接 → 串流

pip install openai feedparser requests schedule python-dotenv pydub
"""

import os, json, time, requests, feedparser, schedule, subprocess, re
from datetime import datetime
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

OPENAI_KEY     = os.getenv("OPENAI_API_KEY")
CANTONESE_KEY  = os.getenv("CANTONESE_AI_API_KEY")
STREAM_URL     = os.getenv("STREAM_URL", "")
ETNET_RSS      = "https://www.etnet.com.hk/www/tc/news/rss.php?section=editor"
OUTPUT_DIR     = Path("./audio_segments")
FINAL_DIR      = Path("./audio_final")
OUTPUT_DIR.mkdir(exist_ok=True)
FINAL_DIR.mkdir(exist_ok=True)

client = OpenAI(api_key=OPENAI_KEY)

# ── 主持人聲音設定 ────────────────────────────────────────
VOICES = {
    "mina":    {"voice_id": "mina_voice",    "speed": 1.05, "pitch":  2, "emoji": "👩‍💼"},
    "zicheng": {"voice_id": "zicheng_voice", "speed": 0.95, "pitch": -3, "emoji": "🧠"},
    "haifeng": {"voice_id": "haifeng_voice", "speed": 1.10, "pitch":  1, "emoji": "😎"},
    "ray":     {"voice_id": "ray_voice",     "speed": 0.88, "pitch":  0, "emoji": "📚"},
    "vee":     {"voice_id": "vee_voice",     "speed": 0.95, "pitch":  2, "emoji": "🎤"},
    "lianwu":  {"voice_id": "lianwu_voice",  "speed": 0.80, "pitch": -2, "emoji": "🌙"},
}

# ── 節目對話配置 ──────────────────────────────────────────
PROGRAMMES = {
    "morning_call": {
        "title": "醒晨財經 Morning Call",
        "hosts": ["mina"],          # 獨播
        "hours": (7, 9),
        "style": "solo",
        "duration_hint": "90秒",
    },
    "trading_floor": {
        "title": "實戰交易廳 Trading Floor",
        "hosts": ["zicheng", "mina"],
        "hours": (9, 12),
        "style": "duo",
        "duration_hint": "3-4分鐘",
        "dynamic": "子誠主導分析，Mina補充快訊，互相有問有答",
    },
    "midday_rescue": {
        "title": "午市急救室 Mid-day Rescue",
        "hosts": ["haifeng", "ray"],
        "hours": (12, 13),
        "style": "duo",
        "duration_hint": "2分鐘",
        "dynamic": "海峰鬼馬出題，Ray認真解釋，形成搞笑反差",
    },
    "second_half": {
        "title": "下半場博弈 Second Half",
        "hosts": ["zicheng", "mina"],
        "hours": (13, 16.16),
        "style": "duo",
        "duration_hint": "3分鐘",
        "dynamic": "子誠部署策略，Mina即市快訊補充，節奏明快",
    },
    "closing_bell": {
        "title": "收市華爾街 Closing Bell",
        "hosts": ["zicheng", "haifeng"],
        "hours": (16.16, 18),
        "style": "duo",
        "duration_hint": "3分鐘",
        "dynamic": "子誠嚴肅覆盤，海峰輕鬆點評，一莊一諧",
    },
    "wealth_academy": {
        "title": "財富學堂 Wealth Academy",
        "hosts": ["ray", "vee"],
        "hours": (18, 20),
        "style": "duo",
        "duration_hint": "3分鐘",
        "dynamic": "Vee提問，Ray解釋，像訪問一樣自然",
    },
    "investor_lounge": {
        "title": "投資者會客室 Investor Lounge",
        "hosts": ["vee", "zicheng"],
        "hours": (20, 22),
        "style": "duo",
        "duration_hint": "4分鐘",
        "dynamic": "Vee訪問，子誠作嘉賓分享見解，輕鬆深度兼備",
    },
    "us_market": {
        "title": "美股連線 US Market Live",
        "hosts": ["mina"],
        "hours": (22, 23.5),
        "style": "solo",
        "duration_hint": "90秒",
    },
    "midnight_harbour": {
        "title": "心靈避風塘 Midnight Harbour",
        "hosts": ["lianwu"],
        "hours": (23.5, 7),
        "style": "music",
        "duration_hint": "30秒串場",
    },
}

# ── PROMPT 模板 ───────────────────────────────────────────
HOST_PERSONAS = {
    "mina":    "Mina，女，財經新聞主播，清晰快報，語氣專業親切",
    "zicheng": "子誠，男，資深財經分析師，深沉有分量，善用比喻拆局",
    "haifeng": "海峰，男，鬼馬快嘴，潮語幽默，但唔離地，偶爾自嘲",
    "ray":     "Ray，男，財經教育主持，慢速清晰，用簡單例子解釋複雜概念",
    "vee":     "Vee，女，訪談型主持，親切溫和，擅長引導嘉賓傾訴",
    "lianwu":  "聯武，男，深夜療癒主持，極輕柔，睡前陪伴感",
}

def build_duo_prompt(prog, news_text):
    h1, h2 = prog["hosts"]
    p1, p2 = HOST_PERSONAS[h1], HOST_PERSONAS[h2]
    dynamic = prog.get("dynamic", "自然對話")
    duration = prog.get("duration_hint", "2-3分鐘")

    return f"""你係一個廣播劇本作家，請為 etnet Radio 嘅《{prog["title"]}》節目寫一段雙主持對話播報稿。

【主持人】
- {p1}
- {p2}

【對話動態】{dynamic}

【今日財經新聞】
{news_text}

【格式要求 — 必須嚴格遵守】
每行只能係以下格式（冒號後係對白）：
{h1.upper()}: 對白內容
{h2.upper()}: 對白內容

例子：
MINA: 各位聽眾好，我係Mina，歡迎收聽etnet Radio！
ZICHENG: 大家好，我係子誠，今日市況頗為波動...
MINA: 係呀子誠，恒指今日跌咗89點，但科技股就逆市升...

【內容要求】
1. 完全用廣東話，夾雜適量英文財經術語
2. 對話要自然，有互動，唔係輪流獨白
3. 加入「嗯」「係呀」「但係...」「等等」等過渡語
4. 偶爾一方可以接住另一方未講完嘅句子
5. 節目長度約{duration}
6. 開頭要有節目開場白，結尾提及 etnet Radio
7. 最後一行必須係其中一位主持講 Station ID：
   「你而家收聽緊 etnet Radio，眼觀大市，耳聽玄機。」或
   「etnet Radio，陪你由開市到入睡。」

只輸出對話稿，唔好加任何說明或標題。"""

def build_solo_prompt(prog, news_text):
    host_id = prog["hosts"][0]
    persona = HOST_PERSONAS[host_id]
    duration = prog.get("duration_hint", "90秒")

    station_ids = [
        "你而家收聽緊 etnet Radio，眼觀大市，耳聽玄機。",
        "etnet Radio，陪你由開市到入睡。",
    ]
    import random
    sid = random.choice(station_ids)

    return f"""你係廣播稿作家，請為 etnet Radio 嘅《{prog["title"]}》節目寫一段獨播稿。

【主持人】{persona}

【今日財經新聞】
{news_text}

【格式要求】
每行格式：
{host_id.upper()}: 對白內容

【內容要求】
1. 完全用廣東話
2. 符合主持人風格
3. 長度約{duration}
4. 結尾加 Station ID：「{sid}」

只輸出對話稿，唔好加任何說明。"""

# ── 1. 抓新聞 ─────────────────────────────────────────────
def fetch_news(max_items=6):
    print(f"[{ts()}] 抓取 etnet 新聞...")
    try:
        feed = feedparser.parse(ETNET_RSS)
        items = []
        for e in feed.entries[:max_items]:
            items.append(f"• {e.get('title','')}：{e.get('summary','')[:150]}")
        return "\n".join(items)
    except Exception as ex:
        print(f"[{ts()}] RSS 失敗: {ex}")
        return "• 市場暫無重大消息"

# ── 2. 生成對話稿 ─────────────────────────────────────────
def generate_dialogue(prog, news_text):
    style = prog.get("style", "duo")
    if style == "music":
        # 深夜節目：生成簡短串場白
        return [(prog["hosts"][0], "夜深咗，各位投資者，今日辛苦晒。放鬆一下，聽住音樂，etnet Radio陪住你。")]

    prompt = build_duo_prompt(prog, news_text) if style == "duo" else build_solo_prompt(prog, news_text)

    print(f"[{ts()}] GPT-4o 生成對話稿...")
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1200,
            temperature=0.75,
        )
        raw = resp.choices[0].message.content.strip()
        return parse_dialogue(raw, prog["hosts"])
    except Exception as ex:
        print(f"[{ts()}] GPT 失敗: {ex}")
        return []

# ── 3. 解析對話稿 → [(speaker, text), ...] ───────────────
def parse_dialogue(raw_script, hosts):
    lines = []
    host_map = {h.upper(): h for h in hosts}
    # 支援 MINA: / mina: / Mina: 格式
    all_keys = {h.upper() for h in VOICES.keys()}

    for line in raw_script.split("\n"):
        line = line.strip()
        if not line:
            continue
        for key in all_keys:
            if line.upper().startswith(key + ":"):
                speaker = key.lower()
                text = line[len(key)+1:].strip()
                if text:
                    lines.append((speaker, text))
                break

    print(f"[{ts()}] 解析到 {len(lines)} 句對白")
    return lines

# ── 4. 逐句 TTS 合成 ─────────────────────────────────────
def synthesize_line(speaker, text, idx, session_id):
    voice = VOICES.get(speaker)
    if not voice:
        return None

    filename = OUTPUT_DIR / f"{session_id}_{idx:03d}_{speaker}.mp3"

    try:
        resp = requests.post(
            "https://api.cantonese.ai/v1/tts",
            headers={
                "Authorization": f"Bearer {CANTONESE_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "text": text,
                "voice_id": voice["voice_id"],
                "language": "cantonese",
                "speed": voice["speed"],
                "pitch": voice["pitch"],
                "output_format": "mp3",
            },
            timeout=30,
        )
        if resp.status_code == 200:
            filename.write_bytes(resp.content)
            print(f"  [{ts()}] {VOICES[speaker]['emoji']} {speaker}: {text[:30]}...")
            return str(filename)
        else:
            print(f"  [{ts()}] TTS 失敗 ({resp.status_code}): {speaker}")
            return None
    except Exception as ex:
        print(f"  [{ts()}] TTS 請求失敗: {ex}")
        return None

def synthesize_dialogue(dialogue, session_id):
    """逐句合成，保留對話順序"""
    print(f"[{ts()}] 開始合成 {len(dialogue)} 句對白...")
    audio_files = []
    for idx, (speaker, text) in enumerate(dialogue):
        path = synthesize_line(speaker, text, idx, session_id)
        if path:
            audio_files.append(path)
        time.sleep(0.3)  # 避免 rate limit
    return audio_files

# ── 5. ffmpeg 拼接 ────────────────────────────────────────
def merge_audio(audio_files, output_path, pause_ms=400):
    """
    用 ffmpeg 拼接所有音頻片段
    句子之間加入 pause_ms 毫秒靜音（模擬對話節奏）
    """
    if not audio_files:
        return None

    # 建立 concat list
    concat_file = OUTPUT_DIR / "concat_list.txt"
    silence_file = OUTPUT_DIR / "silence.mp3"

    # 生成靜音片段
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi",
        "-i", f"anullsrc=r=44100:cl=mono",
        "-t", str(pause_ms/1000),
        "-acodec", "libmp3lame", "-ab", "128k",
        str(silence_file)
    ], capture_output=True)

    # 建立 concat 清單（每句之間加靜音）
    with open(concat_file, "w") as f:
        for af in audio_files:
            f.write(f"file '{os.path.abspath(af)}'\n")
            f.write(f"file '{os.path.abspath(silence_file)}'\n")

    # 拼接
    result = subprocess.run([
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_file),
        "-acodec", "libmp3lame", "-ab", "128k",
        str(output_path)
    ], capture_output=True)

    if result.returncode == 0:
        print(f"[{ts()}] 音頻拼接完成: {output_path}")
        return str(output_path)
    else:
        print(f"[{ts()}] 拼接失敗: {result.stderr.decode()}")
        return None

# ── 6. 串流推送 ───────────────────────────────────────────
def stream_audio(audio_file):
    if not STREAM_URL or not audio_file:
        print(f"[{ts()}] 跳過串流（冇設定 STREAM_URL）")
        return
    print(f"[{ts()}] 推送串流...")
    subprocess.Popen([
        "ffmpeg", "-re", "-i", audio_file,
        "-acodec", "libmp3lame", "-ab", "128k",
        "-ar", "44100", "-f", "mp3", STREAM_URL
    ])

# ── 7. 判斷當前節目 ───────────────────────────────────────
def get_current_programme():
    now = datetime.now()
    cur = now.hour + now.minute / 60
    for key, prog in PROGRAMMES.items():
        s, e = prog["hours"]
        in_range = (cur >= s and cur < e) if e > s else (cur >= s or cur < e)
        if in_range:
            return key, prog
    return "midnight_harbour", PROGRAMMES["midnight_harbour"]

# ── 8. 主流程 ─────────────────────────────────────────────
def broadcast_cycle():
    prog_key, prog = get_current_programme()
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    print(f"\n{'='*55}")
    print(f"[{ts()}] 📻 《{prog['title']}》")
    hosts_str = " × ".join([f"{VOICES[h]['emoji']}{h}" for h in prog["hosts"]])
    print(f"[{ts()}] 主持：{hosts_str}")

    # 抓新聞
    news_text = fetch_news()

    # 生成對話稿
    dialogue = generate_dialogue(prog, news_text)
    if not dialogue:
        print(f"[{ts()}] 生成失敗，跳過")
        return

    # 打印對話預覽
    print(f"\n--- 對話預覽 ---")
    for speaker, text in dialogue[:4]:
        emoji = VOICES.get(speaker, {}).get("emoji", "🎙️")
        print(f"  {emoji} {speaker}: {text[:50]}...")
    if len(dialogue) > 4:
        print(f"  ... 共 {len(dialogue)} 句")
    print("---\n")

    # TTS 合成
    audio_files = synthesize_dialogue(dialogue, session_id)
    if not audio_files:
        print(f"[{ts()}] TTS 全部失敗")
        return

    # 拼接
    final_path = FINAL_DIR / f"{session_id}_{prog_key}.mp3"
    merged = merge_audio(audio_files, final_path)

    # 串流
    if merged:
        stream_audio(merged)

    # 清理舊段落音頻
    for f in audio_files:
        try: os.remove(f)
        except: pass

    print(f"[{ts()}] ✅ 廣播週期完成")

def ts():
    return datetime.now().strftime("%H:%M:%S")

# ── 9. 排程 ──────────────────────────────────────────────
if __name__ == "__main__":
    print(f"[{ts()}] 🎙️ etnet Radio Podcast Pipeline v2 啟動")
    print(f"[{ts()}] 雙主持對話模式 ON")

    broadcast_cycle()  # 立即跑一次

    schedule.every(5).minutes.do(broadcast_cycle)
    while True:
        schedule.run_pending()
        time.sleep(30)
