# BNPLGuard：组员十分钟导读

本包用于组内理解、演示和继续写作的证据交接，不是正式课程报告，也不是已完成的用户研究。先读本文件，再读 [EVIDENCE_MAP.md](EVIDENCE_MAP.md)，最后把 [AI_HANDOFF_PROMPT.md](AI_HANDOFF_PROMPT.md) 粘贴到自己的大模型对话，并上传本包。三份中文导航来自已交付交接包，现按反馈接收情况更新；正式课程报告未代写。

## 1. 项目要回答什么（第 1 分钟）

- RQ1：传统 ML 能否识别调查中自报难以支付日常支出及账单的人？用 CFPB 数据、Dummy 对照和冻结测试集回答。它不是 BNPL default prediction。
- RQ2：使用独立的 BNPL Repayment Stress Simulator 后，用户能否正确理解新增月还款、收入下降对当月现金结余的影响？现已收到3人汇编反馈并复核；只有1人的应用题明确为无提示结果，不能用 AUC 或混合提示后的正确率证明效果。
- 目标用户：风险分析师、金融机构产品／风险团队，以及本次课程演示受众。
- 公开应用：https://bnplguard-yixuan502.streamlit.app/ 。源码仓库：https://github.com/yixuan502/BNPLGuard （私有；本包不包含凭据，也不改变访问权限）。

## 2. 一个完整虚构案例（第 2–4 分钟）

这是一场虚构演示，包含两套不同口径的输入，不能把 AUD 月收入换成美国调查编码。

1. **Screen**：点击 Load fictional example，再 Run screening。固定输入见 [config/app_examples.json](config/app_examples.json)：PPINCIMP=1、SAVINGSRANGES=1、EMPLOY=1、VOLATILITY=1、EARNERS=1、HOUSING=1、PRODHAVE_8=0、PPHHSIZE=1。大意是年度家庭收入低于 USD20,000、当前储蓄 USD0、自雇、月收入大体稳定、一个收入贡献者、自有住房、无教育贷款、单人家庭。实际标签与选项以 schema 为准。
2. 页面显示 **83.85%**，由冻结 Logistic Regression 的完整 Pipeline 调用 predict_proba 计算。它估计该自报财务困难标签，不是借贷审批或未来违约概率。研究分类阈值固定 0.5；没有 low/medium/high 风险分级。
3. **Explain → Local**：同一次提交的 SHAP 展示 8 项原始输入相对固定训练背景如何推高／压低这个模型估计；单位是 log-odds，不能说成概率百分点或个人真实原因。Global 是另一个问题：验证集总体 Permutation Importance。修改 Screen 输入会使旧结果失效，需要重新提交。
4. **Stress**：点击 Load fictional financial example。输入 AUD 月税后收入 I4500、必要生活支出 E2500、非BNPL还款 D700、现有BNPL B0=400、新增BNPL Bnew=200、紧急储蓄 S1000；收入下降20%、假设减少现有BNPL200；点击 Compare scenarios。五个结余依次 **900、700、0、-200、1100 AUD**。E 不再含已填的债务／分期还款。
5. 新增月还款只改变独立模拟器的结余、RTI、储蓄覆盖及场景差值；它不会自动改变先前的83.85%。界面英文解释来自既有规则模板，不是 LLM 临场计算。

公式：B=B0+Bnew；buffer=I-E-D-B；RTI=(D+B)/I；coverage=S/(E+D+B)。Current 排除 Bnew；income shock 只在基准收入上施加一次下降；combined 同时加 Bnew 与收入冲击。Coverage 是无新收入且支出不变假设下的覆盖月数，不是实际耗尽日期。正月结余不保证每个到期日有现金；减少还款只是情景假设，不改变合同。零收入／零分母返回有原因的 N/A，不强行填1。

## 3. CFPB：从调查到网页（第 5–7 分钟）

数据是美国2016年 National Financial Well-Being Survey，2017年9月发布。原始6394行217列；44条缺失标签不填0，剔除后6350人，其中2454个正例。ENDSMEET 的1（not at all difficult）→0，2/3（somewhat/very difficult）→1。这是同期自报困难，不是未来事件。

