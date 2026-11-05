"""Create the two English user-study PDFs without changing application code."""
from pathlib import Path
import json, shutil
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'user_testing/materials_v1'
OUT.mkdir(parents=True,exist_ok=True)
VERIFIED=json.loads((OUT/'cases_verified.json').read_text())
URL='https://bnplguard-yixuan502.streamlit.app/'
VERSION='771aadd7b8c15de4c972d9b634f01e50ce9f0eb2'
W,H=A4; M=44; WIDTH=W-2*M
INK=colors.HexColor('#183047'); TEAL=colors.HexColor('#176B87')
GREY=colors.HexColor('#536374'); LINE=colors.HexColor('#CCD5DD')
BODY=ParagraphStyle('body',fontName='Helvetica',fontSize=10.1,leading=14,textColor=INK)
SMALL=ParagraphStyle('small',parent=BODY,fontSize=8.7,leading=12)
HEAD=ParagraphStyle('head',parent=BODY,fontName='Helvetica-Bold',fontSize=13,leading=17)

class PDF:
    def __init__(self,path,audience,pages):
        self.c=canvas.Canvas(str(path),pagesize=A4)
        self.c.setTitle('BNPLGuard '+audience)
        self.c.setAuthor('BNPLGuard project')
        self.audience=audience;self.pages=pages;self.page=0
    def new(self,title,kicker=None):
        if self.page:self.c.showPage()
        self.page+=1;self.y=H-48
        self.c.setFillColor(TEAL);self.c.setFont('Helvetica-Bold',10)
        self.c.drawString(M,self.y,'BNPLGuard')
        self.c.setFillColor(GREY);self.c.setFont('Helvetica',8.5)
        self.c.drawRightString(W-M,self.y,self.audience+' | Materials v1')
        self.y-=17;self.c.setStrokeColor(LINE);self.c.line(M,self.y,W-M,self.y)
        self.y-=31;self.c.setFillColor(INK);self.c.setFont('Helvetica-Bold',20)
        self.c.drawString(M,self.y,title);self.y-=22
        if kicker:self.p(kicker,SMALL)
        self.c.setFillColor(GREY);self.c.setFont('Helvetica',8)
        self.c.drawString(M,27,'5 November 2026 | Fictional cases only')
        self.c.drawRightString(W-M,27,f'{self.page} / {self.pages}')
    def p(self,text,style=BODY,gap=9):
        para=Paragraph(text,style);_,height=para.wrap(WIDTH,900)
        assert self.y-height>48,('Page overflow',self.page,text)
        para.drawOn(self.c,M,self.y-height);self.y-=height+gap
    def h(self,text):self.p(text,HEAD,7)
    def table(self,rows,widths=None):
        white=ParagraphStyle('white',parent=SMALL,textColor=colors.white,fontName='Helvetica-Bold')
        rows=[[Paragraph(str(v),white if i==0 else SMALL) for v in row] for i,row in enumerate(rows)]
        t=Table(rows,colWidths=widths or [WIDTH/len(rows[0])]*len(rows[0]),hAlign='LEFT')
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),INK),('TEXTCOLOR',(0,0),(-1,0),colors.white),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),('LINEBELOW',(0,0),(-1,0),.5,INK),('LINEBELOW',(0,1),(-1,-1),.35,LINE)]))
        _,height=t.wrap(WIDTH,900);assert self.y-height>48,('Table overflow',self.page)
        t.drawOn(self.c,M,self.y-height);self.y-=height+13
    def field(self,name,height=28,multiline=False,maxlen=300):
        assert self.y-height>48
        self.c.acroForm.textfield(name=name,tooltip=name.replace('_',' '),x=M,y=self.y-height,width=WIDTH,height=height,
            fontName='Helvetica',fontSize=10,borderWidth=.7,borderColor=LINE,fillColor=colors.white,textColor=INK,
            forceBorder=True,fieldFlags='multiline' if multiline else '',maxlen=maxlen,value='')
        self.y-=height+13
    def save(self):assert self.page==self.pages;self.c.save()

