/* app.js - Frontend logic for Student Risk Stratification System */

const RISK_COLORS = { 0: '#22c55e', 1: '#f59e0b', 2: '#f97316', 3: '#ef4444' };
const RISK_ICONS  = { 0: '🟢', 1: '🟡', 2: '🟠', 3: '🔴' };

// ── Demo data presets ─────────────────────────────────────────
const DEMO_PRESETS = {
  low: {
    gender_num: 0, age_num: 0, education_num: 3, imd_band_num: 8, disability_num: 0,
    num_of_prev_attempts: 0, studied_credits: 60,
    early_registration: 1, reg_days_before: 45, unregistered: 0,
    total_clicks: 2500, active_days: 80, avg_clicks_day: 31.2, max_clicks_day: 120,
    n_resources: 18, click_density: 3.5,
    avg_score: 82.5, min_score: 70.0, std_score: 5.2, avg_tma_score: 85.0,
    n_submitted: 5, n_late: 0, avg_submit_delay: -5.5
  },
  high: {
    gender_num: 1, age_num: 1, education_num: 0, imd_band_num: 2, disability_num: 1,
    num_of_prev_attempts: 2, studied_credits: 120,
    early_registration: 0, reg_days_before: 5, unregistered: 0,
    total_clicks: 120, active_days: 10, avg_clicks_day: 3.1, max_clicks_day: 25,
    n_resources: 5, click_density: 0.8,
    avg_score: 35.0, min_score: 15.0, std_score: 15.0, avg_tma_score: 38.0,
    n_submitted: 2, n_late: 2, avg_submit_delay: 2.5
  }
};

// Float fields to parse correctly
const FLOAT_FIELDS = ['avg_clicks_day', 'click_density', 'avg_score', 'min_score', 'std_score', 'avg_tma_score', 'avg_submit_delay'];

// ── Tab switching ─────────────────────────────────────────────
function showTab(tabId) {
  document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
  document.getElementById('tab-' + tabId).classList.add('active');
  if (event && event.target) {
    event.target.classList.add('active');
  }
}

// ── Modal ─────────────────────────────────────────────────────
function openModal(src, title) {
  const modalImg = document.getElementById('modalImg');
  const modalTitle = document.getElementById('modalTitle');
  const modalOverlay = document.getElementById('modalOverlay');
  if (modalImg && modalTitle && modalOverlay) {
    modalImg.src = src;
    modalTitle.textContent = title;
    modalOverlay.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
  }
}
function closeModal() {
  const modalOverlay = document.getElementById('modalOverlay');
  if (modalOverlay) {
    modalOverlay.classList.add('hidden');
    document.body.style.overflow = '';
  }
}

// ── Fill demo data ────────────────────────────────────────────
const demoBtn = document.getElementById('demoBtn');
if (demoBtn) {
  demoBtn.addEventListener('click', function() {
    const preset = this._toggle ? DEMO_PRESETS.low : DEMO_PRESETS.high;
    this._toggle = !this._toggle;
    Object.entries(preset).forEach(([key, val]) => {
      const el = document.getElementById(key);
      if (el) el.value = val;
    });
    this.textContent = this._toggle ? '📋 Demo Rủi Ro Thấp' : '📋 Demo Rủi Ro Cao';
  });
}

// ── Form submit ───────────────────────────────────────────────
const predictForm = document.getElementById('predictForm');
if (predictForm) {
  predictForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    const btn = document.getElementById('predictBtn');
    const btnText = document.getElementById('btnText');
    const btnSpinner = document.getElementById('btnSpinner');

    // Loading state
    if (btnText) btnText.classList.add('hidden');
    if (btnSpinner) btnSpinner.classList.remove('hidden');
    if (btn) btn.disabled = true;

    const formData = new FormData(this);
    const payload = {};
    formData.forEach((val, key) => {
      payload[key] = FLOAT_FIELDS.includes(key) ? parseFloat(val) : parseInt(val);
    });

    try {
      const res = await fetch('/api/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Lỗi server');
      }

      const data = await res.json();
      showResult(data);

    } catch (err) {
      if (err.message.includes('fetch') || err.message.includes('Failed')) {
        showResult(simulateResult(payload));
      } else {
        alert('❌ Lỗi: ' + err.message);
      }
    } finally {
      if (btnText) btnText.classList.remove('hidden');
      if (btnSpinner) btnSpinner.classList.add('hidden');
      if (btn) btn.disabled = false;
    }
  });
}

