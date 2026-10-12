// Renderiza cenas.html quadro a quadro e junta com o áudio original.
// Uso: node render.js <audio> <saida.mp4> [--preview t1,t2,...]
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const [audio, out, flag, times] = process.argv.slice(2);
const FPS = 30, DUR = +(process.env.DUR || 44.72);
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  await page.goto('file://' + path.resolve(__dirname, 'cenas.html'));
  await page.evaluate(() => window.ready);
  const frame = t => page.evaluate(t => { renderFrame(t); return document.getElementById('c').toDataURL('image/jpeg', 0.93); }, t);
  if (flag === '--preview') {
    for (const t of times.split(',')) {
      const d = await frame(+t);
      fs.writeFileSync(`${out}-${t}.jpg`, Buffer.from(d.split(',')[1], 'base64'));
    }
    return browser.close();
  }
  const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
    '-i', audio, '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p',
    '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  const total = Math.ceil(DUR * FPS);
  for (let i = 0; i < total; i++) {
    const d = await frame(i / FPS);
    if (!ff.stdin.write(Buffer.from(d.split(',')[1], 'base64'))) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 150 === 0) console.log(`quadro ${i}/${total}`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await browser.close();
})();
