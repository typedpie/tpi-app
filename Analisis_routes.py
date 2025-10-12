# analysis_routes.py
# Rutas de análisis (HTML + cálculo) separadas del main

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import text

import io, base64
import numpy as np
import pandas as pd
from scipy import stats

import matplotlib
matplotlib.use("Agg")              # necesario en Render
import matplotlib.pyplot as plt

from database import get_db

router = APIRouter(tags=["analisis"])

# --- helpers locales (copias pequeñas para evitar dependencias cruzadas) ---
def q1(db: Session, sql: str, params: dict | None = None):
    return db.execute(text(sql), params or {}).mappings().all()

FORM_STYLE = """
<style>
body{font-family:system-ui,-apple-system,Segoe UI,Roboto;padding:14px;max-width:1200px;margin:auto}
label{display:block;margin-top:12px;font-weight:600}
input,select,button,textarea{width:100%;padding:10px;margin-top:6px;border-radius:8px;border:1px solid #ddd;font-size:16px}
button{background:#111;color:#fff;border:none}
.small{font-size:12px;color:#666}
table{border-collapse:collapse}
th,td{border:1px solid #ddd;padding:6px}
</style>
"""

# --- consultas y cálculo ---
def fetch_times(db: Session, proceso: str, maquina: str, tipo: str, producto: str | None = None) -> pd.DataFrame:
    sql = """
        SELECT
          tr.fecha,
          p.nombre  AS proceso,
          m.nombre  AS maquina,
          pr.nombre AS producto,
          tr.tipo,
          tr.tiempo_seg::float AS tiempo_seg
        FROM tiempo_real tr
        JOIN proceso  p  ON p.id_proceso  = tr.id_proceso
        JOIN maquina  m  ON m.id_maquina  = tr.id_maquina
        JOIN producto pr ON pr.id_producto = tr.id_producto
        WHERE LOWER(p.nombre) = LOWER(:proceso)
          AND LOWER(m.nombre) = LOWER(:maquina)
          AND LOWER(tr.tipo)  = LOWER(:tipo)
          {extra}
        ORDER BY tr.fecha
    """.format(extra="AND LOWER(pr.nombre)=LOWER(:producto)" if producto else "")
    params = {"proceso": proceso, "maquina": maquina, "tipo": tipo}
    if producto: params["producto"] = producto
    rows = q1(db, sql, params)
    return pd.DataFrame(rows)

def resumen_estadistico(x: np.ndarray) -> dict:
    n = x.size
    mean = float(np.mean(x)) if n else np.nan
    std  = float(np.std(x, ddof=1)) if n > 1 else np.nan
    q1, med, q3 = (np.percentile(x, [25, 50, 75]) if n else (np.nan, np.nan, np.nan))
    iqr = (q3 - q1) if n else np.nan
    cv  = (std/mean*100) if (n and mean) else np.nan
    if n > 1:
        tcrit = stats.t.ppf(0.975, df=n-1)
        ci_low  = mean - tcrit * std / np.sqrt(n)
        ci_high = mean + tcrit * std / np.sqrt(n)
    else:
        ci_low = ci_high = np.nan
    return {
        "n": n, "mean": mean, "std": std, "cv%": cv,
        "min": float(np.min(x)) if n else np.nan,
        "q1": float(q1), "median": float(med), "q3": float(q3),
        "max": float(np.max(x)) if n else np.nan,
        "iqr": float(iqr), "ci95_low": float(ci_low), "ci95_high": float(ci_high)
    }

