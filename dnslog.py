import datetime
import threading
import os
from flask import Flask, render_template_string, make_response, request, redirect, url_for
from dnslib import DNSRecord, QTYPE, RR, A
from dnslib.server import DNSServer, BaseResolver, DNSLogger

app = Flask(__name__)

# ====================== 配置 ======================
DOMAIN = os.getenv('DNSLOG_DOMAIN', 'log.rcs-team.com')  # 支持环境变量修改域名
dns_logs = []  # 内存存储


class CustomResolver(BaseResolver):
    def resolve(self, request, handler):
        qname = str(request.q.qname)
        client_ip = handler.client_address[0]
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if qname.endswith(f"{DOMAIN}.") or qname == f"{DOMAIN}.":
            dns_logs.append({
                'time': current_time,
                'client_ip': client_ip,
                'query': qname.rstrip('.')
            })
            if len(dns_logs) > 1000:
                dns_logs.pop(0)

        reply = request.reply()
        if request.q.qtype == QTYPE.A:
            reply.add_answer(RR(qname, QTYPE.A, rdata=A("127.0.0.1"), ttl=60))
        return reply


def start_dns_server():
    resolver = CustomResolver()
    logger = DNSLogger(log="request,reply,error")
    server = DNSServer(resolver, port=53, address="0.0.0.0", logger=logger)
    print(f"🚀 DNS Server 启动成功 | 监听端口 53 | 目标域名: {DOMAIN}")
    server.start_thread()


# ====================== 美化后的 HTML 模板 ======================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="3">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DNSLog Server</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
    <style>
        body { background-color: #0f172a; color: #e2e8f0; }
        table { border-collapse: separate; border-spacing: 0; }
        tr:hover { background-color: #1e2937 !important; }
        .copy-btn { transition: all 0.2s; }
        .copy-btn:hover { transform: scale(1.1); }
    </style>
</head>
<body class="min-h-screen">
    <div class="max-w-6xl mx-auto p-6">
        <!-- Header -->
        <div class="flex items-center justify-between mb-8">
            <div>
                <h1 class="text-4xl font-bold flex items-center gap-3">
                    <i class="fa-solid fa-globe text-emerald-400"></i>
                    DNSLog Server
                </h1>
                <p class="text-emerald-400 mt-1">目标域名: <span class="font-mono bg-slate-800 px-3 py-1 rounded">{{ domain }}</span></p>
            </div>
            <div class="flex items-center gap-4">
                <div class="bg-slate-800 px-6 py-3 rounded-2xl text-center">
                    <div class="text-3xl font-bold text-emerald-400">{{ logs|length }}</div>
                    <div class="text-xs text-slate-400">总记录数</div>
                </div>
                <button onclick="clearLogs()" 
                        class="bg-red-500 hover:bg-red-600 px-6 py-3 rounded-2xl font-medium flex items-center gap-2 transition">
                    <i class="fa-solid fa-trash"></i> 清空记录
                </button>
            </div>
        </div>

        <!-- Search -->
        <div class="mb-6">
            <input type="text" id="searchInput" 
                   onkeyup="filterTable()" 
                   placeholder="🔍 搜索 IP 或 Query..." 
                   class="w-full bg-slate-800 border border-slate-700 rounded-3xl px-6 py-4 text-lg focus:outline-none focus:border-emerald-500">
        </div>

        <!-- Table -->
        <div class="bg-slate-900 rounded-3xl overflow-hidden shadow-2xl">
            <table class="w-full">
                <thead>
                    <tr class="bg-slate-800">
                        <th class="px-8 py-5 text-left text-sm font-medium text-slate-400">时间</th>
                        <th class="px-8 py-5 text-left text-sm font-medium text-slate-400">Client IP</th>
                        <th class="px-8 py-5 text-left text-sm font-medium text-slate-400">Query</th>
                        <th class="w-24"></th>
                    </tr>
                </thead>
                <tbody id="logTable" class="text-sm">
                    {% for log in logs|reverse %}
                    <tr class="border-t border-slate-700 hover:bg-slate-800 transition">
                        <td class="px-8 py-5 font-mono">{{ log.time }}</td>
                        <td class="px-8 py-5 font-mono">{{ log.client_ip }}</td>
                        <td class="px-8 py-5 font-mono">{{ log.query }}</td>
                        <td class="px-8 py-5">
                            <button onclick="copyToClipboard('{{ log.client_ip }}')" 
                                    class="copy-btn text-emerald-400 hover:text-emerald-300">
                                <i class="fa-solid fa-copy"></i>
                            </button>
                        </td>
                    </tr>
                    {% else %}
                    <tr>
                        <td colspan="4" class="px-8 py-20 text-center">
                            <i class="fa-solid fa-inbox text-6xl text-slate-700 mb-4"></i>
                            <p class="text-slate-400">暂无记录，快去打个 DNS 请求试试吧～</p>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <div class="text-center text-slate-500 text-xs mt-8">
            Powered by Flask + dnslib | 单文件美化版 | 每 3 秒自动刷新
        </div>
    </div>

    <script>
        function filterTable() {
            const input = document.getElementById('searchInput').value.toLowerCase();
            const rows = document.querySelectorAll('#logTable tr');
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(input) ? '' : 'none';
            });
        }

        function copyToClipboard(text) {
            navigator.clipboard.writeText(text);
            const btn = event.currentTarget;
            const original = btn.innerHTML;
            btn.innerHTML = '<i class="fa-solid fa-check"></i>';
            setTimeout(() => btn.innerHTML = original, 1500);
        }

        function clearLogs() {
            if (confirm('确定要清空所有记录吗？')) {
                window.location.href = '/clear';
            }
        }

        // Tailwind 初始化
        tailwind.config = { content: ["*"], theme: { extend: {} } }
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    resp = make_response(render_template_string(HTML_TEMPLATE, logs=dns_logs, domain=DOMAIN))
    resp.headers['Cache-Control'] = 'no-store'
    return resp


@app.route('/clear')
def clear():
    dns_logs.clear()
    return redirect(url_for('index'))


if __name__ == '__main__':
    dns_thread = threading.Thread(target=start_dns_server, daemon=True)
    dns_thread.start()

    print("🌐 Web UI 启动成功 | 访问 http://你的IP:80")
    app.run(host='0.0.0.0', port=80)