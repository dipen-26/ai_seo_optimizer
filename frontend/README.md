RankForge — Frontend (preview)
=================================

Quick preview and test instructions for the frontend UI.

How to preview
---------------

Open `frontend/index.html` in your browser (double-click or use Live Server).

Default API
-----------

The UI will use `http://127.0.0.1:8000` as the API base by default. You can change this in **Settings**.

Mock behavior
-------------

If the backend is not available the UI falls back to mocked responses for CRO and GMB audits.

Test the CRO flow
-----------------
1. Open `frontend/index.html`.
2. Click `CRO` in the top nav.
3. Enter a URL and click `Run Audit`.
4. Results appear in the Results panel.

Files changed
------------

- `index.html` — full app shell and panels
- `assets/css/styles.css` — design tokens + components
- `assets/js/api.js` — nav, form handlers, mock responses
- `assets/img/logo.svg` — small SVG logo

Enjoy! If you want additional pages (Reports, detailed score rings, or animations), tell me which next.
