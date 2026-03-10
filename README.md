# 🚀 DNSLog Server（单文件美化版）

一个**超级好看**的 DNS 日志服务器，专门用于渗透测试、漏洞验证、打点记录、外网接收 DNS 出网等场景。

![界面预览](https://github.com/nuoy58053-byte/dnslog/raw/main/preview.png)  
（上传完后记得把截图改名 preview.png 放仓库里就能显示）

### ✨ 特性
- **现代深色 UI**（Tailwind CSS + 响应式）
- 实时搜索、记录统计、一键复制 IP
- 每 3 秒自动刷新
- 支持环境变量修改目标域名
- **完全单文件**（只需 dnslog.py，无需额外文件）
- Docker 一键部署

### 🎯 使用方法

#### 1. Docker 快速启动（推荐）
```bash
docker run -d \
  -p 80:80 \
  -p 53:53/udp \
  --name dnslog \
  nuoy58053-byte/dnslog:latest
