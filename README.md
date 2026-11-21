# discord_bot

## 重新部署

設定檔不在這個 repo，放在私有 repo `discord_bot_secret`。Discord token 與 Google service account 金鑰沒有備份，每次部署都重新產生。

1. 在 GCP 的 us-central1 建立一台 e2-micro，搭配 30GB 以內的標準磁碟，這樣會落在 Always Free 額度內。
2. 在 VM 上把兩個 repo 都 clone 下來，再把 `discord_bot_secret/settings/` 複製到 `discord_bot/settings/`。
3. 到 Discord Developer Portal 的 Bot 頁面按 Reset Token，把新 token 填進 `settings/.env` 的 `DISCORD_TOKEN`。
4. 到 GCP 的 IAM 頁面替讀取 Google Drive 的 service account 建立新金鑰，放到 `settings/`，並把路徑填進 `GOOGLE_AUTH_KEY_PATH`。
5. 用 Python 3.10 以上安裝套件並啟動。

```
pip install -U -r requirements.txt
nohup python3 -u main.py > bot.log 2>&1 &
```

`-u` 讓 `print` 立刻寫進 `bot.log`，才看得到登入身份與載入了幾個斜線指令。

`settings/.env` 不要加 `TESTING`，否則 bot 一上線就會立刻發送紀念日訊息與圖片。

不用的時候直接刪除 VM，不要只停機或暫停。暫停狀態的 RAM 會計費，而 `/rem-add` 新增的提醒事項記得先複製回 `discord_bot_secret` 再刪。

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
