# FinPilot — Product & Engineering Development Plan

Version: 1.0  
Project Type: Cross-platform AI Financial Research Application  
Target Platforms: iOS, Android  
Development Approach: Incremental, Modular, Test-driven

---

## 1. Project Overview

### 1.1 项目目标

开发一款极简、低成本、可扩展的 AI 金融研究 APP，提供：

- 股票行情及历史数据查询。
- 金融数学模型及股票价格概率预测。
- 公司基本面分析及估值。
- AI Agent 自由聊天与金融研究。
- 个人持仓及投资风险管理。
- 每日市场报告及自动推送。
- 用户自定义价格及风险提醒。

系统旨在辅助投资研究与决策，而不是保证投资收益或自动执行股票交易。

### 1.2 初期项目范围

- 优先支持美国股票市场。
- 支持 iOS 和 Android。
- 使用免费金融数据及开源数学模型。
- 优先满足个人使用需求。
- 为未来多用户及商业化保留必要的扩展能力。
- 不开发自动交易功能。
- 不开发高频交易功能。
- 不提前引入复杂微服务架构。

---

## 2. Core Development Principles

### 2.1 Design Philosophy

**Make everything as clean as Linear or Apple Notes.**

Simple goals. Simple architecture. Simple design. Simple implementation.

所有产品及工程决策必须遵守以下原则：

1. 目标简单：每项功能解决一个明确的问题。
2. 架构简单：不引入没有实际需求的技术组件。
3. 设计简单：优先通过布局、层级及交互表达信息。
4. 实现简单：选择满足需求的最直接、可靠且可维护的实现方式。

删除不必要的标语、解释性文字、提示文字、装饰性标签及重复信息。

如果一个页面必须依赖大量文字才能让用户理解其用途，应优先重新设计布局，而不是增加说明。

但不得为了视觉简洁而删除必要的错误反馈、无障碍信息、数据来源、风险提示及法律要求的信息。

### 2.2 UX / DX / AX

每项设计和工程决策都必须同时考虑以下三个维度。

**UX — User Experience**

- 用户能够快速理解功能。
- 减少操作步骤及认知负担。
- 保持页面响应迅速。
- 提供一致的交互方式。
- 不展示没有实际价值的信息。

**DX — Developer Experience**

- 清晰的项目目录及模块边界。
- 类型安全、命名一致。
- 简单的本地开发环境。
- 可复现的安装及部署过程。
- 容易测试、调试和维护。
- 避免重复实现及无意义抽象。

**AX — Agent Experience**

- AI Coding Agent 能快速理解项目结构。
- 每个模块具有明确的职责。
- API、数据结构及业务规则有明确契约。
- 项目文档与实际代码保持一致。
- 工具调用使用结构化输入和输出。
- Agent 不需要猜测已有功能、数据库结构或业务逻辑。

每个决定都应尽可能同时改善 UX、DX 和 AX。

若三者存在无法避免的冲突，必须明确记录原因及取舍，不得为了其中一个维度而无意破坏另一个维度。

### 2.3 Do Not Break Anything

禁止为了实现新功能而破坏已经正常运行的功能。

每次修改必须：

- 先理解现有实现及依赖关系。
- 确认修改范围及影响范围。
- 保持已有 API 和数据的兼容性。
- 添加必要的自动化测试。
- 执行相关测试及回归测试。
- 更新受影响的文档。
- 保证数据库迁移可安全执行。
- 提供可行的回滚方案。

未经批准，不允许删除已有功能、修改核心架构或进行大范围重构。

### 2.4 YAGNI / KISS / DRY

- **YAGNI:** 不提前开发尚未需要的功能。
- **KISS:** 优先选择简单可靠的解决方案。
- **DRY:** 避免重复业务逻辑，但不进行过早抽象。

不得仅为了采用某种技术而引入该技术。

不得为了未来可能出现的需求而过度设计当前系统。

---

## 3. Technical Architecture

### 3.1 Technology Stack