8项特征：PPINCIMP（年度家庭USD收入档位）、SAVINGSRANGES（当前储蓄档位）、EMPLOY（个人工作状态）、VOLATILITY（家庭月收入变动）、EARNERS（家庭收入贡献者）、HOUSING（住房）、PRODHAVE_8（教育贷款）、PPHHSIZE（家庭人数）。年龄不在最终8项输入中；年龄只用于评价分组。

清洗：CodebookTransformer 校验原始编码；储蓄 -1/98/99 和 EMPLOY99 作为缺失；EMPLOY4–8归为同类。全是类别特征，不把收入档位当金额或连续变量缩放。缺失用训练集 most_frequent 填补，OneHotEncoder 处理类别，均封装在 Pipeline，交叉验证时每折内拟合。ID、目标和结果近义字段不作为输入；划分ID隔离固定，不能为提高分数重新划分。

固定 train/validation/test =3810/1270/1270（60/20/20，seed42）。候选是 Dummy、LR、有限搜索RF，并比较训练内部拟合的 sigmoid calibration。验证 LR AP0.720857、AUC0.816946、Brier0.167396；RF AP0.717325、AUC0.812763、Brier0.173677。LR校准 Brier0.167281，改善约0.000115；预先规则考虑近似表现、概率误差和复杂度，最终保留**原始LR，不额外校准**。不是预设RF最好，也不是看测试集再选LR。

冻结参数：C1、lbfgs、max_iter1000、class_weight=None，阈值0.5；没有 train+validation refit。可信工件 [models/cfpb/stage4_v1/logistic_regression.joblib](models/cfpb/stage4_v1/logistic_regression.joblib) 的SHA256为 `6f8a82a70e38ae9d5f6143ca4b491d21932d480ca1b38e3d93f079c6794c06d8`。

正式测试集 n1270、正例491：LR Accuracy 0.766142、Precision 0.723502、Recall 0.639511、F1 0.678919、AUC 0.843158、AP 0.763422、Brier 0.157295。混淆矩阵 [TN,FP,FN,TP]=[659,120,177,314]。AP95%CI [0.725172,0.802343]。主结果未加调查权重；finalwt敏感性另存。区间是固定模型在本测试样本上的行bootstrap，不覆盖完整训练／选模或复杂调查设计。

限制：US2016→当前澳洲的迁移未验证；缺失填补与代理特征影响解释；局部概率高估、子群体错误率差异必须保留。Brier低不等于充分校准，组间接近也不等于无偏见。测试RF的AP略高于LR也不能据此重选部署模型。

## 4. Kaggle 为什么做、为什么放附录（第 8 分钟）

独立探索另一数据源能否给出有价值的 recorded default_flag 分类证据。文件10345行17列，4040个flag1（39.0527%）；固定6207/2069/2069划分，与CFPB完全隔离。10项输入：age、monthly_income、credit_score、purchase_amount、app_usage_frequency、debt_to_income_ratio、employment_type、product_category、location、bnpl_installments。排除ID、repayment_delay_days、missed_payments、risk_score、customer_segment及其衍生项，并排除transaction_date；后验还款／评分时间不明，不能用泄漏变量追高分。

按预先验证规则冻结RF；RF测试 AP 0.566320、AUC 0.697078、Brier 0.206394；LR测试 AP 0.568170、AUC 0.707620、Brier 0.207157。RF train AP0.921401 对 validation0.529174，过拟合明显；测试差异的配对区间包含0，没有重选赢家。

页面截图声明 CC0 1.0，但真实／合成、default标准与观察窗、币种、付款频率和特征时间可得性仍未知。日期只覆盖2023年1–6月、2024年7–12月，中间断12个月。Australia 是一个类别，不是澳洲真实外部验证。最终用途是**报告附录**；不进入个人预测、不与CFPB拼接或平均概率、不做跨任务AUC排名、不把 purchase_amount/installments 当月还款。

## 5. 状态、分工和接下来（第 9–10 分钟）

