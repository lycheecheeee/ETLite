# GitHub 上傳指南

## 📦 已完成的步驟

✅ Git 倉庫已初始化
✅ 所有文件已添加到暫存區
✅ 第一個 commit 已創建

## 🚀 接下來只需 3 步

### 步驟 1: 在 GitHub 上創建私有倉庫

1. 訪問：https://github.com/new
2. 填寫倉庫信息：
   - **Repository name**: `netzai-podcast-system`
   - **Description**: "AI 粵語理財播客系統 - 結合人工智能、音頻內容與心理學設計的財經資訊平台"
   - **Visibility**: 🔒 **Private** (私有)
   - ❌ 不要勾選 "Initialize this repository with a README"
3. 點擊 **"Create repository"**

### 步驟 2: 添加遠程倉庫地址

在終端執行以下命令（替換 `YOUR_USERNAME` 為你的 GitHub 用戶名）：

```bash
cd c:\Users\user\Desktop\etnet_radio_v2
git remote add origin https://github.com/YOUR_USERNAME/netzai-podcast-system.git
```

### 步驟 3: 推送代碼到 GitHub

```bash
# 推送到 main 分支
git branch -M main
git push -u origin main
```

## 🔐 如果遇到認證問題

### 方法 A: 使用 Personal Access Token

1. 訪問：https://github.com/settings/tokens
2. 點擊 **"Generate new token (classic)"**
3. 選擇 scopes: 勾選 **`repo`** (Full control of private repositories)
4. 生成 token 並複製
5. 推送時使用：
   ```bash
   git push -u origin main
   # 當提示輸入密碼時，粘貼你的 token
   ```

### 方法 B: 使用 SSH（推薦）

1. 生成 SSH key：
   ```bash
   ssh-keygen -t ed25519 -C "your_email@example.com"
   ```
2. 添加 SSH key 到 GitHub：
   - 訪問：https://github.com/settings/keys
   - 點擊 **"New SSH key"**
   - 粘貼 `~/.ssh/id_ed25519.pub` 的內容
3. 使用 SSH 地址：
   ```bash
   git remote add origin git@github.com:YOUR_USERNAME/netzai-podcast-system.git
   git push -u origin main
   ```

## ✅ 驗證上傳成功

推送完成後，你應該看到：

```
Enumerating objects: XX, done.
Counting objects: 100% (XX/XX), done.
Delta compression using up to X threads
Compressing objects: 100% (XX/XX), done.
Writing objects: 100% (XX/XX), XX.XX KiB | X.XX MiB/s, done.
Total 3 (delta 0), reused 0 (delta 0), pack-reused 0
remote: 
remote: Create a pull request for 'main' on GitHub by visiting:
remote:      https://github.com/YOUR_USERNAME/netzai-podcast-system/pulls
remote: 
To github.com:YOUR_USERNAME/netzai-podcast-system.git
 * [new branch]      main -> main
Branch 'main' set up to track remote branch 'main' from 'origin'.
```

然後訪問你的倉庫頁面確認所有文件都已上傳。

## 📊 預期的倉庫結構

上傳成功後，你的 GitHub 倉庫應該包含：

```
netzai-podcast-system/
├── 📄 README.md              # 項目介紹
├── 📄 ARCHITECTURE.md        # 系統架構詳解
├── 📄 QUICKSTART.md          # 快速開始指南
├── 📄 .gitignore             # Git 忽略文件
├── 📄 docker-compose.yml     # Docker 編排
├── 📁 src/                   # 前端源碼
│   ├── components/           # React 組件
│   └── ...
├── 📁 backend/               # 後端服務
│   ├── app/                  # Python 代碼
│   ├── requirements.txt      # Python 依賴
│   └── Dockerfile
└── 📁 dialogue/              # 音頻文件（如果有的話）
```

## 🎯 後續操作建議

### 1. 設置 GitHub Pages（可選）

如果你想展示前端演示：

1. 訪問倉庫的 **Settings → Pages**
2. Source: 選擇 **GitHub Actions**
3. 添加部署 workflow

### 2. 添加 CI/CD（可選）

創建 `.github/workflows/ci.yml`：

```yaml
name: CI/CD

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm ci
      - run: npm test

  test-backend:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: password
      redis:
        image: redis:7
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r backend/requirements.txt
      - run: pytest backend/tests/
```

### 3. 邀請協作者（可選）

1. 訪問倉庫的 **Settings → Collaborators**
2. 點擊 **"Add people"**
3. 輸入協作者的 GitHub 用戶名

---

**祝你上傳順利！** 🎉

如有任何問題，請查看 GitHub 文檔或聯繫技術支援。