| Component | Technology |
|---|---|
| Mobile Application | React Native + Expo |
| Language | TypeScript / Python |
| Navigation | Expo Router |
| Server State | TanStack Query |
| Local State | React Context / Zustand（按需） |
| Backend | FastAPI |
| API Validation | Pydantic |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Database Migration | Alembic |
| Quantitative Analysis | NumPy, SciPy, pandas, arch |
| AI Agent | LangGraph |
| LLM Integration | OpenAI-compatible API |
| Background Tasks | Python Scheduler / Worker |
| Push Notifications | Expo Notifications |
| Containerisation | Docker Compose |
| Testing | pytest / Vitest / React Native Testing Library |
| CI/CD | GitHub Actions |

Redis、Celery、n8n、pgvector 等组件仅在现有实现无法满足明确需求时引入。

### 3.2 Architecture

采用 Modular Monolith，而非 Microservices。

```text
iOS / Android
      |
      v
   FastAPI
      |
      +-- Market Data
      +-- Financial Research
      +-- Quant Engine
      +-- Portfolio
      +-- AI Agent
      +-- Notifications
      |
      v
  PostgreSQL

Background Worker
      |
      +-- Data Synchronisation
      +-- Model Execution
      +-- Report Generation
      +-- Alert Evaluation
      +-- Push Delivery
```

架构要求：

- Mobile APP 不直接访问数据库。
- Mobile APP 不包含服务端 LLM API Key。
- 数据供应商通过统一接口接入。
- 数学模型不依赖 UI 或 LLM。
- AI Agent 通过明确的工具接口获取数据。
- 所有金融计算集中在后端。
- 后台任务独立于 APP 生命周期运行。
- 不允许循环模块依赖。

### 3.3 Data Providers

| Data | Initial Provider |
|---|---|
| Historical Stock Prices | Tiingo Starter |
| Daily Stock Prices | Tiingo Starter |
| Company Filings | SEC EDGAR |
| Financial Statements | SEC Company Facts |
| Macroeconomic Data | FRED |
| Exchange Rates | 经授权的免费汇率数据源 |
| Company Announcements | Company Investor Relations |
| News | 经授权的新闻来源 |
| AI Inference | Local LLM / Hosted LLM |

数据源必须可替换。

个人开发阶段使用个人 API 凭证。商业化前必须确认数据展示、存储、衍生分析、AI 处理及推送授权。

---

## 4. Product Design

### 4.1 Navigation

底部导航只保留四个主要页面：

| Page | Responsibility |
|---|---|
| Home | 市场概览、自选股、每日报告 |
| Research | 股票详情、估值、预测及研究 |
| AI | 自由聊天与金融研究 |
| Portfolio | 持仓、交易记录及风险 |

Notifications 和 Settings 通过顶部入口访问，不单独占用底部导航。

### 4.2 Visual Design Rules

参考 Linear 和 Apple Notes 的设计语言，但不直接复制其品牌资产。

- 大量合理留白。
- 清晰的信息层级。
- 统一字体、颜色、间距及圆角。
- 支持 Light Mode 和 Dark Mode。
- 优先使用原生交互模式。
- 不使用无意义渐变。
- 不使用装饰性卡片堆叠。
- 不使用营销标语。
- 不添加重复的 Section Subtitle。
- 不为普通信息添加 Badge。
- 不使用无意义动画。
- 不在同一页面重复展示相同数据。
- 涨跌信息不能仅通过颜色表达。
- 颜色主要用于状态、风险和交互反馈。

### 4.3 Interaction Rules

- 每个页面具有一个明确的主要目的。
- 每项常用操作应尽可能在少量步骤内完成。
- 优先展示结果，而不是功能介绍。
- Loading、Empty、Error、Offline 状态必须明确。
- 不使用虚假实时数据或虚构预测结果填充界面。
- 删除数据等不可逆操作必须得到确认。
- 所有行情及预测必须具有数据更新时间。

---

# 5. Development Roadmap

## Phase 0 — Project Foundation

### Objective

建立稳定、简单、可持续开发的项目基础。

### Development Tasks

- 初始化 Git Repository。
- 创建 React Native Expo 项目。
- 创建 FastAPI 项目。
- 配置 PostgreSQL。
- 配置 SQLAlchemy 和 Alembic。
- 配置环境变量。
- 创建 Docker Compose。
- 建立开发、测试及生产环境配置。
- 创建 Health Check API。
- 配置代码格式化及 Lint。
- 配置基础 CI。
- 建立项目文档。
- 配置统一设计变量 Design Tokens。
- 建立四个空白导航页面。

