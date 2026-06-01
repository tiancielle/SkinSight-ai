// ═══════════════════════════════════════════════════════════════════════════════
// patients.js — Dossier patient SkinSight AI
// ═══════════════════════════════════════════════════════════════════════════════

let currentPatientId = null;

const PHOTOTYPES = {
  'I':   'Très claire — brûle toujours, ne bronze jamais',
  'II':  'Claire — brûle facilement, bronze peu',
  'III': 'Intermédiaire — brûle parfois, bronze progressivement',
  'IV':  'Mate — brûle rarement, bronze facilement',
  'V':   'Foncée — brûle très rarement, bronze intensément',
  'VI':  'Très foncée — ne brûle jamais',
};

// ── Liste patients ────────────────────────────────────────────────────────────
async function loadPatients() {
  const list = document.getElementById('patients-list');
  list.innerHTML = '<div class="empty-state">Chargement…</div>';
  try {
    const res  = await fetch(`${API}/patients`);
    const data = await res.json();
    if (!data.patients.length) {
      list.innerHTML = `
        <div class="empty-state">
          Aucun patient enregistré.<br>
          <span style="color:var(--terra);cursor:pointer;text-decoration:underline"
                onclick="showPatientForm()">Créer le premier patient →</span>
        </div>`;
      return;
    }
    list.innerHTML = data.patients.map(p => `
      <div class="patient-row" onclick="openPatient(${p.id})">
        <div class="patient-avatar">${p.prenom[0]}${p.nom[0]}</div>
        <div style="flex:1">
          <div class="patient-name">${p.prenom} ${p.nom}</div>
          <div class="patient-meta">${p.age} ans · ${p.sexe} · Phototype ${p.phototype}</div>
        </div>
        <div style="text-align:right">
          <div style="font-size:.68rem;color:var(--txt3)">${p.date_creation}</div>
          <button class="btn-delete" onclick="event.stopPropagation();deletePatient(${p.id})">Supprimer</button>
        </div>
      </div>`).join('');
  } catch {
    list.innerHTML = '<div class="empty-state">Erreur — vérifie le serveur FastAPI.</div>';
  }
}

// ── Formulaire création ───────────────────────────────────────────────────────
function showPatientForm() {
  document.getElementById('patient-form-box').style.display = 'block';
  document.getElementById('patients-list').style.display    = 'none';
  document.getElementById('patient-fiche').style.display    = 'none';
  document.getElementById('btn-new-patient').style.display  = 'none';
}

function hidePatientForm() {
  document.getElementById('patient-form-box').style.display = 'none';
  document.getElementById('patients-list').style.display    = 'block';
  document.getElementById('btn-new-patient').style.display  = 'inline-block';
}

async function savePatient() {
  const nom      = document.getElementById('pt-nom').value.trim();
  const prenom   = document.getElementById('pt-prenom').value.trim();
  const age      = document.getElementById('pt-age').value;
  const sexe     = document.getElementById('pt-sexe').value;
  const phototype= document.getElementById('pt-phototype').value;
  const notes    = document.getElementById('pt-notes').value.trim();

  if (!nom || !prenom || !age) {
    alert('Nom, prénom et âge sont obligatoires.');
    return;
  }

  try {
    const res = await fetch(`${API}/patients`, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ nom, prenom, age: parseInt(age), sexe, phototype, notes }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail);

    // Reset form
    ['pt-nom','pt-prenom','pt-age','pt-notes'].forEach(id => document.getElementById(id).value = '');
    document.getElementById('pt-sexe').value      = 'M';
    document.getElementById('pt-phototype').value = 'I';

    hidePatientForm();
    loadPatients();

    // Mettre à jour le dropdown de la page Analyse
    loadPatientsDropdown();
  } catch (e) {
    alert('Erreur : ' + e.message);
  }
}

