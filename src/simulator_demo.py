"""Export the fictional stage-six example; never read models or real financial data."""
import argparse
import csv
import json
import os
from pathlib import Path
from decimal import Decimal
from .common import ROOT, read_json, write_json, sha256
from .simulator_presentation import run_simulation, NOTICE


def export_demo(output_dir='outputs/simulator/stage6_demo_v1'):
    out=Path(output_dir)
    if not out.is_absolute():out=ROOT/out
    if out.exists():raise FileExistsError(f'Preserve existing demo {out}; choose a new --output-dir.')
    specification=read_json('config/simulator_demo.json')
    result=run_simulation(specification['fictional_inputs'],**specification['scenario_settings'])
    assert result['status']=='ok'
    out.mkdir(parents=True)
    write_json(out/'scenarios.json',{'notice':NOTICE,'input_kind':'fictional supplied example','result':result})
    write_json(out/'demo_config.json',specification)
    rows=[]
    print(NOTICE)
    print(f"{'Scenario':30} {'Buffer AUD':>12} {'Delta AUD':>12} {'RTI %':>10} {'Coverage months':>17}")
    for scenario in result['scenarios']:
        m=scenario['metrics'];d=scenario['delta_from_current']
        row={'scenario':scenario['key'],'title':scenario['title'],'status':scenario['status'],'currency':result['currency']}
        row.update({f'input_{k}':v for k,v in scenario['effective_inputs'].items()})
        for key,item in m.items():row[key]=item['value'];row[f'{key}_reason']=item['reason']
        for key,item in d.items():row[f'delta_{key}']=item['value'];row[f'delta_{key}_reason']=item['reason']
        row['assumptions']=' | '.join(scenario['assumptions']);row['notice']=NOTICE;rows.append(row)
        rti=Decimal(m['repayment_to_income']['value'])*100
        print(f"{scenario['title']:30} {Decimal(m['cash_buffer']['value']):12.2f} {Decimal(d['cash_buffer']['value']):12.2f} {rti:10.2f} {Decimal(m['savings_coverage']['value']):17.3f}")
    with (out/'scenario_comparison.csv').open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    # Plotting dependencies belong to this example/export layer, not the calculator.
    os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'outputs/.mplconfig'))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    values=[float(r['cash_buffer']) for r in rows]
    fig,ax=plt.subplots(figsize=(11,5.8),layout='constrained')
    currency=result['currency'];drop=result['settings']['income_drop_percent'];reduction=result['settings']['bnpl_reduction']
    labels=['Current','Added BNPL',f'Income -{drop}%',f'Added BNPL\n+ income -{drop}%',f'Existing BNPL\n-{currency}{reduction} (hypothetical)']
    bars=ax.bar(labels,values,color=['#126b77' if v>0 else '#bf6036' if v<0 else '#697887' for v in values],width=.6)
    ax.bar_label(bars,labels=[f'{currency} {v:,.0f}' for v in values],padding=5,fontsize=11)
    ax.axhline(0,color='black',lw=1)
    ax.axhline(values[0],color='#697887',linestyle='--',lw=1,label=f'Current buffer: {currency}{values[0]:,.0f}')
    ax.set_ylim(-400,1400);ax.set_ylabel(f'Monthly cash flow buffer ({currency})')
    ax.set_title('Independent scenarios relative to current; combined shock is explicitly labeled',fontsize=10)
    ax.spines[['top','right']].set_visible(False);ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True);ax.legend(loc='upper left',fontsize=9)
    fig.suptitle('BNPL monthly repayment stress scenarios',fontsize=15)
    fig.supxlabel(NOTICE+'\nA positive monthly buffer does not guarantee enough cash on every due date.',fontsize=10)
    fig.savefig(out/'scenario_comparison.png',dpi=180);plt.close(fig)
    sources=['src/input_validation.py','src/bnpl_simulator.py','src/simulator_presentation.py','src/simulator_demo.py','config/simulator_demo.json']
    write_json(out/'manifest.json',{'notice':NOTICE,'currency':result['currency'],'scenario_count':len(rows),'input_kind':'fictional','model_or_dataset_loaded':False,'source_sha256':{p:sha256(ROOT/p) for p in sources},'output_sha256':{p.name:sha256(p) for p in out.iterdir() if p.is_file()}})
    print(f'Saved comparison table, full assumptions and chart: {out}')
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output-dir',default='outputs/simulator/stage6_demo_v1');args=parser.parse_args();export_demo(args.output_dir)
