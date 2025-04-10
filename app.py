from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

NOTION_API_KEY = os.environ.get("NOTION_API_KEY")
NOTION_VERSION = "2022-06-28"


def get_block_children(block_id):
    url = f"https://api.notion.com/v1/blocks/{block_id}/children?page_size=100"
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Notion-Version": NOTION_VERSION,
    }
    res = requests.get(url, headers=headers)
    data = res.json()
    blocks = []

    for block in data.get("results", []):
        text = extract_text_from_block(block)
        if text:
            blocks.append(text)
        # 자식 블록이 있다면 재귀
        if block.get("has_children"):
            blocks.extend(get_block_children(block["id"]))

    return blocks


def extract_text_from_block(block):
    try:
        block_type = block["type"]
        content = block.get(block_type, {})

        # title (예: 페이지 제목)
        if "title" in content:
            return ''.join([t["plain_text"] for t in content["title"]])

        # 일반적인 텍스트 블록
        if "rich_text" in content:
            return ''.join([t["plain_text"] for t in content["rich_text"]])

    except Exception:
        pass

    return None


@app.route("/")
def home():
    return "✅ Notion API 서버가 실행 중입니다!"


@app.route("/notion")
def notion():
    page_id = request.args.get("page_id")
    if not page_id:
        return jsonify({"error": "Missing page_id"}), 400

    try:
        # 하이픈 제거
        page_id = page_id.replace("-", "")
        blocks = get_block_children(page_id)
        return jsonify({"blocks": blocks})
    except Exception as e:
        return jsonify({"error": "Notion API error", "details": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
