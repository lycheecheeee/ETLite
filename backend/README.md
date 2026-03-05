# Net 仔 Podcast System - 後端服務

AI 粵語理財播客完整語音系統

## 🏗️ 系統架構

```
┌─────────────────────────────────────────────────────────────┐
│                         前端層                               │
│  React Web App / React Native App / WhatsApp Bot           │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      API Gateway                             │
│              FastAPI + WebSocket Server                      │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│   TTS 服務     │  │  音頻處理服務  │  │  AI 生成服務   │
│  Azure TTS    │  │   Pydub       │  │  OpenAI LLM   │
└───────────────┘  └───────────────┘  └───────────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                       數據層                                 │
│  PostgreSQL (數據) + Redis (緩存) + MinIO (音頻文件)        │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 快速開始

### 1. 環境準備

```bash
# 安裝 Docker 和 Docker Compose
# Windows: Docker Desktop
# Mac: Docker Desktop
# Linux: docker.io + docker-compose
```

### 2. 配置環境變量

```bash
cd backend
cp .env.example .env
# 編輯 .env 文件，填入你的 Azure TTS 和 OpenAI API 密鑰
```

### 3. 啟動所有服務

```bash
# 從項目根目錄執行
docker-compose up -d
```

這會啟動：
- ✅ PostgreSQL (端口 5432)
- ✅ Redis (端口 6379)
- ✅ MinIO (端口 9000, 控制台 9001)
- ✅ FastAPI 後端 (端口 8000)
- ✅ Celery Worker (背景任務)
- ✅ Flower (Celery 監控，端口 5555)
- ✅ Prometheus (監控，端口 9090)
- ✅ Grafana (可視化，端口 3000)

### 4. 訪問服務

- **API 文檔**: http://localhost:8000/docs
- **MinIO 控制台**: http://localhost:9001 (minioadmin/minioadmin)
- **Flower 監控**: http://localhost:5555
- **Grafana**: http://localhost:3000 (admin/admin)

## 📡 API 端點

### 用戶相關
- `POST /api/v1/users` - 創建用戶
- `GET /api/v1/users/{user_id}/profile` - 獲取用戶畫像

### 播客相關
- `POST /api/v1/podcasts/generate` - 生成個人化播客
- `GET /api/v1/podcasts` - 獲取播客列表
- `GET /api/v1/podcasts/{podcast_id}` - 獲取播客詳情
- `POST /api/v1/podcasts/{podcast_id}/play` - 記錄播放

### 內容原子相關
- `GET /api/v1/atoms` - 獲取內容原子列表
- `POST /api/v1/atoms` - 創建新內容原子

### 市場數據相關
- `GET /api/v1/market/indices` - 獲取市場指數
- `GET /api/v1/market/stocks/{stock_code}` - 獲取股價

### WebSocket
- `WS /ws/podcast` - 實時播客更新推送

## 🎙️ TTS 語音生成

使用 Azure Cognitive Services 進行粵語語音合成：

```python
from app.services.tts_service import tts_service

# 簡單文本轉語音
audio_path = await tts_service.synthesize_speech(
    text="早晨！我係子程，歡迎收聽 Net 仔財經早新聞"
)

# 帶情感的語音
audio_path = await tts_service.synthesize_with_emotion(
    text="騰訊業績超預期，股價大升 5%！",
    emotion="excited"  # cheerful/sad/angry/excited/friendly
)

# 使用 SSML 高級控制
ssml = tts_service.create_ssml(
    text="恒指而家係 18256 點",
    rate="fast",
    pitch="high",
    volume="loud"
)
audio_path = await tts_service.synthesize_speech(
    text="",
    ssml=ssml
)
```

## 🎵 音頻處理

```python
from app.services.audio_processor import audio_processor

# 合併多個音頻片段
final_audio = await audio_processor.merge_segments(
    segments=["seg1.wav", "seg2.wav", "seg3.wav"],
    add_jingles=True,  # 添加過場音樂
    crossfade=100  # 交叉淡化 100ms
)

# 添加背景音樂
mixed_audio = await audio_processor.add_background_music(
    voice_track="voice.wav",
    music_track="bgm.mp3",
    music_volume=-20  # 音樂音量降低 20dB
)

# 移除靜音
trimmed = await audio_processor.trim_silence("audio.wav")

# 標準化音量
normalized = await audio_processor.normalize_audio("audio.wav")
```

## 📊 數據庫模型

主要模型：
- **User**: 用戶資料 + 三維畫像
- **Podcast**: 播客節目
- **PodcastSegment**: 節目分段（主持人、文本、音頻）
- **ContentAtom**: 內容原子（市場數據、個股資訊等）
- **UserInteraction**: 用戶互動記錄

## 🔧 開發指南

### 本地開發（不使用 Docker）

```bash
# 創建虛擬環境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安裝依賴
pip install -r requirements.txt

# 啟動 PostgreSQL 和 Redis（需要預先安裝）
# 修改 .env 中的連接字符串

# 運行應用
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 測試

```bash
# 運行測試
pytest tests/

# 帶覆蓋率報告
pytest --cov=app tests/
```

## 📈 監控與日誌

### Prometheus + Grafana

Prometheus 每 15 秒抓取一次指標：
- API 響應時間
- 請求成功率
- WebSocket 連接數
- TTS 生成時間
- 音頻處理隊列長度

Grafana 儀表板預配置：
- 系統健康狀態
- API 性能指標
- 業務指標（播客生成數量、活躍用戶等）

### 日誌

日誌文件位於 `backend/logs/app.log`

```python
import logging

logging.info("信息級別")
logging.warning("警告級別")
logging.error("錯誤級別")
```

## 🎯 生產部署

### 擴展策略

```bash
# 增加後端實例
docker-compose up -d --scale backend=3

# 增加 Celery Worker
docker-compose up -d --scale celery_worker=5
```

### 負載均衡

使用 Nginx 或 Traefik 作為反向代理：

```nginx
upstream backend_servers {
    server backend_1:8000;
    server backend_2:8000;
    server backend_3:8000;
}

server {
    listen 80;
    location / {
        proxy_pass http://backend_servers;
    }
}
```

## 🛠️ 故障排除

### 常見問題

**1. TTS 服務無法連接**
```bash
# 檢查 Azure 密鑰是否正確
# 確認網絡可以訪問 Azure 服務
curl https://southeastasia.tts.speech.microsoft.com/
```

**2. 數據庫連接失敗**
```bash
# 檢查 PostgreSQL 是否運行
docker-compose ps postgres

# 查看數據庫日誌
docker-compose logs postgres
```

**3. Redis 連接超時**
```bash
# 重啟 Redis
docker-compose restart redis
```

## 📝 TODO

- [ ] 集成 OpenAI 生成個性化劇本
- [ ] 實現語音識別（STT）用於 Call-in
- [ ] 添加更多音效和背景音樂
- [ ] 優化 TTS 延遲（使用流式傳輸）
- [ ] 實現離線 TTS 模型（VITS/Piper）
- [ ] 添加 A/B 測試框架

---

**Net 仔 Podcast System** © 2026
Built with ❤️ for Cantonese investors