// ── Fiche patient ─────────────────────────────────────────────────────────────
async function openPatient(id) {
  currentPatientId = id;
  const fiche = document.getElementById('patient-fiche');
  const list  = document.getElementById('patients-list');

  list.style.display  = 'none';
  fiche.style.display = 'block';
  document.getElementById('btn-new-patient').style.display = 'none';
  fiche.innerHTML = '<div class="empty-state">Chargement…</div>';

  try {
    const res  = await fetch(`${API}/patients/${id}`);
    const data = await res.json();
    const p    = data.patient;
    const analyses = data.analyses;

    const photoDesc = PHOTOTYPES[p.phototype] || '';
    const PATHO_COLORS = {
      saine:'#7a9e87', acne_inflammatoire:'#c47c5a',
      acne_non_inflammatoire:'#d4a882', rosacee:'#9b7fa6', hyperpigmentation:'#7a9e87'
    };

    fiche.innerHTML = `
      <div class="patient-header">
        <div class="patient-avatar-lg">${p.prenom[0]}${p.nom[0]}</div>
        <div style="flex:1">
          <div style="font-family:'DM Serif Display',serif;font-size:1.3rem;color:var(--txt)">${p.prenom} ${p.nom}</div>
          <div style="font-size:.78rem;color:var(--txt2);margin-top:.2rem">${p.age} ans · ${p.sexe === 'M' ? 'Homme' : 'Femme'} · Phototype ${p.phototype} — <em>${photoDesc}</em></div>
          ${p.notes ? `<div style="font-size:.73rem;color:var(--txt3);margin-top:.3rem">${p.notes}</div>` : ''}
        </div>
        <div style="display:flex;gap:.5rem;align-items:flex-start">
          <button class="btn btn-main" onclick="generatePatientPDF(${p.id})">Rapport PDF</button>
          <button class="btn btn-ghost" onclick="analyserPatient(${p.id}, '${p.prenom} ${p.nom}')">Analyser</button>
          <button class="btn btn-ghost" onclick="closePatient()">← Retour</button>
        </div>
      </div>

      <div class="moment-tabs" style="margin-top:1rem">
        <button class="moment-tab active" onclick="switchPatientTab('dossier', this)">Dossier</button>
        <button class="moment-tab" onclick="switchPatientTab('routine', this)">Routine</button>
        <button class="moment-tab" onclick="switchPatientTab('avantapres', this)">Avant / Après</button>
      </div>

      <div id="ptab-dossier" class="ptab">
        <div class="stats-row" style="margin-top:1rem">
          <div class="stat-card">
            <div class="stat-label">Analyses</div>
            <div class="stat-val">${analyses.length}</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">Dernière visite</div>
            <div class="stat-val" style="font-size:.95rem">${analyses[0]?.date?.slice(0,10) || '—'}</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">Dernier diagnostic</div>
            <div class="stat-val" style="font-size:.82rem;color:${PATHO_COLORS[analyses[0]?.pathologie]||'#b5a89e'}">${analyses[0]?.pathologie_fr || '—'}</div>
          </div>
        </div>

        ${analyses.length > 1 ? `
        <div style="margin-top:1.2rem;background:var(--bg2);border:1px solid var(--brd);border-radius:14px;padding:1rem">
          <div class="section-label" style="margin-bottom:.8rem">Évolution de la confiance</div>
          <canvas id="evolution-chart" height="80"></canvas>
        </div>` : ''}

        <div style="margin-top:1.2rem">
          <div class="section-label" style="margin-bottom:.6rem">Historique des analyses</div>
          ${analyses.length ? analyses.map(a => `
            <div class="hist-row">
              <div class="hist-bar" style="background:${PATHO_COLORS[a.pathologie]||'#b5a89e'}"></div>
              <div style="flex:1">
                <div class="hist-name">${a.pathologie_fr}</div>
                <div class="hist-date">${a.date}</div>
              </div>
              <span class="hist-pct" style="color:${PATHO_COLORS[a.pathologie]||'#b5a89e'}">${a.confiance}%</span>
            </div>`).join('') : '<div class="empty-state">Aucune analyse pour ce patient.</div>'}
        </div>
      </div>

      <div id="ptab-routine" class="ptab" style="display:none">
        ${analyses.length ? (() => {
          const lastPathologie   = analyses[0].pathologie;
          const lastPathologieFr = analyses[0].pathologie_fr;
          const col = PATHO_COLORS[lastPathologie] || '#b5a89e';
          return `
            <div style="margin-top:1rem;font-size:.78rem;color:var(--txt2);margin-bottom:1rem">
              Basée sur le dernier diagnostic : <strong style="color:${col}">${lastPathologieFr}</strong>
            </div>
            <div class="moment-tabs">
              <button class="moment-tab active" onclick="switchPatientRoutine('matin', this)">Matin</button>
              <button class="moment-tab" onclick="switchPatientRoutine('soir', this)">Soir</button>
            </div>
            <div id="pt-routine-matin" style="display:block;margin-top:.8rem">
              ${(ROUTINES?.[lastPathologie]?.matin || []).map((s,i) => `
                <div class="routine-step-full">
                  <div class="rsf-num" style="background:${col}18;border-color:${col}40;color:${col}">${i+1}</div>
                  <div>
                    <div class="rsf-title">${s.nom}</div>
                    <div class="rsf-desc">${s.desc}</div>
                    <span class="rsf-tag" style="background:${col}18;color:${col};border-color:${col}40">${s.tag}</span>
                  </div>
                </div>`).join('')}
            </div>
            <div id="pt-routine-soir" style="display:none;margin-top:.8rem">
              ${(ROUTINES?.[lastPathologie]?.soir || []).map((s,i) => `
                <div class="routine-step-full">
                  <div class="rsf-num" style="background:${col}18;border-color:${col}40;color:${col}">${i+1}</div>
                  <div>
                    <div class="rsf-title">${s.nom}</div>
                    <div class="rsf-desc">${s.desc}</div>
                    <span class="rsf-tag" style="background:${col}18;color:${col};border-color:${col}40">${s.tag}</span>
                  </div>
                </div>`).join('')}
            </div>`;
        })() : '<div class="empty-state" style="margin-top:1rem">Aucun diagnostic — lancez une analyse d\'abord.</div>'}
      </div>

      <div id="ptab-avantapres" class="ptab" style="display:none">
        <div style="margin-top:1rem">
          <div class="aa-grid">
            <div class="aa-card" id="pt-aa-card-avant" onclick="document.getElementById('pt-aa-input-avant').click()">
              <div class="aa-label">Avant</div>
              <img class="aa-img" id="pt-aa-img-avant" alt="avant">
              <div class="aa-placeholder" id="pt-aa-ph-avant">Cliquer pour importer</div>
              <div class="aa-result" id="pt-aa-res-avant"></div>
            </div>
            <div class="aa-card" id="pt-aa-card-apres" onclick="document.getElementById('pt-aa-input-apres').click()">
              <div class="aa-label">Après</div>
              <img class="aa-img" id="pt-aa-img-apres" alt="après">
              <div class="aa-placeholder" id="pt-aa-ph-apres">Cliquer pour importer</div>
              <div class="aa-result" id="pt-aa-res-apres"></div>
            </div>
          </div>
          <input type="file" id="pt-aa-input-avant" accept="image/*" style="display:none" onchange="handlePatientAA('avant',this)">
          <input type="file" id="pt-aa-input-apres" accept="image/*" style="display:none" onchange="handlePatientAA('apres',this)">
          <button class="btn btn-main" id="pt-btn-aa" onclick="runPatientAA(${p.id})" disabled style="margin-top:.8rem">Comparer les deux analyses</button>
          <div class="loader" id="pt-aa-loader" style="margin-top:.8rem">
            <div class="spin"></div><span>Analyse en cours…</span>
          </div>
          <div class="evolution-box" id="pt-evolution-box" style="margin-top:.8rem;display:none">
            <div class="evo-title">Évolution détectée</div>
            <div id="pt-evo-content"></div>
          </div>
        </div>
      </div>`;

    // ← ICI après fiche.innerHTML, à l'intérieur du try
    window._lastAnalyses = analyses;
    document.querySelectorAll('.ptab').forEach(t => t.style.display = 'none');
    document.getElementById('ptab-dossier').style.display = 'block';

    if (analyses.length > 1) {
      setTimeout(() => drawEvolutionChart(analyses), 300);
    }

  } catch (e) {
    fiche.innerHTML = `<div class="empty-state">Erreur : ${e.message}</div>`;
  }
}

