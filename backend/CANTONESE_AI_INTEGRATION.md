# Cantonese AI TTS 集成指南

## 🎙️ 概述

Net 仔系統已成功集成 **Cantonese AI TTS API**，提供高質素嘅粵語語音合成功能。

### API 信息

- **服務商**: Cantonese.ai
- **API URL**: `https://cantonese.ai/api/tts`
- **支持語言**: 粵語 (Cantonese)
- **音質**: 24kHz WAV 格式
- **響應時間**: ~2-3 秒/句

---

## ✅ 已完成集成

### 1. 核心服務模塊

**文件**: `app/services/cantonese_tts_service.py`

```python
from app.services.cantonese_tts_service import cantonese_tts

# 簡單使用
audio_path = await cantonese_tts.synthesize_speech(
    text="早晨！我係子程，歡迎收聽 Net 仔財經早新聞",
    output_filename="morning_news.wav"
)

# 自定義參數
audio_path = await cantonese_tts.synthesize_speech(
    text="恒指今日大升 500 點！",
    speed=1.2,      # 加快語速（興奮）
    pitch=10        # 提高音調
)

# 批量合成
segments = [
    {"text": "早晨！我係子程", "speed": 1.0},
    {"text": "今日恒指高開 256 點", "speed": 1.1},
    {"text": "騰訊業績強勁", "speed": 1.2}
]
results = await cantonese_tts.batch_synthesize(
    texts=segments,
    prefix="podcast_segment"
)
```

### 2. 配置管理

**文件**: `app/core/config.py`

```python
# 新增配置項
CANTONESE_AI_API_URL: str = "https://cantonese.ai/api/tts"
CANTONESE_AI_API_KEY: str = "sk-o0sqn7wHhgsSqHoNW0j58q0f0vwcms9"
CANTONESE_AI_VOICE_ID: str = "2725cf0f-efe2-4132-9e06-62ad84b2973d"
```

### 3. 播客生成器升級

**文件**: `app/services/podcast_generator.py`

播客生成器現在自動使用 Cantonese AI TTS（如果配置了 API Key）：

```python
class PodcastGenerator:
    def __init__(self):
        self.audio_processor = AudioProcessor()
        # 自動選擇 Cantonese AI 作為主要 TTS 服務
        self.tts_service = cantonese_tts if settings.CANTONESE_AI_API_KEY else tts_service
```

---

## 🔧 使用方法

### 方法 1: 直接使用 Cantonese TTS 服務

```python
from app.services.cantonese_tts_service import cantonese_tts

async def generate_audio():
    # 單句合成
    audio_path = await cantonese_tts.synthesize_speech(
        text="你今日食咗飯未？",
        output_filename="greeting.wav"
    )
    
    # 帶情感合成
    audio_path = await cantonese_tts.synthesize_speech(
        text="好消息！恒指突破兩萬點！",
        speed=1.3,   # 快速（興奮）
        pitch=15     # 高音調
    )
```

### 方法 2: 使用播客生成器（推薦）

```python
from app.services.podcast_generator import PodcastGenerator

generator = PodcastGenerator()

# 生成個人化播客
podcast = await generator.generate_daily_podcast(
    user_id="user_123",
    profile={
        "foundation": "intermediate",
        "mindset": "balanced",
        "timeframe": "medium"
    },
    podcast_type="morning"
)
```

### 方法 3: 運行示例腳本

```bash
cd backend
python examples/cantonese_tts_example.py
```

會生成多個示例音頻文件：
- `example_morning_news.wav` - 晨早新聞
- `example_market_surge.wav` - 市場急升（快語速）
- `example_caution.wav` - 謹慎提示（慢語速）
- `podcast_example_*.wav` - 完整播客分段
- `emotion_example_*.wav` - 不同情感變化

---

## 📊 API 參數詳解

### 請求參數

| 參數 | 類型 | 必填 | 說明 | 示例值 |
|------|------|------|------|--------|
| `api_key` | string | ✅ | API 認證密鑰 | `sk-o0sqn7...` |
| `text` | string | ✅ | 粵語文本內容 | `早晨！我係子程` |
| `voice_id` | string | ✅ | 語音 ID | `2725cf0f-...` |
| `frame_rate` | string | ❌ | 採樣率 | `"24000"` |
| `speed` | float | ❌ | 語速 (0.5-2.0) | `1.0` |
| `pitch` | int | ❌ | 音調 (-100 to 100) | `0` |
| `language` | string | ❌ | 語言 | `"cantonese"` |
| `output_extension` | string | ❌ | 輸出格式 | `"wav"` |
| `should_return_timestamp` | bool | ❌ | 返回時間戳 | `false` |

### 情感映射表

播客生成器會自動將情感映射到速度/音調：

