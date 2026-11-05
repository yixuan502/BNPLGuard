# Offline result explainer and optional rewrite adapter

The callable template version is complete and runs without any API, key or network. src/result_explainer.py accepts trusted structured producer outputs from FrozenCFPBExplainer and run_simulation. It validates schema/probability/class/direction/reconstruction/display contracts and renders existing values. It neither scores a model nor computes income, repayments, ratios, deltas or a combined score. Shared assumptions are stated once, with each scenario's changes and producer rule messages retained.

CFPB text states the survey label, fixed threshold/class, up to three signed raw-input contributions and scope limits. Contributions are relative to background in log-odds, not personal causes or probability points. Simulator text states each buffer and delta, RTI, coverage, N/A reasons and assumptions. The existing negative-buffer and hypothetical-reduction notices remain. Zero income/outflows remain explainable partial results. Invalid simulator inputs return errors without a narrative.

## Optional LLM adapter: prepared, not live-tested

src/llm_adapter.py contains an injected-transport interface only: no OpenAI/provider client, key discovery, HTTP implementation or live call. Default enabled=False. It will not call a transport without separately explicit cost authorization, financial-data-transfer authorization and configured provider/transport. These flags are false in actual usage; enabled flags in tests refer only to in-process fictional mocks, not authorization to send real data later.

An optional provider may select only from preapproved factual phrasing variants and segment order, returning a bound facts_digest. Arbitrary free text and numeric edits are rejected. Every segment must occur exactly once, including limitations. This is a bounded paraphrase/arrangement interface, not unrestricted language generation; numeric-only matching cannot certify arbitrary prose semantics. No open financial chat or RAG exists.

Missing configuration, denied authorization, exception, timeout, omitted limits or invalid output returns the unchanged template. UI waiting is bounded by a daemon worker; an eventual transport must honor the supplied timeout because a local timeout cannot cancel a remote request already sent. Mock fallback tests passed; no external LLM quality, provider latency or paid integration validation is claimed.

Fictional combined service demonstration: outputs/extensions/demo_v2/explanation.txt. The initial verbose draft was retained in demo_v1; demo_v2 is the saved demonstration.

```python
from src.extension_service import predict_and_explain_cfpb, simulate_and_explain
from src.result_explainer import explain_results
from src.common import read_json
codes = read_json('data/metadata/extensions_baseline.json')['cfpb_inputs'][0]  # fictional
screen = predict_and_explain_cfpb(codes)
stress = simulate_and_explain({'I':4500,'E':2500,'D':700,'B0':400,'Bnew':200,'S':1000}, income_drop=0.2, bnpl_reduction=200)
text = explain_results(cfpb=screen, simulator=stress['simulation'])
```

The financial example is illustrative, not empirical model evidence. Explicitly handle invalid_input before calling explain_results with a CFPB result. No user inputs are persisted by these callable interfaces.