function analyserPatient(patientId, patientName) {
  const navEl = document.querySelector('.nav-item');
  navigate('analyse', navEl);
  const sel = document.getElementById('patient-select');
  if (!sel) return;
  const trySelect = setInterval(() => {
    for (let opt of sel.options) {
      if (opt.value == patientId) {
        sel.value = patientId;
        sel.style.borderColor = 'var(--terra)';
        sel.style.background  = 'var(--terra-l)';
        setTimeout(() => {
          sel.style.borderColor = '';
          sel.style.background  = '';
        }, 2000);
        clearInterval(trySelect);
        break;
      }
    }
  }, 100);
}


function closePatient() {
  currentPatientId = null;
  document.getElementById('patient-fiche').style.display  = 'none';
  document.getElementById('patients-list').style.display  = 'block';
  document.getElementById('btn-new-patient').style.display = 'inline-block';
}

async function deletePatient(id) {
  if (!confirm('Supprimer ce patient ? Ses analyses resteront dans l\'historique général.')) return;
  await fetch(`${API}/patients/${id}`, { method: 'DELETE' });
  loadPatients();
  loadPatientsDropdown();
}



// ── Dropdown patient dans page Analyse ───────────────────────────────────────
async function loadPatientsDropdown() {
  const sel = document.getElementById('patient-select');
  if (!sel) return;
  try {
    const res  = await fetch(`${API}/patients`);
    const data = await res.json();
    sel.innerHTML = '<option value="">— Analyse sans patient —</option>' +
      data.patients.map(p => `<option value="${p.id}">${p.prenom} ${p.nom} (${p.age} ans)</option>`).join('');
  } catch {}
}

