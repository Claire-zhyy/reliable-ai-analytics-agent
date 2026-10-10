---
type: note
status: active
created: 2026-09-21
updated: 2026-09-21
project: job-search
tags: [type/note, status/active, topic/ai]
---

# Reliable AI Analytics Agent · Project Brief

## English Version

### 1. What problem is this project solving?

AI increasingly allows business users to ask questions directly against company data, such as "What was our revenue last month?", "How did it change from the previous month?", or "Which customers contributed most to the increase?". An LLM can interpret the question, generate SQL, query the database, and return an answer much faster than a traditional ad hoc analytics workflow.

The main challenge is reliability. A SQL query can execute successfully and still produce the wrong business answer because of incorrect joins, metric definitions, filters, or assumptions. These errors are particularly risky because the resulting numbers still look reasonable, and nobody knows the correct answer in advance.

If every AI-generated answer must be manually validated by a Data Analyst, much of the efficiency benefit disappears. This project therefore investigates how reliably an LLM can answer business questions over a multi-table database, what types of analytical errors it makes, and how much structured business context and workflow controls each improve that reliability.

### 2. Why is a simple "AI writes SQL" demo not enough?

A simple text-to-SQL demo only shows that an LLM can translate a natural-language question into executable SQL. It does not show that the resulting business answer is correct.

Many analytical errors do not cause SQL failures. Joining one-to-many tables can duplicate rows and inflate metrics; using the wrong customer identifier can distort retention or repeat-purchase calculations; and ambiguous business terms such as "revenue" or "completed orders" can be interpreted differently without producing any visible error. The query runs and returns a plausible number that is still wrong.

For real business use, the important question is not whether an LLM can generate SQL, but whether it can produce reliable analytical answers. This project measures that reliability against a verified benchmark, identifies failure modes, and tests whether explicit business context and workflow controls reduce those errors.

### 3. Experimental setup

The database is the Olist Brazilian E-Commerce Public Dataset (roughly 100,000 orders across 9 related tables, including orders, order items, payments, customers, sellers and reviews), loaded into a local DuckDB file so that the whole project can be reproduced without a database server.

The benchmark contains 39 business questions written in the language a business stakeholder would use, deliberately not copied from the wording of the business documentation. The questions cover six types: simple aggregation, multi-table joins, metric definitions, date logic, ambiguous questions, and failure traps such as join amplification or questions likely to trigger invented columns. Each question has one of three predefined expected behaviours: `execute_sql`, `clarify`, or `insufficient_data`. For `execute_sql` questions, I wrote and manually verified reference SQL and expected results or a fixed analytical rubric. For `clarify` questions, the correct behaviour is to ask a focused clarification before returning a final answer. For `insufficient_data` questions, the correct behaviour is to identify the specific data gap without substituting an unsupported proxy.

Before the benchmark is frozen, the 39 questions will be divided into development and held-out sets. Development questions may be used repeatedly to diagnose failures and improve business semantics, prompts, workflow controls, and validation rules. Held-out questions are reserved for the final generalisation test and must not be used for tuning before the system, semantics, and workflow are frozen.

Conceptually related contrast questions are assigned using connected groups rather than independent pairs: `{Q13, Q24, Q38}`, `{Q16, Q35}`, `{Q05, Q14}`, `{Q37, Q25}`, and `{Q39, Q34}`. Every group must be placed wholly in development or wholly in held-out so that a development-driven change cannot indirectly tune a closely related held-out question. The remaining questions are balanced by type and difficulty as far as the small category sizes allow. Once frozen, held-out performance cannot be used to revise group membership, grading rules, semantics, prompts, or workflow controls. Headline result accuracy will be based primarily on held-out `execute_sql` questions, while the four `clarify` and two `insufficient_data` questions will also be reported as pooled descriptive counts across development and held-out sets because their per-split samples are too small for stable rates.

Answers are graded on the query result and metric correctness, not the SQL text, because the same correct answer can be produced by many different queries. For elapsed-duration metrics, second-, minute-, hour-, interval-, and otherwise equivalent elapsed-time calculations are acceptable, with a ±0.1-day tolerance where appropriate; calendar-boundary day differences are not treated as numerically equivalent. Numeric tolerance, row and column ordering rules, and the clarification criteria are fixed in `docs/evaluation-methodology.md` before the first evaluation run. Every run logs the question, generated SQL, execution result, model behaviour and final answer, and every incorrect answer is tagged with an error category (for example join amplification, wrong grain, metric definition, date boundary, filtering, missed clarification, hallucinated column, or SQL execution error).

To keep the comparison attributable, all three versions use the same model, the same temperature, the same base prompt structure, the same underlying database access and SQL execution tool, and the same evaluation runner. The only thing that changes between versions is the layer being tested.

