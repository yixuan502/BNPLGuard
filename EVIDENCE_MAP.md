# EVIDENCE_MAP：写作与核查入口

## Current status - 6 November 2026

The [source repository](https://github.com/yixuan502/BNPLGuard) is public. The [public app](https://bnplguard-yixuan502.streamlit.app/) has accepted release marker `stress-installments-20261105` (application source `a77bc23`). Updated-app structured retest records have been received for three participants: two new and one returning. Read the [anonymous retest summary](docs/retest_evidence_2026-11-06.md) for independent versus prompted outcomes and unresolved questions. Original participant workbooks remain private; the study does not prove causal improvement or universal independent completion.

This current status supersedes earlier private-repository and pending-retest statements below. Earlier stage records retain their original context and are not current completion claims. Final report/video, signed student contributions, AI disclosure and Moodle approval/deadline evidence still require separate verification.

## Historical handoff text

证据优先顺序：当前冻结配置/序列化工件与已保存的实际指标 → 当轮方法/验收记录 → 时间更早的说明/计划。数字按下表的字段读取，不把历史阶段描述改写成最终事实。导航均使用包内相对路径；原副本历史绝对路径和manifest文件清单不代表收件人机器状态。

| 可以写的结论 | 包内文件与具体表/图/字段 | 数字口径 | 解释限制 |
|---|---|---|---|
| CFPB标签与样本 | [config/label_mapping.json](config/label_mapping.json)：mapping/missing_codes；另见docs/data_audit.md | 6394原始；6350有效；2454正例 | 同期自报困难，不是违约标签 |
| 8项输入与清洗 | [config/feature_schema.json](config/feature_schema.json)：features；src/preprocessing.py 的 CodebookTransformer/build_pipeline | 收入/储蓄是档位；训练mode填补和one-hot | 不是AUD月度金额；年龄仅评价分组 |
| 固定划分与防泄漏 | [data/splits/cfpb_split_ids.json](data/splits/cfpb_split_ids.json)：train/validation/test；models/cfpb/stage4_v1/cv_fold_ids.json | 3810/1270/1270，seed42 | 所有学习型处理折内拟合；不重划分追分 |
| 验证选LR | [models/cfpb/stage4_v1/comparison.json](models/cfpb/stage4_v1/comparison.json)：logistic_regression.validation / random_forest.validation；docs/model_selection.md | LR AP0.720857/AUC0.816946/Brier0.167396；RF AP0.717325 | sigmoid LR Brier0.167281的微小收益未抵消复杂度；不以测试选模 |
| 最终模型合同 | [config/stage5_frozen.json](config/stage5_frozen.json)：artifact/artifact_sha256/features/threshold/calibration/fit_population | 原训练3810人；threshold0.5；calibration none | test_evaluated:false 是测试前freeze历史状态，不是尚未正式测试 |
| CFPB正式测试指标 | [outputs/evaluation/stage5_v1/test_metrics.json](outputs/evaluation/stage5_v1/test_metrics.json)：各模型 average_precision/roc_auc/brier/accuracy/precision/recall/f1/confusion_matrix_tn_fp_fn_tp | 同一1270人、491正例；未加权；分类阈值0.5 | RF测试AP0.766896略高LR0.763422，不能重选部署模型 |
| 曲线、混淆矩阵 | [outputs/evaluation/stage5_v1/figures/test_roc_pr.png](outputs/evaluation/stage5_v1/figures/test_roc_pr.png)：另见figures/test_confusion_matrices.png与原始*_roc.csv/*_pr.csv | 正式锁定测试集 | AP不是梯形PR曲线面积 |
| 置信区间和配对比较 | [outputs/evaluation/stage5_v1/bootstrap_intervals.json](outputs/evaluation/stage5_v1/bootstrap_intervals.json)：logistic_regression；paired_differences.json；stage5_evaluation.json.bootstrap | 2000次普通respondent行bootstrap；percentile95% | 固定模型条件抽样不确定性，不含重训/选模/复杂调查设计；配对同抽样行 |
| 概率可靠性 | [outputs/evaluation/stage5_v1/lr_probability_diagnostics.json](outputs/evaluation/stage5_v1/lr_probability_diagnostics.json)：mean_prediction=0.401084；observed_positive_rate=0.386614；lr_calibration_bins.csv | 10等宽箱；图figures/lr_test_reliability.png | 局部高估保留；低Brier或未额外校准均不能单独证明可靠/不可靠 |
| 子群体差异 | [outputs/evaluation/stage5_v1/subgroup_metrics.csv](outputs/evaluation/stage5_v1/subgroup_metrics.csv)：model=logistic_regression，scheme=age_primary 的n/positive_n/negative_n/recall/false_positive_rate | 18–34: n287,Recall0.780,FPR0.321168；62+:n436,Recall0.458333,FPR0.063291 | 描述性结果；有组间误差差异，不等于因果歧视或无偏见认证 |
| 调查权重 | [outputs/evaluation/stage5_v1/weighted_test_sensitivity.json](outputs/evaluation/stage5_v1/weighted_test_sensitivity.json)：finalwt单独敏感性；docs/stage5_evaluation.md | 主训练/评价未加权 | 加权敏感性不是完整调查总体推断 |
| Global Permutation Importance | [outputs/evaluation/stage5_v1/validation_permutation_importance.csv](outputs/evaluation/stage5_v1/validation_permutation_importance.csv)：mean_ap_drop/sd_ap_drop；figures/lr_validation_permutation.png | validation n1270、30次；储蓄均值0.208307 SD0.014293，收入0.029354 SD0.008613 | 原始列经完整Pipeline，指标AP；全局预测重要性非个人因果 |
| Local SHAP与映射 | [config/cfpb_shap_background.json](config/cfpb_shap_background.json)：n/seed/ids/encoded_to_raw；models/cfpb/explanations_v1/background_encoded.npz | 200个固定训练背景，seed20261105；LinearExplainer Independent | log-odds；独立mask破坏依赖；分组可加不等于条件因果解释 |
| 虚构个人解释及加总检验 | [outputs/explanations/cfpb_shap_v1/fictional_0.json](outputs/explanations/cfpb_shap_v1/fictional_0.json)：probability/contributions/checks；fictional_local_contributions.png | 例子概率0.8384946；最大加总误差6.66e-16 | 只有虚构示例，不是用户研究观察 |
| 模拟器五情景 | [outputs/simulator/stage6_demo_v1/scenarios.json](outputs/simulator/stage6_demo_v1/scenarios.json)：scenarios[].key/metrics/delta_from_current/assumptions；scenario_comparison.csv/png | AUD I4500/E2500/D700/B0400/Bnew200/S1000；20%冲击、减少200；900/700/0/-200/1100 | deterministic calculation；正月结余不保具体到期日；无违约概率 |
| Kaggle来源与许可证据 | [data/metadata/kaggle_supplement_v2.json](data/metadata/kaggle_supplement_v2.json)：license/evidence_class/page_claims/still_unknown；docs/references/kaggle_supplement_2026-11-05/page_summary_2.png | 页面截图CC0 1.0；本地10345×17，flag1=4040 | 截图不证明合成或真实；默认定义/时间窗/货币/频率未知 |
| Kaggle审计和泄漏 | [outputs/kaggle_audit/v1/quality_summary.json](outputs/kaggle_audit/v1/quality_summary.json)：另见field_leakage_review.csv、monthly_record_counts.csv、docs/kaggle_leakage_review.md | 12个缺失月份；每ID一行但语义粒度未知 | 不能用事后delay/missed/score/segment证明申请时预测价值 |
| Kaggle协议与特征 | [config/kaggle_experiment.json](config/kaggle_experiment.json)：data/seed/fractions/cv_folds/selection_rule；kaggle_feature_schema.json | 6207/2069/2069；10个已审查输入；train-fold Pipeline | 仅file内recorded-label探索；不与CFPB合并，不是外部验证 |
| Kaggle冻结选RF及过拟合 | [models/kaggle/exploratory_v1/frozen.json](models/kaggle/exploratory_v1/frozen.json)：outputs/kaggle_experiment/v1/validation_comparison.csv与development_metrics.json | RF trainAP0.921401 vs valAP0.529174 | 按预先Brier容差冻结，并非普遍RF最优；不得用训练高分做业务宣传 |
| Kaggle真实测试与区间 | [outputs/kaggle_experiment/v1/test_metrics.json](outputs/kaggle_experiment/v1/test_metrics.json)：各模型指标；bootstrap_intervals.json；paired_lr_minus_comparators.json；test_curves.png | 同一2069条/808正例；1000次固定模型行bootstrap | LR/RF差异配对区间含0；未知源构造误差不在区间中 |
| Kaggle采用决策 | [docs/data_source_decision.md](docs/data_source_decision.md)：最新扩展决策；docs/kaggle_model_card.md、docs/kaggle_experiment.md | 报告附录only，无个人Kaggle输入界面 | 历史audit C暂缓已被后续授权独立实验更新，不能只读旧段 |
| 模板与LLM状态 | [src/result_explainer.py](src/result_explainer.py)：explain_results：mode/llm_status/llm_live_tested；src/llm_adapter.py RewriteOptions | 网页规则模板；LLM disabled/not live-tested | mock transport/timeout测试不是实际LLM调用；无开放理财聊天 |
| 澳洲背景证据 | [docs/references/australia_2026-11-05/source_register.json](docs/references/australia_2026-11-05/source_register.json)：sources[].url/published_on/accessed_on/supports/limit | 官方发布/编纂日与2026-11-05访问日分别记录；docs/australian_context.md | 不等于澳洲数据验证或应用合规认证；监管原文需写作当日再核对 |
| 部署与公开可用性 | [outputs/deploy/stage8_v1/acceptance.json](outputs/deploy/stage8_v1/acceptance.json)：deployed_commit/stage8_complete/online_areas/postpush_anonymous_check；cloud_postpush_ax.txt | 771aadd；已有匿名四区验收；docs/deployment.md | 旧online_acceptance字段未更新，见下文冲突说明；不等于永远在线 |
| 真实用户测试材料 | [user_testing/materials_v1/anonymous_results.xlsx](user_testing/materials_v1/anonymous_results.xlsx)：Sessions / Responses；主持人指南和参与者PDF | 空模板仍为空；另见 [反馈核验](docs/user_testing_feedback_review.md) 和 [汇总JSON](outputs/user_testing/feedback_review_v1/review.json)：收到3人汇编记录，16/18文字题、18/18应用记录（12题有提示） | 不能把示例、程序测试、空模板说成3名参与者反馈 |

## 自动从最终JSON核对的对照表

CFPB validation（models/cfpb/stage4_v1/comparison.json 的 validation；n1270；阈值0.5）：

| 模型 | AP | AUC | Brier |
|---|---:|---:|---:|
| dummy | 0.386614 | 0.500000 | 0.237144 |
| logistic_regression | 0.720857 | 0.816946 | 0.167396 |
| random_forest | 0.717325 | 0.812763 | 0.173677 |

CFPB test（outputs/evaluation/stage5_v1/test_metrics.json；n1270；不是上述validation）：

| 模型 | AP | AUC | Brier | Accuracy | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|---:|---:|
| dummy | 0.386614 | 0.500000 | 0.237144 | 0.613386 | N/A | 0.000000 | 0.000000 |
| logistic_regression | 0.763422 | 0.843158 | 0.157295 | 0.766142 | 0.723502 | 0.639511 | 0.678919 |
| random_forest | 0.766896 | 0.836302 | 0.166682 | 0.762205 | 0.732187 | 0.606925 | 0.663697 |

Kaggle test（outputs/kaggle_experiment/v1/test_metrics.json；n2069；另一个任务）：

| 模型 | AP | AUC | Brier | Accuracy | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|---:|---:|
| dummy | 0.390527 | 0.500000 | 0.238016 | 0.609473 | N/A | 0.000000 | 0.000000 |
| logistic_regression | 0.568170 | 0.707620 | 0.207157 | 0.646206 | 0.559561 | 0.441832 | 0.493776 |
| random_forest | 0.566320 | 0.697078 | 0.206394 | 0.644756 | 0.557662 | 0.436881 | 0.489938 |

N/A precision 的原因是 Dummy 无预测正例，不应填成“精确率0”掩盖未定义。

## 必须明确指出的历史冲突

1. config/stage5_frozen.json 的 test_evaluated:false 是测试前合同；stage5真实指标、completion_receipt与评价文档证明后续已评价。保持freeze原件，不据此说“测试集未用”。
2. outputs/deploy/stage8_v1/acceptance.json 的 online_acceptance:"NOT YET PERFORMED" 是残留旧字段。相同文件 stage8_complete:true、online_areas、deployed_commit、postpush_anonymous_check 与cloud_postpush_ax.txt、docs/deployment.md和实际截图记录后续验收。保留矛盾，不偷偷改原件；准确说“有已记录匿名验收，单个旧字段未同步”。
3. docs/progress.md、docs/experiment_log.md、docs/rubric_checklist.md 含历史pending或过期状态，不能忽略日期和后续完成记录。Kaggle早期延期不等于未做实验。
4. 本次仓库新增研究证据、导航和用户反馈核验；历史已验收部署仍以771aadd记录为准，未重新做线上验收；源码运行行为未改。源码仓库私有和网页公开是两件事。

## 易误写 → 准确表述

- “预测BNPL违约” → CFPB分类同期自报支出/账单困难，未验证未来违约。
- “RF测试AP更高，所以部署RF” → 选择在validation时冻结LR，test对照不能反向重选。
- “SHAP储蓄贡献2意味着提高概率200百分点” → 贡献是log-odds；sigmoid用于把总logit还原概率；关联不是干预效果。
- “减少BNPL会把Screen风险从84%降到…” → 模拟器只改现金流/比率；没有验证金额到调查编码的映射。
- “Kaggle39%是真实市场违约率/澳洲验证” → 这是来源与标签定义不完整的文件内频率，Australia仅类别。
- “CFPB AUC高于Kaggle，所以数据/模型更好” → 任务、标签、样本不同，不能作直接优劣排名。
- “Brier低，已完全校准/公平” → 保留局部高估与子群体误差，未作此认证。
- “3名用户已认可模型” → 只准备3个匿名ID和空白材料；理解研究尚未采集，也不验证模型有效性。
- “LLM解释已验证” → 英文规则模板已运行；可选LLM接口仅mock与回退测试，未live-tested。

## 本次交付核查记录

文件完整性已检查：实际解压并逐文件比对SHA256，ZIP CRC检查通过，三份导航中的包内链接均检查目标存在，冻结模型/背景/配置副本与原件一致。细节计数见本节末尾。

运行复现已验证：**本次未做全新环境安装或全研究流程重跑，不能这样宣称**。只做文件核查；已有stage8干净检出smoke与154测试记录作为历史证据随包。原始CSV、旧baseline和保护快照缺失会影响部分研究复核/原测试；获取说明和影响见START_HERE。应用核心所需runtime_files清单对应文件另行核查完整。

本包共255个文件；从原项目复制252个原件，新增3份导航；所有副本逐文件哈希一致。发布清单仅省略AGENTS.md与历史project_spec.md两项非运行指令，其余运行依赖文件齐全。


本次GitHub仓库补充发布的核验：266个审阅文件，现有项目环境154项回归测试通过（6.27秒），数据审计PASS，192个受保护文件哈希不变。原桌面ZIP的255文件计数与CRC记录仅指先前ZIP快照。新反馈为汇编工作簿来源记录；只发布聚合核验，不发布参与者原始文件。


## Stress and calculator publication update — 5 November 2026

Repository main contains the updated interface and monthly instalment calculator at commit `a77bc23b6fdb5b54645c5c4d23d7b4aaac6ffb67`, release marker `stress-installments-20261105`. The source was pushed successfully to the existing private repository. At the last anonymous check the public application still displayed the older version and did not show the new marker; Cloud rollout and the new-version online acceptance remain unconfirmed. Do not describe this revision as publicly accepted until the marker and requested interactions are checked. Real participant retesting remains outstanding. No participant responses were fabricated. See user_testing/retest_v1/ for blank materials and docs/installment_plan.md for the current calculation.


## Public acceptance completed — 2026-11-05T23:39:09+11:00

The prior Cloud pending note is superseded. After authorized reboot, an anonymous in-app browser displayed release marker `stress-installments-20261105` from app source commit `a77bc23b6fdb5b54645c5c4d23d7b4aaac6ffb67`. Screen fictional example returned83.85%, eight-feature SHAP and template text. Stress standard buffers900/700/0/-200/1100 AUD;600/0/3 previewed and applied200;100/0/3 displayed33.33/33.34 and applied33.34, yielding866.66 added-plan buffer. Editing invalidated prior results, switching restored manual200, reset cleared fields. Explain global plot and Model saved metrics AP0.7634/AUC0.8432/Brier0.1573 loaded. A390x844 viewport displayed the five standard scenario cards and the100/3 preview, visually inspected; this is emulation, not a physical iPhone or independent user test. Desktop was checked with the normal in-app-browser viewport. Local full regression170 passed; relevant tests32 passed after release marker. Original model, simulator and prior responses remain unchanged. Actual participant retest remains pending. Public app: https://bnplguard-yixuan502.streamlit.app/.


## Latest retest evidence — 6 November 2026

The previous statements that real retesting was pending are historical and superseded. A user-supplied structured workbook records three updated-app sessions: two new participants and one returning, on Windows, iPhone and iPad. Read [the separate anonymous retest evidence](docs/retest_evidence_2026-11-06.md) for per-task independent versus assisted outcomes, exact workbook cell references, follow-up summary versus facilitator observation, and the P01 savings/hesitation issue requiring field-note confirmation. The workbook's English prose is not verified verbatim; do not use direct quotes. Project brief p.3 and rubric p.4 specify at least three users and a structured instrument; the supplied workbook documents those elements, subject to source/consent verification and current course requirements. The retest is not a controlled pre/post experiment and does not prove improvement. Source workbook remains private and is not in this package.


## Latest handoff review — 6 November 2026

Updated-app real retest has been received: two new participants and one returning participant, with task-specific hints and unresolved P01 savings/hesitation. See docs/retest_evidence_2026-11-06.md. A separate internal checklist reviews the supplied report and PPT drafts against current evidence. The recent update and comparison documents in the new handoff take precedence over historical pending-status notes. Original participant workbooks and the team draft originals are excluded from the team package; no application, model, GitHub or deployment change occurred in this handoff.