### Deliverables

- `README.md`
- `PLAN.md`
- `AGENTS.md`
- `.env.example`
- `docker-compose.yml`
- Initial database migration
- Mobile application shell
- Backend health endpoint

### Acceptance Criteria

- 一条明确的命令可以启动本地后端服务。
- iOS 和 Android 可以正常启动 APP。
- APP 能够连接 FastAPI。
- 数据库连接及迁移正常。
- CI 能够自动运行基础检查。
- Repository 不包含任何真实 Secret。
- 不包含虚假的业务数据。

---

## Phase 1 — Market Data Foundation

### Objective

建立可靠的股票数据获取和存储系统。

### Development Tasks

1. 建立 Market Data Provider Interface。
2. 实现 Tiingo Provider。
3. 支持股票 Symbol 查询。
4. 获取股票基础信息。
5. 获取每日 OHLCV 数据。
6. 获取历史股价数据。
7. 处理股票拆分及分红调整。
8. 将数据存储至 PostgreSQL。
9. 实现历史数据增量更新。
10. 实现 API 请求限流。
11. 实现错误重试及超时处理。
12. 实现数据完整性检查。
13. 保存数据来源及更新时间。
14. 建立自选股功能。

### Tiingo Starter Constraints

- Maximum unique symbols: 500/month.
- Maximum requests: 50/hour.
- Maximum requests: 1,000/day.
- Maximum bandwidth: 1GB/month.

系统必须能够配置及监控这些限制，而不是将限制硬编码到各个业务模块中。

### Core APIs

```text
GET /api/v1/market/search
GET /api/v1/market/stocks/{symbol}
GET /api/v1/market/stocks/{symbol}/history

GET    /api/v1/watchlist
POST   /api/v1/watchlist
DELETE /api/v1/watchlist/{symbol}
```

### Mobile Features

- 股票搜索。
- 添加及删除自选股。
- 自选股价格列表。
- 股票基础信息页面。
- 历史价格走势图。
- 时间范围切换。

### Acceptance Criteria

- NVDA 等美股能够正确搜索。
- 历史数据能够正常获取及存储。
- 重复同步不会产生重复数据。
- APP 刷新不会产生不必要的外部 API 请求。
- API 额度耗尽时能够安全降级。
- 数据来源及更新时间正确显示。
- 不将每日收盘价标记为实时行情。

---

## Phase 2 — Financial Fundamentals

### Objective

建立独立、可靠的公司基本面研究模块。

### Development Tasks

- 接入 SEC EDGAR。
- 建立 Ticker-to-CIK Mapping。
- 获取 10-K、10-Q 和 8-K 文件索引。
- 获取 SEC Company Facts。
- 解析及标准化财务指标。
- 保存财报发布日期及报告周期。
- 处理修订财报及重复财务记录。
- 计算基础财务比率。
- 建立财务趋势数据。
- 建立财报事件时间线。

### Financial Metrics

- Revenue
- Gross Profit
- Gross Margin
- Operating Income
- Operating Margin
- Net Income
- EPS
- Free Cash Flow
- Cash and Debt
- Shares Outstanding
- Revenue Growth
- Earnings Growth
- P/E Ratio
- Price-to-FCF Ratio

### Mobile Features

股票详情页面增加 Fundamentals Section：

- 核心财务指标。
- 营收及利润趋势。
- 现金流趋势。
- 历史财报。
- 财务数据来源。

### Acceptance Criteria

- 财务指标能够追溯至原始财报。
- 季度及年度数据不会被错误混合。
- 财报发布日期与报告周期明确区分。
- 不将缺失数据默认为零。
- 不使用未来发布的财报进行历史回测。
- 财务计算拥有独立单元测试。

---

## Phase 3 — Valuation Engine

### Objective

提供可解释、可调整的股票估值分析。

### Development Tasks

#### Model 1 — Discounted Cash Flow

- 读取历史自由现金流。
- 支持未来现金流增长率。
- 支持多阶段增长模型。
- 支持折现率。
- 支持永续增长率。
- 计算企业价值及股权价值。
- 计算每股理论价值。
- 生成敏感性分析。

#### Model 2 — Reverse DCF

