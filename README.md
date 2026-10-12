* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: "Segoe UI", Arial, sans-serif;
  background: radial-gradient(circle at top, #eff6ff 0%, #f8fafc 35%, #eef2ff 100%);
  color: #0f172a;
}

.page-shell {
  max-width: 1280px;
  margin: 0 auto;
  padding: 32px 22px 60px;
}

.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 18px;
  background: linear-gradient(135deg, #0f172a 0%, #1d4ed8 100%);
  border-radius: 22px;
  padding: 24px 28px;
  box-shadow: 0 20px 40px rgba(15, 23, 42, 0.12);
}

.brand-wrap {
  display: flex;
  align-items: center;
  gap: 18px;
}

.brand-mark {
  width: 56px;
  height: 56px;
  display: grid;
  place-items: center;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.14);
  border: 1px solid rgba(255, 255, 255, 0.2);
  font-size: 1.8rem;
  font-weight: 700;
  color: white;
}

.eyebrow,
.kicker {
  margin: 0 0 8px;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-size: 0.7rem;
  opacity: 0.8;
}

h1 {
  margin: 0;
  font-size: clamp(1.8rem, 3vw, 2.5rem);
  color: white;
}

.menu-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.primary-btn,
.secondary-btn,
.ghost-btn {
  border-radius: 12px;
  padding: 11px 18px;
  border: none;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.25s ease;
}

.primary-btn {
  background: white;
  color: #0f172a;
}

.secondary-btn {
  background: rgba(255, 255, 255, 0.08);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.ghost-btn {
  background: rgba(255, 255, 255, 0.08);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.15);
}

.primary-btn:hover,
.secondary-btn:hover,
.ghost-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 25px rgba(15, 23, 42, 0.12);
}

.content-grid {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: 24px;
  margin-top: 24px;
}

.panel {
  background: rgba(255, 255, 255, 0.72);
  backdrop-filter: blur(4px);
  border: 1px solid rgba(226, 232, 240, 0.8);
  border-radius: 22px;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.04);
  padding: 24px;
}

.hero-panel {
  min-height: 170px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  background: linear-gradient(135deg, rgba(14, 116, 144, 0.10), rgba(37, 99, 235, 0.18));
}

.hero-panel h2 {
  margin: 0;
  font-size: clamp(1.5rem, 2vw, 2.1rem);
  line-height: 1.25;
}

.hero-meta {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  color: #475569;
  font-size: 0.85rem;
  flex-wrap: wrap;
}

.cards {
  display: grid;
  grid-template-columns: repeat(4, minmax(150px, 1fr));
  gap: 18px;
  grid-column: 1 / -1;
}

.card {
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(226, 232, 240, 0.8);
  border-radius: 18px;
  padding: 18px 18px 16px;
  box-shadow: 0 8px 22px rgba(15, 23, 42, 0.04);
}

.card .label {
  display: block;
  color: #64748b;
  font-size: 0.72rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.card strong {
  display: block;
  margin-top: 10px;
  font-size: 2.1rem;
  line-height: 1.1;
}

.card small {
  display: block;
  color: #475569;
  margin-top: 6px;
}

.accent-blue { border-top: 4px solid #2563eb; }
.accent-green { border-top: 4px solid #16a34a; }
.accent-red { border-top: 4px solid #dc2626; }
.accent-gold { border-top: 4px solid #d97706; }

.insights-panel,
.chart-panel,
.table-panel {
  grid-column: span 1;
}

.section-head {
  margin-bottom: 16px;
}

.section-head h3 {
  margin: 0;
  font-size: 1.35rem;
}

.insight-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.insight-item {
  display: flex;
  gap: 14px;
  padding: 14px 12px;
  border-radius: 16px;
  border: 1px solid rgba(148, 163, 184, 0.22);
  background: rgba(248, 250, 252, 0.9);
}

.insight-item.positive {
  border-left: 4px solid #16a34a;
}

.insight-item.warning {
  border-left: 4px solid #dc2626;
}

.insight-item.neutral {
  border-left: 4px solid #64748b;
}

.insight-icon {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  display: grid;
  place-items: center;
  font-weight: 800;
  background: rgba(255, 255, 255, 0.7);
}

.insight-item h4 {
  margin: 0 0 6px;
  font-size: 1rem;
}

.insight-item p {
  margin: 0;
  color: #475569;
  line-height: 1.5;
}

.chart-area {
  margin-top: 10px;
}

.bar-row {
  display: grid;
  grid-template-columns: 130px 1fr 80px;
  align-items: center;
  gap: 12px;
  margin-bottom: 14px;
}

.bar-label {
  font-weight: 700;
  color: #334155;
}

.bar-track {
  width: 100%;
  height: 14px;
  background: #e2e8f0;
  border-radius: 999px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 999px;
}

.bar-fill.up { background: linear-gradient(90deg, #22c55e, #16a34a); }
.bar-fill.down { background: linear-gradient(90deg, #f87171, #dc2626); }
.bar-fill.flat { background: linear-gradient(90deg, #94a3b8, #64748b); }

.bar-value {
  text-align: right;
  font-weight: 700;
  color: #334155;
}

.table-panel {
  grid-column: 1 / -1;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
}

th, td {
  border-bottom: 1px solid rgba(226, 232, 240, 0.9);
  padding: 12px 10px;
  text-align: left;
}

thead th {
  background: rgba(248, 250, 252, 0.85);
  color: #475569;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  font-size: 0.75rem;
}

.trend-badge {
  display: inline-block;
  padding: 6px 10px;
  border-radius: 999px;
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.trend-badge.up { background: rgba(22, 163, 74, 0.12); color: #16a34a; }
.trend-badge.down { background: rgba(220, 38, 38, 0.12); color: #dc2626; }
.trend-badge.flat { background: rgba(100, 116, 139, 0.12); color: #475569; }

@media (max-width: 900px) {
  .content-grid {
    grid-template-columns: 1fr;
  }

  .cards {
    grid-template-columns: repeat(2, minmax(150px, 1fr));
  }
}

@media (max-width: 600px) {
  .topbar {
    flex-direction: column;
    align-items: flex-start;
  }

  .menu-actions {
    width: 100%;
    justify-content: flex-start;
  }

  .cards {
    grid-template-columns: 1fr;
  }

  .bar-row {
    grid-template-columns: 1fr;
  }
}