// ── Rapport PDF patient complet ───────────────────────────────────────────────
async function generatePatientPDF(patientId) {
  const res  = await fetch(`${API}/patients/${patientId}`);
  const data = await res.json();
  const p    = data.patient;
  const analyses = data.analyses;

  const { jsPDF } = window.jspdf;
  const doc = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' });
  const W = 210, M = 18;
  let y = 0;

  const TERRA = [196,124,90], MAUVE = [155,127,166];
  const TXT   = [42,31,26],   TXT2  = [122,104,96];
  const BG3   = [245,240,235], WHITE = [255,255,255];
  const PATHO_COLORS_RGB = {
    saine:[122,158,135], acne_inflammatoire:[196,124,90],
    acne_non_inflammatoire:[212,168,130], rosacee:[155,127,166], hyperpigmentation:[122,158,135]
  };

  // Header
  doc.setFillColor(...TERRA);
  doc.rect(0, 0, W, 28, 'F');
  doc.setTextColor(...WHITE);
  doc.setFont('helvetica','bold'); doc.setFontSize(18);
  doc.text('SkinSight AI', M, 12);
  doc.setFont('helvetica','normal'); doc.setFontSize(8);
  doc.text('Dossier patient complet', M, 18);
  const now = new Date();
  doc.text(now.toLocaleDateString('fr-FR',{day:'2-digit',month:'long',year:'numeric'}), W-M, 12, {align:'right'});
  y = 36;

  // Infos patient
  doc.setFillColor(...BG3);
  doc.rect(M, y, W-2*M, 22, 'F');
  doc.setTextColor(...TERRA); doc.setFont('helvetica','bold'); doc.setFontSize(12);
  doc.text(`${p.prenom} ${p.nom}`, M+4, y+8);
  doc.setTextColor(...TXT2); doc.setFont('helvetica','normal'); doc.setFontSize(8);
  doc.text(`${p.age} ans · ${p.sexe === 'M' ? 'Homme' : 'Femme'} · Phototype ${p.phototype}`, M+4, y+14);
  doc.text(`Patient depuis le ${p.date_creation} · ${analyses.length} analyse(s)`, M+4, y+19);
  y += 28;

  // Historique
  doc.setTextColor(...TERRA); doc.setFont('helvetica','bold'); doc.setFontSize(9);
  doc.text('HISTORIQUE DES ANALYSES', M, y); y += 8;

  analyses.forEach((a, i) => {
    if (y > 265) { doc.addPage(); y = 20; }
    const col = PATHO_COLORS_RGB[a.pathologie] || MAUVE;
    doc.setFillColor(...col);
    doc.rect(M, y, 3, 10, 'F');
    doc.setTextColor(...TXT); doc.setFont('helvetica','bold'); doc.setFontSize(8);
    doc.text(a.pathologie_fr, M+6, y+4);
    doc.setTextColor(...TXT2); doc.setFont('helvetica','normal'); doc.setFontSize(7);
    doc.text(`${a.date} · Confiance : ${a.confiance}%`, M+6, y+9);

    // Barre confiance
    doc.setFillColor(...BG3);
    doc.rect(W-M-50, y+2, 50, 3, 'F');
    doc.setFillColor(...col);
    doc.rect(W-M-50, y+2, 50*a.confiance/100, 3, 'F');
    y += 13;
  });

  // Footer
  doc.setFillColor(...BG3); doc.rect(0,285,W,12,'F');
  doc.setTextColor(...TXT2); doc.setFont('helvetica','normal'); doc.setFontSize(7);
  doc.text('SkinSight AI · Dossier patient confidentiel · Usage médical uniquement', W/2, 291, {align:'center'});

  doc.save(`SkinSight_Patient_${p.nom}_${p.prenom}.pdf`);
}

