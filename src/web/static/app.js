/* app.js - Frontend logic for Student Risk Stratification System */

const RISK_COLORS = { 0: '#22c55e', 1: '#f59e0b', 2: '#f97316', 3: '#ef4444' };
const RISK_LABELS = { 0: 'LOW', 1: 'MEDIUM', 2: 'HIGH', 3: 'VERY HIGH' };

// ── Init on load ──────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  // Check if we are on a page with studentSearchInput
  const searchInput = document.getElementById('studentSearchInput');
  if (searchInput && searchInput.disabled && searchInput.value) {
    console.log("Student detected, auto-querying for:", searchInput.value);
    searchStudent();
  }

  // Handle Notifications from Query Params
  const urlParams = new URLSearchParams(window.location.search);
  const msg = urlParams.get('msg');
  const err = urlParams.get('error');

  if (msg) {
    const msgMap = {
      'login_success': { title: 'Đăng nhập thành công', text: 'Chào mừng bạn quay lại hệ thống.', type: 'success' },
      'logout_success': { title: 'Đăng xuất thành công', text: 'Hẹn gặp lại bạn lần sau.', type: 'info' },
      'reg_success': { title: 'Đăng ký thành công', text: 'Tài khoản của bạn đã được tạo.', type: 'success' },
      'password_reset_simulated': { title: 'Đã gửi yêu cầu', text: 'Yêu cầu khôi phục mật khẩu đã được xử lý.', type: 'info' }
    };
    const toastData = msgMap[msg] || { title: 'Thông báo', text: msg, type: 'info' };
    showToast(toastData.title, toastData.text, toastData.type);
  }

  if (err) {
    const errMap = {
      'auth_failed': { title: 'Đăng nhập thất bại', text: 'Sai tên đăng nhập hoặc mật khẩu.', type: 'error' },
      'reg_failed': { title: 'Đăng ký thất bại', text: 'Tên đăng nhập hoặc email đã tồn tại.', type: 'error' }
    };
    const toastData = errMap[err] || { title: 'Lỗi', text: err, type: 'error' };
    showToast(toastData.title, toastData.text, toastData.type);
  }

  // Handle Pending Trials after login
  const pendingTrial = sessionStorage.getItem('pending_trial');
  const isLoggedIn = !!document.querySelector('a[href="/api/v1/auth/logout"]');
  if (pendingTrial && isLoggedIn) {
    const trialData = JSON.parse(pendingTrial);
    fetch('/api/v1/student/persist-trial', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(trialData)
    }).then(() => {
      sessionStorage.removeItem('pending_trial');
      console.log("✅ Guest trial persisted after login");
    });
  }

  // Clean up URL without reloading
  if (msg || err) {
    const newUrl = window.location.pathname;
    window.history.replaceState({}, document.title, newUrl);
  }
});

// ── Toast Notification ────────────────────────────────────────
function showToast(title, message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `
    <div class="toast-content">
      <div class="toast-title">${title}</div>
      <div class="toast-msg">${message}</div>
    </div>
    <button class="toast-close" onclick="this.parentElement.remove()">✕</button>
  `;

  container.appendChild(toast);

  // Animate in
  setTimeout(() => toast.classList.add('show'), 10);

  // Auto remove after 5 seconds
  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => toast.remove(), 400); // Wait for transition
  }, 5000);
}

// ── Navigation & UI ───────────────────────────────────────────
function toggleDropdown(e) {
  e.stopPropagation();
  const dropdown = document.querySelector('.dropdown-content');
  if (dropdown) {
    dropdown.style.display = dropdown.style.display === 'block' ? 'none' : 'block';
  }
}

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
  const imgModal = document.getElementById('imgModal');
  if (modalOverlay) modalOverlay.classList.add('hidden');
  if (imgModal) imgModal.classList.remove('open');
  document.body.style.overflow = '';
}

