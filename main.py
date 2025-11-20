from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, condecimal
from sqlalchemy import text
from sqlalchemy.orm import Session
from database import get_db
#------------------------------------
from fastapi import Request
import os 
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import Form



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

def norm_tipo(s: str | None) -> str:
    v = (s or "").strip().lower()
    mapping = {
        "setup": "setup", "set-up": "setup", "set_up": "setup",
        "t_proceso": "proceso", "tproceso": "proceso", "proceso": "proceso",
        "postproceso": "postproceso", "post-proceso": "postproceso", "post": "postproceso",
        "espera": "espera", "wait": "espera"
    }
    return mapping.get(v, "proceso")

#----------admin cambios -----------
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN")  # configurar en Render

def check_admin_token(request: Request):
    """
    Permite acceso si el token correcto llega por cookie 'adm' o por query ?token=...
    Si ADMIN_TOKEN no está seteado (local), no exige credenciales.
    """
    if not ADMIN_TOKEN:
        return
    cookie_token = request.cookies.get("adm")
    if cookie_token == ADMIN_TOKEN:
        return
    query_token = request.query_params.get("token")
    if query_token == ADMIN_TOKEN:
        return
    raise HTTPException(status_code=401, detail="No autorizado. Inicia sesión en /admin/login")

@app.get("/admin/login", response_class=HTMLResponse)
def admin_login_form():
    return """
    <html>
      <head><title>Login Admin</title></head>
      <body style="font-family: system-ui; padding: 16px; max-width: 420px; margin: auto; text-align:center;">
        <h2>🔐 Acceso administrador</h2>
        <p>Ingresa la clave de administrador</p>
        <form method="post" action="/admin/login" style="margin-top:12px;">
          <input type="password" name="token" placeholder="Clave" style="width:100%;padding:10px;border-radius:8px;border:1px solid #ddd;">
          <button type="submit" style="margin-top:12px;padding:10px 16px;">Entrar</button>
        </form>
        <p style="margin-top:16px;"><a href="/">⬅ Volver al inicio</a></p>
      </body>
    </html>
    """

@app.post("/admin/login")
def admin_login(token: str = Form(...)):
    if not ADMIN_TOKEN or token == ADMIN_TOKEN:
        resp = RedirectResponse(url="/admin", status_code=302)
        resp.set_cookie(key="adm", value=token, httponly=True, max_age=60*60*8)  # 8 horas
        return resp
    return HTMLResponse("""
      <html><body style="font-family: system-ui; padding: 16px; text-align:center;">
        <p>❌ Clave incorrecta</p>
        <p><a href="/admin/login">Intentar de nuevo</a></p>
        <p><a href="/">⬅ Volver al inicio</a></p>
      </body></html>
    """, status_code=401)

@app.get("/admin/logout")
def admin_logout():
    resp = RedirectResponse(url="/", status_code=302)
    resp.delete_cookie("adm")
    return resp

@app.get("/admin", response_class=HTMLResponse)
def admin_home(request: Request):
    check_admin_token(request)
    return """
    <html>
      <head><title>Admin TPI</title></head>
      <body style="font-family: system-ui; padding: 16px; max-width: 900px; margin: auto;">
        <h2>🛠️ Panel de administración</h2>
        <ul>
          <li><a href="/admin/real">Ver y eliminar <b>tiempos REALES</b></a></li>
          <li><a href="/admin/nominal">Ver y eliminar <b>tiempos NOMINALES</b></a></li>
          <li><a href="/admin/experiencia">Ver y eliminar <b>tiempos EXPERIENCIA</b></a></li>
        </ul>
        <p style="margin-top:16px;">
          <a href="/">⬅ Volver al inicio (no admin)</a> |
          <a href="/admin/logout">🚪 Salir del modo admin</a>
        </p>
      </body>
    </html>
    """

