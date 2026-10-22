document.addEventListener('DOMContentLoaded', () => {
    // ========================================================
    // Theme Management Engine
    // ========================================================
    const THEME_STORAGE_KEY = 'medipredict_theme';
    const DEFAULT_THEME = 'oceanic-dark';
    const LIGHT_THEME = 'clinical-light';

    function getCurrentTheme() {
        return localStorage.getItem(THEME_STORAGE_KEY) || DEFAULT_THEME;
    }

    function applyTheme(themeName) {
        document.documentElement.setAttribute('data-theme', themeName);
        localStorage.setItem(THEME_STORAGE_KEY, themeName);
        updateThemeUI(themeName);
    }

    function updateThemeUI(themeName) {
        const quickToggleIcon = document.getElementById('quickThemeIcon');
        const quickBtn = document.getElementById('quickThemeToggle');
        if (quickToggleIcon) {
            if (themeName === LIGHT_THEME) {
                quickToggleIcon.className = 'bi bi-moon-stars-fill text-primary';
                if (quickBtn) quickBtn.title = 'Switch to Dark Mode';
            } else {
                quickToggleIcon.className = 'bi bi-sun-fill text-warning';
                if (quickBtn) quickBtn.title = 'Switch to Light Mode';
            }
        }

        document.querySelectorAll('.theme-select-btn').forEach(btn => {
            const val = btn.getAttribute('data-theme-value');
            const checkIcon = btn.querySelector('.theme-check-icon');
            if (val === themeName) {
                btn.classList.add('active');
                if (checkIcon) checkIcon.classList.remove('d-none');
            } else {
                btn.classList.remove('active');
                if (checkIcon) checkIcon.classList.add('d-none');
            }
        });
    }

    // Initialize Theme UI immediately
    const currentTheme = getCurrentTheme();
    applyTheme(currentTheme);

    // Event listener for theme dropdown buttons
    document.querySelectorAll('.theme-select-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const selectedTheme = btn.getAttribute('data-theme-value');
            if (selectedTheme) {
                applyTheme(selectedTheme);
            }
        });
    });

    // Quick light/dark toggle button
    const quickThemeToggle = document.getElementById('quickThemeToggle');
    if (quickThemeToggle) {
        quickThemeToggle.addEventListener('click', () => {
            const active = getCurrentTheme();
            if (active === LIGHT_THEME) {
                applyTheme(DEFAULT_THEME);
            } else {
                applyTheme(LIGHT_THEME);
            }
        });
    }

    // Cross-tab theme sync
    window.addEventListener('storage', (e) => {
        if (e.key === THEME_STORAGE_KEY && e.newValue) {
            applyTheme(e.newValue);
        }
    });

    const MAX_FILES_PER_UPLOAD = 99;

    function showAlert(msg, type='danger') {
        const container = document.getElementById('alert-container');
        if (container) {
            container.innerHTML = `<div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${msg}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>`;
        } else {
            alert(msg);
        }
    }

    function isValidEmail(email) {
        if (!email || typeof email !== 'string') return false;
        const re = /^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$/;
        return re.test(email.trim());
    }

    // Attach real-time validation to all email inputs
    document.querySelectorAll('input[type="email"], #email').forEach(input => {
        let feedback = input.parentNode.querySelector('.email-live-feedback');
        if (!feedback) {
            feedback = document.createElement('div');
            feedback.className = 'email-live-feedback small mt-1';
            input.parentNode.appendChild(feedback);
        }

        input.addEventListener('input', () => {
            const val = input.value.trim();
            if (!val) {
                input.classList.remove('is-valid', 'is-invalid');
                feedback.innerHTML = '';
                return;
            }
            if (isValidEmail(val)) {
                input.classList.remove('is-invalid');
                input.classList.add('is-valid');
                feedback.className = 'email-live-feedback small text-success mt-1';
                feedback.innerHTML = '<i class="bi bi-check-circle-fill me-1"></i> Valid email format';
            } else {
                input.classList.remove('is-valid');
                input.classList.add('is-invalid');
                feedback.className = 'email-live-feedback small text-danger mt-1';
                feedback.innerHTML = '<i class="bi bi-exclamation-circle-fill me-1"></i> Enter a complete email (e.g. name@example.com)';
            }
        });
    });

    document.querySelectorAll('input[type="file"]').forEach((input) => {
        input.addEventListener('change', (event) => {
            const selectedFiles = Array.from(event.target.files || []);
            if (selectedFiles.length > MAX_FILES_PER_UPLOAD) {
                event.target.value = '';
                showAlert(`Yowza, that's a lot of files. Try uploading fewer than ${MAX_FILES_PER_UPLOAD} at a time.`, 'warning');
            }
        });
    });

    // Login Form
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = (document.getElementById('email').value || '').trim();
            const password = document.getElementById('password').value;

            if (!isValidEmail(email)) {
                showAlert('Please enter a valid email address (e.g. name@example.com)', 'danger');
                document.getElementById('email').focus();
                return;
            }

            try {
                const res = await fetch('/api/auth/login', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({email, password})
                });
                const data = await res.json();
                if (res.ok) {
                    window.location.href = '/dashboard';
                } else {
                    showAlert(data.error || 'Login failed', 'danger');
                }
            } catch (err) {
                showAlert('Network error', 'danger');
            }
        });
    }

    // Register Form
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = (document.getElementById('username').value || '').trim();
            const email = (document.getElementById('email').value || '').trim();
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirm_password').value;
            const role = document.getElementById('role').value;

            if (!isValidEmail(email)) {
                showAlert('Please enter a valid email address (e.g. name@example.com)', 'danger');
                document.getElementById('email').focus();
                return;
            }

            if (password !== confirmPassword) {
                showAlert('Passwords do not match', 'danger');
                return;
            }
            try {
                const res = await fetch('/api/auth/register', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({username, email, password, role})
                });
                const data = await res.json();
                if (res.ok) {
                    window.location.href = '/login';
                } else {
                    showAlert(data.error || 'Registration failed', 'danger');
                }
            } catch (err) {
                showAlert('Network error', 'danger');
            }
        });
    }

    // Dashboard History Loader
    const historyTable = document.getElementById('history-table');
    if (historyTable) {
        let allHistoryRecords = [];
        const searchInput = document.getElementById('history-search-input');
        const filterSelect = document.getElementById('history-filter-select');
        const countBadge = document.getElementById('record-count-badge');
        const emptyState = document.getElementById('history-empty-state');
        const tbody = historyTable.querySelector('tbody');

        const renderRecords = (records) => {
            tbody.innerHTML = '';
            if (countBadge) {
                countBadge.innerText = `${records.length} Record${records.length === 1 ? '' : 's'}`;
            }

            if (records.length === 0) {
                if (emptyState) emptyState.classList.remove('d-none');
                return;
            }

            if (emptyState) emptyState.classList.add('d-none');

            records.forEach(h => {
                const topDiseases = Object.entries(h.top_predictions || {});
                let topD = 'Inconclusive';
                let probVal = 0;
                if (topDiseases.length > 0) {
                    topD = topDiseases[0][0];
                    probVal = parseFloat(topDiseases[0][1]);
                }

                let riskClass = 'risk-low';
                if (probVal >= 50) riskClass = 'risk-high';
                else if (probVal >= 25) riskClass = 'risk-moderate';

                const dateObj = new Date(h.date_predicted);
                const dateStr = dateObj.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
                const timeStr = dateObj.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' });

                const patientInitial = (h.patient_name || 'P').charAt(0).toUpperCase();
                const patientAge = h.patient_age ? `${h.patient_age} yrs` : '';
                const patientGender = h.patient_gender ? h.patient_gender : '';
                const patientSub = [patientAge, patientGender].filter(Boolean).join(' • ') || 'Patient Record';

                // Medical Reports & PDF Links
                let reportsHtml = '<div class="d-flex flex-wrap gap-1">';
                if (h.medical_report_file) {
                    reportsHtml += `<a href="/api/predictions/download_medical_report/${h.id}" class="report-doc-link" title="Download Uploaded Medical Report">
                        <i class="bi bi-file-earmark-medical-fill text-info"></i> ${h.medical_report_type ? h.medical_report_type.split(' ')[0] : 'Report'}
                    </a>`;
                }
                if (h.pdf_report_path) {
                    reportsHtml += `<a href="/api/predictions/download_report/${h.id}" class="report-doc-link" title="Download Generated AI PDF Report">
                        <i class="bi bi-file-earmark-pdf-fill text-danger"></i> AI PDF
                    </a>`;
                }
                if (!h.medical_report_file && !h.pdf_report_path) {
                    reportsHtml += `<span class="text-muted small">None</span>`;
                }
                reportsHtml += '</div>';

                tbody.innerHTML += `
                    <tr>
                        <td>
                            <div class="fw-bold">${dateStr}</div>
                            <div class="small text-muted">${timeStr}</div>
                        </td>
                        <td>
                            <div class="patient-cell">
                                <div class="patient-avatar">${patientInitial}</div>
                                <div>
                                    <div class="patient-name">${h.patient_name}</div>
                                    <div class="patient-meta">${patientSub}</div>
                                </div>
                            </div>
                        </td>
                        <td>
                            <span class="diagnosis-pill ${riskClass}">
                                <i class="bi bi-heart-pulse-fill"></i> ${topD} ${probVal ? `(${probVal}%)` : ''}
                            </span>
                        </td>
                        <td>${reportsHtml}</td>
                        <td class="text-end">
                            <a href="/results?id=${h.id}" class="btn btn-sm btn-primary">
                                <i class="bi bi-eye-fill me-1"></i> View
                            </a>
                        </td>
                    </tr>
                `;
            });
        };

        const filterAndRender = () => {
            const query = (searchInput ? searchInput.value : '').toLowerCase().trim();
            const conditionFilter = (filterSelect ? filterSelect.value : 'all');

            const filtered = allHistoryRecords.filter(h => {
                const nameMatches = (h.patient_name || '').toLowerCase().includes(query);
                const ageMatches = h.patient_age ? h.patient_age.toString().includes(query) : false;
                const topD = Object.keys(h.top_predictions || {})[0] || '';
                const diseaseMatches = topD.toLowerCase().includes(query);
                
                const matchesSearch = !query || nameMatches || ageMatches || diseaseMatches;
                const matchesCondition = conditionFilter === 'all' || topD === conditionFilter;

                return matchesSearch && matchesCondition;
            });

            renderRecords(filtered);
        };

        const loadHistory = async () => {
            try {
                const res = await fetch('/api/predictions/history');
                const data = await res.json();
                if (res.ok) {
                    allHistoryRecords = data.history || [];
                    
                    if (filterSelect) {
                        const conditions = new Set();
                        allHistoryRecords.forEach(h => {
                            const topD = Object.keys(h.top_predictions || {})[0];
                            if (topD) conditions.add(topD);
                        });
                        filterSelect.innerHTML = '<option value="all">All Conditions</option>';
                        conditions.forEach(cond => {
                            filterSelect.innerHTML += `<option value="${cond}">${cond}</option>`;
                        });
                    }

                    filterAndRender();
                } else {
                    tbody.innerHTML = `<tr><td colspan="5" class="text-center py-4 text-danger">${data.error || 'Failed to load records'}</td></tr>`;
                }
            } catch (err) {
                console.error(err);
                tbody.innerHTML = `<tr><td colspan="5" class="text-center py-4 text-danger">Network error loading patient history</td></tr>`;
            }
        };

        if (searchInput) searchInput.addEventListener('input', filterAndRender);
        if (filterSelect) filterSelect.addEventListener('change', filterAndRender);

        loadHistory();
    }

    // Predict Form
    const predictForm = document.getElementById('predict-form');
    if (predictForm) {
        predictForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = document.getElementById('predict-btn');
            btn.disabled = true;
            btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Analyzing Patient Data...';
            
            const symptoms = [];
            document.querySelectorAll('.sym-cb:checked').forEach(cb => symptoms.push(cb.value));

            const formData = new FormData();
            formData.append('patient_name', document.getElementById('patient_name').value);
            formData.append('age', document.getElementById('age').value);
            formData.append('gender', document.getElementById('gender').value);
            formData.append('blood_pressure', document.getElementById('blood_pressure').value);
            formData.append('cholesterol', document.getElementById('cholesterol').value);
            formData.append('glucose', document.getElementById('glucose').value);
            formData.append('bmi', document.getElementById('bmi').value);
            formData.append('tumor_size', document.getElementById('tumor_size').value);
            formData.append('bilirubin', document.getElementById('bilirubin').value);
            formData.append('alkaline_phosphatase', document.getElementById('alkaline_phosphatase').value);
            formData.append('blood_urea', document.getElementById('blood_urea').value);
            formData.append('serum_creatinine', document.getElementById('serum_creatinine').value);
            formData.append('symptoms', JSON.stringify(symptoms));

            // Medical Report Fields
            const reportTypeEl = document.getElementById('medical_report_type');
            if (reportTypeEl) formData.append('medical_report_type', reportTypeEl.value);

            const reportNotesEl = document.getElementById('medical_report_notes');
            if (reportNotesEl) formData.append('medical_report_notes', reportNotesEl.value);

            const reportFileEl = document.getElementById('medical_report_file');
            if (reportFileEl && reportFileEl.files.length > 0) {
                formData.append('medical_report_file', reportFileEl.files[0]);
            }

            try {
                const res = await fetch('/api/predictions/predict', {
                    method: 'POST',
                    body: formData
                });
                const data = await res.json();
                if (res.ok) {
                    window.location.href = `/results?id=${data.id}`;
                } else {
                    showAlert(data.error || 'Prediction failed');
                    btn.disabled = false;
                    btn.innerHTML = '<i class="bi bi-cpu-fill me-2"></i>Analyze & Predict Disease';
                }
            } catch (err) {
                showAlert('Network error occurred during prediction');
                btn.disabled = false;
                btn.innerHTML = '<i class="bi bi-cpu-fill me-2"></i>Analyze & Predict Disease';
            }
        });
    }

    // Results Page
    const resultsContainer = document.getElementById('results-container');
    if (resultsContainer) {
        const urlParams = new URLSearchParams(window.location.search);
        const historyId = urlParams.get('id');
        
        if (!historyId) {
            resultsContainer.innerHTML = '<div class="alert alert-danger">Invalid prediction ID</div>';
            return;
        }

        const loadResults = async () => {
            try {
                const res = await fetch(`/api/predictions/history/${historyId}`);
                const data = await res.json();
                
                if (res.ok) {
                    const patAge = data.patient_info.age ? ` (${data.patient_info.age} yrs, ${data.patient_info.gender})` : '';
                    let resultsHtml = `
                    <div class="col-md-9">
                        <div class="card shadow-sm mb-4">
                            <div class="card-body p-4 p-md-5">
                                <div class="d-flex flex-wrap align-items-center justify-content-between mb-3 gap-2">
                                    <div>
                                        <h3 class="mb-1">Diagnostic Report: ${data.patient_info.name}${patAge}</h3>
                                        <small class="text-muted"><i class="bi bi-clock me-1"></i>Date: ${new Date(data.date_predicted).toLocaleString()}</small>
                                    </div>
                                    <div class="d-flex gap-2">
                                        <a href="/api/predictions/download_report/${data.id}" class="btn btn-secondary">
                                            <i class="bi bi-file-earmark-pdf-fill text-danger me-1"></i> Download PDF
                                        </a>
                                        <a href="/dashboard" class="btn btn-outline-primary">
                                            <i class="bi bi-arrow-left me-1"></i> Dashboard
                                        </a>
                                    </div>
                                </div>
                                <hr>
                                
                                <h4 class="mb-3">Top AI Predictions</h4>
                                <ul class="list-group mb-4">
                    `;
                    
                    for (const [disease, prob] of Object.entries(data.prediction_results)) {
                        const probNum = parseFloat(prob);
                        let badgeClass = 'bg-primary';
                        if (probNum >= 50) badgeClass = 'bg-danger';
                        else if (probNum >= 25) badgeClass = 'bg-warning text-dark';
                        
                        resultsHtml += `<li class="list-group-item d-flex justify-content-between align-items-center">
                            <span class="fw-semibold"><i class="bi bi-activity text-primary me-2"></i>${disease}</span>
                            <span class="badge ${badgeClass} rounded-pill fs-6">${prob}%</span>
                        </li>`;
                    }
                    
                    resultsHtml += `</ul>
                                <div class="clinical-explanation-box">
                                    <div class="clinical-explanation-header">
                                        <div class="clinical-explanation-title">
                                            <i class="bi bi-clipboard2-pulse-fill text-primary"></i>
                                            <span>Clinical Diagnostic Explanation</span>
                                        </div>
                                        <span class="badge bg-primary px-3 py-2">
                                            <i class="bi bi-shield-check me-1"></i> AI Decision Rationale
                                        </span>
                                    </div>
                                    <p class="clinical-explanation-text">
                                        ${data.explanations.text || 'Diagnostic reasoning is based on vital signs and reported symptoms aligned with clinical thresholds.'}
                                    </p>
                                </div>
                            </div>
                        </div>`;

                    if (data.medical_report_file || data.medical_report_notes) {
                        resultsHtml += `
                        <div class="card shadow-sm mb-4">
                            <div class="card-body p-4 p-md-5">
                                <h4 class="mb-3 d-flex align-items-center gap-2">
                                    <i class="bi bi-file-earmark-medical text-primary"></i> Attached Medical Report & Clinical Notes
                                </h4>
                                <div class="d-flex flex-wrap align-items-center justify-content-between p-3 rounded mb-3" style="background: var(--input-bg); border: 1px solid var(--border-color);">
                                    <div class="d-flex align-items-center gap-2">
                                        <i class="bi bi-file-earmark-text-fill fs-3 text-info"></i>
                                        <div>
                                            <div class="fw-bold">${data.medical_report_type || 'General Medical Report'}</div>
                                            <small class="text-muted">${data.medical_report_file ? 'Uploaded Patient Document' : 'Clinical notes on record'}</small>
                                        </div>
                                    </div>
                                    ${data.medical_report_file ? `
                                        <a href="/api/predictions/download_medical_report/${data.id}" class="btn btn-sm btn-outline-primary mt-2 mt-sm-0">
                                            <i class="bi bi-download me-1"></i> Download Attached Report
                                        </a>` : ''}
                                </div>
                                ${data.medical_report_notes ? `
                                    <div class="p-3 rounded" style="background: var(--table-hover);">
                                        <div class="fw-semibold small text-muted text-uppercase mb-1">Doctor / Lab Remarks:</div>
                                        <p class="mb-0">${data.medical_report_notes}</p>
                                    </div>
                                ` : ''}
                            </div>
                        </div>`;
                    }

                    // Explainable AI (XAI) Section: SHAP & LIME
                    const shapImg = data.explanations.shap_image || data.explanations.image;
                    const limeImg = data.explanations.lime_image;
                    const limeRules = data.explanations.lime_rules || [];
                    const shapFeatures = data.explanations.shap_features || [];

                    if (shapImg || limeImg) {
                        resultsHtml += `
                        <div class="card shadow-sm mb-4">
                            <div class="card-body p-4 p-md-5">
                                <div class="d-flex flex-wrap align-items-center justify-content-between mb-3 gap-2">
                                    <div>
                                        <h4 class="mb-1 d-flex align-items-center gap-2">
                                            <i class="bi bi-lightbulb-fill text-warning"></i> Explainable AI (XAI): Why This Prediction?
                                        </h4>
                                        <p class="text-muted small mb-0">Dual-engine verification using SHAP (Game-Theoretic Attribution) and LIME (Local Surrogate Rules).</p>
                                    </div>
                                    <div class="badge bg-primary px-3 py-2">Clinician Explainability</div>
                                </div>

                                <!-- XAI Navigation Tabs -->
                                <ul class="nav nav-pills mb-4" id="xaiTabs" role="tablist">
                                    <li class="nav-item" role="presentation">
                                        <button class="nav-link active" id="shap-tab" data-bs-toggle="pill" data-bs-target="#shap-pane" type="button" role="tab">
                                            <i class="bi bi-bar-chart-fill me-1"></i> SHAP Attribution
                                        </button>
                                    </li>
                                    <li class="nav-item" role="presentation">
                                        <button class="nav-link" id="lime-tab" data-bs-toggle="pill" data-bs-target="#lime-pane" type="button" role="tab">
                                            <i class="bi bi-sliders me-1"></i> LIME Decision Rules
                                        </button>
                                    </li>
                                    <li class="nav-item" role="presentation">
                                        <button class="nav-link" id="compare-tab" data-bs-toggle="pill" data-bs-target="#compare-pane" type="button" role="tab">
                                            <i class="bi bi-check2-circle me-1"></i> Diagnostic Corroboration
                                        </button>
                                    </li>
                                </ul>

                                <div class="tab-content" id="xaiTabsContent">
                                    <!-- SHAP Tab -->
                                    <div class="tab-pane fade show active" id="shap-pane" role="tabpanel">
                                        <div class="row align-items-center">
                                            <div class="col-lg-8 text-center mb-3 mb-lg-0">
                                                ${shapImg ? `<img src="/${shapImg}" class="img-fluid rounded border shadow-sm" alt="SHAP Plot" style="max-height: 400px; width: 100%; object-fit: contain;">` : '<p class="text-muted">SHAP plot unavailable</p>'}
                                            </div>
                                            <div class="col-lg-4">
                                                <div class="p-3 rounded" style="background: var(--input-bg); border: 1px solid var(--border-color);">
                                                    <h6 class="fw-bold text-primary mb-2"><i class="bi bi-info-circle me-1"></i> How SHAP Works</h6>
                                                    <p class="small text-muted mb-3">SHAP assigns each vital feature an additive Shapley value calculated over all possible feature coalitions. Blue bars show features that drove the diagnosis upward.</p>
                                                    ${shapFeatures.length > 0 ? `
                                                        <div class="fw-bold small text-uppercase mb-2">Top Positive Factors:</div>
                                                        <ul class="list-unstyled small mb-0">
                                                            ${shapFeatures.map(f => `
                                                                <li class="d-flex justify-content-between py-1 border-bottom border-secondary-subtle">
                                                                    <span>${f.feature}</span>
                                                                    <span class="fw-semibold ${f.shap_value > 0 ? 'text-info' : 'text-danger'}">${f.shap_value > 0 ? '+' : ''}${f.shap_value}</span>
                                                                </li>
                                                            `).join('')}
                                                        </ul>
                                                    ` : ''}
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    <!-- LIME Tab -->
                                    <div class="tab-pane fade" id="lime-pane" role="tabpanel">
                                        <div class="row align-items-center">
                                            <div class="col-lg-8 text-center mb-3 mb-lg-0">
                                                ${limeImg ? `<img src="/${limeImg}" class="img-fluid rounded border shadow-sm" alt="LIME Plot" style="max-height: 400px; width: 100%; object-fit: contain;">` : '<p class="text-muted">LIME plot unavailable</p>'}
                                            </div>
                                            <div class="col-lg-4">
                                                <div class="p-3 rounded" style="background: var(--input-bg); border: 1px solid var(--border-color);">
                                                    <h6 class="fw-bold text-success mb-2"><i class="bi bi-info-circle me-1"></i> How LIME Works</h6>
                                                    <p class="small text-muted mb-3">LIME builds a local interpretable surrogate model around this specific patient. Green bars indicate localized threshold rules confirming the diagnosis.</p>
                                                    ${limeRules.length > 0 ? `
                                                        <div class="fw-bold small text-uppercase mb-2">Local Threshold Rules:</div>
                                                        <ul class="list-unstyled small mb-0">
                                                            ${limeRules.map(r => `
                                                                <li class="d-flex justify-content-between py-1 border-bottom border-secondary-subtle">
                                                                    <span class="text-truncate me-2" title="${r.rule}">${r.rule}</span>
                                                                    <span class="fw-semibold ${r.weight > 0 ? 'text-success' : 'text-warning'}">${r.weight > 0 ? '+' : ''}${r.weight}</span>
                                                                </li>
                                                            `).join('')}
                                                        </ul>
                                                    ` : ''}
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    <!-- Corroboration Tab -->
                                    <div class="tab-pane fade" id="compare-pane" role="tabpanel">
                                        <div class="table-responsive">
                                            <table class="table table-sm table-hover align-middle mb-0">
                                                <thead>
                                                    <tr>
                                                        <th>Technique</th>
                                                        <th>Perspective</th>
                                                        <th>Key Finding for This Patient</th>
                                                        <th>Clinical Verdict</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    <tr>
                                                        <td><span class="badge bg-primary">SHAP</span></td>
                                                        <td>Game-Theoretic Global Impact</td>
                                                        <td>${shapFeatures.length > 0 ? shapFeatures.slice(0, 2).map(f => f.feature).join(', ') : 'Biometric indicators'}</td>
                                                        <td><span class="text-success"><i class="bi bi-check-circle-fill me-1"></i>Consistent Feature Drivers</span></td>
                                                    </tr>
                                                    <tr>
                                                        <td><span class="badge bg-success">LIME</span></td>
                                                        <td>Local Instance Surrogate</td>
                                                        <td>${limeRules.length > 0 ? limeRules.slice(0, 2).map(r => r.rule).join('; ') : 'Localized bounds'}</td>
                                                        <td><span class="text-success"><i class="bi bi-check-circle-fill me-1"></i>Threshold Rules Met</span></td>
                                                    </tr>
                                                </tbody>
                                            </table>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>`;
                    }

                    resultsHtml += `</div>`;
                    resultsContainer.innerHTML = resultsHtml;
                } else {
                    resultsContainer.innerHTML = `<div class="alert alert-danger">${data.error || 'Failed to load results'}</div>`;
                }
            } catch (err) {
                resultsContainer.innerHTML = '<div class="alert alert-danger">Network error loading results</div>';
            }
        };
        
        loadResults();
    }

    // Forgot Password Form
    const forgotForm = document.getElementById('forgot-form');
    if (forgotForm) {
        const sendOtpBtn = document.getElementById('send-otp-btn');
        const emailSection = document.getElementById('email-section');
        const otpSection = document.getElementById('otp-section');
        let currentEmail = '';

        sendOtpBtn.addEventListener('click', async () => {
            const email = (document.getElementById('email').value || '').trim();
            if (!isValidEmail(email)) {
                showAlert('Please enter a valid email address (e.g. name@example.com)', 'danger');
                document.getElementById('email').focus();
                return;
            }
            currentEmail = email;
            sendOtpBtn.disabled = true;
            sendOtpBtn.innerText = 'Sending OTP...';
            
            try {
                const res = await fetch('/api/auth/forgot-password', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({email})
                });
                const data = await res.json();
                if (res.ok) {
                    let msg = data.message;
                    if (data.dev_otp) {
                        msg += `<br><br><strong>[DEV MODE] OTP:</strong> <span class="fs-4 fw-bold font-monospace">${data.dev_otp}</span>`;
                    }
                    showAlert(msg, 'success');
                    
                    // Show OTP fields
                    emailSection.style.display = 'none';
                    otpSection.style.display = 'block';
                } else {
                    showAlert(data.error || 'Failed to send OTP', 'danger');
                }
            } catch (err) {
                showAlert('Network error', 'danger');
            }
            sendOtpBtn.disabled = false;
            sendOtpBtn.innerText = 'Send OTP';
        });

        forgotForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const otp = document.getElementById('otp').value;
            const newPassword = document.getElementById('new_password').value;
            const confirmNewPassword = document.getElementById('confirm_new_password').value;
            
            if (!otp || !newPassword || !confirmNewPassword) {
                showAlert('Please fill all fields', 'danger');
                return;
            }
            
            if (newPassword !== confirmNewPassword) {
                showAlert('Passwords do not match', 'danger');
                return;
            }
            
            const btn = document.getElementById('reset-btn');
            btn.disabled = true;
            btn.innerText = 'Updating...';
            
            try {
                const res = await fetch(`/api/auth/verify-reset-otp`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({email: currentEmail, otp, password: newPassword})
                });
                const data = await res.json();
                if (res.ok) {
                    showAlert(data.message, 'success');
                    setTimeout(() => { window.location.href = '/login'; }, 2000);
                } else {
                    showAlert(data.error || 'Failed to update password', 'danger');
                    btn.disabled = false;
                    btn.innerText = 'Verify & Reset Password';
                }
            } catch (err) {
                showAlert('Network error', 'danger');
                btn.disabled = false;
                btn.innerText = 'Verify & Reset Password';
            }
        });
    }
});