| 情感 | Speed | Pitch | 使用場景 |
|------|-------|-------|----------|
| `cheerful` | 1.1 | +5 | 歡快、積極嘅內容 |
| `professional` | 1.0 | 0 | 專業、中性嘅分析 |
| `excited` | 1.3 | +10 | 激動人心嘅消息 |
| `friendly` | 1.0 | +5 | 友好、親切嘅對話 |
| `neutral` | 1.0 | 0 | 一般陳述 |

---

## 🧪 測試驗證

### 快速測試

```bash
cd backend
python test_cantonese_api.py
```

**預期結果：**
```
Testing Cantonese AI TTS API...
Text: 早晨！我係子程，歡迎收聽 Net 仔財經早新聞
Voice ID: 2725cf0f-efe2-4132-9e06-62ad84b2973d
Success! Audio saved to test_cantonese_output.wav
   File size: 50981 bytes
```

### 完整測試

```bash
python examples/cantonese_tts_example.py
```

會測試：
1. 單句合成
2. 批量合成（5 個分段）
3. 不同情感變化

---

## 📁 輸出文件

所有生成的音頻保存在：

```
backend/audio/generated/
├── example_morning_news.wav
├── example_market_surge.wav
├── example_caution.wav
├── podcast_example_000.wav
├── podcast_example_001.wav
├── ...
└── emotion_example_1.wav
```

---

## 🚀 生產環境部署

### 1. 環境變量配置

在 `.env` 文件中設置：

```env
# Cantonese AI TTS Configuration
CANTONESE_AI_API_URL=https://cantonese.ai/api/tts
CANTONESE_AI_API_KEY=sk-o0sqn7wHhgsSqHoNW0j58q0f0vwcms9
CANTONESE_AI_VOICE_ID=2725cf0f-efe2-4132-9e06-62ad84b2973d
```

### 2. Docker 部署

更新 `docker-compose.yml` 確保環境變量正確傳遞：

```yaml
services:
  backend:
    environment:
      - CANTONESE_AI_API_KEY=${CANTONESE_AI_API_KEY}
      - CANTONESE_AI_VOICE_ID=${CANTONESE_AI_VOICE_ID}
```

### 3. 錯誤處理與重試

建議添加重試機制：

```python
from tenacity import retry, stop_after_attempt, wait_exponential

class CantoneseTTSService:
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def synthesize_speech(self, text, **kwargs):
        # ... implementation
```

---

## 💡 最佳實踐

### 1. 文本預處理

```python
# 清理特殊字符
def preprocess_text(text: str) -> str:
    # 移除 emoji（TTS 可能不支持）
    text = re.sub(r'[\U0001F600-\U0001F64F]', '', text)
    # 標準化標點
    text = text.replace('...', '。').replace('!!', '！')
    return text.strip()
```

### 2. 並發控制

批量合成時限制並發數量：

```python
# 最多 5 個同時請求
semaphore = asyncio.Semaphore(5)

async def synthesize_with_semaphore(index, item):
    async with semaphore:
        return await self.synthesize_speech(...)
```

### 3. 緩存機制

避免重複合成相同文本：

```python
import hashlib
from app.services.cache_service import cache

async def get_or_generate_audio(text: str):
    # 生成文本的 hash 作為 cache key
    text_hash = hashlib.md5(text.encode()).hexdigest()
    cache_key = f"tts:{text_hash}"
    
    # 檢查緩存
    cached_path = await cache.get(cache_key)
    if cached_path:
        return cached_path
    
    # 生成新音頻
    audio_path = await cantonese_tts.synthesize_speech(text=text)
    
    # 存入緩存
    await cache.set(cache_key, audio_path, expire=3600)
    return audio_path
```

---

## 📈 成本估算

### API 定價（假設）

如果 Cantonese AI 按字符計費：

- **單價**: $0.0001 / 字符
- **每日播客**: 約 3000 字符
- **月成本**: 3000 × 30 天 × $0.0001 = $9/月
- **年成本**: ~$108/年

相比 Azure TTS（~$16/1M 字符），Cantonese AI 提供更優質嘅粵語體驗。

---

## 🔍 故障排除

### 常見問題

**Q1: API 返回 401 錯誤**
- 檢查 API Key 是否正確
- 確認 API Key 沒有過期

**Q2: 音頻質量不佳**
- 調整 `speed` 和 `pitch` 參數
- 確保文本標點正確

**Q3: 響應時間過長**
- 檢查網絡連接
- 實施緩存機制
- 考慮批量處理

**Q4: 中文亂碼**
- 確保文件編碼為 UTF-8
- Windows 用戶需要設置 `PYTHONUTF8=1`

---

## 📞 技術支援

如有問題，請查看：
- API 文檔：https://cantonese.ai/docs
- GitHub Issues: https://github.com/lycheecheeee/ETLite/issues
- 示例代碼：`backend/examples/cantonese_tts_example.py`

---

**Cantonese AI TTS 集成完成！** 🎉

Net 仔系統而家擁有業界領先嘅粵語語音合成能力，可以為用戶提供自然、流暢嘅粵語理財播客體驗！