# =========================
# ADMIN: Listas y borrado
# =========================
@app.get("/admin/real", response_class=HTMLResponse)
def admin_list_real(request: Request, limit: int = 50, db: Session = Depends(get_db)):
    check_admin_token(request)
    rows = q1(db, """
    SELECT
      tr.id_tiempo_real,
      to_char(tr.fecha AT TIME ZONE 'America/Santiago', 'YYYY-MM-DD HH24:MI') AS fecha,
      tr.tiempo_seg,
      tr.operario,
      tr.tipo,                                    
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

    html = ["""
<html><head><title>Admin REALES</title></head>
<body style="font-family: system-ui; padding: 16px; max-width: 1100px; margin: auto;">
  <h2>🧭 Registros REALES recientes</h2>
  <p>
    <a href="/admin">⬅ Volver al panel</a> |
    <a href="/">⬅ Volver al inicio (no admin)</a> |
    <a href="/admin/logout">🚪 Salir del modo admin</a>
  </p>
  <table border="1" cellpadding="6" cellspacing="0">
    <tr>
      <th>ID</th>
      <th>Fecha</th>
      <th>Proceso</th>
      <th>Máquina</th>
      <th>Producto</th>
      <th>Tipo</th>
      <th>tiempo_seg</th>
      <th>Operario</th>
      <th>Acciones</th>
    </tr>
"""]
    TIPO_LABEL = {"proceso":"T_Proceso","setup":"SetUp","postproceso":"Post-proceso","espera":"Espera"}
    for r in rows:
        tipo_txt = TIPO_LABEL.get(r['tipo'], r['tipo'])
        html.append(f"""
        <tr>
          <td>{r['id_tiempo_real']}</td>
          <td>{r['fecha']}</td>
          <td>{r['proceso']}</td>
          <td>{r['maquina']}</td>
          <td>{r['producto']}</td>
          <td>{tipo_txt}</td>
          <td>{r['tiempo_seg']}</td>
          <td>{r.get('operario') or ''}</td>
          <td>
            <form method="post" action="/admin/real/delete/{r['id_tiempo_real']}" 
                  onsubmit="return confirm('¿Eliminar registro REAL #{r['id_tiempo_real']}?');">
              <button type="submit">❌ Eliminar</button>
            </form>
          </td>
        </tr>
        """)
    html.append("""
      </table>
      <p style="margin-top:10px;">Mostrando últimos registros.</p>
      <p>
        <a href="/admin">⬅ Volver al panel</a> |
        <a href="/">⬅ Volver al inicio (no admin)</a>
      </p>
    </body></html>
    """)
    return HTMLResponse("".join(html))

@app.post("/admin/real/delete/{id_tiempo_real}")
def admin_delete_real(id_tiempo_real: int, request: Request, db: Session = Depends(get_db)):
    check_admin_token(request)
    db.execute(text("DELETE FROM tiempo_real WHERE id_tiempo_real = :id"), {"id": id_tiempo_real})
    db.commit()
    return HTMLResponse("""
      <html><body style="font-family: system-ui; padding: 16px;">
        <p>Registro REAL eliminado.</p>
        <p><a href="/admin/real">⬅ Volver a la lista</a></p>
      </body></html>
    """)

@app.get("/admin/nominal", response_class=HTMLResponse)
def admin_list_nominal(request: Request, limit: int = 100, db: Session = Depends(get_db)):
    check_admin_token(request)

    try:
        rows = q1(db, """
            SELECT
              tn.id_tiempo_nominal,
              tn.tiempo_seg,
              tn.fuente,
              tn.unidad_original,
              tn.notas,
              tn.tipo,  -- 👈 importante
              to_char(tn.fecha_fuente AT TIME ZONE 'America/Santiago', 'YYYY-MM-DD HH24:MI') AS fecha_txt,
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
    except Exception as e:
        return HTMLResponse(f"<pre style='padding:16px;font-family:monospace;'>Error consultando BD:\n{e}</pre>", status_code=500)

    html = ["""
    <html><head><title>Admin NOMINALES</title></head>
    <body style="font-family: system-ui; padding: 16px; max-width: 1200px; margin: auto;">
      <h2>📘 Tiempos NOMINALES (ficha) cargados</h2>
      <p>
        <a href="/admin">⬅ Volver al panel</a> |
        <a href="/">⬅ Volver al inicio (no admin)</a> |
        <a href="/admin/logout">🚪 Salir del modo admin</a>
      </p>
      <table border="1" cellpadding="6" cellspacing="0">
        <tr>
          <th>ID</th>
          <th>Proceso</th>
          <th>Máquina</th>
          <th>Producto</th>
          <th>Tipo</th>
          <th>Nominal (min)</th>
          <th>Fuente</th>
          <th>Original</th>
          <th>Unidad</th>
          <th>Notas</th>
          <th>Fecha</th>
          <th>Acciones</th>
        </tr>
    """]

    TIPO_LABEL = {"proceso":"T_Proceso","setup":"SetUp","postproceso":"Post-proceso","espera":"Espera"}

    for r in rows:
        tipo_txt = TIPO_LABEL.get(r.get('tipo'), r.get('tipo') or '—')
        notas = (r.get('notas') or '')
        notas_corta = (notas[:60] + '…') if len(notas) > 60 else notas

        html.append(f"""
        <tr>
          <td>{r['id_tiempo_nominal']}</td>
          <td>{r['proceso']}</td>
          <td>{r['maquina']}</td>
          <td>{r['producto']}</td>
          <td>{tipo_txt}</td>
          <td>{r['tiempo_seg']}</td>
          <td>{r.get('fuente') or ''}</td>
          <td>{r.get('valor_original') or ''}</td>
          <td>{r.get('unidad_original') or ''}</td>
          <td>{notas_corta}</td>
          <td>{r.get('fecha_txt') or ''}</td>
          <td>
            <form method="post" action="/admin/nominal/delete/{r['id_tiempo_nominal']}"
                  onsubmit="return confirm('¿Eliminar NOMINAL #{r['id_tiempo_nominal']}?');">
              <button type="submit">❌ Eliminar</button>
            </form>
          </td>
        </tr>
        """)

    html.append("""
      </table>
      <p style="margin-top:10px;">Recuerda: hay restricción única por (máquina, producto, <b>tipo</b>).</p>
      <p>
        <a href="/admin">⬅ Volver al panel</a> |
        <a href="/">⬅ Volver al inicio (no admin)</a>
      </p>
    </body></html>
    """)
    return HTMLResponse("".join(html))

@app.post("/admin/nominal/delete/{id_tiempo_nominal}")
def admin_delete_nominal(id_tiempo_nominal: int, request: Request, db: Session = Depends(get_db)):
    check_admin_token(request)
    db.execute(text("DELETE FROM tiempo_nominal WHERE id_tiempo_nominal = :id"), {"id": id_tiempo_nominal})
    db.commit()
    return HTMLResponse("""
      <html><body style="font-family: system-ui; padding: 16px;">
        <p>Nominal eliminado.</p>
        <p><a href="/admin/nominal">⬅ Volver a la lista</a></p>
      </body></html>
    """)
@app.get("/admin/experiencia", response_class=HTMLResponse)
def admin_list_experiencia(request: Request, limit: int = 100, db: Session = Depends(get_db)):
    check_admin_token(request)
    rows = q1(db, """
        SELECT
          te.id_tiempo_experiencia,
          to_char(te.fecha AT TIME ZONE 'America/Santiago', 'YYYY-MM-DD HH24:MI') AS fecha,
          te.tiempo_seg,
          te.operario,
          te.tipo,
          te.notas,
          p.nombre  AS proceso,
          m.nombre  AS maquina,
          pr.nombre AS producto
        FROM tiempo_experiencia te
        JOIN proceso  p  ON p.id_proceso  = te.id_proceso
        JOIN maquina  m  ON m.id_maquina  = te.id_maquina
        JOIN producto pr ON pr.id_producto = te.id_producto
        ORDER BY te.fecha DESC
        LIMIT :lim
    """, {"lim": limit})

    html = ["""
    <html><head><title>Admin EXPERIENCIA</title></head>
    <body style="font-family: system-ui; padding: 16px; max-width: 1200px; margin: auto;">
      <h2>📝 Tiempos por EXPERIENCIA</h2>
      <p>
        <a href="/admin">⬅ Volver al panel</a> |
        <a href="/">⬅ Volver al inicio (no admin)</a> |
        <a href="/admin/logout">🚪 Salir del modo admin</a>
      </p>
      <table border="1" cellpadding="6" cellspacing="0">
        <tr>
          <th>ID</th>
          <th>Fecha</th>
          <th>Proceso</th>
          <th>Máquina</th>
          <th>Producto</th>
          <th>Tipo</th>
          <th>Segundos</th>
          <th>Operario</th>
          <th>Notas</th>
          <th>Acciones</th>
        </tr>
    """]
    TIPO_LABEL = {"proceso":"T_Proceso","setup":"SetUp","postproceso":"Post-proceso","espera":"Espera"}
    for r in rows:
        notas = (r.get('notas') or '')
        notas_corta = (notas[:60] + '…') if len(notas) > 60 else notas
        tipo_txt = TIPO_LABEL.get(r.get('tipo'), r.get('tipo') or '—')
        html.append(f"""
        <tr>
          <td>{r['id_tiempo_experiencia']}</td>
          <td>{r['fecha']}</td>
          <td>{r['proceso']}</td>
          <td>{r['maquina']}</td>
          <td>{r['producto']}</td>
          <td>{tipo_txt}</td>
          <td>{r['tiempo_seg']}</td>
          <td>{r.get('operario') or ''}</td>
          <td>{notas_corta}</td>
          <td>
            <form method="post" action="/admin/experiencia/delete/{r['id_tiempo_experiencia']}"
                  onsubmit="return confirm('¿Eliminar EXPERIENCIA #{r['id_tiempo_experiencia']}?');">
              <button type="submit">❌ Eliminar</button>
            </form>
          </td>
        </tr>
        """)
    html.append("""
      </table>
      <p style="margin-top:10px;">Mostrando últimos registros por experiencia.</p>
      <p>
        <a href="/admin">⬅ Volver al panel</a> |
        <a href="/">⬅ Volver al inicio (no admin)</a>
      </p>
    </body></html>
    """)
    return HTMLResponse("".join(html))


@app.post("/admin/experiencia/delete/{id_tiempo_experiencia}")
def admin_delete_experiencia(id_tiempo_experiencia: int, request: Request, db: Session = Depends(get_db)):
    check_admin_token(request)
    db.execute(text("DELETE FROM tiempo_experiencia WHERE id_tiempo_experiencia = :id"),
               {"id": id_tiempo_experiencia})
    db.commit()
    return HTMLResponse("""
      <html><body style="font-family: system-ui; padding: 16px;">
        <p>Registro de EXPERIENCIA eliminado.</p>
        <p><a href="/admin/experiencia">⬅ Volver a la lista</a></p>
      </body></html>
    """)

#----------admin cambios -----------


# -------- Endpoints de catálogos (para selects en cascada) --------
@app.get("/options/procesos")
def procesos(db: Session = Depends(get_db)):
    rows = q1(db, """
        SELECT DISTINCT p.nombre
        FROM public.proceso p
        JOIN public.proceso_maquina pm ON pm.id_proceso = p.id_proceso
        ORDER BY p.nombre
    """)
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

#--------fin pagina inicio------------------
from home import router as home_router
app.include_router(home_router)

from fastapi.staticfiles import StaticFiles
app.mount("/static",StaticFiles(directory="static"), name="static")

# -------- Modelos de entrada --------
class MedicionReal(BaseModel):
    proceso: str
    maquina: str
    producto: str
    tipo: str 
    tiempo_seg: condecimal(max_digits=10, decimal_places=3)  #segundos
    operario: str | None = None

class TiempoNominal(BaseModel):
    proceso: str
    maquina: str
    producto: str
    tipo: str                               # 'setup' | 'proceso' | 'postproceso' | 'espera'
    tiempo_seg: condecimal(max_digits=10, decimal_places=3)
    fuente: str | None = "ficha_tecnica"
    unidad_original: str | None = None
    notas: str | None = None

class TiempoExperiencia(BaseModel):
    proceso: str
    maquina: str
    producto: str
    tipo: str                                # 'setup' | 'proceso' | 'postproceso' | 'espera'
    tiempo_seg: condecimal(max_digits=10, decimal_places=3)  # segundos
    operario: str | None = None
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

    tipo = norm_tipo(data.tipo)

    db.execute(text("""
    INSERT INTO tiempo_real (id_proceso, id_maquina, id_producto, tiempo_seg, operario, tipo)
    VALUES (:p,:m,:pr,:t_seg,:op,:tipo)
"""), {"p": id_proceso, "m": id_maquina, "pr": id_producto,
       "t_seg": str(data.tiempo_seg), "op": data.operario, "tipo": data.tipo})
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

    tipo = norm_tipo(data.tipo)

    db.execute(text("""
        INSERT INTO tiempo_nominal
          (id_proceso, id_maquina, id_producto, tipo, tiempo_seg, fuente, unidad_original, notas)
        VALUES (:p,:m,:pr,:tipo,:t_seg,:f,:uo,:n)
        ON CONFLICT (id_maquina, id_producto, tipo)
        DO UPDATE SET tiempo_seg=EXCLUDED.tiempo_seg,
                      fuente=COALESCE(EXCLUDED.fuente, tiempo_nominal.fuente),
                      unidad_original=EXCLUDED.unidad_original,
                      notas=EXCLUDED.notas,
                      fecha_fuente=NOW();
    """), {
        "p": id_proceso,
        "m": id_maquina,
        "pr": id_producto,
        "tipo": tipo,
        "t_seg": str(data.tiempo_seg),                 # ←SEGUNDOS
        "f": data.fuente,
        "uo": data.unidad_original,
        "n": data.notas
    })
    db.commit()
    return {"ok": True}

@app.post("/tiempo-experiencia")
def crear_experiencia(data: TiempoExperiencia, db: Session = Depends(get_db)):
    # IDs por nombre (tus tablas usan id_proceso/id_maquina/id_producto)
    id_proceso  = id_by_name(db, "proceso", data.proceso)
    id_maquina  = id_by_name(db, "maquina", data.maquina)
    id_producto = id_by_name(db, "producto", data.producto)
    must(id_proceso is not None, "Proceso no existe")
    must(id_maquina is not None, "Máquina no existe")
    must(id_producto is not None, "Producto no existe")

    # Validar asociaciones (sigues usando 'proceso_maquina' y 'maquina_producto')
    pm = q1_one(db, "SELECT 1 FROM proceso_maquina WHERE id_proceso=:p AND id_maquina=:m",
                {"p": id_proceso, "m": id_maquina})
    must(bool(pm), "Esa máquina NO está asociada a ese proceso")

    mp = q1_one(db, "SELECT 1 FROM maquina_producto WHERE id_maquina=:m AND id_producto=:pr",
                {"m": id_maquina, "pr": id_producto})
    must(bool(mp), "Ese producto NO está asociado a esa máquina")

    tipo = norm_tipo(data.tipo)

    db.execute(text("""
        INSERT INTO tiempo_experiencia
          (id_proceso, id_maquina, id_producto, tipo, tiempo_seg, operario, notas)
        VALUES (:p,:m,:pr,:tipo,:t_seg,:op,:n)
    """), {
        "p": id_proceso,
        "m": id_maquina,
        "pr": id_producto,
        "tipo": tipo,
        "t_seg": str(data.tiempo_seg),   # segundos
        "op": data.operario,
        "n": data.notas
    })
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

<label>Tipo de tiempo</label>
<select id="tipo">
  <option value="">-- selecciona --</option>
  <option value="setup">SetUp</option>
  <option value="proceso">Proceso</option>
  <option value="postproceso">Post-proceso</option>
  <option value="espera">Espera</option>
</select>

<label>Modo de captura</label>
<select id="modo">
  <option value="">-- selecciona --</option>                      
  <option value="manual">Ingresar tiempo</option>
  <option value="cronometro">Tomar tiempo (cronómetro)</option>
</select>

<!-- Caja: entrada manual -->
<div id="box-manual" style="margin-top:6px;">
  <label>Tiempo (segundos)</label>
  <input id="tiempo" type="number" step="1" placeholder="ej: 180" />
</div>

<!-- Caja: cronómetro -->
<div id="box-crono" style="display:none; margin-top:6px;">
  <label>Tiempo (cronómetro)</label>
  <div id="crono-display" style="font-size:28px;font-weight:700;padding:8px 0;">00:00.000</div>
  <div style="display:flex;gap:8px;flex-wrap:wrap;">
    <button type="button" id="btn-start" onclick="cronoStart()">▶️ Iniciar</button>
    <button type="button" id="btn-pause" onclick="cronoPause()" disabled>⏸️ Pausar</button>
    <button type="button" id="btn-reset" onclick="cronoReset()" disabled>↺ Reiniciar</button>
  </div>
  <p id="crono-msg" class="small"></p>
</div>

<label>Cantidad Operarios (opcional)</label><input id="operario" type="text" />

<button onclick="enviar()">Guardar</button>
<p id="msg" class="small"></p>

<a href="/"><button style="margin-top: 20px; padding: 8px 16px;">⬅ Volver al inicio</button></a>

<script>
// ------- catálogos -------
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
  document.getElementById('producto').innerHTML='<option value="">-- selecciona --</option>';
}
async function loadProductos(){
  const m=document.getElementById('maquina').value;
  const r=await fetch('/options/productos?maquina='+encodeURIComponent(m)); const d=await r.json();
  const s=document.getElementById('producto'); s.innerHTML='<option value="">-- selecciona --</option>';
  d.forEach(x=>s.innerHTML+=`<option>${x}</option>`);
}

