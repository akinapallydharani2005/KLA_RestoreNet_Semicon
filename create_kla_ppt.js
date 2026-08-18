const pptxgen = require('pptxgenjs');
const {
  imageSizingCrop,
  safeOuterShadow,
  warnIfSlideHasOverlaps,
  warnIfSlideElementsOutOfBounds,
} = require('/home/oai/skills/slides/pptxgenjs_helpers');

const pptx = new pptxgen();
pptx.layout = 'LAYOUT_WIDE';
pptx.author = 'KLA RestoreNet-Hybrid Team';
pptx.company = 'SEMICON India Hackathon';
pptx.subject = 'AI-Based Restoration of Degraded Images';
pptx.title = 'KLA RestoreNet-Hybrid';
pptx.lang = 'en-US';
pptx.theme = { headFontFace: 'Aptos Display', bodyFontFace: 'Aptos', lang: 'en-US' };

const W = 13.333, H = 7.5;
const C = {
  bg: '07131D', bg2: '0B1C2B', panel: '102A3F', teal: '18D3C6', cyan: '2FC4FF',
  green: '7EF29D', orange: 'FFB545', red: 'FF5D73', purple: 'B69CFF',
  text: 'F2F7FF', muted: 'A8BED2', muted2: '6F8498', line: '2B536C', white: 'FFFFFF', black: '000000'
};
const ROOT = '/mnt/data/kla_restore_work/KLA_RestoreNet_Submission';
const IMG = {
  degr: `${ROOT}/results/figures/degradation_observation.png`,
  examples: `${ROOT}/results/figures/restoration_examples.png`,
  failure: `${ROOT}/results/figures/failure_case.png`,
  psnr: `${ROOT}/results/figures/psnr_bar.png`,
  ssim: `${ROOT}/results/figures/ssim_bar.png`,
  gt: `${ROOT}/sample_data/gt/sample_0000.png`,
  lr: `${ROOT}/sample_data/noisy_lr/sample_0000.png`,
  out: `${ROOT}/sample_data/output/sample_0000.png`,
};

