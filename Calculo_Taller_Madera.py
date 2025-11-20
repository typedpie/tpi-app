# Calculo_Taller_Madera.py

from fastapi import APIRouter
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import statistics
import math

router = APIRouter()

# =========================================================
# DATOS BASE – LLENA ESTO CON TU EXCEL
# =========================================================
# Estructura:
#   - Dimensionadora: trabaja por LOTE
#       tipo = "lote"
#       tiempo_lote_min = valor columna "Tiempo Total de Lote (min/Lote)"
#       unidades_por_lote = 4   (según lo que comentaste)
#
#   - Resto de procesos: trabajan por UNIDAD
#       tipo = "unitario"
#       tiempo_min = minutos por unidad (desde tu hoja)
#
# OJO: si dejas ceros aquí, tus resultados serán basura. Esto
# hay que llenarlo con los datos REALES de la hoja.

PRODUCTOS_MADERA = {
    # --- EJEMPLO COMPLETO: AJUSTA ESTOS NÚMEROS A TU EXCEL ---

    "cielo_natura_perforado_305x1220": {
        "nombre": "Cielo natura perforado 305 1x4 (305x1220 mm)",
        "procesos": {
            "Dimensionadora": {
                "tipo": "lote",
                # TODO: pon el valor real desde la columna "Tiempo Total de Lote (min/Lote)"
                "tiempo_lote_min": 4.5,      # EJEMPLO
                "unidades_por_lote": 4,
            },
            "Tapacanto": {
                "tipo": "unitario",
                # TODO: valor real desde tu hoja (min/unidad)
                "tiempo_min": 2.0,           # EJEMPLO
            },
            "KDT": {
                "tipo": "unitario",
                "tiempo_min": 15.0,           # EJEMPLO
            },
            "Lijado": {
                "tipo": "unitario",
                "tiempo_min": 26.1667,       # EJEMPLO
            },
            "Tinta": {
                "tipo": "unitario",
                "tiempo_min": 2.0,           # EJEMPLO
            },
            "Barnizado y secado": {
                "tipo": "unitario",
                "tiempo_min": 0.5667,        # EJEMPLO
            },
            "Viledon": {
                "tipo": "unitario",
                "tiempo_min": 1.0,           # EJEMPLO
            },
        },
    },

    # A PARTIR DE AQUÍ, SOLO PLANTILLAS PARA QUE TÚ LAS LLENES.
    # Usa los nombres que ves en la hoja y copia los tiempos correctos.

    "tabla_604x1204": {
        "nombre": "Tabla 604x1204 mm",
        "procesos": {
            "Dimensionadora": {
                "tipo": "lote",
                "tiempo_lote_min": 7.75,      # TODO
                "unidades_por_lote": 4,
            },
            "Tapacanto": {"tipo": "unitario", "tiempo_min": 2.5},  # TODO
            "KDT": {"tipo": "unitario", "tiempo_min": 22.0},        # TODO
            "Lijado": {"tipo": "unitario", "tiempo_min": 26.16666667},     # TODO
            "Tinta": {"tipo": "unitario", "tiempo_min": 2.0},      # TODO
            "Barnizado y secado": {"tipo": "unitario", "tiempo_min": 0.566666667},  # TODO
            "Viledon": {"tipo": "unitario", "tiempo_min": 1.2},    # TODO
        },
    },

    "cielo_natura_1220x2440": {
        "nombre": "Cielo natura 1220x2440",
        "procesos": {
            "Dimensionadora": {
                "tipo": "lote",
                # aquí probablemente va ese 2,3529 que se ve en tu captura
                "tiempo_lote_min": 6.25,   # TODO: confirma
                "unidades_por_lote": 4,
            },
             "Tapacanto": {"tipo": "unitario", "tiempo_min": 3.0},  # TODO
            "KDT": {"tipo": "unitario", "tiempo_min": 25.0},        # TODO
            "Lijado": {"tipo": "unitario", "tiempo_min": 26.16666667},     # TODO
            "Tinta": {"tipo": "unitario", "tiempo_min": 2.0},      # TODO
            "Barnizado y secado": {"tipo": "unitario", "tiempo_min": 0.566666667},  # TODO
            "Viledon": {"tipo": "unitario", "tiempo_min": 1.0},    # TODO
        },
    },

    "cielo_natura_1220x2441": {
        "nombre": "Cielo natura 1220x2441",
        "procesos": {
            "Dimensionadora": {
                "tipo": "lote",
                "tiempo_lote_min": 6.25,      # TODO
                "unidades_por_lote": 4,
            },
            # Rellena como arriba
        },
    },

    "cielo_ranurado_especial_800x800": {
        "nombre": "Cielo ranurado especial 800x800",
        "procesos": {
            "Dimensionadora": {
                "tipo": "lote",
                "tiempo_lote_min": 5.0,      # TODO #falta verificar tiempo corte dimensionadora a este formato.
                "unidades_por_lote": 4,
            },
            # resto de procesos...
        },
    },

    "cielo_ranurado_especial_1200x1200": {
        "nombre": "Cielo ranurado especial 1200x1200",
        "procesos": {
            "Dimensionadora": {
                "tipo": "lote",
                "tiempo_lote_min": 6.0,      # TODO #falta verificar tiempo corte dimensionadora a este formato.
                "unidades_por_lote": 4,
            },
            # resto de procesos...
        },
    },

    "cielo_natura_ranurado_doble_301_tipo_B_2x4_(604x1214mm)": {
        "nombre": "Cielo natura ranurado doble 301 tipo B 2x4 (604x1214mm)",
        "procesos": {
            "Dimensionadora": {
                "tipo": "lote",
                "tiempo_lote_min": 4.5,      # TODO #falta verificar tiempo corte dimensionadora a este formato.
                "unidades_por_lote": 4,
            },
            # resto de procesos...
        },
    },




    # Y así sigues con:
    # - Cielo natura ranurado doble 301 tipo B 2x4 (varias dimensiones)
    #   rellenando todos los tiempos de la hoja.
}