// ── Official Search ───────────────────────────────────────────
async function searchStudent() {
  const searchInput = document.getElementById('studentSearchInput');
  const studentId = searchInput ? searchInput.value : null;
  if (!studentId) return;

  const btn = document.querySelector('.search-btn');
  const originalText = btn ? btn.innerText : '';
  if (btn && !btn.disabled) btn.innerText = 'Đang truy vấn...';

  try {
    const response = await fetch(`/api/v1/student/query/${studentId}`);
    if (!response.ok) {
      if (response.status === 404) throw new Error('Mã sinh viên không tồn tại hoặc dữ liệu chưa sẵn sàng');
      if (response.status === 403) throw new Error('Bạn chỉ có thể xem dữ liệu của chính mình');
      throw new Error('Không thể truy vấn dữ liệu');
    }

    const data = await response.json();
    displayStudent(data);
  } catch (err) {
    console.error('❌ Lỗi:', err.message);
    if (searchInput && !searchInput.disabled) alert('❌ Lỗi: ' + err.message);
  } finally {
    if (btn && !btn.disabled) btn.innerText = originalText;
  }
}

function displayStudent(data) {
  const panel = document.getElementById('studentDataPanel');
  if (!panel) return;

  panel.classList.remove('hidden');
  panel.style.display = 'block';

  const searchInput = document.getElementById('studentSearchInput');
  const isSelf = searchInput && searchInput.disabled && searchInput.value == data.student.id_student;

  if (searchInput && !searchInput.disabled) {
    panel.scrollIntoView({ behavior: 'smooth' });
  }

  const header = panel.querySelector('h3');
  if (header) {
    header.innerText = isSelf ? 'Kết quả dự đoán của bạn' : `Kết quả dự đoán sinh viên #${data.student.id_student}`;
  }

  const resId = document.getElementById('resStudentId');
  if (resId) resId.innerText = data.student.id_student;

  const riskBadge = document.getElementById('resRiskBadge');
  const riskVal = data.prediction.risk_label || 'UNKNOWN';
  if (riskBadge) {
    riskBadge.innerText = riskVal;
  }

  const confEl = document.getElementById('resConfidence');
  if (confEl) confEl.innerText = (data.prediction.confidence || 0).toFixed(2);

  const recEl = document.getElementById('resRecommendation');
  if (recEl) recEl.innerText = data.prediction.recommendation || '';

  // Dynamic search risk styling updates
  const card = document.getElementById('resRiskCard');
  const glow = document.getElementById('resRiskBadgeGlow');
  const title = document.getElementById('resRiskTitle');
  const bullet = document.getElementById('resRiskBullet');
  const recBox = document.getElementById('resRecommendationBox');

  if (title) {
    title.innerText = riskVal;
  }

  const riskUpper = riskVal.toUpperCase().trim();
  let bg_grad = '', border_color = '', badge_grad = '', risk_title_color = '', shadow_glow = '', stripe_color = '';

  if (riskUpper.includes('LOW')) {
    bg_grad = 'linear-gradient(135deg, rgba(46, 204, 113, 0.05) 0%, rgba(255, 255, 255, 1) 100%)';
    border_color = 'rgba(46, 204, 113, 0.2)';
    badge_grad = 'linear-gradient(135deg, #27ae60 0%, #2ecc71 100%)';
    risk_title_color = '#27ae60';
    shadow_glow = 'rgba(46, 204, 113, 0.12)';
    stripe_color = '#27ae60';
  } else if (riskUpper.includes('MEDIUM')) {
    bg_grad = 'linear-gradient(135deg, rgba(230, 126, 34, 0.05) 0%, rgba(255, 255, 255, 1) 100%)';
    border_color = 'rgba(230, 126, 34, 0.2)';
    badge_grad = 'linear-gradient(135deg, #d35400 0%, #e67e22 100%)';
    risk_title_color = '#d35400';
    shadow_glow = 'rgba(230, 126, 34, 0.12)';
    stripe_color = '#e67e22';
  } else if (riskUpper.includes('HIGH')) {
    bg_grad = 'linear-gradient(135deg, rgba(231, 76, 60, 0.05) 0%, rgba(255, 255, 255, 1) 100%)';
    border_color = 'rgba(231, 76, 60, 0.2)';
    badge_grad = 'linear-gradient(135deg, #c0392b 0%, #e74c3c 100%)';
    risk_title_color = '#c0392b';
    shadow_glow = 'rgba(231, 76, 60, 0.12)';
    stripe_color = '#e74c3c';
  } else {
    bg_grad = 'linear-gradient(135deg, rgba(147, 41, 30, 0.05) 0%, rgba(255, 255, 255, 1) 100%)';
    border_color = 'rgba(147, 41, 30, 0.25)';
    badge_grad = 'linear-gradient(135deg, #78281f 0%, #93291e 100%)';
    risk_title_color = '#78281f';
    shadow_glow = 'rgba(147, 41, 30, 0.15)';
    stripe_color = '#93291e';
  }

  if (card) {
    card.style.background = bg_grad;
    card.style.borderColor = border_color;
    card.style.boxShadow = `0 15px 35px rgba(0,0,0,0.02), 0 10px 30px ${shadow_glow}`;
  }
  if (glow) {
    glow.style.background = badge_grad;
  }
  if (riskBadge) {
    riskBadge.style.background = badge_grad;
    riskBadge.style.boxShadow = `0 8px 25px ${shadow_glow}`;
  }
  if (title) {
    title.style.color = risk_title_color;
  }
  if (bullet) {
    bullet.style.color = risk_title_color;
  }
  if (recBox) {
    recBox.style.borderLeftColor = stripe_color;
  }

  // Detailed Stats Grid - Official (23 features potentially)
  const grid = document.getElementById('resDataTable');
  if (grid) {
    grid.innerHTML = '';
    const s = data.student;
    const features = [
      { label: 'Môn học', val: s.code_module },
      { label: 'Học kỳ', val: s.code_presentation },
      { label: 'Điểm trung bình', val: (s.avg_score || 0).toFixed(2), risky: s.avg_score < 40 },
      { label: 'Tổng số click', val: s.total_clicks || 0, risky: s.total_clicks < 200 },
      { label: 'Số ngày hoạt động', val: s.active_days || 0, risky: s.active_days < 15 },
      { label: 'Số lần học lại', val: s.num_of_prev_attempts || 0, risky: s.num_of_prev_attempts > 0 },
      { label: 'Số tín chỉ', val: s.studied_credits || 0, risky: s.studied_credits > 120 },
      { label: 'Bài nộp muộn', val: s.n_late || 0, risky: s.n_late > 1 },
      { label: 'Click trung bình/ngày', val: (s.avg_clicks_day || 0).toFixed(1), risky: s.avg_clicks_day < 5 },
      { label: 'Điểm thấp nhất', val: (s.min_score || 0).toFixed(1), risky: s.min_score < 30 },
      { label: 'Độ trễ nộp bài', val: (s.avg_submit_delay || 0).toFixed(1) + ' ngày', risky: s.avg_submit_delay > 0 }
    ];

    features.forEach(f => {
      const item = document.createElement('div');
      item.className = 'data-item' + (f.risky ? ' at-risk' : '');
      item.innerHTML = `
        <span class="data-label">${f.label}</span>
        <span class="data-value">${f.val}</span>
        ${f.risky ? '<span class="risk-tag" style="background:var(--primary); color:white; padding:2px 6px; border-radius:4px; font-size:0.6rem; margin-left:10px;">Cảnh báo</span>' : ''}
      `;
      grid.appendChild(item);
    });
  }

  // Feature Analysis
  renderAnalysis(data.student);
}

