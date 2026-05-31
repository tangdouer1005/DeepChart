# DeepChart 开源整理 — Phase 0 盘点报告
日期: 2026-05-31

## 1. 三个 domain 的位置与数量（全部与论文 Table 7 对齐）

| Domain | 物理位置 | 基础 query 数 | 论文 | context 变体 |
|---|---|---|---|---|
| **Academic**（nature） | 远程 5090 `…/bench/json/` | **178** | 178 ✓ | Normal / Long (×2) |
| **Finance**（annual_report） | 远程 5090 `…/bench/json2/` | **290** | 290 ✓ | Normal / Long / Ultra-Long (×3) |
| **Research Report**（多模） | 本地 `new_domain_eval/new_domain/json/` | **256** | 256 ✓ | report-level (×1) |

- 178+290+256 = **724 基础 query** = 论文 "Queries 724" ✓
- 178×2 + 290×3 + 256 = **1,482 实例** = 论文 "Instances 1,482" ✓✓✓

## 2. 远程文本域参考文件清单

Academic（json/, id 1..178）：
- `ground_truth_code/nature_1/` — Stage1 抽取+推理 py (178)
- `ground_truth_code/nature_2_py/` — Stage2 可视化 Python (178)
- `ground_truth_code/nature_2_html/` — Stage2 可视化 HTML (178)
- `ground_truth_code/nature_2_output/` — 178 json + 28 png（渲染缓存）

Finance（json2/, id 1..290）：
- `ground_truth_code/report_py_1/` — Stage1 (**284/290**，缺6)
- `ground_truth_code/report_py_1_output/` — D_src+D_der (**284/290**，缺6)
- `ground_truth_code/report_py_2/` — Stage2 Python (290) ✓
- `ground_truth_code/report/` — Stage2 HTML (290) ✓

公共参考：
- `ground_truth_image/` — 179 张 `id-N.png`（**属 Academic 集**）
- `ground_truth_table/` — 23 个 src_data 表目录（学术按 DOI / 金融 annual_report_table / alpha_table）

## 3. 本地多模域（Research Report）
- 实例: `new_domain_eval/new_domain/json/` (256)，另有 json_query / json_query_single (各256)、json_back(155草稿)
- 源报告: `new_domain/` → cbinsights / startupgenome / nature / startupblink / annual_report
- eval 工作区: `new_domain_eval/{code, new_domain, output, tmp}`
- 模型结果: `output/{gpt-5.2, glm-5, qwen3.6-flash, paper_edits}`

## 4. ✅ 收口核查结果

**(a) 缺口1 — Finance 缺的 6 个 stage1：精确定位**
缺 `report_py_1`+`report_py_1_output` 的是 id = **268, 278, 284, 285, 286, 288**。
这 6 个的 `report_py_2`(stage2) 齐全，只缺第一阶段。
→ 处理：补跑这 6 条 stage1（保 290），或剔除降为 284。建议补跑。

**(b) 缺口2 — Finance 参考图位置：确认**
Finance **无预存 png**（`report_py_1_output/`、`report_py_2/` 下 0 图）；参考图由执行 `report_py_2`(py)/`report`(html) **现场渲染**。`ground_truth_image/` 那 179 张是 Academic 的。
→ Phase 6 批量执行 `report_py_2` 生成并缓存 Finance 参考图。

**(c) context 变体来源：确认**
- Finance `data/annual_report/`：`md_3table_context`=**Normal**、`pdfs_good_md`=**Long**、`pdfs_good`(完整10-K)=**Ultra-Long**
- Academic `data/nature/<doi>/`：每篇 DOI 一目录（全文 md + 源数据 + 图）；Normal/Long 由全文 md 不同截取构成
- 精确拼接逻辑在 `run_nature_1.py` / `batch_run_nature_2.py`，Phase 4 细读

**(d) 两域 schema 不一致（Phase 3 ETL 重点）**
- Academic（json/）：`data.paper` 指向全文 md；顶层有 gt_table/gt_image/gt_code 键；`data.type=text_file`
- Finance（json2/）：`data.table_context`+`data.table` 显式多文件路径；`data.type=text_files`
- Academic query 含 `{code_type}` 模板变量 + 中文 → 需确认真实 query 是否在 `query_full`（探测因工具延迟未稳定返回，留 Phase 1 收尾）

**(e) 每实例引用完整性**：Finance table 路径共 **5716** 条，**0 缺失**；Academic `paper` md 全部存在。

## 5. ⚠️ 必须脱敏（Phase 5）
- 远程: `RAG/main.py`、`RAG/rag_retriever.py`、`RAG/data_for_rag/financial_metrics_lib.json`、`report_py_1/{22,216}.py`；home `google_accounts.json`
- 本地根: `anywhere_key`、`glm_key`、`key`、`cookie`

## 6. 待统一/排除
- GT 前缀 `nature_*`/`report_*` → 统一 academic/finance
- `data.type` text_file vs text_files
- 中文字段（indicator_full、表目录 "腾讯22-25年中财报"）：保留/翻译待定
- 排除草稿集：`json2_pre`(155)、`json2_rm`、`json_rm`、`json_back`(155)
- 不进发布集的本地垃圾：`tmp/`、`logs/`、`.cache_*`、`.tmp_read*`、`node_modules/`

## 7. 环境备注（重要）
本会话 Bash/Read 工具持续**输出延迟/串话**、SSH 批量一错全连带取消、安全分类器间歇宕机。
**可靠路径（已验证）**：本地写脚本 → `scp` 上传 → **单条** `ssh python3` → `scp` 下载 → 本地 Read。**绝不并行、绝不把 Write/Edit 与 ssh 同批。**
远程 home 剩 428G；本地多模去 tmp 后上传量待 Phase 2 测算。