function drawEvolutionChart(analyses) {
  const canvas = document.getElementById('evolution-chart');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  
  // ← CORRECTION : Forcer les dimensions si offsetWidth est 0 (canvas non encore rendu)
  let W = canvas.offsetWidth;
  let H = canvas.offsetHeight || 120;
  if (W === 0) { 
    W = canvas.parentElement?.offsetWidth - 30 || 400; 
    canvas.width = W; 
    canvas.height = H; 
  } else {
    canvas.width = W;
    canvas.height = H;
  }

  const PATHO_COLORS_HEX = {
    saine:                  '#7a9e87',
    acne_inflammatoire:     '#c47c5a',
    acne_non_inflammatoire: '#d4a882',
    rosacee:                '#9b7fa6',
    hyperpigmentation:      '#7a9e87',
  };

  // Données inversées (chronologique)
  const data = [...analyses].reverse();
  const N    = data.length;
  const padL = 35, padR = 15, padT = 10, padB = 25;
  const chartW = W - padL - padR;
  const chartH = H - padT - padB;

  // Grille
  ctx.strokeStyle = '#ece5de';
  ctx.lineWidth   = 0.5;
  [0, 25, 50, 75, 100].forEach(v => {
    const y = padT + chartH - (v / 100) * chartH;
    ctx.beginPath();
    ctx.moveTo(padL, y);
    ctx.lineTo(W - padR, y);
    ctx.stroke();

    ctx.fillStyle = '#b5a89e';
    ctx.font = '9px DM Sans, sans-serif';
    ctx.textAlign = 'right';
    ctx.fillText(`${v}%`, padL - 4, y + 3);
  });

  // Courbe
  ctx.beginPath();
  data.forEach((a, i) => {
    const x = padL + (i / (N - 1)) * chartW;
    const y = padT + chartH - (a.confiance / 100) * chartH;
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.strokeStyle = '#c47c5a';
  ctx.lineWidth   = 2;
  ctx.stroke();

  // Aire sous la courbe
  ctx.beginPath();
  data.forEach((a, i) => {
    const x = padL + (i / (N - 1)) * chartW;
    const y = padT + chartH - (a.confiance / 100) * chartH;
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.lineTo(padL + chartW, padT + chartH);
  ctx.lineTo(padL, padT + chartH);
  ctx.closePath();
  ctx.fillStyle = 'rgba(196,124,90,0.08)';
  ctx.fill();

  // Points colorés par pathologie
  data.forEach((a, i) => {
    const x   = padL + (i / (N - 1)) * chartW;
    const y   = padT + chartH - (a.confiance / 100) * chartH;
    const col = PATHO_COLORS_HEX[a.pathologie] || '#c47c5a';

    ctx.beginPath();
    ctx.arc(x, y, 5, 0, Math.PI * 2);
    ctx.fillStyle = col;
    ctx.fill();
    ctx.strokeStyle = '#fff';
    ctx.lineWidth   = 1.5;
    ctx.stroke();

    // Date sous le point
    ctx.fillStyle  = '#b5a89e';
    ctx.font       = '8px DM Sans, sans-serif';
    ctx.textAlign  = 'center';
    ctx.fillText(a.date.slice(5, 10), x, H - 5);
  });
}

// ── Onglets fiche patient ─────────────────────────────────────────────────────
function switchPatientTab(tab, el) {
  document.querySelectorAll('.ptab').forEach(t => {
    t.style.display = 'none';
  });
  document.getElementById('ptab-' + tab).style.display = 'block';
  el.closest('.moment-tabs').querySelectorAll('.moment-tab').forEach(b => b.classList.remove('active'));
  el.classList.add('active');
  
  // Redessiner le graphique si on revient sur Dossier
  if (tab === 'dossier') {
    const canvas = document.getElementById('evolution-chart');
    if (canvas && window._lastAnalyses) {
      setTimeout(() => drawEvolutionChart(window._lastAnalyses), 100);
    }
  }
}

function switchPatientRoutine(moment, el) {
  document.getElementById('pt-routine-matin').style.display = moment === 'matin' ? 'block' : 'none';
  document.getElementById('pt-routine-soir').style.display  = moment === 'soir'  ? 'block' : 'none';
  el.closest('.moment-tabs').querySelectorAll('.moment-tab').forEach(b => b.classList.remove('active'));
  el.classList.add('active');
}

// ── Avant/Après patient ───────────────────────────────────────────────────────
let ptAaFiles = { avant: null, apres: null };

function handlePatientAA(side, input) {
  const file = input.files[0];
  if (!file) return;
  ptAaFiles[side] = file;
  const img  = document.getElementById('pt-aa-img-'  + side);
  const ph   = document.getElementById('pt-aa-ph-'   + side);
  const card = document.getElementById('pt-aa-card-' + side);
  const reader = new FileReader();
  reader.onload = e => {
    img.src = e.target.result;
    img.style.display = 'block';
    ph.style.display  = 'none';
    card.classList.add('has-img');
  };
  reader.readAsDataURL(file);
  if (ptAaFiles.avant && ptAaFiles.apres)
    document.getElementById('pt-btn-aa').disabled = false;
}

async function runPatientAA(patientId) {
  document.getElementById('pt-aa-loader').classList.add('show');
  document.getElementById('pt-evolution-box').classList.remove('show');
  document.getElementById('pt-btn-aa').disabled = true;

  async function analyseSide(side) {
    const fd = new FormData();
    fd.append('file', ptAaFiles[side]);
    const url = `${API}/predict?patient_id=${patientId}`;
    const res  = await fetch(url, { method: 'POST', body: fd });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail);
    const col = window.COLORS?.[data.pathologie] || '#b5a89e';
    const box = document.getElementById('pt-aa-res-' + side);
    box.innerHTML = `<span style="font-weight:500;color:${col}">${data.pathologie_fr}</span> — ${data.confiance}%`;
    box.classList.add('show');
    return data;
  }

  try {
    const [avant, apres] = await Promise.all([analyseSide('avant'), analyseSide('apres')]);
    const same = avant.pathologie === apres.pathologie;
    const colA = window.COLORS?.[avant.pathologie] || '#b5a89e';
    const colB = window.COLORS?.[apres.pathologie] || '#b5a89e';
    let msg = apres.pathologie === 'saine' && avant.pathologie !== 'saine'
      ? "Excellente évolution — peau améliorée significativement."
      : same ? "Situation stable — même pathologie sur les deux photos."
      : "Changement de pathologie détecté entre les deux photos.";
    document.getElementById('pt-evo-content').innerHTML = `
      <div style="display:flex;align-items:center;gap:.5rem;font-size:.82rem;margin-bottom:.5rem">
        <span style="color:${colA};font-weight:500">${avant.pathologie_fr} (${avant.confiance}%)</span>
        <span>→</span>
        <span style="color:${colB};font-weight:500">${apres.pathologie_fr} (${apres.confiance}%)</span>
      </div>
      <div style="font-size:.76rem;color:var(--txt2)">${msg}</div>`;
    document.getElementById('pt-evolution-box').classList.add('show');
  } catch(e) {
    alert('Erreur : ' + e.message);
  } finally {
    document.getElementById('pt-aa-loader').classList.remove('show');
    document.getElementById('pt-btn-aa').disabled = false;
  }
}

// Init
document.addEventListener('DOMContentLoaded', () => {
  loadPatientsDropdown();
});