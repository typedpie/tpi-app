from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, condecimal
from sqlalchemy import text
from sqlalchemy.orm import Session
from database import get_db

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