def pruebas_ajuste(x: np.ndarray) -> list[dict]:
    if x.size < 3: return []
    out = []
    mu, sigma = x.mean(), x.std(ddof=1)
    p_shap = stats.shapiro(x).pvalue if 3 <= x.size <= 5000 else np.nan
    p_ks_n = stats.kstest(x, 'norm', args=(mu, sigma)).pvalue
    out.append({"Distribución":"Normal","Parámetros":f"mu={mu:.3f}, sigma={sigma:.3f}","p(KS)":p_ks_n,"p(Shapiro)":p_shap})
    if np.all(x>0):
        logx = np.log(x); mu_l, sig_l = logx.mean(), logx.std(ddof=1)
        p_ks_ln = stats.kstest(x, 'lognorm', args=(sig_l, 0, np.exp(mu_l))).pvalue
        out.append({"Distribución":"Log-normal","Parámetros":f"mu_log={mu_l:.3f}, sigma_log={sig_l:.3f}","p(KS)":p_ks_ln,"p(Shapiro)":np.nan})
    loc_e, scale_e = stats.expon.fit(x)
    p_ks_e = stats.kstest(x, 'expon', args=(loc_e, scale_e)).pvalue
    out.append({"Distribución":"Exponencial","Parámetros":f"loc={loc_e:.3f}, scale={scale_e:.3f}","p(KS)":p_ks_e,"p(Shapiro)":np.nan})
    a, loc_g, scale_g = stats.gamma.fit(x)
    p_ks_g = stats.kstest(x, 'gamma', args=(a, loc_g, scale_g)).pvalue
    out.append({"Distribución":"Gamma","Parámetros":f"shape={a:.3f}, loc={loc_g:.3f}, scale={scale_g:.3f}","p(KS)":p_ks_g,"p(Shapiro)":np.nan})
    return out

def _fig_to_b64(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=160, bbox_inches="tight")
    plt.close(fig)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")

def graficos_base64(x: np.ndarray, titulo: str) -> tuple[str,str]:
    # Histograma + normal
    fig = plt.figure(figsize=(7,4))
    bins = max(5, int(np.ceil(np.sqrt(len(x))))) if len(x)>0 else 5
    counts, bin_edges, _ = plt.hist(x, bins=bins, edgecolor="black")
    plt.title(f"{titulo} – Histograma"); plt.xlabel("Tiempo (s)"); plt.ylabel("Frecuencia")
    if len(x)>1 and x.std(ddof=1)>0:
        xs = np.linspace(bin_edges[0], bin_edges[-1], 200)
        pdf = stats.norm.pdf(xs, x.mean(), x.std(ddof=1))
        plt.plot(xs, pdf * len(x) * (bin_edges[1]-bin_edges[0]))
    b64_hist = _fig_to_b64(fig)
    # QQ-plot
    if len(x)>1 and x.std(ddof=1)>0:
        fig2 = plt.figure(figsize=(5,5))
        stats.probplot(x, dist="norm", sparams=(x.mean(), x.std(ddof=1)), plot=plt)
        plt.title(f"{titulo} – QQ-plot vs Normal")
        b64_qq = _fig_to_b64(fig2)
    else:
        b64_qq = ""
    return b64_hist, b64_qq

# -------- UI simple para lanzar análisis --------
@router.get("/app/analisis", response_class=HTMLResponse)
def app_analisis():
    return HTMLResponse(FORM_STYLE + """
<h2>Analizar datos (real)</h2>

<label>Proceso</label><select id="proceso"></select>
<label>Máquina</label><select id="maquina"></select>
<label>Producto (opcional)</label><select id="producto"></select>
<label>Tipo de tiempo</label>
<select id="tipo">
  <option value="setup">SetUp</option>
  <option value="proceso">Proceso</option>
  <option value="postproceso">Post-proceso</option>
  <option value="espera">Espera</option>
</select>

<button onclick="go()">Analizar</button>
<p class="small" id="msg"></p>

<a href="/"><button style="margin-top: 20px; padding: 8px 16px;">⬅ Volver</button></a>

<script>
async function loadProcesos(){
  const r=await fetch('/options/procesos'); const d=await r.json();
  const s=document.getElementById('proceso'); s.innerHTML='<option value="">-- selecciona --</option>';
  d.forEach(x=>s.innerHTML+=`<option>${x}</option>`);
}
async function loadMaquinas(){
  const p=document.getElementById('proceso').value;
  const r=await fetch('/options/maquinas?proceso='+encodeURIComponent(p)); const d=await r.json();
  const s=document.getElementById('maquina'); s.innerHTML='<option value="">-- selecciona --</option>';
  d.forEach(x=>s.innerHTML+=`<option>${x}</option>`);
  document.getElementById('producto').innerHTML='<option value="">-- opcional --</option>';
}
async function loadProductos(){
  const m=document.getElementById('maquina').value;
  const r=await fetch('/options/productos?maquina='+encodeURIComponent(m)); const d=await r.json();
  const s=document.getElementById('producto'); s.innerHTML='<option value="">-- opcional --</option>';
  d.forEach(x=>s.innerHTML+=`<option>${x}</option>`);
}
function go(){
  const p=document.getElementById('proceso').value;
  const m=document.getElementById('maquina').value;
  const pr=document.getElementById('producto').value;
  const t=document.getElementById('tipo').value;
  if(!p||!m||!t){ document.getElementById('msg').textContent='Completa Proceso, Máquina y Tipo.'; return; }
  const url='/analizar?proceso='+encodeURIComponent(p)+'&maquina='+encodeURIComponent(m)+'&tipo='+encodeURIComponent(t)+(pr?('&producto='+encodeURIComponent(pr)):'');
  window.location = url;
}
document.getElementById('proceso').addEventListener('change',loadMaquinas);
document.getElementById('maquina').addEventListener('change',loadProductos);
loadProcesos();
</script>
""")