QUESTIONS=[
 'Before the proposed new BNPL repayment, what is the current monthly cash buffer? Give an AUD amount.',
 'What is the monthly cash buffer after adding only the proposed new BNPL repayment?',
 'Compared with the current situation, by how much does the buffer change after only that new repayment? Give an amount and direction.',
 'What is the final monthly cash buffer if the stated income is 20% lower and the proposed new BNPL repayment also applies?',
 'Compared with the current situation, by how much does the buffer change in that combined scenario? Give an amount and direction.',
 'In that combined scenario, is there a surplus, a shortfall, or exactly zero?'
]
participant=PDF(OUT/'participant_test_sheet.pdf','Participant sheet',4)
participant.new('Your 10-minute app test')
participant.p('Use fictional information only. Do not enter your own income, debts, savings, name or contact details. Participation is voluntary; you may skip a question or stop.')
participant.p('Your facilitator will give you an anonymous ID and tell you which case to use first. You can type in the blank PDF fields or write on a printed copy.')
participant.p('Anonymous ID (provided by the facilitator):',gap=5);participant.field('participant_id',25,maxlen=3)
participant.p('Part 1: text-only case / Part 2: app case (provided by the facilitator):',gap=5);participant.field('assigned_case_order',25,maxlen=60)
participant.h('1. Text-only task')
participant.p('Read your first assigned case and answer its six questions independently. Do not open BNPLGuard yet. A basic calculator is allowed. If unsure, write your best answer or "not sure". Tell the facilitator when you have finished.')
participant.h('2. App task')
participant.p('When the facilitator says Part 2 starts, open the public app below. Use the <b>Stress</b> area for your other assigned case and answer the same six questions on that case page. Enter the case values rather than loading the default financial example. Use AUD, a 20% income reduction and zero hypothetical reduction of existing BNPL.')
participant.p(f'<link href="{URL}" color="#176B87">{URL}</link>')
participant.p('A basic calculator is also allowed in this part. Tell the facilitator before changing an answer you have already submitted. You may ask for help; they will first preserve what you have done independently.')
participant.h('3. Final reflection')
participant.p('After the case tasks, complete the Screen activity and feedback on page 4. All cases and questionnaire examples are fictional.')

for case in ['A','B']:
    participant.new('Case '+case,'Use this page only in the part assigned by your facilitator.')
    p=VERIFIED[case]['inputs']
    participant.p('All amounts are AUD. Income, living expenses and repayments are monthly. Necessary living expenses exclude every debt and BNPL repayment listed separately. Emergency savings is an available balance today. Other assumptions remain unchanged in each scenario.',SMALL)
    rows=[['Fictional information','AUD'],['Monthly after-tax income',f"{p['I']:,}"],['Necessary living expenses',f"{p['E']:,}"],['Non-BNPL debt repayments',f"{p['D']:,}"],['Existing BNPL repayments',f"{p['B0']:,}"],['Proposed new BNPL repayments',f"{p['Bnew']:,}"],['Available emergency savings',f"{p['S']:,}"]]
    participant.table(rows,[WIDTH*.76,WIDTH*.24])
    # Six short answers fit on one case page without revealing scoring or solutions.
    for i,q in enumerate(QUESTIONS,1):
        participant.p(f'<b>Q{i}.</b> '+q,SMALL,4)
        participant.field(f'case_{case}_Q{i}',22,maxlen=160)
