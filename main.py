from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, condecimal
from sqlalchemy import text
from sqlalchemy.orm import Session
from database import get_db
#------------------------------------
from fastapi import Request
import Os 


app = FastAPI(title="TPI – Captura de Tiempos")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"], allow_credentials=True
)

# -------- Helpers SQL --------
def q1(db: Session, sql: str, params: dict = None):
    return db.execute(text(sql), params or {}).mappings().all()

def q1_one(db: Session, sql: str, params: dict):
    return db.execute(text(sql), params).mappings().fetchone()

def id_by_name(db: Session, table: str, name: str | None):
    if not name: return None
    row = q1_one(db, f"SELECT id_{table} AS id FROM {table} WHERE nombre=:n", {"n": name})
    return int(row["id"]) if row else None

def must(cond: bool, msg: str):
    if not cond: raise HTTPException(400, msg)
#----------admin cambios -----------
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN")  # lo definimos en Render

def check_admin_token(request: Request):
    """Protege las rutas /admin con un token simple via query string ?token=..."""
    if not ADMIN_TOKEN:
        # Si no configuraste ADMIN_TOKEN en Render, no exige token (útil en pruebas locales)
        return
    token = request.query_params.get("token")
    if token != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="No autorizado. Agrega ?token=TU_TOKEN a la URL")

# ===== ADMIN: Home del panel =====
@app.get("/admin", response_class=HTMLResponse)
def admin_home(request: Request):
    check_admin_token(request)
    return f"""
    <html>
      <head><title>Admin TPI</title></head>
      <body style="font-family: system-ui; padding: 16px; max-width: 900px; margin: auto;">
        <h2>🛠️ Panel de administración</h2>
        <p>Selecciona qué quieres revisar:</p>
        <ul>
          <li><a href="/admin/real?token={(ADMIN_TOKEN or '')}">Ver y eliminar <b>tiempos REALES</b></a></li>
          <li><a href="/admin/nominal?token={(ADMIN_TOKEN or '')}">Ver y eliminar <b>tiempos NOMINALES</b></a></li>
        </ul>
        <p><a href="/">⬅ Volver al inicio</a></p>
      </body>
    </html>
    """

# ===== ADMIN: Lista y borrado de TIEMPOS REALES =====
@app.get("/admin/real", response_class=HTMLResponse)
def admin_list_real(request: Request, limit: int = 50, db: Session = Depends(get_db)):
    check_admin_token(request)
    rows = q1(db, """
        SELECT
          tr.id_tiempo_real,
          tr.fecha,                -- si tu columna es created_at, cambia por created_at
          tr.tiempo_min,
          tr.operario,
          p.nombre  AS proceso,
          m.nombre  AS maquina,
          pr.nombre AS producto
        FROM tiempo_real tr
        JOIN proceso  p  ON p.id_proceso  = tr.id_proceso
        JOIN maquina  m  ON m.id_maquina  = tr.id_maquina
        JOIN producto pr ON pr.id_producto = tr.id_producto
        ORDER BY tr.fecha DESC
        LIMIT :lim
    """, {"lim": limit})

    html = [f"""
    <html><head><title>Admin REALES</title></head>
    <body style="font-family: system-ui; padding: 16px; max-width: 1100px; margin: auto;">
      <h2>🧭 Registros REALES recientes</h2>
      <p><a href="/admin?token={(ADMIN_TOKEN or '')}">⬅ Volver al panel</a></p>
      <table border="1" cellpadding="6" cellspacing="0">
        <tr>
          <th>ID</th><th>Fecha</th><th>Proceso</th><th>Máquina</th><th>Producto</th>
          <th>Tiempo (min)</th><th>Operario</th><th>Acciones</th>
        </tr>
    """]
    for r in rows:
        html.append(f"""
        <tr>
          <td>{r['id_tiempo_real']}</td>
          <td>{r['fecha']}</td>
          <td>{r['proceso']}</td>
          <td>{r['maquina']}</td>
          <td>{r['producto']}</td>
          <td>{r['tiempo_min']}</td>
          <td>{r.get('operario') or ''}</td>
          <td>
            <form method="post" action="/admin/real/delete/{r['id_tiempo_real']}?token={(ADMIN_TOKEN or '')}"
                  onsubmit="return confirm('¿Eliminar registro REAL #{r['id_tiempo_real']}?');">
              <button type="submit">❌ Eliminar</button>
            </form>
          </td>
        </tr>
        """)
    html.append("""
      </table>
      <p style="margin-top:10px;">Mostrando últimos registros. Para más filtros, usa Neon directamente.</p>
      <p><a href="/">⬅ Volver al inicio</a></p>
    </body></html>
    """)
    return HTMLResponse("".join(html))

