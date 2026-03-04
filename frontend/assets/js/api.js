(function(){
  // Default to localhost:8000, but use current origin if available
  const DEFAULT_BASE = typeof window !== 'undefined' ? window.location.origin : 'http://127.0.0.1:8000';
  
  // Get API_BASE from localStorage, validating it first
  let storedBase = localStorage.getItem('rf_api_base');
  if(storedBase && !storedBase.startsWith('http')){
    localStorage.removeItem('rf_api_base');
    storedBase = null;
  }
  
  let API_BASE = storedBase || DEFAULT_BASE;

  // Ensure API_BASE ends with / and paths start with /
  function getApiUrl(path) {
    const base = API_BASE.endsWith('/') ? API_BASE.slice(0, -1) : API_BASE;
    const cleanPath = path.startsWith('/') ? path : '/' + path;
    return base + cleanPath;
  }

  function el(sel){return document.querySelector(sel)}
  function els(sel){return Array.from(document.querySelectorAll(sel))}

  function showSection(name){
    els('.panel').forEach(p=>p.classList.remove('active'));
    const s = document.getElementById('section-' + name);
    if(s) {
      s.classList.add('active');
      // Update URL hash when section changes
      window.location.hash = '#' + name;
    }
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
    
    // Handle hash changes (back button, bookmarks, direct URL)
    window.addEventListener('hashchange', ()=>{
      const hash = window.location.hash.slice(1) || 'overview';
      els('.nav-btn').forEach(n=>n.classList.remove('active'));
      els('.side-link').forEach(n=>n.classList.remove('active'));
      const navBtn = els('.nav-btn').find(b => b.dataset.section === hash);
      const sideLink = els('.side-link').find(b => b.dataset.section === hash);
      if(navBtn) navBtn.classList.add('active');
      if(sideLink) sideLink.classList.add('active');
      showSectionWithoutHash(hash);
    });
    
    // Set initial section from URL hash on page load
    const hash = window.location.hash.slice(1) || 'overview';
    const navBtn = els('.nav-btn').find(b => b.dataset.section === hash);
    const sideLink = els('.side-link').find(b => b.dataset.section === hash);
    if(navBtn) navBtn.classList.add('active');
    if(sideLink) sideLink.classList.add('active');
    showSectionWithoutHash(hash);
  }

  function showSectionWithoutHash(name){
    els('.panel').forEach(p=>p.classList.remove('active'));
    const s = document.getElementById('section-' + name);
    if(s) s.classList.add('active');
  }

  function saveReportToStorage(type, payload, result){
    // Get existing reports
    let reports = JSON.parse(localStorage.getItem('rf_reports') || '[]');
    
    // Add new report
    const report = {
      id: Date.now(),
      type: type,
      timestamp: new Date().toISOString(),
      payload: result,
      score: result.score,
      summary: ''
    };
    
    // Add summary based on type
    if(type === 'cro') {
      report.summary = `CRO Audit: ${payload.url} - Score: ${result.score}`;
    } else {
      report.summary = `GMB Audit: ${payload.business_name} - Score: ${result.score}`;
    }
    
    reports.unshift(report);
    
    // Keep only last 20 reports
    if(reports.length > 20) {
      reports = reports.slice(0, 20);
    }
    
    localStorage.setItem('rf_reports', JSON.stringify(reports));
    loadReports();
  }

  function loadReports(){
    const reports = JSON.parse(localStorage.getItem('rf_reports') || '[]');
    const reportsList = el('#reports-list');
    const noReports = el('#no-reports');
    
    if(reports.length === 0) {
      if(reportsList) reportsList.style.display = 'none';
      if(noReports) noReports.style.display = 'block';
      return;
    }
    
    if(noReports) noReports.style.display = 'none';
    if(reportsList) reportsList.style.display = 'block';
    
    reportsList.innerHTML = reports.map(report => {
      const date = new Date(report.timestamp);
      const dateStr = date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
      const badge = report.type === 'cro' ? '<span class="badge badge-cro">CRO</span>' : '<span class="badge badge-gmb">GMB</span>';
      
      return `
        <div class="report-card">
          <div class="report-header">
            <div>
              ${badge}
              <span class="report-summary">${report.summary}</span>
            </div>
            <button class="btn-delete" onclick="deleteReport(${report.id})">Delete</button>
          </div>
          <div class="report-date">${dateStr}</div>
          <button class="btn-view" onclick="viewReport(${report.id})">View Report</button>
        </div>
      `;
    }).join('');
  }

  function viewReport(id){
    const reports = JSON.parse(localStorage.getItem('rf_reports') || '[]');
    const report = reports.find(r => r.id === id);
    
    if(!report) return;
    
    if(report.type === 'cro') {
      renderResultsForCro(report.payload);
    } else {
      renderResultsForGmb(report.payload);
    }
    
    showSection('results');
  }

  function deleteReport(id){
    if(!confirm('Delete this report?')) return;
    
    let reports = JSON.parse(localStorage.getItem('rf_reports') || '[]');
    reports = reports.filter(r => r.id !== id);
    localStorage.setItem('rf_reports', JSON.stringify(reports));
    loadReports();
  }

  function showToast(msg){
    console.log('TOAST:', msg);
  }

  function showLoadingSpinner(message = 'Processing...'){
    const spinner = el('#loading-spinner');
    const spinnerText = el('#spinner-text');
    if(spinner) {
      spinner.classList.remove('hidden');
      if(spinnerText) spinnerText.textContent = message;
    }
  }

  function hideLoadingSpinner(){
    const spinner = el('#loading-spinner');
    if(spinner) {
      spinner.classList.add('hidden');
    }
  }

  async function callApi(path, body){
    try{
      const cleanBody = {};
      for(const [key, value] of Object.entries(body)){
        if(value === null || value === undefined){
          cleanBody[key] = '';
        } else {
          let cleanValue = String(value);
          cleanValue = cleanValue.replace(/[\x00-\x08\x0b-\x0c\x0e-\x1f]/g, '');
          cleanValue = cleanValue.replace(/\r\n|\r|\n/g, '\\n');
          cleanValue = cleanValue.replace(/\t/g, ' ');
          cleanBody[key] = cleanValue.trim();
        }
      }
      
      const jsonString = JSON.stringify(cleanBody);
      const apiUrl = getApiUrl(path);
      console.log('API URL:', apiUrl);
      const res = await fetch(apiUrl, {
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
      metrics: {profile_completeness: 0, reviews: 0, photos: 0, posts: 0, rating: 0, review_count: 0, photo_count: 0, post_count: 0},
      extracted_data: null
    }
  }

  function renderResultsForCro(data){
    const out = el('#results');
    if(!out) return;
    out.classList.remove('empty');
    
    // Extract all the data from the API response
    const extracted = data.extracted_data || {};
    const title = extracted.title || 'N/A';
    const metaDesc = extracted.meta_description || 'Not found';
    const h1Count = extracted.h1_count || 0;
    const h1Text = (extracted.h1_text && extracted.h1_text[0]) || 'N/A';
    const buttonCount = extracted.button_count || 0;
    const buttons = extracted.buttons || [];
    const formCount = extracted.form_count || 0;
    const imageCount = extracted.image_count || 0;
    const isHttps = extracted.is_https || false;
    const jsRendered = extracted.js_rendered || false;
    const industry = data.industry || 'default';
    const pagespeed = data.pagespeed;
    const viewportAnalysis = data.viewport_analysis;
    
    // Trust signals
    const trust = extracted.trust_signals || {};
    const hasSchema = trust.has_schema || false;
    const schemaTypes = (trust.schema && trust.schema.schema_types) || [];
    const thirdPartyReviews = trust.third_party_reviews || [];
    const isHttpsSignal = trust.is_https || false;
    
    // AI Suggestions
    const aiSuggestionsHtml = data.ai_suggestions && data.ai_suggestions.length > 0
      ? `<div class="section-box">
           <h4>🤖 AI Recommendations</h4>
           <ul>${data.ai_suggestions.map(s=>`<li>${s}</li>`).join('')}</ul>
         </div>`
      : '';
    
    // PageSpeed data
    let pagespeedHtml = '';
    if(pagespeed) {
      pagespeedHtml = `
        <div class="section-box">
          <h4>⚡ PageSpeed Insights</h4>
          <div class="metrics-grid">
            <div class="metric-item">
              <span class="metric-label">Performance Score</span>
              <span class="metric-value ${pagespeed.score >= 90 ? 'good' : pagespeed.score >= 50 ? 'medium' : 'poor'}">${pagespeed.score || 0}</span>
            </div>
            <div class="metric-item">
              <span class="metric-label">LCP</span>
              <span class="metric-value ${(pagespeed.lcp || 0) <= 2.5 ? 'good' : 'poor'}">${(pagespeed.lcp || 0).toFixed(1)}s</span>
            </div>
            <div class="metric-item">
              <span class="metric-label">FID</span>
              <span class="metric-value ${(pagespeed.fid || 0) <= 100 ? 'good' : 'poor'}">${pagespeed.fid || 0}ms</span>
            </div>
            <div class="metric-item">
              <span class="metric-label">CLS</span>
              <span class="metric-value ${(pagespeed.cls || 0) <= 0.1 ? 'good' : 'poor'}">${(pagespeed.cls || 0).toFixed(2)}</span>
            </div>
          </div>
        </div>
      `;
    }
    
    // Above the fold analysis
    let viewportHtml = '';
    if(viewportAnalysis) {
      viewportHtml = `
        <div class="section-box">
          <h4>👁️ Above-the-Fold Analysis</h4>
          <div class="metrics-grid">
            <div class="metric-item">
              <span class="metric-label">CTAs Above Fold</span>
              <span class="metric-value">${viewportAnalysis.cta_above_fold || 0}</span>
            </div>
            <div class="metric-item">
              <span class="metric-label">CTAs Below Fold</span>
              <span class="metric-value">${viewportAnalysis.cta_below_fold || 0}</span>
            </div>
            <div class="metric-item">
              <span class="metric-label">Viewport Size</span>
              <span class="metric-value">${viewportAnalysis.viewport?.width || 0}x${viewportAnalysis.viewport?.height || 0}</span>
            </div>
          </div>
        </div>
      `;
    }
    
    // Buttons found
    const buttonsHtml = buttons.length > 0 
      ? `<div class="items-list">
           <span class="item-label">Buttons/CTAs found:</span>
           ${buttons.slice(0, 5).map(b => `<span class="item-tag">${b.text || b.type}</span>`).join('')}
         </div>`
      : '';

    out.innerHTML = `
      <div class="results-card">
        <div class="score-section">
          <div class="score-circle" data-value="${data.score}">
            <span class="score-number">${data.score}</span>
          </div>
          <div class="score-info">
            <h3>CRO Audit Score</h3>
            <p class="score-subtitle">${data.issues?.length || 0} issues • ${data.recommendations?.length || 0} recommendations</p>
            <p class="score-meta">Industry: ${industry} | JS Rendered: ${jsRendered ? '✓' : '✗'} | HTTPS: ${isHttps ? '✓' : '✗'}</p>
          </div>
        </div>
        
        <div class="data-summary">
          <div class="section-box">
            <h4>📄 Page Data</h4>
            <div class="data-row"><span>Title:</span><span>${title}</span></div>
            <div class="data-row"><span>H1:</span><span>${h1Text}</span></div>
            <div class="data-row"><span>Meta Description:</span><span>${metaDesc.substring(0, 80)}...</span></div>
            <div class="metrics-grid">
              <div class="metric-item"><span class="metric-label">H1 Tags</span><span>${h1Count}</span></div>
              <div class="metric-item"><span class="metric-label">Buttons</span><span>${buttonCount}</span></div>
              <div class="metric-item"><span class="metric-label">Forms</span><span>${formCount}</span></div>
              <div class="metric-item"><span class="metric-label">Images</span><span>${imageCount}</span></div>
            </div>
            ${buttonsHtml}
          </div>
          
          <div class="section-box">
            <h4>🔒 Trust Signals</h4>
            <div class="metrics-grid">
              <div class="metric-item">
                <span class="metric-label">HTTPS/SSL</span>
                <span class="metric-value ${isHttpsSignal ? 'good' : 'poor'}">${isHttpsSignal ? '✓ Secure' : '✗ Not Secure'}</span>
              </div>
              <div class="metric-item">
                <span class="metric-label">Schema.org</span>
                <span class="metric-value ${hasSchema ? 'good' : 'warning'}">${hasSchema ? '✓ Found' : '✗ Missing'}</span>
              </div>
              ${schemaTypes.length > 0 ? `<div class="metric-item"><span class="metric-label">Schema Types</span><span>${schemaTypes.slice(0,3).join(', ')}</span></div>` : ''}
              ${thirdPartyReviews.length > 0 ? `<div class="metric-item"><span class="metric-label">Third-Party Reviews</span><span>${thirdPartyReviews.join(', ')}</span></div>` : ''}
            </div>
          </div>
          
          ${pagespeedHtml}
          ${viewportHtml}
        </div>
        
        <div class="issues-section">
          <div class="section-box">
            <h4>⚠️ Issues Found</h4>
            ${data.issues && data.issues.length > 0 
              ? `<ul class="issues-list">${data.issues.map(i=>`<li class="issue-${i.level || 'improve'}"><span class="issue-level">[${i.level || 'info'}]</span> <strong>${i.title}</strong>: ${i.detail || ''}</li>`).join('')}</ul>`
              : '<p class="no-issues">✓ No issues found!</p>'
            }
          </div>
          
          <div class="section-box">
            <h4>💡 Recommendations</h4>
            <ul>${data.recommendations && data.recommendations.length > 0 
              ? data.recommendations.map(r=>`<li>${r}</li>`).join('')
              : '<li>No specific recommendations</li>'
            }</ul>
          </div>
        </div>
        
        ${aiSuggestionsHtml}
      </div>
      
      <style>
        .results-card { background: #1a1a1f; border-radius: 12px; padding: 24px; }
        .score-section { display: flex; align-items: center; gap: 20px; margin-bottom: 24px; padding-bottom: 20px; border-bottom: 1px solid #333; }
        .score-circle { width: 100px; height: 100px; border-radius: 50%; background: linear-gradient(135deg, #667eea, #764ba2); display: flex; align-items: center; justify-content: center; }
        .score-number { font-size: 36px; font-weight: bold; color: white; }
        .score-info h3 { margin: 0 0 8px 0; font-size: 24px; }
        .score-subtitle { margin: 0; color: #888; }
        .score-meta { margin: 8px 0 0 0; font-size: 12px; color: #666; }
        .data-summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 16px; margin-bottom: 24px; }
        .section-box { background: #252525; border-radius: 8px; padding: 16px; }
        .section-box h4 { margin: 0 0 12px 0; font-size: 14px; color: #aaa; text-transform: uppercase; letter-spacing: 0.5px; }
        .data-row { display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid #333; font-size: 13px; }
        .data-row span:first-child { color: #888; }
        .data-row span:last-child { color: #fff; text-align: right; max-width: 70%; }
        .metrics-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; margin-top: 12px; }
        .metric-item { background: #1a1a1f; padding: 10px; border-radius: 6px; text-align: center; }
        .metric-label { display: block; font-size: 11px; color: #666; margin-bottom: 4px; }
        .metric-value { display: block; font-size: 16px; font-weight: bold; }
        .metric-value.good { color: #4caf50; }
        .metric-value.medium { color: #ff9800; }
        .metric-value.poor { color: #f44336; }
        .metric-value.warning { color: #ff9800; }
        .items-list { margin-top: 12px; }
        .item-label { display: block; font-size: 11px; color: #666; margin-bottom: 6px; }
        .item-tag { display: inline-block; background: #333; padding: 4px 8px; border-radius: 4px; font-size: 11px; margin: 2px; }
        .issues-section { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 16px; }
        .issues-list { list-style: none; padding: 0; margin: 0; }
        .issues-list li { padding: 10px; margin-bottom: 8px; border-radius: 6px; font-size: 13px; }
        .issue-critical { background: rgba(244,67,54,0.15); border-left: 3px solid #f44336; }
        .issue-high { background: rgba(255,152,0,0.15); border-left: 3px solid #ff9800; }
        .issue-improve { background: rgba(33,150,243,0.15); border-left: 3px solid #2196f3; }
        .issue-info { background: rgba(158,158,158,0.15); border-left: 3px solid #9e9e9e; }
        .issue-level { font-weight: bold; text-transform: uppercase; font-size: 10px; }
        .no-issues { color: #4caf50; text-align: center; padding: 20px; }
      </style>
    `;
    animateMetricValues();
  }

  function renderResultsForGmb(data){
    const out = el('#results');
    if(!out) return;
    out.classList.remove('empty');
    
    // Extract all data
    const metrics = data.metrics || {};
    const extracted = data.extracted_data || {};
    
    // Profile data
    const businessName = extracted.business_name || 'N/A';
    const location = extracted.location || 'N/A';
    const categories = extracted.categories || [];
    const phone = extracted.phone || 'Not provided';
    const website = extracted.website || 'Not provided';
    const address = extracted.address || 'N/A';
    const description = extracted.description || 'Not provided';
    const hours = extracted.hours || {};
    
    // Metrics
    const rating = metrics.rating || 0;
    const reviewCount = metrics.review_count || 0;
    const photoCount = metrics.photo_count || 0;
    const postCount = metrics.post_count || 0;
    const profileScore = Math.round(metrics.profile_completeness || 0);
    const reviewsScore = Math.round(metrics.reviews || 0);
    const photosScore = Math.round(metrics.photos || 0);
    const postsScore = Math.round(metrics.posts || 0);
    
    // Data source info
    const dataSource = data.data_source || 'unknown';
    const dataNote = data.data_note || '';
    const warning = data.warning || '';
    const extractionStatus = data.extraction_status || 'unknown';
    
    // AI Suggestions
    const aiSuggestionsHtml = data.ai_suggestions && data.ai_suggestions.length > 0
      ? `<div class="section-box">
           <h4>🤖 AI Strategy Recommendations</h4>
           <ul>${data.ai_suggestions.map(s=>`<li>${s}</li>`).join('')}</ul>
         </div>`
      : '';

    // Warning if extraction had issues
    const warningHtml = warning 
      ? `<div class="warning-box">⚠️ ${warning}</div>`
      : '';
    
    // Data source badge
    const sourceBadge = extractionStatus === 'complete' 
      ? `<span class="source-badge success">✓ Live Data</span>`
      : `<span class="source-badge warning">⚠️ Partial Data</span>`;

    out.innerHTML = `
      <div class="results-card">
        <div class="score-section">
          <div class="score-circle" data-value="${data.score}">
            <span class="score-number">${data.score}</span>
          </div>
          <div class="score-info">
            <h3>GMB Audit Score</h3>
            <p class="score-subtitle">${data.issues?.length || 0} issues • ${data.recommendations?.length || 0} recommendations</p>
            <p class="score-meta">${rating}⭐ • ${reviewCount} reviews • ${photoCount} photos • ${postCount} posts</p>
            <div class="source-row">${sourceBadge} <span class="source-text">${dataNote}</span></div>
          </div>
        </div>
        
        ${warningHtml}
        
        <div class="data-summary">
          <div class="section-box">
            <h4>🏪 Business Profile</h4>
            <div class="data-row"><span>Business Name:</span><span>${businessName}</span></div>
            <div class="data-row"><span>Location:</span><span>${location}</span></div>
            <div class="data-row"><span>Address:</span><span>${address}</span></div>
            <div class="data-row"><span>Phone:</span><span>${phone}</span></div>
            <div class="data-row"><span>Website:</span><span>${website}</span></div>
            ${categories.length > 0 ? `<div class="data-row"><span>Categories:</span><span>${categories.join(', ')}</span></div>` : ''}
            ${description && description !== 'Not provided' ? `<div class="data-row full"><span>Description:</span><span>${description}</span></div>` : ''}
          </div>
          
          <div class="section-box">
            <h4>📊 Score Breakdown</h4>
            <div class="metrics-grid">
              <div class="metric-item">
                <span class="metric-label">Profile</span>
                <span class="metric-value ${profileScore >= 20 ? 'good' : profileScore >= 10 ? 'medium' : 'poor'}">${profileScore}</span>
              </div>
              <div class="metric-item">
                <span class="metric-label">Reviews</span>
                <span class="metric-value ${reviewsScore >= 20 ? 'good' : reviewsScore >= 10 ? 'medium' : 'poor'}">${reviewsScore}</span>
              </div>
              <div class="metric-item">
                <span class="metric-label">Photos</span>
                <span class="metric-value ${photosScore >= 15 ? 'good' : photosScore >= 8 ? 'medium' : 'poor'}">${photosScore}</span>
              </div>
              <div class="metric-item">
                <span class="metric-label">Posts</span>
                <span class="metric-value ${postsScore >= 15 ? 'good' : postsScore >= 8 ? 'medium' : 'poor'}">${postsScore}</span>
              </div>
            </div>
          </div>
          
          <div class="section-box">
            <h4>⭐ Google Metrics</h4>
            <div class="metrics-grid">
              <div class="metric-item">
                <span class="metric-label">Rating</span>
                <span class="metric-value">${rating > 0 ? rating + ' ⭐' : 'N/A'}</span>
              </div>
              <div class="metric-item">
                <span class="metric-label">Reviews</span>
                <span class="metric-value">${reviewCount > 0 ? reviewCount : 'N/A'}</span>
              </div>
              <div class="metric-item">
                <span class="metric-label">Photos</span>
                <span class="metric-value">${photoCount > 0 ? photoCount : 'N/A'}</span>
              </div>
              <div class="metric-item">
                <span class="metric-label">Posts</span>
                <span class="metric-value">${postCount > 0 ? postCount : 'N/A'}</span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="issues-section">
          <div class="section-box">
            <h4>⚠️ Issues Found</h4>
            ${data.issues && data.issues.length > 0 
              ? `<ul class="issues-list">${data.issues.map(i=>`<li class="issue-${i.level || 'improve'}"><span class="issue-level">[${i.level || 'info'}]</span> <strong>${i.title}</strong>: ${i.detail || ''}</li>`).join('')}</ul>`
              : '<p class="no-issues">✓ No issues found!</p>'
            }
          </div>
          
          <div class="section-box">
            <h4>💡 Recommendations</h4>
            <ul>${data.recommendations && data.recommendations.length > 0 
              ? data.recommendations.map(r=>`<li>${r}</li>`).join('')
              : '<li>No specific recommendations</li>'
            }</ul>
          </div>
        </div>
        
        ${aiSuggestionsHtml}
      </div>
      
      <style>
        .results-card { background: #1a1a1f; border-radius: 12px; padding: 24px; }
        .score-section { display: flex; align-items: center; gap: 20px; margin-bottom: 24px; padding-bottom: 20px; border-bottom: 1px solid #333; }
        .score-circle { width: 100px; height: 100px; border-radius: 50%; background: linear-gradient(135deg, #f093fb, #f5576c); display: flex; align-items: center; justify-content: center; }
        .score-number { font-size: 36px; font-weight: bold; color: white; }
        .score-info h3 { margin: 0 0 8px 0; font-size: 24px; }
        .score-subtitle { margin: 0; color: #888; }
        .score-meta { margin: 8px 0 0 0; font-size: 14px; color: #aaa; }
        .source-row { margin-top: 8px; }
        .source-badge { padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: bold; }
        .source-badge.success { background: rgba(76,175,80,0.2); color: #4caf50; }
        .source-badge.warning { background: rgba(255,152,0,0.2); color: #ff9800; }
        .source-text { font-size: 11px; color: #666; margin-left: 8px; }
        .warning-box { background: rgba(255,152,0,0.15); border: 1px solid #ff9800; border-radius: 8px; padding: 12px; margin-bottom: 16px; color: #ff9800; }
        .data-summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; margin-bottom: 24px; }
        .section-box { background: #252525; border-radius: 8px; padding: 16px; }
        .section-box h4 { margin: 0 0 12px 0; font-size: 14px; color: #aaa; text-transform: uppercase; letter-spacing: 0.5px; }
        .data-row { display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid #333; font-size: 13px; }
        .data-row span:first-child { color: #888; }
        .data-row span:last-child { color: #fff; text-align: right; }
        .data-row.full { flex-direction: column; gap: 4px; }
        .data-row.full span:last-child { text-align: left; color: #aaa; font-size: 12px; }
        .metrics-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; margin-top: 12px; }
        .metric-item { background: #1a1a1f; padding: 10px; border-radius: 6px; text-align: center; }
        .metric-label { display: block; font-size: 11px; color: #666; margin-bottom: 4px; }
        .metric-value { display: block; font-size: 16px; font-weight: bold; }
        .metric-value.good { color: #4caf50; }
        .metric-value.medium { color: #ff9800; }
        .metric-value.poor { color: #f44336; }
        .issues-section { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; }
        .issues-list { list-style: none; padding: 0; margin: 0; }
        .issues-list li { padding: 10px; margin-bottom: 8px; border-radius: 6px; font-size: 13px; }
        .issue-critical { background: rgba(244,67,54,0.15); border-left: 3px solid #f44336; }
        .issue-high { background: rgba(255,152,0,0.15); border-left: 3px solid #ff9800; }
        .issue-improve { background: rgba(33,150,243,0.15); border-left: 3px solid #2196f3; }
        .issue-warning { background: rgba(255,193,7,0.15); border-left: 3px solid #ffc107; }
        .issue-info { background: rgba(158,158,158,0.15); border-left: 3px solid #9e9e9e; }
        .issue-level { font-weight: bold; text-transform: uppercase; font-size: 10px; }
        .no-issues { color: #4caf50; text-align: center; padding: 20px; }
      </style>
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
        
        // Show loading spinner
        showLoadingSpinner('⏳ Running CRO Audit...');
        
        const res = await callApi('/api/cro/audit', body);
        hideLoadingSpinner();
        
        if(res && res.success !== false) {
          renderResultsForCro(res);
          saveReportToStorage('cro', body, res);
          showSectionWithoutHash('results');
          window.location.hash = '#results';
        } else {
          const errorMsg = res?.error || 'Unable to reach API server. Make sure the backend is running at the configured API URL.';
          showToast('Error: ' + errorMsg);
          const results = el('#results');
          if(results) {
            results.classList.add('empty');
            results.innerHTML = `<div class="error-message"><strong>❌ Error:</strong> ${errorMsg}</div>`;
          }
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
        
        // Show loading spinner
        showLoadingSpinner('🔍 Analyzing Google Business Profile...');
        
        const res = await callApi('/api/gmb/audit', body);
        hideLoadingSpinner();
        
        if(res && res.success !== false) {
          renderResultsForGmb(res);
          saveReportToStorage('gmb', body, res);
          showSectionWithoutHash('results');
          window.location.hash = '#results';
        } else {
          const errorMsg = res?.error || 'Unable to reach API server. Make sure the backend is running at the configured API URL.';
          showToast('Error: ' + errorMsg);
          const results = el('#results');
          if(results) {
            results.classList.add('empty');
            results.innerHTML = `<div class="error-message"><strong>❌ Error:</strong> ${errorMsg}</div>`;
          }
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
    wireForms();
    loadReports();
    animateMetricValues();
  }

  // Make functions globally accessible for onclick handlers
  window.viewReport = viewReport;
  window.deleteReport = deleteReport;

  document.addEventListener('DOMContentLoaded', init);
})();