- 输入当前市场价格。
- 反推市场隐含增长率。
- 比较历史增长率。
- 展示估值所依赖的增长假设。

#### Model 3 — Relative Valuation

- 历史 P/E 对比。
- Historical Price-to-FCF。
- Peer Comparison。
- 可比公司估值区间。

### Mobile Features

Research 页面增加 Valuation Section：

- 当前市场价格。
- 模型估值区间。
- Bear / Base / Bull Scenarios。
- 可调整的估值参数。
- 敏感性分析。
- 模型运行时间及数据来源。

### Acceptance Criteria

- 相同数据及参数产生可复现的结果。
- 用户可以查看及修改模型假设。
- 模型可以识别无效输入。
- 折现率及永续增长率符合数学约束。
- 估值结果不是确定的未来目标价格。
- LLM 不参与实际数学计算。
- 每种估值模型拥有独立测试。

---

## Phase 4 — Quantitative Forecast Engine

### Objective

通过统计模型估算未来股票价格分布及风险，而不是提供没有依据的单点价格预测。

### Development Tasks

#### Step 4.1 — Statistical Foundation

- 计算 Daily Log Returns。
- 计算 Historical Volatility。
- 计算 Rolling Volatility。
- 计算 Drawdown。
- 分析历史收益率分布。
- 检查异常值及数据质量。

#### Step 4.2 — Baseline Models

- Random Walk。
- Historical Bootstrap。
- Geometric Brownian Motion。

建立简单模型作为后续模型的比较基准。

#### Step 4.3 — Volatility Models

- GARCH(1,1)。
- Student-t Distribution。
- 动态波动率预测。
- 参数拟合及诊断。
- 模型拟合失败时的降级处理。

#### Step 4.4 — Monte Carlo Simulation

- 支持可配置的模拟路径数量。
- 默认模拟 10,000 条路径。
- 支持提高至 100,000 条路径。
- 支持不同预测周期。
- 计算价格分位数。
- 计算期末下跌概率。
- 计算期间触及目标价格的概率。
- 计算最大回撤分布。
- 保存随机种子及模型参数。

#### Step 4.5 — Advanced Models

只有基础模型经过验证之后，才考虑：

- Merton Jump Diffusion。
- EGARCH。
- Hidden Markov Model。
- Market Regime Detection。
- Ensemble Forecasting。

新增模型必须证明能够提供实际价值，不能仅增加技术复杂度。

### Forecast Horizons

- 7 trading days.
- 30 trading days.
- 90 trading days.
- 180 trading days.

### Forecast Outputs

- P5 / P25 / P50 / P75 / P95。
- Expected Return。
- Expected Volatility。
- Probability of Loss。
- Downside Probability。
- Price Barrier Hit Probability。
- VaR。
- CVaR。

### Mobile Features

- 价格预测扇形图。
- 预测周期切换。
- 预测价格区间。
- 下跌概率。
- 用户自定义目标价格概率。
- 模型参数。
- 模型历史表现。

### Acceptance Criteria

- 模型不依赖 LLM。
- 预测过程可以复现。
- 所有预测均保存生成时间及数据截止时间。
- 不覆盖历史预测。
- 明确区分期末概率与期间触及概率。
- 模型失败时不返回伪造结果。
- 模型没有通过验证时，不将其显示为可靠交易信号。

---

## Phase 5 — Backtesting & Model Evaluation

### Objective

建立客观的模型验证系统，判断预测是否真正有效。

### Development Tasks

- 建立历史预测回放机制。
- 实现 Walk-forward Testing。
- 实现 Out-of-Sample Testing。
- 防止 Look-ahead Bias。
- 防止 Data Leakage。
- 考虑 Survivorship Bias。
- 实现交易手续费模拟。
- 实现滑点模拟。
- 支持 AUD/USD 汇率影响。
- 保存模型版本及回测参数。
- 每日将真实结果与历史预测进行比较。

### Evaluation Metrics

| Type | Metrics |
|---|---|
| Price Accuracy | MAE, RMSE |
| Probability Accuracy | Brier Score, CRPS |
| Interval Accuracy | Prediction Interval Coverage |
| Direction Accuracy | Directional Accuracy |
| Strategy Performance | Total Return, CAGR |
| Risk | Max Drawdown, Sharpe, Sortino, CVaR |

### Benchmark Strategies

