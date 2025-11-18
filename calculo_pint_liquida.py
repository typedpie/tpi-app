# calculo_pint_liquida.py
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["calculoo"])

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

/* NAVBAR (igual que home pero compacto) */
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
  max-width:960px;
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
input, button{
  font-size:0.95rem;
}
input{
  width:100%;
  padding:10px 12px;
  border-radius:12px;
  border:1px solid #d1d5db;
  outline:none;
}
input:focus{
  border-color:#f97316;
  box-shadow:0 0 0 1px rgba(249,115,22,0.35);
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

@router.get("/app/pintura-liquida", response_class=HTMLResponse)
def app_pintura_liquida():
    # Aquí no importamos nada extra: toda la lógica está en el JS de abajo.
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
    <h2>🎨 Calculadora – Línea de pintura líquida</h2>
    <p class="small">
      Modelo basado en el dato real: un rollo de <b>660 m</b> y <b>0,5 mm</b> de espesor
      se corre a <b>10,2 m/min</b> y demora aproximadamente <b>64 min</b>.
      <br>
      Se asume que la velocidad de la línea es <b>inversamente proporcional al espesor</b> del rollo.
      <br>
      Rango de uso: largo entre 1 y 700 m, espesor entre 0,5 y 1,5 mm.
    </p>

    <h3>Ingresar parámetros del rollo</h3>

    <label for="largoRollo">Largo del rollo (m)</label>
    <input type="number" id="largoRollo" min="1" max="700" step="1" placeholder="660">

    <label for="espesorRollo">Espesor del rollo (mm)</label>
    <input type="number" id="espesorRollo" min="0.5" max="1.5" step="0.1" placeholder="0.5">

    <button type="button" onclick="calcularPinturaLiquida()">Calcular tiempo</button>
    <p id="msg" class="small"></p>

    <div id="resultadoPinturaLiquida" class="result" style="display:none;"></div>

    <button type="button" class="secondary-btn" style="margin-top:20px" onclick="window.location.href='/'">
      ⬅ Volver al inicio
    </button>
  </div>
</div>

<script>
// Constantes del modelo
const BASE_SPEED_M_PER_MIN = 10.2;  // m/min para 0,5 mm
const BASE_THICKNESS_MM = 0.5;      // mm
const MIN_LARGO_M = 1;
const MAX_LARGO_M = 700;
const MIN_ESPESOR_MM = 0.5;
const MAX_ESPESOR_MM = 1.5;

// v(e) = v_base * (e_base / e)
// t_min = L / v(e)
function calcularPinturaLiquida(){
  const largoInput = document.getElementById("largoRollo");
  const espesorInput = document.getElementById("espesorRollo");
  const salida = document.getElementById("resultadoPinturaLiquida");
  const msg = document.getElementById("msg");

  msg.textContent = "";
  salida.style.display = "none";
  salida.innerHTML = "";

  const largo = parseFloat(largoInput.value);
  const espesor = parseFloat(espesorInput.value);

  if (isNaN(largo) || isNaN(espesor)) {
    msg.textContent = "⚠️ Ingresa largo y espesor del rollo.";
    return;
  }

  if (largo < MIN_LARGO_M || largo > MAX_LARGO_M) {
    msg.textContent = `⚠️ El largo debe estar entre ${MIN_LARGO_M} y ${MAX_LARGO_M} m.`;
    return;
  }

  if (espesor < MIN_ESPESOR_MM || espesor > MAX_ESPESOR_MM) {
    msg.textContent = `⚠️ El espesor debe estar entre ${MIN_ESPESOR_MM} y ${MAX_ESPESOR_MM} mm.`;
    return;
  }

  const velocidad = BASE_SPEED_M_PER_MIN * (BASE_THICKNESS_MM / espesor); // m/min
  const tiempoMin = largo / velocidad;

  const horas = Math.floor(tiempoMin / 60);
  const minutosRestantes = Math.round(tiempoMin - horas * 60);

  let textoTiempo = `${tiempoMin.toFixed(1)} minutos`;
  if (horas > 0) {
    textoTiempo += ` (aprox. ${horas} h ${minutosRestantes} min)`;
  }

  salida.innerHTML = `
    <p><strong>Velocidad de línea estimada:</strong> ${velocidad.toFixed(2)} m/min</p>
    <p><strong>Tiempo estimado por rollo:</strong> ${textoTiempo}</p>
    <p class="small">
      Supuesto: velocidad inversamente proporcional al espesor, usando como referencia
      el rollo de 660 m y 0,5 mm que corre a 10,2 m/min (≈64 min).
    </p>
  `;
  salida.style.display = "block";
}
</script>
""")