### 4. What three versions will I compare?

#### Version A — Raw Schema Baseline

Version A has access to the database schema and a `run_sql` tool, but receives no business definitions, analytical rules or validation steps. Each question gets one SQL attempt; if the query fails to execute, the failure is recorded rather than repaired. This version represents what happens when a company connects an LLM directly to its database without any preparation, and it establishes the baseline before analyst-provided context is introduced.

#### Version B — Business Semantics

Version B receives the same access as Version A, plus the business context I wrote: the evidence-free model data dictionary in `02-tables-model-context.md` (table grain, primary and foreign keys, one-to-many relationships and known join risks) and the business-semantics document (metric definitions with numerator, denominator, date field, filters and edge cases, plus rules such as using `customer_unique_id` to identify the same customer across orders). The evidence-bearing internal profiles in `02-tables.md` and `02-tables-overview.md` are not supplied to the evaluated model. Version B adds no new workflow steps.

The comparison between A and B measures how much structured business context alone improves analytical reliability.

#### Version C — Business Semantics + Workflow Controls

Version C keeps everything in Version B and adds workflow controls at two levels. Prompt-level rules instruct the model to ask for clarification when a question is genuinely ambiguous, not to make unsupported assumptions silently, to state the intended analytical grain, to check one-to-many joins for duplication risk, and to report which metric definition it used. Code-level checks are enforced by the program rather than requested of the model, as a separate validation and bounded self-repair layer around the shared SQL execution tool: generated SQL is checked against the real schema before execution so that non-existent tables or columns are rejected; execution errors are returned to the model for a limited number of repair attempts; and structural sanity checks compare row counts and distinct key counts against the intended grain so that unexpected join amplification or duplication is flagged rather than reported with confidence.

The comparison between B and C measures whether a structured analytical process adds reliability beyond business context alone. Separating the experiment into three versions makes it possible to distinguish the contribution of business knowledge from the contribution of workflow controls, rather than introducing both at once and attributing any improvement to an unknown combination of factors.

### 5. How will I determine whether the project succeeds?

The project succeeds if it produces a reproducible and interpretable evaluation of all three versions on the same held-out questions, not only if a predetermined accuracy target is reached. A clear finding that an intervention did not help is a valid result, provided the methodology and limitations are transparent.

Before running any version, I record two hypotheses. First, that the A → B improvement will come mainly from fewer metric-definition, wrong-grain and join-amplification errors, because the baseline lacks business knowledge rather than SQL ability. Second, that the B → C improvement will come mainly from ambiguous questions and execution errors. These are hypotheses to be tested, not targets, and the final report will state whether each one held.

Results are reported as counts as well as rates, with development and held-out results shown separately where sample size permits. Responses are scored separately on `behavior`, `result`, and, where applicable, `assumption_transparency`. Because the benchmark includes `clarify` questions and Version C is explicitly instructed to clarify, part of any B → C gain on those questions is expected by design. For that reason, `execute_sql`, `clarify`, and `insufficient_data` outcomes are reported separately, and over-clarification, meaning Version C asks for clarification on a question that should have been answered directly, is tracked as its own failure mode. Question-level regressions in either direction (a question answered correctly by A but not B, or by B but not C) are recorded and analysed. A small repeatability test, in which five representative questions are run three times each on the final version, checks whether answers stay consistent across runs.

Because the benchmark is intentionally small, percentage changes are not treated as precise estimates of real-world performance. A single additional correct answer can materially change a held-out rate, and the `clarify` and `insufficient_data` categories are especially small. The main weight of the conclusion therefore rests on counts and on which error categories decrease, persist or appear at each stage, especially where the same pattern shows up in both the development and held-out sets. The result is evidence from a controlled case study, not a general claim about LLM performance.

### 6. What is explicitly out of scope?

This project is an analytics reliability evaluation case study, not a production AI product and not a comparison between LLMs. A single model is used throughout so that differences come from the context and workflow layers rather than from model choice.

The core scope does not include a production user interface, cloud deployment, enterprise authentication or permissions, production MLOps, fine-tuning, or a complex multi-agent architecture. These matter in a production implementation, but they are not needed to answer the project's main question.

RAG and MCP are optional extensions, attempted only after the core A/B/C held-out evaluation and error analysis are complete. If the core experiment is not finished, the extensions are dropped rather than allowed to compromise its completeness or interpretability.

---

## 中文版

### 1. 这个项目在解决什么问题？

现在 AI 越来越可以让业务人员直接对公司数据提问，例如"上个月的 revenue 是多少？""和上上个月相比增长了多少？""哪些客户贡献了主要增长？"。LLM 可以理解问题、生成 SQL、查询数据库并快速返回结果，比传统的 ad hoc analytics workflow 快很多。