@app.post("/admin/real/delete/{id_tiempo_real}")
def admin_delete_real(id_tiempo_real: int, request: Request, db: Session = Depends(get_db)):
    check_admin_token(request)
    db.execute(text("DELETE FROM tiempo_real WHERE id_tiempo_real = :id"), {"id": id_tiempo_real})
    db.commit()
    return HTMLResponse(f"""
      <html><body style="font-family: system-ui; padding: 16px;">
        <p>Registro REAL #{id_tiempo_real} eliminado.</p>
        <p><a href="/admin/real?token={(ADMIN_TOKEN or '')}">⬅ Volver a la lista</a></p>
      </body></html>
    """)

# ===== ADMIN: Lista y borrado de TIEMPOS NOMINALES =====
@app.get("/admin/nominal", response_class=HTMLResponse)
def admin_list_nominal(request: Request, limit: int = 100, db: Session = Depends(get_db)):
    check_admin_token(request)
    rows = q1(db, """
        SELECT
          tn.id_tiempo_nominal,
          tn.tiempo_min,
          tn.fuente,
          tn.valor_original,
          tn.unidad_original,
          tn.notas,
          tn.fecha_fuente,
          p.nombre  AS proceso,
          m.nombre  AS maquina,
          pr.nombre AS producto
        FROM tiempo_nominal tn
        JOIN proceso  p  ON p.id_proceso  = tn.id_proceso
        JOIN maquina  m  ON m.id_maquina  = tn.id_maquina
        JOIN producto pr ON pr.id_producto = tn.id_producto
        ORDER BY tn.fecha_fuente DESC NULLS LAST
        LIMIT :lim
    """, {"lim": limit})

    html = [f"""
    <html><head><title>Admin NOMINALES</title></head>
    <body style="font-family: system-ui; padding: 16px; max-width: 1200px; margin: auto;">
      <h2>📘 Tiempos NOMINALES (ficha) cargados</h2>
      <p><a href="/admin?token={(ADMIN_TOKEN or '')}">⬅ Volver al panel</a></p>
      <table border="1" cellpadding="6" cellspacing="0">
        <tr>
          <th>ID</th><th>Proceso</th><th>Máquina</th><th>Producto</th>
          <th>Nominal (min)</th><th>Fuente</th><th>Original</th><th>Unidad</th><th>Notas</th><th>Fecha</th><th>Acciones</th>
        </tr>
    """]
    for r in rows:
        notas = (r.get('notas') or '')
        notas_corta = (notas[:60] + '…') if len(notas) > 60 else notas
        html.append(f"""
        <tr>
          <td>{r['id_tiempo_nominal']}</td>
          <td>{r['proceso']}</td>
          <td>{r['maquina']}</td>
          <td>{r['producto']}</td>
          <td>{r['tiempo_min']}</td>
          <td>{r.get('fuente') or ''}</td>
          <td>{r.get('valor_original') or ''}</td>
          <td>{r.get('unidad_original') or ''}</td>
          <td>{notas_corta}</td>
          <td>{r.get('fecha_fuente') or ''}</td>
          <td>
            <form method="post" action="/admin/nominal/delete/{r['id_tiempo_nominal']}?token={(ADMIN_TOKEN or '')}"
                  onsubmit="return confirm('¿Eliminar NOMINAL #{r['id_tiempo_nominal']}?');">
              <button type="submit">❌ Eliminar</button>
            </form>
          </td>
        </tr>
        """)
    html.append("""
      </table>
      <p style="margin-top:10px;">Recuerda: hay restricción única por (proceso, máquina, producto). Si borras uno, podrás volver a cargarlo.</p>
      <p><a href="/">⬅ Volver al inicio</a></p>
    </body></html>
    """)
    return HTMLResponse("".join(html))

