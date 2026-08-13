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
      'account_locked': { title: 'Tài khoản bị khóa', text: 'Tài khoản của bạn đã bị vô hiệu hóa. Vui lòng liên hệ quản trị viên.', type: 'error' },
      'reg_failed': { title: 'Đăng ký thất bại', text: 'Tên đăng nhập hoặc email đã tồn tại.', type: 'error' }
    };
    const toastData = errMap[err] || { title: 'Lỗi', text: err, type: 'error' };
    showToast(toastData.title, toastData.text, toastData.type);
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
    if (searchInput && !searchInput.disabled) showToast('Lỗi truy vấn', err.message, 'error');
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
    div.style.borderRadius = 'var(--radius-sm)';
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

document.addEventListener('click', () => {
  const dropdown = document.querySelector('.dropdown-content');
  if (dropdown) dropdown.style.display = 'none';
});

document.addEventListener('keydown', e => {
  if (e.key === 'Escape') {
    closeModal();
    const logoutModal = document.getElementById('custom-logout-modal');
    if (logoutModal) logoutModal.remove();
  }
});

// Custom Premium Logout Confirmation Modal
function confirmLogout(event) {
  event.preventDefault();
  
  // Create overlay
  const overlay = document.createElement('div');
  overlay.id = 'custom-logout-modal';
  overlay.style.position = 'fixed';
  overlay.style.inset = '0';
  overlay.style.backgroundColor = 'rgba(0, 0, 0, 0.6)';
  overlay.style.zIndex = '9999';
  overlay.style.display = 'flex';
  overlay.style.alignItems = 'center';
  overlay.style.justifyContent = 'center';
  overlay.style.padding = '20px';
  overlay.style.backdropFilter = 'blur(4px)';
  overlay.style.animation = 'fadeIn 0.2s ease-out';

  // Modal Card
  const card = document.createElement('div');
  card.style.background = 'white';
  card.style.padding = '28px';
  card.style.borderRadius = '8px';
  card.style.maxWidth = '400px';
  card.style.width = '100%';
  card.style.boxShadow = '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)';
  card.style.border = '1px solid #f1f5f9';
  card.style.textAlign = 'center';
  card.style.animation = 'scaleIn 0.2s cubic-bezier(0.34, 1.56, 0.64, 1)';

  card.innerHTML = `
    <div style="width: 56px; height: 56px; background: #fff1f2; color: #e11d48; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 20px; font-size: 1.5rem;">
      🚪
    </div>
    <h3 style="margin: 0 0 10px; color: #0f172a; font-size: 1.25rem; font-weight: 700; font-family: 'Inter', sans-serif;">Xác nhận đăng xuất</h3>
    <p style="margin: 0 0 24px; color: #64748b; font-size: 0.95rem; line-height: 1.5; font-family: 'Inter', sans-serif;">Bạn có chắc chắn muốn đăng xuất khỏi hệ thống RiskSight?</p>
    <div style="display: flex; gap: 12px;">
      <button id="logout-cancel-btn" style="flex: 1; padding: 10px 16px; background: #f1f5f9; color: #475569; border: none; border-radius: 6px; font-weight: 600; font-size: 0.95rem; cursor: pointer; transition: all 0.2s; font-family: 'Inter', sans-serif;">Hủy</button>
      <a href="/api/v1/auth/logout" style="flex: 1; padding: 10px 16px; background: #c8102e; color: white; border: none; border-radius: 6px; font-weight: 600; font-size: 0.95rem; cursor: pointer; text-decoration: none; text-align: center; display: block; transition: all 0.2s; font-family: 'Inter', sans-serif;" onmouseover="this.style.opacity='0.9'" onmouseout="this.style.opacity='1'">Đăng xuất</a>
    </div>
  `;

  overlay.appendChild(card);
  document.body.appendChild(overlay);

  // Add keyframe animations dynamically if they don't exist
  if (!document.getElementById('custom-modal-styles')) {
    const style = document.createElement('style');
    style.id = 'custom-modal-styles';
    style.innerHTML = `
      @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
      }
      @keyframes scaleIn {
        from { transform: scale(0.95); opacity: 0; }
        to { transform: scale(1); opacity: 1; }
      }
    `;
    document.head.appendChild(style);
  }

  // Cancel action
  card.querySelector('#logout-cancel-btn').addEventListener('click', () => {
    overlay.remove();
  });

  // Click outside to close
  overlay.addEventListener('click', (e) => {
    if (e.target === overlay) {
      overlay.remove();
    }
  });
}
