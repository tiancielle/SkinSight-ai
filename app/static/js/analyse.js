// ── State ─────────────────────────────────────────────────────────────────────
let currentFile = null;
let lastResult  = null;

// ── File handling ─────────────────────────────────────────────────────────────
function handleFile(file) {
  if (!file) return;
  currentFile = file;
  const reader = new FileReader();
  reader.onload = e => {
    const prev = document.getElementById('uz-preview');
    prev.src = e.target.result;
    prev.style.display = 'block';
    document.getElementById('uz-title').textContent = file.name;
    document.getElementById('btn-analyse').disabled = false;
  };
  reader.readAsDataURL(file);
}

function handleDrop(e) {
  e.preventDefault();
  document.getElementById('upload-zone').classList.remove('drag');
  const file = e.dataTransfer.files[0];
  if (file && file.type.startsWith('image/')) handleFile(file);
}

// ── Analyse ───────────────────────────────────────────────────────────────────
async function runAnalysis() {
  if (!currentFile) return;

  
  document.getElementById('loader').classList.add('show');
  document.getElementById('result-box').classList.remove('show');
  document.getElementById('btn-analyse').disabled = true;

  const formData = new FormData();
  formData.append('file', currentFile);

  // ← Ajout : récupération du patient_id depuis le dropdown
  const patientId = document.getElementById('patient-select')?.value || null;
  const url = patientId ? `${API}/predict?patient_id=${patientId}` : `${API}/predict`;

  try {
    const res  = await fetch(url, { method: 'POST', body: formData });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Erreur API');
    lastResult = data;
    localStorage.setItem('skinsight_last_result', JSON.stringify(data));
    renderResult(data);
    refreshStats();
  } catch (err) {
    alert('Erreur : ' + err.message + '\n\nVérifie que le serveur FastAPI tourne sur :8000\n→ uvicorn app.api.main:app --reload --port 8000');
  } finally {
    document.getElementById('loader').classList.remove('show');
    document.getElementById('btn-analyse').disabled = false;
  }
}

