# discord_bot

## 重新部署

設定檔不在這個 repo，放在私有 repo `discord_bot_secret`。Discord token 與 Google service account 金鑰沒有備份，每次部署都重新產生。

1. 在 GCP 的 us-central1 建立一台 e2-micro，搭配 30GB 以內的標準磁碟，這樣會落在 Always Free 額度內。
2. 在 VM 上把兩個 repo 都 clone 下來，再把 `discord_bot_secret/settings/` 複製到 `discord_bot/settings/`。
3. 重新產生 Discord token，填進 `settings/.env` 的 `DISCORD_TOKEN`。
   - 登入 https://discord.com/developers/applications ，點進這個 bot 的應用程式。應用程式名稱寫在 `discord_bot_secret` 的 README。
   - 左側選 Bot，在 Token 區塊按 Reset Token，再按確認。
   - Discord 會要求帳號的兩步驟驗證，輸入驗證碼後新 token 才會出現。
   - token 只會顯示這一次，離開頁面就看不到了，要立刻複製。舊 token 會同時失效。
4. 到 GCP 的 IAM 頁面替讀取 Google Drive 的 service account 建立新金鑰，放到 `settings/`，並把路徑填進 `GOOGLE_AUTH_KEY_PATH`。
5. 用 Python 3.10 以上安裝套件並啟動。

```
pip install -U -r requirements.txt
nohup python3 -u main.py > bot.log 2>&1 &
```

`-u` 讓 `print` 立刻寫進 `bot.log`，才看得到登入身份與載入了幾個斜線指令。

`settings/.env` 不要加 `TESTING`，否則 bot 一上線就會立刻發送紀念日訊息與圖片。

不用的時候直接刪除 VM，不要只停機或暫停。暫停狀態的 RAM 會計費，而 `/rem-add` 新增的提醒事項記得先複製回 `discord_bot_secret` 再刪。

刪除 VM 後，讓用過的憑證失效。
- Discord 沒有刪除 token 的功能。到 Bot 頁面再按一次 Reset Token，舊 token 就會失效，新產生的 token 不用複製，直接離開頁面。
- 到 GCP 的 IAM 頁面刪除這次替 service account 建立的金鑰。

------------------------------------------------------
<< 別人的 readme >>

# Node.js 請看這篇教學
https://reurl.cc/xDozj1

# Python 原文教學
https://reurl.cc/5gV0WV


==========================
# 加在最開始模組導入
import keep_alive

# 加在 bot.run(token) 前一行
keep_alive.keep_alive()

# 監控 Bot 網站
https://uptimerobot.com/
------------------------------------------------------
