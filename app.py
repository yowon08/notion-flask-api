from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

NOTION_API_KEY = os.environ.get("NOTION_API_KEY")

@app.route("/")
def home():
    return "✅ This is your Notion API server. Use /notion?page_id=... to fetch content."

@app.route("/notion")
def get_notion_content():
    page_id = request.args.get("page_id")
    if not page_id:
        return jsonify({"error": "Missing page_id"}), 400

    page_id = page_id.replace("-", "")  # ✅ 하이픈 제거

    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }

    try:
        res = requests.get(url, headers=headers)
        res.raise_for_status()

        blocks = res.json().get("results", [])
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
