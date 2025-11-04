from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["calculo"])

FORM_STYLE = """
<style>
body{font-family:system-ui,-apple-system,Segoe UI,Roboto;padding:14px;max-width:800px;margin:auto}
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
primero procesa todos los paneles de una medida, luego los de la siguiente, y así sucesivamente.
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
    <!-- filas se agregan por JS -->
  </tbody>
</table>
<button type="button" class="small-btn" onclick="addRow()">➕ Agregar medida</button>

<h3>Parámetros del horno</h3>
<label>Horas efectivas de trabajo del horno (por día)</label>
<input id="horas" type="number" step="0.1" placeholder="ej: 8" />

<label>Eficiencia global del sistema (%)</label>
<input id="eficiencia" type="number" step="1" placeholder="ej: 85 (si lo dejas vacío asumo 100)" />

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

// agrega una fila inicial por defecto
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

  let e_raw = document.getElementById('eficiencia').value;
  let e = e_raw ? parseFloat(e_raw) : 100;
  if(isNaN(e) || e <= 0 || e > 100){
    msg.textContent = '⚠️ La eficiencia debe estar entre 1 y 100 (%).';
    return;
  }

  // constantes del horno
  const ANCHO_PRENSA = 1300;
  const LARGO_PRENSA = 6200;
  const T_CICLO = 10; // minutos por ciclo
  const ciclos_por_dia = (h * 60) / T_CICLO;
  const factor = e / 100.0;

  let detalle = [];
  let total_teor = 0;
  let total_efec = 0;

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

    const paneles_dia_teor = n_paneles * ciclos_por_dia;
    const paneles_dia_efec = paneles_dia_teor * factor;

    const dias_teor = q / paneles_dia_teor;
    const dias_efec = q / paneles_dia_efec;

    total_teor += dias_teor;
    total_efec += dias_efec;

    detalle.push({
      ancho: a,
      largo: l,
      cantidad: q,
      por_ciclo: n_paneles,
      prod_teor: paneles_dia_teor,
      prod_efec: paneles_dia_efec,
      dias_teor: dias_teor,
      dias_efec: dias_efec
    });
  }

  // construir HTML de resultados
  let html = `
    <h3>📊 Resultados por medida</h3>
    <table>
      <thead>
        <tr>
          <th>Medida (mm)</th>
          <th>Cant.</th>
          <th>Paneles/ciclo</th>
          <th>Prod. diaria teórica</th>
          <th>Prod. diaria efectiva (${e.toFixed(1)}%)</th>
          <th>Días teóricos</th>
          <th>Días efectivos</th>
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
        <td>${d.prod_teor.toFixed(1)}</td>
        <td>${d.prod_efec.toFixed(1)}</td>
        <td>${d.dias_teor.toFixed(2)}</td>
        <td>${d.dias_efec.toFixed(2)}</td>
      </tr>
    `;
  }

  html += `
      </tbody>
    </table>
    <hr>
    <h3>⏱️ Resumen del pedido completo</h3>
    <p><b>Días totales (teórico 100%):</b> ${total_teor.toFixed(2)} días (~${Math.ceil(total_teor)} días calendario)</p>
    <p><b>Días totales (con eficiencia ${e.toFixed(1)}%):</b> ${total_efec.toFixed(2)} días (~${Math.ceil(total_efec)} días calendario)</p>
    <p class="small">Supuestos: horno trabaja por lotes homogéneos (una medida a la vez), ciclo fijo de ${T_CICLO} min, prensa 1300×6200 mm, eficiencia aplica a paradas, setups, etc.</p>
  `;

  res.innerHTML = html;
  res.style.display = 'block';
}
</script>
""")
