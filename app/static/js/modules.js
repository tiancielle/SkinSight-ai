// ═══════════════════════════════════════════════════════════════════════════════
// historique.js
// ═══════════════════════════════════════════════════════════════════════════════
async function loadHistory() {
  const list = document.getElementById('hist-list');
  list.innerHTML = '<div class="empty-state">Chargement…</div>';
  try {
    // ← Modification : ajout du paramètre with_patients=true
    const res  = await fetch(`${API}/history?with_patients=true`);
    const data = await res.json();
    if (!data.history.length) {
      list.innerHTML = '<div class="empty-state">Aucune analyse enregistrée.</div>';
      return;
    }
    list.innerHTML = data.history.map(h => `
      <div class="hist-row">
        <div class="hist-bar" style="background:${COLORS[h.pathologie] || '#b5a89e'}"></div>
        <div style="flex:1">
          <div class="hist-name">${h.pathologie_fr}</div>
          <!-- ← Modification : affichage du patient si présent -->
          <div class="hist-date">${h.date} · ${h.patient || '—'}</div>
        </div>
        <span class="hist-pct" style="color:${COLORS[h.pathologie] || '#b5a89e'}">${h.confiance}%</span>
      </div>`).join('');
  } catch {
    list.innerHTML = '<div class="empty-state">Impossible de charger — vérifie le serveur FastAPI.</div>';
  }
}


// ═══════════════════════════════════════════════════════════════════════════════
// avantapres.js
// ═══════════════════════════════════════════════════════════════════════════════
let aaFiles = { avant: null, apres: null };
const AA_COLORS = {
  saine:                  '#7a9e87',
  acne_inflammatoire:     '#c47c5a',
  acne_non_inflammatoire: '#d4a882',
  rosacee:                '#9b7fa6',
  hyperpigmentation:      '#7a9e87',
};

function handleAA(side, input) {
  const file = input.files[0];
  if (!file) return;
  aaFiles[side] = file;
  const img  = document.getElementById('aa-img-'  + side);
  const ph   = document.getElementById('aa-ph-'   + side);
  const card = document.getElementById('aa-card-' + side);
  const reader = new FileReader();
  reader.onload = e => {
    img.src = e.target.result;
    img.style.display = 'block';
    ph.style.display  = 'none';
    card.classList.add('has-img');
  };
  reader.readAsDataURL(file);
  if (aaFiles.avant && aaFiles.apres) document.getElementById('btn-aa').disabled = false;
}

async function analyseAASide(side) {
  const formData = new FormData();
  formData.append('file', aaFiles[side]);
  const res  = await fetch(`${API}/predict`, { method: 'POST', body: formData });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail);
  const col = AA_COLORS[data.pathologie] || '#b5a89e';
  const box = document.getElementById('aa-res-' + side);
  box.innerHTML = `<span style="font-weight:500;color:${col}">${data.pathologie_fr}</span> — <span style="color:var(--txt2)">${data.confiance}%</span>`;
  box.classList.add('show');
  return data;
}

async function runAA() {
  document.getElementById('aa-loader').classList.add('show');
  document.getElementById('evolution-box').classList.remove('show');
  document.getElementById('btn-aa').disabled = true;
  try {
    const [avant, apres] = await Promise.all([analyseAASide('avant'), analyseAASide('apres')]);
    renderEvolution(avant, apres);
    refreshStats();
  } catch (e) {
    alert('Erreur : ' + e.message);
  } finally {
    document.getElementById('aa-loader').classList.remove('show');
    document.getElementById('btn-aa').disabled = false;
  }
}

function renderEvolution(avant, apres) {
  const box  = document.getElementById('evolution-box');
  const same = avant.pathologie === apres.pathologie;
  const improved = apres.confiance < avant.confiance && avant.pathologie !== 'saine';
  const colA = AA_COLORS[avant.pathologie] || '#b5a89e';
  const colB = AA_COLORS[apres.pathologie] || '#b5a89e';

  let msg = '';
  if (apres.pathologie === 'saine' && avant.pathologie !== 'saine')
    msg = "Excellente évolution — la peau semble s'être améliorée significativement.";
  else if (same && improved)
    msg = "Même pathologie mais avec une confiance réduite — légère amélioration détectée.";
  else if (same)
    msg = "Situation stable — pathologie identique sur les deux photos.";
  else
    msg = "Changement de pathologie détecté entre les deux photos.";

  document.getElementById('evo-content').innerHTML = `
    <div style="display:flex;align-items:center;gap:.5rem;margin-bottom:.6rem;font-size:.82rem">
      <span style="color:${colA};font-weight:500">${avant.pathologie_fr} (${avant.confiance}%)</span>
      <span style="color:var(--txt3);font-size:1rem">→</span>
      <span style="color:${colB};font-weight:500">${apres.pathologie_fr} (${apres.confiance}%)</span>
    </div>
    <div style="font-size:.76rem;color:var(--txt2)">${msg}</div>`;
  box.classList.add('show');
}


