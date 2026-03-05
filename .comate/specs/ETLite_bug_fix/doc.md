# ETLite Bug Fix 需求文檔

## 需求背景
ETLite 是一個 AI 粵語理財播客系統，結合人工智能、音頻內容與心理學設計的財經資訊平台。用戶報告存在多個功能異常和顯示問題，需要進行全面的bug修復。

## 需求場景具體處理邏輯
- 前端React應用運行在端口3000，後端FastAPI服務應運行在端口8000
- 用戶可以進行理財畫像測試、收聽AI播客、使用互動電台等功能
- 系統需要與外部API進行通信（AI聊天、TTS語音合成、新聞播客生成）
- 音頻文件需要正確載入和播放

## 架構技術方案
- 前端：React 18 + Vite + TypeScript + Tailwind CSS
- 後端：FastAPI + PostgreSQL + Redis + MinIO
- 外部服務：OpenAI GPT-4 + Azure TTS + Cantonese AI TTS

## 影響文件
### 主要問題文件：
1. **前端組件文件**：
   - `src/components/InteractiveRadio.tsx` - 音頻文件路徑問題
   - `src/components/PodcastPlayer.tsx` - 音頻文件路徑問題
   - `src/components/ChatWithLeungZai.tsx` - API調用和TTS服務問題
   - `src/components/AINewsPodcast.tsx` - API調用問題
   - `src/components/SmartRadioPlayer.tsx` - API調用和音頻問題

2. **配置文件**：
   - `vite.config.ts` - 可能需要配置代理
   - `package.json` - 腳本配置

3. **後端配置**：
   - `backend/app/main.py` - 靜態文件服務配置
   - `backend/app/core/config.py` - 環境變量配置

## 實現細節

### Bug 1: 音頻文件路徑錯誤
**問題**：多個組件中引用的音頻文件路徑不正確，如 `/dialogue/00_zicheng.wav`
**修復方案**：
- 檢查音頻文件是否存在於正確位置
- 更新文件路徑或創建正確的文件結構
- 配置靜態文件服務

```typescript
// 當前錯誤路徑
audioFile: '/dialogue/00_zicheng.wav'
// 修復後路徑
audioFile: '/audio/dialogue/00_zicheng.wav'
```

### Bug 2: API調用失敗
**問題**：多個組件調用 `http://localhost:8000/api/v1/...` 端點失敗
**修復方案**：
- 檢查後端服務是否正在運行
- 配置CORS策略
- 添加錯誤處理和降級方案

```typescript
// 添加錯誤處理
try {
  const response = await fetch('http://localhost:8000/api/v1/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({...})
  })
  if (!response.ok) throw new Error('API call failed')
  return await response.json()
} catch (error) {
  console.error('API Error:', error)
  // 降級到本地mock數據
  return getMockData()
}
```

### Bug 3: TTS API配置問題
**問題**：`ChatWithLeungZai.tsx` 中硬編碼的 Cantonese AI TTS API密鑰和端點
**修復方案**：
- 將API密鑰移至環境變量
- 添加備用TTS服務
- 改進錯誤處理

```typescript
// 使用環境變量
const TTS_API_KEY = import.meta.env.VITE_CANTONESE_AI_API_KEY
const TTS_ENDPOINT = import.meta.env.VITE_CANTONESE_AI_ENDPOINT
```

### Bug 4: 後端靜態文件服務配置
**問題**：後端靜態文件服務路徑配置可能不正確
**修復方案**：
- 檢查 `main.py` 中的靜態文件掛載
- 確保音頻文件位於正確目錄

```python
# 修復靜態文件服務
app.mount("/audio", StaticFiles(directory="backend/app/static/audio"), name="audio")
```

## 邊界條件與異常處理
- 網絡連接失敗時的降級處理
- API調用超時處理
- 音頻文件載入失敗的備用方案
- 用戶輸入驗證和錯誤提示

## 數據流動路徑
1. 用戶操作 → React組件
2. API調用 → FastAPI後端
3. 外部服務集成 (OpenAI/Azure TTS)
4. 靜態文件服務 → 音頻播放

## 預期成果
- 所有音頻文件能正常載入和播放
- API調用成功，數據正確顯示
- TTS功能正常工作
- 錯誤處理完善，用戶體驗流暢
- 後端服務穩定運行