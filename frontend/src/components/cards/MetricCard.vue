<script setup>
const emit = defineEmits(["select"]);

defineProps({
  title: {
    type: String,
    default: "",
  },
  value: {
    type: [String, Number],
    default: "0",
  },
  subtitle: {
    type: String,
    default: "",
  },
  icon: {
    type: [Object, Function],
    default: null,
  },
  tone: {
    type: String,
    default: "purple",
  },
  loading: {
    type: Boolean,
    default: false,
  },
  clickable: {
    type: Boolean,
    default: false,
  },
});

function openCard() {
  emit("select");
}

function onKeydown(event) {
  if (event.key === "Enter" || event.key === " ") {
    event.preventDefault();
    openCard();
  }
}
</script>

<template>
  <article
    class="kpi-card qb-card"
    :class="{ 'kpi-card--clickable': clickable }"
    :role="clickable ? 'button' : undefined"
    :tabindex="clickable ? 0 : undefined"
    @click="clickable && openCard()"
    @keydown="clickable && onKeydown($event)"
  >
    <div class="kpi-card-main">
      <div class="kpi-card-content">
        <p class="kpi-title">{{ title }}</p>

        <p v-if="loading" class="kpi-value kpi-value--loading">
          <span class="skeleton-block"></span>
        </p>

        <p v-else class="kpi-value">{{ value }}</p>

        <p class="kpi-description">{{ subtitle }}</p>
      </div>

      <div v-if="icon" class="kpi-icon" :class="`kpi-icon-${tone}`">
        <component :is="icon" :size="19" />
      </div>
    </div>

    <div class="kpi-bottom-border"></div>
  </article>
</template>

<style scoped>
.kpi-card {
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-width: 0;
  padding: 12px 14px 10px;
  overflow: hidden;
  background: var(--card-bg, #ffffff);
  border: 1px solid var(--border-color, #e1e6f2);
  border-radius: 11px;
  box-shadow: 0 2px 7px rgb(31 41 55 / 5%);
  transition:
    box-shadow 0.18s ease,
    transform 0.18s ease,
    border-color 0.18s ease;
}

.kpi-card--clickable {
  cursor: pointer;
}

.kpi-card--clickable:hover {
  border-color: #cfc6ea;
  box-shadow: 0 8px 20px rgb(73 59 145 / 12%);
  transform: translateY(-1px);
}

.kpi-card--clickable:focus-visible {
  outline: 2px solid #6040c5;
  outline-offset: 2px;
}

.kpi-card-main {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  justify-content: space-between;
  gap: 10px;
  min-width: 0;
}

.kpi-card-content {
  flex: 1 1 auto;
  min-width: 0;
}

.kpi-title {
  margin: 0;
  color: var(--text-muted, #78809b);
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.2px;
  line-height: 1.5;
  overflow-wrap: break-word;
  text-transform: uppercase;
}

.kpi-value {
  margin: 5px 0 0;
  color: var(--text-color, #17153c);
  font-size: 21px;
  font-weight: 650;
  line-height: 1.3;
  letter-spacing: -0.5px;
  overflow-wrap: anywhere;
}

.kpi-value--loading {
  width: 72%;
  height: 24px;
  margin-top: 7px;
}

.kpi-value--loading .skeleton-block {
  display: block;
  width: 100%;
  height: 100%;
}

.kpi-description {
  margin: 3px 0 0;
  color: var(--text-muted, #78809b);
  font-size: 11px;
  line-height: 1.45;
  overflow-wrap: break-word;
}

.kpi-icon {
  display: flex;
  flex: 0 0 34px;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border-radius: 9px;
}

.kpi-icon-purple {
  color: #6d28d9;
  background: #f3eefe;
}

.kpi-icon-blue {
  color: #2563eb;
  background: #eff6ff;
}

.kpi-icon-green {
  color: #059669;
  background: #ecfdf5;
}

.kpi-icon-orange {
  color: #c2410c;
  background: #fff7ed;
}

.kpi-icon-red {
  color: #be123c;
  background: #fff1f2;
}

.kpi-icon-teal {
  color: #0f766e;
  background: #ecfdf5;
}

.kpi-bottom-border {
  position: absolute;
  right: 0;
  bottom: 0;
  left: 0;
  height: 3px;
  background: linear-gradient(90deg, #493b91, #c43f9d);
}

@media (max-width: 600px) {
  .kpi-card {
    padding: 13px;
  }

  .kpi-value {
    font-size: 21px;
  }
}
</style>