// ═══════════════════════════════════════════════════════════════════════════════
// webcam.js
// ═══════════════════════════════════════════════════════════════════════════════
const AR_ZONES = {
  acne_inflammatoire:     { zones:['Front','Joues','Menton'], label:'Acné inflammatoire',     color:'#c47c5a' },
  rosacee:                { zones:['Joues','Nez'],            label:'Rosacée',                color:'#9b7fa6' },
  hyperpigmentation:      { zones:['Front','Joues'],          label:'Hyperpigmentation',      color:'#7a9e87' },
  acne_non_inflammatoire: { zones:['Front','Nez'],            label:'Acné non inflammatoire', color:'#d4a882' },
  saine:                  { zones:[],                         label:'Peau saine',             color:'#7a9e87' },
};

let currentAR    = 'acne_inflammatoire';
let arOpacity    = 0.4;
let cameraActive = false;
let videoStream  = null;
let animFrame    = null;
let wsAR         = null;
let wsConnected  = false;
let sendInterval = null;

function buildLegend() {
  const cfg = AR_ZONES[currentAR];
  document.getElementById('ar-badge-txt').textContent = 'Simulation AR · ' + (cfg ? cfg.label : '—');
  const list = document.getElementById('legend-list');
  if (!cfg || !cfg.zones.length) {
    list.innerHTML = '<div class="empty-state" style="padding:.5rem 0">Aucune zone — peau saine</div>';
    return;
  }
  const ZONE_DESC = { Front:'Zone T — sébum élevé', Joues:'Zone U — sensible', Menton:'Zone hormonale', Nez:'Axe central — rougeurs' };
  list.innerHTML = cfg.zones.map(z => `
    <div class="legend-item">
      <div class="legend-color" style="background:${cfg.color};opacity:.6"></div>
      <div class="legend-name">${z}</div>
      <div class="legend-desc">${ZONE_DESC[z] || ''}</div>
    </div>`).join('');
}

function switchAR(pathologie, el) {
  currentAR = pathologie;
  document.querySelectorAll('.ar-btn').forEach(b => b.classList.remove('active'));
  el.classList.add('active');
  buildLegend();
}

function connectWS() {
  wsAR = new WebSocket('ws://localhost:8765');
  wsAR.onopen = () => {
    wsConnected = true;
    document.getElementById('ar-badge-txt').textContent = 'MediaPipe · Connecté';
  };
  wsAR.onclose = () => {
    wsConnected = false;
    document.getElementById('ar-badge-txt').textContent = 'Simulation AR · MediaPipe absent';
  };
  wsAR.onerror = () => {
    wsConnected = false;
  };
  wsAR.onmessage = (event) => {
    try {
      const data   = JSON.parse(event.data);
      const canvas = document.getElementById('cam-canvas');
      const video  = document.getElementById('cam-video');
      const ctx    = canvas.getContext('2d');
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      if (data.error || data.simulated || !data.face_detected) {
        drawSimulatedOverlay(ctx, canvas); return;
      }
      const zones = data.zones || {};
      const color = data.color || [196, 124, 90];
      const rgba  = `rgba(${color[0]},${color[1]},${color[2]},${arOpacity})`;
      Object.entries(zones).forEach(([zoneName, pts]) => {
        if (!pts || pts.length < 3) return;
        const xs = pts.map(p => p[0]), ys = pts.map(p => p[1]);
        const cx = (Math.min(...xs) + Math.max(...xs)) / 2;
        const cy = (Math.min(...ys) + Math.max(...ys)) / 2;
        const rx = (Math.max(...xs) - Math.min(...xs)) / 2 * 1.3;
        const ry = (Math.max(...ys) - Math.min(...ys)) / 2 * 1.3;
        ctx.beginPath(); ctx.ellipse(cx, cy, rx, ry, 0, 0, Math.PI * 2);
        ctx.fillStyle = rgba; ctx.fill();
        ctx.strokeStyle = `rgba(${color[0]},${color[1]},${color[2]},0.8)`;
        ctx.lineWidth = 1.5; ctx.stroke();
        ctx.fillStyle = '#fff'; ctx.font = 'bold 11px DM Sans, sans-serif';
        ctx.textAlign = 'center'; ctx.shadowColor = 'rgba(0,0,0,0.5)'; ctx.shadowBlur = 3;
        ctx.fillText(zoneName, cx, cy + 4); ctx.shadowBlur = 0;
      });
    } catch (e) { console.error('[AR]', e); }
  };
}