- Buy and Hold。
- Dollar Cost Averaging。
- Fixed Percentage Dip Buying。
- Random Walk Forecast。
- Historical Volatility Forecast。

### Acceptance Criteria

- 所有回测严格按照当时可获得的数据执行。
- 训练、验证及测试数据按时间顺序分离。
- 模型与简单基准进行比较。
- 保存失败及表现不佳的模型结果。
- 不通过选择性展示结果掩盖亏损。
- 无法证明高级模型优于基础模型时，优先使用基础模型。

---

## Phase 6 — Portfolio Management

### Objective

让用户能够记录真实持仓、现金储备及投资风险。

### Development Tasks

- 创建个人 Portfolio。
- 设置基础货币，默认 AUD。
- 手动记录买入及卖出。
- 记录交易价格及数量。
- 记录交易手续费。
- 记录交易时的汇率。
- 计算平均持仓成本。
- 计算已实现及未实现盈亏。
- 计算投资组合总价值。
- 记录现金余额。
- 计算资产配置及集中度。
- 计算投资组合波动率及风险。

### Position Scenario Simulator

支持用户设置：

- Total Investment Budget。
- Initial Position。
- Available Cash。
- Target Prices。
- Additional Investment Amounts。
- Maximum Exposure。
- Minimum Cash Reserve。

系统计算：

- 不同股价下的持仓价值。
- 加仓后的平均成本。
- 剩余现金。
- 潜在亏损。
- 风险敞口。
- 不同策略的模拟结果。

### Acceptance Criteria

- 资金金额使用 Decimal 或等效精确类型。
- 多币种计算具有明确汇率记录。
- 不允许重复计算交易。
- 交易修改能够正确更新持仓。
- Portfolio 与假设模拟相互独立。
- 模拟操作不会修改真实持仓。
- 不自动执行任何股票交易。

---

## Phase 7 — AI Financial Research Agent

### Objective

提供能够使用真实金融数据、数学模型及个人研究上下文的自由聊天 Agent。

### Architecture

一个主 Agent，多个专业工具。

不在第一版采用 Multi-Agent Swarm。

```text
User Query
    |
Investment Research Agent
    |
    +-- Market Tools
    +-- Financial Tools
    +-- Valuation Tools
    +-- Quant Tools
    +-- Portfolio Tools
    +-- Research Tools
    |
Evidence Validation
    |
Final Response
```

### Development Tasks

- 建立 LangGraph Agent。
- 实现 LLM Provider Interface。
- 支持 OpenAI-compatible API。
- 实现 Structured Tool Calling。
- 实现 SSE Streaming。
- 实现聊天记录保存。
- 实现上下文管理。
- 实现用户偏好及研究上下文。
- 实现工具超时及重试机制。
- 实现引用及数据来源展示。
- 实现 Token Usage Tracking。
- 实现 AI 请求成本监控。
- 实现 Prompt Injection 防护。
- 建立工具权限控制。

### Agent Tools

```text
get_stock_quote
get_stock_history
get_company_financials
get_company_filings
get_company_announcements
get_macro_indicators

calculate_dcf
calculate_reverse_dcf
get_valuation
get_price_forecast
get_downside_probability
get_price_barrier_probability
get_model_performance

get_portfolio
get_portfolio_risk
simulate_position_strategy

create_alert
list_alerts
```

### Agent Behaviour Rules

- 不允许编造实时股价。
- 不允许编造财报数据。
- 不允许自行生成未经计算的预测概率。
- 不允许将新闻推测描述为事实。
- 不允许隐藏模型的不确定性。
- 涉及具体数字时必须调用相关工具。
- 所有重要金融数据必须提供来源及时间。
- 数据不足时明确说明。
- 不允许通过自然语言绕过工具权限。
- 修改用户持仓等重要操作必须获得明确授权。
- 不执行股票交易。

### Mobile Features

- 类似 ChatGPT 的极简聊天页面。
- 流式回答。
- Markdown Rendering。
- Financial Data Cards。
- Forecast Charts。
- Source References。
- Conversation History。
- Stop Generation。
- Retry Response。

### Acceptance Criteria