- 已完成：冻结CFPB模型及正式评价、独立模拟器、真实SHAP、英文模板、Kaggle独立实验、澳洲官方背景整理、四区Streamlit集成、公开部署及已有匿名浏览器验收。
- LLM：`src/llm_adapter.py` 是默认关闭的可选接口；只测试模拟 transport／回退。**LLM adapter prepared, not live-tested**。没有已启用的API或聊天机器人。
- 测试材料与反馈：[user_testing/materials_v1/participant_test_sheet.pdf](user_testing/materials_v1/participant_test_sheet.pdf) 只发这一份给参与者。[user_testing/materials_v1/facilitator_guide_and_answers.pdf](user_testing/materials_v1/facilitator_guide_and_answers.pdf) 是组内保留答案。[user_testing/materials_v1/anonymous_results.xlsx](user_testing/materials_v1/anonymous_results.xlsx) 的 Sessions 填设备/版本/时间/主观反馈，Responses 填逐题原话、提示前后得分。只有P01–P03及分配/题号预填，空白模板仍为空；已收到的汇编反馈另见 [核验记录](docs/user_testing_feedback_review.md)。文字题16/18，应用题记录18/18，其中12题在操作提示后记录。原始反馈工作簿保存在本地私有目录，不上传仓库。
- 组员待完成：已收到工作簿记载的3名非开发者反馈；仍需核实日期、补充提示前应用答案和清晰的Screen原文；按正式课程要求准备报告与视频、文献及本人贡献／签名、AI使用披露。不得虚构个人贡献、反馈或显著改进。本轮没有代写报告，也没有指派谁已经完成了什么。

**共同演示路线**：打开公开网址 → Screen加载虚构问卷并提交 → Explain Local讲贡献、Global讲总体重要性 → Stress加载虚构财务案例展示900/700/0/-200/1100与差值 → Model展示正式测试、校准/子群体限制 → 展开Kaggle附录和澳洲背景 → 说明真实用户测试仍待完成。每人都先独立走一遍；三人视频中实际发言安排由组内决定。

## 6. 版本、运行、获取缺失材料

历史已验收部署为 `771aadd7b8c15de4c972d9b634f01e50ce9f0eb2`。本次仓库扩充研究工件、三份导航、测试材料和反馈核验摘要，未改应用源码／配置／模型。以 Git HEAD 查看当前交接版本；新提交不等于已重新完成线上浏览器验收。桌面原ZIP是本次扩充之前的历史快照，未覆盖重建。

在解压后的本包根目录操作，**不要照搬历史文档中的原电脑绝对路径**。原README等原样保留供追踪；实际代码以当前src/config和工件为准；旧项目提示词不是完成证据。

```bash
python3.13 -m venv .venv
.venv/bin/python -m pip install -r requirements-app-lock.txt
.venv/bin/python -m streamlit run app.py
# 或已有 uv：uv sync --frozen --group test
# uv run --frozen python -m streamlit run app.py
# 原始CSV不在包中时，可在全新副本做四区程序检查：
.venv/bin/python deployment/smoke.py
```

PyCharm选择本机解压目录下新建的 `.venv` 解释器，工作目录为有app.py的包根目录；入口用module streamlit，参数run app.py。停止用Ctrl+C，端口忙时先确认现有进程，勿照抄历史PID。无需API key。模型只加载本包可信工件。

**未随包附带的材料及影响**：