// ── Simulate result (demo mode without API) ───────────────────
function simulateResult(payload) {
  const score = payload.avg_score;
  const clicks = payload.total_clicks;
  const attempts = payload.num_of_prev_attempts;
  
  let level = 0;
  if (score < 40 || clicks < 150) level = 3;
  else if (score < 55 || clicks < 400) level = 2;
  else if (score < 65 || clicks < 800) level = 1;
  
  if (attempts >= 2) level = Math.min(3, level + 1);

  const labels = ['Low', 'Medium', 'High', 'Very High'];
  const recs = [
    'Sinh viên đang có tiến độ học tập tốt. Tiếp tục duy trì và tham gia đầy đủ các hoạt động học tập.',
    'Sinh viên cần chú ý hơn đến việc học. Nên tăng cường tương tác với hệ thống VLE.',
    'Sinh viên có nguy cơ cao cần được hỗ trợ ngay. Giảng viên nên liên hệ trực tiếp.',
    'Sinh viên có nguy cơ rất cao bỏ học. Cần can thiệp khẩn cấp từ cố vấn học thuật.'
  ];

  const baseProbs = [0.1, 0.1, 0.1, 0.1];
  baseProbs[level] = 0.65;
  const remaining = 0.35;
  [0,1,2,3].filter(i=>i!==level).forEach((i)=>{ baseProbs[i] = remaining / 3; });

  return {
    risk_level: level,
    risk_label: labels[level],
    confidence: Math.round(baseProbs[level] * 100),
    probabilities: {
      'Low': Math.round(baseProbs[0]*100*10)/10,
      'Medium': Math.round(baseProbs[1]*100*10)/10,
      'High': Math.round(baseProbs[2]*100*10)/10,
      'Very High': Math.round(baseProbs[3]*100*10)/10
    },
    recommendation: recs[level],
    model_used: 'LightGBM (Demo Mode)'
  };
}

// ── Render result ─────────────────────────────────────────────
function showResult(data) {
  const { risk_level, risk_label, confidence, probabilities, recommendation } = data;
  const color = RISK_COLORS[risk_level];

  const placeholder = document.getElementById('resultPlaceholder');
  if (placeholder) placeholder.classList.add('hidden');
  
  const content = document.getElementById('resultContent');
  if (content) {
    content.classList.remove('hidden');
    if (window.innerWidth < 900) {
      content.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }

  const iconEl = document.getElementById('riskIcon');
  if (iconEl) iconEl.textContent = RISK_ICONS[risk_level];
  
  const riskLevel = document.getElementById('riskLevel');
  if (riskLevel) {
    riskLevel.textContent = risk_label + ' Risk';
    riskLevel.style.color = color;
  }

  const ring = document.getElementById('confRing');
  if (ring) {
    const circumference = 314;
    const offset = circumference - (confidence / 100) * circumference;
    ring.style.stroke = color;
    setTimeout(() => { ring.style.strokeDashoffset = offset; }, 50);
  }
  
  const confVal = document.getElementById('confValue');
  if (confVal) confVal.textContent = Math.round(confidence) + '%';

  const probColors = { Low: '#22c55e', Medium: '#f59e0b', High: '#f97316', 'Very High': '#ef4444' };
  const probBars = document.getElementById('probBars');
  if (probBars) {
    probBars.innerHTML = '';
    Object.entries(probabilities).forEach(([label, pct]) => {
      probBars.innerHTML += `
        <div class="prob-row">
          <span class="prob-label">${label}</span>
          <div class="prob-track">
            <div class="prob-fill" style="width:0%;background:${probColors[label]}" 
                 data-width="${pct}"></div>
          </div>
          <span class="prob-val" style="color:${probColors[label]}">${pct}%</span>
        </div>`;
    });
    setTimeout(() => {
      probBars.querySelectorAll('.prob-fill').forEach(el => {
        el.style.width = el.dataset.width + '%';
      });
    }, 100);
  }

  const recText = document.getElementById('recText');
  if (recText) recText.textContent = recommendation;
  
  const recEl = document.getElementById('recommendation');
  if (recEl) recEl.style.borderLeft = `3px solid ${color}`;
}

const sections = document.querySelectorAll('section[id]');
const navLinks = document.querySelectorAll('.nav-link');
window.addEventListener('scroll', () => {
  let current = '';
  sections.forEach(s => {
    if (window.scrollY >= s.offsetTop - 120) current = s.id;
  });
  navLinks.forEach(l => {
    l.classList.toggle('active', l.getAttribute('href') === '#' + current);
  });
}, { passive: true });

document.addEventListener('keydown', e => {
  if (e.key === 'Escape') closeModal();
});