// ------- UI modo manual/cronómetro -------
const boxManual = ()=>document.getElementById('box-manual');
const boxCrono  = ()=>document.getElementById('box-crono');

document.getElementById('modo').addEventListener('change', ()=>{
  const v = document.getElementById('modo').value;
  if (v==='cronometro'){ boxManual().style.display='none'; boxCrono().style.display='block'; }
  else { boxManual().style.display='block'; boxCrono().style.display='none'; }
});

// ------- Lógica de cronómetro -------
let crono = { running:false, start:0, elapsed:0, hnd:null };

function fmt(ms){
  const m = Math.floor(ms/60000);
  const s = Math.floor((ms%60000)/1000);
  const cs = ms%1000;
  return `${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')}.${String(cs).padStart(3,'0')}`;
}
function paint(){
  const now = Date.now();
  const ms = crono.elapsed + (crono.running ? (now - crono.start) : 0);
  document.getElementById('crono-display').textContent = fmt(ms);
}
function cronoStart(){
  if (crono.running) return;
  crono.running = true;
  crono.start = Date.now();
  crono.hnd = setInterval(paint, 33);
  document.getElementById('btn-start').disabled = true;
  document.getElementById('btn-pause').disabled = false;
  document.getElementById('btn-reset').disabled = false;
  document.getElementById('crono-msg').textContent = '';
}
function cronoPause(){
  if (!crono.running) return;
  crono.running = false;
  crono.elapsed += Date.now() - crono.start;
  clearInterval(crono.hnd); crono.hnd=null;
  paint();
  document.getElementById('btn-start').disabled = false;
  document.getElementById('btn-pause').disabled = true;
}
function cronoReset(){
  crono.running=false; crono.elapsed=0; crono.start=0;
  clearInterval(crono.hnd); crono.hnd=null;
  paint();
  document.getElementById('btn-start').disabled = false;
  document.getElementById('btn-pause').disabled = true;
  document.getElementById('btn-reset').disabled = true;
  document.getElementById('crono-msg').textContent = '';
}
paint(); // inicializa 00:00.000

