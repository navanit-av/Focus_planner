from flask import Flask, request, jsonify, render_template_string
import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "planner.db"

app = Flask(__name__)

HTML = r"""
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Focus Planner</title>
<style>
:root{
  --bg:#f6f7f9;--surface:#fff;--surface2:#f9fafb;--line:#e5e7eb;
  --text:#111827;--muted:#6b7280;--green:#16a34a;--green-bg:#ecfdf3;
  --red:#dc2626;--red-bg:#fef2f2;--yellow:#d97706;--yellow-bg:#fffbeb;
  --blue:#2563eb;--blue-bg:#eff6ff;--shadow:0 2px 12px rgba(15,23,42,.05)
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--text);
font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
button,input,select{font:inherit}button{cursor:pointer}
button:disabled{opacity:.5;cursor:not-allowed}
.app{max-width:1180px;margin:auto;padding:24px}
.topbar{display:flex;align-items:center;justify-content:space-between;padding:4px 0 22px}
.brand{font-size:19px;font-weight:800;letter-spacing:-.03em}
.brand span{font-weight:500;color:var(--muted)}
.today-chip{background:var(--surface);border:1px solid var(--line);padding:7px 11px;
border-radius:999px;font-size:12px;color:var(--muted)}
.hero{background:var(--surface);border:1px solid var(--line);border-radius:16px;
padding:22px;box-shadow:var(--shadow)}
.hero-row{display:flex;justify-content:space-between;gap:20px;align-items:center}
.eyebrow{text-transform:uppercase;letter-spacing:.12em;color:var(--muted);font-size:10px;font-weight:800}
h1{font-size:32px;letter-spacing:-.045em;margin:6px 0 5px}
.hero p{margin:0;color:var(--muted);font-size:14px}
.streak-chip{background:var(--green-bg);color:var(--green);border:1px solid #bbf7d0;
padding:10px 13px;border-radius:12px;font-weight:800;white-space:nowrap}
.tabs{display:flex;gap:5px;margin-top:20px}
.tab{border:0;background:transparent;color:var(--muted);border-radius:8px;padding:9px 13px;font-weight:700}
.tab.active{background:#111827;color:white}
.section{display:none}.section.active{display:block}
.toolbar{display:flex;justify-content:space-between;align-items:end;gap:14px;margin:24px 0 14px;flex-wrap:wrap}
.toolbar h2{margin:0;font-size:22px;letter-spacing:-.03em}.toolbar p{margin:4px 0 0;color:var(--muted);font-size:13px}
.week-controls{display:flex;align-items:center;gap:7px;flex-wrap:wrap}
.btn{border:1px solid var(--line);background:var(--surface);color:var(--text);border-radius:8px;
padding:8px 11px;font-weight:700;font-size:13px}
.btn:hover{background:var(--surface2)}
.btn.primary{background:#111827;color:white;border-color:#111827}
.btn.green{background:var(--green-bg);color:var(--green);border-color:#bbf7d0}
.btn.danger{background:var(--red-bg);color:var(--red);border-color:#fecaca}
.btn.ghost{background:transparent}
.icon-btn{width:32px;height:32px;padding:0}
.grid{display:grid;gap:14px}.two{grid-template-columns:1.4fr .6fr}
.card{background:var(--surface);border:1px solid var(--line);border-radius:13px;padding:16px;box-shadow:var(--shadow)}
.day-picker{display:flex;gap:7px;overflow:auto;padding:2px 0 12px}
.day-btn{min-width:84px;border:1px solid var(--line);background:var(--surface);color:var(--muted);
border-radius:10px;padding:9px;text-align:left}
.day-btn strong{display:block;color:var(--text);font-size:12px}.day-btn span{font-size:11px}
.day-btn.active{background:#111827;color:white;border-color:#111827}
.day-btn.active strong{color:white}
.day-btn.has-missed{border-color:#fca5a5;background:var(--red-bg)}
.day-btn.has-missed.active{background:#111827;border-color:#111827}
.card-title{display:flex;justify-content:space-between;gap:10px;align-items:flex-start}
.card h3{margin:0;font-size:16px}.small{font-size:12px;color:var(--muted)}
.progress-label{display:flex;justify-content:space-between;font-size:12px;color:var(--muted)}
.progress{height:8px;background:#eef0f2;border-radius:99px;overflow:hidden;margin-top:7px}
.progress>span{display:block;height:100%;background:#111827;width:0;transition:.2s}
.task-stack{display:flex;flex-direction:column;gap:7px}
.task-row{display:grid;grid-template-columns:auto 1fr auto;gap:10px;align-items:center;
padding:11px;border:1px solid var(--line);border-radius:10px;background:var(--surface)}
.task-row.missed{border-color:#fecaca;background:var(--red-bg)}
.task-row.done{background:#fafafa}
.check{width:18px;height:18px;accent-color:#111827}
.task-title{font-weight:700;font-size:13px;line-height:1.3}.task-title.done{text-decoration:line-through;color:#9ca3af}
.task-meta{font-size:11px;color:var(--muted);margin-top:3px}
.status{display:inline-flex;align-items:center;gap:5px;border-radius:999px;padding:4px 7px;font-size:10px;font-weight:800}
.status.completed{background:var(--green-bg);color:var(--green)}
.status.pending{background:var(--yellow-bg);color:var(--yellow)}
.status.missed{background:var(--red-bg);color:var(--red)}
.status.today{background:var(--blue-bg);color:var(--blue)}
.form{display:grid;grid-template-columns:1fr 150px 110px auto;gap:7px}
input,select{background:var(--surface);color:var(--text);border:1px solid var(--line);
border-radius:8px;padding:9px;outline:none;font-size:13px}
input:focus,select:focus{border-color:#9ca3af;box-shadow:0 0 0 3px #f3f4f6}
.empty{border:1px dashed var(--line);border-radius:10px;padding:18px;text-align:center;color:var(--muted);font-size:12px}
.missed-box{border:1px solid #fecaca;background:#fff7f7;border-radius:13px;padding:15px;margin-bottom:14px}
.missed-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px}
.missed-head strong{color:var(--red);font-size:14px}
.section-note{font-size:12px;color:var(--muted)}
.stat-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:14px}
.stat{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:15px;box-shadow:var(--shadow)}
.stat strong{display:block;font-size:25px;letter-spacing:-.04em}.stat span{font-size:11px;color:var(--muted)}
.history{display:flex;flex-direction:column;gap:7px}
.history-row{display:grid;grid-template-columns:110px 1fr 100px 90px;gap:10px;align-items:center;
background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:11px 13px}
.history-date{font-weight:750;font-size:13px}.history-progress{color:var(--muted);font-size:12px}
.week-summary{display:flex;gap:12px;align-items:center;flex-wrap:wrap}
.badge{padding:4px 7px;border:1px solid var(--line);border-radius:999px;font-size:10px;color:var(--muted)}
.week-label{font-weight:800;min-width:180px;text-align:center}
.toast{position:fixed;right:18px;bottom:18px;background:#111827;color:white;padding:11px 14px;
border-radius:9px;font-weight:700;font-size:13px;display:none;z-index:10}
@media(max-width:900px){.two{grid-template-columns:1fr}.form{grid-template-columns:1fr 1fr}.form button{grid-column:span 2}.stat-grid{grid-template-columns:repeat(2,1fr)}}
@media(max-width:600px){.app{padding:13px}.hero-row{align-items:flex-start;flex-direction:column}h1{font-size:28px}
.history-row{grid-template-columns:1fr 1fr}.history-row .status{justify-self:end}}
</style>
</head>
<body>
<div class="app">
  <div class="topbar">
    <div class="brand">FOCUS <span>/ planner</span></div>
    <div id="topToday" class="today-chip"></div>
  </div>

  <header class="hero">
    <div class="hero-row">
      <div>
        <div class="eyebrow">Weekly → daily system</div>
        <h1>Do the work. Keep the streak.</h1>
        <p>Plan your week, choose today's work, and keep a clean history of what actually got done.</p>
      </div>
      <div class="streak-chip">🔥 <span id="heroStreak">0</span> day streak</div>
    </div>
    <div class="tabs">
      <button class="tab active" data-tab="today">Today</button>
      <button class="tab" data-tab="week">Week</button>
      <button class="tab" data-tab="tracker">History & Streak</button>
    </div>
  </header>

  <section id="today" class="section active">
    <div class="toolbar">
      <div><h2>Today's Plan</h2><p id="todaySubtitle">Choose a realistic set of tasks.</p></div>
      <div class="week-controls">
        <button class="btn" onclick="changeDay(-1)">←</button>
        <strong id="dateLabel"></strong>
        <button class="btn" onclick="changeDay(1)">→</button>
        <button class="btn primary" onclick="goToday()">Today</button>
      </div>
    </div>

    <div class="day-picker" id="dayPicker"></div>

    <div id="missedBox"></div>

    <div class="grid two">
      <div class="card">
        <div class="card-title">
          <div><h3>Daily Tasks</h3><div class="small">Complete every task to mark the day complete.</div></div>
          <button id="lockBtn" class="btn primary" onclick="toggleLock()">🔓 Lock</button>
        </div>
        <div id="todayTasks" class="task-stack" style="margin-top:13px"></div>
        <div style="display:grid;grid-template-columns:1fr auto;gap:7px;margin-top:12px">
          <input id="dailyTitle" placeholder="Add a task for today…" onkeydown="if(event.key==='Enter') addDaily()">
          <button id="dailyAddBtn" class="btn primary" onclick="addDaily()">Add</button>
        </div>
        <div style="margin-top:16px">
          <div class="progress-label"><span id="taskProgressText">0 of 0 complete</span><span id="taskProgressPct">0%</span></div>
          <div class="progress"><span id="taskProgress"></span></div>
        </div>
      </div>

      <div>
        <div class="card">
          <div class="card-title">
            <div><h3>Day status</h3><div class="small">Your streak is based on completed daily plans.</div></div>
            <span id="dayStatus" class="status pending">Pending</span>
          </div>
          <div style="font-size:30px;font-weight:850;margin-top:16px" id="dayCompletion">0%</div>
          <div class="small" id="dayCompletionNote">Add tasks to begin.</div>
        </div>

        <div class="card" style="margin-top:14px">
          <div class="card-title"><div><h3>Weekly tasks</h3><div class="small">Pull a weekly task into today.</div></div></div>
          <div id="weeklyPicker" class="task-stack" style="margin-top:12px"></div>
        </div>
      </div>
    </div>
  </section>

  <section id="week" class="section">
    <div class="toolbar">
      <div><h2>Weekly Tasks</h2><p>Keep every task in history. Completed tasks stay visible.</p></div>
      <div class="week-controls">
        <button class="btn" onclick="changeWeek(-1)">← Previous</button>
        <div class="week-label" id="weekLabel"></div>
        <button class="btn" onclick="changeWeek(1)">Next →</button>
        <button class="btn primary" onclick="goCurrentWeek()">This week</button>
      </div>
    </div>

    <div class="card" style="margin-bottom:14px">
      <div class="form">
        <input id="weeklyTitle" placeholder="Add a weekly task…">
        <select id="weeklyQuadrant">
          <option value="doit">Do</option>
          <option value="schedule">Schedule</option>
          <option value="delegate">Delegate</option>
          <option value="eliminate">Eliminate</option>
        </select>
        <select id="weeklyPriority">
          <option value="high">High</option>
          <option value="medium" selected>Medium</option>
          <option value="low">Low</option>
        </select>
        <button class="btn primary" onclick="addWeekly()">Add task</button>
      </div>
    </div>

    <div class="card">
      <div class="card-title">
        <div><h3>All weekly tasks</h3><div class="small">Completed and pending tasks remain in your history.</div></div>
        <div class="week-summary">
          <span id="weeklyCompleted" class="status completed">0 completed</span>
          <span id="weeklyPending" class="status pending">0 pending</span>
        </div>
      </div>
      <div id="weeklyList" class="task-stack" style="margin-top:13px"></div>
    </div>
  </section>

  <section id="tracker" class="section">
    <div class="toolbar">
      <div><h2>History & Streak</h2><p>Track your daily completion instead of Pomodoros.</p></div>
      <button class="btn" onclick="loadTracker()">Refresh</button>
    </div>

    <div class="stat-grid">
      <div class="stat"><strong id="streak">0</strong><span>Current streak</span></div>
      <div class="stat"><strong id="bestStreak">0</strong><span>Best streak</span></div>
      <div class="stat"><strong id="completionRate">0%</strong><span>Completion rate</span></div>
      <div class="stat"><strong id="completedDays">0</strong><span>Completed days</span></div>
    </div>

    <div class="card">
      <div class="card-title">
        <div><h3>Recent days</h3><div class="small">Green = complete · red = missed · yellow = pending</div></div>
      </div>
      <div id="history" class="history" style="margin-top:13px"></div>
    </div>
  </section>
</div>
<div id="toast" class="toast"></div>

<script>
let selectedDate = new Date();
let selectedWeek = new Date();
let locked = false;

const $ = id => document.getElementById(id);
const pad = n => String(n).padStart(2,'0');
const iso = d => `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}`;
const fmt = d => d.toLocaleDateString(undefined,{weekday:'long',month:'long',day:'numeric',year:'numeric'});
const esc = s => String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]));
const startOfWeek = d => {
  const x=new Date(d); const day=x.getDay();
  x.setDate(x.getDate()-(day===0?6:day-1)); x.setHours(0,0,0,0); return x;
};
const endOfWeek = d => {const x=startOfWeek(d);x.setDate(x.getDate()+6);return x;};

async function api(url, options={}) {
  const r=await fetch(url,{headers:{'Content-Type':'application/json'},...options});
  const text=await r.text();
  if(!r.ok){
    let msg=text;
    try{msg=JSON.parse(text).error||text}catch(_){}
    toast(msg||'Request failed');
    throw new Error(msg);
  }
  return text?JSON.parse(text):{};
}
function toast(msg){
  const t=$('toast');t.textContent=msg;t.style.display='block';
  clearTimeout(window.toastTimer);window.toastTimer=setTimeout(()=>t.style.display='none',1800);
}
function showTab(tab){
  document.querySelectorAll('.section').forEach(s=>s.classList.toggle('active',s.id===tab));
  document.querySelectorAll('.tab').forEach(b=>b.classList.toggle('active',b.dataset.tab===tab));
  if(tab==='today')loadDaily();
  if(tab==='week')loadWeekly();
  if(tab==='tracker')loadTracker();
}
document.querySelectorAll('.tab').forEach(b=>b.onclick=()=>showTab(b.dataset.tab));

function setDateUI(){
  $('dateLabel').textContent=fmt(selectedDate);
  $('topToday').textContent=new Date().toLocaleDateString(undefined,{month:'short',day:'numeric',year:'numeric'});
  renderDayPicker();
}
function renderDayPicker(){
  const start=startOfWeek(selectedDate),box=$('dayPicker');box.innerHTML='';
  for(let i=0;i<7;i++){
    const d=new Date(start);d.setDate(start.getDate()+i);
    const ds=iso(d);
    box.innerHTML+=`<button class="day-btn ${ds===iso(selectedDate)?'active':''}" onclick="pickDay('${ds}')">
      <strong>${d.toLocaleDateString(undefined,{weekday:'short'})}</strong>
      <span>${d.toLocaleDateString(undefined,{month:'short',day:'numeric'})}</span>
    </button>`;
  }
}
function pickDay(s){selectedDate=new Date(s+'T00:00:00');setDateUI();loadDaily()}
function goToday(){selectedDate=new Date();setDateUI();loadDaily()}
function changeDay(n){selectedDate.setDate(selectedDate.getDate()+n);setDateUI();loadDaily()}

async function loadDaily(){
  setDateUI();
  const d=iso(selectedDate);
  const data=await api('/api/daily?date='+d);
  locked=!!data.locked;
  $('lockBtn').textContent=locked?'🔒 Unlock':'🔓 Lock';
  $('lockBtn').className=locked?'btn':'btn primary';
  $('dailyTitle').disabled=locked;$('dailyAddBtn').disabled=locked;
  renderMissed(data.missed);
  renderTodayTasks(data.tasks,data.status);
  renderWeeklyPicker(data.weekly);
  updateDayStatus(data);
  loadHeroStreak();
}
function renderMissed(tasks){
  const box=$('missedBox');
  if(!tasks.length){box.innerHTML='';return}
  box.innerHTML=`<div class="missed-box">
    <div class="missed-head">
      <strong>⚠ Missed from yesterday</strong>
      <span class="section-note">These tasks were not completed.</span>
    </div>
    <div class="task-stack">
      ${tasks.map(t=>`<div class="task-row missed">
        <input class="check" type="checkbox" disabled>
        <div><div class="task-title" style="color:var(--red)">${esc(t.title)}</div>
        <div class="task-meta">From ${esc(t.date)}</div></div>
        <button class="btn danger" onclick="carryTask(${t.id})">Move to today</button>
      </div>`).join('')}
    </div>
  </div>`;
}
function renderTodayTasks(tasks,status){
  const box=$('todayTasks');box.innerHTML='';
  if(!tasks.length){
    box.innerHTML='<div class="empty">No tasks for this day. Add tasks below or pull one from your weekly plan.</div>';
  } else {
    tasks.forEach((t,i)=>{
      box.innerHTML+=`<div class="task-row ${t.completed?'done':''}">
        <input class="check" type="checkbox" ${t.completed?'checked':''} onchange="toggleDaily(${t.id},this.checked)">
        <div>
          <div class="task-title ${t.completed?'done':''}">${i+1}. ${esc(t.title)}</div>
          <div class="task-meta">${t.source?'From weekly plan':'Today-only'}${t.quadrant?' · '+esc(t.quadrant):''}</div>
        </div>
        <button class="btn icon-btn" ${locked?'disabled':''} onclick="deleteDaily(${t.id})">×</button>
      </div>`;
    });
  }
  const done=tasks.filter(t=>t.completed).length,total=tasks.length,pct=total?Math.round(done/total*100):0;
  $('taskProgressText').textContent=`${done} of ${total} complete`;
  $('taskProgressPct').textContent=pct+'%';
  $('taskProgress').style.width=pct+'%';
}
function updateDayStatus(data){
  const status=data.status;
  const el=$('dayStatus');
  el.className='status '+(status==='completed'?'completed':status==='missed'?'missed':'pending');
  el.textContent=status==='completed'?'Completed':status==='missed'?'Missed':status==='empty'?'No tasks':'Pending';
  const pct=data.total?Math.round(data.completed/data.total*100):0;
  $('dayCompletion').textContent=pct+'%';
  $('dayCompletionNote').textContent=data.total?`${data.completed} of ${data.total} tasks completed.`:'Add tasks to begin.';
}
function renderWeeklyPicker(rows){
  const box=$('weeklyPicker');box.innerHTML='';
  if(!rows.length){box.innerHTML='<div class="empty">No pending weekly tasks.</div>';return}
  rows.slice(0,8).forEach(t=>{
    box.innerHTML+=`<div class="task-row">
      <span class="status ${t.priority==='high'?'missed':'pending'}">${esc(t.priority)}</span>
      <div><div class="task-title">${esc(t.title)}</div><div class="task-meta">${esc(t.quadrant)}</div></div>
      <button class="btn primary" ${locked?'disabled':''} onclick="addFromWeekly(${t.id})">Add</button>
    </div>`;
  });
}
async function toggleLock(){
  await api('/api/daily/lock',{method:'POST',body:JSON.stringify({date:iso(selectedDate),locked:!locked})});
  loadDaily();toast(!locked?'Day locked':'Day unlocked');
}
async function addDaily(){
  if(locked)return;
  const title=$('dailyTitle').value.trim();if(!title)return;
  await api('/api/daily',{method:'POST',body:JSON.stringify({title,date:iso(selectedDate)})});
  $('dailyTitle').value='';loadDaily();
}
async function addFromWeekly(id){
  if(locked)return;
  await api('/api/daily',{method:'POST',body:JSON.stringify({weekly_id:id,date:iso(selectedDate)})});
  loadDaily();toast('Added to today');
}
async function toggleDaily(id,completed){
  await api('/api/daily/'+id,{method:'PATCH',body:JSON.stringify({completed})});
  loadDaily();
}
async function deleteDaily(id){
  if(locked)return;
  await api('/api/daily/'+id,{method:'DELETE'});loadDaily();
}
async function carryTask(id){
  await api('/api/daily/carry/'+id,{method:'POST',body:JSON.stringify({date:iso(selectedDate)})});
  loadDaily();toast('Task moved to today');
}

function weekRange(){
  const s=startOfWeek(selectedWeek),e=endOfWeek(selectedWeek);
  return `${s.toLocaleDateString(undefined,{month:'short',day:'numeric'})} — ${e.toLocaleDateString(undefined,{month:'short',day:'numeric',year:'numeric'})}`;
}
function updateWeekLabel(){$('weekLabel').textContent=weekRange()}
function changeWeek(n){selectedWeek.setDate(selectedWeek.getDate()+n*7);updateWeekLabel();loadWeekly()}
function goCurrentWeek(){selectedWeek=new Date();updateWeekLabel();loadWeekly()}

async function loadWeekly(){
  updateWeekLabel();
  const data=await api('/api/weekly');
  const completed=data.filter(t=>t.done).length,pending=data.length-completed;
  $('weeklyCompleted').textContent=completed+' completed';
  $('weeklyPending').textContent=pending+' pending';
  const box=$('weeklyList');box.innerHTML='';
  if(!data.length){box.innerHTML='<div class="empty">No weekly tasks yet.</div>';return}
  data.forEach(t=>{
    box.innerHTML+=`<div class="task-row ${t.done?'done':''}">
      <input class="check" type="checkbox" ${t.done?'checked':''} onchange="toggleWeekly(${t.id},this.checked)">
      <div>
        <div class="task-title ${t.done?'done':''}">${esc(t.title)}</div>
        <div class="task-meta">${esc(t.priority)} priority · ${esc(t.quadrant)} · ${t.days_added} days on list</div>
      </div>
      <div style="display:flex;gap:5px;align-items:center">
        <span class="status ${t.done?'completed':'pending'}">${t.done?'Completed':'Pending'}</span>
        <button class="btn primary" onclick="addFromWeeklyFromWeek(${t.id})">Today</button>
        <button class="btn danger icon-btn" onclick="deleteWeekly(${t.id})">×</button>
      </div>
    </div>`;
  });
}
async function addWeekly(){
  const title=$('weeklyTitle').value.trim();if(!title)return;
  await api('/api/weekly',{method:'POST',body:JSON.stringify({
    title,quadrant:$('weeklyQuadrant').value,priority:$('weeklyPriority').value
  })});
  $('weeklyTitle').value='';loadWeekly();toast('Weekly task added');
}
async function toggleWeekly(id,done){
  await api('/api/weekly/'+id,{method:'PATCH',body:JSON.stringify({done})});loadWeekly();
}
async function deleteWeekly(id){
  if(!confirm('Delete this weekly task and its linked daily tasks?'))return;
  await api('/api/weekly/'+id,{method:'DELETE'});loadWeekly();
}
async function addFromWeeklyFromWeek(id){
  await api('/api/daily',{method:'POST',body:JSON.stringify({weekly_id:id,date:iso(selectedDate)})});
  showTab('today');toast('Added to selected day');
}

async function loadTracker(){
  const d=await api('/api/tracker');
  $('streak').textContent=d.streak;
  $('bestStreak').textContent=d.best_streak;
  $('completionRate').textContent=d.completion_rate+'%';
  $('completedDays').textContent=d.completed_days;
  $('heroStreak').textContent=d.streak;
  const box=$('history');box.innerHTML='';
  if(!d.days.length){box.innerHTML='<div class="empty">No daily history yet.</div>';return}
  d.days.forEach(x=>{
    const pct=x.total?Math.round(x.completed/x.total*100):0;
    const status=x.status==='completed'?'completed':x.status==='missed'?'missed':'pending';
    box.innerHTML+=`<div class="history-row">
      <div class="history-date">${esc(x.date_label)}</div>
      <div class="history-progress">${x.completed} / ${x.total} tasks · ${pct}%</div>
      <div class="progress"><span style="width:${pct}%"></span></div>
      <span class="status ${status}">${x.status==='completed'?'Completed':x.status==='missed'?'Missed':'Pending'}</span>
    </div>`;
  });
}
async function loadHeroStreak(){
  try{
    const d=await api('/api/tracker?days=1');
    $('heroStreak').textContent=d.streak;
  }catch(_){}
}

document.addEventListener('DOMContentLoaded',()=>{
  setDateUI();updateWeekLabel();loadDaily();
});
</script>
</body>
</html>
"""

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS weekly_tasks(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      title TEXT NOT NULL,
      quadrant TEXT NOT NULL DEFAULT 'schedule',
      priority TEXT NOT NULL DEFAULT 'medium',
      done INTEGER NOT NULL DEFAULT 0,
      created_at TEXT NOT NULL,
      completed_at TEXT
    );

    CREATE TABLE IF NOT EXISTS daily_tasks(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      title TEXT NOT NULL,
      date TEXT NOT NULL,
      weekly_id INTEGER,
      completed INTEGER NOT NULL DEFAULT 0,
      completed_at TEXT,
      carried_from INTEGER,
      dismissed INTEGER NOT NULL DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS daily_locks(
      date TEXT PRIMARY KEY,
      locked INTEGER NOT NULL DEFAULT 0
    );
    """)

    cols = {r["name"] for r in conn.execute("PRAGMA table_info(weekly_tasks)").fetchall()}
    if "priority" not in cols:
        conn.execute("ALTER TABLE weekly_tasks ADD COLUMN priority TEXT NOT NULL DEFAULT 'medium'")
    if "completed_at" not in cols:
        conn.execute("ALTER TABLE weekly_tasks ADD COLUMN completed_at TEXT")

    cols = {r["name"] for r in conn.execute("PRAGMA table_info(daily_tasks)").fetchall()}
    if "completed_at" not in cols:
        conn.execute("ALTER TABLE daily_tasks ADD COLUMN completed_at TEXT")
    if "carried_from" not in cols:
        conn.execute("ALTER TABLE daily_tasks ADD COLUMN carried_from INTEGER")
    if "dismissed" not in cols:
        conn.execute("ALTER TABLE daily_tasks ADD COLUMN dismissed INTEGER NOT NULL DEFAULT 0")

    # Pomodoro is intentionally no longer used.
    # Existing pomodoros data is left untouched so an old database can open safely.
    conn.commit()
    conn.close()

def day_status(conn, d):
    rows = conn.execute(
        "SELECT completed FROM daily_tasks WHERE date=? AND dismissed=0", (d,)
    ).fetchall()
    total = len(rows)
    completed = sum(1 for r in rows if r["completed"])
    if total == 0:
        return "empty", total, completed
    if completed == total:
        return "completed", total, completed
    if d < date.today().isoformat():
        return "missed", total, completed
    return "pending", total, completed

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/api/weekly", methods=["GET", "POST"])
def weekly():
    conn = get_db()

    if request.method == "POST":
        x = request.get_json() or {}
        title = (x.get("title") or "").strip()
        if not title:
            conn.close()
            return jsonify(error="Title required"), 400

        q = x.get("quadrant", "schedule")
        if q not in {"doit", "schedule", "delegate", "eliminate"}:
            q = "schedule"

        priority = x.get("priority", "medium")
        if priority not in {"high", "medium", "low"}:
            priority = "medium"

        conn.execute(
            """INSERT INTO weekly_tasks
               (title,quadrant,priority,created_at)
               VALUES(?,?,?,?)""",
            (title, q, priority, datetime.now().isoformat())
        )
        conn.commit()

    rows = conn.execute("""
        SELECT w.*,
               CAST(julianday('now')-julianday(w.created_at) AS INTEGER) days_added
        FROM weekly_tasks w
        ORDER BY w.done ASC, w.id DESC
    """).fetchall()

    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route("/api/weekly/<int:task_id>", methods=["PATCH", "DELETE"])
def weekly_item(task_id):
    conn = get_db()

    if request.method == "DELETE":
        conn.execute("DELETE FROM daily_tasks WHERE weekly_id=?", (task_id,))
        conn.execute("DELETE FROM weekly_tasks WHERE id=?", (task_id,))
    else:
        x = request.get_json() or {}
        if "done" in x:
            done = 1 if x["done"] else 0
            completed_at = datetime.now().isoformat() if done else None
            conn.execute(
                "UPDATE weekly_tasks SET done=?,completed_at=? WHERE id=?",
                (done, completed_at, task_id)
            )
        if "priority" in x and x["priority"] in {"high", "medium", "low"}:
            conn.execute(
                "UPDATE weekly_tasks SET priority=? WHERE id=?",
                (x["priority"], task_id)
            )

    conn.commit()
    conn.close()
    return jsonify(ok=True)

@app.route("/api/daily", methods=["GET", "POST"])
def daily():
    conn = get_db()

    if request.method == "POST":
        x = request.get_json() or {}
        d = x.get("date")
        if not d:
            conn.close()
            return jsonify(error="Date required"), 400

        lock = conn.execute(
            "SELECT locked FROM daily_locks WHERE date=?", (d,)
        ).fetchone()
        if lock and lock["locked"]:
            conn.close()
            return jsonify(error="This day's plan is locked"), 409

        weekly_id = x.get("weekly_id")

        if weekly_id:
            w = conn.execute(
                "SELECT title FROM weekly_tasks WHERE id=?", (weekly_id,)
            ).fetchone()
            if not w:
                conn.close()
                return jsonify(error="Weekly task not found"), 404

            title = w["title"]
            exists = conn.execute(
                """SELECT id FROM daily_tasks
                   WHERE date=? AND weekly_id=? AND dismissed=0""",
                (d, weekly_id)
            ).fetchone()

            if exists:
                conn.close()
                return jsonify(ok=True, duplicate=True)
        else:
            title = (x.get("title") or "").strip()
            if not title:
                conn.close()
                return jsonify(error="Title required"), 400

        conn.execute(
            """INSERT INTO daily_tasks
               (title,date,weekly_id,completed,carried_from,dismissed)
               VALUES(?,?,?,0,?,0)""",
            (title, d, weekly_id, x.get("carried_from"))
        )
        conn.commit()

    d = request.args.get("date", date.today().isoformat())

    lock = conn.execute(
        "SELECT locked FROM daily_locks WHERE date=?", (d,)
    ).fetchone()
    locked = bool(lock and lock["locked"])

    tasks = conn.execute("""
        SELECT d.*, w.quadrant, w.priority,
               CASE WHEN d.weekly_id IS NOT NULL THEN 1 ELSE 0 END source
        FROM daily_tasks d
        LEFT JOIN weekly_tasks w ON w.id=d.weekly_id
        WHERE d.date=? AND d.dismissed=0
        ORDER BY d.completed, d.id
    """, (d,)).fetchall()

    yesterday = (
        date.fromisoformat(d) - timedelta(days=1)
    ).isoformat()

    missed = conn.execute("""
        SELECT id,title,date,weekly_id
        FROM daily_tasks
        WHERE date=? AND completed=0 AND dismissed=0
        ORDER BY id
    """, (yesterday,)).fetchall()

    weekly_rows = conn.execute("""
        SELECT w.*,
               CAST(julianday('now')-julianday(w.created_at) AS INTEGER) days_added
        FROM weekly_tasks w
        WHERE w.done=0 AND w.quadrant!='eliminate'
        ORDER BY
          CASE w.priority
            WHEN 'high' THEN 1
            WHEN 'medium' THEN 2
            ELSE 3
          END,
          w.id DESC
    """).fetchall()

    status, total, completed = day_status(conn, d)

    conn.close()

    return jsonify(
        tasks=[dict(r) for r in tasks],
        missed=[dict(r) for r in missed],
        weekly=[dict(r) for r in weekly_rows],
        locked=locked,
        status=status,
        total=total,
        completed=completed
    )

@app.route("/api/daily/<int:task_id>", methods=["PATCH", "DELETE"])
def daily_item(task_id):
    conn = get_db()

    row = conn.execute(
        "SELECT date,completed FROM daily_tasks WHERE id=?", (task_id,)
    ).fetchone()

    if not row:
        conn.close()
        return jsonify(error="Task not found"), 404

    lock = conn.execute(
        "SELECT locked FROM daily_locks WHERE date=?", (row["date"],)
    ).fetchone()

    if request.method == "DELETE":
        if lock and lock["locked"]:
            conn.close()
            return jsonify(error="This day's plan is locked"), 409
        conn.execute("DELETE FROM daily_tasks WHERE id=?", (task_id,))
    else:
        x = request.get_json() or {}
        completed = 1 if x.get("completed") else 0
        completed_at = datetime.now().isoformat() if completed else None

        conn.execute(
            """UPDATE daily_tasks
               SET completed=?,completed_at=?
               WHERE id=?""",
            (completed, completed_at, task_id)
        )

    conn.commit()
    conn.close()
    return jsonify(ok=True)

@app.route("/api/daily/carry/<int:task_id>", methods=["POST"])
def carry_daily_task(task_id):
    conn = get_db()

    source = conn.execute("""
        SELECT *
        FROM daily_tasks
        WHERE id=? AND completed=0 AND dismissed=0
    """, (task_id,)).fetchone()

    if not source:
        conn.close()
        return jsonify(error="Missed task not found"), 404

    x = request.get_json() or {}
    target_date = x.get("date", date.today().isoformat())

    lock = conn.execute(
        "SELECT locked FROM daily_locks WHERE date=?", (target_date,)
    ).fetchone()

    if lock and lock["locked"]:
        conn.close()
        return jsonify(error="Today's plan is locked"), 409

    exists = conn.execute("""
        SELECT id FROM daily_tasks
        WHERE date=? AND weekly_id IS ? AND title=? AND dismissed=0
    """, (target_date, source["weekly_id"], source["title"])).fetchone()

    if not exists:
        conn.execute("""
            INSERT INTO daily_tasks
            (title,date,weekly_id,completed,carried_from,dismissed)
            VALUES(?,?,?,0,?,0)
        """, (
            source["title"],
            target_date,
            source["weekly_id"],
            source["id"]
        ))

    # Keep the original missed task in history, but mark it as handled.
    conn.execute(
        "UPDATE daily_tasks SET dismissed=1 WHERE id=?", (task_id,)
    )

    conn.commit()
    conn.close()
    return jsonify(ok=True)

@app.route("/api/daily/lock", methods=["POST"])
def daily_lock():
    x = request.get_json() or {}
    d = x.get("date")

    if not d:
        return jsonify(error="Date required"), 400

    value = 1 if x.get("locked") else 0
    conn = get_db()

    conn.execute("""
        INSERT INTO daily_locks(date,locked)
        VALUES(?,?)
        ON CONFLICT(date) DO UPDATE SET locked=excluded.locked
    """, (d, value))

    conn.commit()
    conn.close()
    return jsonify(ok=True, locked=bool(value))

@app.route("/api/tracker")
def tracker():
    conn = get_db()

    # Build history for every day that has tasks.
    rows = conn.execute("""
        SELECT date,
               COUNT(*) AS total,
               SUM(CASE WHEN completed=1 THEN 1 ELSE 0 END) AS completed
        FROM daily_tasks
        WHERE dismissed=0
        GROUP BY date
        ORDER BY date
    """).fetchall()

    counts = {
        r["date"]: {
            "total": r["total"],
            "completed": r["completed"] or 0
        }
        for r in rows
    }

    today = date.today()

    # A completed day requires at least one task and every task complete.
    def complete_day(ds):
        x = counts.get(ds)
        return bool(x and x["total"] > 0 and x["completed"] == x["total"])

    # Current streak: today counts only if it is complete.
    # If today is not complete, start from yesterday so the user can
    # still see the active historical streak while working today.
    streak = 0
    cursor = today
    if not complete_day(cursor):
        cursor -= timedelta(days=1)

    while complete_day(cursor.isoformat()):
        streak += 1
        cursor -= timedelta(days=1)

    # Best streak across all recorded days.
    best = 0
    run = 0
    cursor = None

    for ds in sorted(counts):
        d = date.fromisoformat(ds)
        if cursor is not None and d == cursor + timedelta(days=1) and complete_day(ds):
            run += 1
        elif complete_day(ds):
            run = 1
        else:
            run = 0

        best = max(best, run)
        cursor = d

    total_days = len(counts)
    completed_days = sum(1 for ds in counts if complete_day(ds))
    completion_rate = round((completed_days / total_days) * 100) if total_days else 0

    # Recent 30 days, including empty days only when they are relevant
    # to the streak/calendar view.
    history = []
    start = today - timedelta(days=29)
    cur = start

    while cur <= today:
        ds = cur.isoformat()
        x = counts.get(ds)

        if x:
            if x["completed"] == x["total"]:
                status = "completed"
            elif cur < today:
                status = "missed"
            else:
                status = "pending"

            history.append({
                "date": ds,
                "date_label": cur.strftime("%b %d, %Y"),
                "total": x["total"],
                "completed": x["completed"],
                "status": status
            })

        cur += timedelta(days=1)

    conn.close()

    return jsonify(
        days=history,
        streak=streak,
        best_streak=best,
        completion_rate=completion_rate,
        completed_days=completed_days
    )

if __name__ == "__main__":
    init_db()
    app.run(debug=False, host="127.0.0.1", port=9744)