from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

NOTION_API_KEY = os.environ.get("NOTION_API_KEY")
NOTION_VERSION = "2022-06-28"  # 최신 버전으로 맞춰줄 것

headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Notion-Version": NOTION_VERSION,
    "Content-Type": "application/json"
}

# 재귀적으로 모든 텍스트 블록 가져오기
def get_all_text_blocks(block_id):
    url = f"https://api.notion.com/v1/blocks/{block_id}/children?page_size=100"
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        print("🔴 Error while fetching children of block:", block_id)
        return []

    blocks = res.json().get("results", [])
    texts = []

    for block in blocks:
        block_type = block.get("type", "")
        if block_type == "image":
            continue  # 이미지 제외

        if "rich_text" in block.get(block_type, {}):
            rich_texts = block[block_type]["rich_text"]
            for rt in rich_texts:
                if "plain_text" in rt:
                    texts.append(rt["plain_text"])

        # 자식 블록이 또 있으면 재귀적으로 탐색
        if block.get("has_children"):
            child_id = block["id"]
            texts.extend(get_all_text_blocks(child_id))

    return texts

@app.route("/notion")
def get_notion_data():
    page_id = request.args.get("page_id")
    if not page_id:
        return jsonify({"error": "Missing page_id"}), 400

    page_id = page_id.replace("-", "")

    try:
        all_texts = get_all_text_blocks(page_id)
        return jsonify({"blocks": all_texts})
    except Exception as e:
        print("🔥 Notion API error:", e)
        return jsonify({"error": "Notion API error"}), 500

@app.route("/")
def index():
    return "✅ Notion API server is running!"

