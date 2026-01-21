#!/usr/bin/env python3
"""Mock LLM service for testing RAG pipeline"""
from flask import Flask, request, jsonify

app = Flask(__name__)

MOCK_RESPONSES = {
    "default": "基于提供的上下文，这是一个模拟的 LLM 响应。在实际环境中，这里会返回真实的大语言模型生成的答案。"
}

@app.route('/v1/chat/completions', methods=['POST'])
def chat_completions():
    data = request.json
    messages = data.get('messages', [])

    # Extract user question
    user_msg = next((m['content'] for m in messages if m['role'] == 'user'), '')

    # Simple keyword-based mock responses
    if 'flink' in user_msg.lower() or 'cdc' in user_msg.lower():
        answer = "Flink CDC 配置需要启用 MySQL binlog 并创建复制用户。具体步骤请参考相关文档。"
    elif 'milvus' in user_msg.lower() or '向量' in user_msg.lower():
        answer = "Milvus 向量数据库支持多种索引类型，推荐使用 HNSW 索引以获得最佳性能。"
    elif 'spark' in user_msg.lower() or '去重' in user_msg.lower():
        answer = "Spark 可以使用 MinHash LSH 算法进行高效的数据去重，适合处理大规模数据集。"
    else:
        answer = MOCK_RESPONSES['default']

    return jsonify({
        "id": "mock-completion-001",
        "object": "chat.completion",
        "created": 1234567890,
        "model": "mock-llm",
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": answer
            },
            "finish_reason": "stop"
        }]
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
