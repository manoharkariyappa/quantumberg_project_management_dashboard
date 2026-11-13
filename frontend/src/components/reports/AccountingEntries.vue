<script setup>
import { computed, ref } from "vue";
import {
  ArrowUpRight,
  FileText,
  Search,
} from "lucide-vue-next";
import {
  formatCurrency,
  formatDate,
} from "../../utils/formatters.js";

const props = defineProps({
  entries: {
    type: Array,
    default: () => [],
  },

  loading: {
    type: Boolean,
    default: false,
  },

  currency: {
    type: String,
    default: "INR",
  },
});

defineEmits(["view-all", "open-entry"]);

const searchText = ref("");
const selectedType = ref("");

const filteredEntries = computed(() => {
  const search = searchText.value.trim().toLowerCase();

  return props.entries.filter((entry) => {
    const voucherType = entry.voucher_type || entry.doctype || "";

    const account = entry.account || entry.account_name || "";

    const party = entry.party || entry.party_name || "";

    const searchableText = [
      entry.name,
      voucherType,
      account,
      party,
    ]
      .filter(Boolean)
      .join(" ")
      .toLowerCase();

    const matchesSearch = !search || searchableText.includes(search);

    const matchesType =
      !selectedType.value ||
      voucherType.toLowerCase() === selectedType.value.toLowerCase();

    return matchesSearch && matchesType;
  });
});

const totalDebit = computed(() =>
  props.entries.reduce(
    (total, entry) => total + Number(entry.debit || 0),
    0,
  ),
);

const totalCredit = computed(() =>
  props.entries.reduce(
    (total, entry) => total + Number(entry.credit || 0),
    0,
  ),
);

function voucherType(entry) {
  return entry.voucher_type || entry.doctype || "Voucher";
}

function typeClass(entry) {
  const type = voucherType(entry);

  const classes = {
    "Journal Entry": "type-journal",
    "Payment Entry": "type-payment",
    "Purchase Invoice": "type-purchase",
    "Sales Invoice": "type-sales",
    "Expense Claim": "type-expense",
  };

  return classes[type] || "type-journal";
}

function getStatus(entry) {
  if (entry.docstatus === 1 || entry.status === "Submitted") {
    return "Submitted";
  }

  if (entry.docstatus === 2 || entry.status === "Cancelled") {
    return "Cancelled";
  }

  if (entry.docstatus === 0 || entry.status === "Draft") {
    return "Draft";
  }

  return entry.status || "Unknown";
}

function getStatusClass(entry) {
  const status = getStatus(entry).toLowerCase();

  if (status === "submitted") return "status-submitted";
  if (status === "cancelled") return "status-cancelled";
  if (status === "draft") return "status-draft";

  return "status-neutral";
}
</script>

