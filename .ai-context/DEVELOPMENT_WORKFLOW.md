# 开发工作流与风险管理

## 核心原则

1. **接口优先**: 有数据交互的并行任务必须先定义接口
2. **测试驱动**: 每个任务完成后立即测试
3. **持续集成**: 每个任务完成后部署到测试环境验证
4. **增量交付**: 小步快跑，避免大批量集成

## 开发流程

### 1. 任务开始前

**对于有数据交互的任务**:

```bash
# 1. 检查依赖任务是否完成
make task-next

# 2. 如果有跨服务交互，先定义接口
# 创建接口文档: docs/api/[service-name].yaml (OpenAPI)
# 或: schemas/[entity-name].proto (Protocol Buffers)
```

**接口定义检查清单**:
- [ ] 请求/响应数据结构
- [ ] 错误码和错误处理
- [ ] 认证和授权方式
- [ ] 性能要求（延迟、吞吐量）
- [ ] 版本控制策略

### 2. 开发阶段

```bash
# 1. 创建功能分支
git checkout -b feature/T-XXX-task-name

# 2. 实现功能（遵循接口定义）

# 3. 编写单元测试
# Python: uv run pytest tests/
# Java: mvn test
# Scala: sbt test

# 4. 本地集成测试
make dev-minimal  # 启动依赖服务
# 运行集成测试
```

### 3. 任务完成后

```bash
# 1. 运行完整测试套件
make test-all

# 2. 代码质量检查
make lint
make type-check

# 3. 构建和打包
# Python: uv build
# Java: mvn package
# Scala: sbt assembly

# 4. 部署到测试环境
make deploy-test

# 5. 运行冒烟测试
make smoke-test

# 6. 更新任务状态
# 编辑 .ai-context/tasks/tasks.yaml
# 状态: 待处理 -> 已完成

# 7. 提交代码
git commit -m "[T-XXX] 完成任务描述"
git push origin feature/T-XXX-task-name
```

## 风险识别与应对

### 风险矩阵

| 风险 | 影响 | 概率 | 优先级 | 应对策略 |
|------|------|------|--------|---------|
| 接口不兼容 | 高 | 中 | P0 | 接口优先开发 + Contract Testing |
| 集成失败 | 高 | 中 | P0 | 增量集成 + 自动化测试 |
| 数据模型不一致 | 高 | 中 | P0 | Schema Registry + 数据验证 |
| 依赖冲突 | 中 | 高 | P1 | 依赖锁定 + 隔离环境 |
| 配置漂移 | 中 | 中 | P1 | 配置中心 + 验证 |
| 测试覆盖不足 | 高 | 中 | P0 | 测试金字塔 + 覆盖率要求 |
| 构建失败 | 中 | 低 | P2 | CI/CD + Docker |
| 性能问题 | 中 | 中 | P1 | 性能测试 + 监控 |
| 安全漏洞 | 高 | 低 | P1 | 安全扫描 + 审计 |
| 文档过时 | 低 | 高 | P2 | 文档即代码 + 自动生成 |

### P0 风险详细应对

#### 1. 接口不兼容

**场景**: Java Kafka Producer 和 Python Consumer 数据格式不匹配

**预防**:
```yaml
# schemas/message.yaml (OpenAPI Schema)
MessageSchema:
  type: object
  required: [id, timestamp, data]
  properties:
    id: {type: string, format: uuid}
    timestamp: {type: integer, format: int64}
    data: {type: object}
```

**检测**:
- Contract Testing (Pact, Spring Cloud Contract)
- Schema Validation (JSON Schema, Avro)

**修复**:
- 版本化接口 (v1, v2)
- 向后兼容的变更

#### 2. 集成失败

**场景**: Spark 作业输出格式与 Flink 作业输入格式不匹配

**预防**:
```bash
# 定义数据格式
docs/data-formats/training-data.md
docs/data-formats/rag-documents.md
```

**检测**:
- 端到端集成测试
- 数据管道验证

**修复**:
- 数据转换层
- 格式适配器

#### 3. 数据模型不一致

**场景**: Python 使用 snake_case，Java 使用 camelCase

**预防**:
```python
# 统一数据模型定义
# schemas/entities.py
from pydantic import BaseModel, Field

class Document(BaseModel):
    document_id: str = Field(alias="documentId")
    created_at: int = Field(alias="createdAt")

    class Config:
        populate_by_name = True  # 支持两种命名
```

**检测**:
- Schema 验证
- 序列化/反序列化测试

**修复**:
- 统一命名约定
- 自动转换层

### P1 风险详细应对

#### 4. 依赖冲突

**预防**:
```bash
# Python
uv lock  # 锁定依赖版本

# Java
mvn dependency:tree  # 检查依赖树
mvn enforcer:enforce  # 强制依赖规则

# Scala
sbt dependencyTree
```

**检测**:
- CI 构建失败
- 依赖扫描工具

**修复**:
- 依赖排除
- 版本对齐

#### 5. 配置漂移

**预防**:
```yaml
# config/validation-schema.yaml
kafka:
  bootstrap_servers:
    type: string
    pattern: "^[a-z0-9.-]+:[0-9]+$"
    required: true
```

**检测**:
- 配置验证脚本
- 启动时验证

**修复**:
- 配置同步
- 环境变量标准化

#### 6. 测试覆盖不足

**要求**:
- 单元测试覆盖率 >= 80%
- 关键路径必��有集成测试
- 每个 API 端点必须有测试

**检测**:
```bash
# Python
uv run pytest --cov=src --cov-report=html
# 检查 htmlcov/index.html

# Java
mvn jacoco:report
# 检查 target/site/jacoco/index.html
```

**修复**:
- 补充测试用例
- 重构提高可测试性

## 测试策略

