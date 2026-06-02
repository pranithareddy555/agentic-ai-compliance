from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.api.routes import router
from app.config import settings

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description=(
        "Multi-agent regulatory compliance workflow built with FastAPI, LangGraph, "
        "Pydantic, and a local vector knowledge base."
    ),
)

app.include_router(router)


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Agentic AI for Regulatory Compliance</title>
    <style>
      :root { --text: #e5eefb; --muted: #9fb0c7; --accent: #71b7ff; --accent-2: #5ce1a6; --border: rgba(148, 163, 184, 0.2); --panel: rgba(16, 24, 39, 0.78); }
      * { box-sizing: border-box; }
      body { margin: 0; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; color: var(--text); background: radial-gradient(circle at top left, rgba(113,183,255,0.22), transparent 32%), radial-gradient(circle at top right, rgba(92,225,166,0.18), transparent 28%), linear-gradient(180deg, #091120 0%, #050b14 100%); min-height: 100vh; }
      .wrap { max-width: 1200px; margin: 0 auto; padding: 56px 24px 40px; }
      .hero, .section, .card { border: 1px solid var(--border); }
      .hero { display: grid; gap: 20px; padding: 36px; border-radius: 28px; background: linear-gradient(180deg, rgba(15,23,42,0.86), rgba(8,17,31,0.92)); box-shadow: 0 24px 80px rgba(0,0,0,0.32); }
      .eyebrow { display: inline-flex; align-items: center; gap: 10px; color: var(--accent-2); font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; font-size: 12px; }
      h1 { margin: 0; font-size: clamp(2.3rem, 5vw, 4.5rem); line-height: 0.95; max-width: 10ch; }
      .sub { color: var(--muted); font-size: 1.05rem; max-width: 68ch; line-height: 1.65; }
      .grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 18px; margin-top: 24px; }
      .card { padding: 20px; border-radius: 20px; background: var(--panel); backdrop-filter: blur(18px); }
      .card h3 { margin: 0 0 8px; font-size: 1rem; }
      .card p, li { color: var(--muted); line-height: 1.6; margin: 0; }
      .actions { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 8px; }
      a.btn { display: inline-flex; align-items: center; justify-content: center; padding: 12px 18px; border-radius: 999px; text-decoration: none; font-weight: 700; border: 1px solid transparent; }
      .primary { background: linear-gradient(135deg, var(--accent), #9ad0ff); color: #07111f; }
      .ghost { border-color: var(--border); color: var(--text); background: rgba(255,255,255,0.03); }
      .section { margin-top: 28px; padding: 26px; border-radius: 24px; background: rgba(255,255,255,0.03); }
      code { padding: 2px 8px; border-radius: 8px; background: rgba(255,255,255,0.08); }
      .footer { margin-top: 22px; color: var(--muted); font-size: 0.95rem; }
      @media (max-width: 900px) { .grid { grid-template-columns: 1fr; } .hero { padding: 26px; } .wrap { padding: 24px 16px 32px; } }
    </style>
  </head>
  <body>
    <main class="wrap">
      <section class="hero">
        <div class="eyebrow">Agentic AI Compliance Platform</div>
        <h1>Automated regulatory review for modern financial teams.</h1>
        <p class="sub">This project ingests internal policy text, searches a local regulatory knowledge base, compares both with a multi-agent workflow, and produces a structured compliance report that pauses for human approval when necessary.</p>
        <div class="actions">
          <a class="btn primary" href="/docs">Open API Docs</a>
          <a class="btn ghost" href="/redoc">View ReDoc</a>
        </div>
      </section>
      <section class="grid">
        <div class="card"><h3>Researcher Agent</h3><p>Retrieves the most relevant regulatory rules from the local knowledge base.</p></div>
        <div class="card"><h3>Auditor Agent</h3><p>Compares the uploaded policy against the retrieved rules and flags gaps.</p></div>
        <div class="card"><h3>Reporting Agent</h3><p>Produces a clean, structured compliance report and requests human approval.</p></div>
      </section>
      <section class="section">
        <h3 style="margin-top:0;">Run the full demo</h3>
        <ol>
          <li>Start the backend with <code>uvicorn app.main:app --reload</code></li>
          <li>Start the Streamlit dashboard with <code>streamlit run streamlit_app.py</code></li>
          <li>Open <code>http://127.0.0.1:8501</code> for the polished UI</li>
        </ol>
        <p class="footer">The <code>/docs</code> page is the technical API console. The professional user-facing experience is the Streamlit dashboard.</p>
      </section>
    </main>
  </body>
</html>"""
