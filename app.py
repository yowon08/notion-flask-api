from flask import Flask, request, jsonify
import requests
import os
import re

app = Flask(__name__)

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_VERSION = "2022-06-28"

@app.route("/notion")
def get_notion():
    page_id = request.args.get("page_id")
    if not page_id:
        return jsonify({"error": "Missing page_id"}), 400

    # ✅ page_id에서 하이픈 자동 제거
    page_id = page_id.replace("-", "")
    if not re.fullmatch(r"[0-9a-fA-F]{32}", page_id):
        return jsonify({"error": "Invalid page_id format"}), 400

    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Notion-Version": NOTION_VERSION
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return jsonify({"error": "Notion API error"}), 500

    blocks = response.json().get("results", [])
    texts = []

    for block in blocks:
        if block["type"] == "paragraph":
            texts.append("".join(
                text.get("plain_text", "") for text in block["paragraph"]["text"]
            ))

    return jsonify({"blocks": texts})
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render가 요구하는 방식!
    app.run(host="0.0.0.0", port=port)