function drawSimulatedOverlay(ctx, canvas) {
  const ZONE_RECTS = {
    Front:      { x:.27, y:.08, w:.46, h:.22 },
    JoueGauche: { x:.10, y:.38, w:.30, h:.28 },
    JoueDroite: { x:.60, y:.38, w:.30, h:.28 },
    Menton:     { x:.33, y:.72, w:.34, h:.16 },
    Nez:        { x:.38, y:.38, w:.24, h:.28 },
  };
  const ZONE_MAP_SIM = {
    acne_inflammatoire:     ['Front','JoueGauche','JoueDroite','Menton'],
    acne_non_inflammatoire: ['Front','Nez'],
    rosacee:                ['JoueGauche','JoueDroite','Nez'],
    hyperpigmentation:      ['Front','JoueGauche','JoueDroite'],
    saine:                  [],
  };
  const cfg = AR_ZONES[currentAR];
  if (!cfg) return;
  const [r, g, b] = cfg.color.match(/\w\w/g).map(x => parseInt(x, 16));
  (ZONE_MAP_SIM[currentAR] || []).forEach(z => {
    const rect = ZONE_RECTS[z]; if (!rect) return;
    const cx = (rect.x + rect.w / 2) * canvas.width;
    const cy = (rect.y + rect.h / 2) * canvas.height;
    ctx.beginPath(); ctx.ellipse(cx, cy, rect.w/2*canvas.width, rect.h/2*canvas.height, 0, 0, Math.PI*2);
    ctx.fillStyle = `rgba(${r},${g},${b},${arOpacity})`; ctx.fill();
    ctx.strokeStyle = `rgba(${r},${g},${b},0.8)`; ctx.lineWidth = 1.5; ctx.stroke();
  });
}

async function toggleCamera() {
  const btn = document.getElementById('btn-cam');
  if (!cameraActive) {
    try {
      videoStream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480 } });
      const video  = document.getElementById('cam-video');
      const canvas = document.getElementById('cam-canvas');
      video.srcObject = videoStream;
      video.style.display = canvas.style.display = 'block';
      document.getElementById('cam-frame').querySelector('.cam-placeholder').style.display = 'none';
      canvas.width = 640; canvas.height = 480;
      cameraActive = true;
      btn.textContent = 'Arrêter la caméra';
      connectWS();
      sendInterval = setInterval(() => {
        if (!cameraActive || !wsConnected || wsAR.readyState !== WebSocket.OPEN) {
          const ctx = canvas.getContext('2d');
          ctx.clearRect(0, 0, canvas.width, canvas.height);
          ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
          drawSimulatedOverlay(ctx, canvas); return;
        }
        const tmp = document.createElement('canvas');
        tmp.width = 320; tmp.height = 240;
        tmp.getContext('2d').drawImage(video, 0, 0, 320, 240);
        wsAR.send(JSON.stringify({ frame: tmp.toDataURL('image/jpeg', 0.7), pathologie: currentAR }));
      }, 150);
    } catch (e) { alert('Impossible d\'accéder à la caméra : ' + e.message); }
  } else {
    stopCamera();
  }
}

function stopCamera() {
  if (sendInterval) clearInterval(sendInterval);
  if (wsAR)         wsAR.close();
  if (videoStream)  videoStream.getTracks().forEach(t => t.stop());
  if (animFrame)    cancelAnimationFrame(animFrame);
  const video  = document.getElementById('cam-video');
  const canvas = document.getElementById('cam-canvas');
  video.style.display = canvas.style.display = 'none';
  document.getElementById('cam-frame').querySelector('.cam-placeholder').style.display = '';
  document.getElementById('btn-cam').textContent = 'Activer la caméra';
  document.getElementById('ar-badge-txt').textContent = 'En attente';
  cameraActive = false;
}

document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('opacity-slider').addEventListener('input', function () {
    arOpacity = this.value / 10;
    document.getElementById('opacity-val').textContent = Math.round(arOpacity * 100) + '%';
  });
  buildLegend();
});