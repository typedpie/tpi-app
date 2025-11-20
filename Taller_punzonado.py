from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["taller_punzonado"])

FORM_STYLE = """
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{
  font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
  background:#f3f4f6;
  color:#0f172a;
}

/* enlaces */
a{text-decoration:none;color:inherit}

/* NAVBAR (igual que otras calculadoras) */
.navbar{
  position:sticky;
  top:0;
  z-index:40;
  display:flex;
  align-items:center;
  justify-content:space-between;
  padding:12px 56px;
  background:linear-gradient(90deg,#020617,#111827);
  color:#f9fafb;
  box-shadow:0 10px 30px rgba(15,23,42,0.45);
}
.brand{
  display:flex;
  align-items:center;
  gap:18px;
}
.brand-logo{
  display:flex;
  align-items:center;
  gap:8px;
}
.brand-logo img{
  height:30px;
}
.brand-divider{
  width:1px;
  height:24px;
  background:rgba(248,250,252,0.35);
}

.nav-menu{
  list-style:none;
  display:flex;
  align-items:center;
  gap:24px;
  font-size:0.82rem;
  text-transform:uppercase;
  letter-spacing:0.08em;
}
.nav-menu>li{
  position:relative;
  cursor:pointer;
  padding-bottom:10px;
}
.nav-link{
  color:#f9fafb;
  text-decoration:none;
  padding-bottom:3px;
}
.nav-link:hover{
  border-bottom:2px solid #f97316;
}

/* dropdown */
.dropdown{
  display:none;
  position:absolute;
  top:60%;
  left:0;
  margin-top:6px;
  background:rgba(15,23,42,0.97);
  border-radius:10px;
  min-width:240px;
  padding:10px 0;
  box-shadow:0 18px 40px rgba(0,0,0,0.45);
  z-index:50;
}
.nav-menu li:hover .dropdown{
  display:block;
}
.dropdown a{
  display:block;
  padding:8px 16px;
  font-size:0.8rem;
  color:#e5e7eb;
  white-space:nowrap;
}
.dropdown a span{
  display:block;
  font-size:0.72rem;
  color:#9ca3af;
}
.dropdown a:hover{
  background:rgba(249,115,22,0.08);
  color:#ffffff;
}

/* botón admin */
.cta-btn{
  background:#f97316;
  color:#111827;
  border-radius:999px;
  padding:8px 18px;
  font-size:0.8rem;
  font-weight:600;
  border:none;
  text-decoration:none;
  text-transform:uppercase;
  letter-spacing:0.08em;
  box-shadow:0 10px 24px rgba(249,115,22,0.4);
}
.cta-btn:hover{
  filter:brightness(1.05);
}

/* CONTENIDO PÁGINA */
.page-wrapper{
  max-width:1080px;
  margin:32px auto 40px;
  padding:0 20px;
}
.card{
  background:#ffffff;
  border-radius:18px;
  box-shadow:0 16px 40px rgba(15,23,42,0.12);
  padding:24px 26px 30px;
}
h2{
  font-size:1.6rem;
  margin-bottom:10px;
}
.small{
  font-size:0.86rem;
  color:#6b7280;
}
h3{
  margin-top:24px;
  margin-bottom:8px;
  font-size:1.05rem;
}

/* formularios */
label{
  display:block;
  margin-top:12px;
  margin-bottom:4px;
  font-weight:600;
  font-size:0.93rem;
}
input, select, button{
  font-size:0.95rem;
}
input, select{
  width:100%;
  padding:10px 12px;
  border-radius:12px;
  border:1px solid #d1d5db;
  outline:none;
}
input:focus, select:focus{
  border-color:#f97316;
  box-shadow:0 0 0 1px rgba(249,115,22,0.35);
}

/* layout de máquinas */
.machine-card{
  margin-top:18px;
  padding:14px 16px 16px;
  border-radius:16px;
  border:1px solid #e5e7eb;
  background:#f9fafb;
}
.machine-header{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:10px;
}
.machine-title{
  font-weight:600;
}
.machine-header small{
  font-size:0.78rem;
  color:#6b7280;
}
.inline{
  display:flex;
  flex-wrap:wrap;
  gap:10px;
}
.inline > div{
  flex:1 1 160px;
}

/* botones */
button{
  background:#111827;
  color:#f9fafb;
  border:none;
  border-radius:999px;
  padding:8px 18px;
  cursor:pointer;
}
button.secondary-btn{
  background:#000000;
}
button:disabled{
  opacity:0.65;
  cursor:not-allowed;
}

/* resultado */
.result{
  margin-top:22px;
  padding:16px 18px;
  border-radius:14px;
  background:#f9fafb;
  border:1px solid #e5e7eb;
  font-size:0.9rem;
}
table{
  border-collapse:collapse;
  width:100%;
  margin-top:10px;
}
th,td{
  border:1px solid #e5e7eb;
  padding:6px;
  font-size:0.85rem;
  text-align:center;
}

/* responsive */
@media (max-width:800px){
  .navbar{
    padding:10px 16px;
    flex-wrap:wrap;
    gap:8px;
  }
  .page-wrapper{
    margin-top:20px;
    padding:0 12px;
  }
  .card{
    padding:18px 16px 22px;
  }
}
</style>
"""