function bg(slide) {
  slide.background = { color: C.bg };
  slide.addShape(pptx.ShapeType.rect, { x:0, y:0, w:W, h:H, fill:{color:C.bg}, line:{color:C.bg, transparency:100} });
  slide.addShape(pptx.ShapeType.line, { x:0.52, y:H-0.36, w:12.25, h:0, line:{color:C.line, width:0.8, transparency:35} });
  slide.addShape(pptx.ShapeType.rect, { x:0, y:H-0.13, w:W, h:0.13, fill:{color:C.teal, transparency:45}, line:{color:C.teal, transparency:100} });
}
function title(slide, t, sub='') {
  slide.addText(t, { x:0.56, y:0.34, w:10.8, h:0.48, fontFace:'Aptos Display', fontSize:27, bold:true, color:C.text, margin:0 });
  if (sub) slide.addText(sub, { x:0.58, y:0.86, w:11.2, h:0.25, fontSize:10.5, color:C.muted, margin:0, fit:'shrink' });
  slide.addShape(pptx.ShapeType.line, { x:0.58, y:1.18, w:1.4, h:0, line:{color:C.teal, width:2.3} });
}
function footer(slide, n) {
  slide.addText('KLA RestoreNet-Hybrid  |  SEMICON India Hackathon', { x:0.56, y:7.18, w:6.4, h:0.18, fontSize:7.5, color:C.muted2, margin:0 });
  slide.addText(String(n).padStart(2,'0'), { x:12.25, y:7.11, w:0.55, h:0.25, fontSize:10.5, bold:true, color:C.teal, align:'right', margin:0 });
}
function panel(slide, x,y,w,h, opts={}) {
  slide.addShape(pptx.ShapeType.roundRect, { x,y,w,h, rectRadius:0.08, fill:{color:opts.color||C.panel, transparency: opts.transparency ?? 0}, line:{color:opts.line||C.line, transparency:opts.lineTrans??20, width:0.8}, shadow: opts.shadow === false ? undefined : safeOuterShadow('000000', 0.24, 45, 1.5, 0.8)});
}
function text(slide, txt, x,y,w,h, opts={}) {
  slide.addText(txt, { x,y,w,h, fontSize:opts.size||13, color:opts.color||C.text, bold:opts.bold||false, margin:0.04, fit:'shrink', breakLine:false, valign:'top', paraSpaceAfterPt:opts.space??4 });
}
function bullets(slide, items, x,y,w,h, opts={}) {
  const s = items.map(v => `• ${v}`).join('\n');
  text(slide, s, x,y,w,h, { size:opts.size||12.5, color:opts.color||C.text, space:6 });
}
function image(slide, path, x,y,w,h, label=null, crop=true) {
  panel(slide, x,y,w,h, {color:'081420', line:C.line, lineTrans:35});
  const pad=0.07;
  if (crop) slide.addImage({path, ...imageSizingCrop(path, x+pad, y+pad, w-2*pad, h-2*pad)});
  else slide.addImage({path, x:x+pad, y:y+pad, w:w-2*pad, h:h-2*pad});
  if (label) {
    slide.addShape(pptx.ShapeType.roundRect, {x:x+0.12, y:y+0.11, w:Math.min(w-0.24, 2.45), h:0.28, rectRadius:0.09, fill:{color:C.bg2, transparency:8}, line:{color:C.teal, transparency:45, width:0.6}});
    slide.addText(label, {x:x+0.20, y:y+0.17, w:Math.min(w-0.40,2.25), h:0.13, fontSize:8, bold:true, color:C.teal, margin:0});
  }
}
function chip(slide, label, x,y,w,color=C.teal) {
  slide.addShape(pptx.ShapeType.roundRect, {x,y,w,h:0.32, rectRadius:0.14, fill:{color, transparency:84}, line:{color, transparency:18, width:0.7}});
  slide.addText(label, {x:x+0.06, y:y+0.08, w:w-0.12, h:0.14, fontSize:8.5, bold:true, color, align:'center', margin:0});
}
function metric(slide, value, label, x,y,w,h,color=C.teal) {
  panel(slide, x,y,w,h, {color:C.bg2, line:color, lineTrans:45});
  slide.addText(value, {x:x+0.07, y:y+0.16, w:w-0.14, h:0.46, fontSize:24, bold:true, color, align:'center', margin:0});
  slide.addText(label, {x:x+0.07, y:y+0.72, w:w-0.14, h:0.31, fontSize:9.5, color:C.muted, align:'center', margin:0, fit:'shrink'});
}
function arrow(slide, x1,y1,x2,y2,color=C.teal) {
  slide.addShape(pptx.ShapeType.line, {x:x1, y:y1, w:x2-x1, h:y2-y1, line:{color, width:1.4, endArrowType:'triangle'}});
}
function addNotes(slide, txt) { slide.addNotes(txt); }

