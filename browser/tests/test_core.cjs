const assert=require('node:assert/strict'),crypto=require('node:crypto');const {SHA256,crc32,inspect,comparison,plan}=require('../src/core');
function file(b,name='test.img'){return new File([b],name);}
function gpt(){const b=Buffer.alloc(1024*512);b[510]=85;b[511]=170;b[450]=238;b.writeUInt32LE(1,454);b.writeUInt32LE(1023,458);const h=b.subarray(512,1024),t=b.subarray(1024,1536);h.write('EFI PART');h.writeUInt32LE(0x10000,8);h.writeUInt32LE(92,12);h.writeBigUInt64LE(1n,24);h.writeBigUInt64LE(1023n,32);h.writeBigUInt64LE(34n,40);h.writeBigUInt64LE(990n,48);h.writeBigUInt64LE(2n,72);h.writeUInt32LE(4,80);h.writeUInt32LE(128,84);t[0]=1;t.writeBigUInt64LE(34n,32);t.writeBigUInt64LE(99n,40);h.writeUInt32LE(crc32(t),88);h.writeUInt32LE(crc32(h.subarray(0,92)),16);return b;}
function fixHeader(b){const h=b.subarray(512,604);h.fill(0,16,20);h.writeUInt32LE(crc32(h),16);}
(async()=>{let n=0;const pass=()=>n++;
 for(const len of [0,1,3,55,56,63,64,65,127,128,1024,4194305]){const b=crypto.randomBytes(len),h=new SHA256();for(let p=0;p<len;p+=37)h.update(b.subarray(p,p+37));assert.equal(h.digest(),crypto.createHash('sha256').update(b).digest('hex'));assert.throws(()=>h.digest());pass();}
 assert.equal(crc32(Buffer.from('123456789')),0xcbf43926);pass();
 assert.equal(comparison('a'.repeat(64),' A'.trim().repeat(64)),'MATCH');assert.throws(()=>comparison('a','hello'));assert.equal(comparison('a'.repeat(64),'b'.repeat(64)),'MISMATCH');pass();
 for(let len of [0,1,511,512,513]){const r=await inspect(file(Buffer.alloc(len)));assert.equal(r.format,'Unrecognized');pass();}
 const b=Buffer.alloc(1024*1024);b[510]=85;b[511]=170;b[450]=12;b.writeUInt32LE(1,454);b.writeUInt32LE(2047,458);let r=await inspect(file(b));assert.equal(r.errors.length,0);assert.equal(r.partitions[0].sectors,'2047');pass();
 b.writeUInt32LE(2048,458);r=await inspect(file(b));assert.match(r.errors.join(),/out-of-file/);pass();
 b.writeUInt32LE(100,458);b[466]=12;b.writeUInt32LE(90,470);b.writeUInt32LE(100,474);r=await inspect(file(b));assert.match(r.errors.join(),/overlap/);pass();
 let g=gpt();r=await inspect(file(g));assert.equal(r.errors.length,0);assert.equal(r.checks.gptHeaderCRC,'match');assert.equal(r.checks.gptEntriesCRC,'match');assert.equal(r.checks.backupGPT,'not checked');pass();
 g[600]^=1;r=await inspect(file(g));assert.match(r.errors.join(),/header CRC/);pass();
 g=gpt();g[1024]^=1;r=await inspect(file(g));assert.match(r.errors.join(),/array CRC/);pass();
 g=gpt();g.writeUInt32LE(40000,512+80);fixHeader(g);r=await inspect(file(g));assert.match(r.errors.join(),/4 MiB/);pass();
 g=gpt();g.writeBigUInt64LE(2n**63n,512+72);fixHeader(g);r=await inspect(file(g));assert.match(r.errors.join(),/exceeds file/);pass();
 const iso=Buffer.alloc(40000);iso.write('CD001',32769);r=await inspect(file(iso,'<script>.iso'));assert.equal(r.iso9660Signature,true);assert.match(r.scope,/not bootability/);pass();
 let maxRead=0;const big={size:2**40,name:'huge.img',slice:(s,e)=>{maxRead=Math.max(maxRead,e-s);return new Blob([Buffer.alloc(e-s)]);}};r=await inspect(big);assert(maxRead<=4096);pass();
 await assert.rejects(inspect(file(b),512,()=>{throw Error('Cancelled')}),/Cancelled/);await assert.rejects(inspect(file(b),1024));pass();
 const p=plan(r,'100');assert.equal(p.executable,false);assert.equal(p.targetDetected,false);assert.equal(p.capacityFits,false);assert.throws(()=>plan(r,'1e9'));assert.throws(()=>plan(r,'-1'));pass();
 console.log(JSON.stringify({passed:n,scope:'Synthetic, in-memory files only; no disk access.'}));
})().catch(e=>{console.error(e);process.exit(1)});