participant.new('Screen and your feedback')
participant.p('When the facilitator asks, open <b>Screen</b>, select <b>Load fictional example</b>, then <b>Run screening</b>. Use that questionnaire example, rather than the AUD case values.')
participant.p('<b>S1.</b> In your own words, what does the displayed Screen percentage estimate? What conclusion would you avoid drawing from it?',gap=5)
participant.field('screen_meaning_original',110,True,1400)
participant.p('<b>Clarity.</b> How clear was the app when comparing the monthly scenarios? Choose one number: 1 = very unclear, 2 = unclear, 3 = neither clear nor unclear, 4 = clear, 5 = very clear.',gap=5)
participant.field('subjective_clarity_1_to_5',26,maxlen=1)
participant.p('<b>One comment.</b> In your own words, describe one thing that was clear or easy to misunderstand. Do not include personal financial information.',gap=5)
participant.field('verbatim_feedback',125,True,1400)
participant.p('Thank you. Please return this sheet to the facilitator. You may explain anything you want to add after your independent responses have been recorded.',SMALL)
participant.save()

guide=PDF(OUT/'facilitator_guide_and_answers.pdf','Facilitator only',5)
guide.new('Study setup and allocation')
guide.p('<b>Research question:</b> After using the simulator, can users correctly identify the effects of added monthly BNPL repayments and lower income on the monthly cash buffer? This is preparation only. No participant data have been collected.')
guide.p('<b>Recruitment:</b> three real people who did not develop the application. Project A Tech Team, PDF p.3, requires at least three test users and a structured feedback instrument. Marking Criteria A Tech Team, PDF p.4 (Results and Evaluation), also specifies at least three users and a structured instrument. Nondeveloper recruitment is an additional requirement of this protocol. Do not count developers or fictional QA as users.',SMALL)
guide.table([['Anonymous ID','Part 1: text only','Part 2: app'],['P01','Case A','Case B'],['P02','Case B','Case A'],['P03','Case A','Case B']])
guide.p('Keep text first and app second for every participant. Only case allocation is alternated. With three participants the case distribution is 2:1, not fully balanced. Keep the unused case hidden until Part 2; collect or cover the first case sheet after its answers are locked.',SMALL)
guide.h('Before anyone starts')
guide.p(f'Open {URL} without requiring participant login. Warm the service before timing, check Screen/Stress are usable, then start a fresh empty session. Use the same device, calculator policy and script within each session. Do not demonstrate answers or the default financial example beforehand.')
guide.p(f'Planned app revision: <b>{VERSION[:7]}</b>. Source: docs/deployment.md and outputs/deploy/stage8_v1/acceptance.json. Current GitHub main was checked as the same full revision. Live browser Screen loaded without a login prompt during material preparation. The page does not display a commit hash; version attribution combines the deployment receipt and unchanged main, not a browser-read hash. Recheck at each session; enter the actual verified commit in the blank workbook field. Stop and document an unexpected version or access failure.',SMALL)
guide.p('Use the three preassigned IDs only. Do not record names, emails, ages or real finances. One member leads each session; an optional observer records notes silently. Keep one shared master workbook with a designated editor per session; do not overwrite another member\'s edits. Do not send the guide or workbook to participants.',SMALL)

guide.new('Script and timing')
guide.h('Read this opening verbatim')
guide.p('"We are testing how this application communicates fictional monthly scenarios, not testing you. This takes about ten minutes. We will record anonymous answers, times and a short comment; no real financial details, names, audio or video. You may skip a question or stop. Please first work from one written case without the app, then use the app for a different case. A basic calculator is allowed in both parts. I will preserve your first answers before helping. Is that OK, and did you take part in developing this app?"')
guide.p('Record consent and nondeveloper confirmation in Sessions. If consent is declined or the person is a developer, do not run or score a session; do not fabricate a replacement record. Recruit another nondeveloper under a new explicit ID if needed.',SMALL)
guide.table([['Elapsed target','Action'],['0:00-1:00','Opening, consent, ID and case allocation.'],['1:00-3:00','Text-only case, six answers independently. Lock T1-T6.'],['3:00-6:00','Other case in Stress independently. Lock A1-A6.'],['6:00-7:00','Optional standardized assistance and revised answers. Keep originals unchanged.'],['7:00-8:30','Fictional Screen task and S1 interpretation. Preserve original before meaning help.'],['8:30-9:30','Subjective clarity and one verbatim comment.'],['9:30-10:00','Close and save. Debrief only after answers/ratings are locked.']],[WIDTH*.25,WIDTH*.75])
guide.p('Use a stopwatch. Start each active task when its case/instructions are available and stop at completion or the stated limit. Record seconds separately for text, app and assisted review. Pause only for observable technical loading/failure; record total paused seconds and reason. Do not pause for thinking, typing or navigation. Ten minutes is approximate; extend for technical delay and record it.',SMALL)
guide.p('At each cutoff say: "Please give your independent responses now, including any you are unsure about." Copy exactly, mark unattempted items, then lock them. Do not correct or praise accuracy. If help is requested early, first lock the entire current part (including blanks); mark its independent phase ended, then help. Never describe assisted work as independent.',SMALL)

