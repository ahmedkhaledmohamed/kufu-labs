// Uses an installed Playwright package and isolated headless browser, no user profile.
const {chromium}=require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {pathToFileURL,fileURLToPath}=require('node:url');
const root=path.resolve(__dirname,'..');
(async()=>{
 const browser=await chromium.launch({headless:true,...(process.env.CHROME_PATH?{executablePath:process.env.CHROME_PATH}:{})});
 try {
  const page=await browser.newPage({viewport:{width:1440,height:1100}});
  page.setDefaultTimeout(5000);
  fs.writeFileSync(path.join(__dirname,'verification.json'),JSON.stringify({status:'running'})+'\n');
  const errors=[],httpRequests=[];page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(/^https?:/.test(r.url()))httpRequests.push(r.url());});
  const home=pathToFileURL(path.join(root,'index.html')).href;
  await page.goto(home);
  await page.locator('#problemList details').last().waitFor({state:'attached'});
  assert.equal(await page.locator('#problemList details').count(),25);
  assert.equal(await page.locator('#sourceList article').count(),15);
  await page.getByLabel('Search problems, evidence or tools').fill('provenance');
  assert.match(await page.locator('#problemCount').textContent(),/of 25/);
  assert.ok(await page.locator('#problemList details:visible').count()>=2);
  await page.getByLabel('Domain',{exact:true}).selectOption('Behavioural neuroscience');
  await page.getByLabel('Work state',{exact:true}).selectOption('Local patch verified');
  assert.equal(await page.locator('#problemList details:visible').count(),1);
  await page.getByLabel('Search problems, evidence or tools').fill('nothing-matches-7cf5');
  assert.equal(await page.locator('#empty').isVisible(),true);
  await page.getByRole('button',{name:'Clear filters',exact:true}).click();
  assert.equal(await page.locator('#problemList details:visible').count(),25);
  await page.locator('#problem-pairwise-overlap summary').click();
  assert.match(await page.locator('#problem-pairwise-overlap .body').textContent(),/one source family/i);
  await page.getByRole('link',{name:'Problem and evidence',exact:true}).first().click();
  assert.equal(await page.locator('#problem-pairwise-overlap').getAttribute('open'),'');
  await page.goto(home+'#problem-deleted-flags');
  assert.equal(await page.locator('#problem-deleted-flags').getAttribute('open'),'');
  assert.match(await page.locator('#problem-deleted-flags').textContent(),/No fix implemented/);
  const board=page.locator('#sourceList article').filter({has:page.getByRole('heading',{name:'SLEAP issues and discussions',exact:true})});
  await board.getByRole('button',{name:'Show related problems'}).click();
  assert.equal(await page.locator('#sourceFilter').inputValue(),'sleap');
  const shown=await page.locator('#problemList details:visible .title').allTextContents();
  assert.ok(shown.includes('Inspect pairwise IoU / OKS while tuning duplicate filtering'));
  await page.getByRole('button',{name:'Clear filters',exact:true}).click();
  // Every exploration opens a real page; documentation renders as readable HTML.
  const entries=await page.locator('#explorationList h3 a').evaluateAll(nodes=>nodes.map(n=>({title:n.textContent,href:n.href})));
  for(const entry of entries){await page.goto(entry.href);assert.ok(await page.locator('h1').first().isVisible());await page.goto(home);}
  await page.getByRole('link',{name:'Pose-review task validation',exact:true}).click();
  assert.equal(await page.locator('main table').count()>0,true);
  assert.match(await page.locator('main').textContent(),/later approved|later authorised|later approved/i);
  await page.getByRole('link',{name:'Scientific software lab',exact:true}).click();
  await page.getByRole('link',{name:'Pairwise overlap inspector',exact:true}).first().click();
  await page.locator('#scenario').selectOption('flipped');
  await page.getByRole('button',{name:'Keypoint OKS',exact:true}).click();
  assert.match(await page.locator('#resultSummary').textContent(),/2 retained/);
  await page.goBack();assert.equal(await page.title(),'Scientific software lab');
  await page.getByRole('link',{name:'Validation',exact:true}).click();
  assert.match(await page.locator('#validationList').textContent(),/not the whole|not the whole dedicated-array/);
  const output=process.env.HUB_OUTPUT || '/private/tmp/lab-hub-verification';fs.mkdirSync(output,{recursive:true});
  await page.goto(home);
  await page.screenshot({path:path.join(output,'desktop.png'),fullPage:false});
  await page.locator('#problem-pairwise-overlap summary').click();
  await page.locator('#problem-pairwise-overlap').scrollIntoViewIfNeeded();
  await page.screenshot({path:path.join(output,'evidence.png'),fullPage:false});
  await page.setViewportSize({width:390,height:844});await page.goto(home);
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
  await page.screenshot({path:path.join(output,'mobile.png'),fullPage:false});
  await page.getByRole('link',{name:'Problem board',exact:true}).click();
  await page.getByLabel('Search problems, evidence or tools').fill('microscopy');
  assert.ok(await page.locator('#problemList details:visible').count()>0);
  await page.locator('#problem-label-free summary').click();
  await page.locator('#problem-label-free').scrollIntoViewIfNeeded();
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
  await page.screenshot({path:path.join(output,'mobile-problem.png'),fullPage:false});
  // Audit all local links on the hub and generated research pages without visiting external sites.
  const recordFiles=fs.readdirSync(path.join(__dirname,'records')).filter(f=>f.endsWith('.html'));
  const files=[path.join(root,'index.html'),...recordFiles.map(f=>path.join(__dirname,'records',f))];
  let localLinks=0;
  for(const file of files){
   await page.goto(pathToFileURL(file).href);
   const links=await page.locator('a[href]').evaluateAll(nodes=>nodes.map(n=>n.href));
   for(const href of links){if(href.startsWith('file:')){const url=new URL(href);url.hash='';url.search='';const target=fileURLToPath(url);assert.equal(fs.existsSync(target),true,`Missing ${target} linked from ${file}`);localLinks++;}}
  }
  assert.deepEqual(errors,[]);assert.deepEqual(httpRequests,[]);
  const report={browser:await browser.version(),node:process.versions.node,playwright:require(path.join(process.env.PLAYWRIGHT_MODULE || 'playwright','package.json')).version,problems:25,sourceBoards:15,explorations:entries.length,researchPages:recordFiles.length,localLinks,viewports:['1440x1100','390x844'],pageErrors:errors,httpRequests:0,checks:['search and compound filters','empty and reset state','deep-link opening','evidence details','source-board filter','all exploration links','readable research tables','demo control and browser return','validation scope','desktop/mobile screenshot review','mobile horizontal overflow','all local document links','standalone offline browsing']};
  fs.writeFileSync(path.join(output,'results.json'),JSON.stringify(report,null,2)+'\n');fs.writeFileSync(path.join(__dirname,'verification.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));
 }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