<template>
  <section class="table-card qb-card">
    <header class="table-card-header">
      <div class="min-w-0">
        <h2>Recent Accounting Entries</h2>
        <p>Financial transactions across projects</p>
      </div>

      <button
        type="button"
        class="dashboard-link"
        @click="$emit('view-all')"
      >
        View All
        <ArrowUpRight :size="13" />
      </button>
    </header>

    <div class="summary-grid">
      <div class="summary-item">
        <span>Total Debit</span>
        <strong>{{ formatCurrency(totalDebit, currency) }}</strong>
      </div>

      <div class="summary-item">
        <span>Total Credit</span>
        <strong>{{ formatCurrency(totalCredit, currency) }}</strong>
      </div>

      <div class="summary-item">
        <span>Transactions</span>
        <strong>{{ entries.length }}</strong>
      </div>
    </div>

    <div class="table-toolbar">
      <label class="table-search">
        <Search :size="13" />
        <input
          v-model="searchText"
          type="search"
          placeholder="Search voucher, account, or party..."
          aria-label="Search accounting entries"
        />
      </label>

      <select v-model="selectedType" class="table-filter">
        <option value="">All Vouchers</option>
        <option value="Journal Entry">Journal Entry</option>
        <option value="Payment Entry">Payment Entry</option>
        <option value="Purchase Invoice">Purchase Invoice</option>
        <option value="Sales Invoice">Sales Invoice</option>
        <option value="Expense Claim">Expense Claim</option>
      </select>
    </div>

    <div v-if="loading" class="table-skeleton">
      <div
        v-for="index in 5"
        :key="index"
        class="skeleton-block table-skeleton-row"
      ></div>
    </div>

    <div v-else-if="filteredEntries.length === 0" class="empty-state">
      No accounting entries found.
    </div>

    <div v-else class="table-scroll">
      <table class="qb-table">
        <thead>
          <tr>
            <th>Voucher</th>
            <th>Posting Date</th>
            <th>Account / Party</th>
            <th class="numeric">Debit</th>
            <th class="numeric">Credit</th>
            <th>Status</th>
          </tr>
        </thead>

        <tbody>
          <tr
            v-for="entry in filteredEntries"
            :key="`${entry.voucher_type || entry.doctype || ''}-${entry.name}`"
            @click="$emit('open-entry', entry)"
          >
            <td>
              <div class="table-doc-cell">
                <span class="table-doc-icon">
                  <FileText :size="13" />
                </span>

                <div class="min-w-0">
                  <span class="table-doc-link">
                    {{ entry.name || "—" }}
                  </span>

                  <small class="table-doc-id">
                    <span class="type-pill" :class="typeClass(entry)">
                      {{ voucherType(entry) }}
                    </span>
                  </small>
                </div>
              </div>
            </td>

            <td class="date-cell">
              {{ formatDate(entry.posting_date) }}
            </td>

            <td>
              <div class="account-cell">
                <span class="account-name">
                  {{
                    entry.account ||
                    entry.account_name ||
                    entry.party ||
                    entry.party_name ||
                    "—"
                  }}
                </span>

                <small v-if="entry.party && entry.account">
                  {{ entry.party }}
                </small>
              </div>
            </td>

            <td class="numeric amount-cell">
              {{ formatCurrency(entry.debit || 0, currency) }}
            </td>

            <td class="numeric amount-cell credit-cell">
              {{ formatCurrency(entry.credit || 0, currency) }}
            </td>

            <td>
              <span class="status-pill" :class="getStatusClass(entry)">
                <span class="status-pill-dot"></span>
                {{ getStatus(entry) }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="!loading && filteredEntries.length" class="table-footer">
      Showing {{ filteredEntries.length }} of {{ entries.length }} entries
    </div>
  </section>
</template>

<style scoped>
.table-card {
  display: flex;
  flex-direction: column;
}

.table-card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 13px 8px;
  border-bottom: 1px solid var(--border-color, #edf0f7);
}

.table-card-header h2 {
  overflow: hidden;
  color: var(--text-color, #17153c);
  text-overflow: ellipsis;
  white-space: nowrap;
}

.table-card-header p {
  margin: 3px 0 0;
  color: var(--text-muted, #78809b);
  font-size: 11px;
  line-height: 1.4;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 9px;
  padding: 12px 15px;
}

.summary-item {
  display: flex;
  flex-direction: column;
  gap: 3px;
  padding: 10px 12px;
  background: var(--subtle-fg, #f8f9fd);
  border-radius: 9px;
}

.summary-item span {
  color: var(--text-muted, #78809b);
  font-size: 10px;
  letter-spacing: 0.25px;
  text-transform: uppercase;
}

.summary-item strong {
  overflow-wrap: anywhere;
  color: var(--text-color, #17153c);
  font-size: 14px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}

.table-toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 0 15px 11px;
}

.table-search {
  display: inline-flex;
  flex: 1 1 160px;
  height: 32px;
  align-items: center;
  gap: 7px;
  padding: 0 10px;
  color: var(--text-muted, #78809b);
  background: var(--card-bg, #ffffff);
  border: 1px solid var(--border-color, #e1e6f2);
  border-radius: 7px;
}

.table-search input {
  min-width: 0;
  flex: 1;
  height: 100%;
  padding: 0;
  color: var(--text-color, #333333);
  font-size: 12px;
  background: transparent;
  border: 0;
  outline: none;
}

.table-search:focus-within {
  border-color: #c4b8ef;
  box-shadow: 0 0 0 3px rgb(96 64 197 / 8%);
}

.table-filter {
  height: 32px;
  min-width: 150px;
  padding: 0 8px;
  color: var(--text-color, #333333);
  font-size: 12px;
  background: var(--card-bg, #ffffff);
  border: 1px solid var(--border-color, #e1e6f2);
  border-radius: 7px;
  outline: none;
}

.table-scroll {
  width: 100%;
  max-height: 264px;
  overflow: auto;
}

.qb-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  white-space: nowrap;
}

.qb-table th {
  padding: 9px 12px;
  color: var(--text-muted, #78809b);
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.25px;
  text-align: left;
  text-transform: uppercase;
  white-space: nowrap;
  background: var(--subtle-fg, #f8f9fd);
  border-bottom: 1px solid var(--border-color, #edf0f7);
}

.qb-table td {
  padding: 9px 12px;
  color: var(--text-color, #333333);
  font-size: 12px;
  vertical-align: middle;
  border-bottom: 1px solid var(--border-color, #f0f2f8);
}

.qb-table tbody tr {
  cursor: pointer;
}

.qb-table tbody tr:last-child td {
  border-bottom: 0;
}

.qb-table tbody tr:hover {
  background: var(--subtle-fg, #fafbff);
}

.numeric {
  text-align: right;
  font-variant-numeric: tabular-nums;
}

.table-doc-cell {
  display: flex;
  align-items: center;
  gap: 9px;
  min-width: 0;
}

.table-doc-icon {
  display: grid;
  flex-shrink: 0;
  width: 28px;
  height: 28px;
  color: #6d28d9;
  font-size: 13px;
  background: #f3eefe;
  border-radius: 8px;
  place-items: center;
}

.table-doc-link {
  overflow: hidden;
  max-width: 170px;
  color: #6040c5;
  font-size: 12px;
  font-weight: 600;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.table-doc-id {
  display: block;
  margin-top: 2px;
}

.type-pill {
  display: inline-flex;
  align-items: center;
  padding: 1px 7px;
  font-size: 9px;
  font-weight: 650;
  white-space: nowrap;
  border-radius: 999px;
}

.type-journal {
  color: #6d28d9;
  background: #f3eefe;
}

.type-payment {
  color: #047857;
  background: #ecfdf5;
}

.type-purchase {
  color: #b45309;
  background: #fffbeb;
}

.type-sales {
  color: #1d4ed8;
  background: #eff6ff;
}

.type-expense {
  color: #be123c;
  background: #fff1f2;
}

.account-cell {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.account-name {
  overflow: hidden;
  max-width: 180px;
  color: var(--text-color, #333333);
  font-size: 12px;
  font-weight: 600;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.account-cell small {
  overflow: hidden;
  max-width: 180px;
  color: var(--text-muted, #78809b);
  font-size: 10px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.amount-cell {
  font-weight: 650;
}

.credit-cell {
  color: #047857;
}

.date-cell {
  color: var(--text-muted, #78809b);
}

.status-pill {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 2px 8px;
  font-size: 10px;
  font-weight: 600;
  line-height: 1.5;
  white-space: nowrap;
  border-radius: 999px;
}

.status-pill-dot {
  flex-shrink: 0;
  width: 6px;
  height: 6px;
  background: currentColor;
  border-radius: 50%;
}

.status-submitted {
  color: #047857;
  background: #ecfdf5;
}

.status-cancelled {
  color: #be123c;
  background: #fff1f2;
}

.status-draft {
  color: #b45309;
  background: #fffbeb;
}

.status-neutral {
  color: #475569;
  background: #f1f5f9;
}

.table-skeleton {
  display: flex;
  flex-direction: column;
  gap: 9px;
  padding: 14px 15px;
}

.table-skeleton-row {
  width: 100%;
  height: 42px;
}

.table-footer {
  padding: 9px 13px;
  color: var(--text-muted, #78809b);
  font-size: 11px;
  border-top: 1px solid var(--border-color, #edf0f7);
}

@media (max-width: 700px) {
  .summary-grid {
    grid-template-columns: 1fr;
  }
}
</style>
