# Python Services

DataForge AI 的 Python 服务模块，包含 RAG 服务、API 和配置管理。

## 服务列表

- **RAG API**: FastAPI 实现的 RAG 查询服务
- **Config Service**: 统一配置管理
- **Monitoring**: Prometheus 指标导出

## 开发

```bash
# 安装依赖
uv sync

# 运行测试
uv run pytest

# 启动服务
uv run python -m dataforge_ai.rag.api
```

## 依赖

详见 `pyproject.toml`
