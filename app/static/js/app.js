// ── Navigation ────────────────────────────────────────────────────────────────
const PAGE_TITLES = {
  analyse:    'Tableau de bord',
  routine:    'Ma routine',
  historique: 'Historique',
  fiches:     'Fiches pathologies',
  avantapres: 'Avant / Après',
  webcam:     'Webcam AR',
  patients:   'Dossiers patients',
};

function navigate(pageId, navEl) {
  const page = document.getElementById('page-' + pageId);
  if (!page) return;
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  page.classList.add('active');
  if (navEl) navEl.classList.add('active');
  const title = document.getElementById('topbar-title');
  if (title) title.textContent = PAGE_TITLES[pageId] || '';
  if (pageId === 'historique') loadHistory();
  if (pageId === 'patients')   loadPatients();
  if (pageId === 'routine')    initRoutinePage();
  if (pageId === 'fiches')     buildFiches();  // ← ajouter
}

// ── Stats ─────────────────────────────────────────────────────────────────────
async function refreshStats() {
  try {
    const res  = await fetch(`${API}/stats`);
    const data = await res.json();
    document.getElementById('stat-total').textContent = data.total;
    document.getElementById('stat-avg').textContent   = data.avg_confiance + '%';
    document.getElementById('sb-total').textContent   = data.total + ' analyse(s)';
    document.getElementById('sb-avg').textContent     = `Précision moy. ${data.avg_confiance}%`;
  } catch {}

  // ← Compteur patients
  try {
    const res2 = await fetch(`${API}/patients`);
    const data2 = await res2.json();
    const count = document.getElementById('patients-count');
    if (count && data2.patients.length) count.textContent = data2.patients.length;
  } catch {}
}

async function setLastStat() {
  try {
    const res  = await fetch(`${API}/history?limit=1`);
    const data = await res.json();
    if (data.history.length)
      document.getElementById('stat-last').textContent = data.history[0].confiance + '%';
  } catch {}
}

// ── Fiches ────────────────────────────────────────────────────────────────────
function buildFiches() {
  document.getElementById('fiche-grid').innerHTML = FICHES.map(f => `
    <div class="fiche-card">
      <div class="fiche-icon-wrap" style="background:${f.colorL};width:8px;height:8px;border-radius:50%"></div>
      <div class="fiche-title">${f.titre}</div>
      <div class="fiche-desc">${f.desc}</div>
      <div class="fiche-meta"><b style="color:${f.color}">Causes :</b> ${f.causes}</div>
      <div class="fiche-meta"><b style="color:${f.color}">Traitement :</b> ${f.traitement}</div>
      <span class="pill" style="background:${f.colorL};color:${f.color};border:1px solid ${f.color}40">${f.tag}</span>
    </div>`).join('');
}

// ── Profil ────────────────────────────────────────────────────────────────────
function genId() { return 'u_' + Math.random().toString(36).slice(2, 10); }

let selectedSkin = '';
function selectSkin(el, val) {
  document.querySelectorAll('.skin-btn').forEach(b => b.classList.remove('active'));
  el.classList.add('active');
  selectedSkin = val;
}

function saveProfile() {
  const name = document.getElementById('modal-name').value.trim();
  if (!name) { document.getElementById('modal-name').focus(); return; }
  const profile = {
    id:   localStorage.getItem('skinsight_id') || genId(),
    name,
    skin: selectedSkin || 'non renseigné',
  };
  localStorage.setItem('skinsight_id',   profile.id);
  localStorage.setItem('skinsight_name', profile.name);
  localStorage.setItem('skinsight_skin', profile.skin);
  document.getElementById('modal-overlay').classList.add('hidden');
  renderProfileBadge(profile.name, profile.skin);
}

//  MODIFIÉ : guard null pour éviter crash si badge absent
function renderProfileBadge(name, skin) {
  const badge = document.getElementById('profile-badge');
  if (!badge) return; // ← guard null
  badge.style.display = 'block';
  document.getElementById('pb-name').textContent = name;
  document.getElementById('pb-skin').textContent = 'Peau ' + skin;
}

//  MODIFIÉ : suppression du setTimeout qui ouvrait la modale automatiquement
function initProfile() {
  const name = localStorage.getItem('skinsight_name');
  const skin = localStorage.getItem('skinsight_skin');
  if (name) renderProfileBadge(name, skin || '—');
}

// ── Init ──────────────────────────────────────────────────────────────────────
// buildFiches();  ← SUPPRIMÉ : plus appelé au chargement initial
refreshStats();
setLastStat();
setInterval(refreshStats, 30000);
initProfile();