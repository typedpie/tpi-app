# calc_taller_pintura.py
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["taller_pintura"])

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

@router.get("/app/taller-pintura", response_class=HTMLResponse)
def app_taller_pintura():
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
            Taller de pintura (riel)
            <span>Tiempo estimado para productos colgados.</span>
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
    <h2>🎨 Calculadora – Taller de pintura (líneas sobre riel)</h2>

    <p class="small">
      Esta calculadora estima el tiempo de recorrido en las dos líneas de pintura del taller:
      <br><br>
      • <b>Línea electrostática</b>: riel con forma de óvalo completo.<br>
      • <b>Línea electro-líquida</b>: solo funciona un tramo recto de <b>56 m</b>.
      <br><br>
      Se asume una velocidad de línea equivalente a <b>95 cm/min</b> para la perilla ≈ 8 (dato medido en planta).
      Para la línea electrostática se aproxima la longitud del óvalo como:
      <b>2·56 m + π·5 m ≈ 128 m</b>.
      <br>
      <span class="small">
        (Supuesto geométrico: dos tramos rectos de 56 m separados por curvas de ancho 5 m.)
      </span>
    </p>

    <h3>Parámetros del pedido</h3>

    <label for="linea">Selecciona la línea de pintura</label>
    <select id="linea">
      <option value="">-- selecciona --</option>
      <option value="electroestatica">Línea electrostática (óvalo completo)</option>
      <option value="electroliquida">Línea electro-líquida (tramo recto de 56 m)</option>
    </select>

    <label for="cantidad">Cantidad de productos a pintar (unidades)</label>
    <input type="number" id="cantidad" min="1" step="1" placeholder="ej: 120">

    <button type="button" onclick="calcularTallerPintura()">Calcular tiempo</button>
    <p id="msg" class="small"></p>

    <div id="resultadoTallerPintura" class="result" style="display:none;"></div>

    <button type="button" class="secondary-btn" style="margin-top:20px" onclick="window.location.href='/'">
      ⬅ Volver al inicio
    </button>
  </div>
</div>

<script>
// --- Constantes de modelo ---
// Velocidad medida: 95 cm/min cuando la perilla está alrededor de 8.
// La usamos como velocidad base de ambas líneas.
const SPEED_CM_PER_MIN = 95;
const SPEED_M_PER_MIN  = SPEED_CM_PER_MIN / 100.0;

// Geometría (supuesto):
// - Tramo recto medido: 56 m
// - Ancho del óvalo: 5 m
// Línea electrostática: óvalo completo -> 2*56 + π*5
// Línea electro-líquida: solo el tramo recto de 56 m
const STRAIGHT_LENGTH_M = 56;   // longitud de cada tramo recto
const OVAL_WIDTH_M      = 5;    // separación entre rectas (diámetro de curvas)
const A = STRAIGHT_LENGTH_M/2;  // semi-eje mayor
const B = OVAL_WIDTH_M/2;       // Semi-eje menor
const LENGTH_ELECTROESTATICA_M = Math.PI * (3*(A+B) - Math.sqrt((3*A+B)*(A+3*B)));                                             
const LENGTH_ELECTROLIQUIDA_M  = STRAIGHT_LENGTH_M;

// Helpers de formato
function formatMinToHM(minTotal){
  const horas = Math.floor(minTotal / 60);
  const minutos = Math.round(minTotal - horas * 60);
  if (horas <= 0){
    return `${minutos} min`;
  }
  return `${horas} h ${minutos} min`;
}

function calcularTallerPintura(){
  const linea = document.getElementById("linea").value;
  const cantidad = parseInt(document.getElementById("cantidad").value || "0", 10);
  const salida = document.getElementById("resultadoTallerPintura");
  const msg = document.getElementById("msg");

  msg.textContent = "";
  salida.style.display = "none";
  salida.innerHTML = "";

  if (!linea){
    msg.textContent = "⚠️ Selecciona la línea de pintura.";
    return;
  }
  if (!cantidad || cantidad <= 0){
    msg.textContent = "⚠️ Ingresa una cantidad de productos mayor a 0.";
    return;
  }

  let distancia_m = 0;
  let descripcionLinea = "";

  if (linea === "electroestatica"){
    distancia_m = LENGTH_ELECTROESTATICA_M;
    descripcionLinea = "Línea electrostática (óvalo completo).";
  } else if (linea === "electroliquida"){
    distancia_m = LENGTH_ELECTROLIQUIDA_M;
    descripcionLinea = "Línea electro-líquida (tramo recto de 56 m).";
  } else {
    msg.textContent = "⚠️ Línea no reconocida.";
    return;
  }

  // Tiempo unitario = distancia / velocidad
  const tiempoUnitMin = distancia_m / SPEED_M_PER_MIN;  // minutos por producto
  const tiempoPedidoMin = tiempoUnitMin * cantidad;     // simplificación: N × tiempo unitario

  const tiempoUnitTexto   = `${tiempoUnitMin.toFixed(1)} min por producto`;
  const tiempoPedidoTexto = `${tiempoPedidoMin.toFixed(1)} min (~${formatMinToHM(tiempoPedidoMin)})`;

  salida.innerHTML = `
    <p><strong>Línea seleccionada:</strong> ${descripcionLinea}</p>
    <p><strong>Velocidad de línea asumida:</strong> ${SPEED_M_PER_MIN.toFixed(2)} m/min (a partir de 95 cm/min).</p>
    <p><strong>Distancia recorrida por producto:</strong> ${distancia_m.toFixed(1)} m</p>
    <hr>
    <p><strong>Cantidad de productos:</strong> ${cantidad} unidades</p>
    <p><strong>Tiempo estimado por producto:</strong> ${tiempoUnitTexto}</p>
    <p><strong>Tiempo estimado para todo el pedido:</strong> ${tiempoPedidoTexto}</p>
    <p class="small">
      Nota: se asume que cada producto recorre la longitud completa de la línea a velocidad constante
      y se aproxima el tiempo total como <b>cantidad × tiempo unitario</b>.
      Nota2: los tiempos aun no se estan ajustando a la experiencia por operario que es de 1 hora 40 minutos
    </p>
  `;
  salida.style.display = "block";
}
</script>
""")