# =============================
# MODELO PARA LA API DE CÁLCULO
# =============================

class CalculoMaderaRequest(BaseModel):
    producto_id: str
    cantidad: int


@router.post("/api/taller-madera/calcular")
def calcular_taller_madera(payload: CalculoMaderaRequest):
    """
    Calcula tiempos para el taller de madera considerando que:
      - Dimensionadora trabaja por LOTE.
      - Resto de procesos son por UNIDAD.
    """

    if payload.producto_id not in PRODUCTOS_MADERA:
        return JSONResponse(
            status_code=400,
            content={"error": "Producto no reconocido"},
        )

    if payload.cantidad <= 0:
        return JSONResponse(
            status_code=400,
            content={"error": "La cantidad debe ser mayor a 0"},
        )

    producto = PRODUCTOS_MADERA[payload.producto_id]
    cantidad = payload.cantidad

    detalle_procesos = []
    tiempos_unitarios_equivalentes = []

    for nombre_proc, info in producto["procesos"].items():
        tipo = info.get("tipo")
        if tipo == "lote":
            tiempo_lote = float(info["tiempo_lote_min"])
            unidades_por_lote = int(info.get("unidades_por_lote", 1))
            if unidades_por_lote <= 0:
                return JSONResponse(
                    status_code=400,
                    content={"error": f"unidades_por_lote inválido en {nombre_proc}"},
                )

            n_lotes = math.ceil(cantidad / unidades_por_lote)
            tiempo_total_min = n_lotes * tiempo_lote
            tiempo_unit_equivalente = tiempo_total_min / cantidad  # min/unidad efectivos

            detalle_procesos.append({
                "proceso": nombre_proc,
                "tipo": "lote",
                "tiempo_lote_min": round(tiempo_lote, 3),
                "unidades_por_lote": unidades_por_lote,
                "lotes_necesarios": n_lotes,
                "tiempo_unit_min_equivalente": round(tiempo_unit_equivalente, 3),
                "tiempo_total_min": round(tiempo_total_min, 3),
            })
            tiempos_unitarios_equivalentes.append(tiempo_unit_equivalente)

        elif tipo == "unitario":
            tiempo_unit = float(info["tiempo_min"])
            tiempo_total_min = tiempo_unit * cantidad

            detalle_procesos.append({
                "proceso": nombre_proc,
                "tipo": "unitario",
                "tiempo_unit_min": round(tiempo_unit, 3),
                "tiempo_total_min": round(tiempo_total_min, 3),
            })
            tiempos_unitarios_equivalentes.append(tiempo_unit)

        else:
            return JSONResponse(
                status_code=400,
                content={"error": f"Tipo de proceso desconocido en {nombre_proc}"},
            )

    # Tiempo total y unitario promedio de TODA la orden
    tiempo_total_min = sum(p["tiempo_total_min"] for p in detalle_procesos)
    tiempo_total_horas = tiempo_total_min / 60.0
    tiempo_unitario_promedio_min = tiempo_total_min / cantidad

    # Estadísticos entre procesos (usando equivalentes min/unidad)
    promedio_proceso_min = statistics.mean(tiempos_unitarios_equivalentes)
    desv_proceso_min = (
        statistics.pstdev(tiempos_unitarios_equivalentes)
        if len(tiempos_unitarios_equivalentes) > 1
        else 0.0
    )

    idx_lento = max(
        range(len(tiempos_unitarios_equivalentes)),
        key=lambda i: tiempos_unitarios_equivalentes[i],
    )
    idx_rapido = min(
        range(len(tiempos_unitarios_equivalentes)),
        key=lambda i: tiempos_unitarios_equivalentes[i],
    )
    proceso_lento = detalle_procesos[idx_lento]
    proceso_rapido = detalle_procesos[idx_rapido]

    return {
        "producto_id": payload.producto_id,
        "producto_nombre": producto["nombre"],
        "cantidad": cantidad,
        "tiempo_total_min": round(tiempo_total_min, 3),
        "tiempo_total_horas": round(tiempo_total_horas, 3),
        "tiempo_unitario_promedio_min": round(tiempo_unitario_promedio_min, 3),
        "promedio_proceso_min": round(promedio_proceso_min, 3),
        "desviacion_proceso_min": round(desv_proceso_min, 3),
        "proceso_mas_lento": proceso_lento,
        "proceso_mas_rapido": proceso_rapido,
        "procesos": detalle_procesos,
    }


