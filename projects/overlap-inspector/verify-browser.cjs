/* SPDX-License-Identifier: GPL-3.0-only */
// Run with PLAYWRIGHT_MODULE pointing to an installed playwright package.
const {chromium}=require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const assert=require('node:assert/strict');
const path=require('node:path');
const fs=require('node:fs');
const {pathToFileURL}=require('node:url');
(async()=>{
 const browser=await chromium.launch({headless:true, ...(process.env.CHROME_PATH?{executablePath:process.env.CHROME_PATH}:{})});
 try {
  const page=await browser.newPage({viewport:{width:1360,height:1100}});
  const errors=[],requests=[];
  page.on('pageerror',e=>errors.push(e.message));
  page.on('request',r=>requests.push(r.url()));
  await page.goto(pathToFileURL(path.join(__dirname,'index.html')).href);
  const pick=async id=>page.locator('#scenario').selectOption(id);
  const summary=()=>page.locator('#resultSummary').textContent();
  await page.locator('#plot circle').first().waitFor();
  assert.match(await summary(),/1 retained · 1 suppressed/);
  await pick('flipped');
  assert.match(await summary(),/1 retained · 1 suppressed/);
  await page.getByRole('button',{name:'Keypoint OKS',exact:true}).click();
  assert.match(await summary(),/2 retained · 0 suppressed/);
  await pick('directional');
  assert.match(await summary(),/2 retained · 0 suppressed/);
  await page.locator('#order').selectOption('10');
  assert.match(await summary(),/1 retained · 1 suppressed/);
  await page.locator('#boundary').click();
  assert.match(await summary(),/2 retained · 0 suppressed/);
  const exact=Number(await page.locator('#thresholdNumber').inputValue());
  await page.locator('#thresholdNumber').fill(String(exact-1e-8));
  await page.locator('#thresholdNumber').press('Tab');
  assert.match(await summary(),/1 retained · 1 suppressed/);
  await pick('chain');
  await page.getByRole('button',{name:'Box IoU',exact:true}).click();
  assert.match(await summary(),/2 retained · 1 suppressed/);
  await page.locator('#order').selectOption('102');
  assert.match(await summary(),/1 retained · 2 suppressed/);
  const before=await page.locator('#plot rect').count();
  await page.locator('#boxes').uncheck();
  assert.equal(await page.locator('#plot rect').count(),0);assert.equal(before,3);
  await page.locator('#boxes').check();
  await page.locator('#pair').selectOption('0,2');
  assert.match(await page.locator('#measurements').textContent(),/OKS A → C/);
  await page.locator('#order').selectOption('tie');
  assert.match(await page.locator('#announcement').textContent(),/threshold 0.5/);
  await pick('missing');
  assert.match(await summary(),/2 retained · 0 suppressed · 1 unavailable/);
  await pick('degenerate');
  await page.getByRole('button',{name:'Keypoint OKS',exact:true}).click();
  assert.match(await summary(),/2 retained · 0 suppressed/);
  await page.locator('#thresholdNumber').fill('1.5');
  await page.locator('#thresholdNumber').press('Tab');
  assert.equal(await page.locator('#thresholdNumber').inputValue(),'0');
  assert.match(await page.locator('#announcement').textContent(),/between 0 and 1/);
  // Exercise the actual range input using the keyboard.
  await page.locator('#threshold').focus();await page.keyboard.press('ArrowRight');
  assert.equal(await page.locator('#thresholdNumber').inputValue(),'0.001');
  // Cross-check every selectable oracle boundary through the public DOM controls.
  const cases=await page.evaluate(()=>DATA.cases.map(c=>({id:c.id,tables:c.tables})));
  let boundaryViews=0;
  for(const c of cases){
   await pick(c.id);
   for(const method of ['iou','oks']){
    await page.locator('#'+method).click();
    for(const [order,rows]of Object.entries(c.tables[method])){
     await page.locator('#order').selectOption(order);
     for(const row of rows){
      await page.locator('#thresholdNumber').fill(String(row.lower));
      await page.locator('#thresholdNumber').press('Tab');
      assert.deepEqual(await page.locator('#states strong').allTextContents(),row.states);
      boundaryViews++;
     }
    }
   }
  }
  await pick('chain');await page.locator('#iou').click();await page.locator('#order').selectOption('102');
  const output=process.env.DEMO_OUTPUT || '/private/tmp/overlap-demo-verification';
  fs.mkdirSync(output,{recursive:true});
  await page.screenshot({path:path.join(output,'desktop.png'),fullPage:true});
  await page.setViewportSize({width:390,height:844});
  const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth);
  assert.equal(overflow,false);
  await page.screenshot({path:path.join(output,'mobile.png'),fullPage:false});
  await page.locator('#threshold').scrollIntoViewIfNeeded();
  await page.screenshot({path:path.join(output,'mobile-controls.png'),fullPage:false});
  await page.getByText('Implementation, provenance & limits',{exact:true}).click();
  assert.match(await page.locator('#provenance').textContent(),/498 full-filter runs/);
  // Runtime performs no HTTP requests, including fonts/CDNs.
  assert.equal(requests.filter(u=>/^https?:/.test(u)).length,0);
  assert.deepEqual(errors,[]);
  const report={browser:await browser.version(),viewportChecks:['1360x1100','390x844'],boundaryViews,pageErrors:errors,httpRequests:0,checks:['default suppression','metric switch','directional score reversal','exact equality and just below boundary','three-instance context','bounding-box toggle','pair selection','tied scores','missing/unavailable','zero area','invalid threshold recovery','keyboard slider','all oracle boundary states','mobile overflow','source disclosure','offline file launch']};
  fs.writeFileSync(path.join(output,'browser-results.json'),JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify(report,null,2));
 } finally {await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