1. 原始CFPB CSV不自动再分发（项目未确认单独数据许可）。从 https://www.consumerfinance.gov/data-research/financial-well-being-survey-data/ 获取2016 public-use文件，放 `data/raw/cfpb/NFWBS_PUF_2016_data.csv`；应为6394×217，SHA256 `3680d33576549a99a8dfd7f99d5661a36a8fc1aac0d66f2bf2ec5524695304d8`。Codebook/Guide已在docs/references中。缺CSV不影响冻结网页预测、SHAP、模拟器及查看指标；会阻止重新做数据审计、训练和逐行复核。不得以新版或不同字节CSV悄悄覆盖冻结来源。
2. Kaggle原始CSV不附。到 https://www.kaggle.com/datasets/shree0910/buy-now-and-pay-later-fintech-ml-dataset （可能需自行登录并确认条款），下载并放 `data/raw/kaggle_bnpl/Buy_Now_Pay_Later_BNPL_CreditRisk_Dataset.csv`；应10345×17、SHA256 `780cdb1eec43519b0764059563d89258ef1d9e4cef3b1ffdeab9622d6976b1bd`。页面CC0截图证据已附；不代表源版本字节一致已认证。缺CSV只影响独立审计／实验复现，不影响当前应用。
3. 参考Notebook代码许可未知，不附Notebook。来源 https://www.kaggle.com/code/sumedh1507/bnpl-credit-risk-insights ，项目审查记录见docs/kaggle_notebook_review.md；不需它即可运行自主src实现，不能冒充其保存输出为本项目结果。
4. 课程PDF在原项目存在，但未确认可再分发授权，本包不附全文。组员到本课程UNSW Moodle（https://moodle.telt.unsw.edu.au/course/view.php?id=101900）各自获取 `project-a-tech-team.pdf` 与 `marking-criteria-a-tech-team.pdf`，可放docs/references同名路径。核对Project第3页用户测试人数／报告结构，第4页README/视频要求、第5页AI使用；Rubric第4页用户测试要求、第6页视频、第7页贡献与处罚。包内docs/rubric_checklist.md和测试主持人指南是已有摘记，不替代原文；Moodle当期截止日期等仍需组员确认。缺PDF不影响应用，但影响正式要求的独立核验。
5. 澳洲资料只附官方来源register和项目讨论，未打包整站HTML；按register的url、published_on/accessed_on自行取官方原文。用于业务背景，不是模型外部验证或合规认证。
6. 不附旧环境、Git历史、重复复现目录、bootstrap逐次大数组、个体级预测、课程提示词和账户材料。部分原研究测试依赖旧baseline目录／本地保护快照，故本包不是完整研究归档；不要宣称原154项测试已在本包重跑。包内旧manifest保留其原run文件列表，列表里的被裁掉文件不是“本包已有”。

**原桌面ZIP的历史交付检查（不是本次新增反馈的验收）**：文件完整性已检查（ZIP实际解压、逐文件SHA256、三份导航链接目标与冻结工件哈希）；本次未在全新环境完整安装并重跑，不能写成“运行复现已验证”。已有stage8 GitHub干净检出四区检查是历史证据，不是本次解压验收的替代。


## Stress and instalment release (5 November 2026)

Release marker: `stress-installments-20261105`. Updated Stress input order, savings separation, five visible scenario results and optional monthly instalment estimation. User retest forms are prepared; actual participant retest remains pending. See docs/installment_plan.md, docs/stress_feedback_changes.md and user_testing/retest_v1/. Online acceptance and actual commit must be checked separately; do not infer them from this preparation note.


## Stress and calculator publication update — 5 November 2026

Repository main contains the updated interface and monthly instalment calculator at commit `a77bc23b6fdb5b54645c5c4d23d7b4aaac6ffb67`, release marker `stress-installments-20261105`. The source was pushed successfully to the existing private repository. At the last anonymous check the public application still displayed the older version and did not show the new marker; Cloud rollout and the new-version online acceptance remain unconfirmed. Do not describe this revision as publicly accepted until the marker and requested interactions are checked. Real participant retesting remains outstanding. No participant responses were fabricated. See user_testing/retest_v1/ for blank materials and docs/installment_plan.md for the current calculation.


## Public acceptance completed — 2026-11-05T23:39:09+11:00

The prior Cloud pending note is superseded. After authorized reboot, an anonymous in-app browser displayed release marker `stress-installments-20261105` from app source commit `a77bc23b6fdb5b54645c5c4d23d7b4aaac6ffb67`. Screen fictional example returned83.85%, eight-feature SHAP and template text. Stress standard buffers900/700/0/-200/1100 AUD;600/0/3 previewed and applied200;100/0/3 displayed33.33/33.34 and applied33.34, yielding866.66 added-plan buffer. Editing invalidated prior results, switching restored manual200, reset cleared fields. Explain global plot and Model saved metrics AP0.7634/AUC0.8432/Brier0.1573 loaded. A390x844 viewport displayed the five standard scenario cards and the100/3 preview, visually inspected; this is emulation, not a physical iPhone or independent user test. Desktop was checked with the normal in-app-browser viewport. Local full regression170 passed; relevant tests32 passed after release marker. Original model, simulator and prior responses remain unchanged. Actual participant retest remains pending. Public app: https://bnplguard-yixuan502.streamlit.app/.
