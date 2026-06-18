# APK Upload Telegram Bot

Telegram bot jo APK file receive karke GitHub pe upload karta hai. Same file path pe upload hoti hai, taki direct download link kabhi na badle.

## How it Works
1. Telegram pe APK file bhejo (e.g. `MParivahan.apk`)
2. Bot file download karta hai
3. GitHub pe same naam se upload/update karta hai
4. Download link reply mein milta hai

---

## Setup Guide (Zero to Running)

### Step 1: GitHub Personal Access Token banana
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. "Generate new token (classic)" click karo
3. Note: `APK Bot Token`
4. Expiration: apni marzi se
5. Scopes mein sirf **`repo`** check karo
6. Generate karo aur token copy karo (ek baar hi dikhega)

### Step 2: Is code ko GitHub pe push karo
```bash
git init
git add .
git commit -m "Initial bot setup"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_BOT_REPO.git
git push -u origin main
```

### Step 3: Northflank Setup
1. [northflank.com](https://northflank.com) pe login karo
2. **New Project** banao → naam do (e.g. `apk-bot`)
3. Project ke andar **New Service** → **Combined Service** select karo
4. **Source**: GitHub select karo, apna bot repo connect karo
5. **Branch**: `main`
6. **Build**: Dockerfile detected hoga automatically
7. **Port**: koi port set karne ki zarurat nahi (bot polling use karta hai)

### Step 4: Environment Variables set karo (Northflank)
Service ke andar → **Environment** tab → **Add variables**:

| Key | Value |
|-----|-------|
| `TELEGRAM_BOT_TOKEN` | BotFather se mila token |
| `GITHUB_TOKEN` | Step 1 ka token |
| `GITHUB_REPO` | `ilanding/Pomatoapk` |
| `GITHUB_BRANCH` | `main` |

### Step 5: Deploy!
- Save karo → Northflank automatically build aur deploy karega
- Logs mein `Bot started...` dikhega → sab set hai!

---

## Usage
- Koi bhi `.apk` file Telegram pe bhejo
- Bot reply karega direct download link ke saath
- Purani file automatically replace ho jaati hai
- Link hamesha same rehta hai!

## Direct Download Link Format
```
https://github.com/ilanding/Pomatoapk/raw/main/MParivahan.apk
```
