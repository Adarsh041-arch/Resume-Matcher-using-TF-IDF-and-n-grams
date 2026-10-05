/**
 * ResumeMatcher Frontend Application Logic
 */

document.addEventListener("DOMContentLoaded", () => {
  // Elements
  const tabUpload = document.getElementById("tab-upload");
  const tabText = document.getElementById("tab-text");
  const uploadContainer = document.getElementById("upload-container");
  const textContainer = document.getElementById("text-container");
  const dropZone = document.getElementById("drop-zone");
  const fileInput = document.getElementById("file-input");
  const fileBadge = document.getElementById("file-preview-badge");
  const fileNameLabel = document.getElementById("file-name-label");
  const btnClearFile = document.getElementById("btn-clear-file");

  const resumeTextArea = document.getElementById("resume-text");
  const jdTextArea = document.getElementById("jd-text");
  const btnClearJd = document.getElementById("btn-clear-jd");
  const resumeCharCount = document.getElementById("resume-char-count");
  const jdCharCount = document.getElementById("jd-char-count");

  const sliderTfidf = document.getElementById("slider-tfidf");
  const sliderSkill = document.getElementById("slider-skill");
  const valTfidf = document.getElementById("val-tfidf");
  const valSkill = document.getElementById("val-skill");

  const btnRunMatch = document.getElementById("btn-run-match");
  const matchLoader = document.getElementById("match-loader");
  const resultsSection = document.getElementById("results-section");

  // Gauge & Metrics Elements
  const gaugeCircle = document.getElementById("gauge-circle");
  const gaugeScore = document.getElementById("gauge-score");
  const matchStatusTitle = document.getElementById("match-status-title");
  const matchStatusDesc = document.getElementById("match-status-desc");

  const scoreTfidf = document.getElementById("score-tfidf");
  const barTfidf = document.getElementById("bar-tfidf");
  const scoreSkills = document.getElementById("score-skills");
  const barSkills = document.getElementById("bar-skills");

  const statMatchedCount = document.getElementById("stat-matched-count");
  const statMissingCount = document.getElementById("stat-missing-count");
  const statJdSkills = document.getElementById("stat-jd-skills");
  const statResumeSkills = document.getElementById("stat-resume-skills");
  const matchedInventoryCount = document.getElementById("matched-inventory-count");

  const missingSkillsContainer = document.getElementById("missing-skills-container");
  const categoryGridContainer = document.getElementById("category-grid-container");
  const matchedChipsContainer = document.getElementById("matched-chips-container");
  const missingFilterPills = document.querySelectorAll("#missing-priority-filters .filter-pill");

  const btnExportReport = document.getElementById("btn-export-report");
  const btnBenchmarkModal = document.getElementById("btn-benchmark-modal");
  const benchmarkModal = document.getElementById("benchmark-modal");
  const btnCloseModal = document.getElementById("btn-close-modal");

  // State
  let currentFile = null;
  let activeTab = "upload";
  let sampleData = null;
  let lastResultData = null;

  // 1. Fetch Samples on Load
  fetch("/api/samples")
    .then((r) => r.json())
    .then((data) => {
      sampleData = data;
    })
    .catch((err) => console.warn("Could not pre-load sample presets:", err));

  // 2. Tab Switching
  tabUpload.addEventListener("click", () => {
    activeTab = "upload";
    tabUpload.classList.add("active");
    tabText.classList.remove("active");
    uploadContainer.classList.remove("hidden");
    textContainer.classList.add("hidden");
  });

  tabText.addEventListener("click", () => {
    activeTab = "text";
    tabText.classList.add("active");
    tabUpload.classList.remove("active");
    textContainer.classList.remove("hidden");
    uploadContainer.classList.add("hidden");
  });

  // 3. Dropzone & File Input
  dropZone.addEventListener("click", (e) => {
    if (e.target !== btnClearFile) fileInput.click();
  });

  ["dragenter", "dragover"].forEach((eventName) => {
    dropZone.addEventListener(eventName, (e) => {
      e.preventDefault();
      dropZone.classList.add("dragover");
    });
  });

  ["dragleave", "drop"].forEach((eventName) => {
    dropZone.addEventListener(eventName, (e) => {
      e.preventDefault();
      dropZone.classList.remove("dragover");
    });
  });

  dropZone.addEventListener("drop", (e) => {
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileSelected(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener("change", (e) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFileSelected(e.target.files[0]);
    }
  });

  function handleFileSelected(file) {
    currentFile = file;
    fileNameLabel.textContent = file.name;
    fileBadge.classList.remove("hidden");
    resumeCharCount.textContent = `Attached file: ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
  }

  btnClearFile.addEventListener("click", (e) => {
    e.stopPropagation();
    currentFile = null;
    fileInput.value = "";
    fileBadge.classList.add("hidden");
    resumeCharCount.textContent = "0 characters";
  });

  // 4. Character counters
  resumeTextArea.addEventListener("input", () => {
    resumeCharCount.textContent = `${resumeTextArea.value.length} characters`;
  });

  jdTextArea.addEventListener("input", () => {
    jdCharCount.textContent = `${jdTextArea.value.length} characters`;
  });

  btnClearJd.addEventListener("click", () => {
    jdTextArea.value = "";
    jdCharCount.textContent = "0 characters";
  });

  // 5. Weight Sliders Synchronization
  sliderTfidf.addEventListener("input", (e) => {
    const val = parseInt(e.target.value);
    valTfidf.textContent = `${val}%`;
    const complement = 100 - val;
    sliderSkill.value = complement;
    valSkill.textContent = `${complement}%`;
  });

  sliderSkill.addEventListener("input", (e) => {
    const val = parseInt(e.target.value);
    valSkill.textContent = `${val}%`;
    const complement = 100 - val;
    sliderTfidf.value = complement;
    valTfidf.textContent = `${complement}%`;
  });

  // 6. Quick Load Preset Scenarios
  document.querySelectorAll(".btn-preset").forEach((btn) => {
    btn.addEventListener("click", () => {
      const role = btn.getAttribute("data-role");
      if (!sampleData) return;

      if (role === "data_scientist") {
        resumeTextArea.value = sampleData.resumes.data_scientist_resume || "";
        jdTextArea.value = sampleData.job_descriptions.senior_data_scientist_jd || "";
      } else if (role === "devops") {
        resumeTextArea.value = sampleData.resumes.devops_engineer_resume || "";
        jdTextArea.value = sampleData.job_descriptions.senior_devops_jd || "";
      } else if (role === "backend") {
        resumeTextArea.value = sampleData.resumes.backend_engineer_resume || "";
        jdTextArea.value = sampleData.job_descriptions.backend_python_jd || "";
      }

      // Switch to text tab so user can see what was loaded
      tabText.click();
      resumeTextArea.dispatchEvent(new Event("input"));
      jdTextArea.dispatchEvent(new Event("input"));

      // Trigger automatic match
      btnRunMatch.click();
    });
  });

  // 7. Analyze & Calculate Match
  btnRunMatch.addEventListener("click", async () => {
    const jdVal = jdTextArea.value.trim();
    if (!jdVal) {
      alert("Please paste or load a target Job Description first.");
      return;
    }

    const tfidfWeight = parseInt(sliderTfidf.value) / 100;
    const skillWeight = parseInt(sliderSkill.value) / 100;

    // Show loader
    matchLoader.classList.remove("hidden");
    resultsSection.classList.add("hidden");

    try {
      let data;
      if (activeTab === "upload" && currentFile) {
        // Multipart upload
        const formData = new FormData();
        formData.append("resume_file", currentFile);
        formData.append("jd_text", jdVal);
        formData.append("tfidf_weight", tfidfWeight.toString());
        formData.append("skill_weight", skillWeight.toString());

        const res = await fetch("/api/match", {
          method: "POST",
          body: formData
        });
        if (!res.ok) throw new Error((await res.json()).detail || "Failed to analyze resume file");
        data = await res.json();
      } else {
        // Direct text
        const resumeVal = resumeTextArea.value.trim();
        if (!resumeVal) {
          alert("Please upload a resume file or paste resume text.");
          matchLoader.classList.add("hidden");
          return;
        }

        const res = await fetch("/api/match-text", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            resume_text: resumeVal,
            jd_text: jdVal,
            tfidf_weight: tfidfWeight,
            skill_weight: skillWeight
          })
        });
        if (!res.ok) throw new Error((await res.json()).detail || "Failed to analyze text");
        data = await res.json();
      }

      lastResultData = data;
      renderResults(data);
    } catch (err) {
      alert("Error: " + err.message);
    } finally {
      matchLoader.classList.add("hidden");
    }
  });

  // 8. Render Results Function
  function renderResults(data) {
    resultsSection.classList.remove("hidden");
    resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });

    // Animate Gauge
    const score = data.composite_score;
    const circumference = 2 * Math.PI * 66; // r=66 -> ~414.69
    const offset = circumference - (score / 100) * circumference;

    gaugeCircle.style.strokeDashoffset = offset.toString();
    gaugeScore.textContent = `${Math.round(score)}%`;

    // Gauge status colors
    if (score >= 70) {
      gaugeCircle.style.stroke = "var(--accent-emerald)";
      matchStatusTitle.textContent = "Outstanding Fit";
      matchStatusTitle.style.color = "#34d399";
      matchStatusDesc.textContent = "Candidate demonstrates high lexical & taxonomic alignment with JD.";
    } else if (score >= 45) {
      gaugeCircle.style.stroke = "var(--accent-amber)";
      matchStatusTitle.textContent = "Moderate Potential Fit";
      matchStatusTitle.style.color = "#fbbf24";
      matchStatusDesc.textContent = "Candidate possesses relevant transferable skills with a few addressable gaps.";
    } else {
      gaugeCircle.style.stroke = "var(--accent-coral)";
      matchStatusTitle.textContent = "Low Alignment / Mismatch";
      matchStatusTitle.style.color = "#f43f5e";
      matchStatusDesc.textContent = "Significant skill deficit detected between candidate profile and role requirements.";
    }

    // Sub-metrics
    scoreTfidf.textContent = `${data.tfidf_similarity}%`;
    barTfidf.style.width = `${data.tfidf_similarity}%`;

    scoreSkills.textContent = `${data.skill_overlap_pct}%`;
    barSkills.style.width = `${data.skill_overlap_pct}%`;

    // Stat boxes
    statMatchedCount.textContent = data.matched_skills_count;
    statMissingCount.textContent = data.missing_skills_count;
    statJdSkills.textContent = data.jd_total_skills;
    statResumeSkills.textContent = data.resume_total_skills;
    matchedInventoryCount.textContent = data.matched_skills_count;

    // Render Missing Skills
    renderMissingSkills(data.missing_skills);

    // Render Category Breakdown Matrix
    renderCategoryMatrix(data.category_breakdown);

    // Render Matched Skills Inventory
    renderMatchedInventory(data.matched_skills);
  }

  function renderMissingSkills(missingList, priorityFilter = "all") {
    missingSkillsContainer.innerHTML = "";
    const filtered = missingList.filter((item) => {
      if (priorityFilter === "all") return true;
      return item.priority === priorityFilter;
    });

    if (filtered.length === 0) {
      missingSkillsContainer.innerHTML = `<p style="color: var(--text-muted); font-size: 0.9rem; grid-column: 1 / -1;">No missing skills in this priority tier!</p>`;
      return;
    }

    filtered.forEach((item) => {
      const el = document.createElement("div");
      el.className = "missing-skill-item";
      const priorityClass = item.priority.toLowerCase();

      el.innerHTML = `
        <div class="missing-skill-meta">
          <span class="missing-skill-name">${item.skill}</span>
          <span class="missing-skill-category">${item.category}</span>
        </div>
        <div class="missing-badges">
          <span class="badge-priority ${priorityClass}">${item.priority}</span>
          <span class="freq-chip">${item.frequency_in_jd}x in JD</span>
        </div>
      `;
      missingSkillsContainer.appendChild(el);
    });
  }

  // Missing Skills Filter Pills
  missingFilterPills.forEach((pill) => {
    pill.addEventListener("click", () => {
      missingFilterPills.forEach((p) => p.classList.remove("active"));
      pill.classList.add("active");
      const filter = pill.getAttribute("data-filter");
      if (lastResultData) {
        renderMissingSkills(lastResultData.missing_skills, filter);
      }
    });
  });

  function renderCategoryMatrix(categories) {
    categoryGridContainer.innerHTML = "";
    const catKeys = Object.keys(categories);

    if (catKeys.length === 0) {
      categoryGridContainer.innerHTML = `<p style="color: var(--text-muted); font-size: 0.9rem;">No category breakdown available.</p>`;
      return;
    }

    catKeys.forEach((catName) => {
      const cat = categories[catName];
      const card = document.createElement("div");
      card.className = "category-card";

      const matchedPills = cat.matched.map((s) => `<span class="pill-matched">✓ ${s}</span>`).join("");
      const missingPills = cat.missing.map((s) => `<span class="pill-missing">✕ ${s}</span>`).join("");

      card.innerHTML = `
        <div class="cat-header">
          <span class="cat-title">${catName}</span>
          <span class="cat-ratio color-${cat.coverage_pct >= 70 ? 'emerald' : cat.coverage_pct >= 40 ? 'amber' : 'coral'}">
            ${cat.matched_count}/${cat.total_required} (${cat.coverage_pct}%)
          </span>
        </div>
        <div class="cat-progress-track">
          <div class="cat-progress-fill" style="width: ${cat.coverage_pct}%"></div>
        </div>
        <div class="cat-pills">
          ${matchedPills}
          ${missingPills}
        </div>
      `;
      categoryGridContainer.appendChild(card);
    });
  }

  function renderMatchedInventory(matchedList) {
    matchedChipsContainer.innerHTML = "";
    if (matchedList.length === 0) {
      matchedChipsContainer.innerHTML = `<p style="color: var(--text-muted); font-size: 0.9rem;">No matching skills detected.</p>`;
      return;
    }

    matchedList.forEach((m) => {
      const chip = document.createElement("span");
      chip.className = "matched-chip";
      chip.innerHTML = `<span class="check">✓</span> ${m.skill} <span style="opacity: 0.6; font-size: 0.72rem;">(${m.category})</span>`;
      matchedChipsContainer.appendChild(chip);
    });
  }

  // 9. Export JSON Summary
  btnExportReport.addEventListener("click", () => {
    if (!lastResultData) return;
    const blob = new Blob([JSON.stringify(lastResultData, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `resume_match_report_${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  });

  // 10. Benchmark Modal
  btnBenchmarkModal.addEventListener("click", () => {
    benchmarkModal.classList.remove("hidden");
  });

  btnCloseModal.addEventListener("click", () => {
    benchmarkModal.classList.add("hidden");
  });

  benchmarkModal.addEventListener("click", (e) => {
    if (e.target === benchmarkModal) {
      benchmarkModal.classList.add("hidden");
    }
  });
});