// ------- reset formulario -------
function resetReal(){
  document.getElementById('proceso').value = '';
  document.getElementById('maquina').innerHTML  = '<option value="">-- selecciona --</option>';
  document.getElementById('producto').innerHTML = '<option value="">-- selecciona --</option>';
  document.getElementById('tipo').value = '';
  document.getElementById('modo').value = '';
  boxManual().style.display='block'; boxCrono().style.display='none';
  document.getElementById('tiempo').value = '';
  document.getElementById('operario').value = '';
  cronoReset();
}

// ------- enviar -------
async function enviar(){
  const btn = event?.target || document.querySelector('button[onclick="enviar()"]');
  if (btn?.disabled) return; 
  btn && (btn.disabled = true);

  // Lee valores
  const proceso  = document.getElementById('proceso').value;
  const maquina  = document.getElementById('maquina').value;
  const producto = document.getElementById('producto').value;
  const tipo     = document.getElementById('tipo').value;     // setup | proceso | postproceso | espera
  const modo     = document.getElementById('modo').value;     // manual | cronometro

  // Validaciones
  if (!proceso || !maquina || !producto){
    document.getElementById('msg').textContent='❌ Completa Proceso, Máquina y Producto.';
    btn.disabled=false; return;
  }
  if (!tipo){
    document.getElementById('msg').textContent='❌ Selecciona el tipo de tiempo.';
    btn.disabled=false; return;
  }
  if (!modo){
    document.getElementById('msg').textContent='❌ Selecciona el modo de captura.';
    btn.disabled=false; return;
  }

  // --- ahora trabajamos SIEMPRE en SEGUNDOS ---
  let seg = null;

  if (modo === 'cronometro') {
    // ms acumulados (si está corriendo, sumo desde el último start)
    const ms = crono.elapsed + (crono.running ? (Date.now() - crono.start) : 0);
    if (ms <= 0) {
      document.getElementById('msg').textContent = '❌ El cronómetro está en 0.';
      btn.disabled=false; return;
    }
    seg = ms / 1000;                              // ← a segundos
  } else { // manual
    const v = Number(document.getElementById('tiempo').value);
    if (!v || v <= 0){
      document.getElementById('msg').textContent='❌ Ingresa un tiempo válido en segundos.';
      btn.disabled=false; return;
    }
    seg = v;                                      // ya viene en segundos
  }

  const body = {
    proceso,
    maquina,
    producto,
    tipo,
    tiempo_seg: Number(seg).toFixed(3),           // ← en segundos
    operario: document.getElementById('operario').value || null
  };

  const r = await fetch('/tiempo-real', {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body: JSON.stringify(body)
  });

  if (r.ok){
    document.getElementById('msg').textContent = '✅ Guardado';
    resetReal(); 
    loadProcesos();
  } else {
    document.getElementById('msg').textContent = '❌ Error: ' + (await r.text());
  }
  btn && (btn.disabled = false);
}

