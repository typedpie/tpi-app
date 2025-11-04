# calculo.py
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["calculo"])

FORM_STYLE = """
<style>
body{font-family:system-ui,-apple-system,Segoe UI,Roboto;padding:14px;max-width:900px;margin:auto}
label{display:block;margin-top:12px;font-weight:600}
input,button{padding:8px 10px;border-radius:8px;border:1px solid #ddd;font-size:15px}
input{width:100%;}
button{background:#111;color:#fff;border:none;cursor:pointer}
button.small-btn{width:auto;padding:6px 10px;font-size:13px;margin-left:6px;}
.small{font-size:13px;color:#666}
.result{margin-top:20px;padding:14px;border-radius:8px;background:#f5f5f5}
table{border-collapse:collapse;width:100%;margin-top:10px;}
th,td{border:1px solid #ddd;padding:6px;font-size:13px;text-align:center}
tr.medida-row td input{width:100%}
</style>
"""

@router.get("/app/calculo", response_class=HTMLResponse)
def app_calculo():
    return HTMLResponse(FORM_STYLE + """
<h2>📏 Cálculo de producción – Paneles compuestos</h2>

<p class="small">
Ingresa una o varias medidas de panel. El modelo asume que el horno trabaja por lotes:
primero procesa todos los paneles de una medida, luego los de la siguiente.
Se calcula:
<ul>
  <li>Capacidad del horno (paneles/ciclo, paneles/día y días del pedido)</li>
  <li>Aprovechamiento del área del horno (%)</li>
  <li><b>Tiempo por panel</b> = tiempo horno/panel + tiempo de armado/panel (estimado)</li>
</ul>
Para el <b>armado</b> se toma como referencia 215,4 s para un panel de 345×2000 mm, y se escala linealmente
según el área del panel.
</p>

<h3>Medidas del pedido</h3>
<table id="tabla-medidas">
  <thead>
    <tr>
      <th>Ancho (mm)</th>
      <th>Largo (mm)</th>
      <th>Cantidad</th>
      <th></th>
    </tr>
  </thead>
  <tbody id="tbody-medidas">
    <!-- filas por JS -->
  </tbody>
</table>
<button type="button" class="small-btn" onclick="addRow()">➕ Agregar medida</button>

<h3>Parámetros del horno</h3>
<label>Horas efectivas de trabajo del horno (por día)</label>
<input id="horas" type="number" step="0.1" placeholder="ej: 8" />

<button onclick="calcular()">Calcular</button>
<p id="msg" class="small"></p>

<div id="resultado" class="result" style="display:none;"></div>

<a href="/"><button style="margin-top: 20px; padding: 8px 16px;">⬅ Volver al inicio</button></a>

<script>
// --- manejo de filas de medidas ---
function addRow(ancho='', largo='', cantidad=''){
  const tbody = document.getElementById('tbody-medidas');
  const tr = document.createElement('tr');
  tr.className = 'medida-row';
  tr.innerHTML = `
    <td><input type="number" step="1" class="ancho" placeholder="345" value="${ancho}"></td>
    <td><input type="number" step="1" class="largo" placeholder="2000" value="${largo}"></td>
    <td><input type="number" step="1" class="cantidad" placeholder="300" value="${cantidad}"></td>
    <td><button type="button" class="small-btn" onclick="removeRow(this)">🗑️</button></td>
  `;
  tbody.appendChild(tr);
}

function removeRow(btn){
  const tr = btn.closest('tr');
  tr && tr.remove();
}

// fila inicial
addRow();

// --- cálculo principal ---
function calcular(){
  const msg = document.getElementById('msg');
  const res = document.getElementById('resultado');
  msg.textContent = '';
  res.style.display = 'none';
  res.innerHTML = '';

  const rows = Array.from(document.querySelectorAll('tr.medida-row'));
  if(rows.length === 0){
    msg.textContent = '⚠️ Agrega al menos una medida.';
    return;
  }

  const h = parseFloat(document.getElementById('horas').value);
  if(!h || h <= 0){
    msg.textContent = '⚠️ Ingresa las horas efectivas de trabajo por día.';
    return;
  }

  // constantes del horno
  const ANCHO_PRENSA = 1300;
  const LARGO_PRENSA = 6200;
  const AREA_PRENSA = ANCHO_PRENSA * LARGO_PRENSA;
  const T_CICLO_MIN = 10;          // minutos por ciclo
  const T_CICLO_SEG = T_CICLO_MIN * 60;
  const ciclos_por_dia = (h * 60) / T_CICLO_MIN;

  // referencia para armado
  const ANCHO_BASE = 345;
  const LARGO_BASE = 2000;
  const AREA_BASE = ANCHO_BASE * LARGO_BASE;   // mm2
  const T_ARMADO_BASE = 215.4;                 // segundos por panel base

  let detalle = [];
  let total_dias = 0;
  let total_paneles = 0;
  let total_seg_trabajo = 0;   // suma (tiempo_total_por_panel * cantidad)

  for(const row of rows){
    const a = parseFloat(row.querySelector('.ancho').value);
    const l = parseFloat(row.querySelector('.largo').value);
    const q = parseFloat(row.querySelector('.cantidad').value);

    if(!a || !l || !q || q <= 0){
      msg.textContent = '⚠️ Todas las filas deben tener ancho, largo y cantidad válidos.';
      return;
    }

    const n_ancho = Math.floor(ANCHO_PRENSA / a);
    const n_largo = Math.floor(LARGO_PRENSA / l);
    const n_paneles = n_ancho * n_largo;

    if(n_paneles <= 0){
      msg.textContent = '⚠️ Con alguna de las medidas ingresadas no cabe ningún panel en la prensa.';
      return;
    }

    // capacidad diaria (solo horno)
    const paneles_dia = n_paneles * ciclos_por_dia;
    const dias = q / paneles_dia;
    total_dias += dias;

    // eficiencia de uso de área (aprovechamiento)
    const area_panel = a * l;                         // mm2
    const area_usada = n_paneles * area_panel;
    const eficiencia_area = area_usada / AREA_PRENSA * 100; // %

    // tiempos por panel (segundos)
    const t_horno_panel = T_CICLO_SEG / n_paneles;           // horno
    const factor_area = area_panel / AREA_BASE;              // escala vs panel base
    const t_armado_panel = T_ARMADO_BASE * factor_area;      // armado estimado
    const t_total_panel = t_horno_panel + t_armado_panel;    // taller por panel

    total_paneles += q;
    total_seg_trabajo += t_total_panel * q;

    detalle.push({
      ancho: a,
      largo: l,
      cantidad: q,
      por_ciclo: n_paneles,
      prod_dia: paneles_dia,
      dias: dias,
      eff_area: eficiencia_area,
      t_horno_min: t_horno_panel / 60.0,
      t_armado_min: t_armado_panel / 60.0,
      t_total_min: t_total_panel / 60.0
    });
  }

  const tiempo_promedio_panel_min = total_seg_trabajo / total_paneles / 60.0;

  // construir HTML de resultados
  let html = `
    <h3>📊 Resultados por medida</h3>
    <table>
      <thead>
        <tr>
          <th>Medida (mm)</th>
          <th>Cant.</th>
          <th>Paneles/ciclo</th>
          <th>Aprovechamiento horno (%)</th>
          <th>Prod. diaria (paneles/día)</th>
          <th>Días (horno)</th>
          <th>Horno/panel (min)</th>
          <th>Armado/panel (min, estimado)</th>
          <th>Total/panel (min)</th>
        </tr>
      </thead>
      <tbody>
  `;

  for(const d of detalle){
    html += `
      <tr>
        <td>${d.ancho} × ${d.largo}</td>
        <td>${d.cantidad}</td>
        <td>${d.por_ciclo}</td>
        <td>${d.eff_area.toFixed(1)}%</td>
        <td>${d.prod_dia.toFixed(1)}</td>
        <td>${d.dias.toFixed(2)}</td>
        <td>${d.t_horno_min.toFixed(2)}</td>
        <td>${d.t_armado_min.toFixed(2)}</td>
        <td>${d.t_total_min.toFixed(2)}</td>
      </tr>
    `;
  }

  html += `
      </tbody>
    </table>
    <hr>
    <h3>⏱️ Resumen del pedido completo</h3>
    <p><b>Días totales estimados (por cuello de botella horno):</b> ${total_dias.toFixed(2)} días (~${Math.ceil(total_dias)} días calendario)</p>
    <p><b>Tiempo promedio de trabajo por panel (horno + armado):</b> ${tiempo_promedio_panel_min.toFixed(2)} min/panel</p>
    <p class="small">
      Supuestos: horno trabaja por lotes homogéneos (una medida a la vez), ciclo fijo de 10 min,
      prensa de 1300×6200 mm. El tiempo de armado se escala linealmente con el área del panel,
      usando como referencia 215,4 s para un panel de 345×2000 mm.
    </p>
  `;

  res.innerHTML = html;
  res.style.display = 'block';
}
</script>
""")

