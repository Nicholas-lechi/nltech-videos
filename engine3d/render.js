const { chromium } = require('playwright');
const fs=require('fs'),{spawn}=require('child_process');
const [,,mode,out]=process.argv;
(async()=>{
  const TL=JSON.parse(fs.readFileSync('/home/claude/v3d/timeline.json'));
  const b=await chromium.launch({args:['--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist','--allow-file-access-from-files']});
  const p=await b.newPage({viewport:{width:1080,height:1920},deviceScaleFactor:1});
  p.on('console',m=>{if(m.type()==='error')console.log('PAGE',m.text())});p.on('pageerror',e=>console.log('ERR',e.message));
  await p.addInitScript(tl=>{window.__TL__=tl},TL);
  await p.goto('file:///home/claude/v3d/scene.html');await p.evaluate(()=>window.ready);
  if(mode==='stills'){
    const ts=[0,2,5.2,7.5,10.8,14.2];
    for(const [i,t] of ts.entries()){await p.evaluate(t=>renderAt(t),t);await p.screenshot({path:`/home/claude/v3d/still${i}.jpg`,type:'jpeg',quality:85})}
  }else{
    const n=Math.round(TL.duration*TL.fps);
    const ff=spawn('ffmpeg',['-y','-loglevel','error','-f','image2pipe','-c:v','mjpeg','-r','30','-i','-','-i','/home/claude/v3d/voice.wav','-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-af','loudnorm=I=-14:TP=-1.5','-shortest','-movflags','+faststart',out],{stdio:['pipe','inherit','inherit']});
    const t0=Date.now();
    for(let i=0;i<n;i++){await p.evaluate(t=>renderAt(t),i/TL.fps);const buf=await p.screenshot({type:'jpeg',quality:93});if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));if(i%60===0)console.log(i,'/',n,((Date.now()-t0)/1000).toFixed(0)+'s')}
    ff.stdin.end();await new Promise(r=>ff.on('close',r));
  }
  await b.close();
})();
