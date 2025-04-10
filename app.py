from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

NOTION_API_KEY = os.environ.get("NOTION_API_KEY")
NOTION_VERSION = "2022-06-28"

@app.route("/")
def home():
    return "✅ This is your Notion API server. Use /notion?page_id=... to fetch content."

@app.route("/notion")
def get_notion_content():
    page_id = request.args.get("page_id")

    if not page_id:
        return jsonify({"error": "Missing page_id"}), 400

    # 하이픈 제거
    page_id = page_id.replace("-", "")

    url = f"https://api.notion.com/v1/blocks/{page_id}/children"

    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Notion-Version": NOTION_VERSION
    }

    try:
        res = requests.get(url, headers=headers)

        # ✅ 디버깅 로그 출력
        print("🔗 요청 URL:", url)
        print("📨 응답 상태 코드:", res.status_code)
        print("📄 응답 본문:", res.text)

        res.raise_for_status()

        data = res.json()
        blocks = data.get("results", [])
        texts = []

        for block in blocks:
            paragraph = block.get("paragraph", {})
            rich_text = paragraph.get("rich_text", [])
            if rich_text:
                texts.append(rich_text[0].get("plain_text", ""))

        return jsonify({"blocks": texts})

    except Exception as e:
        print("🔥 Notion API error:", e)
        return jsonify({"error": "Notion API error"}), 500

# 🔥 Render용 포트 바인딩 필수
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