- Agent 能查询指定股票行情。
- Agent 能调用数学模型。
- Agent 能结合用户持仓进行情景分析。
- Agent 不会将假设参数冒充真实数据。
- 工具失败时能够明确反馈。
- 聊天取消及重试不会造成重复写入。
- 每个工具具有输入输出 Schema。
- 对关键金融问题建立自动化 Agent Evaluation Dataset。

---

## Phase 8 — Automated Reports & Notifications

### Objective

让用户无需主动打开 APP，也能够获得重要市场信息。

### Development Tasks

#### Daily Market Report

- 检查美股交易日及交易时间。
- 更新自选股行情。
- 更新财务及重大公告。
- 运行预测模型。
- 更新模型表现。
- 生成结构化每日报告。
- 调用 LLM 生成简洁分析。
- 保存报告。
- 发送 Push Notification。

#### Price Alerts

- 用户自定义目标价格。
- Percentage Change Alert。
- Price Crossing Detection。
- 防止重复触发。
- Cooldown。
- Alert History。

#### Risk Alerts

- 波动率异常。
- 持仓集中度变化。
- 预测下行风险变化。
- 最大回撤阈值。

#### Earnings Alerts

- 财报发布日期提醒。
- 财报发布提醒。
- 核心财务指标变化。

### Notification Requirements

- 支持 APNs 及 FCM。
- 使用 Expo Push Notifications。
- 支持用户自定义通知时间。
- 默认时区 Australia/Melbourne。
- 自动处理夏令时。
- 支持通知开关。
- 支持 Deep Linking。
- 记录通知发送结果。
- 避免重复通知。
- APP 关闭后后台任务仍能运行。

### Default Schedule

| Job | Schedule |
|---|---|
| Market Data Sync | 每个美股交易日收盘后 |
| Forecast Update | 行情同步成功后 |
| Model Evaluation | 行情同步成功后 |
| Daily Report | 数据及模型更新成功后 |
| Daily Push | 用户设定时间 |
| Portfolio Review | 每周一次 |

### Acceptance Criteria

- 周末及休市日不会生成错误交易报告。
- 上游数据更新失败时不会发布虚假报告。
- 同一任务重复执行不会产生重复推送。
- 推送可以进入对应股票或报告页面。
- 延迟行情不会被描述为实时行情。
- 用户可以关闭任意非必要通知。

---

## Phase 9 — Authentication, Privacy & Security

### Objective

完成个人版到多用户系统的安全升级。

基础安全措施必须从 Phase 0 开始实施。本阶段负责完整的账户体系、用户数据隔离及安全加固。

### Development Tasks

- 用户注册及登录。
- Secure Session Management。
- Access Token / Refresh Token。
- Secure Mobile Credential Storage。
- 用户数据隔离。
- Portfolio Ownership Validation。
- User-specific Watchlists。
- User-specific Chat History。
- User-specific Notification Settings。
- API Rate Limiting。
- 数据加密。
- Secret Management。
- Audit Logging。
- Database Backup。
- Backup Restoration Testing。
- 用户数据导出。
- 用户账户及数据删除。

### BYOK Data Provider Support

- 用户配置自己的金融数据 API Key。
- API Key 加密保存。
- 后端不得向日志输出 API Key。
- 验证用户数据供应商权限。
- 支持凭证删除及替换。
- 用户之间禁止未经授权共享原始数据。
- 根据供应商条款控制缓存及衍生数据使用。

### Acceptance Criteria

- 用户无法访问其他用户的持仓、聊天或凭证。
- 敏感数据不会进入日志。
- Secret 不会进入 Git。
- 数据库备份能够恢复。
- 用户可以删除账户及相关数据。
- 所有受保护的 API 具有权限测试。
- 未通过安全检查前不得开放公众注册。

---

## Phase 10 — Deployment & Personal Release

### Objective

完成稳定的个人使用版本。

### Development Tasks

- 配置生产 Docker Compose。
- 配置 HTTPS。
- 配置域名及反向代理。
- 配置 PostgreSQL 持久化。
- 配置自动备份。
- 配置健康检查。
- 配置结构化日志。
- 配置后台任务监控。
- 配置 API Usage Monitoring。
- 配置 AI Cost Monitoring。
- 创建 Expo Production Build。
- 配置 Android 测试分发。
- 配置 iOS 测试分发。
- 完成真实设备测试。
- 完成部署文档。