@router.get("/app/taller-punzonado", response_class=HTMLResponse)
def app_taller_punzonado():
    return HTMLResponse(FORM_STYLE + """
<header class="navbar">
  <div class="brand">
    <div class="brand-logo">
      <img src="/static/img/logo_hd.png" alt="Hunter Douglas">
    </div>
    <div class="brand-divider"></div>
    <div class="brand-logo">
      <img src="/static/img/logo_udd.png" alt="Universidad del Desarrollo">
    </div>
  </div>

  <nav>
    <ul class="nav-menu">
      <li><a href="/" class="nav-link">Inicio</a></li>

      <li>
        <span class="nav-link">Tomar tiempos ▾</span>
        <div class="dropdown">
          <a href="/app/real">
            Tiempos REALES
            <span>Captura directa en taller.</span>
          </a>
          <a href="/app/experiencia">
            Tiempos EXPERIENCIA
            <span>Estimación de jefes y operarios.</span>
          </a>
          <a href="/app/nominal">
            Tiempos NOMINALES
            <span>Valores estándar para planificación.</span>
          </a>
          <a href="/app/analisis">
            Análisis de datos
            <span>Histogramas, promedios y outliers.</span>
          </a>
        </div>
      </li>

      <li>
        <span class="nav-link">Calculadoras ▾</span>
        <div class="dropdown">
          <a href="/app/calculo">
            Paneles compuestos
            <span>Capacidad del horno y días del pedido.</span>
          </a>
          <a href="/app/pintura-liquida">
            Línea de pintura líquida
            <span>Tiempo estimado por rollo.</span>
          </a>
          <a href="/app/taller-pintura">
            Taller de pintura
            <span>Tiempo de pintado para líneas sobre riel.</span>
          </a>
          <a href="/app/taller-punzonado">
            Taller de punzonado
            <span>Secuencia de 5 máquinas del taller.</span>
          </a>
        </div>
      </li>

      <li>
        <a href="/admin/login" class="cta-btn">Modo admin</a>
      </li>
    </ul>
  </nav>
</header>

<div class="page-wrapper">
  <div class="card">
    <h2>🛠️ Calculadora – Taller de punzonado</h2>
    <p class="small">
      Esta calculadora estima el tiempo nominal de un pedido que pasa por hasta <b>5 máquinas</b> del
      taller de punzonado. Para cada máquina puedes decidir si se usa o no, cuántas unidades
      procesa y el <b>orden en el flujo</b> (1 = primero, 2 = segundo, etc.).
      <br><br>
      El resultado muestra:
      <ul>
        <li>Tiempo por máquina (setup, proceso, desmontaje y total).</li>
        <li>Tiempo total estimado del taller para el pedido.</li>
        <li>Tiempo promedio por unidad del pedido.</li>
      </ul>
      Nota: por "unidades" puedes entender planchas, piezas o productos, según cómo se alimente la máquina.
    </p>

    <h3>Datos generales del pedido</h3>

    <label for="cantidad_global">Cantidad total de productos del pedido (unidades finales)</label>
    <input type="number" id="cantidad_global" min="1" step="1" placeholder="ej: 500">

    <p class="small">
      Esta cantidad se usa sólo para calcular el <b>tiempo promedio por unidad del pedido</b>.
      En cada máquina, la "cantidad de unidades" son las piezas/planchas que pasan por esa máquina.
    </p>

    <!-- Punzonadora CNC -->
    <div class="machine-card">
      <div class="machine-header">
        <div>
          <span class="machine-title">1️⃣ Punzonadora CNC (planchas con perforaciones)</span><br>
          <small>Usa tabla nominal de perforaciones vs. tiempo de proceso.</small>
        </div>
        <div class="inline">
          <div>
            <label style="margin-top:0;">
              <input type="checkbox" id="use_cnc"> Incluir máquina
            </label>
          </div>
          <div>
            <label style="margin-top:0;">Orden en el flujo</label>
            <input type="number" id="orden_cnc" min="1" step="1" placeholder="ej: 1">
          </div>
        </div>
      </div>

      <div class="inline">
        <div>
          <label>Cantidad de unidades procesadas (planchas)</label>
          <input type="number" id="cant_cnc" min="1" step="1" placeholder="ej: 20">
        </div>
        <div>
          <label>Perforaciones por unidad</label>
          <input type="number" id="perfs_cnc" min="1" step="1" placeholder="ej: 1000">
        </div>
      </div>
      <p class="small">
        Setup fijo = 11,8 min, desmontaje = 7,17 min.
        El tiempo de proceso se interpola entre los puntos de ficha (1000 a 5000 perforaciones).
        Para menos de 1000 se asume proporcional y para más de 5000 se congela en el último valor.
      </p>
    </div>

    <!-- Corte y Prensa -->
    <div class="machine-card">
      <div class="machine-header">
        <div>
          <span class="machine-title">2️⃣ Corte y Prensa (bobina a planchas)</span><br>
          <small>Velocidad nominal: 2,36 m/min.</small>
        </div>
        <div class="inline">
          <div>
            <label style="margin-top:0;">
              <input type="checkbox" id="use_cortep"> Incluir máquina
            </label>
          </div>
          <div>
            <label style="margin-top:0;">Orden en el flujo</label>
            <input type="number" id="orden_cortep" min="1" step="1" placeholder="ej: 1">
          </div>
        </div>
      </div>

      <div class="inline">
        <div>
          <label>Cantidad de unidades procesadas (planchas)</label>
          <input type="number" id="cant_cortep" min="1" step="1" placeholder="ej: 40">
        </div>
        <div>
          <label>Largo por unidad (m)</label>
          <input type="number" id="largo_cortep" min="0.01" step="0.01" placeholder="ej: 2.5">
        </div>
      </div>
      <p class="small">
        Setup fijo = 5 min, desmontaje = 5 min. El tiempo de proceso se calcula como
        <b>metros totales / 2,36 m/min</b>.
      </p>
    </div>

    <!-- Plegadora -->
    <div class="machine-card">
      <div class="machine-header">
        <div>
          <span class="machine-title">3️⃣ Plegadora (dobleces manuales)</span><br>
          <small>Tiempo por pliegue según área de la pieza.</small>
        </div>
        <div class="inline">
          <div>
            <label style="margin-top:0;">
              <input type="checkbox" id="use_pleg"> Incluir máquina
            </label>
          </div>
          <div>
            <label style="margin-top:0;">Orden en el flujo</label>
            <input type="number" id="orden_pleg" min="1" step="1" placeholder="ej: 2">
          </div>
        </div>
      </div>

      <div class="inline">
        <div>
          <label>Cantidad de unidades dobladas (piezas)</label>
          <input type="number" id="cant_pleg" min="1" step="1" placeholder="ej: 200">
        </div>
        <div>
          <label>Área de la pieza (m²)</label>
          <input type="number" id="area_pleg" min="0.1" step="0.01" placeholder="ej: 0.8">
        </div>
        <div>
          <label>Pliegues por pieza</label>
          <input type="number" id="pliegues_pleg" min="1" step="1" placeholder="ej: 2">
        </div>
      </div>
      <p class="small">
        Setup fijo = 10 min, desmontaje = 6,88 min.
        Para área entre 0,5 y 1 m² se usa 1,29 min/pliegue.
        Para área entre 1 y 4 m² se usa 1,21 min/pliegue.
        Si el área queda fuera de rango, se aproxima usando el tramo más cercano.
      </p>
    </div>

    <!-- Cortadora Láser -->
    <div class="machine-card">
      <div class="machine-header">
        <div>
          <span class="machine-title">4️⃣ Cortadora láser</span><br>
          <small>Velocidad nominal de corte: 1,35 m/min.</small>
        </div>
        <div class="inline">
          <div>
            <label style="margin-top:0;">
              <input type="checkbox" id="use_laser"> Incluir máquina
            </label>
          </div>
          <div>
            <label style="margin-top:0;">Orden en el flujo</label>
            <input type="number" id="orden_laser" min="1" step="1" placeholder="ej: 3">
          </div>
        </div>
      </div>

      <div class="inline">
        <div>
          <label>Cantidad de unidades cortadas (piezas)</label>
          <input type="number" id="cant_laser" min="1" step="1" placeholder="ej: 300">
        </div>
        <div>
          <label>Largo total de corte por unidad (m)</label>
          <input type="number" id="corte_laser" min="0.01" step="0.01" placeholder="ej: 1.6">
        </div>
        <div>
          <label>Set-up (min)</label>
          <input type="number" id="setup_laser" min="0" step="0.1" placeholder="ej: 8">
        </div>
        <div>
          <label>Desmontaje (min)</label>
          <input type="number" id="desm_laser" min="0" step="0.1" placeholder="ej: 5">
        </div>
      </div>
      <p class="small">
        Si aún no tienes medidos setup/desmontaje, puedes dejarlos en 0 y solo se considerará
        el tiempo de proceso: metros totales / 1,35 m/min.
      </p>
    </div>

    <!-- Punzonadora en línea / DALCO -->
    <div class="machine-card">
      <div class="machine-header">
        <div>
          <span class="machine-title">5️⃣ Punzonadora en línea (DALCO)</span><br>
          <small>Velocidad según largo de la pieza.</small>
        </div>
        <div class="inline">
          <div>
            <label style="margin-top:0;">
              <input type="checkbox" id="use_dalco"> Incluir máquina
            </label>
          </div>
          <div>
            <label style="margin-top:0;">Orden en el flujo</label>
            <input type="number" id="orden_dalco" min="1" step="1" placeholder="ej: 4">
          </div>
        </div>
      </div>

      <div class="inline">
        <div>
          <label>Cantidad de unidades procesadas (piezas)</label>
          <input type="number" id="cant_dalco" min="1" step="1" placeholder="ej: 400">
        </div>
        <div>
          <label>Largo de la pieza (m)</label>
          <input type="number" id="largo_dalco" min="0.01" step="0.01" placeholder="ej: 0.9">
        </div>
      </div>
      <p class="small">
        Setup fijo = 17,29 min, desmontaje = 9,92 min.
        Para largo &lt; 1 m se usa 1,26 m/min; para largo ≥ 1 m se usa 1,35 m/min.
        El tiempo de proceso se calcula como metros totales / velocidad.
      </p>
    </div>

    <br>
    <button type="button" onclick="calcularPunzonado()">Calcular taller de punzonado</button>
    <p id="msg" class="small"></p>

    <div id="resultadoPunzonado" class="result" style="display:none;"></div>

    <button type="button" class="secondary-btn" style="margin-top:20px" onclick="window.location.href='/'">
      ⬅ Volver al inicio
    </button>
  </div>
</div>

<script>
// ---------- Helpers numéricos ----------
function toNumber(id){
  const v = parseFloat(document.getElementById(id).value);
  return isNaN(v) ? null : v;
}
function formatMin(min){
  if (!isFinite(min)) return '-';
  const h = Math.floor(min / 60);
  const m = min - h*60;
  if (h <= 0) return m.toFixed(1) + ' min';
  return h + ' h ' + m.toFixed(1) + ' min';
}

// ---------- Modelo Punzonadora CNC ----------
const CNC_SETUP_MIN = 11.8;
const CNC_DESM_MIN  = 7.17;
const CNC_POINTS = [
  {perfs: 1000, procMin: 16.42},
  {perfs: 1500, procMin: 24.00},
  {perfs: 2000, procMin: 25.50},
  {perfs: 3500, procMin: 31.14},
  {perfs: 4000, procMin: 33.92},
  {perfs: 5000, procMin: 42.00}
];

function cncTiempoProcesoPorUnidad(perfs){
  if (!perfs || perfs <= 0) return 0;
  // tramo 0–1000: proporcional
  if (perfs <= 1000){
    return (16.42 / 1000.0) * perfs;
  }
  // mayor que último punto: congela en último valor
  const last = CNC_POINTS[CNC_POINTS.length - 1];
  if (perfs >= last.perfs){
    return last.procMin;
  }
  // interpolación lineal por tramos
  for (let i=0; i<CNC_POINTS.length-1; i++){
    const a = CNC_POINTS[i];
    const b = CNC_POINTS[i+1];
    if (perfs >= a.perfs && perfs <= b.perfs){
      const t = (perfs - a.perfs) / (b.perfs - a.perfs);
      return a.procMin + t * (b.procMin - a.procMin);
    }
  }
  return last.procMin; // fallback
}

// ---------- Modelo Corte y Prensa ----------
const CORTEP_SETUP_MIN = 5.0;
const CORTEP_DESM_MIN  = 5.0;
const CORTEP_V_M_PER_MIN = 2.36;

// ---------- Modelo Plegadora ----------
const PLEG_SETUP_MIN = 10.0;
const PLEG_DESM_MIN  = 6.88;

function plegTiempoPorPliegue(area){
  if (!area || area <= 0) return 0;
  if (area < 0.5) return 1.29; // aprox al primer tramo
  if (area <= 1.0) return 1.29;
  if (area <= 4.0) return 1.21;
  return 1.21; // aprox tramo superior si se pasa
}

// ---------- Modelo Cortadora Láser ----------
const LASER_V_M_PER_MIN = 1.35;

// ---------- Modelo Punzonadora en Línea (DALCO) ----------
const DALCO_SETUP_MIN = 17.29;
const DALCO_DESM_MIN  = 9.92;

function dalcoVelocidad(largo){
  if (!largo || largo <= 0) return null;
  if (largo < 1.0) return 1.26;
  return 1.35;
}

// ---------- Cálculo general ----------
function calcularPunzonado(){
  const msg = document.getElementById("msg");
  const out = document.getElementById("resultadoPunzonado");
  msg.textContent = "";
  out.style.display = "none";
  out.innerHTML = "";

  const cantGlobal = toNumber("cantidad_global");

  const maquinas = [];

  // --- CNC ---
  if (document.getElementById("use_cnc").checked){
    const orden = toNumber("orden_cnc") || 999;
    const cant  = toNumber("cant_cnc");
    const perfs = toNumber("perfs_cnc");
    if (!cant || cant <= 0 || !perfs || perfs <= 0){
      msg.textContent = "⚠️ Completa cantidad y perforaciones para la Punzonadora CNC.";
      return;
    }
    const tProcUnidad = cncTiempoProcesoPorUnidad(perfs); // min por unidad
    const tProcLote   = tProcUnidad * cant;
    const tTotal      = CNC_SETUP_MIN + tProcLote + CNC_DESM_MIN;
    maquinas.push({
      nombre: "Punzonadora CNC",
      orden,
      setup: CNC_SETUP_MIN,
      proc: tProcLote,
      desm: CNC_DESM_MIN,
      total: tTotal
    });
  }

  // --- Corte y Prensa ---
  if (document.getElementById("use_cortep").checked){
    const orden = toNumber("orden_cortep") || 999;
    const cant  = toNumber("cant_cortep");
    const largo = toNumber("largo_cortep");
    if (!cant || cant <= 0 || !largo || largo <= 0){
      msg.textContent = "⚠️ Completa cantidad y largo para Corte y Prensa.";
      return;
    }
    const metros = cant * largo;
    const tProcLote = metros / CORTEP_V_M_PER_MIN;
    const tTotal = CORTEP_SETUP_MIN + tProcLote + CORTEP_DESM_MIN;
    maquinas.push({
      nombre: "Corte y Prensa",
      orden,
      setup: CORTEP_SETUP_MIN,
      proc: tProcLote,
      desm: CORTEP_DESM_MIN,
      total: tTotal
    });
  }

  // --- Plegadora ---
  if (document.getElementById("use_pleg").checked){
    const orden = toNumber("orden_pleg") || 999;
    const cant  = toNumber("cant_pleg");
    const area  = toNumber("area_pleg");
    const plieg = toNumber("pliegues_pleg");
    if (!cant || cant <= 0 || !area || area <= 0 || !plieg || plieg <= 0){
      msg.textContent = "⚠️ Completa cantidad, área y pliegues para la Plegadora.";
      return;
    }
    const tPorPliegue = plegTiempoPorPliegue(area);
    const tProcLote = cant * plieg * tPorPliegue;
    const tTotal = PLEG_SETUP_MIN + tProcLote + PLEG_DESM_MIN;
    maquinas.push({
      nombre: "Plegadora",
      orden,
      setup: PLEG_SETUP_MIN,
      proc: tProcLote,
      desm: PLEG_DESM_MIN,
      total: tTotal
    });
  }

  // --- Láser ---
  if (document.getElementById("use_laser").checked){
    const orden = toNumber("orden_laser") || 999;
    const cant  = toNumber("cant_laser");
    const corte = toNumber("corte_laser");
    const setup = toNumber("setup_laser") || 0;
    const desm  = toNumber("desm_laser") || 0;
    if (!cant || cant <= 0 || !corte || corte <= 0){
      msg.textContent = "⚠️ Completa cantidad y largo de corte para la Cortadora láser.";
      return;
    }
    const metros = cant * corte;
    const tProcLote = metros / LASER_V_M_PER_MIN;
    const tTotal = setup + tProcLote + desm;
    maquinas.push({
      nombre: "Cortadora láser",
      orden,
      setup,
      proc: tProcLote,
      desm,
      total: tTotal
    });
  }

  // --- DALCO ---
  if (document.getElementById("use_dalco").checked){
    const orden = toNumber("orden_dalco") || 999;
    const cant  = toNumber("cant_dalco");
    const largo = toNumber("largo_dalco");
    if (!cant || cant <= 0 || !largo || largo <= 0){
      msg.textContent = "⚠️ Completa cantidad y largo para la Punzonadora en línea (DALCO).";
      return;
    }
    const v = dalcoVelocidad(largo);
    if (!v){
      msg.textContent = "⚠️ Largo inválido para DALCO.";
      return;
    }
    const metros = cant * largo;
    const tProcLote = metros / v;
    const tTotal = DALCO_SETUP_MIN + tProcLote + DALCO_DESM_MIN;
    maquinas.push({
      nombre: "Punzonadora en línea (DALCO)",
      orden,
      setup: DALCO_SETUP_MIN,
      proc: tProcLote,
      desm: DALCO_DESM_MIN,
      total: tTotal
    });
  }

  if (maquinas.length === 0){
    msg.textContent = "⚠️ Activa al menos una máquina del taller.";
    return;
  }

  // ordenar por flujo
  maquinas.sort((a,b)=>a.orden - b.orden);

  // acumulados
  let totalSetup = 0;
  let totalProc  = 0;
  let totalDesm  = 0;
  let totalAll   = 0;
  maquinas.forEach(m=>{
    totalSetup += m.setup;
    totalProc  += m.proc;
    totalDesm  += m.desm;
    totalAll   += m.total;
  });

  let html = `
    <h3>📊 Detalle por máquina (según orden de flujo)</h3>
    <table>
      <thead>
        <tr>
          <th>Orden</th>
          <th>Máquina</th>
          <th>Set-up (min)</th>
          <th>Proceso (min)</th>
          <th>Desmontaje (min)</th>
          <th>Total máquina (min)</th>
        </tr>
      </thead>
      <tbody>
  `;
  maquinas.forEach(m=>{
    html += `
      <tr>
        <td>${isFinite(m.orden) ? m.orden : '—'}</td>
        <td>${m.nombre}</td>
        <td>${m.setup.toFixed(2)}</td>
        <td>${m.proc.toFixed(2)}</td>
        <td>${m.desm.toFixed(2)}</td>
        <td>${m.total.toFixed(2)}</td>
      </tr>
    `;
  });
  html += `
      </tbody>
    </table>
    <hr>
    <h3>⏱️ Resumen del taller</h3>
    <p><b>Set-up total:</b> ${totalSetup.toFixed(2)} min</p>
    <p><b>Proceso total:</b> ${totalProc.toFixed(2)} min</p>
    <p><b>Desmontaje total:</b> ${totalDesm.toFixed(2)} min</p>
    <p><b>Tiempo total estimado del taller:</b> ${totalAll.toFixed(2)} min (${formatMin(totalAll)})</p>
  `;

  if (cantGlobal && cantGlobal > 0){
    const tUnit = totalAll / cantGlobal;
    html += `
      <p><b>Tiempo promedio por unidad del pedido:</b> ${tUnit.toFixed(2)} min/unidad</p>
      <p class="small">
        Se divide el tiempo total del taller por la cantidad total de productos del pedido.
        Si algunas máquinas procesan menos unidades que otras, interpreta este valor como
        un promedio global del pedido.
      </p>
    `;
  } else {
    html += `
      <p class="small">
        Si quieres el tiempo promedio por unidad del pedido, ingresa la
        <b>cantidad total de productos</b> en la parte superior.
      </p>
    `;
  }

  out.innerHTML = html;
  out.style.display = "block";
}
</script>
""")