@app.post("/admin/nominal/delete/{id_tiempo_nominal}")
def admin_delete_nominal(id_tiempo_nominal: int, request: Request, db: Session = Depends(get_db)):
    check_admin_token(request)
    db.execute(text("DELETE FROM tiempo_nominal WHERE id_tiempo_nominal = :id"), {"id": id_tiempo_nominal})
    db.commit()
    return HTMLResponse(f"""
      <html><body style="font-family: system-ui; padding: 16px;">
        <p>Nominal #{id_tiempo_nominal} eliminado.</p>
        <p><a href="/admin/nominal?token={(ADMIN_TOKEN or '')}">⬅ Volver a la lista</a></p>
      </body></html>
    """)
#----------admin cambios -----------


# -------- Endpoints de catálogos (para selects en cascada) --------
@app.get("/options/procesos")
def procesos(db: Session = Depends(get_db)):
    rows = q1(db, "SELECT nombre FROM proceso ORDER BY nombre")
    return [r["nombre"] for r in rows]

@app.get("/options/maquinas")
def maquinas(proceso: str = Query(...), db: Session = Depends(get_db)):
    rows = q1(db, """
        SELECT m.nombre
        FROM proceso_maquina pm
        JOIN proceso p ON p.id_proceso=pm.id_proceso
        JOIN maquina m ON m.id_maquina=pm.id_maquina
        WHERE p.nombre=:p
        ORDER BY m.nombre
    """, {"p": proceso})
    return [r["nombre"] for r in rows]

@app.get("/options/productos")
def productos(maquina: str = Query(...), db: Session = Depends(get_db)):
    rows = q1(db, """
        SELECT pr.nombre
        FROM maquina_producto mp
        JOIN maquina m ON m.id_maquina=mp.id_maquina
        JOIN producto pr ON pr.id_producto=mp.id_producto
        WHERE m.nombre=:m
        ORDER BY pr.nombre
    """, {"m": maquina})
    return [r["nombre"] for r in rows]
