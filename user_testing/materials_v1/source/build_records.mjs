import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';

const root=process.env.BNPLGUARD_PROJECT_ROOT ?? path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../..');
const out=`${root}/user_testing/materials_v1`;
const qa=`${root}/outputs/user_testing/materials_v1`;
await fs.mkdir(out,{recursive:true});await fs.mkdir(qa,{recursive:true});
const wb=Workbook.create();
const allocations=[['P01','A','B'],['P02','B','A'],['P03','A','B']];
const sessions=wb.worksheets.add('Sessions');
const headers=['Participant ID','Text case (first)','App case (second)','Device','Browser','App commit','Nondeveloper confirmed','Consent','Text active seconds','App active seconds','Assisted seconds','Loading pause seconds','Any hint','Subjective clarity 1-5','Verbatim feedback','Technical notes'];
sessions.getRange('A1:P1').values=[headers];
sessions.getRange('A2:P4').values=allocations.map(a=>[...a,...Array(13).fill(null)]);
const responses=wb.worksheets.add('Responses');
const responseHeaders=['Participant ID','Text case','App case','Item ID','Independent original response','Before-help objective score','Hint code(s)','Exact hint and timing','Response after help','After-help objective score','Disposition / notes'];
responses.getRange('A1:K1').values=[responseHeaders];
const rows=[];
for(const a of allocations){
  for(const part of ['T','A'])for(let i=1;i<=6;i++)rows.push([...a,`${part}${i}`,...Array(7).fill(null)]);
  rows.push([...a,'S1',...Array(7).fill(null)]);
}
responses.getRange('A2:K40').values=rows;
for(const [sheet,cols,last] of [[sessions,'P',4],[responses,'K',40]]){
  sheet.showGridLines=false;
  sheet.getRange(`A1:${cols}${last}`).format.font={name:'Arial',size:10,color:'#183047'};
  sheet.getRange(`A1:${cols}${last}`).format.verticalAlignment='top';
  sheet.getRange(`A1:${cols}${last}`).format.wrapText=true;
  sheet.getRange(`A1:${cols}1`).format={fill:'#183047',font:{name:'Arial',bold:true,color:'#FFFFFF',size:10},rowHeight:48,verticalAlignment:'center',horizontalAlignment:'center',wrapText:true};
  sheet.getRange(`A2:${cols}${last}`).format.rowHeight=44;
  sheet.getRange(`A1:${cols}${last}`).format.columnWidth=16;
  sheet.freezePanes.freezeRows(1);sheet.freezePanes.freezeColumns(3);
  sheet.getRange(`A2:C${last}`).format.fill='#F0F3F6';
  sheet.getRange(`A1:${cols}${last}`).format.borders={insideHorizontal:{style:'thin',color:'#E4E9ED'}};
}
sessions.getRange('D2:P4').format.fill='#FFFCF0';
sessions.getRange('O1:P4').format.columnWidth=40;
sessions.getRange('G1:H4').format.columnWidth=18;
sessions.getRange('N1:N4').format.columnWidth=20;
sessions.getRange('I2:L4').setNumberFormat('0.0');
sessions.getRange('N2:N4').setNumberFormat('0');
for(const col of ['G','H','M'])sessions.getRange(`${col}2:${col}4`).dataValidation={rule:{type:'list',values:['Yes','No']}};
sessions.getRange('N2:N4').dataValidation={rule:{type:'whole',operator:'between',formula1:1,formula2:5}};
responses.getRange('A1:C40').format.columnWidth=13;
responses.getRange('D1:D40').format.columnWidth=10;
responses.getRange('E1:E40').format.columnWidth=34;
responses.getRange('H1:I40').format.columnWidth=31;
responses.getRange('K1:K40').format.columnWidth=25;
responses.getRange('E2:K40').format.fill='#FFFCF0';
responses.getRange('F2:F40').setNumberFormat('0');responses.getRange('J2:J40').setNumberFormat('0');
for(let i=0;i<rows.length;i++){
  const row=i+2;const max=rows[i][3]==='S1'?2:1;
  for(const col of ['F','J'])responses.getRange(`${col}${row}`).dataValidation={rule:{type:'whole',operator:'between',formula1:0,formula2:max}};
}
wb.recalculate();
// A completely uncollected study must not display zero scores or fabricated quotes.
if(sessions.getRange('D2:P4').values.flat().some(v=>v!==null&&v!==''))throw Error('Session results are not blank');
if(responses.getRange('E2:K40').values.flat().some(v=>v!==null&&v!==''))throw Error('Response results are not blank');
const scan=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!|#N/A|#SPILL!|#CALC!',options:{useRegex:true,maxResults:10},maxChars:1000});
await fs.writeFile(`${qa}/workbook_inspection.json`,JSON.stringify({allocations,responseRows:rows.length,allResultsBlank:true,formulaScan:scan.ndjson},null,2));
for(const [name,range] of [['Sessions','A1:P5'],['Responses','A1:K8']]){
  const preview=await wb.render({sheetName:name,range,scale:1.3,format:'png'});
  await fs.writeFile(`${qa}/${name.toLowerCase()}_preview.png`,new Uint8Array(await preview.arrayBuffer()));
}
await (await SpreadsheetFile.exportXlsx(wb)).save(`${out}/anonymous_results.xlsx`);
console.log(JSON.stringify({sheets:['Sessions','Responses'],sessionRows:3,responseRows:39,allResultsBlank:true}));
