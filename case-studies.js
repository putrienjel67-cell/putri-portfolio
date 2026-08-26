document.addEventListener("DOMContentLoaded", () => {
  const projects = window.projectCaseStudies || {};
  const projectKeys = Object.keys(projects);
  const selectedKeys = ["proj-003", "proj-010", "proj-002"];
  const announcer = document.querySelector("[data-announcer]");
  const menuButton = document.querySelector(".menu-button");
  const siteNav = document.querySelector(".site-nav");
  let activeProjectKey = "";
  let projectTrigger = null;
  let lightboxItems = [];
  let lightboxIndex = 0;
  let lightboxTrigger = null;

  const escapeHtml = value => String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");

  const evidenceCaption = filename => filename
    .replace(/\.png$/i, "")
    .replace(/^EV-\d+[A-C]?_?/i, "")
    .replaceAll("_", " ");

  const previewPath = key => `assets/p${key.slice(-2)}.png`;
  const projectHash = key => `#case-${key}`;

  function announce(message) {
    if (announcer) announcer.textContent = message;
  }

  function renderSelectedWork() {
    const target = document.querySelector("[data-selected-projects]");
    if (!target) return;
    target.innerHTML = selectedKeys.map(key => {
      const item = projects[key];
      if (!item) return "";
      return `
        <article class="selected-project">
          <a class="selected-media" href="${projectHash(key)}" data-project-link="${key}" aria-label="View case study: ${escapeHtml(item.name)}">
            <img src="${previewPath(key)}" width="1600" height="900" loading="eager" alt="${escapeHtml(item.name)} project evidence preview">
          </a>
          <div class="selected-copy">
            <div class="project-meta"><span>${escapeHtml(item.id)}</span><span>${escapeHtml(item.category)}</span></div>
            <h3>${escapeHtml(item.name)}</h3>
            <p>${escapeHtml(item.summary)}</p>
            <a class="text-link" href="${projectHash(key)}" data-project-link="${key}">View Case Study<span aria-hidden="true"> →</span></a>
          </div>
        </article>`;
    }).join("");
  }

  function renderProjectIndex() {
    const target = document.querySelector("[data-project-index]");
    if (!target) return;
    target.innerHTML = projectKeys.map(key => {
      const item = projects[key];
      return `
        <a class="project-row" href="${projectHash(key)}" data-project-link="${key}">
          <span class="project-number">${escapeHtml(item.id.replace("PROJ-", ""))}</span>
          <span class="project-thumb"><img src="${previewPath(key)}" width="320" height="240" loading="lazy" alt=""></span>
          <span>
            <span class="project-title">${escapeHtml(item.name)}</span>
            <span class="project-category">${escapeHtml(item.category)}</span>
            <span class="project-purpose">${escapeHtml(item.summary)}</span>
          </span>
        </a>`;
    }).join("");
  }

  const caseDialog = document.createElement("dialog");
  caseDialog.className = "case-dialog";
  caseDialog.setAttribute("aria-labelledby", "case-title");
  caseDialog.innerHTML = `
    <div class="case-shell">
      <nav class="case-topbar" aria-label="Case study navigation">
        <button type="button" class="case-close">Back to Projects</button>
        <span class="case-progress" aria-live="polite"></span>
        <div class="case-top-actions">
          <button type="button" class="case-previous">Previous</button>
          <button type="button" class="case-next">Next</button>
        </div>
      </nav>
      <div class="case-render"></div>
    </div>`;
  document.body.append(caseDialog);

  const lightbox = document.createElement("dialog");
  lightbox.className = "lightbox";
  lightbox.setAttribute("aria-labelledby", "lightbox-caption");
  lightbox.innerHTML = `
    <div class="lightbox-layout">
      <div class="lightbox-bar">
        <button type="button" class="lightbox-previous">Previous image</button>
        <span class="lightbox-count" aria-live="polite"></span>
        <button type="button" class="lightbox-close">Close image</button>
        <button type="button" class="lightbox-next">Next image</button>
      </div>
      <div class="lightbox-media"><img alt=""></div>
      <p class="lightbox-caption" id="lightbox-caption"></p>
    </div>`;
  document.body.append(lightbox);

  function listMarkup(items, className = "case-list") {
    return `<ul class="${className}">${items.map(item => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`;
  }

  function tagsMarkup(items) {
    return `<div class="tag-list">${items.map(item => `<span>${escapeHtml(item)}</span>`).join("")}</div>`;
  }

  function groupEvidence(item) {
    const groups = { "Input / Before": [], "Process / Checks": [], "Output / Result": [] };
    const outputPattern = /Dashboard|Queue|Summary|SOP|Template|Notes|Handoff|Checklist|Plan|Tracker|Master_Customer|Cleaned_Data_After/i;
    const inputPattern = /Raw|Source|Statement|Registry|Reference/i;
    item.gallery.forEach(filename => {
      if (inputPattern.test(filename)) groups["Input / Before"].push(filename);
      else if (outputPattern.test(filename)) groups["Output / Result"].push(filename);
      else groups["Process / Checks"].push(filename);
    });
    return Object.entries(groups).filter(([, files]) => files.length);
  }

  function evidenceMarkup(key, item) {
    let number = 0;
    return groupEvidence(item).map(([label, files]) => `
      <section class="evidence-group" aria-labelledby="${key}-${label.replaceAll(/[^a-z]+/gi, "-").toLowerCase()}">
        <div class="evidence-group-title">
          <h4 id="${key}-${label.replaceAll(/[^a-z]+/gi, "-").toLowerCase()}">${escapeHtml(label)}</h4>
          <span>${files.length} screenshot${files.length === 1 ? "" : "s"}</span>
        </div>
        <div class="evidence-grid">
          ${files.map(filename => {
            const currentNumber = ++number;
            const src = `assets/projects/${key}/${filename}`;
            const caption = evidenceCaption(filename);
            return `
              <figure class="evidence-figure">
                <button class="evidence-button" type="button" data-image="${src}" data-caption="${escapeHtml(item.id)} evidence: ${escapeHtml(caption)}" aria-label="Open screenshot: ${escapeHtml(caption)}">
                  <img src="${src}" width="1600" height="1000" loading="lazy" alt="${escapeHtml(item.id)} evidence: ${escapeHtml(caption)}">
                </button>
                <figcaption><span>${String(currentNumber).padStart(2, "0")}</span>${escapeHtml(caption)}</figcaption>
              </figure>`;
          }).join("")}
        </div>
      </section>`).join("");
  }

  function downloadsMarkup(item) {
    return item.files.map(file => `
      <article class="download-item">
        <div>
          <p class="case-label">${escapeHtml(file.role)}</p>
          <h4>${escapeHtml(file.label)}</h4>
          <p>${escapeHtml(file.description)}</p>
        </div>
        <a class="button button-secondary" href="${escapeHtml(file.path)}" download>Download Workbook</a>
      </article>`).join("");
  }

  function renderCaseStudy(key, options = {}) {
    const item = projects[key];
    if (!item) return;
    activeProjectKey = key;
    const index = projectKeys.indexOf(key);
    const renderTarget = caseDialog.querySelector(".case-render");
    renderTarget.innerHTML = `
      <header class="case-hero">
        <div class="case-hero-grid">
          <div>
            <p class="case-kicker">${escapeHtml(item.id)} | ${escapeHtml(item.category)}</p>
            <h2 id="case-title">${escapeHtml(item.name)}</h2>
            <p class="case-summary">${escapeHtml(item.summary)}</p>
          </div>
          <dl class="case-facts">
            <div><dt>Evidence</dt><dd>${item.gallery.length} screenshots</dd></div>
            <div><dt>Downloads</dt><dd>${item.files.length} workbook${item.files.length === 1 ? "" : "s"}</dd></div>
            <div><dt>Tools</dt><dd>${escapeHtml(item.tools.slice(0, 3).join(", "))}</dd></div>
          </dl>
        </div>
        <p class="case-disclosure">Independent practice simulation using fictional data. Results describe the workbook dataset and workflow output, not paid client impact.</p>
      </header>
      <main class="case-main">
        <div class="case-overview">
          <section class="case-block"><p class="case-label">Problem</p><h3>What needed attention</h3><p>${escapeHtml(item.problem)}</p></section>
          <section class="case-block"><p class="case-label">Input</p><h3>Data and working scope</h3><p>${escapeHtml(item.data)}</p></section>
        </div>
        <section class="case-row"><h3>My Work</h3>${listMarkup(item.work)}</section>
        <section class="case-row"><h3>Process</h3>${listMarkup(item.workflow, "case-list workflow-list")}</section>
        <section class="case-row"><h3>Checks / QA</h3>${listMarkup(item.qa)}</section>
        <section class="case-row"><h3>Exceptions</h3>${listMarkup(item.exceptions)}</section>
        <section class="case-row"><h3>Result</h3><p class="case-result">${escapeHtml(item.result)}</p></section>
        <section class="case-row"><h3>Skills Shown</h3>${tagsMarkup(item.skills)}</section>
        <section class="case-row"><h3>Tools Used</h3>${tagsMarkup(item.tools)}</section>
        <section class="evidence-section" aria-labelledby="evidence-title">
          <div class="evidence-heading">
            <p class="case-label">Evidence</p>
            <h3 id="evidence-title">See the work from input to output.</h3>
            <p>Open any screenshot for a full-size view. Evidence is grouped by its role in the workflow.</p>
          </div>
          ${evidenceMarkup(key, item)}
        </section>
        <section class="downloads-section" aria-labelledby="downloads-title">
          <div class="downloads-heading">
            <p class="case-label">Downloads</p>
            <h3 id="downloads-title">Project workbooks</h3>
            <p>Files found in the repository and verified against this project. Screenshots remain the primary evidence.</p>
          </div>
          <div class="download-list">${downloadsMarkup(item)}</div>
        </section>
        <nav class="case-bottom-nav" aria-label="Browse case studies">
          <button type="button" class="case-previous" ${index === 0 ? "disabled" : ""}>Previous Case Study</button>
          <span>${String(index + 1).padStart(2, "0")} / ${String(projectKeys.length).padStart(2, "0")}</span>
          <button type="button" class="case-next" ${index === projectKeys.length - 1 ? "disabled" : ""}>Next Case Study</button>
        </nav>
      </main>`;

    caseDialog.querySelector(".case-progress").textContent = `${item.id} of ${projectKeys.length}`;
    caseDialog.querySelectorAll(".case-previous").forEach(button => { button.disabled = index === 0; });
    caseDialog.querySelectorAll(".case-next").forEach(button => { button.disabled = index === projectKeys.length - 1; });
    renderTarget.querySelectorAll(".evidence-button").forEach(button => button.addEventListener("click", () => openLightbox(button)));
    renderTarget.querySelectorAll(".evidence-button img").forEach(image => image.addEventListener("error", () => {
      const button = image.closest(".evidence-button");
      button.classList.add("image-error");
      button.disabled = true;
      button.textContent = "Screenshot could not be loaded";
    }, { once: true }));
    renderTarget.querySelectorAll(".case-previous").forEach(button => button.addEventListener("click", () => openAdjacent(-1)));
    renderTarget.querySelectorAll(".case-next").forEach(button => button.addEventListener("click", () => openAdjacent(1)));

    if (!caseDialog.open) caseDialog.showModal();
    caseDialog.scrollTop = 0;
    document.body.classList.add("modal-open");
    if (!options.fromRoute) history.pushState({ project: key }, "", projectHash(key));
    caseDialog.querySelector(".case-close").focus();
    announce(`${item.name} case study opened`);
  }

  function closeCaseStudy(options = {}) {
    if (lightbox.open) lightbox.close();
    if (caseDialog.open) caseDialog.close();
    document.body.classList.remove("modal-open");
    activeProjectKey = "";
    if (!options.fromRoute) history.pushState(null, "", "#projects");
    const returnTarget = projectTrigger || document.querySelector("#projects");
    projectTrigger = null;
    if (returnTarget instanceof HTMLElement) returnTarget.focus({ preventScroll: true });
    if (!options.fromRoute) document.querySelector("#projects")?.scrollIntoView({ block: "start" });
    announce("Case study closed");
  }

  function openAdjacent(direction) {
    const nextKey = projectKeys[projectKeys.indexOf(activeProjectKey) + direction];
    if (nextKey) renderCaseStudy(nextKey);
  }

  function openLightbox(button) {
    lightboxItems = [...caseDialog.querySelectorAll(".evidence-button:not(:disabled)")];
    lightboxIndex = lightboxItems.indexOf(button);
    lightboxTrigger = button;
    updateLightbox();
    lightbox.showModal();
    lightbox.querySelector(".lightbox-close").focus();
    announce("Screenshot preview opened");
  }

  function updateLightbox() {
    const item = lightboxItems[lightboxIndex];
    if (!item) return;
    const image = lightbox.querySelector("img");
    const caption = item.dataset.caption;
    image.src = item.dataset.image;
    image.alt = caption;
    lightbox.querySelector(".lightbox-caption").textContent = caption;
    lightbox.querySelector(".lightbox-previous").disabled = lightboxIndex === 0;
    lightbox.querySelector(".lightbox-next").disabled = lightboxIndex === lightboxItems.length - 1;
    lightbox.querySelector(".lightbox-count").textContent = `${lightboxIndex + 1} / ${lightboxItems.length}`;
  }

  function moveLightbox(direction) {
    const nextIndex = lightboxIndex + direction;
    if (nextIndex >= 0 && nextIndex < lightboxItems.length) {
      lightboxIndex = nextIndex;
      updateLightbox();
    }
  }

  function closeLightbox() {
    if (lightbox.open) lightbox.close();
    const image = lightbox.querySelector("img");
    image.removeAttribute("src");
    lightboxTrigger?.focus({ preventScroll: true });
    lightboxTrigger = null;
    announce("Screenshot preview closed");
  }

  function handleRoute() {
    const key = location.hash.startsWith("#case-") ? location.hash.slice(6) : "";
    if (projects[key]) renderCaseStudy(key, { fromRoute: true });
    else if (caseDialog.open) closeCaseStudy({ fromRoute: true });
  }

  renderSelectedWork();
  renderProjectIndex();

  document.querySelectorAll("[data-project-link]").forEach(link => link.addEventListener("click", event => {
    event.preventDefault();
    projectTrigger = link;
    const key = link.dataset.projectLink;
    renderCaseStudy(key);
  }));

  menuButton?.addEventListener("click", () => {
    const open = menuButton.getAttribute("aria-expanded") === "true";
    menuButton.setAttribute("aria-expanded", String(!open));
    siteNav?.classList.toggle("open", !open);
  });
  siteNav?.querySelectorAll("a").forEach(link => link.addEventListener("click", () => {
    menuButton?.setAttribute("aria-expanded", "false");
    siteNav.classList.remove("open");
  }));

  caseDialog.querySelector(".case-close").addEventListener("click", () => closeCaseStudy());
  caseDialog.querySelector(".case-previous").addEventListener("click", () => openAdjacent(-1));
  caseDialog.querySelector(".case-next").addEventListener("click", () => openAdjacent(1));
  caseDialog.addEventListener("cancel", event => {
    event.preventDefault();
    if (lightbox.open) closeLightbox();
    else closeCaseStudy();
  });
  lightbox.querySelector(".lightbox-close").addEventListener("click", closeLightbox);
  lightbox.querySelector(".lightbox-previous").addEventListener("click", () => moveLightbox(-1));
  lightbox.querySelector(".lightbox-next").addEventListener("click", () => moveLightbox(1));
  lightbox.addEventListener("cancel", event => { event.preventDefault(); closeLightbox(); });
  document.addEventListener("keydown", event => {
    if (!lightbox.open) return;
    if (event.key === "ArrowLeft") moveLightbox(-1);
    if (event.key === "ArrowRight") moveLightbox(1);
  });
  window.addEventListener("popstate", handleRoute);
  window.addEventListener("hashchange", handleRoute);
  handleRoute();
});
