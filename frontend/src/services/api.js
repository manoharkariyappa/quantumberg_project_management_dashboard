const API_METHOD = "quantumberg_project_management_dashboard.api.get_dashboard_data";

function getFrappe() {
  return window.frappe;
}

function normalizeError(error) {
  if (!error) {
    return "Request failed";
  }

  if (typeof error === "string") {
    return error;
  }

  const response = error.responseJSON || error;
  const serverMessages = response?._server_messages;

  if (serverMessages) {
    try {
      const messages = JSON.parse(serverMessages);
      const first = JSON.parse(messages[0]);
      const message = first?.message || messages[0];

      if (message) {
        return String(message).replace(/<[^>]+>/g, " ").trim();
      }
    } catch {
      return String(serverMessages);
    }
  }

  return (
    response?.exception ||
    response?.message ||
    error.message ||
    "Request failed"
  );
}

function callViaFrappe(method, args) {
  return new Promise((resolve, reject) => {
    getFrappe().call({
      method,
      args,
      type: "POST",
      callback: (response) => resolve(response?.message),
      error: (error) => reject(new Error(normalizeError(error))),
    });
  });
}

async function callViaFetch(method, args) {
  const headers = {
    Accept: "application/json",
    "Content-Type": "application/json",
  };

  if (window.csrf_token) {
    headers["X-Frappe-CSRF-Token"] = window.csrf_token;
  }

  const response = await fetch(`/api/method/${method}`, {
    method: "POST",
    credentials: "same-origin",
    headers,
    body: JSON.stringify(args || {}),
  });

  if (!response.ok) {
    throw new Error(`Dashboard API returned HTTP ${response.status}`);
  }

  const result = await response.json();

  if (result.exc) {
    throw new Error("Frappe could not load the dashboard data.");
  }

  return result.message;
}

export function getDashboardData(args = {}) {
  if (getFrappe()?.call) {
    return callViaFrappe(API_METHOD, args);
  }

  return callViaFetch(API_METHOD, args);
}

export function openDocument(doctype, name) {
  if (!doctype || !name) {
    return;
  }

  if (getFrappe()?.set_route) {
    getFrappe().set_route("Form", doctype, name);
    return;
  }

  window.location.href = `/app/${encodeURIComponent(
    String(doctype).toLowerCase().replace(/\s+/g, "-")
  )}/${encodeURIComponent(name)}`;
}

export function openList(doctype, filters = null) {
  if (!doctype) {
    return;
  }

  if (getFrappe()?.set_route) {
    getFrappe().route_options =
      filters && Object.keys(filters).length ? filters : null;
    getFrappe().set_route("List", doctype);
    return;
  }

  window.location.href = `/app/${encodeURIComponent(
    String(doctype).toLowerCase().replace(/\s+/g, "-")
  )}`;
}

export function openNewDocument(doctype) {
  if (!doctype) {
    return;
  }

  if (getFrappe()?.new_doc) {
    getFrappe().new_doc(doctype);
    return;
  }

  window.location.href = `/app/${encodeURIComponent(
    String(doctype).toLowerCase().replace(/\s+/g, "-")
  )}/new`;
}

export function openQueryReport(reportName, filters = {}) {
  if (getFrappe()?.set_route) {
    getFrappe().set_route("query-report", reportName, filters);
    return;
  }

  window.location.href = `/app/query-report/${encodeURIComponent(reportName)}`;
}

export function getToday() {
  return (
    getFrappe()?.datetime?.get_today?.() ||
    new Date().toISOString().slice(0, 10)
  );
}