guide.new('Assistance and recording')
guide.p('Before both independent case parts are locked, only repeat written wording verbatim or resolve access problems. If operational help is needed earlier, lock that part first. Defer numerical feedback and conceptual teaching until both independent parts are locked. Use the lowest applicable prompt and preserve its exact words.',SMALL)
guide.table([['Code','Permitted standardized prompt'],['H0','No help, or verbatim repetition only. Note which wording was repeated.'],['H1 navigation','"The four areas are at the top. Open Stress for the financial case."'],['H2 operation','"Use the field labels to enter the supplied case. Set currency to AUD, income reduction to 20%, and hypothetical BNPL reduction to zero."'],['H3 operation','"Use Compare scenarios. You can inspect a scenario and its displayed explanation."'],['H4 concept','Only after BOTH independent sets are locked: "Monthly cash buffer uses monthly income, living expenses and repayments. A change from current is a difference; the final buffer is a level. Please review your answer."'],['TECH','URL/load/connection assistance. Record pause time and cause. Do not supply numeric results.']],[WIDTH*.23,WIDTH*.77])
guide.p('Allow up to one minute of assisted review. Ask "Would you like to revise any answer?" Record a revised answer only if given. Do not overwrite originals. If no help/revision occurred, leave after-help response/score blank; do not copy an independent answer into it. Give no answer-key amounts until all responses and feedback are frozen.',SMALL)
guide.h('Workbook entry rules')
guide.p('<b>Sessions</b>: one row per ID. Fill device/browser, actual app commit, consent and nondeveloper check, active seconds, paused seconds, whether any prompt occurred, subjective clarity 1-5, and one exact quote. Clarity and the quote are subjective, not comprehension scores.')
guide.p('<b>Responses</b>: one row per item, linked by ID and case allocation. T1-T6 = text Q1-Q6; A1-A6 = app Q1-Q6; S1 = Screen interpretation. Original answer and before score are separate from hint code/details, revised answer and after score. Item IDs are structural labels, not results. Copy the participant\'s actual words, including signs and units.')
guide.p('Before collection, blank means not yet collected. During a completed timed part, record "NR" for no answer and score 0. For withdrawal or technical failure, use "WITHDRAWN" or "TECH" and leave the score blank; retain the reason. Do not convert missing/failed sessions to zero. All populated scores must describe real observed responses.',SMALL)

