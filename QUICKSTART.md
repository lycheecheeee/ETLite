# Net 仔 - 快速開始指南

## 🚀 5 分鐘快速體驗

### 步驟 1：檢查環境

確保你已安裝：
- ✅ Node.js 18+ 
- ✅ Docker Desktop（用於後端）
- ✅ Python 3.11+（可選，本地開發用）

### 步驟 2：啟動前端（已經運行中）

前端已經在 `http://localhost:3001` 運行中！

如果未運行，執行：
```bash
cd c:\Users\user\Desktop\etnet_radio_v2
npm run dev
```

### 步驟 3：配置後端（可選）

如果你想體驗完整的 TTS 語音生成功能：

#### 3.1 獲取 Azure TTS 密鑰（免費）

1. 訪問：https://portal.azure.com/#create/Microsoft.CognitiveServicesSpeechServices
2. 創建 Speech Service（選擇 Free F0 層級）
3. 複製 Key 和 Region

#### 3.2 配置環境變量

```bash
cd backend
copy .env.example .env
```

編輯 `.env` 文件：
```env
AZURE_SPEECH_KEY=你的_Azure_密鑰
AZURE_SPEECH_REGION=southeastasia
OPENAI_API_KEY=你的_OpenAI_密鑰（可選）
```

### 步驟 4：啟動後端服務

#### 方法 A：使用 Docker（推薦）

```bash
# 從項目根目錄執行
docker-compose up -d
```

等待 30 秒讓所有服務啟動，然後訪問：
- **API 文檔**: http://localhost:8000/docs
- **MinIO 控制台**: http://localhost:9001

#### 方法 B：本地運行（無需 Docker）

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 步驟 5：測試 TTS 功能

```bash
cd backend
python test_tts.py
```

如果看到 `✅ All tests passed!`，說明 TTS 配置成功！

---

## 📱 使用指南

### 1. 用戶畫像測試

訪問 http://localhost:3001 → 點擊「個人化測試」

回答 6 條問題後，系統會生成你的投資畫像：
- 理財基礎（新手/中階/高階）
- 人生心態（求穩/平衡/進取）
- 時間視角（長線/中線/短線）

### 2. 收聽播客

切換到「AI 播客」或「互動電台」分頁：
- ▶️ 播放按鈕開始收聽
- ⏭️ 跳轉到不同段落
- 💬 發送訊息給主持人
- 📞 模擬 Call-in 互動

### 3. 瀏覽內容原子

切换到「內容原子」分頁：
- 查看市場數據、個股資訊
- AI 推薦軌道（智能排序）
- Gamma 模式（自定義佈局）

---

## 🔧 常見問題

### Q1: Docker 容器無法啟動

**解決方法：**
```bash
# 查看日誌
docker-compose logs

# 重啟服務
docker-compose restart

# 完全重置
docker-compose down -v
docker-compose up -d
```

### Q2: TTS 測試失敗

**檢查清單：**
- [ ] Azure 密鑰是否正確？
- [ ] 網絡是否可以訪問 Azure？
- [ ] 密鑰是否已激活？

**測試連接：**
```bash
curl https://southeastasia.tts.speech.microsoft.com/
```

### Q3: 前端無法連接後端

**解決方法：**
1. 確認後端已啟動：http://localhost:8000/health
2. 檢查 CORS 設置（允許 localhost:3001）
3. 清除瀏覽器緩存

---

## 📚 下一步

### 探索更多功能

1. **API 測試**
   ```bash
   # 訪問 Swagger UI
   http://localhost:8000/docs
   
   # 測試播客生成接口
   POST /api/v1/podcasts/generate
   ```

2. **監控儀表板**
   - Grafana: http://localhost:3000 (admin/admin)
   - Flower: http://localhost:5555

3. **查看日誌**
   ```bash
   docker-compose logs -f backend
   docker-compose logs -f celery_worker
   ```

### 開發者資源

- **完整文檔**: 查看 `ARCHITECTURE.md`
- **API 參考**: 查看 `backend/README.md`
- **源碼結構**: 查看 `backend/app/` 目錄

---

## 🎯 快速命令參考

```bash
# 啟動所有服務
docker-compose up -d

# 停止所有服務
docker-compose down

# 查看服務狀態
docker-compose ps

# 查看日誌
docker-compose logs -f

# 重啟單一服務
docker-compose restart backend

# 進入容器
docker-compose exec backend bash

# 數據庫備份
docker-compose exec postgres pg_dump -U netzai netzai_db > backup.sql

# 恢復數據庫
docker-compose exec -T postgres psql -U netzai netzai_db < backup.sql
```

---

## 💡 提示

- **開發模式**: 修改代碼後自動重載（`--reload` 參數）
- **靜音調試**: 設置 `LOG_LEVEL=WARNING` 減少輸出
- **性能測試**: 使用 `wrk` 或 `ab` 進行壓力測試
- **安全生產**: 務必更改默認密碼和密鑰！

---

**祝你使用愉快！** 🎉

如有問題，請查看 GitHub Issues 或聯繫開發團隊。
