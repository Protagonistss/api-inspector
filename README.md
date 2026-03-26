# API Inspector

基于 mitmproxy 的网络请求抓取工具，用于开发调试。

## 功能特性

- **HTTP/HTTPS 请求捕获**：完整捕获请求和响应信息
- **WebSocket 支持**：捕获 WebSocket 连接和消息
- **灵活的过滤**：支持按域名、方法、状态码、内容类型过滤
- **多种输出格式**：表格、详细模式、JSON 格式
- **终端美化**：使用 Rich 库实现语法高亮和彩色输出

## 安装

```bash
pip install -e .
```

## 快速开始

### 1. 启动代理

```bash
# 默认端口 8080
api-inspector start

# 指定端口
api-inspector start --port 8888

# 后台运行（仅显示 JSON 输出）
api-inspector start --json
```

### 2. 配置系统代理

**Windows:**
```
设置 -> 网络 -> 代理 -> 手动设置代理
HTTP 代理: 127.0.0.1:8080
HTTPS 代理: 127.0.0.1:8080
```

**macOS/Linux:**
```bash
export http_proxy=http://127.0.0.1:8080
export https_proxy=http://127.0.0.1:8080
```

### 3. HTTPS 证书安装

首次使用 HTTPS 抓取需要安装证书：

```bash
# 查看证书信息
api-inspector certs
```

**Windows:**
```bash
certutil -addstore root ~/.mitmproxy/mitmproxy-ca-cert.pem
```

**macOS:**
打开 `~/.mitmproxy/mitmproxy-ca-cert.pem` 并添加到钥匙串，设为"始终信任"

**Linux (Ubuntu/Debian):**
```bash
sudo cp ~/.mitmproxy/mitmproxy-ca-cert.pem /usr/local/share/ca-certificates/mitmproxy.crt
sudo update-ca-certificates
```

## 使用示例

### 过滤请求

```bash
# 只捕获特定域名
api-inspector start --filter "api.example.com"

# 支持通配符
api-inspector start --filter "api.*.com"

# 只看 POST 请求
api-inspector start --method POST

# 多个过滤条件
api-inspector start --method POST --method PUT --filter "api.example.com"
```

### 输出格式

```bash
# 详细模式（显示完整请求体）
api-inspector start --verbose

# JSON 输出（便于日志记录和处理）
api-inspector start --json

# 禁用颜色
api-inspector start --no-color
```

### 按状态码过滤

```bash
# 只看 200 响应
api-inspector start --status-code 200

# 只看错误响应
api-inspector start --status-code 400 --status-code 500
```

### 按内容类型过滤

```bash
# 只看 JSON 响应
api-inspector start --content-type json

# 只看 HTML
api-inspector start --content-type html
```

## 输出示例

```
10:01:23 | POST | https://api.example.com/users | 201 | 256B | 45ms
10:01:25 | GET  | https://api.example.com/users/1 | 200 | 128B | 12ms
10:01:30 | WS   | wss://ws.example.com/chat | → {"type":"ping"}
10:01:31 | WS   | wss://ws.example.com/chat | ← {"type":"pong"}
```

详细模式示例：

```
10:01:23 | POST | https://api.example.com/users | 201 | 256B | 45ms

Request:
  Headers:
    Content-Type: application/json
    Authorization: Bearer xxx...

  Body:
    {"name": "John", "email": "john@example.com"}

Response: 201
  Headers:
    Content-Type: application/json

  Body:
    {
      "id": 1,
      "name": "John",
      "email": "john@example.com"
    }
```

## 命令行选项

| 选项 | 简写 | 描述 |
|------|------|------|
| `--port` | `-p` | 代理端口（默认 8080） |
| `--host` | `-h` | 代理主机（默认 127.0.0.1） |
| `--filter` | `-f` | URL 过滤模式（支持通配符） |
| `--method` | `-m` | HTTP 方法过滤 |
| `--status-code` | `-s` | 状态码过滤 |
| `--content-type` | `-c` | 内容类型过滤 |
| `--json` | | JSON 输出格式 |
| `--verbose` | `-V` | 详细输出模式 |
| `--no-color` | | 禁用颜色输出 |
| `--version` | `-v` | 显示版本号 |

## 技术栈

- Python 3.10+
- [mitmproxy](https://mitmproxy.org/) - 代理引擎
- [Rich](https://github.com/Textualize/rich) - 终端美化
- [Click](https://click.palletsprojects.com/) - CLI 框架

## 开发

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest
```

## License

MIT
