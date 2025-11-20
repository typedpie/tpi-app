from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["calculo_sliding"])

FORM_STYLE = """
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{
  font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
  background:#f3f4f6;
  color:#0f172a;
}
/* Navbar y Layout */
.navbar{
  position:sticky; top:0; z-index:40; display:flex; align-items:center; justify-content:space-between;
  padding:12px 56px; background:linear-gradient(90deg,#020617,#111827); color:#f9fafb;
  box-shadow:0 10px 30px rgba(15,23,42,0.45);
}
.brand{ display:flex; align-items:center; gap:18px; }
.brand-logo img{ height:30px; }
.brand-divider{ width:1px; height:24px; background:rgba(248,250,252,0.35); }
.nav-menu{ list-style:none; display:flex; align-items:center; gap:24px; font-size:0.82rem; text-transform:uppercase; letter-spacing:0.08em; }
.nav-menu>li{ position:relative; cursor:pointer; padding-bottom:10px; }
.nav-link{ color:#f9fafb; text-decoration:none; padding-bottom:3px; }
.nav-link:hover{ border-bottom:2px solid #f97316; }

.dropdown{
  display:none; position:absolute; top:60%; left:0; margin-top:6px;
  background:rgba(15,23,42,0.97); border-radius:10px; min-width:240px; padding:10px 0;
  box-shadow:0 18px 40px rgba(0,0,0,0.45); z-index:50;
}
.nav-menu li:hover .dropdown{ display:block; }
.dropdown a{ display:block; padding:8px 16px; font-size:0.8rem; color:#e5e7eb; white-space:nowrap; }
.dropdown a span{ display:block; font-size:0.72rem; color:#9ca3af; }
.dropdown a:hover{ background:rgba(249,115,22,0.08); color:#ffffff; }

.cta-btn{
  background:#f97316; color:#111827; border-radius:999px; padding:8px 18px;
  font-size:0.8rem; font-weight:600; border:none; text-decoration:none;
  text-transform:uppercase; letter-spacing:0.08em; box-shadow:0 10px 24px rgba(249,115,22,0.4);
}

.page-wrapper{ max-width:960px; margin:32px auto 40px; padding:0 20px; }
.card{
  background:#ffffff; border-radius:18px; box-shadow:0 16px 40px rgba(15,23,42,0.12);
  padding:24px 26px 30px; margin-bottom: 24px;
}
h2{ font-size:1.6rem; margin-bottom:10px; }
h3{ margin-top:24px; margin-bottom:8px; font-size:1.05rem; border-bottom: 1px solid #eee; padding-bottom: 6px;}
.small{ font-size:0.86rem; color:#6b7280; }

label{ display:block; margin-top:12px; margin-bottom:4px; font-weight:600; font-size:0.93rem; }
input, select{ width:100%; padding:10px 12px; border-radius:12px; border:1px solid #d1d5db; outline:none; font-size:0.95rem; }
input:focus{ border-color:#f97316; box-shadow:0 0 0 1px rgba(249,115,22,0.35); }
button{ background:#111827; color:#f9fafb; border:none; border-radius:999px; padding:8px 18px; cursor:pointer; margin-top:15px; font-size:0.95rem;}
.secondary-btn{ background:#000000; }
.result{ margin-top:15px; padding:14px; border-radius:10px; background:#f0fdf4; border:1px solid #bbf7d0; color:#14532d; font-weight:500; display:none; }
.metric-box { display: flex; gap: 15px; flex-wrap: wrap; margin-top: 10px;}
.metric { background: #f8fafc; padding: 10px; border-radius: 8px; border: 1px solid #e2e8f0; flex: 1; min-width: 140px;}
.metric span { display: block; font-size: 0.75rem; color: #64748b; text-transform: uppercase; }
.metric strong { font-size: 1.1rem; color: #0f172a; }

@media (max-width:800px){ .navbar{ padding:10px 16px; flex-wrap:wrap; } .page-wrapper{ padding:0 12px; } }
</style>
"""