// eventos iniciales
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

<label>Tipo de tiempo</label>
<select id="tipo">
  <option value="">-- selecciona --</option>
  <option value="setup">SetUp</option>
  <option value="proceso">Proceso</option>
  <option value="postproceso">Post-proceso</option>
  <option value="espera">Espera</option>
</select>

<label>Tiempo (segundos)</label>
<input id="tiempo_seg" type="number" step="1" placeholder="ej: 180" />

<label class="small">Metadatos (opcional)</label>
<input id="fuente" placeholder="ficha_tecnica / manual / estimacion" />
<input id="unidad" placeholder="unidad original (ej perforaciones/min)" />
<textarea id="notas" placeholder="cómo convertiste a min/unidad"></textarea>

<button onclick="enviar()">Guardar / Actualizar</button>
<p id="msg" class="small"></p>

<a href="/"><button style="margin-top:20px; padding:8px 16px;">⬅ Volver al inicio</button></a>

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
  document.getElementById('producto').innerHTML='<option value="">-- selecciona --</option>';
}
async function loadProductos(){
  const m=document.getElementById('maquina').value;
  const r=await fetch('/options/productos?maquina='+encodeURIComponent(m)); const d=await r.json();
  const s=document.getElementById('producto'); s.innerHTML='<option value="">-- selecciona --</option>';
  d.forEach(x=>s.innerHTML+=`<option>${x}</option>`);
}

