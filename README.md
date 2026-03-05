# 🎙️ Net 仔 - AI 粵語理財播客

> 結合人工智能、音頻內容與心理學設計的財經資訊平台  
> 專注服務以粵語為母語的香港投資者

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![React](https://img.shields.io/badge/React-18.2-blue)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue)](https://www.docker.com/)

---

## ✨ 核心特色

### 🌌 宇宙級產品體驗
- **萬有引力**: 個人化算法自動聚合內容
- **星球**: 每隻股票作為獨立天體運行
- **星系**: 四大內容頻道（財經/健康/生活/Diva）
- **陰陽燭海**: K 線數據可視化呈現
- **黑洞**: 過濾詐騙與不實資訊
- **蟲洞**: 語音指令實現快捷導航

### 🎯 解決五大痛點
| 痛點 | Net 仔方案 |
|------|-----------|
| ❌ 資訊過載 | ✅ AI 個人化篩選 |
| ❌ 語言隔閡 | ✅ 100% 粵語內容 |
| ❌ 情緒孤立 | ✅ 互動電台 + 社群 |
| ❌ 決策困難 | ✅ 三維畫像 + 智能建議 |
| ❌ 時間碎片 | ✅ 原子化內容 + 語音導航 |

---

## 🚀 快速開始

### 前端應用（已運行）

```bash
# 訪問地址
http://localhost:3001
```

包含功能：
- ✅ 用戶三維標籤測試
- ✅ 互動電台（多主持人 + Call-in）
- ✅ AI 播客播放器
- ✅ 內容原子展示
- ✅ Gamma 模式自定義界面

### 後端服務（可選）

```bash
# 啟動所有後端服務
docker-compose up -d

# 訪問 API 文檔
http://localhost:8000/docs
```

後端功能：
- 🎙️ Azure TTS 語音合成
- 🤖 AI 內容生成
- 📊 PostgreSQL + Redis
- 💾 MinIO 音頻存儲
- 📡 WebSocket 實時推送

詳細配置請查看 [QUICKSTART.md](./QUICKSTART.md)

---

## 📁 項目結構

```
etnet_radio_v2/
├── src/                          # 前端源碼
│   ├── components/               # React 組件
│   │   ├── UserProfileTest.tsx   # 用戶測試
│   │   ├── InteractiveRadio.tsx  # 互動電台
│   │   ├── PodcastPlayer.tsx     # 播客播放器
│   │   ├── ContentAtoms.tsx      # 內容原子
│   │   └── GammaMode.tsx         # Gamma 模式
│   ├── App.tsx                   # 主應用
│   └── index.css                 # 全局樣式
│
├── backend/                      # 後端服務
│   ├── app/
│   │   ├── api/                  # API 路由
│   │   ├── core/                 # 核心配置
│   │   ├── db/                   # 數據庫
│   │   ├── services/             # 業務邏輯
│   │   │   ├── tts_service.py    # TTS 服務
│   │   │   ├── podcast_generator.py  # 播客生成
│   │   │   └── audio_processor.py    # 音頻處理
│   │   └── main.py               # 入口文件
│   ├── requirements.txt          # Python 依賴
│   └── Dockerfile                # Docker 配置
│
├── docker-compose.yml            # Docker 編排
├── ARCHITECTURE.md               # 架構文檔
└── QUICKSTART.md                 # 快速開始指南
```

---

## 🎨 功能演示

### 1. 用戶畫像測試 (6 問題)

透過 6 條問題分析用戶的：
- **理財基礎**: 新手 / 中階 / 高階
- **人生心態**: 求穩型 / 平衡型 / 進取型
- **時間視角**: 長線 / 中線 / 短線

### 2. 互動電台系統

**真實電台體驗：**
- 🎙️ 雙主持人交替主持（子程 👨‍🎤 / 敏娜 👩‍🎤）
- 📻 8 段音頻串流播放
- 💬 即時留言討論區
- 📞 Call-in 熱線系統
- 📊 實時統計數據

### 3. AI 播客生成器

**自動化流程：**
```
用戶畫像 → AI 劇本生成 → TTS 語音合成 → 音頻處理 → 最終輸出
           (OpenAI)      (Azure)      (Pydub)    (MinIO)
```

### 4. 內容原子系統

**7 種內容形態：**
- ⚡ 閃電快訊 (<10 秒)
- 📰 語音頭條 (30 秒)
- 🎙️ 深度播客 (5-8 分鐘)
- 💬 問答對話 (互動式)
- 📊 數據可視 (圖表 + 語音)
- 📖 故事敘述 (場景化)
- 🎤 專家訪談 (真人對話)

### 5. Gamma 模式

**三種軌道：**
1. 🛤️ 傳統軌道 - 編輯預設線性流程
2. 🤖 AI 推薦軌道 - 算法自動排列
3. 🎨 自由軌道 - 用戶拖曳自定義

---

## 🛠️ 技術棧

### 前端
- **Framework**: React 18 + Vite + TypeScript
- **UI**: Tailwind CSS + Shadcn/ui
- **Audio**: HTML5 Audio API
- **Real-time**: WebSocket

### 後端
- **Framework**: FastAPI + Uvicorn
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **TTS**: Azure Cognitive Services
- **AI**: OpenAI GPT-4
- **Storage**: MinIO (S3-compatible)

### 基礎設施
- **Container**: Docker + Docker Compose
- **Orchestration**: Kubernetes (生產環境)
- **Monitoring**: Prometheus + Grafana
- **Logging**: ELK Stack

---

## 📊 系統架構

```
┌─────────────────────────────────────────────────────────┐
│                     用戶層                               │
│  Web App / Mobile App / WhatsApp Bot                   │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  API Gateway                             │
│           FastAPI + WebSocket Server                    │
└────────────┬─────────────────────┬──────────────────────┘
             │                     │
      ┌──────▼──────┐       ┌──────▼──────┐
      │  TTS 服務    │       │  AI 生成服務  │
      │  Azure TTS  │       │  OpenAI     │
      └─────────────┘       └─────────────┘
             │                     │
             └──────────┬──────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│                    數據層                                │
│  PostgreSQL + Redis + MinIO                            │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 商業模型

### 會員分層

| 功能 | 非會員 | 會員 | 付費會員 |
|------|--------|------|----------|
| 即時新聞 | ❌ 延遲 | ✅ | ✅ |
| 音頻質素 | 96kbps | 192kbps | 320kbps |
| AI 問答 | 3 次/日 | 20 次/日 | 無限 |
| 自選股 | 3 隻 | 50 隻 | 無限 |

### 定價策略
- **月費**: $88 HKD
- **年費**: $888 HKD (省 16%)
- **家庭計劃**: 4 人 $168 (人均$42)

---

## 📈 發展路線圖

### Phase 1 - MVP ✅ (已完成)
- ✅ Web 前端原型
- ✅ 用戶標籤系統
- ✅ 互動電台界面
- ✅ 後端 API 架構

### Phase 2 - Beta (3-6 個月)
- [ ] React Native App
- [ ] WhatsApp Bot
- [ ] 實時市場數據
- [ ] 付費系統

### Phase 3 - Launch (6-12 個月)
- [ ] 自訓練 TTS 模型
- [ ] 語音識別 (STT)
- [ ] 券商 API 對接
- [ ] 社交功能

### Phase 4 - Scale (12-18 個月)
- [ ] 專家直播間
- [ ] Group Investment
- [ ] AI 投顧服務
- [ ] 跨境財富管理

---

## 🧪 測試

### 前端測試
```bash
npm test
```

### 後端測試
```bash
cd backend
pytest tests/
```

### TTS 測試
```bash
cd backend
python test_tts.py
```

---

## 📚 文檔

- **[QUICKSTART.md](./QUICKSTART.md)** - 5 分鐘快速開始
- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - 完整系統架構
- **[backend/README.md](./backend/README.md)** - 後端開發指南

---

## 🤝 貢獻指南

歡迎提交 Issue 和 Pull Request！

1. Fork 本項目
2. 創建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

---

## 📄 授權

本項目採用 MIT 授權 - 詳見 [LICENSE](LICENSE) 文件

---

## 👥 團隊

- **Product**: Net 仔產品團隊
- **Tech Lead**: [你的名字]
- **AI/TTS**: Azure Cognitive Services
- **Design**: 宇宙主題設計團隊

---

## 📞 聯絡方式

- **網站**: https://netzai.com
- **Email**: hello@netzai.com
- **WhatsApp**: +852 XXXX XXXX

---

## 🙏 鳴謝

感謝以下開源項目和服務：
- [React](https://reactjs.org/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Azure Cognitive Services](https://azure.microsoft.com/zh-hk/services/cognitive-services/)
- [OpenAI](https://openai.com/)

---

**Made with ❤️ for Cantonese investors in Hong Kong**

© 2026 Net 仔. All rights reserved.
