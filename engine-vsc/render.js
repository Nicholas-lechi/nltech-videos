const { chromium } = require('playwright');
const fs=require('fs'),{spawn,execFileSync}=require('child_process');
const [,,mode,out]=process.argv;
const TL=JSON.parse(fs.readFileSync('/home/claude/vsc/out/timeline.json'));
const H=process.env.LAYOUT==='h';async function page(b){const p=await b.newPage({viewport:H?{width:1920,height:1080}:{width:1080,height:1920},deviceScaleFactor:1});
  p.on('pageerror',e=>console.log('ERR',e.message));await p.addInitScript(([tl,h])=>{window.__TL__=tl;window.__H__=h},[TL,H]);
  await p.goto(H?'file:///home/claude/vsc/scene-h.html':'file:///home/claude/vsc/scene.html');await p.evaluate(()=>window.ready);return p}
async function part(b,i0,i1,file){const p=await page(b);
  const ff=spawn('ffmpeg',['-y','-loglevel','error','-f','image2pipe','-c:v','mjpeg','-r','30','-i','-','-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p',file],{stdio:['pipe','inherit','inherit']});
  for(let i=i0;i<i1;i++){await p.evaluate(t=>renderAt(t),i/30);const buf=await p.screenshot({type:'jpeg',quality:92});if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));if((i-i0)%300===0)console.log(file.split('/').pop(),i-i0,'/',i1-i0)}
  ff.stdin.end();await new Promise(r=>ff.on('close',r))}
(async()=>{
  const b=await chromium.launch({args:['--allow-file-access-from-files']});
  if(mode==='stills'){const p=await page(b);const ts=process.argv.slice(4).map(Number);
    for(const [i,t] of ts.entries())await p.screenshot({path:`/home/claude/vsc/out/s${i}.jpg`,type:'jpeg',quality:80}).then(()=>0),await p.evaluate(t=>renderAt(t),t),await p.screenshot({path:`/home/claude/vsc/out/s${i}.jpg`,type:'jpeg',quality:80});
  }else{
    const n=Math.round(TL.duration*30),h=Math.ceil(n/2),w='/home/claude/vsc/out';
    await Promise.all([part(b,0,h,w+'/p0.mp4'),part(b,h,n,w+'/p1.mp4')]);
    fs.writeFileSync(w+'/list.txt',`file '${w}/p0.mp4'\nfile '${w}/p1.mp4'\n`);
    execFileSync('ffmpeg',['-y','-loglevel','error','-f','concat','-safe','0','-i',w+'/list.txt','-i',w+'/voice.wav','-map','0:v','-map','1:a','-c:v','copy','-af','loudnorm=I=-14:TP=-1.5','-c:a','aac','-b:a','160k','-ar','48000','-shortest','-movflags','+faststart',out]);
  }
  await b.close();
})();