function resetNominal(){
  document.getElementById('proceso').value = '';
  document.getElementById('maquina').innerHTML  = '<option value="">-- selecciona --</option>';
  document.getElementById('producto').innerHTML = '<option value="">-- selecciona --</option>';
  document.getElementById('tipo').value = '';
  document.getElementById('tiempo_seg').value = '';
  document.getElementById('fuente').value = '';          // <— sin valor por defecto
  document.getElementById('unidad').value = '';
  document.getElementById('notas').value = '';
}

async function enviar(){
  const btn = event?.target || document.querySelector('button[onclick="enviar()"]');
  if (btn?.disabled) return; btn && (btn.disabled = true);

  const proceso  = document.getElementById('proceso').value;
  const maquina  = document.getElementById('maquina').value;
  const producto = document.getElementById('producto').value;
  const tipo     = document.getElementById('tipo').value;
  const tseg     = Number(document.getElementById('tiempo_seg').value);

  if(!proceso || !maquina || !producto || !tipo){
    document.getElementById('msg').textContent='❌ Completa Proceso, Máquina, Producto y Tipo.';
    btn.disabled=false; return;
  }
  if(!tseg || tseg<=0){
    document.getElementById('msg').textContent='❌ Ingresa un tiempo válido en segundos.';
    btn.disabled=false; return;
  }

  const body = {
    proceso: proceso,
    maquina: maquina,
    producto: producto,
    tipo: tipo,
    tiempo_seg: Number(tseg).toFixed(3),   // segundos
    fuente: document.getElementById('fuente').value || null,
    unidad_original: document.getElementById('unidad').value || null,
    notas: document.getElementById('notas').value || null
  };

  const r=await fetch('/tiempo-nominal',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  if(r.ok){
    document.getElementById('msg').textContent='✅ Guardado/Actualizado';
    resetNominal(); loadProcesos();
  }else{
    document.getElementById('msg').textContent='❌ Error: '+(await r.text());
  }
  btn && (btn.disabled = false);
}

document.getElementById('proceso').addEventListener('change',loadMaquinas);
document.getElementById('maquina').addEventListener('change',loadProductos);
loadProcesos();
</script>
""")

@app.get("/app/experiencia", response_class=HTMLResponse)
def app_experiencia():
    return HTMLResponse(FORM_STYLE + """
<h2>Registrar tiempo por EXPERIENCIA (operario)</h2>

<label>Proceso</label><select id="proceso"></select>
<label>Máquina</label><select id="maquina"></select>
<label>Producto</label><select id="producto"></select>

<label>Tipo de tiempo</label>
<select id="tipo">
  <option value="">-- selecciona --</option>
  <option value="setup">SetUp</option>
  <option value="proceso">Proceso</option>
  <option value="postproceso">Post-proceso</option>
  <option value="espera">Espera</option>
</select>

<label>Tiempo (segundos)</label>
<input id="tiempo_seg" type="number" step="1" placeholder="ej: 180" />

<label>Bitácora / Notas (opcional)</label>
<textarea id="notas" placeholder="Observaciones del operario, condiciones, supuestos…"></textarea>

<label>Numero de operarios</label>
<input id="operario" placeholder="Nombre o iniciales" />

<button onclick="enviar()">Guardar</button>
<p id="msg" class="small"></p>

<a href="/"><button style="margin-top:20px; padding:8px 16px;">⬅ Volver al inicio</button></a>

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
  document.getElementById('producto').innerHTML='<option value="">-- selecciona --</option>';
}
async function loadProductos(){
  const m=document.getElementById('maquina').value;
  const r=await fetch('/options/productos?maquina='+encodeURIComponent(m)); const d=await r.json();
  const s=document.getElementById('producto'); s.innerHTML='<option value="">-- selecciona --</option>';
  d.forEach(x=>s.innerHTML+=`<option>${x}</option>`);
}
function resetForm(){
  document.getElementById('proceso').value='';
  document.getElementById('maquina').innerHTML='<option value="">-- selecciona --</option>';
  document.getElementById('producto').innerHTML='<option value="">-- selecciona --</option>';
  document.getElementById('tipo').value='';
  document.getElementById('tiempo_seg').value='';
  document.getElementById('notas').value='';
  document.getElementById('operario').value='';
}
async function enviar(){
  const btn = event?.target; if(btn) btn.disabled=true;
  const proceso  = document.getElementById('proceso').value;
  const maquina  = document.getElementById('maquina').value;
  const producto = document.getElementById('producto').value;
  const tipo     = document.getElementById('tipo').value;
  const tseg     = Number(document.getElementById('tiempo_seg').value);
  if(!proceso || !maquina || !producto || !tipo){
    document.getElementById('msg').textContent='❌ Completa Proceso, Máquina, Producto y Tipo.'; if(btn) btn.disabled=false; return;
  }
  if(!tseg || tseg<=0){
    document.getElementById('msg').textContent='❌ Ingresa un tiempo válido en segundos.'; if(btn) btn.disabled=false; return;
  }
  const body = {
    proceso, maquina, producto, tipo,
    tiempo_seg: Number(tseg).toFixed(3),
    operario: document.getElementById('operario').value || null,
    notas: document.getElementById('notas').value || null
  };
  const r = await fetch('/tiempo-experiencia', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(body)});
  if(r.ok){ document.getElementById('msg').textContent='✅ Guardado'; resetForm(); loadProcesos(); }
  else    { document.getElementById('msg').textContent='❌ Error: '+(await r.text()); }
  if(btn) btn.disabled=false;
}
document.getElementById('proceso').addEventListener('change',loadMaquinas);
document.getElementById('maquina').addEventListener('change',loadProductos);
loadProcesos();
</script>
""")
#--------------------------------

from Analisis_routes import router as analysis_router
app.include_router(analysis_router)

from calculo import router as calculo_router
app.include_router(calculo_router)

from calculo_pint_liquida import router as calculo_pint_liquida_router
app.include_router (calculo_pint_liquida_router)

from calc_taller_pintura import router as calc_taller_pintura_router
app.include_router(calc_taller_pintura_router)

from Calculo_Taller_Madera import router as Calculo_Taller_Madera_router
app.include_router(Calculo_Taller_Madera_router)