// 1
{
  const slide=pptx.addSlide(); bg(slide);
  image(slide, IMG.examples, 6.95, 0.55, 5.8, 5.45, null, true);
  chip(slide, 'SEMICON INDIA HACKATHON — KLA PROBLEM', 0.64, 0.78, 3.55, C.green);
  slide.addText('KLA RestoreNet-Hybrid', {x:0.66, y:1.45, w:6.2, h:0.72, fontSize:39, bold:true, color:C.text, margin:0});
  slide.addText('AI-Based Restoration of Degraded Images for Semiconductor Inspection', {x:0.68, y:2.28, w:6.25, h:0.52, fontSize:17.5, color:C.teal, margin:0, fit:'shrink'});
  slide.addText('One-line solution: lightweight residual CNN for joint denoising + 2× super-resolution, optimized for quality and full-pipeline runtime.', {x:0.7, y:3.12, w:5.9, h:0.8, fontSize:13, color:C.muted, margin:0, fit:'shrink'});
  metric(slide, '27.41 dB', 'demo PSNR', 0.72, 4.35, 1.55, 1.2, C.green);
  metric(slide, '0.7105', 'demo SSIM', 2.45, 4.35, 1.55, 1.2, C.teal);
  metric(slide, '~90 ms', 'CPU demo / image', 4.18, 4.35, 1.55, 1.2, C.orange);
  text(slide, 'Team: [TEAM NAME]\nMembers: [ADD NAMES]\nRepository: [ADD GITHUB LINK]', 0.76, 6.0, 5.6, 0.9, {size:12.2, color:C.text});
  footer(slide,1); addNotes(slide, 'Introduce the task: restore degraded semiconductor inspection images. Our package focuses on a reproducible, lightweight AI pipeline that removes speckle and Gaussian noise while restoring lost resolution.');
}
// 2
{
  const slide=pptx.addSlide(); bg(slide); title(slide, 'Problem Understanding', 'Recover clean high-resolution inspection images from degraded low-resolution inputs');
  image(slide, IMG.lr, 0.75, 1.5, 3.2, 3.2, 'NoisyLR input');
  image(slide, IMG.out, 5.05, 1.5, 3.2, 3.2, 'Restored output');
  image(slide, IMG.gt, 9.35, 1.5, 3.2, 3.2, 'Ground truth target');
  arrow(slide, 4.05, 3.1, 4.85, 3.1); arrow(slide, 8.35, 3.1, 9.15, 3.1);
  bullets(slide, [
    'Input: degraded noisy low-resolution image with speckle + Gaussian noise + downsampling',
    'Output: restored image at expected GT resolution, usually 2× larger than NoisyLR',
    'Must preserve real structure; over-smoothing and hallucinated details hurt the score',
    'Hidden test contains familiar and unfamiliar content, so generalization matters'
  ], 0.78, 5.35, 11.8, 1.1, {size:12.5});
  footer(slide,2); addNotes(slide, 'The task is not just denoising. The algorithm must remove grain, recover spatial resolution, and preserve true structure. The hidden test will include both in-distribution and out-of-distribution images.');
}
// 3
{
  const slide=pptx.addSlide(); bg(slide); title(slide, 'Dataset Analysis & Degradation Observations', 'NoisyLR can be out of [0,1], while GT remains clipped and clean');
  image(slide, IMG.degr, 0.72, 1.35, 7.4, 4.4, 'GT vs NoisyLR + histogram', false);
  bullets(slide, [
    'GT images are clean high-SNR targets normalized to [0,1]',
    'NoisyLR images are lower-resolution observations with wider intensity spread',
    'Speckle noise is multiplicative and can amplify bright regions',
    'Gaussian noise reduces pixel fidelity and edge confidence',
    'Downsampling removes high-frequency details that the model must reconstruct carefully'
  ], 8.55, 1.58, 3.95, 3.55, {size:12.2});
  chip(slide, 'Design implication: clip outputs, not inputs too aggressively', 8.58, 5.35, 3.9, C.orange);
  footer(slide,3); addNotes(slide, 'Our preprocessing intentionally allows mild out-of-range input values because the challenge says NoisyLR can exceed [0,1]. We only clip the final output to [0,1], because KLA scores exactly what is saved.');
}
// 4
{
  const slide=pptx.addSlide(); bg(slide); title(slide, 'End-to-End Pipeline', 'A clean evaluator-facing workflow with no manual source-code edits');
  // connectors first
  arrow(slide, 2.25, 3.05, 3.2, 3.05); arrow(slide, 4.7, 3.05, 5.65, 3.05); arrow(slide, 7.15, 3.05, 8.1, 3.05); arrow(slide, 9.6, 3.05, 10.55, 3.05);
  const nodes = [
    ['Input folder', 'NoisyLR images', 0.75, 2.35, C.cyan],
    ['Preprocess', 'robust range handling', 3.2, 2.35, C.teal],
    ['AI restoration', '2× residual CNN', 5.65, 2.35, C.green],
    ['Postprocess', 'clip + convert', 8.1, 2.35, C.orange],
    ['Output folder', 'restored images', 10.55, 2.35, C.purple],
  ];
  for (const [a,b,x,y,col] of nodes) {
    panel(slide,x,y,1.5,1.3,{color:C.bg2,line:col,lineTrans:35});
    text(slide,a,x+0.12,y+0.23,1.26,0.25,{size:12,bold:true,color:col});
    text(slide,b,x+0.12,y+0.62,1.26,0.36,{size:9.5,color:C.muted});
  }
  panel(slide, 1.15, 5.05, 10.95, 0.9, {color:'0B1A28', line:C.teal, lineTrans:40});
  text(slide, 'Official command:  python inference.py <input_test_images_dir> <output_dir>', 1.4, 5.32, 10.4, 0.3, {size:15, bold:true, color:C.text});
  bullets(slide, ['Preserves relative filenames', 'Supports PNG/JPG/TIFF/BMP/NPY', 'CUDA automatically when available', 'CPU fallback for reproducibility'], 1.4, 6.22, 10.3, 0.55, {size:11});
  footer(slide,4); addNotes(slide, 'This is the pipeline the evaluator will run. It accepts only input and output folders, loads the checkpoint and config, restores all images, and writes outputs without any manual path edits.');
}
// 5
{
  const slide=pptx.addSlide(); bg(slide); title(slide, 'Preprocessing & Augmentation', 'Handle the official degradations without adding unsupported assumptions');
  image(slide, IMG.degr, 7.15, 1.38, 5.25, 3.28, 'degradation model', false);
  bullets(slide, [
    'Input preprocessing keeps mild NoisyLR out-of-range values instead of hard clipping immediately',
    'Final output is clipped inside the solution because KLA scores saved images directly',
    'Training augmentation: flips, rotations, random crops and diverse synthetic noise levels',
    'Synthetic pairs include texture, dendrite, wafer-like lines, blobs and mixed-edge patterns',
    'Augmentation objective: improve OOD generalization while preserving fine structures'
  ], 0.78, 1.45, 5.75, 3.55, {size:12.2});
  panel(slide,0.88,5.45,11.45,0.86,{color:C.bg2,line:C.orange,lineTrans:40});
  text(slide, 'Key rule: train with variable degradation, but benchmark only speckle noise + Gaussian noise + downsampling.', 1.15, 5.74, 10.85, 0.26, {size:14, bold:true, color:C.orange});
  footer(slide,5); addNotes(slide, 'The model does not try to identify the exact order of degradation. It learns the inverse restoration in one step, while the data pipeline exposes it to different noise strengths and content types.');
}
// 6
{
  const slide=pptx.addSlide(); bg(slide); title(slide, 'Model Architecture & Design Rationale', 'Small residual CNN: stable base path + learned detail correction');
  // architecture connectors first
  arrow(slide, 2.0, 3.0, 2.9, 3.0); arrow(slide, 4.4, 3.0, 5.3, 3.0); arrow(slide, 6.8, 3.0, 7.7, 3.0); arrow(slide, 9.2, 3.0, 10.1, 3.0);
  const cols=[C.cyan,C.teal,C.green,C.orange,C.purple];
  const labels=[['NoisyLR','1× input'],['Bicubic','2× base'],['Depthwise blocks','fast features'],['Residual head','bounded detail'],['Restored','2× output']];
  for (let i=0;i<labels.length;i++) {
    const x=0.75+i*2.4; panel(slide,x,2.3,1.25,1.35,{color:C.bg2,line:cols[i],lineTrans:35});
    text(slide,labels[i][0],x+0.08,2.6,1.1,0.22,{size:11.2,bold:true,color:cols[i]});
    text(slide,labels[i][1],x+0.08,2.95,1.1,0.22,{size:9.2,color:C.muted});
  }
  bullets(slide, [
    'Bicubic path prevents catastrophic output when checkpoint is weak or under-trained',
    'Depthwise-separable blocks reduce parameter count and improve throughput',
    'Bounded residual discourages hallucination and extreme pixel shifts',
    'Fully convolutional design supports different input sizes without architectural changes'
  ], 0.95, 4.55, 5.6, 1.25, {size:12.1});
  metric(slide, '32', 'channels', 7.1, 4.55, 1.35, 1.1, C.teal);
  metric(slide, '6', 'residual blocks', 8.75, 4.55, 1.35, 1.1, C.green);
  metric(slide, '2×', 'SR scale', 10.4, 4.55, 1.35, 1.1, C.orange);
  footer(slide,6); addNotes(slide, 'The model is designed for challenge scoring: enough capacity to denoise and restore detail, but small enough for strong full-pipeline speed. The residual path makes it safer than direct image generation.');
}
// 7
{
  const slide=pptx.addSlide(); bg(slide); title(slide, 'Loss Functions & Training Setup', 'Balance pixel fidelity, structural quality and edge preservation');
  panel(slide,0.8,1.45,5.2,3.1,{color:C.bg2,line:C.teal,lineTrans:40});
  text(slide, 'Training objective', 1.05,1.75,2.2,0.3,{size:14,bold:true,color:C.teal});
  text(slide, 'Loss = Charbonnier/L1 + 0.10 × Gradient loss\nOptional extension: SSIM + LPIPS/perceptual loss after baseline stabilizes', 1.05,2.3,4.65,0.92,{size:14,color:C.text});
  bullets(slide, ['Charbonnier/L1 improves PSNR and numerical fidelity', 'Gradient loss protects edges and thin structures', 'Optional LPIPS targets perceptual similarity'], 1.05,3.45,4.65,0.85,{size:11.4});
  panel(slide,7.1,1.45,5.2,3.1,{color:C.bg2,line:C.green,lineTrans:40});
  text(slide, 'Training protocol', 7.35,1.75,2.4,0.3,{size:14,bold:true,color:C.green});
  bullets(slide, ['Clean train/validation split', 'Random crops at GT resolution', 'AdamW optimizer', 'Track seed, checkpoint, metrics and config', 'Overfit small pairs first for sanity'], 7.35,2.25,4.55,1.55,{size:11.8});
  image(slide, IMG.psnr, 2.0,5.25,3.9,1.62,'PSNR sanity chart', false);
  image(slide, IMG.ssim, 7.1,5.25,3.9,1.62,'SSIM sanity chart', false);
  footer(slide,7); addNotes(slide, 'The initial model uses L1 and gradient loss because they are stable and quick to reproduce. Once the official training data is available, SSIM and LPIPS can be added carefully to improve the competition metrics.');
}
// 8
{
  const slide=pptx.addSlide(); bg(slide); title(slide, 'Experiment Tracking & Baseline Comparison', 'One-change-at-a-time validation to avoid metric leakage');
  image(slide, IMG.psnr, 0.78,1.42,5.2,3.0,'PSNR comparison', false);
  image(slide, IMG.ssim, 7.05,1.42,5.2,3.0,'SSIM comparison', false);
  panel(slide,0.95,5.1,11.35,0.95,{color:C.bg2,line:C.teal,lineTrans:42});
  text(slide, 'Baseline: fast classical median + bicubic + unsharp restoration. Final: residual CNN checkpoint plus clipped output.', 1.15,5.42,10.9,0.25,{size:13.3,bold:true,color:C.text});
  bullets(slide, ['Record: config, random seed, checkpoint, dataset split, PSNR, SSIM, LPIPS, runtime', 'Keep validation split separate from training/model selection', 'Inspect images in addition to metrics to detect lost edges or hallucinated texture'], 1.15,6.28,11.2,0.6,{size:10.6});
  footer(slide,8); addNotes(slide, 'This slide shows how we compare the final model against a simple baseline. The important part is experiment hygiene: no validation leakage and no changes without tracking the metrics and visual output.');
}
// 9
{
  const slide=pptx.addSlide(); bg(slide); title(slide, 'PSNR, SSIM & LPIPS Results', 'Bundled synthetic validation demonstrates the working pipeline');
  metric(slide, '27.413 dB', 'RestoreNet-Hybrid PSNR', 0.95,1.55,2.2,1.25,C.green);
  metric(slide, '0.7105', 'RestoreNet-Hybrid SSIM', 3.55,1.55,2.2,1.25,C.teal);
  metric(slide, 'optional', 'LPIPS if package installed', 6.15,1.55,2.2,1.25,C.purple);
  metric(slide, '27.104 dB', 'classical baseline PSNR', 8.75,1.55,2.2,1.25,C.orange);
  image(slide, IMG.examples, 0.95,3.35,7.7,2.8,'sample restoration panel', false);
  panel(slide,9.1,3.35,3.1,2.8,{color:C.bg2,line:C.line,lineTrans:35});
  text(slide, 'Important interpretation', 9.35,3.68,2.4,0.25,{size:13,bold:true,color:C.orange});
  bullets(slide, ['These are demo numbers from bundled synthetic data', 'Official score requires training on KLA dataset', 'Hidden GT will be scored by KLA using PSNR, SSIM, LPIPS and runtime'], 9.35,4.15,2.5,1.28,{size:10.7});
  footer(slide,9); addNotes(slide, 'I should clearly say these numbers are synthetic sanity-check results, not the final hidden test result. The package is ready structurally, but official training data is needed for true leaderboard performance.');
}
// 10
{
  const slide=pptx.addSlide(); bg(slide); title(slide, 'Runtime, Batch Size & Optimization', 'Optimize the whole pipeline, not only the neural-network forward pass');
  panel(slide,0.82,1.55,5.4,3.4,{color:C.bg2,line:C.teal,lineTrans:38});
  text(slide,'Runtime includes',1.08,1.88,2.4,0.3,{size:14,bold:true,color:C.teal});
  bullets(slide,['script startup and model initialization','disk image reading','preprocessing and CPU→GPU transfer','model execution','GPU→CPU transfer and image saving'],1.08,2.38,4.75,1.65,{size:12});
  panel(slide,7.05,1.55,5.4,3.4,{color:C.bg2,line:C.green,lineTrans:38});
  text(slide,'Optimization choices',7.31,1.88,2.8,0.3,{size:14,bold:true,color:C.green});
  bullets(slide,['small residual CNN architecture','single-pass restoration','no external model download during inference','preserve filenames with minimal I/O overhead','CUDA support with CPU fallback'],7.31,2.38,4.75,1.65,{size:12});
  metric(slide,'~90 ms','CPU demo/image',2.1,5.45,1.75,1.15,C.orange);
  metric(slide,'H100','official target GPU',5.8,5.45,1.75,1.15,C.teal);
  metric(slide,'2×','default output scale',9.5,5.45,1.75,1.15,C.green);
  footer(slide,10); addNotes(slide, 'KLA measures the full script runtime, not just the model. Our design avoids heavy architectures and model downloads, and it keeps output naming simple to minimize overhead.');
}
// 11
{
  const slide=pptx.addSlide(); bg(slide); title(slide, 'Visual Results, Failure Cases & Limitations', 'Inspect restored images because metrics alone can miss structural errors');
  image(slide, IMG.examples, 0.75,1.35,5.65,3.25,'successful restorations', false);
  image(slide, IMG.failure, 6.95,1.35,5.65,3.25,'hard/failure example', false);
  bullets(slide, ['Strong speckle on very thin features can still remove useful structure', 'OOD textures with unusual frequency may lose fine micro-patterns', 'Gradient loss helps edges but too much can create ringing', 'Next step: official-data training + SSIM/LPIPS loss tuning + border/frequency augmentation'], 0.95,5.35,11.2,1.05,{size:11.8});
  footer(slide,11); addNotes(slide, 'The remaining limitations are typical for restoration: smoothing thin structures, losing high-frequency details, or ringing near sharp boundaries. Our plan directly targets those using official data and better perceptual/structural loss balancing.');
}
// 12
{
  const slide=pptx.addSlide(); bg(slide); title(slide, 'Conclusion & Submission Package', 'A complete reproducible project aligned with KLA deliverables');
  bullets(slide, ['Standalone inference script with input/output directory arguments', 'Training script, model architecture, config, weights and dependencies included', 'Evaluation script reports PSNR, SSIM and optional LPIPS', 'README documents setup, training, inference and assumptions', 'Solution PPT and visual result/failure samples included'], 0.78,1.45,5.85,2.1,{size:12.6});
  panel(slide,7.0,1.4,5.25,2.1,{color:C.bg2,line:C.teal,lineTrans:38});
  text(slide,'Final takeaway',7.28,1.75,2.5,0.28,{size:15,bold:true,color:C.teal});
  text(slide,'Restore real structure, suppress degradation, and keep the evaluator pipeline simple, fast and reproducible.',7.28,2.28,4.55,0.72,{size:15,bold:true,color:C.text});
  panel(slide,0.86,4.55,11.4,1.35,{color:'0B1A28',line:C.orange,lineTrans:45});
  text(slide,'Before final upload: replace demo checkpoint with official-data-trained checkpoint and fill Team/GitHub placeholders.',1.15,4.96,10.85,0.32,{size:14.5,bold:true,color:C.orange});
  text(slide,'External resources: no external dataset or pretrained third-party weights are bundled in this package.',1.15,5.44,10.85,0.25,{size:11.8,color:C.muted});
  footer(slide,12); addNotes(slide, 'Conclude that the submission package is complete and reproducible. The only remaining team-specific edits are team name, repository link, and replacing the demo checkpoint with official training results.');
}

for (const s of pptx._slides) {
  warnIfSlideHasOverlaps(s, pptx);
  warnIfSlideElementsOutOfBounds(s, pptx);
}

pptx.writeFile({ fileName: `${ROOT}/solution_presentation.pptx` });