# -------- Reporte HTML (tabla + gráficos) --------
@router.get("/analizar", response_class=HTMLResponse)
def analizar(proceso: str, maquina: str, tipo: str, producto: str | None = None,
             export: int | None = None, db: Session = Depends(get_db)):
    df = fetch_times(db, proceso, maquina, tipo, producto)
    if df.empty:
        return HTMLResponse(f"<html><body style='font-family:system-ui;padding:16px;'><p>⚠️ No hay datos para esos filtros.</p><p><a href='/app/analisis'>⬅ Volver</a></p></body></html>")

    if export:
        csv = df.to_csv(index=False)
        return HTMLResponse(content=csv, media_type="text/csv",
                            headers={"Content-Disposition": f"attachment; filename=datos_{tipo}.csv"})

    x = df["tiempo_seg"].to_numpy(dtype=float)
    res = resumen_estadistico(x)
    fits = pruebas_ajuste(x)
    lo = res["q1"] - 1.5*res["iqr"]; hi = res["q3"] + 1.5*res["iqr"]
    outs = df.loc[(df["tiempo_seg"]<lo)|(df["tiempo_seg"]>hi), ["fecha","producto","tiempo_seg"]]
    titulo = f"{maquina} – {tipo}"
    b64_hist, b64_qq = graficos_base64(x, titulo)

    def fmt(v): 
        return "—" if v is None or (isinstance(v,float) and np.isnan(v)) else (f"{v:.3f}" if isinstance(v,float) else v)
    rows_res = "".join([f"<tr><td>{k}</td><td>{fmt(v)}</td></tr>" for k,v in res.items()])
    rows_fit = "".join([f"<tr><td>{f['Distribución']}</td><td>{f['Parámetros']}</td><td>{fmt(f['p(KS)'])}</td><td>{fmt(f['p(Shapiro)'])}</td></tr>" for f in fits])

    html = f"""
    <html><head><title>Análisis</title></head>
    <body style="font-family:system-ui; padding:16px;">
      <h2>📈 Análisis de datos</h2>
      <p><b>Proceso:</b> {proceso} &nbsp;|&nbsp; <b>Máquina:</b> {maquina} &nbsp;|&nbsp; <b>Tipo:</b> {tipo} {(f'| <b>Producto:</b> {producto}' if producto else '')}</p>
      <p><a href="/app/analisis">⬅ Elegir otros filtros</a> &nbsp;|&nbsp;
         <a href="/analizar?proceso={proceso}&maquina={maquina}&tipo={tipo}{('&producto='+producto if producto else '')}&export=1">⬇ Descargar CSV</a></p>

      <h3>Resumen</h3>
      <table>
        <tr><th>Métrica</th><th>Valor</th></tr>
        {rows_res}
      </table>

      <h3 style="margin-top:18px;">Bondad de ajuste (p-valores)</h3>
      <table>
        <tr><th>Distribución</th><th>Parámetros</th><th>p(KS)</th><th>p(Shapiro)</th></tr>
        {rows_fit if rows_fit else '<tr><td colspan=4>n insuficiente</td></tr>'}
      </table>

      <div style="display:flex; gap:16px; flex-wrap:wrap; margin-top:18px;">
        <div><img src="{b64_hist}" style="max-width:560px; border:1px solid #ddd"/></div>
        {f'<div><img src="{b64_qq}" style="max-width:420px; border:1px solid #ddd"/></div>' if b64_qq else ''}
      </div>

      <h3 style="margin-top:18px;">Posibles atípicos (IQR)</h3>
      {"<p>Ninguno</p>" if outs.empty else outs.to_html(index=False)}
    </body></html>
    """
    return HTMLResponse(html)