### Acceptance Criteria

- iPhone 和 Android 真机可以正常使用。
- 手机关闭后仍可接收服务端推送。
- 服务重启不会丢失持仓及历史预测。
- 数据库可以恢复。
- 后端更新不会破坏当前 APP API。
- 生产错误可追踪。
- 用户不会看到调试日志。
- 运行成本可以监控。

---

## Phase 11 — Commercial Readiness

### Objective

在不重构核心架构的前提下，为未来商业化做好准备。

### Development Tasks

- 确认金融数据供应商授权。
- 确认 Developer Program / BYOK 权限。
- 审核第三方新闻及数据再利用权限。
- 审核 AI 衍生数据使用权限。
- 审核澳洲金融服务监管要求。
- 明确金融信息及个性化金融建议的产品边界。
- 建立 Privacy Policy。
- 建立 Terms of Service。
- 建立 Subscription System。
- 建立 Feature Entitlements。
- 建立 User Usage Quotas。
- 建立 Account Management。
- 建立 Cost Monitoring。
- 完成 App Store / Google Play 审核要求。

### Acceptance Criteria

- 具有明确且适用的数据商业使用授权。
- 产品功能经过必要的法律及隐私审查。
- 订阅状态与功能权限正确关联。
- 不允许一个个人 API Key 服务所有商业用户。
- 不依赖免责声明规避监管。
- 不影响已有个人版功能。

---

## 6. Database Design

### Core Tables

| Module | Tables |
|---|---|
| Authentication | users, sessions |
| Market | securities, market_prices, watchlists |
| Financials | financial_reports, financial_facts |
| Valuation | valuations, valuation_assumptions |
| Quant | model_runs, forecasts, forecast_quantiles |
| Evaluation | backtests, forecast_evaluations |
| Portfolio | portfolios, transactions, positions |
| AI | conversations, messages, tool_runs |
| Notifications | alerts, notification_events, devices |
| Reports | daily_reports |
| Providers | provider_credentials, provider_usage |
| System | job_runs, audit_logs |

数据库表必须按开发阶段逐步创建，不允许在 Phase 0 一次性创建所有未来业务表。

### Data Integrity Rules

- 使用明确的 Primary Key 和 Foreign Key。
- 使用合理的 Unique Constraints。
- 所有时间统一保存为 UTC。
- 交易日使用对应交易所的市场日期。
- 金额及持仓数量使用精确数值类型。
- 记录原始数据来源。
- 区分数据发生时间与系统获取时间。
- 重要金融数据及模型结果必须可追溯。
- 禁止直接覆盖历史预测结果。
- 用户私有数据必须遵守数据隔离规则。

---

## 7. Repository Structure

```text
finpilot/
├── apps/
│   └── mobile/
│       ├── app/
│       ├── components/
│       ├── features/
│       ├── hooks/
│       ├── services/
│       ├── theme/
│       └── types/
│
├── backend/
│   ├── app/
│   │   ├── core/
│   │   ├── market/
│   │   ├── financials/
│   │   ├── valuation/
│   │   ├── quant/
│   │   ├── evaluation/
│   │   ├── portfolio/
│   │   ├── agent/
│   │   ├── notifications/
│   │   ├── reports/
│   │   └── auth/
│   ├── migrations/
│   └── tests/
│
├── infrastructure/
├── experiments/
├── docs/
│   ├── architecture.md
│   ├── api.md
│   ├── data-sources.md
│   ├── models.md
│   └── decisions/
│
├── .github/
│   └── workflows/
│
├── AGENTS.md
├── PLAN.md
├── README.md
├── CHANGELOG.md
├── .env.example
└── docker-compose.yml
```

目录结构是目标结构。尚未开发的模块不需要提前创建空目录及空文件。

---

## 8. AI Coding Agent Development Rules

所有参与开发的 Coding Agent 必须遵守以下工作流程。

### Before Implementation

1. 阅读 `AGENTS.md`。
2. 阅读 `PLAN.md`。
3. 确认当前开发阶段。
4. 检查已有代码及测试。
5. 确认受影响的模块。
6. 提出最小可行修改方案。
7. 确认是否涉及数据库、API 或安全变更。

### During Implementation

