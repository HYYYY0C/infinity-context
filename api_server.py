#!/usr/bin/env python3
"""
🌐 Infinity Context API Server

让小模型也能使用 Hermes 的无限上下文能力！

使用方式:
  小模型 → HTTP POST → Infinity Context API → Hermes → 返回摘要
"""

import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, Any

# 模拟 Hermes 调用（实际运行时替换为真实调用）
def call_hermes_summarize(conversation: str, model: str = "claude-3-haiku") -> Dict[str, Any]:
    """
    调用 Hermes 生成摘要
    
    在实际 Hermes 环境中，这会调用 delegate_task
    在独立环境中，这可以调用远程 Hermes API
    """
    
    # TODO: 在实际 Hermes 环境中替换为:
    # from hermes_tools import delegate_task
    # result = delegate_task(
    #     goal="生成结构化摘要（JSON 格式）",
    #     context=conversation
    # )
    
    # 模拟响应（用于测试）
    return {
        "success": True,
        "summary": "讨论了 Python 异步编程和性能优化",
        "key_points": [
            "async/await 语法",
            "事件循环机制",
            "性能提升 3 倍"
        ],
        "action_items": [
            "学习 asyncio 库",
            "重构现有代码为异步"
        ],
        "model_used": model,
        "tokens_saved": len(conversation) // 4
    }


class InfinityContextHandler(BaseHTTPRequestHandler):
    """HTTP 请求处理器"""
    
    def do_POST(self):
        """处理 POST 请求（生成摘要）"""
        
        # 读取请求体
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
            return
        
        # 提取对话内容
        conversation = data.get('conversation', '')
        model = data.get('model', 'claude-3-haiku')
        
        if not conversation:
            self.send_error(400, "Missing 'conversation' field")
            return
        
        # 调用 Hermes 生成摘要
        print(f"📝 收到摘要请求：{len(conversation)} 字符")
        result = call_hermes_summarize(conversation, model)
        
        # 返回 JSON 响应
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = json.dumps(result, ensure_ascii=False, indent=2)
        self.wfile.write(response.encode('utf-8'))
        
        print(f"✅ 摘要生成成功：{result['summary'][:50]}...")
    
    def do_GET(self):
        """处理 GET 请求（健康检查）"""
        
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "ok", "service": "infinity-context-api"}')
        
        elif self.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Infinity Context API</title>
                <style>
                    body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; }
                    h1 { color: #2563eb; }
                    code { background: #f3f4f6; padding: 2px 6px; border-radius: 3px; }
                    .endpoint { background: #eff6ff; padding: 15px; border-radius: 5px; margin: 10px 0; }
                </style>
            </head>
            <body>
                <h1>🔄 Infinity Context API</h1>
                <p><strong>让小模型也能使用无限上下文！</strong></p>
                
                <h2>📋 端点</h2>
                
                <div class="endpoint">
                    <h3>POST /summarize</h3>
                    <p>生成会话摘要</p>
                    <p><strong>请求:</strong></p>
                    <pre><code>{
  "conversation": "用户：你好\\n助手：你好！有什么可以帮助你的？",
  "model": "claude-3-haiku"
}</code></pre>
                    <p><strong>响应:</strong></p>
                    <pre><code>{
  "success": true,
  "summary": "讨论了问候和初始对话",
  "key_points": ["问候", "初始对话"],
  "action_items": [],
  "model_used": "claude-3-haiku",
  "tokens_saved": 50
}</code></pre>
                </div>
                
                <div class="endpoint">
                    <h3>GET /health</h3>
                    <p>健康检查</p>
                    <p><strong>响应:</strong> <code>{"status": "ok"}</code></p>
                </div>
                
                <h2>🚀 使用示例</h2>
                
                <h3>cURL</h3>
                <pre><code>curl -X POST http://localhost:8765/summarize \\
  -H "Content-Type: application/json" \\
  -d '{"conversation": "用户：你好", "model": "claude-3-haiku"}'</code></pre>
                
                <h3>Python</h3>
                <pre><code>import requests

response = requests.post(
    "http://localhost:8765/summarize",
    json={
        "conversation": "用户：你好\\n助手：你好！",
        "model": "claude-3-haiku"
    }
)
print(response.json())</code></pre>
                
                <h3>Llama-3-8B (本地小模型)</h3>
                <pre><code># 在你的小模型代码中
import requests

def summarize_with_hermes(conversation):
    response = requests.post(
        "http://your-server:8765/summarize",
        json={"conversation": conversation}
    )
    return response.json()["summary"]

# 小模型只负责对话，摘要交给 Hermes
conversation = get_recent_messages()
summary = summarize_with_hermes(conversation)
continue_conversation(summary)</code></pre>
                
                <hr>
                <p><em>"Small model, Long context" - Infinity Context v1.1.0</em></p>
            </body>
            </html>
            """
            self.wfile.write(html.encode('utf-8'))
        
        else:
            self.send_error(404, "Not Found")
    
    def log_message(self, format, *args):
        """自定义日志格式"""
        print(f"[{self.log_date_time_string()}] {format % args}")


def run_server(port=8765, host='0.0.0.0'):
    """启动 HTTP 服务器"""
    
    server_address = (host, port)
    httpd = HTTPServer(server_address, InfinityContextHandler)
    
    print("=" * 60)
    print("🌐 Infinity Context API Server")
    print("=" * 60)
    print(f"📍 监听地址：http://{host}:{port}")
    print(f"📋 健康检查：http://{host}:{port}/health")
    print(f"📝 摘要接口：http://{host}:{port}/summarize (POST)")
    print("=" * 60)
    print("")
    print("💡 使用方式:")
    print("  小模型 → HTTP POST → Infinity Context API → Hermes → 返回摘要")
    print("")
    print("🚀 示例请求:")
    print('  curl -X POST http://localhost:8765/summarize \\')
    print('    -H "Content-Type: application/json" \\')
    print('    -d \'{"conversation": "用户：你好", "model": "claude-3-haiku"}\'')
    print("=" * 60)
    print("")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n⚠️  服务器已停止")
        httpd.server_close()


if __name__ == "__main__":
    # 从环境变量读取配置
    port = int(os.getenv("INFINITY_CONTEXT_PORT", "8765"))
    host = os.getenv("INFINITY_CONTEXT_HOST", "0.0.0.0")
    
    run_server(port, host)