# =====================
# PÁGINA WEB / FRONTEND
# =====================

FORM_STYLE = """
<style>
body{font-family:system-ui,-apple-system,Segoe UI,Roboto;padding:14px;max-width:720px;margin:auto;background:#f5f5f5}
h2{margin-top:0}
label{display:block;margin-top:12px;font-weight:600}
input,select,button,textarea{width:100%;padding:10px;margin-top:6px;border-radius:8px;border:1px solid #ddd;font-size:15px}
button{background:#111;color:#fff;border:none;cursor:pointer}
button[disabled]{opacity:0.6;cursor:not-allowed}
.small{font-size:12px;color:#666}
.result-card{margin-top:18px;padding:14px;border-radius:10px;background:#fff;border:1px solid #ddd}
.result-card h3{margin-top:0}
table{width:100%;border-collapse:collapse;margin-top:10px;font-size:14px}
th,td{border:1px solid #ddd;padding:6px;text-align:left}
th{background:#fafafa}
.badge{{display:inline-block;padding:2px 6px;border-radius:999px;font-size:11px;border:1px solid #ccc;margin-left:6px}}
</style>
"""


@router.get("/app/taller-madera", response_class=HTMLResponse)
def page_taller_madera():
    options = "\n".join(
        f'<option value="{pid}">{data["nombre"]}</option>'
        for pid, data in PRODUCTOS_MADERA.items()
    )

    html = FORM_STYLE + f"""
<h2>Calculadora – Taller de Madera</h2>
<p class="small">
  Selecciona el producto, indica la cantidad de unidades a producir y
  se calculará el tiempo total de producción considerando que la
  dimensionadora trabaja por lote (4 unidades por plancha).
</p>

<label>Producto</label>
<select id="producto">
  <option value="">-- selecciona --</option>
  {options}
</select>

<label>Cantidad de unidades</label>
<input id="cantidad" type="number" min="1" step="1" placeholder="ej: 100" />

<button onclick="calcular()">Calcular</button>
<p id="msg" class="small"></p>

<div id="resultado"></div>

<a href="/"><button style="margin-top:20px; padding:8px 16px;">⬅ Volver al inicio</button></a>

<script>
async function calcular(){{
    const btn = event?.target; if (btn) btn.disabled = true;

    const producto = document.getElementById('producto').value;
    const cantidad = Number(document.getElementById('cantidad').value);
    const msg      = document.getElementById('msg');
    const resDiv   = document.getElementById('resultado');
    msg.textContent = '';
    resDiv.innerHTML = '';

    if (!producto) {{
        msg.textContent = '❌ Selecciona un producto.';
        if (btn) btn.disabled = false;
        return;
    }}
    if (!cantidad || cantidad <= 0){{
        msg.textContent = '❌ Ingresa una cantidad válida (> 0).';
        if (btn) btn.disabled = false;
        return;
    }}

    try {{
        const r = await fetch('/api/taller-madera/calcular', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{ producto_id: producto, cantidad: cantidad }})
        }});
        const data = await r.json();
        if (!r.ok){{
            msg.textContent = '❌ Error: ' + (data.error || JSON.stringify(data));
            if (btn) btn.disabled = false;
            return;
        }}
        msg.textContent = '✅ Cálculo realizado';

        const filasProcesos = data.procesos.map(p => {{
            if (p.tipo === 'lote') {{
                return `
                  <tr>
                    <td>${{p.proceso}} <span class="badge">lote</span></td>
                    <td>${{p.tiempo_unit_min_equivalente.toFixed(3)}} min/unidad (equivalente)</td>
                    <td>${{p.tiempo_total_min.toFixed(3)}} min</td>
                    <td>${{p.tiempo_lote_min.toFixed(3)}} min/lote · ${{p.unidades_por_lote}} u/lote · ${{p.lotes_necesarios}} lotes</td>
                  </tr>
                `;
            }} else {{
                return `
                  <tr>
                    <td>${{p.proceso}} <span class="badge">unitario</span></td>
                    <td>${{p.tiempo_unit_min.toFixed(3)}} min/unidad</td>
                    <td>${{p.tiempo_total_min.toFixed(3)}} min</td>
                    <td>—</td>
                  </tr>
                `;
            }}
        }}).join('');

        const lento = data.proceso_mas_lento;
        const rapido = data.proceso_mas_rapido;

        resDiv.innerHTML = `
          <div class="result-card">
            <h3>Resultado</h3>
            <p><b>Producto:</b> ${{data.producto_nombre}}</p>
            <p><b>Cantidad:</b> ${{data.cantidad}} unidades</p>
            <p><b>Tiempo total del lote:</b> ${{data.tiempo_total_min}} min (~ ${{data.tiempo_total_horas}} h)</p>
            <p><b>Tiempo promedio por unidad:</b> ${{data.tiempo_unitario_promedio_min}} min/unidad</p>
            <p><b>Promedio entre procesos (equivalente):</b> ${{data.promedio_proceso_min}} min/proceso</p>
            <p><b>Desviación estándar entre procesos:</b> ${{data.desviacion_proceso_min}} min</p>
            <p><b>Proceso más lento (equivalente):</b> ${{lento.proceso}} – ${{lento.tiempo_total_min.toFixed(3)}} min totales</p>
            <p><b>Proceso más rápido (equivalente):</b> ${{rapido.proceso}} – ${{rapido.tiempo_total_min.toFixed(3)}} min totales</p>

            <h4>Detalle por proceso</h4>
            <table>
              <tr>
                <th>Proceso / Máquina</th>
                <th>Tiempo por unidad</th>
                <th>Tiempo total (orden)</th>
                <th>Detalle lote/unitario</th>
              </tr>
              ${{filasProcesos}}
            </table>
          </div>
        `;
    }} catch (err) {{
        console.error(err);
        msg.textContent = '❌ Error inesperado en el cálculo.';
    }} finally {{
        if (btn) btn.disabled = false;
    }}
}}
</script>
"""
    return HTMLResponse(html)
