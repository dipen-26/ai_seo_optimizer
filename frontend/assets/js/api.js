(function(){
  const DEFAULT_BASE = localStorage.getItem('rf_api_base') || (typeof window !== 'undefined' ? window.location.origin : 'http://127.0.0.1:8000');
  let API_BASE = DEFAULT_BASE;

  function el(sel){return document.querySelector(sel)}
  function els(sel){return Array.from(document.querySelectorAll(sel))}

  function showSection(name){
    els('.panel').forEach(p=>p.classList.remove('active'));
    const s = document.getElementById('section-' + name);
    if(s) s.classList.add('active');
  }

  function initNav(){
    els('.nav-btn, .side-link, .btn[data-section]').forEach(btn=>{
      btn.addEventListener('click', e=>{
        const sec = btn.dataset.section;
        if(sec){
          els('.nav-btn').forEach(n=>n.classList.remove('active'));
          if(btn.classList.contains('nav-btn')) btn.classList.add('active');
          els('.side-link').forEach(n=>n.classList.remove('active'));
          if(btn.classList.contains('side-link')) btn.classList.add('active');
          showSection(sec);
        }
      })
    })
  }

  function setApiBaseInUI(){
    const input = el('#setting-api-url');
    if(input) input.value = API_BASE;
  }

  function saveApiBase(){
    const input = el('#setting-api-url');
    if(!input) return;
    API_BASE = input.value || API_BASE;
    localStorage.setItem('rf_api_base', API_BASE);
    showToast('Settings saved');
  }

  function showToast(msg){
    console.log('TOAST:', msg);
  }

  async function callApi(path, body){
    try{
      const res = await fetch(API_BASE + path, {
        method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(body)
      });
      if(!res.ok) throw new Error('non-200');
      return await res.json();
    }catch(err){
      return null;
    }
  }

  function mockCroResponse(payload){
    return {
      score: Math.floor(60 + Math.random()*30),
      issues: [
        {level:'critical', title:'Missing meta description', detail:'Adds to relevance.'},
        {level:'improve', title:'Weak CTA copy', detail:'Make CTA clearer.'}
      ],
      recommendations: [
        'Add a concise meta description (120–155 chars).',
        'Use an action-oriented CTA above the fold.'
      ]
    }
  }

  function mockGmbResponse(payload){
    return {
      score: Math.floor(65 + Math.random()*30),
      missing: ['Business description','10+ photos'],
      recommendations: ['Add business description','Upload recent photos']
    }
  }

  function renderResultsForCro(data){
    const out = el('#results');
    if(!out) return;
    out.classList.remove('empty');
    out.innerHTML = `
      <div class="card">
        <div style="display:flex;align-items:center;gap:16px">
          <div style="width:96px;height:96px;border-radius:999px;background:linear-gradient(135deg,#252733,#14141a);display:flex;align-items:center;justify-content:center;box-shadow:0 0 20px rgba(124,92,255,0.12)">
            <div class="metric-value" data-value="${data.score}" style="font-size:28px">${data.score}</div>
          </div>
          <div>
            <h3>CRO Score: ${data.score}</h3>
            <p>${data.issues.length} issues found • ${data.recommendations.length} recommendations</p>
          </div>
        </div>
        <div style="margin-top:12px">
          <h4>Recommendations</h4>
          <ul>${data.recommendations.map(r=>`<li>${r}</li>`).join('')}</ul>
        </div>
        <div style="margin-top:12px">
          <h4>Issues</h4>
          <ul>${data.issues.map(i=>`<li><strong>[${i.level}]</strong> ${i.title} — ${i.detail}</li>`).join('')}</ul>
        </div>
      </div>
    `;
    animateMetricValues();
  }

  function renderResultsForGmb(data){
    const out = el('#results'); if(!out) return;
    out.classList.remove('empty');
    out.innerHTML = `
      <div class="card">
        <h3>GMB Score: ${data.score}</h3>
        <p>Missing fields: ${data.missing.join(', ')}</p>
        <div style="margin-top:12px">
          <h4>Recommendations</h4>
          <ul>${data.recommendations.map(r=>`<li>${r}</li>`).join('')}</ul>
        </div>
      </div>
    `;
  }

  function animateMetricValues(){
    els('.metric-value[data-value]').forEach(elm=>{
      const target = parseInt(elm.dataset.value,10)||0;
      let cur = 0; const step = Math.max(1, Math.floor(target/40));
      const id = setInterval(()=>{
        cur += step; if(cur>=target){cur=target; clearInterval(id)}; elm.textContent = cur;
      },20);
    })
  }

  function wireForms(){
    const fCro = el('#form-cro');
    if(fCro){
      fCro.addEventListener('submit', async (ev)=>{
        ev.preventDefault();
        const fd = new FormData(fCro); const body = Object.fromEntries(fd.entries());
        const res = await callApi('/api/cro/audit', body) || mockCroResponse(body);
        renderResultsForCro(res);
        showSection('results');
      });
    }

    const fGmb = el('#form-gmb');
    if(fGmb){
      fGmb.addEventListener('submit', async (ev)=>{
        ev.preventDefault();
        const fd = new FormData(fGmb); const body = Object.fromEntries(fd.entries());
        const res = await callApi('/api/gmb/audit', body) || mockGmbResponse(body);
        renderResultsForGmb(res);
        showSection('results');
      })
    }
  }

  function init(){
    initNav(); setApiBaseInUI();
    wireForms();
    const save = el('#save-settings'); if(save) save.addEventListener('click', saveApiBase);
    animateMetricValues();
  }

  document.addEventListener('DOMContentLoaded', init);
})();