真正的问题是答案是否可靠。一段 SQL 即使可以正常运行，也可能因为错误的 join、指标定义、筛选条件或未经依据的假设而得到错误的业务结论。更危险的是，这些错误不会报错，数字看起来也合理，而且没有人事先知道正确答案。

如果每一个 AI 生成的答案都需要 Data Analyst 再手工验证，自动化的效率优势就会被大幅抵消。因此这个项目研究的是：LLM 在 multi-table database 上回答业务问题到底有多可靠，它最常见的 analytical failure modes 是什么，以及 structured business context 和 workflow controls 各自能在多大程度上提高这种可靠性。

### 2. 为什么一个简单的 "AI writes SQL" demo 不够？

一个简单的 text-to-SQL demo 只能证明 LLM 可以把自然语言转换成能执行的 SQL，不能证明最终的业务答案是正确的。

很多分析错误不会导致 SQL 报错。一对多的表直接 join 会复制记录并放大指标；用错 customer identifier 会扭曲 repeat purchase 或 retention 计算；revenue、completed orders 这类概念如果没有明确口径，AI 会自行采用某一种定义。Query 成功运行，返回一个看起来合理但实际错误的数字。

因此在真实业务场景里，重要的问题不是"AI 能不能生成 SQL"，而是"AI 能不能产生可靠的 analytical answer"。这个项目用一套经过验证的 benchmark 衡量这种可靠性、识别 failure modes，并测试明确的 business context 和 workflow controls 能否减少这些错误。

### 3. 实验设置

数据库使用 Olist Brazilian E-Commerce Public Dataset（约 10 万笔订单，9 张互相关联的表，包括订单、商品明细、付款、客户、卖家、评价等），导入本地 DuckDB 文件，任何人下载 repo 后不需要数据库服务器就能复现。

Benchmark 包含 39 道业务问题，用业务同事的口吻写，刻意不照搬业务手册里的措辞。题目覆盖六类：simple aggregation、multi-table joins、metric definitions、date logic、ambiguous questions，以及 failure traps（例如 join amplification、容易诱发编造列名的问法）。每道题都预先规定三种 expected behavior 之一：`execute_sql`、`clarify` 或 `insufficient_data`。`execute_sql` 题有经过验证的 reference SQL 和 expected result，或固定的分析 rubric；`clarify` 题应在给最终答案前提出一个聚焦的澄清问题；`insufficient_data` 题应指出具体数据缺口，而不能用没有依据的 proxy 替代。

Benchmark 冻结前，将把 39 道题划分为 development 和 held-out 两组。Development questions 可以反复用于诊断 failure，并改进 business semantics、prompt、workflow controls 和 validation rules；held-out questions 只用于最终 generalisation test，在 system、semantics 和 workflow 冻结前不能用于 tuning。

概念高度相关的 contrast questions 按 connected groups 分组，而不是把 pair 独立处理：`{Q13, Q24, Q38}`、`{Q16, Q35}`、`{Q05, Q14}`、`{Q37, Q25}`、`{Q39, Q34}`。每组必须整体进入 development 或整体进入 held-out，避免 development 中的改动间接调优近似的 held-out question。其余题目在小类别数量允许的范围内平衡题型和难度。冻结后不能因为 held-out 表现不好而修改 group membership、grading rules、semantics、prompt 或 workflow controls。Headline result accuracy 主要以 held-out 的 `execute_sql` 题为准；4 道 `clarify` 和 2 道 `insufficient_data` 因为样本过小，将合并 development 与 held-out，以描述性题数另行报告。

判分依据是查询结果和 metric correctness，而不是 SQL 文本，因为同一个正确答案可以有很多种写法。对于 elapsed-duration metric，second、minute、hour、timestamp interval 或其他等价的 elapsed-time 实现都可接受，并在适用时使用 ±0.1 day tolerance；calendar-boundary day difference 不视为数值等价。数值误差、行列顺序规则和澄清标准在第一次评估之前写死在 `docs/evaluation-methodology.md` 里。每次运行都记录 question、generated SQL、execution result、model behavior 和 final answer，每道错题贴上 error category 标签（例如 join amplification、wrong grain、metric definition、date boundary、filtering、missed clarification、hallucinated column、SQL execution error）。

为了保证可以归因，三个版本使用同一个模型、同一个 temperature、同一个基础 prompt 结构、同一套底层 database access 和 SQL execution tool，以及同一个 evaluation runner。版本之间唯一变化的，是当前被测试的那一层。

### 4. 我要比较哪三个版本？

#### Version A — Raw Schema Baseline