- 只开发当前任务要求的功能。
- 优先复用已有组件。
- 不创建无意义的 Wrapper。
- 不重复已有业务逻辑。
- 不引入未经确认的新依赖。
- 不修改无关文件。
- 不进行未经批准的全局重构。
- 不使用临时代码冒充正式实现。
- 不通过删除测试解决测试失败。
- 不吞掉异常。
- 不使用 Mock Data 冒充真实生产数据。

### After Implementation

- 运行相关单元测试。
- 运行 Integration Tests。
- 运行 Lint。
- 运行 Type Checking。
- 运行必要的 Regression Tests。
- 检查数据库迁移。
- 检查 API Compatibility。
- 更新文档及任务状态。
- 汇报已完成内容及未解决问题。

### Required Completion Report

每项任务完成后，Agent 必须提供：

```text
Task:
Status:

Implemented:
- ...

Files Changed:
- ...

Tests:
- ...

UX Impact:
DX Impact:
AX Impact:

Compatibility:
Security:
Known Issues:

Next Task:
```

未实际执行的测试不得标记为 Passed。

不能验证的结果必须明确标记为 Unverified。

---

## 9. Definition of Done

一项功能只有满足以下条件，才可以标记为完成。

- [ ] 功能符合当前任务要求。
- [ ] 实现符合 Simple First 原则。
- [ ] 没有不必要的 UI 元素。
- [ ] 没有重复业务逻辑。
- [ ] API Contract 明确。
- [ ] 数据输入经过验证。
- [ ] 错误得到正确处理。
- [ ] 单元测试通过。
- [ ] 必要的集成测试通过。
- [ ] 回归测试通过。
- [ ] 没有引入安全漏洞。
- [ ] 没有破坏现有功能。
- [ ] 文档已更新。
- [ ] UX、DX、AX 影响已评估。
- [ ] 已知限制及风险已记录。

---

## 10. Cost Management

### Personal MVP Target

| Component | Monthly Budget |
|---|---:|
| Tiingo Starter | A$0 |
| SEC EDGAR | A$0 |
| FRED | A$0 |
| Quantitative Models | A$0 |
| PostgreSQL | A$0 |
| Existing Personal Server | A$0 incremental hosting |
| Expo Push | A$0 within applicable limits |
| LLM API | A$0–10 |
| Total Target | A$0–10/month |

预算不包含已有硬件、电费、开发时间、域名及 Apple / Google 开发者账户费用。

### Cost Control Rules

- 优先使用缓存数据。
- 数据采用增量同步。
- 数学模型使用 CPU。
- 不为数学计算调用 LLM。
- 不为普通行情查询调用 LLM。
- 对 AI 请求设置 Token Budget。
- 对后台任务设置并发限制。
- 监控第三方 API 使用量。
- 不未经确认自动升级付费套餐。
- 新付费服务必须具有明确的业务价值。

---

## 11. Development Priorities

### MVP — Core Product

- Phase 0: Project Foundation
- Phase 1: Market Data
- Phase 2: Financial Fundamentals
- Phase 3: Valuation Engine
- Phase 4: Quantitative Forecast
- Phase 5: Model Evaluation
- Phase 6: Portfolio Management
- Phase 7: AI Agent
- Phase 8: Reports & Notifications
- Phase 10: Personal Release

个人版部署前必须完成必要的身份验证、访问控制及安全要求。

### V1.0 — Public-ready Product

- 完整账户体系。
- 多用户数据隔离。
- BYOK Data Providers。
- 完整安全审查。
- 商业数据授权。
- 法律及隐私审查。
- 订阅及使用额度管理。

### V2.0 — Advanced Research

仅在核心功能稳定且存在明确需求后考虑：

- Advanced Quantitative Models。
- Portfolio Optimisation。
- Options Analysis。
- Market Regime Detection。
- Multi-market Support。
- Brokerage Integration。
- Advanced Research Automation。

---

## 12. Final Engineering Principle

The best feature is the one that solves the problem without introducing another problem.

The best architecture is the simplest architecture that meets the actual requirements.

The best interface is the one that needs the least explanation.

The best AI agent is the one that can reliably distinguish facts, calculations, assumptions, and uncertainty.

Every change must improve the product without compromising what already works.

**Simple to use. Simple to develop. Simple for agents to understand. Reliable by design.**
