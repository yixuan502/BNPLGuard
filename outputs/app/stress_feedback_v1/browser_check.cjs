const {chromium}=require('playwright');
const fs=require('fs');
const out=__dirname;
const assert=require('assert');
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
 const results=[];
 try {
 for(const [name,width,height] of [['desktop',1280,900],['narrow',390,844]]){
  const context=await browser.newContext({viewport:{width,height}});const page=await context.newPage();page.setDefaultTimeout(30000);
  await page.goto('http://127.0.0.1:8501/');
  await page.getByText('Stress',{exact:true}).click();
  await page.getByRole('button',{name:'Load fictional financial example',exact:true}).click();
  await page.getByRole('spinbutton',{name:'Monthly after-tax income',exact:true}).waitFor();
  await page.waitForFunction(()=>document.querySelectorAll('input[type="number"]')[0]?.value==='4500.00');
  const order=await page.getByRole('spinbutton').evaluateAll(es=>es.slice(0,6).map(e=>({label:e.getAttribute('aria-label'),y:e.getBoundingClientRect().top,x:e.getBoundingClientRect().left})));
  assert(order.length===6 && order.every((e,i)=>!i||e.y>order[i-1].y));
  assert(order.every(e=>Math.abs(e.x-order[0].x)<2));
  await page.getByRole('heading',{name:'Monthly cash flow',exact:true}).scrollIntoViewIfNeeded();
  await page.screenshot({path:`${out}/${name}_monthly.png`});
  await page.getByRole('heading',{name:'Savings balance today',exact:true}).scrollIntoViewIfNeeded();
  await page.screenshot({path:`${out}/${name}_savings.png`});
  await page.getByRole('button',{name:'Compare scenarios',exact:true}).click();
  await page.getByText('Final monthly cash buffer: AUD 900.00',{exact:true}).waitFor();
  for(const value of ['900.00','700.00','0.00','-200.00','1,100.00'])assert(await page.getByText('Final monthly cash buffer: AUD '+value,{exact:true}).count()===1);
  assert(await page.getByText('Status: Shortfall',{exact:true}).count()===1);
  assert(await page.getByText('Status: Break-even',{exact:true}).count()===1);
  const overflow=await page.evaluate(()=>[document.documentElement,...document.querySelectorAll('[data-testid="stMain"], [data-testid="stMainBlockContainer"]')].map(e=>({tag:e.tagName,testid:e.dataset.testid,client:e.clientWidth,scroll:e.scrollWidth})));
  assert(overflow.every(e=>e.scroll<=e.client+1),JSON.stringify(overflow));
  await page.getByRole('heading',{name:'Scenario comparison',exact:true}).scrollIntoViewIfNeeded();
  await page.screenshot({path:`${out}/${name}_results_top.png`});
  await page.getByText('Final monthly cash buffer: AUD -200.00',{exact:true}).scrollIntoViewIfNeeded();
  await page.screenshot({path:`${out}/${name}_results_bottom.png`});
  const newInput=page.getByRole('spinbutton',{name:'Monthly proposed new BNPL repayments',exact:true});await newInput.fill('250');await newInput.press('Tab');
  await page.getByText('Inputs changed. The previous result has been cleared; submit again to calculate.',{exact:true}).waitFor();
  assert(await page.getByText('Final monthly cash buffer:',{exact:false}).count()===0);
  await page.getByRole('button',{name:'Reset simulation',exact:true}).click();
  await page.waitForFunction(()=>[...document.querySelectorAll('input[type="number"]')].slice(0,6).every(e=>e.value===''));
  for(const input of await page.getByRole('spinbutton').all()) {await input.fill('0');await input.press('Tab');}
  await page.getByRole('button',{name:'Compare scenarios',exact:true}).click();
  await page.getByText('Final monthly cash buffer: AUD 0.00',{exact:true}).first().waitFor();
  assert(await page.getByText('N/A',{exact:true}).count()>=2);
  assert(await page.getByText('Status: Break-even',{exact:true}).count()===5);
  await page.getByText('Scenario details: RTI, savings coverage and explanation',{exact:true}).scrollIntoViewIfNeeded();
  await page.screenshot({path:`${out}/${name}_zero.png`});
  results.push({name,viewport:{width,height},input_order:order.map(e=>e.label),single_column_order:true,five_visible_scenario_cards:true,standard_buffers:[900,700,0,-200,1100],input_invalidation:true,reset:true,zero_denominator_NA:true,overflow});
  await context.close();
 }
 fs.writeFileSync(out+'/browser_qa.json',JSON.stringify({browser:await browser.version(),mode:'Headless Google Chrome, fresh isolated contexts',physical_device_tested:false,checks:results},null,2));
 console.log(JSON.stringify(results));
 } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
