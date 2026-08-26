/**
 * GATE IN & RA Master Preparation Studio — Client-Side Application Engine
 * Pure HTML5 / Vanilla JavaScript for GitHub Pages
 */

// ============================================================================
// State Management & LocalStorage
// ============================================================================
const AppState = {
  currentView: "step1", // step1, step2, step3, step4, syllabus, progress
  activeTopicId: "M01",
  startDate: null,
  activeSecondsToday: 0,
  completedTopics: new Set(),
  mistakesQueue: [], // Array of { id, date, topicId, topicName, code, question, takeaway, mastered }
  calcDisplay: "0",
  calcRadMode: true,
  calcMemory: 0,

  init() {
    // Load start date (defaults to today - 10 days for illustration or today)
    const savedStart = localStorage.getItem("gate_start_date");
    if (savedStart) {
      this.startDate = new Date(savedStart);
    } else {
      this.startDate = new Date();
      localStorage.setItem("gate_start_date", this.startDate.toISOString().split("T")[0]);
    }

    // Load active topic
    const savedTopic = localStorage.getItem("gate_active_topic");
    if (savedTopic && SYLLABUS_DATA.find(t => t.id === savedTopic)) {
      this.activeTopicId = savedTopic;
    }

    // Load completed topics
    const savedComp = localStorage.getItem("gate_completed_topics");
    if (savedComp) {
      try {
        this.completedTopics = new Set(JSON.parse(savedComp));
      } catch (e) {
        this.completedTopics = new Set();
      }
    }

    // Load mistakes queue
    const savedMistakes = localStorage.getItem("gate_mistakes_queue");
    if (savedMistakes) {
      try {
        this.mistakesQueue = JSON.parse(savedMistakes);
      } catch (e) {
        this.mistakesQueue = [];
      }
    }

    // Load today's active study seconds
    const todayKey = "gate_active_sec_" + this.getTodayStr();
    const savedSec = localStorage.getItem(todayKey);
    this.activeSecondsToday = savedSec ? parseInt(savedSec, 10) : 0;

    // Start Foreground Timer
    this.initForegroundTimer();

    // Render initial view
    this.renderHeader();
    this.switchView("step1");
  },

  getTodayStr() {
    return new Date().toISOString().split("T")[0];
  },

  save() {
    localStorage.setItem("gate_active_topic", this.activeTopicId);
    localStorage.setItem("gate_completed_topics", JSON.stringify([...this.completedTopics]));
    localStorage.setItem("gate_mistakes_queue", JSON.stringify(this.mistakesQueue));
    const todayKey = "gate_active_sec_" + this.getTodayStr();
    localStorage.setItem(todayKey, this.activeSecondsToday.toString());
  },

  // ==========================================================================
  // Foreground Study Clock (Page Visibility API)
  // ==========================================================================
  initForegroundTimer() {
    setInterval(() => {
      // Strictly track time ONLY when the tab is actively focused in foreground
      if (!document.hidden) {
        this.activeSecondsToday++;
        this.updateTimerDisplay();
        if (this.activeSecondsToday % 10 === 0) {
          const todayKey = "gate_active_sec_" + this.getTodayStr();
          localStorage.setItem(todayKey, this.activeSecondsToday.toString());
        }
      }
    }, 1000);

    document.addEventListener("visibilitychange", () => {
      this.updateTimerDisplay();
    });
  },

  updateTimerDisplay() {
    const el = document.getElementById("activeTimerDisplay");
    if (!el) return;
    const hrs = Math.floor(this.activeSecondsToday / 3600);
    const mins = Math.floor((this.activeSecondsToday % 3600) / 60);
    const secs = this.activeSecondsToday % 60;
    const formatted = `${String(hrs).padStart(2, '0')}h ${String(mins).padStart(2, '0')}m ${String(secs).padStart(2, '0')}s`;
    
    if (document.hidden) {
      el.innerHTML = `⏸️ Active Today: ${formatted} (Paused)`;
      el.style.color = "var(--text-muted)";
    } else {
      el.innerHTML = `⏱️ Active Today: ${formatted}`;
      el.style.color = "var(--accent-green)";
    }
  },

  // ==========================================================================
  // Header & Exam Countdown
  // ==========================================================================
  renderHeader() {
    const now = new Date();
    const diffMs = now - this.startDate;
    const daysElapsed = Math.max(1, Math.floor(diffMs / (1000 * 60 * 60 * 24)) + 1);
    const daysRemaining = Math.max(0, TOTAL_DAYS - daysElapsed);

    const dayEl = document.getElementById("headerDayElapsed");
    const remEl = document.getElementById("headerDaysRemaining");
    if (dayEl) dayEl.textContent = daysElapsed;
    if (remEl) remEl.textContent = daysRemaining;

    // Pacing Status
    const expectedTopics = Math.min(57, Math.round((daysElapsed / TOTAL_DAYS) * 57));
    const completedCount = this.completedTopics.size;
    const pacingEl = document.getElementById("headerPacingStatus");
    if (pacingEl) {
      if (completedCount >= expectedTopics - 1) {
        pacingEl.textContent = "🟢 On Track";
        pacingEl.className = "status-badge status-on-track";
      } else {
        pacingEl.textContent = "🟡 Catch-up Needed";
        pacingEl.className = "status-badge status-lagging";
      }
    }
  },

  // ==========================================================================
  // Navigation & View Switching (1 Step At A Time)
  // ==========================================================================
  switchView(viewName) {
    this.currentView = viewName;
    
    // Update sidebar active classes
    document.querySelectorAll(".nav-item").forEach(item => {
      if (item.getAttribute("data-view") === viewName) {
        item.classList.add("active");
      } else {
        item.classList.remove("active");
      }
    });

    // Hide all view sections
    document.querySelectorAll(".view-section").forEach(sec => {
      sec.classList.remove("active");
    });

    // Show active section
    const activeSec = document.getElementById(`view-${viewName}`);
    if (activeSec) {
      activeSec.classList.add("active");
    }

    // Render content for active view
    if (viewName === "step1") this.renderStep1();
    else if (viewName === "step2") this.renderStep2();
    else if (viewName === "step3") this.renderStep3();
    else if (viewName === "step4") this.renderStep4();
    else if (viewName === "syllabus") this.renderSyllabusTree();
    else if (viewName === "progress") this.renderProgressDiary();

    // Trigger KaTeX render
    if (window.renderMathInElement) {
      renderMathInElement(document.body, {
        delimiters: [
          { left: "$$", right: "$$", display: true },
          { left: "$", right: "$", display: false }
        ]
      });
    }
  },

  // ==========================================================================
  // STEP 1: 5-Minute Morning Recall
  // ==========================================================================
  renderStep1() {
    const container = document.getElementById("step1Content");
    if (!container) return;

    const topic = SYLLABUS_DATA.find(t => t.id === this.activeTopicId) || SYLLABUS_DATA[0];

    container.innerHTML = `
      <div class="study-card">
        <div class="step-header">
          <div>
            <div class="step-title">🌅 Step 1: 5-Minute Morning Warm-Up & Recall</div>
            <div class="step-subtitle">Prime your cognitive retention with yesterday's formulas and a 3-question active recall check.</div>
          </div>
          <div style="background:#0B1329; border:1px solid #1E3A8A; color:#38BDF8; font-family:monospace; padding:6px 14px; border-radius:6px;">
            ⏱️ Target: 5 Mins
          </div>
        </div>

        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:16px; margin-bottom:20px;">
          <div style="background:#0F172A; padding:16px; border-radius:8px; border:1px solid var(--border-color);">
            <h4 style="color:var(--accent-blue); margin-bottom:8px;">📚 Active Focus Module</h4>
            <div style="font-weight:700; font-size:1.1rem;">[${topic.id}] ${topic.topic_name}</div>
            <div style="color:var(--text-secondary); font-size:0.85rem; margin-top:4px;">Domain: ${topic.domain} | Module: ${topic.module_name}</div>
            <div class="formula-box">
              $$\\displaystyle ${topic.key_formula_latex}$$
            </div>
          </div>

          <div style="background:#0F172A; padding:16px; border-radius:8px; border:1px solid var(--border-color);">
            <h4 style="color:var(--accent-amber); margin-bottom:8px;">🧠 3-Question Active Recall Blitz</h4>
            <div style="font-size:0.9rem; margin-bottom:12px;">
              <b>Q1:</b> Full Wheatstone Bridge Output = $V_s \\cdot GF \\cdot \\epsilon$<br>
              <b>Q2:</b> Link Twist angle $\\alpha_i$ is measured around $x_i$ axis.<br>
              <b>Q3:</b> 2nd Order Peak Overshoot $M_p = e^{-\\frac{\\pi\\zeta}{\\sqrt{1-\\zeta^2}}}$ depends solely on $\\zeta$.
            </div>
            <div style="background:rgba(16,185,129,0.1); border-left:3px solid var(--accent-green); padding:8px 12px; font-size:0.85rem; color:#34D399;">
              ✅ Concept primed! Ready for today's theory lecture.
            </div>
          </div>
        </div>

        <div style="text-align:right;">
          <button class="btn-primary" onclick="AppState.switchView('step2')">
            🚀 Proceed to Today's Video Lecture ➔
          </button>
        </div>
      </div>
    `;
  },

  // ==========================================================================
  // STEP 2: Video Lecture & Formula Sheet
  // ==========================================================================
  renderStep2(videoMode = "theory") {
    const container = document.getElementById("step2Content");
    if (!container) return;

    const topic = SYLLABUS_DATA.find(t => t.id === this.activeTopicId) || SYLLABUS_DATA[0];
    const vidId = videoMode === "theory" ? topic.yt_theory_vid_id : topic.yt_pyq_vid_id;
    const vidTitle = videoMode === "theory" ? topic.yt_theory_title : topic.yt_pyq_title;

    container.innerHTML = `
      <div class="study-card">
        <div class="step-header">
          <div>
            <div class="step-title">📺 Step 2: In-App Video Lecture & High-Yield Notes</div>
            <div class="step-subtitle">Watch without external redirects, master the governing equations, and take notes.</div>
          </div>
          <button class="btn-secondary" onclick="AppState.toggleCalc()">🖩 Open TCS iON Calculator</button>
        </div>

        <div class="video-toggle-bar">
          <button class="btn-toggle ${videoMode === 'theory' ? 'active' : ''}" onclick="AppState.renderStep2('theory')">
            🏛️ Tier 1: GATE Theory Lecture
          </button>
          <button class="btn-toggle ${videoMode === 'pyq' ? 'active' : ''}" onclick="AppState.renderStep2('pyq')">
            🧮 Tier 2: Step-by-Step PYQ Walkthrough
          </button>
        </div>

        <div style="color:var(--text-secondary); font-size:0.9rem; margin-bottom:8px;">
          <b>Now Playing:</b> ${vidTitle}
        </div>

        <div class="video-container">
          <iframe src="https://www.youtube-nocookie.com/embed/${vidId}?rel=0" allowfullscreen></iframe>
        </div>

        <div style="background:#0F172A; padding:16px; border-radius:8px; border:1px solid var(--border-color); margin-top:16px;">
          <h4 style="color:var(--accent-blue); margin-bottom:8px;">📐 Governing Mathematical Formula</h4>
          <div class="formula-box">
            $$\\displaystyle ${topic.key_formula_latex}$$
          </div>
          <div class="takeaway-box">
            <b>Core Exam Takeaways:</b> ${topic.core_summary}
          </div>
        </div>

        <div style="display:flex; justify-content:space-between; align-items:center; margin-top:20px;">
          <button class="btn-secondary" onclick="AppState.switchView('step1')">⬅️ Back to Recall</button>
          <button class="btn-primary" onclick="AppState.switchView('step3')">
            🧮 Proceed to Today's PYQ Practice ➔
          </button>
        </div>
      </div>
    `;
  },

  // ==========================================================================
  // STEP 3: Interactive GATE PYQ Solver
  // ==========================================================================
  renderStep3() {
    const container = document.getElementById("step3Content");
    if (!container) return;

    const topic = SYLLABUS_DATA.find(t => t.id === this.activeTopicId) || SYLLABUS_DATA[0];
    const isMCQ = topic.pyq_type === "MCQ";

    let inputHtml = "";
    if (isMCQ && topic.pyq_options && topic.pyq_options.length > 0) {
      inputHtml = `
        <div class="option-group">
          ${topic.pyq_options.map((opt, i) => `
            <label class="option-label">
              <input type="radio" name="pyq_option" value="${opt}">
              <span>${opt}</span>
            </label>
          `).join("")}
        </div>
      `;
    } else {
      inputHtml = `
        <div>
          <label style="display:block; font-size:0.9rem; color:var(--text-secondary); margin-bottom:6px;">Enter Numerical Answer (NAT):</label>
          <input type="text" id="natInput" class="nat-input" placeholder="e.g. 138.5">
        </div>
      `;
    }

    container.innerHTML = `
      <div class="study-card">
        <div class="step-header">
          <div>
            <div class="step-title">🧮 Step 3: Interactive GATE Problem Solver</div>
            <div class="step-subtitle">Solve official 1-mark & 2-mark questions directly on-screen under exam conditions.</div>
          </div>
          <button class="btn-secondary" onclick="AppState.toggleCalc()">🖩 Open TCS iON Calculator</button>
        </div>

        <div style="background:#0F172A; padding:20px; border-radius:8px; border:1px solid var(--border-color); margin-bottom:20px;">
          <div style="display:flex; justify-content:space-between; color:var(--text-muted); font-size:0.8rem; text-transform:uppercase; margin-bottom:8px;">
            <span>[${topic.id}] ${topic.domain}</span>
            <span>Weightage: ~${topic.weightage_approx_marks} Marks</span>
          </div>

          <div class="question-text">${topic.pyq_question}</div>

          ${inputHtml}

          <div class="action-row">
            <button class="btn-primary" onclick="AppState.checkPyqAnswer()">🚀 Check Answer</button>
            <button class="btn-danger" onclick="AppState.quarantineCurrentMistake()">⚠️ Tag Mistake</button>
          </div>

          <div id="pyqFeedback"></div>
        </div>

        <div style="display:flex; justify-content:space-between; align-items:center;">
          <button class="btn-secondary" onclick="AppState.switchView('step2')">⬅️ Back to Lecture</button>
          <button class="btn-primary" onclick="AppState.switchView('step4')">
            ✅ Proceed to Daily Wrap-Up ➔
          </button>
        </div>
      </div>
    `;
  },

  checkPyqAnswer() {
    const topic = SYLLABUS_DATA.find(t => t.id === this.activeTopicId);
    if (!topic) return;

    const fb = document.getElementById("pyqFeedback");
    if (!fb) return;

    let userAns = "";
    if (topic.pyq_type === "MCQ") {
      const selected = document.querySelector('input[name="pyq_option"]:checked');
      userAns = selected ? selected.value.trim() : "";
    } else {
      const nat = document.getElementById("natInput");
      userAns = nat ? nat.value.trim() : "";
    }

    if (!userAns) {
      fb.innerHTML = `<div class="feedback-box feedback-error">⚠️ Please select or enter an answer first.</div>`;
      return;
    }

    const correctAns = topic.pyq_correct_answer.trim();
    let isCorrect = false;

    if (topic.pyq_type === "MCQ") {
      if (userAns === correctAns) {
        isCorrect = true;
      } else {
        const uPrefix = userAns.split(")")[0].trim().toUpperCase();
        const cPrefix = correctAns.split(")")[0].trim().toUpperCase();
        isCorrect = (uPrefix === cPrefix && uPrefix.length === 1);
      }
    } else {
      try {
        const uVal = parseFloat(userAns.replace(",", "."));
        const cVal = parseFloat(correctAns.replace(",", "."));
        if (!isNaN(uVal) && !isNaN(cVal)) {
          isCorrect = Math.abs(uVal - cVal) <= 0.05 * Math.abs(cVal) || Math.abs(uVal - cVal) <= 0.1;
        }
      } catch (e) {
        isCorrect = (userAns === correctAns);
      }
    }

    if (isCorrect) {
      fb.innerHTML = `
        <div class="feedback-box feedback-success">🎉 Correct Answer! (${correctAns})</div>
        <div class="solution-box">
          <h4 style="color:var(--accent-green); margin-bottom:8px;">📖 Step-by-Step Mathematical Derivation</h4>
          <div>${topic.pyq_explanation}</div>
        </div>
      `;
    } else {
      fb.innerHTML = `
        <div class="feedback-box feedback-error">❌ Incorrect. Correct Answer is: <b>${correctAns}</b></div>
        <div class="solution-box">
          <h4 style="color:var(--accent-rose); margin-bottom:8px;">📖 Step-by-Step Mathematical Derivation</h4>
          <div>${topic.pyq_explanation}</div>
        </div>
      `;
    }

    if (window.renderMathInElement) {
      renderMathInElement(fb, {
        delimiters: [
          { left: "$$", right: "$$", display: true },
          { left: "$", right: "$", display: false }
        ]
      });
    }
  },

  quarantineCurrentMistake() {
    const topic = SYLLABUS_DATA.find(t => t.id === this.activeTopicId);
    if (!topic) return;

    this.mistakesQueue.push({
      id: Date.now(),
      date: this.getTodayStr(),
      topicId: topic.id,
      topicName: topic.topic_name,
      code: "C",
      question: topic.pyq_question,
      takeaway: topic.pyq_explanation,
      mastered: false
    });
    this.save();
    alert(`⚠️ Problem for '${topic.topic_name}' added to your Redo Mistakes Diary!`);
  },

  // ==========================================================================
  // STEP 4: 10-Second Daily Wrap-Up
  // ==========================================================================
  renderStep4() {
    const container = document.getElementById("step4Content");
    if (!container) return;

    const topic = SYLLABUS_DATA.find(t => t.id === this.activeTopicId) || SYLLABUS_DATA[0];
    const isComp = this.completedTopics.has(topic.id);
    const hrsStudied = (this.activeSecondsToday / 3600).toFixed(1);

    container.innerHTML = `
      <div class="study-card">
        <div class="step-header">
          <div>
            <div class="step-title">✅ Step 4: 10-Second Session Wrap-Up</div>
            <div class="step-subtitle">Log your focused study time and lock in tomorrow's preparation assignment.</div>
          </div>
        </div>

        <div style="background:#0F172A; padding:24px; border-radius:8px; border:1px solid var(--border-color); max-width:600px; margin:0 auto 20px auto;">
          <div style="margin-bottom:16px;">
            <label style="display:block; font-size:0.9rem; color:var(--text-secondary); margin-bottom:8px;">
              ⏱️ Active Foreground Time Logged Today:
            </label>
            <div style="font-family:var(--font-mono); font-size:1.6rem; color:var(--accent-green); font-weight:700;">
              ${Math.floor(this.activeSecondsToday / 3600)}h ${Math.floor((this.activeSecondsToday % 3600) / 60)}m (${hrsStudied} hrs)
            </div>
          </div>

          <div style="margin-bottom:24px;">
            <label style="display:flex; align-items:center; gap:12px; font-size:1rem; cursor:pointer;">
              <input type="checkbox" id="chkComplete" ${isComp ? "checked" : ""} style="transform:scale(1.4); accent-color:var(--accent-green);">
              <span>Mark <b>[${topic.id}] ${topic.topic_name}</b> as Mastered</span>
            </label>
          </div>

          <button class="btn-primary" style="width:100%; justify-content:center;" onclick="AppState.finishDailySession()">
            🎯 Lock in Progress & Advance to Next Topic
          </button>
        </div>
      </div>
    `;
  },

  finishDailySession() {
    const chk = document.getElementById("chkComplete");
    if (chk && chk.checked) {
      this.completedTopics.add(this.activeTopicId);
    } else {
      this.completedTopics.delete(this.activeTopicId);
    }

    // Advance to next uncompleted topic
    const nextTopic = SYLLABUS_DATA.find(t => !this.completedTopics.has(t.id));
    if (nextTopic) {
      this.activeTopicId = nextTopic.id;
    }

    this.save();
    this.renderHeader();
    alert("🎉 Progress saved! Loading next focus topic.");
    this.switchView("step1");
  },

  // ==========================================================================
  // Syllabus Accordion Tree View
  // ==========================================================================
  renderSyllabusTree() {
    const container = document.getElementById("syllabusContent");
    if (!container) return;

    // Group by Week (1 to 20)
    const weeks = {};
    for (let w = 1; w <= TOTAL_WEEKS; w++) weeks[w] = [];
    SYLLABUS_DATA.forEach(t => {
      if (weeks[t.week_number]) weeks[t.week_number].push(t);
    });

    let html = `
      <div class="study-card">
        <div class="step-header">
          <div>
            <div class="step-title">📚 20-Week Master Syllabus Hierarchy (IN & RA)</div>
            <div class="step-subtitle">Select any topic to load it directly into your daily study studio.</div>
          </div>
        </div>
    `;

    for (let w = 1; w <= TOTAL_WEEKS; w++) {
      const topicList = weeks[w];
      if (!topicList || topicList.length === 0) continue;
      const compCount = topicList.filter(t => this.completedTopics.has(t.id)).length;
      const pct = Math.round((compCount / topicList.length) * 100);

      html += `
        <div class="week-card">
          <div class="week-header" onclick="AppState.toggleAccordion('week-${w}')">
            <div>
              <span style="font-weight:700; color:var(--accent-blue);">Week ${w}</span>: ${topicList[0].domain}
            </div>
            <div style="font-size:0.85rem; color:var(--text-secondary);">
              ${compCount}/${topicList.length} Completed (${pct}%)
            </div>
          </div>
          <div id="week-${w}" class="topic-list" style="${w === 1 ? 'display:flex;' : 'display:none;'}">
            ${topicList.map(t => {
              const isDone = this.completedTopics.has(t.id);
              const isActive = t.id === this.activeTopicId;
              return `
                <div class="topic-row ${isDone ? 'completed' : ''} ${isActive ? 'active' : ''}">
                  <div>
                    <span style="font-weight:600;">[${t.id}] ${t.topic_name}</span>
                    <span style="color:var(--text-muted); font-size:0.8rem; margin-left:8px;">(${t.module_name})</span>
                  </div>
                  <div>
                    ${isDone ? '<span style="color:var(--accent-green); font-size:0.85rem; margin-right:12px;">✅ Done</span>' : ''}
                    <button class="btn-secondary" style="padding:4px 10px; font-size:0.8rem;" onclick="AppState.selectTopic('${t.id}')">
                      ${isActive ? '🎯 Active Topic' : 'Set Active'}
                    </button>
                  </div>
                </div>
              `;
            }).join("")}
          </div>
        </div>
      `;
    }

    html += `</div>`;
    container.innerHTML = html;
  },

  toggleAccordion(id) {
    const el = document.getElementById(id);
    if (!el) return;
    el.style.display = el.style.display === "none" ? "flex" : "none";
  },

  selectTopic(topicId) {
    this.activeTopicId = topicId;
    this.save();
    this.switchView("step1");
  },

  // ==========================================================================
  // Progress & Mistakes Diary View
  // ==========================================================================
  renderProgressDiary() {
    const container = document.getElementById("progressContent");
    if (!container) return;

    const totalTopics = SYLLABUS_DATA.length;
    const completedCount = this.completedTopics.size;
    const pct = Math.round((completedCount / totalTopics) * 100);

    const activeMistakes = this.mistakesQueue.filter(m => !m.mastered);
    const masteredMistakes = this.mistakesQueue.filter(m => m.mastered);

    container.innerHTML = `
      <div class="study-card">
        <div class="step-header">
          <div>
            <div class="step-title">📊 Preparation Progress & Mistakes Diary</div>
            <div class="step-subtitle">Track your 20-week velocity, revisit quarantined mistakes, and back up data.</div>
          </div>
          <div style="display:flex; gap:8px;">
            <button class="btn-secondary" onclick="AppState.exportFormulaSheet()">📖 Download Formula Sheet</button>
            <button class="btn-secondary" onclick="AppState.exportBackupJson()">💾 Backup .json</button>
          </div>
        </div>

        <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:16px; margin-bottom:24px;">
          <div style="background:#0F172A; padding:16px; border-radius:8px; border:1px solid var(--border-color); text-align:center;">
            <div style="font-size:0.85rem; color:var(--text-secondary);">Syllabus Cleared</div>
            <div style="font-size:1.8rem; font-weight:800; color:var(--accent-blue);">${pct}%</div>
            <div style="font-size:0.8rem; color:var(--text-muted);">${completedCount} of ${totalTopics} Topics</div>
          </div>
          <div style="background:#0F172A; padding:16px; border-radius:8px; border:1px solid var(--border-color); text-align:center;">
            <div style="font-size:0.85rem; color:var(--text-secondary);">Quarantined Mistakes</div>
            <div style="font-size:1.8rem; font-weight:800; color:var(--accent-rose);">${activeMistakes.length}</div>
            <div style="font-size:0.8rem; color:var(--text-muted);">${masteredMistakes.length} Mastered</div>
          </div>
          <div style="background:#0F172A; padding:16px; border-radius:8px; border:1px solid var(--border-color); text-align:center;">
            <div style="font-size:0.85rem; color:var(--text-secondary);">Total Active Hours</div>
            <div style="font-size:1.8rem; font-weight:800; color:var(--accent-green);">
              ${(this.activeSecondsToday / 3600).toFixed(1)}h
            </div>
            <div style="font-size:0.8rem; color:var(--text-muted);">Logged in Foreground</div>
          </div>
        </div>

        <h4 style="color:var(--text-primary); margin-bottom:12px;">⚠️ Active Quarantined Mistakes (Re-solve to Master)</h4>
        ${activeMistakes.length === 0 ? `
          <div style="background:#0F172A; padding:20px; border-radius:8px; text-align:center; color:var(--text-muted); border:1px solid var(--border-color);">
            ✅ No active mistakes in quarantine! Clean slate.
          </div>
        ` : `
          <div style="display:flex; flex-direction:column; gap:10px;">
            ${activeMistakes.map(m => `
              <div style="background:#0F172A; padding:14px; border-radius:8px; border:1px solid var(--border-color); display:flex; justify-content:space-between; align-items:center;">
                <div>
                  <span style="font-weight:700; color:var(--accent-rose);">[${m.code}] ${m.topicName}</span>
                  <div style="font-size:0.85rem; color:var(--text-secondary); margin-top:4px;">${m.question.substring(0, 100)}...</div>
                </div>
                <button class="btn-secondary" style="padding:6px 12px; font-size:0.8rem;" onclick="AppState.resolveMistake(${m.id})">
                  ✅ Mark Mastered
                </button>
              </div>
            `).join("")}
          </div>
        `}
      </div>
    `;
  },

  resolveMistake(id) {
    const item = this.mistakesQueue.find(m => m.id === id);
    if (item) {
      item.mastered = true;
      this.save();
      this.renderProgressDiary();
    }
  },

  exportBackupJson() {
    const data = {
      startDate: this.startDate.toISOString().split("T")[0],
      activeTopicId: this.activeTopicId,
      completedTopics: [...this.completedTopics],
      mistakesQueue: this.mistakesQueue,
      activeSecondsToday: this.activeSecondsToday
    };
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `gate_in_ra_progress_backup_${this.getTodayStr()}.json`;
    a.click();
  },

  exportFormulaSheet() {
    let md = "# 📖 GATE IN & RA Master Formula Vault Cheat-Sheet\n\n";
    SYLLABUS_DATA.forEach(t => {
      md += `### [${t.id}] ${t.topic_name} (${t.domain})\n`;
      md += `$$\\displaystyle ${t.key_formula_latex}$$\n\n`;
      md += `*Takeaways:* ${t.core_summary}\n\n---\n\n`;
    });
    const blob = new Blob([md], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `gate_in_ra_formula_vault.md`;
    a.click();
  },

  // ==========================================================================
  // TCS iON Virtual Calculator Engine
  // ==========================================================================
  toggleCalc() {
    const modal = document.getElementById("calcModal");
    if (!modal) return;
    modal.classList.toggle("open");
  },

  calcAppend(val) {
    if (this.calcDisplay === "0" || this.calcDisplay === "Error") {
      this.calcDisplay = val;
    } else {
      this.calcDisplay += val;
    }
    this.updateCalcDisplay();
  },

  calcOp(op) {
    if (this.calcDisplay !== "Error") {
      this.calcDisplay += ` ${op} `;
    }
    this.updateCalcDisplay();
  },

  calcClear() {
    this.calcDisplay = "0";
    this.updateCalcDisplay();
  },

  calcDel() {
    if (this.calcDisplay === "Error" || this.calcDisplay.length <= 1) {
      this.calcDisplay = "0";
    } else {
      this.calcDisplay = this.calcDisplay.slice(0, -1);
    }
    this.updateCalcDisplay();
  },

  calcEval() {
    try {
      const clean = this.calcDisplay.replace(/\^/g, "**");
      // Safe arithmetic evaluator
      const res = Function(`"use strict"; return (${clean})`)();
      if (typeof res === "number" && !isNaN(res) && isFinite(res)) {
        this.calcDisplay = String(parseFloat(res.toFixed(8)));
      } else {
        this.calcDisplay = "Error";
      }
    } catch (e) {
      this.calcDisplay = "Error";
    }
    this.updateCalcDisplay();
  },

  calcTrig(fn) {
    try {
      let val = parseFloat(this.calcDisplay);
      if (!this.calcRadMode) val = val * (Math.PI / 180);
      let res = 0;
      if (fn === "sin") res = Math.sin(val);
      else if (fn === "cos") res = Math.cos(val);
      else if (fn === "tan") res = Math.tan(val);
      this.calcDisplay = String(parseFloat(res.toFixed(8)));
    } catch (e) {
      this.calcDisplay = "Error";
    }
    this.updateCalcDisplay();
  },

  calcSingle(fn) {
    try {
      const val = parseFloat(this.calcDisplay);
      let res = 0;
      if (fn === "sqrt") res = Math.sqrt(val);
      else if (fn === "ln") res = Math.log(val);
      else if (fn === "log10") res = Math.log10(val);
      else if (fn === "exp") res = Math.exp(val);
      if (isNaN(res) || !isFinite(res)) this.calcDisplay = "Error";
      else this.calcDisplay = String(parseFloat(res.toFixed(8)));
    } catch (e) {
      this.calcDisplay = "Error";
    }
    this.updateCalcDisplay();
  },

  updateCalcDisplay() {
    const el = document.getElementById("calcScreen");
    if (el) el.textContent = this.calcDisplay;
  }
};

// Bootstrap application on DOM ready
document.addEventListener("DOMContentLoaded", () => {
  AppState.init();
});
