from fastapi import APIRouter
from fastapi.responses import HTMLResponse
import math


router = APIRouter(tags=["calculo"])

FORM_STYLE = """
<style>
body{font-family:system-ui,-apple-system,Segoe UI,Roboto;padding:14px;max-width:600px;margin:auto}
label{display:block;margin-top:12px;font-weight:600}
input,button{width:100%;padding:10px;margin-top:6px;border-radius:8px;border:1px solid #ddd;font-size:16px}
button{background:#111;color:#fff;border:none;margin-top:12px}
.small{font-size:13px;color:#666}
.result{margin-top:20px;padding:14px;border-radius:8px;background:#f5f5f5}
</style>
"""
@router.get ("/app/calculo", response_class=HTMLResponse)
def app_calculo():
    return HTMLResponse(FORM_STYLE + """
<h2>📏 Cálculo de producción – Paneles compuestos</h2>

<label>Ancho del panel (mm)</label>
<input id="ancho" type="number" step="1" placeholder="ej: 345" />

<label>Largo del panel (mm)</label>
<input id="largo" type="number" step="1" placeholder="ej: 2000" />

<label>Cantidad de paneles en la orden</label>
<input id="cantidad" type="number" step="1" placeholder="ej: 300" />

<label>Horas efectivas de trabajo del horno (por día)</label>
<input id="horas" type="number" step="0.1" placeholder="ej: 8" />

<button onclick="calcular()">Calcular</button>
<p id="msg" class="small"></p>

<div id="resultado" class="result" style="display:none;"></div>

<a href="/"><button style="margin-top: 20px; padding: 8px 16px;">⬅ Volver al inicio</button></a>

<script>
function calcular(){
  const a = parseFloat(document.getElementById('ancho').value);
  const l = parseFloat(document.getElementById('largo').value);
  const q = parseFloat(document.getElementById('cantidad').value);
  const h = parseFloat(document.getElementById('horas').value);
  const msg = document.getElementById('msg');
  const res = document.getElementById('resultado');
  msg.textContent = ''; res.style.display='none';

  if(!a||!l||!q||!h){ msg.textContent='⚠️ Completa todos los campos numéricos.'; return; }

  // constantes
  const ANCHO_PRENSA = 1300;
  const LARGO_PRENSA = 6200;
  const T_CICLO = 10; // minutos por ciclo

  const n_ancho = Math.floor(ANCHO_PRENSA / a);
  const n_largo = Math.floor(LARGO_PRENSA / l);
  const n_paneles = n_ancho * n_largo;
  const ciclos_por_dia = (h * 60) / T_CICLO;
  const paneles_dia = n_paneles * ciclos_por_dia;
  const dias_pedido = q / paneles_dia;

  res.innerHTML = `
    <h3>📊 Resultados</h3>
    <p><b>Paneles por ciclo:</b> ${n_paneles}</p>
    <p><b>Producción diaria estimada:</b> ${paneles_dia.toFixed(1)} paneles/día</p>
    <p><b>Días necesarios para el pedido:</b> ${dias_pedido.toFixed(2)} días (~${Math.ceil(dias_pedido)} días calendario)</p>
    <hr>
    <p class='small'>Ciclo del horno: ${T_CICLO} min — Prensa: 1300×6200 mm</p>
  `;
  res.style.display='block';
}
</script>
""")