// ── Render result ─────────────────────────────────────────────────────────────
function renderResult(data) {
  const box = document.getElementById('result-box');
  document.getElementById('btn-pdf').style.display = 'inline-block';
  
  // Diagnostic + sévérité
  document.getElementById('result-name').textContent = data.pathologie_fr;
  
  // ← Ajout : affichage du patient sélectionné
  const patientSelect = document.getElementById('patient-select');
  const patientName = patientSelect?.options[patientSelect.selectedIndex]?.text || '';
  const patientBox = document.getElementById('result-patient');
  if (patientName && patientSelect.value) {
    patientBox.textContent = 'Patient : ' + patientName;
    patientBox.style.display = 'block';
  } else {
    patientBox.style.display = 'none';
  }
  
  const severiteColors = {
    'Sévère':                    '#c47c5a',
    'Modéré':                    '#d4a882',
    'Léger':                     '#7a9e87',
    'Aucune pathologie détectée':'#7a9e87',
  };
  document.getElementById('result-severite').textContent = data.severite || '';
  document.getElementById('result-severite').style.color = severiteColors[data.severite] || '#b5a89e';
  document.getElementById('result-badge').textContent    = `${data.confiance}% de confiance`;
  document.getElementById('conf-label-main').textContent = data.pathologie_fr;

  setTimeout(() => {
    document.getElementById('bar-main').style.width = data.confiance + '%';
  }, 100);

  // Scores par classe
  const scoresList  = document.getElementById('scores-list');
  scoresList.innerHTML = '';
  const scoreColors = {
    acne_inflammatoire:     '#c47c5a',
    acne_non_inflammatoire: '#d4a882',
    rosacee:                '#9b7fa6',
    hyperpigmentation:      '#7a9e87',
    saine:                  '#b5a89e',
  };
  const sorted = Object.entries(data.scores_raw).sort((a, b) => b[1] - a[1]);
  sorted.forEach(([cls, val]) => {
    const row = document.createElement('div');
    row.className = 'score-row';
    row.innerHTML = `
      <span class="score-name">${CLASSES_FR[cls]}</span>
      <div class="score-bar"><div class="score-fill" style="background:${scoreColors[cls]};width:0%" data-w="${val}"></div></div>
      <span class="score-pct">${val.toFixed(1)}%</span>`;
    scoresList.appendChild(row);
  });
  setTimeout(() => {
    scoresList.querySelectorAll('.score-fill').forEach(el => el.style.width = el.dataset.w + '%');
  }, 150);

  // Recommandations
  document.getElementById('reco-grid').innerHTML = data.recommandations.map(r =>
    `<div class="reco-card"><div class="reco-cat">${r.cat}</div><div class="reco-text">${r.texte}</div></div>`
  ).join('');

  // Routine
  renderRoutinePreview(data.routine, 'matin');
  buildFullRoutine(data.routine, data.pathologie_fr, COLORS[data.pathologie]);

  box.classList.add('show');
  box.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// ── Routine preview ───────────────────────────────────────────────────────────
function renderRoutinePreview(routine, moment) {
  const steps = (routine[moment] || []).slice(0, 3);
  document.getElementById('routine-preview-steps').innerHTML = steps.map((s, i) => `
    <div class="routine-step">
      <div class="step-num">${i + 1}</div>
      <div><div class="step-name">${s.nom}</div><div class="step-desc">${s.desc}</div></div>
    </div>`).join('');
}

function switchPreviewMoment(m) {
  document.getElementById('tbm').classList.toggle('active', m === 'matin');
  document.getElementById('tbs').classList.toggle('active', m === 'soir');
  if (lastResult) renderRoutinePreview(lastResult.routine, m);
}

function buildFullRoutine(routine, pathFr, color) {
  document.getElementById('routine-sub').textContent = `Basée sur le dernier diagnostic · ${pathFr}`;
  ['matin', 'soir'].forEach(m => {
    const steps = routine[m] || [];
    document.getElementById('rf-' + m).innerHTML = steps.map((s, i) => `
      <div class="routine-step-full">
        <div class="rsf-num" style="background:${color}18;border-color:${color}40;color:${color}">${i + 1}</div>
        <div>
          <div class="rsf-title">${s.nom}</div>
          <div class="rsf-desc">${s.desc}</div>
          <span class="rsf-tag" style="background:${color}18;color:${color};border-color:${color}40">${s.tag}</span>
        </div>
      </div>`).join('');
  });
}

function switchFullMoment(m, el) {
  document.querySelectorAll('.moment-tab').forEach(t => t.classList.remove('active'));
  el.classList.add('active');
  document.querySelectorAll('.routine-section').forEach(r => r.classList.remove('active'));
  document.getElementById('rf-' + m).classList.add('active');
}

// ── Rapport PDF ───────────────────────────────────────────────────────────────
async function generatePDF() {
  if (!lastResult) return;

  const { jsPDF } = window.jspdf;
  const doc = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' });

  const W = 210, M = 18;
  let y = 0;

  // ── Couleurs ──
  const TERRA  = [196, 124, 90];
  const MAUVE  = [155, 127, 166];
  const TXT    = [42,  31,  26];
  const TXT2   = [122, 104, 96];
  const BG3    = [245, 240, 235];
  const WHITE  = [255, 255, 255];

  const severiteColor = {
    'Sévère':                    [196, 124, 90],
    'Modéré':                    [212, 168, 130],
    'Léger':                     [122, 158, 135],
    'Aucune pathologie détectée':[122, 158, 135],
  };

  // ── Header ────────────────────────────────────────────────────────────────
  doc.setFillColor(...TERRA);
  doc.rect(0, 0, W, 28, 'F');

  doc.setTextColor(...WHITE);
  doc.setFont('helvetica', 'bold');
  doc.setFontSize(18);
  doc.text('SkinSight AI', M, 12);

  doc.setFont('helvetica', 'normal');
  doc.setFontSize(8);
  doc.text('Rapport d\'analyse dermatologique', M, 18);

  const now = new Date();
  const dateStr = now.toLocaleDateString('fr-FR', { day:'2-digit', month:'long', year:'numeric' });
  const timeStr = now.toLocaleTimeString('fr-FR', { hour:'2-digit', minute:'2-digit' });
  doc.text(`${dateStr} à ${timeStr}`, W - M, 12, { align: 'right' });

  const profName = localStorage.getItem('skinsight_name') || '—';
  doc.text(`Opérateur : ${profName}`, W - M, 18, { align: 'right' });

  y = 36;

  // ── Image + Diagnostic côte à côte ────────────────────────────────────────
  // Image
  try {
    const imgEl = document.getElementById('uz-preview');
    if (imgEl && imgEl.src && !imgEl.src.endsWith('#')) {
      const canvas = document.createElement('canvas');
      canvas.width = 200; canvas.height = 200;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(imgEl, 0, 0, 200, 200);
      const imgData = canvas.toDataURL('image/jpeg', 0.8);
      doc.addImage(imgData, 'JPEG', M, y, 50, 50);

      // Cadre autour image
      doc.setDrawColor(...TERRA);
      doc.setLineWidth(0.5);
      doc.rect(M, y, 50, 50);
    }
  } catch (e) { console.warn('Image non disponible'); }

  // Diagnostic
  const diagX = M + 55;
  doc.setTextColor(...TXT2);
  doc.setFont('helvetica', 'normal');
  doc.setFontSize(7);
  doc.text('DIAGNOSTIC IA', diagX, y + 6);

  doc.setTextColor(...TXT);
  doc.setFont('helvetica', 'bold');
  doc.setFontSize(14);
  doc.text(lastResult.pathologie_fr, diagX, y + 14);

  // Sévérité badge
  const sev = lastResult.severite || '';
  const sevColor = severiteColor[sev] || MAUVE;
  doc.setFillColor(...sevColor);
  doc.roundedRect(diagX, y + 17, 35, 7, 2, 2, 'F');
  doc.setTextColor(...WHITE);
  doc.setFont('helvetica', 'bold');
  doc.setFontSize(8);
  doc.text(sev, diagX + 17.5, y + 22, { align: 'center' });

  // Confiance
  doc.setTextColor(...TXT2);
  doc.setFont('helvetica', 'normal');
  doc.setFontSize(8);
  doc.text(`Confiance : ${lastResult.confiance}%`, diagX, y + 30);

  // Barre de confiance
  doc.setFillColor(...BG3);
  doc.roundedRect(diagX, y + 33, 80, 4, 1, 1, 'F');
  doc.setFillColor(...TERRA);
  doc.roundedRect(diagX, y + 33, 80 * lastResult.confiance / 100, 4, 1, 1, 'F');

  // Modèle
  doc.setTextColor(...TXT2);
  doc.setFontSize(7);
  doc.text('Modèle : LightGBM · Pipeline CNN (MobileNetV2 + DenseNet121 + InceptionV3) → PCA-512', diagX, y + 43);

  y += 58;

  // ── Scores par classe ─────────────────────────────────────────────────────
  doc.setFillColor(...BG3);
  doc.rect(M, y, W - 2*M, 8, 'F');
  doc.setTextColor(...TERRA);
  doc.setFont('helvetica', 'bold');
  doc.setFontSize(9);
  doc.text('SCORES PAR CLASSE', M + 3, y + 5.5);
  y += 12;

  const scoreColors = {
    acne_inflammatoire:     [196, 124, 90],
    acne_non_inflammatoire: [212, 168, 130],
    rosacee:                [155, 127, 166],
    hyperpigmentation:      [122, 158, 135],
    saine:                  [181, 168, 158],
  };

  const sorted = Object.entries(lastResult.scores_raw).sort((a, b) => b[1] - a[1]);
  sorted.forEach(([cls, val]) => {
    const clsFr = CLASSES_FR[cls] || cls;
    const col   = scoreColors[cls] || MAUVE;
    const barW  = 80 * val / 100;

    doc.setTextColor(...TXT);
    doc.setFont('helvetica', 'normal');
    doc.setFontSize(8);
    doc.text(clsFr, M, y + 3.5);

    doc.setFillColor(...BG3);
    doc.roundedRect(M + 55, y, 80, 4, 1, 1, 'F');
    doc.setFillColor(...col);
    if (barW > 0) doc.roundedRect(M + 55, y, barW, 4, 1, 1, 'F');

    doc.setTextColor(...TXT2);
    doc.setFontSize(7.5);
    doc.text(`${val.toFixed(1)}%`, M + 140, y + 3.5);

    y += 8;
  });

  y += 4;

  // ── Recommandations ───────────────────────────────────────────────────────
  doc.setFillColor(...BG3);
  doc.rect(M, y, W - 2*M, 8, 'F');
  doc.setTextColor(...TERRA);
  doc.setFont('helvetica', 'bold');
  doc.setFontSize(9);
  doc.text('RECOMMANDATIONS DE SOINS', M + 3, y + 5.5);
  y += 12;

  const recos = lastResult.recommandations || [];
  recos.forEach(r => {
    doc.setFillColor(247, 237, 230);
    doc.roundedRect(M, y, W - 2*M, 12, 2, 2, 'F');

    doc.setTextColor(...TERRA);
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(7);
    doc.text(r.cat.toUpperCase(), M + 3, y + 5);

    doc.setTextColor(...TXT);
    doc.setFont('helvetica', 'normal');
    doc.setFontSize(8);
    doc.text(r.texte, M + 3, y + 10);

    y += 15;
  });

  y += 4;

  // ── Protocole de soins ────────────────────────────────────────────────────
  if (lastResult.routine) {
    ['matin', 'soir'].forEach(moment => {
      const steps = lastResult.routine[moment] || [];
      if (!steps.length) return;

      // Nouvelle page si pas assez de place
      if (y > 230) { doc.addPage(); y = 20; }

      doc.setFillColor(...MAUVE);
      doc.rect(M, y, W - 2*M, 8, 'F');
      doc.setTextColor(...WHITE);
      doc.setFont('helvetica', 'bold');
      doc.setFontSize(9);
      doc.text(`PROTOCOLE ${moment.toUpperCase()}`, M + 3, y + 5.5);
      y += 12;

      steps.forEach((s, i) => {
        if (y > 265) { doc.addPage(); y = 20; }

        doc.setFillColor(240, 234, 244);
        doc.roundedRect(M, y, W - 2*M, 14, 2, 2, 'F');

        // Numéro
        doc.setFillColor(...MAUVE);
        doc.circle(M + 5, y + 7, 3.5, 'F');
        doc.setTextColor(...WHITE);
        doc.setFont('helvetica', 'bold');
        doc.setFontSize(8);
        doc.text(`${i + 1}`, M + 5, y + 8.5, { align: 'center' });

        // Contenu
        doc.setTextColor(...TXT);
        doc.setFont('helvetica', 'bold');
        doc.setFontSize(8);
        doc.text(s.nom, M + 11, y + 5.5);

        doc.setTextColor(...TXT2);
        doc.setFont('helvetica', 'normal');
        doc.setFontSize(7.5);
        const lines = doc.splitTextToSize(s.desc, W - 2*M - 15);
        doc.text(lines[0], M + 11, y + 10.5);

        y += 17;
      });
      y += 4;
    });
  }

  // ── Footer ────────────────────────────────────────────────────────────────
  const pageCount = doc.internal.getNumberOfPages();
  for (let i = 1; i <= pageCount; i++) {
    doc.setPage(i);
    doc.setFillColor(...BG3);
    doc.rect(0, 285, W, 12, 'F');
    doc.setTextColor(...TXT2);
    doc.setFont('helvetica', 'normal');
    doc.setFontSize(7);
    doc.text('SkinSight AI · Rapport généré automatiquement · À valider par un dermatologue certifié', W/2, 291, { align: 'center' });
    doc.text(`Page ${i} / ${pageCount}`, W - M, 291, { align: 'right' });
  }

  // ── Sauvegarde ────────────────────────────────────────────────────────────
  const filename = `SkinSight_${lastResult.pathologie}_${now.toISOString().slice(0,10)}.pdf`;
  doc.save(filename);
}

function initRoutinePage() {
  const stored = localStorage.getItem('skinsight_last_result');
  if (!stored) {
    document.getElementById('routine-sub').textContent = 'Aucun diagnostic — lancez une analyse d\'abord';
    document.getElementById('rf-matin').innerHTML = '<div class="empty-state">Aucun diagnostic disponible.</div>';
    document.getElementById('rf-soir').innerHTML  = '';
    return;
  }
  const data = JSON.parse(stored);
  buildFullRoutine(data.routine, data.pathologie_fr, COLORS[data.pathologie]);
}