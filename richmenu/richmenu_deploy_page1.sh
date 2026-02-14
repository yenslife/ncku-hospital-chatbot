#!/bin/bash

# ======= 使用者設定 =======
ACCESS_TOKEN=$LINE_ACCESS_TOKEN
ALIAS_ID="richmenu1"
IMAGE_PATH="images/richmenu1.png"
CHATBAR_TEXT="點我會有驚喜歐！😎"
RICHMENU_NAME="page1"
# ==========================

echo "[1] 從 list 找出 name 為 ${RICHMENU_NAME} 的 rich menu..."
MENU_IDS=$(curl -s -X GET "https://api.line.me/v2/bot/richmenu/list" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" | jq -r '.richmenus[] | select(.name=="'"$RICHMENU_NAME"'") | .richMenuId')

TOTAL_COUNT=$(echo "$MENU_IDS" | wc -l | tr -d ' ')
echo "[2] 找到 $TOTAL_COUNT 個 rich menu 名稱為 '$RICHMENU_NAME'"

if [[ "$TOTAL_COUNT" -gt 0 ]]; then
  echo "[3] 開始刪除..."
  echo "$MENU_IDS" | while read OLD_ID; do
    echo "🗑️ 刪除 richMenuId: $OLD_ID"
    curl -s -X DELETE "https://api.line.me/v2/bot/richmenu/$OLD_ID" \
      -H "Authorization: Bearer $ACCESS_TOKEN" \
      -H "Content-Type: application/json"
  done
else
  echo "[3] 沒有找到要刪除的 rich menu"
fi

# === 刪除 alias ===
echo "[4] 嘗試刪除 alias $ALIAS_ID..."
ALIAS_EXISTS=$(curl -s -X GET "https://api.line.me/v2/bot/richmenu/alias/${ALIAS_ID}" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" | jq -r '.richMenuId')

if [[ "$ALIAS_EXISTS" != "null" ]]; then
  echo "🗑️ 刪除 alias $ALIAS_ID"
  curl -s -X DELETE "https://api.line.me/v2/bot/richmenu/alias/${ALIAS_ID}" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json"
else
  echo "✅ 無對應 alias，略過"
fi

# 建立新 rich menu，並取得新 richMenuId
echo "[5] 建立新的 rich menu..."
CREATE_RES=$(curl -s -X POST "https://api.line.me/v2/bot/richmenu" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
  "size": {
    "width": 2500,
    "height": 1686
  },
  "selected": true,
  "name": "'$RICHMENU_NAME'",
  "chatBarText": "'$CHATBAR_TEXT'",
"areas": [
    {
      "bounds": {
        "x": 74,
        "y": 219,
        "width": 1131,
        "height": 330
      },
      "action": {
        "type": "message",
        "text": "/基本資料"
      }
    },
    {
      "bounds": {
        "x": 1349,
        "y": 227,
        "width": 1068,
        "height": 326
      },
      "action": {
        "type": "message",
        "text": "/常見問題"
      }
    },
    {
      "bounds": {
        "x": 111,
        "y": 685,
        "width": 1077,
        "height": 330
      },
      "action": {
        "type": "postback",
        "data": "postback_知識寶典"
      }
    },
    {
      "bounds": {
        "x": 1304,
        "y": 689,
        "width": 1085,
        "height": 318
      },
      "action": {
        "type": "message",
        "text": "/治療訊息"
      }
    },
    {
      "bounds": {
        "x": 107,
        "y": 1134,
        "width": 1073,
        "height": 335
      },
      "action": {
        "type": "message",
        "text": "/專家線上療"
      }
    },
    {
      "bounds": {
        "x": 1316,
        "y": 1139,
        "width": 1073,
        "height": 321
      },
      "action": {
        "type": "message",
        "text": "/協助資源"
      }
    }
  ]
}')

NEW_ID=$(echo "$CREATE_RES" | jq -r '.richMenuId')
echo "[5] 新的 richMenuId: $NEW_ID"

# 上傳圖片
echo "[6] 上傳圖片..."
curl -s -X POST "https://api-data.line.me/v2/bot/richmenu/$NEW_ID/content" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: image/png" \
  -T "$IMAGE_PATH"

# 設定 alias
echo "[7] 綁定 alias: $ALIAS_ID → $NEW_ID"
curl -s -X POST "https://api.line.me/v2/bot/richmenu/alias" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "richMenuAliasId": "'$ALIAS_ID'",
    "richMenuId": "'$NEW_ID'"
  }'

# 設定預設 rich menu
echo "[8] 設定預設 rich menu..."
curl -s -X POST "https://api.line.me/v2/bot/user/all/richmenu/$NEW_ID" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d ''

echo "✅ 部署完成！"

