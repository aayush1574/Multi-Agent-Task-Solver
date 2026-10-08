const input = document.querySelector('#objectiveInput');
const runButton = document.querySelector('#runButton');
const runState = document.querySelector('#runState');
const runTitle = document.querySelector('#runTitle');
const runId = document.querySelector('#runId');
const progressBar = document.querySelector('#progressBar');
const outputCard = document.querySelector('#outputCard');
const historyList = document.querySelector('#historyList');
const toast = document.querySelector('#toast');
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

let runs = JSON.parse(localStorage.getItem('relay-runs') || '[]');
let activeRun = null;

const escapeHTML = (value) => String(value).replace(/[&<>'"]/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[char]));
const shorten = (text, length = 54) => text.length > length ? `${text.slice(0, length).trim()}…` : text;

function renderHistory() {
  historyList.innerHTML = runs.length ? runs.slice(0, 4).map((run, index) => `
    <button class="history-item" type="button" data-history="${index}">
      <strong>${escapeHTML(shorten(run.objective))}</strong>
      <span>${escapeHTML(run.id)} · complete</span>
    </button>`).join('') : '<div class="history-empty">No runs yet. Your completed work will stay here.</div>';
}

function makeResult(objective, tools) {
  const subject = shorten(objective.replace(/[.?!]+$/, ''), 72);
  return {
    summary: `The team converted “${subject}” into a focused decision brief. The strongest path is to validate the highest-impact opportunity first, measure it against a clear baseline, and expand only after an early signal is confirmed.`,
    findings: [
      ['Prioritize the leading signal', 'Rank opportunities by expected impact, confidence, and effort; begin with the option that is both measurable and reversible.'],
      ['Run a 30-day validation', 'Assign one owner, define a weekly leading indicator, and use a small pilot to reduce uncertainty before committing more resources.'],
      ['Close the learning loop', 'Review evidence every seven days, record what changed, and stop or scale the initiative against pre-agreed thresholds.']
    ],
    tools
  };
}

function renderResult(run) {
  outputCard.classList.remove('empty');
  outputCard.innerHTML = `
    <h4>Decision brief</h4>
    <p class="summary">${escapeHTML(run.result.summary)}</p>
    ${run.result.findings.map((item, index) => `<div class="finding"><b>0${index + 1}</b><div><strong>${escapeHTML(item[0])}</strong><p>${escapeHTML(item[1])}</p></div></div>`).join('')}
    <div class="tool-note">Evidence path: ${escapeHTML(run.result.tools.length ? run.result.tools.join(' + ') : 'reasoning only')} · Demo data</div>`;
}

function loadRun(run) {
  runId.textContent = run.id;
  runTitle.textContent = shorten(run.objective, 78);
  runState.className = 'run-state complete';
  runState.innerHTML = '<span></span> Complete';
  progressBar.style.width = '100%';
  document.querySelectorAll('.agent-card').forEach(card => {
    card.className = 'agent-card done';
    card.querySelector('.agent-status').textContent = 'Done';
  });
  renderResult(run);
  document.querySelector('#runPanel').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

async function runObjective() {
  const objective = input.value.trim();
  if (objective.length < 12) return showToast('Add a little more detail to the objective.');
  if (activeRun) return;

  const tools = [];
  if (document.querySelector('#sqlTool').checked) tools.push('SQL');
  if (document.querySelector('#apiTool').checked) tools.push('REST API');
  const id = `R-${String((Number(localStorage.getItem('relay-counter')) || 0) + 1).padStart(3, '0')}`;
  localStorage.setItem('relay-counter', String(Number(id.slice(2))));
  activeRun = { id, objective, result: makeResult(objective, tools) };
  runButton.disabled = true;
  runId.textContent = id;
  runTitle.textContent = shorten(objective, 78);
  runState.className = 'run-state running';
  runState.innerHTML = '<span></span> Running';
  outputCard.className = 'output-card empty';
  outputCard.innerHTML = '<div><div class="empty-mark">R</div><p>The team is assembling its response…</p></div>';
  progressBar.style.width = '4%';
  document.querySelector('#runPanel').scrollIntoView({ behavior: 'smooth', block: 'start' });

  const cards = [...document.querySelectorAll('.agent-card')];
  cards.forEach(card => { card.className = 'agent-card'; card.querySelector('.agent-status').textContent = 'Queued'; });
  const labels = ['Structuring objective', tools.length ? `Checking ${tools.join(' + ')}` : 'Reviewing context', 'Testing the evidence', 'Writing decision brief'];
  for (let i = 0; i < cards.length; i += 1) {
    cards[i].classList.add('active');
    cards[i].querySelector('.agent-status').textContent = labels[i];
    progressBar.style.width = `${18 + i * 23}%`;
    await sleep(720 + i * 170);
    cards[i].classList.remove('active');
    cards[i].classList.add('done');
    cards[i].querySelector('.agent-status').textContent = 'Done';
  }

  progressBar.style.width = '100%';
  runState.className = 'run-state complete';
  runState.innerHTML = '<span></span> Complete';
  renderResult(activeRun);
  runs = [activeRun, ...runs].slice(0, 8);
  localStorage.setItem('relay-runs', JSON.stringify(runs));
  renderHistory();
  runButton.disabled = false;
  showToast('Objective completed by 4 agents.');
  activeRun = null;
}

function showToast(message) {
  toast.textContent = message;
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), 2200);
}

document.querySelectorAll('.example').forEach(button => button.addEventListener('click', () => {
  input.value = button.dataset.prompt;
  input.focus();
}));
historyList.addEventListener('click', event => {
  const button = event.target.closest('[data-history]');
  if (button) loadRun(runs[Number(button.dataset.history)]);
});
runButton.addEventListener('click', runObjective);
input.addEventListener('keydown', event => {
  if ((event.metaKey || event.ctrlKey) && event.key === 'Enter') runObjective();
});
document.querySelector('#themeButton').addEventListener('click', () => {
  const next = document.documentElement.dataset.theme === 'dark' ? '' : 'dark';
  document.documentElement.dataset.theme = next;
  localStorage.setItem('relay-theme', next);
});
document.documentElement.dataset.theme = localStorage.getItem('relay-theme') || '';
renderHistory();

if (document.modelContext?.registerTool) {
  try {
    document.modelContext.registerTool({
      name: 'start_objective_run',
      title: 'Start objective run',
      description: 'Start a visible multi-agent demo run for a supplied objective.',
      inputSchema: { type: 'object', properties: { objective: { type: 'string', minLength: 12 } }, required: ['objective'], additionalProperties: false },
      annotations: { readOnlyHint: false, untrustedContentHint: false },
      async execute(data) {
        if (!data || typeof data.objective !== 'string' || data.objective.trim().length < 12) throw new Error('Objective must contain at least 12 characters.');
        input.value = data.objective.trim();
        await runObjective();
        return { status: 'complete', runId: runs[0]?.id, objective: input.value };
      }
    });
  } catch (_) { /* Optional browser capability. */ }
}
