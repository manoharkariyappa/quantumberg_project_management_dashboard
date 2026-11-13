export function toNumber(value) {
  if (value === null || value === undefined || value === "") {
    return 0;
  }

  const number = Number(value);

  return Number.isFinite(number) ? number : 0;
}

export function sumRows(rows, field) {
  return (rows || []).reduce((total, row) => total + toNumber(row?.[field]), 0);
}

export function formatCurrency(
  value,
  currency = "INR",
  { maximumFractionDigits = 0, minimumFractionDigits = 0 } = {}
) {
  const amount = toNumber(value);

  try {
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: currency || "INR",
      currencyDisplay: "narrowSymbol",
      minimumFractionDigits,
      maximumFractionDigits,
    }).format(amount);
  } catch {
    return `${currency || "INR"} ${amount.toFixed(maximumFractionDigits)}`;
  }
}

export function formatCompactNumber(value, currency = "INR") {
  const amount = toNumber(value);
  const absolute = Math.abs(amount);

  if (absolute >= 10000000) {
    return `${formatCurrency(amount / 10000000, currency, {
      maximumFractionDigits: 2,
    })} Cr`;
  }

  if (absolute >= 100000) {
    return `${formatCurrency(amount / 100000, currency, {
      maximumFractionDigits: 2,
    })} L`;
  }

  if (absolute >= 1000) {
    return `${formatCurrency(amount / 1000, currency, {
      maximumFractionDigits: 1,
    })} K`;
  }

  return formatCurrency(amount, currency, { maximumFractionDigits: 0 });
}

export function formatNumber(value, maximumFractionDigits = 0) {
  return new Intl.NumberFormat("en-IN", {
    maximumFractionDigits,
  }).format(toNumber(value));
}

export function formatHours(value, maximumFractionDigits = 1) {
  return `${formatNumber(value, maximumFractionDigits)} h`;
}

export function formatPercent(value, maximumFractionDigits = 0) {
  return `${formatNumber(value, maximumFractionDigits)}%`;
}

function parseDate(value) {
  if (!value) {
    return null;
  }

  const date = new Date(`${String(value).slice(0, 10)}T00:00:00`);

  return Number.isNaN(date.getTime()) ? null : date;
}

export function formatDate(value) {
  const date = parseDate(value);

  if (!date) {
    return value || "—";
  }

  return new Intl.DateTimeFormat("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  }).format(date);
}

export function formatTimestamp(value) {
  return new Intl.DateTimeFormat("en-IN", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date());
}
