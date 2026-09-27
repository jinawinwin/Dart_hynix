(() => {
  const data = window.DASHBOARD_DATA || { rows: [], generated_at: null };
  const rows = data.rows || [];
  const annual = rows.filter(row => row.category === "annual").sort((a,b) => a.year - b.year);
  const latest = annual.at(-1) || rows[0];
  const amount = value => value == null ? "—" : (value / 1e12).toLocaleString("ko-KR", {maximumFractionDigits: 1});
  const eok = value => value == null ? "—" : Math.round(value / 1e8).toLocaleString("ko-KR");
  const pct = value => value == null ? "—" : `${Number(value).toLocaleString("ko-KR", {maximumFractionDigits: 2})}%`;
  const updated = data.generated_at ? new Date(data.generated_at).toLocaleString("ko-KR", {dateStyle:"long",timeStyle:"short"}) : "갱신 기록 없음";
  document.querySelector("#updatedAt").textContent = `최근 생성 ${updated}`;
  document.querySelector("#latestPeriod").textContent = latest ? `${latest.year} · ${latest.fs_div === "CFS" ? "연결" : "별도"}` : "데이터 대기 중";

  const metrics = latest ? [
    ["매출액", amount(latest.revenue), "조원", "연간 누적", "#17191d"],
    ["영업이익", amount(latest.operating_profit), "조원", `영업이익률 ${pct(latest.operating_margin_pct)}`, "#ed1c24"],
    ["당기순이익", amount(latest.net_income), "조원", `순이익률 ${pct(latest.net_margin_pct)}`, "#ff7a1a"],
    ["부채비율", latest.debt_ratio_pct == null ? "—" : Number(latest.debt_ratio_pct).toLocaleString("ko-KR"), "%", "부채 ÷ 자본", "#3856d6"],
  ] : [];
  document.querySelector("#summaryCards").innerHTML = metrics.length ? metrics.map(([label,value,unit,note,color]) => `<article class="metric-card" style="--accent:${color}"><div class="metric-label">${label}</div><div class="metric-value">${value}<span class="metric-unit">${unit}</span></div><div class="metric-note">${note}</div></article>`).join("") : `<p class="empty">첫 수집이 완료되면 핵심 지표가 표시됩니다.</p>`;

  function lineChart(target, series, colors, formatter) {
    const el = document.querySelector(target);
    if (!annual.length) { el.innerHTML = `<p class="empty">연간 데이터가 없습니다.</p>`; return; }
    const width=640,height=270,pad={l:38,r:16,t:16,b:32};
    const values=series.flatMap(key=>annual.map(row=>row[key]).filter(v=>v!=null));
    const min=Math.min(0,...values), max=Math.max(1,...values), span=max-min || 1;
    const x=i=>pad.l+(annual.length===1?(width-pad.l-pad.r)/2:i*(width-pad.l-pad.r)/(annual.length-1));
    const y=v=>pad.t+(max-v)*(height-pad.t-pad.b)/span;
    const grid=[0,.25,.5,.75,1].map(t=>{const yy=pad.t+t*(height-pad.t-pad.b);const value=max-t*span;return `<line class="axis" x1="${pad.l}" y1="${yy}" x2="${width-pad.r}" y2="${yy}"/><text class="axis-label" x="${pad.l-7}" y="${yy+3}" text-anchor="end">${formatter(value)}</text>`}).join("");
    const years=annual.map((row,i)=>`<text class="axis-label" x="${x(i)}" y="${height-8}" text-anchor="middle">${row.year}</text>`).join("");
    const lines=series.map((key,s)=>{const points=annual.map((row,i)=>row[key]==null?null:[x(i),y(row[key])]).filter(Boolean);return `<polyline class="chart-line" stroke="${colors[s]}" points="${points.map(p=>p.join(",")).join(" ")}"/>${points.map(p=>`<circle class="chart-dot" fill="${colors[s]}" cx="${p[0]}" cy="${p[1]}" r="3.5"/>`).join("")}`}).join("");
    el.innerHTML=`<svg viewBox="0 0 ${width} ${height}" preserveAspectRatio="none">${grid}${years}${lines}</svg>`;
  }
  lineChart("#incomeChart",["revenue","operating_profit","net_income"],["#17191d","#ed1c24","#ff7a1a"],v=>`${(v/1e12).toFixed(0)}`);
  lineChart("#ratioChart",["operating_margin_pct","debt_ratio_pct"],["#00866e","#3856d6"],v=>`${v.toFixed(0)}%`);

  const categories=["annual","half-year","quarterly"];
  categories.forEach(category=>document.querySelector(`#${category}Count`).textContent=rows.filter(row=>row.category===category).length);
  const tbody=document.querySelector("#financialTable"),empty=document.querySelector("#emptyState");
  function renderTable(category){
    const selected=rows.filter(row=>row.category===category).sort((a,b)=>b.year-a.year||b.period_order-a.period_order);
    empty.hidden=selected.length>0;document.querySelector(".table-shell").hidden=selected.length===0;
    tbody.innerHTML=selected.map(row=>`<tr><td>${row.year}</td><td><span class="report-tag">${row.report_name} · ${row.fs_div}</span></td><td>${eok(row.revenue)}</td><td>${eok(row.operating_profit)}</td><td>${eok(row.net_income)}</td><td>${eok(row.assets)}</td><td>${eok(row.equity)}</td><td>${pct(row.operating_margin_pct)}</td><td>${pct(row.debt_ratio_pct)}</td></tr>`).join("");
  }
  document.querySelectorAll("[role=tab]").forEach(button=>button.addEventListener("click",()=>{document.querySelectorAll("[role=tab]").forEach(tab=>tab.setAttribute("aria-selected",String(tab===button)));renderTable(button.dataset.category)}));
  renderTable("annual");
})();
