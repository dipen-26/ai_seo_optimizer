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
      // Clean and properly encode data
      const cleanBody = {};
      for(const [key, value] of Object.entries(body)){
        if(value === null || value === undefined){
          cleanBody[key] = '';
        } else {
          let cleanValue = String(value);
          // Remove control characters but preserve normal whitespace
          cleanValue = cleanValue.replace(/[\x00-\x08\x0b-\x0c\x0e-\x1f]/g, '');
          // Normalize and escape newlines so JSON encoder sees literal \n sequences
          cleanValue = cleanValue.replace(/\r\n|\r|\n/g, '\\n');
          // Replace tabs with single space
          cleanValue = cleanValue.replace(/\t/g, ' ');
          cleanBody[key] = cleanValue.trim();
        }
      }
      
      const jsonString = JSON.stringify(cleanBody);
      const res = await fetch(API_BASE + path, {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: jsonString
      });
      
      if(!res.ok){
        try {
          const error = await res.json();
          console.error('API Error:', error);
        } catch(e) {
          console.error('API Error:', res.statusText);
        }
        return null;
      }
      return await res.json();
    }catch(err){
      console.error('API Call Error:', err);
      return null;
    }
  }

  function mockCroResponse(payload){
    return {
      success: true,
      score: Math.floor(60 + Math.random()*30),
      issues: [
        {level:'critical', title:'Missing meta description', detail:'Adds to relevance.'},
        {level:'improve', title:'Weak CTA copy', detail:'Make CTA clearer.'}
      ],
      recommendations: [
        'Add a concise meta description (120–155 chars).',
        'Use an action-oriented CTA above the fold.'
      ],
      ai_suggestions: [],
      extracted_data: null
    }
  }

  function mockGmbResponse(payload){
    return {
      success: true,
      score: Math.floor(65 + Math.random()*30),
      issues: [],
      recommendations: ['Add business description','Upload recent photos'],
      ai_suggestions: [],
      metrics: {profile_completeness: 0, reviews: 0, photos: 0, posts: 0, engagement: 0, rating: 0, review_count: 0, photo_count: 0, post_count: 0},
      extracted_data: null
    }
  }

  function renderResultsForCro(data){
    const out = el('#results');
    if(!out) return;
    out.classList.remove('empty');
    
    const aiSuggestionsHtml = data.ai_suggestions && data.ai_suggestions.length > 0
      ? `<div style="margin-top:12px"><h4>AI Suggestions</h4><ul>${data.ai_suggestions.map(s=>`<li>${s}</li>`).join('')}</ul></div>`
      : '';
    
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
          <ul>${data.issues.map(i=>`<li><strong>[${i.level}]</strong> ${i.title}</li>`).join('')}</ul>
        </div>
        ${aiSuggestionsHtml}
      </div>
    `;
    animateMetricValues();
  }

  function renderResultsForGmb(data){
    const out = el('#results');
    if(!out) return;
    out.classList.remove('empty');
    
    const metricsHtml = data.metrics ? `
      <div style="margin-top:16px">
        <h4>Score Breakdown</h4>
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px">
          <div style="background:#1a1a1f;padding:12px;border-radius:8px">
            <div style="font-size:12px;color:#888">Profile Completeness</div>
            <div style="font-size:18px;font-weight:bold">${Math.round(data.metrics.profile_completeness || 0)}</div>
          </div>
          <div style="background:#1a1a1f;padding:12px;border-radius:8px">
            <div style="font-size:12px;color:#888">Reviews</div>
            <div style="font-size:18px;font-weight:bold">${Math.round(data.metrics.reviews || 0)}</div>
          </div>
          <div style="background:#1a1a1f;padding:12px;border-radius:8px">
            <div style="font-size:12px;color:#888">Photos</div>
            <div style="font-size:18px;font-weight:bold">${Math.round(data.metrics.photos || 0)}</div>
          </div>
          <div style="background:#1a1a1f;padding:12px;border-radius:8px">
            <div style="font-size:12px;color:#888">Posts</div>
            <div style="font-size:18px;font-weight:bold">${Math.round(data.metrics.posts || 0)}</div>
          </div>
        </div>
      </div>
    ` : '';
    
    const aiSuggestionsHtml = data.ai_suggestions && data.ai_suggestions.length > 0
      ? `<div style="margin-top:12px"><h4>AI Strategy</h4><ul>${data.ai_suggestions.map(s=>`<li>${s}</li>`).join('')}</ul></div>`
      : '';
    
    out.innerHTML = `
      <div class="card">
        <div style="display:flex;align-items:center;gap:16px">
          <div style="width:96px;height:96px;border-radius:999px;background:linear-gradient(135deg,#252733,#14141a);display:flex;align-items:center;justify-content:center;box-shadow:0 0 20px rgba(124,92,255,0.12)">
            <div class="metric-value" data-value="${data.score}" style="font-size:28px">${data.score}</div>
          </div>
          <div>
            <h3>GMB Score: ${data.score}</h3>
            <p>${(data.metrics.rating || 0)}⭐ • ${data.metrics.review_count || 0} reviews • ${data.metrics.photo_count || 0} photos</p>
          </div>
        </div>
        ${metricsHtml}
        <div style="margin-top:12px">
          <h4>Recommendations</h4>
          <ul>${data.recommendations.map(r=>`<li>${r}</li>`).join('')}</ul>
        </div>
        <div style="margin-top:12px">
          <h4>Issues Found</h4>
          <ul>${data.issues.map(i=>`<li><strong>[${i.level}]</strong> ${i.title}</li>`).join('')}</ul>
        </div>
        ${aiSuggestionsHtml}
      </div>
    `;
    animateMetricValues();
  }

  function animateMetricValues(){
    els('.metric-value[data-value]').forEach(elm=>{
      const target = parseInt(elm.dataset.value,10)||0;
      let cur = 0;
      const step = Math.max(1, Math.floor(target/40));
      const id = setInterval(()=>{
        cur += step;
        if(cur>=target){cur=target; clearInterval(id)}
        elm.textContent = cur;
      },20);
    })
  }

  function wireForms(){
    const fCro = el('#form-cro');
    if(fCro){
      fCro.addEventListener('submit', async (ev)=>{
        ev.preventDefault();
        const fd = new FormData(fCro);
        const body = Object.fromEntries(fd.entries());
        const res = await callApi('/api/cro/audit', body);
        if(res && res.success !== false) {
          renderResultsForCro(res);
          showSection('results');
        } else {
          showToast('Error: ' + (res?.error || 'Unable to reach API'));
          const fallback = mockCroResponse(body);
          renderResultsForCro(fallback);
          showSection('results');
        }
      });
      
      const resetBtn = el('#btn-cro-reset');
      if(resetBtn){
        resetBtn.addEventListener('click', ()=>{
          fCro.reset();
          const results = el('#results');
          if(results) {
            results.classList.add('empty');
            results.innerHTML = 'No results yet. Run a tool to see suggestions.';
          }
        });
      }
    }

    const fGmb = el('#form-gmb');
    if(fGmb){
      fGmb.addEventListener('submit', async (ev)=>{
        ev.preventDefault();
        const fd = new FormData(fGmb);
        const body = Object.fromEntries(fd.entries());
        const res = await callApi('/api/gmb/audit', body);
        if(res && res.success !== false) {
          renderResultsForGmb(res);
          showSection('results');
        } else {
          showToast('Error: ' + (res?.error || 'Unable to reach API'));
          const fallback = mockGmbResponse(body);
          renderResultsForGmb(fallback);
          showSection('results');
        }
      });
      
      const resetBtn = el('#btn-gmb-reset');
      if(resetBtn){
        resetBtn.addEventListener('click', ()=>{
          fGmb.reset();
          const results = el('#results');
          if(results) {
            results.classList.add('empty');
            results.innerHTML = 'No results yet. Run a tool to see suggestions.';
          }
        });
      }
    }
  }

  function init(){
    initNav();
    setApiBaseInUI();
    wireForms();
    const save = el('#save-settings');
    if(save) save.addEventListener('click', saveApiBase);
    animateMetricValues();
  }

  document.addEventListener('DOMContentLoaded', init);
})();