function closeStudentPanel() {
  const panel = document.getElementById('studentDataPanel');
  if (panel) panel.style.display = 'none';
}

// ── Guest Prediction ──────────────────────────────────────────
async function submitGuestPrediction(event) {
  const form = document.getElementById('guestForm');
  if (!form) return;

  const formData = new FormData(form);
  const data = Object.fromEntries(formData.entries());

  const numericFields = [
    'gender_num', 'age_num', 'education_num', 'imd_band_num', 'disability_num',
    'num_of_prev_attempts', 'studied_credits', 'reg_days_before',
    'n_submitted', 'n_late', 'avg_submit_delay',
    'avg_score', 'min_score', 'total_clicks'
  ];
  numericFields.forEach(field => {
    const val = parseFloat(data[field]);
    data[field] = isNaN(val) ? 0 : val;
  });

  const btn = event.target;
  const originalText = btn.innerHTML;
  btn.innerHTML = "Đang phân tích...";
  btn.disabled = true;

  try {
    const resp = await fetch('/api/v1/student/predict/guest', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });

    const result = await resp.json();
    if (resp.ok) {
      showGuestResult(result, data);
    } else {
      alert("Lỗi: " + (result.detail || "Không thể thực hiện dự báo"));
    }
  } catch (err) {
    alert("Lỗi kết nối server");
  } finally {
    btn.innerHTML = originalText;
    btn.disabled = false;
  }
}

