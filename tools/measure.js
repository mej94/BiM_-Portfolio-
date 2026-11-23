const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({viewport:{width:1588,height:1123}});
  const out = {};
  for (let n = 6; n <= 25; n++) {
    if ([13,18,22].includes(n)) continue;
    const f = path.resolve(__dirname, '../spread/page' + String(n).padStart(2,'0') + '.html');
    await p.goto('file://' + f); await p.waitForTimeout(150);
    out[n] = await p.evaluate(() => [...document.querySelectorAll('body > .abs')].filter(e => !e.matches('.hdr,.ftr,.left')).map(e => {
      const r = e.getBoundingClientRect(), k = 25.4/96; return [r.left*k, r.top*k, r.width*k, r.height*k, e.querySelector('img') ? e.querySelector('img').getAttribute('src') : null];
    }));
  }
  fs.writeFileSync(path.join(__dirname, 'boxes.json'), JSON.stringify(out)); await b.close();
})();