### 测试金字塔

```
        /\
       /E2E\      <- 少量端到端测试 (5%)
      /------\
     /  集成  \    <- 适量集成测试 (15%)
    /----------\
   /   单元测试  \  <- 大量单元测试 (80%)
  /--------------\
```

### 测试类型

| 测试类型 | 工具 | 运行时机 | 目标 |
|---------|------|---------|------|
| 单元测试 | pytest, JUnit, ScalaTest | 每次提交 | 函数/类级别 |
| 集成测试 | pytest, TestContainers | 每次提交 | 模块间交互 |
| Contract 测试 | Pact | 接口变更时 | API 兼容性 |
| E2E 测试 | pytest, Selenium | 每日/发布前 | 完整流程 |
| 性能测试 | Locust, JMeter | 每周/发布前 | 性能指标 |
| 安全测试 | Bandit, OWASP ZAP | 每周 | 安全漏洞 |

### 测试环境

```bash
# 本地开发环境
make dev-minimal

# 集成测试环境
make dev-integration

# 性能测试环境
make dev-performance
```

## 部署策略

### 环境层级

1. **Local**: 开发者本地环境
2. **Test**: 自动化测试环境
3. **Staging**: 预生产环境
4. **Production**: 生产环境

### 部署流程

```bash
# 1. 本地验证
make test-local
make build

# 2. 部署到 Test 环境
make deploy-test
make smoke-test

# 3. 部署到 Staging (手动触发)
make deploy-staging
make integration-test

# 4. 部署到 Production (需要审批)
make deploy-prod
make health-check
```

### 回滚策略

```bash
# 快速回滚到上一个版本
make rollback

# 回滚到指定版本
make rollback VERSION=v1.2.3
```

## 并行开发协调

### 接口优先开发流程

**场景**: T-101 (Kafka Producer) 和 T-103 (Kafka Consumer) 并行开发

**步骤**:

1. **定义消息格式** (Day 1)
```yaml
# schemas/kafka-messages.yaml
TrainingDataMessage:
  type: object
  properties:
    message_id: string
    timestamp: integer
    source: string
    content: string
    metadata: object
```

2. **生成代码** (Day 1)
```bash
# 从 schema 生成 Java/Python 代码
make generate-schemas
```

3. **并行开发** (Day 2-3)
- T-101: 实现 Producer，使用生成的消息类
- T-103: 实现 Consumer，使用生成的消息类

4. **Contract 测试** (Day 3)
```python
# tests/contract/test_kafka_messages.py
def test_producer_consumer_contract():
    # Producer 发送消息
    producer.send(message)

    # Consumer 接收并验证
    received = consumer.poll()
    assert validate_schema(received, TrainingDataMessage)
```

5. **集成测试** (Day 4)
```bash
make test-integration
```

### 依赖管理

**依赖图**:
```
T-101 (Producer) ─┐
                  ├─> T-201 (Spark Job)
T-103 (Consumer) ─┘

T-105 (Config) ───> T-201, T-103, T-101
```

**规则**:
- 被依赖的任务优先完成
- 接口定义必须在依赖任务开始前完成
- 使用 Mock 解除阻塞依赖

## 质量门禁

每个任务完成必须通过以下检查:

- [ ] 单元测试通过 (覆盖率 >= 80%)
- [ ] 集成测试通过
- [ ] 代码风格检查通过
- [ ] 类型检查通过 (Python, TypeScript)
- [ ] 安全扫描无高危漏洞
- [ ] 性能测试达标 (如适用)
- [ ] 文档已更新
- [ ] Code Review 通过

## 监控和告警

### 开发阶段监控

```bash
# 查看服务健康状态
make health-check

# 查看日志
make logs SERVICE=kafka

# 查看指标
make metrics
```

### 关键指标

- **构建成功率**: >= 95%
- **测试通过率**: 100%
- **代码覆盖率**: >= 80%
- **部署成功率**: >= 98%
- **平均修复时间**: < 4 小时

## 工具链

| 用途 | 工具 |
|------|------|
| 版本控制 | Git |
| CI/CD | GitHub Actions |
| 容器化 | Docker, Docker Compose |
| 依赖管理 | uv (Python), Maven (Java), sbt (Scala) |
| 测试 | pytest, JUnit, ScalaTest |
| 代码质量 | Black, Ruff, Checkstyle, Scalafmt |
| 安全扫描 | Bandit, OWASP Dependency Check |
| 监控 | Prometheus, Grafana |
| 日志 | ELK Stack |

## 最佳实践

1. **小步提交**: 每个任务拆分为多个小的可测试单元
2. **持续集成**: 每次提交触发 CI 构建
3. **自动化测试**: 所有测试自动化，无手动测试
4. **文档同步**: 代码和文档同步更新
5. **Code Review**: 所有代码必须经过 Review
6. **性能意识**: 关注性能指标，及时优化
7. **安全第一**: 安全扫描集成到 CI/CD

## 故障处理

### 常见问题

**问题**: 集成测试失败
**排查**:
1. 检查服务是否启动: `make docker-status`
2. 查看日志: `make docker-logs`
3. 验证配置: `make config-validate`
4. 重启服务: `make docker-restart`

**问题**: 依赖冲突
**排查**:
1. 查看依赖树: `mvn dependency:tree` / `uv tree`
2. 排除冲突依赖
3. 锁定版本

**问题**: 性能下降
**排查**:
1. 运行性能测试: `make perf-test`
2. 查看监控指标: `make metrics`
3. 分析瓶颈
4. 优化代码

## 参考资料

- [测试金字塔](https://martinfowler.com/articles/practical-test-pyramid.html)
- [Contract Testing](https://pact.io/)
- [Continuous Integration](https://martinfowler.com/articles/continuousIntegration.html)