function showGuestResult(result, inputData) {
  const panel = document.getElementById('studentDataPanel');
  if (!panel) return;

  panel.classList.remove('hidden');
  panel.style.display = 'block';

  // If GUEST (Not logged in), save to sessionStorage for persistence after login
  const isGuest = !document.querySelector('a[href="/api/v1/auth/logout"]');
  if (isGuest) {
    const persistData = { ...inputData, ...result };
    sessionStorage.setItem('pending_trial', JSON.stringify(persistData));
  }

  const header = panel.querySelector('h3');
  if (header) {
    header.innerHTML = `
      <div style="display:flex; flex-direction:column; gap:5px;">
        <span>Kết quả dự báo tự do (Guest Trial)</span>
        <span style="font-size:0.85rem; font-weight:500; opacity:0.9;">
          Đây là kết quả dự đoán của bạn. Để lưu kết quả -> 
          <a href="javascript:void(0)" onclick="toggleLoginModal()" style="color:white; text-decoration:underline; font-weight:700;">Đăng nhập ngay</a>
        </span>
      </div>
    `;
  }

  const badge = document.getElementById('resRiskBadge');
  const riskVal = result.risk_label || 'UNKNOWN';
  if (badge) {
    badge.innerText = `${riskVal} RISK`;
  }

  const confEl = document.getElementById('resConfidence');
  if (confEl) confEl.innerHTML = result.confidence.toFixed(1);

  const recEl = document.getElementById('resRecommendation');
  if (recEl) recEl.innerText = result.recommendation || '';

  // Apply premium styling updates to Guest Trial results to match official student dashboard perfectly
  const card = document.getElementById('resRiskCard');
  const glow = document.getElementById('resRiskBadgeGlow');
  const title = document.getElementById('resRiskTitle');
  const bullet = document.getElementById('resRiskBullet');
  const recBox = document.getElementById('resRecommendationBox');

  if (title) {
    title.innerText = riskVal;
  }

  const riskUpper = riskVal.toUpperCase().trim();
  let bg_grad = '', border_color = '', badge_grad = '', risk_title_color = '', shadow_glow = '', stripe_color = '';

  if (riskUpper.includes('LOW')) {
    bg_grad = 'linear-gradient(135deg, rgba(46, 204, 113, 0.05) 0%, rgba(255, 255, 255, 1) 100%)';
    border_color = 'rgba(46, 204, 113, 0.2)';
    badge_grad = 'linear-gradient(135deg, #27ae60 0%, #2ecc71 100%)';
    risk_title_color = '#27ae60';
    shadow_glow = 'rgba(46, 204, 113, 0.12)';
    stripe_color = '#27ae60';
  } else if (riskUpper.includes('MEDIUM')) {
    bg_grad = 'linear-gradient(135deg, rgba(230, 126, 34, 0.05) 0%, rgba(255, 255, 255, 1) 100%)';
    border_color = 'rgba(230, 126, 34, 0.2)';
    badge_grad = 'linear-gradient(135deg, #d35400 0%, #e67e22 100%)';
    risk_title_color = '#d35400';
    shadow_glow = 'rgba(230, 126, 34, 0.12)';
    stripe_color = '#e67e22';
  } else if (riskUpper.includes('HIGH')) {
    bg_grad = 'linear-gradient(135deg, rgba(231, 76, 60, 0.05) 0%, rgba(255, 255, 255, 1) 100%)';
    border_color = 'rgba(231, 76, 60, 0.2)';
    badge_grad = 'linear-gradient(135deg, #c0392b 0%, #e74c3c 100%)';
    risk_title_color = '#c0392b';
    shadow_glow = 'rgba(231, 76, 60, 0.12)';
    stripe_color = '#e74c3c';
  } else {
    bg_grad = 'linear-gradient(135deg, rgba(147, 41, 30, 0.05) 0%, rgba(255, 255, 255, 1) 100%)';
    border_color = 'rgba(147, 41, 30, 0.25)';
    badge_grad = 'linear-gradient(135deg, #78281f 0%, #93291e 100%)';
    risk_title_color = '#78281f';
    shadow_glow = 'rgba(147, 41, 30, 0.15)';
    stripe_color = '#93291e';
  }

  if (card) {
    card.style.background = bg_grad;
    card.style.borderColor = border_color;
    card.style.boxShadow = `0 15px 35px rgba(0,0,0,0.02), 0 10px 30px ${shadow_glow}`;
  }
  if (glow) {
    glow.style.background = badge_grad;
    glow.style.opacity = '0.15';
  }
  if (badge) {
    badge.className = ''; // Reset small badge classes to prevent style breaking
    badge.style.background = badge_grad;
    badge.style.boxShadow = `0 8px 25px ${shadow_glow}`;
    badge.style.color = 'white';
    badge.style.opacity = '1';
    badge.style.filter = 'none';
  }
  if (title) {
    title.style.color = risk_title_color;
    title.innerText = riskVal;
  }
  if (bullet) {
    bullet.style.color = risk_title_color;
  }
  if (recBox) {
    recBox.style.borderLeftColor = stripe_color;
  }

  const grid = document.getElementById('resDataTable');
  if (grid) {
    grid.innerHTML = '';
    const eduLabels = ['Không bằng cấp', 'Dưới A Level', 'A Level/Tương đương', 'HE Qualification', 'Sau đại học'];
    const ageLabels = ['0-35', '35-55', '55+'];

    const clickVal = parseInt(inputData.total_clicks);
    let clickLabel = 'Trung bình';
    if (clickVal <= 150) clickLabel = 'Rất ít';
    else if (clickVal >= 3500) clickLabel = 'Rất tích cực';
    else if (clickVal >= 1500) clickLabel = 'Tích cực';

    const features = [
      { label: 'Giới tính', val: inputData.gender_num === 0 ? 'Nam' : 'Nữ' },
      { label: 'Độ tuổi', val: ageLabels[inputData.age_num] || '—' },
      { label: 'Học vấn', val: eduLabels[inputData.education_num] || '—' },
      { label: 'Kinh tế (IMD)', val: inputData.imd_band_num + '0%', risky: inputData.imd_band_num < 2 },
      { label: 'Khuyết tật', val: inputData.disability_num === 0 ? 'Không' : 'Có' },
      { label: 'Số lần học lại', val: inputData.num_of_prev_attempts, risky: inputData.num_of_prev_attempts > 0 },
      { label: 'Số tín chỉ', val: inputData.studied_credits, risky: inputData.studied_credits > 120 },
      { label: 'Đăng ký trước', val: Math.abs(inputData.reg_days_before) + ' ngày', risky: inputData.reg_days_before > -30 },
      { label: 'Số bài đã nộp', val: inputData.n_submitted, risky: inputData.n_submitted < 3 },
      { label: 'Số bài nộp muộn', val: inputData.n_late, risky: inputData.n_late > 0 },
      { label: 'Độ trễ nộp bài', val: inputData.avg_submit_delay + ' ngày', risky: inputData.avg_submit_delay > 0 },
      { label: 'Điểm trung bình', val: inputData.avg_score.toFixed(2), risky: inputData.avg_score < 40 },
      { label: 'Điểm thấp nhất', val: inputData.min_score.toFixed(2), risky: inputData.min_score < 35 },
      { label: 'Mức độ tương tác', val: clickLabel, risky: clickVal < 200 }
    ];

    features.forEach(f => {
      const item = document.createElement('div');
      item.className = 'data-item' + (f.risky ? ' at-risk' : '');
      item.innerHTML = `
        <span class="data-label">${f.label}</span>
        <span class="data-value">${f.val}</span>
        ${f.risky ? '<span class="risk-tag" style="background:var(--primary); color:white; padding:2px 6px; border-radius:4px; font-size:0.6rem; margin-left:10px;">Cảnh báo</span>' : ''}
      `;
      grid.appendChild(item);
    });
  }

  // Feature Analysis
  renderAnalysis(inputData);
  panel.scrollIntoView({ behavior: 'smooth' });
}

