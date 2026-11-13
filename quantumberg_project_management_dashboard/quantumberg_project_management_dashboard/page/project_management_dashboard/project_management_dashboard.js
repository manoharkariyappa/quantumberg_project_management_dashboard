frappe.pages["project-management-dashboard"].on_page_load = function (wrapper) {
  const page = frappe.ui.make_app_page({
    parent: wrapper,
    title: "Project Management Dashboard",
    single_column: true,
  });

  page.main.html(`
    <div
      id="quantumberg-project-management-dashboard-root"
      style="width:100%; min-height:80vh;"
    >
      <div style="padding:24px;color:#64748b;">
        Loading Project Management Dashboard...
      </div>
    </div>
  `);

  const root = page.main.find(
    "#quantumberg-project-management-dashboard-root"
  )[0];

  const assetBase =
    "/assets/quantumberg_project_management_dashboard/dashboard";
  const cssPath = `${assetBase}/index.css`;
  const jsPath = `${assetBase}/index.js`;
  const versionPath = `${assetBase}/version.json`;

  async function getAssetVersion() {
    try {
      const response = await fetch(versionPath, {
        cache: "no-store",
        credentials: "same-origin",
      });

      if (!response.ok) {
        return String(Date.now());
      }

      const data = await response.json();

      return data?.version ? String(data.version) : String(Date.now());
    } catch (error) {
      return String(Date.now());
    }
  }

  function withVersion(path, version) {
    return `${path}?v=${encodeURIComponent(version)}`;
  }

  function loadCSS(href) {
    let link = document.querySelector(
      'link[data-quantumberg-project-management-dashboard="css"]'
    );

    if (link && link.getAttribute("href") === href) {
      return Promise.resolve();
    }

    if (link) {
      link.remove();
    }

    link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = href;
    link.dataset.quantumbergProjectManagementDashboard = "css";
    document.head.appendChild(link);

    return new Promise((resolve, reject) => {
      link.onload = () => resolve();
      link.onerror = () => {
        reject(new Error("Failed to load Project Management Dashboard CSS"));
      };
    });
  }

  function loadJS(src) {
    const existing = document.querySelector(
      'script[data-quantumberg-project-management-dashboard="js"]'
    );

    if (
      existing &&
      existing.getAttribute("src") === src &&
      window.QuantumbergProjectManagementDashboard
    ) {
      return Promise.resolve();
    }

    if (existing) {
      existing.remove();
      window.QuantumbergProjectManagementDashboard = undefined;
    }

    const script = document.createElement("script");
    script.src = src;
    script.dataset.quantumbergProjectManagementDashboard = "js";
    document.body.appendChild(script);

    return new Promise((resolve, reject) => {
      script.onload = () => resolve();
      script.onerror = () => {
        reject(
          new Error("Failed to load Project Management Dashboard JavaScript")
        );
      };
    });
  }

  async function initializeDashboard() {
    try {
      const version = await getAssetVersion();

      await loadCSS(withVersion(cssPath, version));
      await loadJS(withVersion(jsPath, version));

      const dashboard = window.QuantumbergProjectManagementDashboard;

      if (!dashboard || typeof dashboard.mount !== "function") {
        throw new Error(
          "Vue mount function is missing. Check frontend/src/main.js."
        );
      }

      dashboard.mount(root);
    } catch (error) {
      console.error("Project Management Dashboard initialization failed:", error);

      root.innerHTML = `
        <div style="
          margin:20px;
          padding:20px;
          background:#fff1f2;
          color:#be123c;
          border-radius:8px;
        ">
          <h3>Unable to load Project Management Dashboard</h3>
          <p>${frappe.utils.escape_html(error.message || String(error))}</p>
          <p>Check the browser Console for details.</p>
        </div>
      `;
    }
  }

  initializeDashboard();
};