guide.new('Simulator-verified answer key')
guide.p('All amounts are AUD. Verified with the unchanged src.simulator_presentation.run_simulation in the project .venv, income_drop=0.2 and bnpl_reduction=0. The raw verification is retained in cases_verified.json beside these materials. These are standard answers, not participant observations.',SMALL)
guide.table([['Input','Case A','Case B'],['Income I','4,000','5,000'],['Living expenses E','2,200','2,800'],['Other debt D','600','700'],['Existing BNPL B0','300','400'],['New BNPL Bnew','200','300'],['Emergency savings S','800','1,200'],['Income reduction','20%','20%']],[WIDTH*.54,WIDTH*.23,WIDTH*.23])
guide.table([['Item in each part','Case A','Case B'],['Q1 current final buffer','900','1,100'],['Q2 new-BNPL final buffer','700','800'],['Q3 new-only change from current','-200 (decrease 200)','-300 (decrease 300)'],['Q4 combined FINAL buffer','-100','-200'],['Q5 combined CHANGE from current','-1,000 (decrease 1,000)','-1,300 (decrease 1,300)'],['Q6 combined classification','Shortfall','Shortfall']],[WIDTH*.48,WIDTH*.26,WIDTH*.26])
guide.p('<b>Key distinction:</b> A combined final buffer is -100, while its change from the current 900 is -1,000. B combined final buffer is -200, while its change from the current 1,100 is -1,300. A reduction is not the remaining balance.',SMALL)
guide.p('Current = I-E-D-B0. New only = current-Bnew. Combined = 0.8I-E-D-B0-Bnew. Income reduction is applied once to the stated baseline income. Each scenario starts from the current case; changes do not accumulate accidentally. Savings is a stock, not monthly income. E excludes repayments counted separately.',SMALL)

guide.new('Scoring and interpretation')
guide.h('Objective cash-buffer scoring')
guide.p('Award 1 or 0 to each of Q1-Q6 using the key, identically in text and app parts. Q1/Q2/Q4: correct signed final amount. Q3/Q5: correct magnitude AND direction relative to current; "decrease 200" and "-200" are equivalent. A positive magnitude alone is ambiguous when direction is requested and scores 0. Q6: shortfall/deficit/negative buffer is correct. For a negative final amount, "100 shortfall" is equivalent to -100. Accept AUD/dollar notation and exact numeric equivalents within AUD0.01. No partial credit and no credit for method alone.')
guide.p('Compute text and app totals separately, each 0-6, from the before-help scores after collection. Keep assisted totals separately and only for items actually reviewed. Keep denominators explicit when items are TECH/WITHDRAWN. Do not treat blank uncollected cells as zero. Q6 records categorical understanding as well as Q4\'s numeric amount; these items are not independent observations.',SMALL)
guide.h('S1: separate Screen interpretation, 0-2')
guide.p('One point: identifies the estimate as survey financial difficulty covering expenses/paying bills in a typical month. One point: states at least one valid scope limit, such as not BNPL default, not certainty about an individual, not future default/credit approval, or no Australian external validation. Do not give the first point to an answer identifying the target as BNPL default. Preserve contradictory wording for review. Do not add this score to the 0-6 simulator totals.')
guide.p('For this frozen fictional questionnaire, 83.85% is the displayed rounded example, not a required answer to S1. A suitable interpretation is an estimate of the study\'s contemporaneous self-reported financial-difficulty label. It does not establish a personal cause, a BNPL default probability or an approved borrowing amount. Record S1 before explaining this. If a meaning prompt is given afterwards, record the revised text and score separately.',SMALL)
guide.h('After collection')
guide.p('A second member should review raw responses against the fixed key and resolve scoring differences in notes; do not change the key to fit results. Summarize actual item accuracy, within-person text/app totals, times, hints and quotes. Report subjective clarity separately. Three convenience users, the 2:1 case allocation, differing devices, case effects and the fixed text-then-app order limit inference. Practice and assistance can explain changes. This design cannot establish that the simulator causally improves understanding or represents a population. Do not invent feedback, significance or completed fixes.')
guide.p('Store completed materials privately in this project, under anonymous IDs. Keep names/contact lists out of the workbook and do not commit responses or quotes to the deployment repository. This round creates instruments only; no course report, deployment, model, threshold or financial formula is changed.',SMALL)
guide.save()

print(json.dumps({'participant_pages':4,'facilitator_pages':5,'output':str(OUT)}))