function renderAnalysis(features) {
  const area = document.getElementById('resAnalysisArea');
  const content = document.getElementById('resAnalysisContent');
  if (!area || !content) return;

  area.classList.remove('hidden');
  content.innerHTML = '';

  const analysisItems = [];

  // 1. Core Academic Performance
  if (features.avg_score !== undefined) {
    if (features.avg_score < 40) {
      analysisItems.push({
        title: 'Điểm số báo động (Critical)',
        text: `Điểm trung bình ${features.avg_score.toFixed(1)} đang dưới ngưỡng qua môn (40). Đây là nguyên nhân chính khiến hệ thống xếp bạn vào nhóm rủi ro cao.`,
        type: 'danger'
      });
    } else if (features.avg_score < 55) {
      analysisItems.push({
        title: 'Điểm số trung bình yếu',
        text: `Điểm số ${features.avg_score.toFixed(1)} của bạn đang nằm trong vùng nguy hiểm. Chỉ cần một bài thi kết quả kém có thể kéo rủi ro lên mức rất cao.`,
        type: 'warning'
      });
    } else {
      analysisItems.push({
        title: 'Năng lực học tập ổn định',
        text: `Với mức điểm ${features.avg_score.toFixed(1)}, bạn đang kiểm soát tốt lộ trình môn học.`,
        type: 'success'
      });
    }
  }

  // 2. Engagement Analysis
  if (features.total_clicks !== undefined) {
    if (features.total_clicks < 150) {
      analysisItems.push({
        title: 'Thiếu hụt tương tác nghiêm trọng',
        text: `Với mức tương tác rất thấp, bạn hầu như không truy cập vào tài liệu học tập. AI nhận diện đây là dấu hiệu của việc bỏ bê học tập.`,
        type: 'danger'
      });
    } else if (features.total_clicks < 500) {
      analysisItems.push({
        title: 'Tương tác ở mức tối thiểu',
        text: `Mức tương tác hiện tại chỉ đủ để xem thông tin cơ bản. Bạn cần tham gia nhiều hơn vào các diễn đàn và hoạt động thực hành trên VLE.`,
        type: 'warning'
      });
    }
  }

  // 3. Historical Risk
  if (features.num_of_prev_attempts !== undefined && features.num_of_prev_attempts > 0) {
    analysisItems.push({
      title: 'Yếu tố rủi ro từ lịch sử',
      text: `Việc đã thi lại môn này ${features.num_of_prev_attempts} lần tạo áp lực tâm lý và kiến thức hổng, làm tăng khả năng trượt ở lần này.`,
      type: 'warning'
    });
  }

  // 4. Submission Behavior
  if (features.n_late !== undefined && features.n_late > 0) {
    analysisItems.push({
      title: 'Kỷ luật nộp bài chưa tốt',
      text: `Bạn đã nộp muộn ${features.n_late} bài kiểm tra. AI nhận diện đây là dấu hiệu của việc quản lý thời gian kém, ảnh hưởng trực tiếp đến kết quả cuối cùng.`,
      type: 'danger'
    });
  }

  if (features.avg_submit_delay !== undefined && features.avg_submit_delay > 0) {
    analysisItems.push({
      title: 'Độ trễ nộp bài cao',
      text: `Trung bình bạn nộp bài trễ ${features.avg_submit_delay} ngày so với hạn định. Thói quen này thường dẫn đến việc bị dồn bài và áp lực ở cuối kỳ.`,
      type: 'warning'
    });
  }

  // 5. Registration & Context
  if (features.reg_days_before !== undefined && features.reg_days_before > -30) {
    analysisItems.push({
      title: 'Đăng ký môn học muộn',
      text: 'Việc đăng ký sát ngày khai giảng (dưới 30 ngày) có thể khiến bạn bỏ lỡ các thông báo quan trọng và thiếu thời gian chuẩn bị tâm thế học tập.',
      type: 'warning'
    });
  }

  if (features.disability_num !== undefined && features.disability_num === 1) {
    analysisItems.push({
      title: 'Cần hỗ trợ đặc biệt',
      text: 'Hệ thống nhận diện bạn thuộc nhóm cần hỗ trợ thêm về cơ sở vật chất hoặc tài liệu đặc thù. Hãy chủ động liên hệ với cố vấn học tập.',
      type: 'warning'
    });
  }

  if (analysisItems.length === 0) {
    content.innerHTML = '<p style="color:var(--text-dim)">Dữ liệu của bạn cho thấy các chỉ số đều ở mức bình thường.</p>';
    return;
  }

  analysisItems.forEach(item => {
    const div = document.createElement('div');
    const borderCol = item.type === 'danger' ? 'var(--red)' : (item.type === 'warning' ? 'var(--amber)' : 'var(--green)');
    const bgCol = item.type === 'danger' ? '#fff5f5' : (item.type === 'warning' ? '#fffbf2' : '#f6ffed');

    div.style.padding = '15px 20px';
    div.style.borderRadius = '8px';
    div.style.background = bgCol;
    div.style.borderLeft = `5px solid ${borderCol}`;
    div.style.marginBottom = '5px';
    div.innerHTML = `
      <h5 style="margin:0 0 5px; color:var(--secondary); font-weight:800; font-size:0.9rem; text-transform:uppercase;">${item.title}</h5>
      <p style="margin:0; font-size:0.85rem; color:var(--text); line-height:1.5;">${item.text}</p>
    `;
    content.appendChild(div);
  });
}

// ── Utils ─────────────────────────────────────────────────────
window.addEventListener('scroll', () => {
  const sections = document.querySelectorAll('section[id]');
  const navLinks = document.querySelectorAll('.nav-link');
  let current = '';
  sections.forEach(s => {
    if (window.scrollY >= s.offsetTop - 120) current = s.id;
  });
  navLinks.forEach(l => {
    l.classList.toggle('active', l.getAttribute('href') === '#' + current || l.getAttribute('href') === '/' + current);
  });
}, { passive: true });

document.addEventListener('click', () => {
  const dropdown = document.querySelector('.dropdown-content');
  if (dropdown) dropdown.style.display = 'none';
});

document.addEventListener('keydown', e => {
  if (e.key === 'Escape') closeModal();
});