@router.get("/app/sliding-folding", response_class=HTMLResponse)
def app_sliding():
    return HTMLResponse(FORM_STYLE + """
<header class="navbar">
  <div class="brand">
    <div class="brand-logo"><img src="/static/img/logo_hd.png" alt="Hunter Douglas"></div>
    <div class="brand-divider"></div>
    <div class="brand-logo"><img src="/static/img/logo_udd.png" alt="UDD"></div>
  </div>
  <nav>
    <ul class="nav-menu">
      <li><a href="/" class="nav-link">Inicio</a></li>
      <li>
        <span class="nav-link">Calculadoras ▾</span>
        <div class="dropdown">
          <a href="/app/calculo">Paneles compuestos</a>
          <a href="/app/pintura-liquida">Pintura líquida</a>
          <a href="/app/taller-pintura">Taller pintura</a>
          <a href="/app/sliding-folding">Sliding & Folding</a>
        </div>
      </li>
      <li><a href="/admin/login" class="cta-btn">Admin</a></li>
    </ul>
  </nav>
</header>

<div class="page-wrapper">
  
  <div class="card">
    <h2>🪚 1. Tronzadora (Corte de perfiles)</h2>
    <p class="small">Cálculo para mallas Quadrobrise 32x32. Se asume que el perfil base se corta en 3 partes.</p>
    
    <label>Cantidad de Mallas a fabricar</label>
    <input type="number" id="tron_cantidad" placeholder="ej: 10" oninput="calcTronzadora()">
    
    <div class="metric-box">
      <div class="metric"><span>Perfiles req.</span><strong id="tron_perfiles">0</strong></div>
      <div class="metric"><span>Ciclos corte</span><strong id="tron_ciclos">0</strong></div>
      <div class="metric"><span>Tiempo total</span><strong id="tron_tiempo">0 min</strong></div>
    </div>
    <p class="small" style="margin-top:10px">
      Supuestos: 22 perfiles/malla. 1 Ciclo = 3 perfiles = 5 minutos. 
      Se calcula por lotes completos (función techo).
    </p>
  </div>

  <div class="card">
    <h2>⚙️ 2. CNC 4 Metros</h2>
    <p class="small">Mecanizado de marcos y mallas para Quadrobrise 32x32.</p>
    
    <div style="display:flex; gap:10px;">
        <div style="flex:1">
            <label>Cant. Marcos</label>
            <input type="number" id="cnc_marcos" placeholder="0">
        </div>
        <div style="flex:1">
            <label>Cant. Mallas</label>
            <input type="number" id="cnc_mallas" placeholder="0">
        </div>
        <div style="flex:1">
            <label>Cant. Escuadras</label>
            <input type="number" id="cnc_escuadras" placeholder="0">
        </div>
    </div>
    <button onclick="calcCNC()">Calcular CNC</button>
    
    <div id="res_cnc" class="result"></div>
    
    <p class="small" style="margin-top:8px">
      Velocidades: Marco (4 perfiles) = 10 min/unid. Malla (26 perfiles) = 1.5 min/perfil. Escuadra = 0.375 min/unid.
    </p>
  </div>

  <div class="card">
    <h2>🔧 3. Ensamblado Manual</h2>
    <p class="small">Tiempos ajustados. Quadrobrise descarta outliers bajos. Brisolcell calculado por complejidad de grilla.</p>
    
    <label>Producto</label>
    <select id="ens_producto" onchange="toggleBrisolcell()">
        <option value="40">Quadrobrise 32x32 (Promedio: ~40 min)</option> 
        
        <option value="brisolcell_calc">Brisolcell (Cálculo por perfiles)</option> 
        
        <option value="40">Nube Acústica (40 min ±5)</option>
        <option value="30">Woodbrise Bamboo 30x18 (30 min)</option>
        <option value="62">Metalbrise Marco C-Frame (Promedio: ~62 min)</option>
    </select>

    <div id="brisolcell_inputs" style="display:none; background:#f8fafc; padding:10px; border-radius:8px; margin-top:10px; border:1px dashed #cbd5e1;">
        <p class="small" style="margin-bottom:5px"><strong>Grilla Brisolcell:</strong></p>
        <div style="display:flex; gap:10px;">
            <div style="flex:1">
                <label style="margin-top:0; font-size:0.8rem">Perf. Verticales</label>
                <input type="number" id="bris_v" placeholder="Ej: 15">
            </div>
            <div style="flex:1">
                <label style="margin-top:0; font-size:0.8rem">Perf. Horizontales</label>
                <input type="number" id="bris_h" placeholder="Ej: 15">
            </div>
        </div>
    </div>
    
    <label>Cantidad de Unidades (Mallas/Paneles)</label>
    <input type="number" id="ens_cantidad" placeholder="10">
    
    <button onclick="calcEnsamblado()">Calcular Ensamble</button>
    <div id="res_ens" class="result"></div>
  </div>

  <div class="card">
    <h2>🏭 4. Otras Máquinas y Embalaje</h2>
    
    <label>Máquina / Proceso</label>
    <select id="otros_proceso">
        <option value="7.25">Cilindradora - Perfil L (Promedio: 7.25 min)</option>
        <option value="2.33">Doble Tronzadora - Perfil Tubular (2.33 min)</option>
        <option value="27.5">Embalaje - Quadrobrise (Promedio: 27.5 min)</option>
        <option value="5">Embalaje - Nube (5 min)</option>
    </select>
    
    <label>Cantidad</label>
    <input type="number" id="otros_cantidad" placeholder="1">
    
    <button onclick="calcOtros()">Calcular</button>
    <div id="res_otros" class="result"></div>
  </div>

  <button type="button" class="secondary-btn" onclick="window.location.href='/'">⬅ Volver al inicio</button>

</div>

<script>
// --- 1. TRONZADORA ---
function calcTronzadora(){
    const mallas = parseFloat(document.getElementById('tron_cantidad').value) || 0;
    // 22 perfiles por malla
    const total_perfiles = mallas * 22; 
    // La maquina corta 1 perfil largo en 3 chicos. 
    // Ciclos = Total perfiles / 3 (redondeado hacia arriba)
    const ciclos = Math.ceil(total_perfiles / 3);
    // 5 min por ciclo
    const tiempo = ciclos * 5;
    
    document.getElementById('tron_perfiles').innerText = total_perfiles;
    document.getElementById('tron_ciclos').innerText = ciclos;
    document.getElementById('tron_tiempo').innerText = tiempo + " min";
}

// --- 2. CNC ---
function calcCNC(){
    const q_marcos = parseFloat(document.getElementById('cnc_marcos').value) || 0;
    const q_mallas = parseFloat(document.getElementById('cnc_mallas').value) || 0;
    const q_escuadras = parseFloat(document.getElementById('cnc_escuadras').value) || 0;
    
    // Marco: 4 perfiles * 2.5 min = 10 min/marco
    const t_marcos = q_marcos * 10;
    
    // Malla: 26 perfiles * 1.5 min/perfil = 39 min/malla
    const t_mallas = q_mallas * (26 * 1.5);
    
    // Escuadras: 0.375 min/unid
    const t_escuadras = q_escuadras * 0.375;
    
    const total = t_marcos + t_mallas + t_escuadras;
    
    const div = document.getElementById('res_cnc');
    div.style.display = 'block';
    div.innerHTML = `⏱️ Tiempo Total CNC: <b>${total.toFixed(1)} min</b> <br> <small>(${ (total/60).toFixed(2) } horas)</small>`;
}

// --- 3. ENSAMBLADO (LÓGICA NUEVA BRISOLCELL) ---
function toggleBrisolcell(){
    const val = document.getElementById('ens_producto').value;
    const div = document.getElementById('brisolcell_inputs');
    // Si selecciona Brisolcell, mostramos los inputs de perfiles
    div.style.display = (val === 'brisolcell_calc') ? 'block' : 'none';
}

function calcEnsamblado(){
    const selector = document.getElementById('ens_producto');
    const tipo = selector.value;
    const q = parseFloat(document.getElementById('ens_cantidad').value) || 0;
    
    let t_unitario = 0;
    let detalle = "";

    if (tipo === 'brisolcell_calc') {
        // Lógica Brisolcell: Perfiles V x H
        const v = parseFloat(document.getElementById('bris_v').value) || 0;
        const h = parseFloat(document.getElementById('bris_h').value) || 0;
        
        if(v === 0 || h === 0){
            const divErr = document.getElementById('res_ens');
            divErr.style.display = 'block';
            divErr.innerHTML = "⚠️ Para Brisolcell, ingresa la cantidad de perfiles Verticales y Horizontales.";
            return;
        }

        // SUPUESTO: 1.5 min por perfil (encalillado/cruce) + 15 min armado de marco base
        // Una grilla 15x15 = 30 perfiles * 1.5 = 45 min + 15 marco = 60 min.
        t_unitario = ((v + h) * 1.5) + 15;
        detalle = `(Grilla ${v}V x ${h}H + marco)`;
        
    } else {
        // Lógica estándar (promedios fijos)
        t_unitario = parseFloat(tipo);
        detalle = `(Promedio ~${t_unitario} min/unid)`;
    }
    
    const total = t_unitario * q;
    const horas = (total / 60).toFixed(1);
    
    const div = document.getElementById('res_ens');
    div.style.display = 'block';
    div.innerHTML = `
        ⏱️ <strong>Tiempo Total Ensamble: ${total.toFixed(0)} min</strong> 
        <span style="color:#64748b; margin-left:8px">(${horas} horas)</span>
        <br>
        <small style="color:#475569">Base: ${t_unitario.toFixed(1)} min/unidad ${detalle}</small>
    `;
}

// --- 4. OTROS ---
function calcOtros(){
    const t_unit = parseFloat(document.getElementById('otros_proceso').value);
    const q = parseFloat(document.getElementById('otros_cantidad').value) || 0;
    
    const total = t_unit * q;
    const div = document.getElementById('res_otros');
    div.style.display = 'block';
    div.innerHTML = `⏱️ Estimación: <b>${total.toFixed(1)} min</b>`;
}
</script>
""")