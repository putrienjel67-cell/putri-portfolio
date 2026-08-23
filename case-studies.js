document.addEventListener("DOMContentLoaded", () => {
  const projects = window.projectCaseStudies || {};
  const projectKeys = Object.keys(projects);
  const cards = [...document.querySelectorAll(".project")];
  let activeKey = "";
  let activeCard = null;

  const stats = [
    [String(projectKeys.length), "complete case studies"],
    [String(projectKeys.reduce((total, key) => total + projects[key].gallery.length, 0)), "evidence screenshots"],
    [String(projectKeys.reduce((total, key) => total + projects[key].files.length, 0)), "verified project workbooks"],
    ["Formula-driven QA", "checks, review queues, and SOPs"]
  ];

  document.querySelectorAll(".proof-item").forEach((item, index) => {
    if (!stats[index]) return;
    item.querySelector("strong").textContent = stats[index][0];
    item.querySelector("span").textContent = stats[index][1];
  });

  const workSection = document.getElementById("work");
  if (workSection) {
    workSection.querySelector(".kicker").textContent = "Evidence-based projects";
    workSection.querySelector("h2").textContent = "Open the work. Follow the process.";
    workSection.querySelector(".split-head p").textContent = "Each project opens into a complete case study with the problem, workflow, evidence gallery, and downloadable workbook.";
    workSection.querySelector(".filters").setAttribute("aria-label", "Filter projects");
  }
  const supportingHighlight = document.querySelector(".float-card.three");
  if (supportingHighlight) supportingHighlight.textContent = "Written-first admin support";

  const dialog = document.createElement("dialog");
  dialog.className = "case-dialog";
  dialog.setAttribute("aria-labelledby", "case-title");
  dialog.innerHTML = `
    <div class="case-shell">
      <nav class="case-nav" aria-label="Case study navigation">
        <button class="case-close" type="button">Back to projects</button>
        <span class="case-position" aria-live="polite"></span>
        <div class="case-nav-actions">
          <button class="case-prev" type="button">Previous</button>
          <button class="case-next" type="button">Next</button>
        </div>
      </nav>
      <div class="case-content"></div>
    </div>`;
  document.body.append(dialog);

  const viewer = document.createElement("div");
  viewer.className = "gallery-viewer";
  viewer.setAttribute("role", "dialog");
  viewer.setAttribute("aria-modal", "true");
  viewer.setAttribute("aria-label", "Screenshot preview");
  viewer.innerHTML = '<button class="viewer-close" type="button">Close image</button><img alt="">';
  document.body.append(viewer);

  const list = (items, className = "case-list") => `<ul class="${className}">${items.map(item => `<li>${item}</li>`).join("")}</ul>`;
  const tags = items => `<div class="case-tags">${items.map(item => `<span>${item}</span>`).join("")}</div>`;
  const evidenceCaption = filename => filename
    .replace(/\.png$/i, "")
    .replace(/^EV-\d+[A-C]?_?/i, "")
    .replaceAll("_", " ");

  function renderCaseStudy(key, updateHistory = true) {
    const item = projects[key];
    if (!item) return;
    activeKey = key;
    const projectIndex = projectKeys.indexOf(key);
    const evidenceFigure = (filename, index, eager = false) => {
      const src = `assets/projects/${key}/${filename}`;
      return `<figure class="${index === 0 ? "evidence-featured" : ""}">
        <button class="evidence-open" type="button" data-full="${src}" aria-label="Open screenshot: ${evidenceCaption(filename)}">
          <img ${eager ? `src="${src}" loading="eager" fetchpriority="${index === 0 ? "high" : "auto"}"` : `data-src="${src}"`} alt="${item.id} evidence: ${evidenceCaption(filename)}">
        </button>
        <figcaption><span>${String(index + 1).padStart(2, "0")}</span>${evidenceCaption(filename)}</figcaption>
      </figure>`;
    };
    const primaryGallery = item.primaryEvidence.map((filename, index) => evidenceFigure(filename, index, true)).join("");
    const remainingEvidence = item.gallery.filter(filename => !item.primaryEvidence.includes(filename));
    const completeGallery = remainingEvidence.map((filename, index) => evidenceFigure(filename, item.primaryEvidence.length + index)).join("");

    const projectFiles = item.files.map(file => `<article class="file-item">
      <div><p class="case-meta">${file.role}</p><h4>${file.label}</h4><p>${file.description}</p><p class="file-sheets"><strong>Sheets:</strong> ${file.sheets.join(", ")}</p></div>
      <a class="btn secondary" href="${file.path}" download>Download .xlsx</a>
    </article>`).join("");
    const githubAction = item.github
      ? `<a class="btn secondary" href="${item.github}" target="_blank" rel="noopener">View GitHub repository</a>`
      : "";

    dialog.querySelector(".case-position").textContent = `${item.id} of ${projectKeys.length}`;
    dialog.querySelector(".case-prev").disabled = projectIndex === 0;
    dialog.querySelector(".case-next").disabled = projectIndex === projectKeys.length - 1;
    dialog.querySelector(".case-content").innerHTML = `
      <header class="case-hero">
        <div class="case-hero-copy">
          <p class="case-meta">${item.id} | ${item.category}</p>
          <h2 id="case-title">${item.name}</h2>
          <p class="case-summary">${item.summary}</p>
        </div>
        <dl class="case-facts">
          <div><dt>Evidence</dt><dd>${item.gallery.length} screenshots</dd></div>
          <div><dt>Project files</dt><dd>${item.files.length} verified workbook${item.files.length === 1 ? "" : "s"}</dd></div>
          <div><dt>Repository</dt><dd>${item.github ? "Public repository available" : "No public repository"}</dd></div>
        </dl>
        <p class="case-integrity">Independent portfolio simulation using fictional data. Results describe the workbook dataset, not paid client impact.</p>
      </header>
      <div class="case-body">
        <div class="case-intro">
          <section class="case-block"><h3>Problem and objective</h3><p>${item.problem}</p></section>
          <section class="case-block"><h3>Data and work scope</h3><p>${item.data}</p></section>
        </div>
        <section class="case-section case-work"><h3>What I worked on</h3>${list(item.work)}</section>
        <section class="case-section case-process"><h3>Workflow</h3>${list(item.workflow, "case-list workflow-list")}</section>
        <section class="case-section case-tooling"><h3>Tools used</h3>${tags(item.tools)}</section>
        <section class="case-section case-outcome"><h3>Result</h3><div class="case-result">${item.result}</div></section>
        <section class="case-section case-skills"><h3>Skills shown</h3>${tags(item.skills)}</section>
        <section class="evidence-section" aria-labelledby="evidence-title">
          <div class="gallery-head">
            <div><p class="case-meta">Evidence gallery</p><h3 id="evidence-title">The work, not just the claim.</h3></div>
            <p>${item.gallery.length} screenshots from source data, formulas, validation controls, dashboards, queues, and documentation.</p>
          </div>
          <div class="case-gallery primary-gallery">${primaryGallery}</div>
          ${remainingEvidence.length ? `<details class="complete-evidence"><summary>View all evidence (${item.gallery.length})</summary><div class="case-gallery">${completeGallery}</div></details>` : ""}
        </section>
        <section class="case-deliverables" aria-labelledby="deliverables-title">
          <div><p class="case-meta">Recruiter access</p><h3 id="deliverables-title">Project files</h3><p>These are the original source, processed, dashboard, or complete workbooks found in this project folder. No project-specific public GitHub repository was found.</p></div>
          <div class="project-files">${projectFiles}</div>
          <div class="case-actions">${githubAction}<button class="btn secondary case-back" type="button">Back to projects</button></div>
        </section>
        <nav class="case-footer-nav" aria-label="Browse case studies">
          <button class="case-prev" type="button" ${projectIndex === 0 ? "disabled" : ""}>Previous case study</button>
          <span>${String(projectIndex + 1).padStart(2, "0")} / ${String(projectKeys.length).padStart(2, "0")}</span>
          <button class="case-next" type="button" ${projectIndex === projectKeys.length - 1 ? "disabled" : ""}>Next case study</button>
        </nav>
      </div>`;

    dialog.querySelectorAll(".evidence-open").forEach(button => button.addEventListener("click", () => openViewer(button)));
    dialog.querySelector(".complete-evidence")?.addEventListener("toggle", event => {
      if (!event.currentTarget.open) return;
      event.currentTarget.querySelectorAll("img[data-src]").forEach(image => {
        image.src = image.dataset.src;
        image.removeAttribute("data-src");
      });
    }, { once: true });
    dialog.querySelector(".case-back").addEventListener("click", closeCaseStudy);
    dialog.querySelector(".case-content").querySelectorAll(".case-prev").forEach(button => button.addEventListener("click", () => openAdjacent(-1)));
    dialog.querySelector(".case-content").querySelectorAll(".case-next").forEach(button => button.addEventListener("click", () => openAdjacent(1)));
    if (!dialog.open) dialog.showModal();
    dialog.scrollTop = 0;
    document.body.classList.add("case-open");
    if (updateHistory) history.pushState({ caseStudy: key }, "", `#case-${key}`);
  }

  function openAdjacent(direction) {
    const nextIndex = projectKeys.indexOf(activeKey) + direction;
    const nextKey = projectKeys[nextIndex];
    if (nextKey) renderCaseStudy(nextKey);
  }

  function closeCaseStudy(updateHistory = true) {
    if (dialog.open) dialog.close();
    document.body.classList.remove("case-open");
    activeKey = "";
    if (updateHistory) history.pushState(null, "", "#work");
    activeCard?.focus({ preventScroll: true });
    document.getElementById("work")?.scrollIntoView({ block: "start" });
  }

  function openViewer(button) {
    const fullImage = viewer.querySelector("img");
    fullImage.src = button.dataset.full;
    fullImage.alt = button.querySelector("img").alt;
    viewer.classList.add("open");
    viewer.querySelector(".viewer-close").focus();
  }

  function closeViewer() {
    viewer.classList.remove("open");
    viewer.querySelector("img").removeAttribute("src");
  }

  cards.forEach((card, index) => {
    const key = projectKeys[index];
    const item = projects[key];
    if (!item) return;
    card.tabIndex = 0;
    card.setAttribute("role", "link");
    card.setAttribute("aria-label", `Open case study: ${item.name}`);
    card.dataset.project = key;
    const proof = document.createElement("div");
    proof.className = "project-proof";
    proof.innerHTML = `<span>${item.gallery.length} verified screenshots</span><span>${item.files.length} workbook${item.files.length === 1 ? "" : "s"}</span>`;
    const link = document.createElement("span");
    link.className = "case-link";
    link.textContent = "View case study →";
    card.querySelector(".copy").append(proof, link);
    const openCard = () => {
      activeCard = card;
      renderCaseStudy(key);
    };
    card.addEventListener("click", openCard);
    card.addEventListener("keydown", event => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        openCard();
      }
    });
  });

  dialog.querySelector(".case-close").addEventListener("click", closeCaseStudy);
  dialog.querySelector(".case-prev").addEventListener("click", () => openAdjacent(-1));
  dialog.querySelector(".case-next").addEventListener("click", () => openAdjacent(1));
  dialog.addEventListener("cancel", event => {
    event.preventDefault();
    if (viewer.classList.contains("open")) closeViewer();
    else closeCaseStudy();
  });
  viewer.querySelector(".viewer-close").addEventListener("click", closeViewer);
  viewer.addEventListener("click", event => { if (event.target === viewer) closeViewer(); });
  document.addEventListener("keydown", event => { if (event.key === "Escape" && viewer.classList.contains("open")) closeViewer(); });
  window.addEventListener("popstate", () => {
    const key = location.hash.startsWith("#case-") ? location.hash.slice(6) : "";
    if (projects[key]) renderCaseStudy(key, false);
    else if (dialog.open) closeCaseStudy(false);
  });

  const initialKey = location.hash.startsWith("#case-") ? location.hash.slice(6) : "";
  if (projects[initialKey]) renderCaseStudy(initialKey, false);
});