Version A 只获得 database schema 和 `run_sql` 工具，没有业务定义、分析规则或校验步骤。每道题只有一次 SQL 尝试，执行失败就如实记录，不做修复。它代表一家公司什么都不准备、直接把 LLM 接到数据库上的情况，用来在 analyst-provided context 加入之前建立 baseline。

#### Version B — Business Semantics

Version B 在 A 的基础上加入我写的 business context：不含 Evidence 的模型专用 data dictionary `02-tables-model-context.md`（table grain、主键和外键、一对多关系、已知 join 风险）和 business-semantics 文档（每个指标的分子、分母、日期字段、过滤条件和 edge cases，以及例如跨订单识别同一客户必须使用 `customer_unique_id` 这样的规则）。包含数据证据的内部文档 `02-tables.md` 和 `02-tables-overview.md` 不提供给被评测模型。Version B 不增加任何新的 workflow 步骤。

A → B 的比较用于衡量 structured business context 本身能在多大程度上提高 analytical reliability。

#### Version C — Business Semantics + Workflow Controls

Version C 保留 B 的全部内容，并在两个层面加入 workflow controls。Prompt 层的规则要求模型：问题确实有歧义时先 clarification；不允许 silently make unsupported assumptions；明确 intended analytical grain；检查 one-to-many joins 的 duplication risk；在回答中说明使用了哪个指标定义。代码层的检查由程序强制执行，而不是请求模型遵守，并作为共享 SQL execution tool 外的一层独立 validation 和 bounded self-repair layer：生成的 SQL 在执行前与真实 schema 比对，不存在的 table 或 column 直接拦截；执行报错时把报错信息交回模型，限次重试修复；structural sanity checks 会对照 intended grain 检查 row count 和 distinct key count，从而标记异常的 join amplification 或 duplication，而不是把可疑结果直接自信地报告。

B → C 的比较用于衡量：在 business context 已经存在的情况下，结构化的分析流程能否进一步提高 reliability。拆成 A / B / C 三个版本，是为了分别识别 business knowledge 和 workflow controls 的贡献，而不是一次性加入所有改进，最后不知道究竟是什么带来了变化。

### 5. 我怎么判断这个项目是否成功？

项目是否成功，取决于是否在同一批 held-out 题上完成了一套可复现、可解释的 A / B / C evaluation，而不只是是否达到某个预设的 accuracy target。只要 methodology 和 limitations 透明，"某项 intervention 没有带来提升"同样是有效结论。

在跑任何版本之前，我先记录两个假设。第一，A → B 的改善主要来自 metric-definition、wrong-grain 和 join-amplification 错误的减少，因为 baseline 缺的是业务知识而不是 SQL 能力。第二，B → C 的改善主要来自 ambiguous questions 和 execution errors。这些是待检验的假设，不是目标，最终报告会写明每一个是否成立。

结果同时报告题数和比率，并在样本量允许时分别呈现 development 和 held-out。每个回答分别按 `behavior`、`result` 和适用时的 `assumption_transparency` 三个维度评分。由于 benchmark 里有 `clarify` 题，而 Version C 被明确要求澄清，B → C 在这类题上的部分提升是实验设计本身决定的。因此 `execute_sql`、`clarify` 和 `insufficient_data` 分开报告，并且把 over-clarification（C 版在本应直接查数的题上也反问）作为单独的 failure mode 追踪。任何方向的逐题 regression（A 对 B 错，或 B 对 C 错）都会被记录和分析。另外做一个小型 repeatability test：用最终版本把 5 道代表性题目各跑 3 次，检查答案是否一致。

由于 benchmark 规模刻意保持较小，percentage change 不被当成对真实世界 performance 的精确估计。多对或少对 1 道题就可能显著改变 held-out rate，而 `clarify` 和 `insufficient_data` 类别尤其小。因此结论会同时看题数，并重点分析每一层哪些 error categories 减少、不变或新出现，尤其是在 development 和 held-out 两边都出现的同一种模式。最终结果是一个 controlled case study 的证据，不是对 LLM performance 的普遍结论。

### 6. 哪些内容明确不属于这个项目的核心 scope？

这个项目是一个 analytics reliability evaluation case study，不是 production AI product，也不是不同 LLM 之间的比较。全程只使用一个模型，保证结果差异来自 context 和 workflow 两层，而不是模型选择。

核心 scope 不包括 production user interface、cloud deployment、enterprise authentication / permissions、production MLOps、fine-tuning 或复杂的 multi-agent architecture。这些在真正的 production implementation 中很重要，但不是回答本项目核心问题所必需的。

RAG 和 MCP 只作为 optional extensions，在核心 A / B / C held-out evaluation 和 error analysis 完成之后才尝试。如果核心实验没有完成，扩展直接取消，不允许它们影响主实验的完整性或可解释性。