#----------------pagina inicio--------------
@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
        <head>
            <title>TPI - Captura de Tiempos</title>
        </head>
        <body style="font-family: Arial; text-align: center; margin-top: 50px;">
            <h1>📊 TPI - Captura de Tiempos</h1>
            <p>Selecciona una opción:</p>
            <a href="/app/real">
                <button style="padding: 10px 20px; margin: 10px; font-size: 16px;">
                    Registrar tiempo REAL
                </button>
            </a>
            <a href="/app/nominal">
                <button style="padding: 10px 20px; margin: 10px; font-size: 16px;">
                    Registrar tiempo NOMINAL
                </button>
            </a>
        </body>
    </html>
    """
#--------fin pagina inicio------------------

# -------- Modelos de entrada --------
class MedicionReal(BaseModel):
    proceso: str
    maquina: str
    producto: str
    tiempo_min: condecimal(max_digits=10, decimal_places=3)
    operario: str | None = None

class TiempoNominal(BaseModel):
    proceso: str
    maquina: str
    producto: str
    tiempo_min: condecimal(max_digits=10, decimal_places=3)
    fuente: str | None = "ficha_tecnica"
    valor_original: float | None = None
    unidad_original: str | None = None
    notas: str | None = None

# -------- Escrituras --------
@app.post("/tiempo-real")
def crear_real(data: MedicionReal, db: Session = Depends(get_db)):
    id_proceso  = id_by_name(db, "proceso", data.proceso)
    id_maquina  = id_by_name(db, "maquina", data.maquina)
    id_producto = id_by_name(db, "producto", data.producto)
    must(id_proceso is not None, "Proceso no existe")
    must(id_maquina is not None, "Máquina no existe")
    must(id_producto is not None, "Producto no existe")

    pm = q1_one(db, "SELECT 1 FROM proceso_maquina WHERE id_proceso=:p AND id_maquina=:m",
                {"p": id_proceso, "m": id_maquina})
    must(bool(pm), "Esa máquina NO está asociada a ese proceso")

    mp = q1_one(db, "SELECT 1 FROM maquina_producto WHERE id_maquina=:m AND id_producto=:pr",
                {"m": id_maquina, "pr": id_producto})
    must(bool(mp), "Ese producto NO está asociado a esa máquina")

    db.execute(text("""
        INSERT INTO tiempo_real (id_proceso, id_maquina, id_producto, tiempo_min, operario)
        VALUES (:p,:m,:pr,:t,:op)
    """), {"p": id_proceso, "m": id_maquina, "pr": id_producto,
           "t": str(data.tiempo_min), "op": data.operario})
    db.commit()
    return {"ok": True}

@app.post("/tiempo-nominal")
def upsert_nominal(data: TiempoNominal, db: Session = Depends(get_db)):
    id_proceso  = id_by_name(db, "proceso", data.proceso)
    id_maquina  = id_by_name(db, "maquina", data.maquina)
    id_producto = id_by_name(db, "producto", data.producto)
    must(id_proceso is not None, "Proceso no existe")
    must(id_maquina is not None, "Máquina no existe")
    must(id_producto is not None, "Producto no existe")

    pm = q1_one(db, "SELECT 1 FROM proceso_maquina WHERE id_proceso=:p AND id_maquina=:m",
                {"p": id_proceso, "m": id_maquina})
    must(bool(pm), "Esa máquina NO está asociada a ese proceso")

    mp = q1_one(db, "SELECT 1 FROM maquina_producto WHERE id_maquina=:m AND id_producto=:pr",
                {"m": id_maquina, "pr": id_producto})
    must(bool(mp), "Ese producto NO está asociado a esa máquina")

    db.execute(text("""
        INSERT INTO tiempo_nominal (id_proceso, id_maquina, id_producto, tiempo_min, fuente, valor_original, unidad_original, notas)
        VALUES (:p,:m,:pr,:t,:f,:vo,:uo,:n)
        ON CONFLICT (id_proceso, id_maquina, id_producto)
        DO UPDATE SET tiempo_min=EXCLUDED.tiempo_min,
                      fuente=COALESCE(EXCLUDED.fuente, tiempo_nominal.fuente),
                      valor_original=EXCLUDED.valor_original,
                      unidad_original=EXCLUDED.unidad_original,
                      notas=EXCLUDED.notas,
                      fecha_fuente=NOW();
    """), {"p": id_proceso, "m": id_maquina, "pr": id_producto,
           "t": str(data.tiempo_min), "f": data.fuente,
           "vo": data.valor_original, "uo": data.unidad_original, "n": data.notas})
    db.commit()
    return {"ok": True}

# -------- Formularios Web (móvil) --------
FORM_STYLE = """
<style>
body{font-family:system-ui,-apple-system,Segoe UI,Roboto;padding:14px;max-width:520px;margin:auto}
label{display:block;margin-top:12px;font-weight:600}
input,select,button,textarea{width:100%;padding:10px;margin-top:6px;border-radius:8px;border:1px solid #ddd;font-size:16px}
button{background:#111;color:#fff;border:none}
.small{font-size:12px;color:#666}
</style>
"""

@app.get("/app/real", response_class=HTMLResponse)
def app_real():
    return HTMLResponse(FORM_STYLE + """
<h2>Registrar tiempo REAL</h2>
<label>Proceso</label><select id="proceso"></select>
<label>Máquina</label><select id="maquina"></select>
<label>Producto</label><select id="producto"></select>
<label>Tiempo (min)</label><input id="tiempo" type="number" step="0.001" />
<label>Operario (opcional)</label><input id="operario" type="text" />
<button onclick="enviar()">Guardar</button>
<p id="msg" class="small"></p>
                        
<!-- boton para volver inicio -->

<a href="/">
  <button style="margin-top: 20px; padding: 8px 16px;">⬅ Volver al inicio</button>
</a>
<!-- boton para volver inicio -->
                        
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
  d.forEach(x=>s.innerHTML+=`<option>${x}</option>`); document.getElementById('producto').innerHTML='';
}
async function loadProductos(){
  const m=document.getElementById('maquina').value;
  const r=await fetch('/options/productos?maquina='+encodeURIComponent(m)); const d=await r.json();
  const s=document.getElementById('producto'); s.innerHTML='<option value="">-- selecciona --</option>';
  d.forEach(x=>s.innerHTML+=`<option>${x}</option>`);
}
async function enviar(){
  const body={
    proceso:document.getElementById('proceso').value,
    maquina:document.getElementById('maquina').value,
    producto:document.getElementById('producto').value,
    tiempo_min:document.getElementById('tiempo').value,
    operario:document.getElementById('operario').value||null
  };
  const r=await fetch('/tiempo-real',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  document.getElementById('msg').textContent = r.ok ? '✅ Guardado' : '❌ Error: '+(await r.text());
  if(r.ok){document.getElementById('tiempo').value=''; document.getElementById('operario').value='';}
}
document.getElementById('proceso').addEventListener('change',loadMaquinas);
document.getElementById('maquina').addEventListener('change',loadProductos);
loadProcesos();
</script>
""")



@app.get("/app/nominal", response_class=HTMLResponse)
def app_nominal():
    return HTMLResponse(FORM_STYLE + """
<h2>Registrar tiempo NOMINAL (ficha técnica)</h2>
<label>Proceso</label><select id="proceso"></select>
<label>Máquina</label><select id="maquina"></select>
<label>Producto</label><select id="producto"></select>
<label>Tiempo (min)</label><input id="tiempo" type="number" step="0.001" />
<label class="small">Metadatos (opcional)</label>
<input id="fuente" placeholder="ficha_tecnica / manual / estimacion" />
<input id="valor" type="number" step="0.0001" placeholder="valor original (ej 40.0000)" />
<input id="unidad" placeholder="unidad original (ej perforaciones/min)" />
<textarea id="notas" placeholder="cómo convertiste a min/unidad"></textarea>
<button onclick="enviar()">Guardar / Actualizar</button>
<p id="msg" class="small"></p>
                        
<!-- boton para volver inicio -->                        
<a href="/">
  <button style="margin-top: 20px; padding: 8px 16px;">⬅ Volver al inicio</button>
</a>
<!-- boton para volver inicio -->

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
  d.forEach(x=>s.innerHTML+=`<option>${x}</option>`); document.getElementById('producto').innerHTML='';
}
async function loadProductos(){
  const m=document.getElementById('maquina').value;
  const r=await fetch('/options/productos?maquina='+encodeURIComponent(m)); const d=await r.json();
  const s=document.getElementById('producto'); s.innerHTML='<option value="">-- selecciona --</option>';
  d.forEach(x=>s.innerHTML+=`<option>${x}</option>`);
}
async function enviar(){
  const body={
    proceso:document.getElementById('proceso').value,
    maquina:document.getElementById('maquina').value,
    producto:document.getElementById('producto').value,
    tiempo_min:document.getElementById('tiempo').value,
    fuente:document.getElementById('fuente').value||'ficha_tecnica',
    valor_original:document.getElementById('valor').value?Number(document.getElementById('valor').value):null,
    unidad_original:document.getElementById('unidad').value||null,
    notas:document.getElementById('notas').value||null
  };
  const r=await fetch('/tiempo-nominal',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  document.getElementById('msg').textContent = r.ok ? '✅ Guardado/Actualizado' : '❌ Error: '+(await r.text());
}
document.getElementById('proceso').addEventListener('change',loadMaquinas);
document.getElementById('maquina').addEventListener('change',loadProductos);
loadProcesos();
</script>
""")
#--------------------------------


