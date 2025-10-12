import os
from pathlib import Path
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from sqlalchemy import text
from database import engine  # ← reutiliza tu conexión existente

# ---------- Utilidades ----------
def fetch_setup_times(proceso: str, maquina: str, tipo: str = "setup", producto: str | None = None) -> pd.DataFrame:
    """
    Lee tiempo_real con los nombres (join) y filtra por proceso, máquina, tipo y opcionalmente producto.
    Devuelve columnas: fecha, proceso, maquina, producto, tipo, tiempo_seg
    """
    sql = """
        SELECT
          tr.fecha,
          p.nombre  AS proceso,
          m.nombre  AS maquina,
          pr.nombre AS producto,
          tr.tipo,
          tr.tiempo_seg::float AS tiempo_seg
        FROM tiempo_real tr
        JOIN proceso  p  ON p.id_proceso  = tr.id_proceso
        JOIN maquina  m  ON m.id_maquina  = tr.id_maquina
        JOIN producto pr ON pr.id_producto = tr.id_producto
        WHERE LOWER(p.nombre) = LOWER(:proceso)
          AND LOWER(m.nombre) = LOWER(:maquina)
          AND LOWER(tr.tipo)  = LOWER(:tipo)
          {extra_producto}
        ORDER BY tr.fecha
    """.format(extra_producto="AND LOWER(pr.nombre)=LOWER(:producto)" if producto else "")

    params = {"proceso": proceso, "maquina": maquina, "tipo": tipo}
    if producto:
        params["producto"] = producto

    with engine.connect() as conn:
        df = pd.read_sql_query(text(sql), conn, params=params)
    return df


def resumen_estadistico(x: np.ndarray) -> dict:
    n = x.size
    mean = x.mean()
    std = x.std(ddof=1) if n > 1 else np.nan
    q1, median, q3 = np.percentile(x, [25, 50, 75])
    iqr = q3 - q1
    cv = (std / mean * 100) if mean else np.nan
    if n > 1:
        tcrit = stats.t.ppf(0.975, df=n - 1)
        ci_low = mean - tcrit * std / np.sqrt(n)
        ci_high = mean + tcrit * std / np.sqrt(n)
    else:
        ci_low = ci_high = np.nan
    return {
        "n": n,
        "mean": mean, "std": std, "cv%": cv,
        "min": x.min(), "q1": q1, "median": median, "q3": q3, "max": x.max(),
        "iqr": iqr, "ci95_low": ci_low, "ci95_high": ci_high
    }


def pruebas_ajuste(x: np.ndarray) -> pd.DataFrame:
    rows = []
    n = x.size
    if n < 3:
        return pd.DataFrame(rows)

    # Normal
    mu, sigma = x.mean(), x.std(ddof=1)
    p_shapiro = stats.shapiro(x).pvalue if 3 <= n <= 5000 else np.nan
    p_ks_norm = stats.kstest(x, 'norm', args=(mu, sigma)).pvalue
    rows.append({"Distribución": "Normal", "Parámetros": f"mu={mu:.3f}, sigma={sigma:.3f}",
                 "p(KS)": p_ks_norm, "p(Shapiro)": p_shapiro})

    # Log-normal
    if np.all(x > 0):
        logx = np.log(x)
        mu_l, sig_l = logx.mean(), logx.std(ddof=1)
        p_ks_logn = stats.kstest(x, 'lognorm', args=(sig_l, 0, np.exp(mu_l))).pvalue
        rows.append({"Distribución": "Log-normal", "Parámetros": f"mu_log={mu_l:.3f}, sigma_log={sig_l:.3f}",
                     "p(KS)": p_ks_logn, "p(Shapiro)": np.nan})

    # Exponencial
    loc_e, scale_e = stats.expon.fit(x)
    p_ks_exp = stats.kstest(x, 'expon', args=(loc_e, scale_e)).pvalue
    rows.append({"Distribución": "Exponencial", "Parámetros": f"loc={loc_e:.3f}, scale={scale_e:.3f}",
                 "p(KS)": p_ks_exp, "p(Shapiro)": np.nan})

    # Gamma
    a, loc_g, scale_g = stats.gamma.fit(x)
    p_ks_gamma = stats.kstest(x, 'gamma', args=(a, loc_g, scale_g)).pvalue
    rows.append({"Distribución": "Gamma", "Parámetros": f"shape={a:.3f}, loc={loc_g:.3f}, scale={scale_g:.3f}",
                 "p(KS)": p_ks_gamma, "p(Shapiro)": np.nan})

    return pd.DataFrame(rows)


def graficos(x: np.ndarray, titulo_base: str, outdir: Path):
    outdir.mkdir(parents=True, exist_ok=True)

    # Histograma + normal escalada
    plt.figure(figsize=(7, 4))
    bins = max(5, int(np.ceil(np.sqrt(len(x)))))
    counts, bin_edges, _ = plt.hist(x, bins=bins, edgecolor="black")
    plt.title(f"{titulo_base} – Histograma")
    plt.xlabel("Tiempo (s)")
    plt.ylabel("Frecuencia")
    if len(x) > 1 and x.std(ddof=1) > 0:
        xs = np.linspace(bin_edges[0], bin_edges[-1], 200)
        pdf = stats.norm.pdf(xs, x.mean(), x.std(ddof=1))
        bin_w = bin_edges[1] - bin_edges[0]
        plt.plot(xs, pdf * len(x) * bin_w)  # escalar a frecuencias
    plt.tight_layout()
    plt.savefig(outdir / "histograma.png", dpi=150)
    plt.close()

    # QQ-plot vs normal
    if len(x) > 1 and x.std(ddof=1) > 0:
        plt.figure(figsize=(5, 5))
        stats.probplot(x, dist="norm", sparams=(x.mean(), x.std(ddof=1)), plot=plt)
        plt.title(f"{titulo_base} – QQ-plot vs Normal")
        plt.tight_layout()
        plt.savefig(outdir / "qqplot.png", dpi=150)
        plt.close()


def main():
    parser = argparse.ArgumentParser(description="Análisis de tiempos reales (setup/proceso/post/espera) desde la BD.")
    parser.add_argument("--proceso", required=True, help="Nombre del proceso (ej: 'Paneles Compuestos')")
    parser.add_argument("--maquina", required=True, help="Nombre de la máquina (ej: 'Aplicador de adhesivo (PN)')")
    parser.add_argument("--tipo",    required=True, help="Tipo: setup | proceso | postproceso | espera", default="setup")
    parser.add_argument("--producto", help="(Opcional) nombre de producto exacto")
    parser.add_argument("--out",      help="Carpeta de salida", default="outputs_analisis")
    args = parser.parse_args()

    df = fetch_setup_times(args.proceso, args.maquina, args.tipo, args.producto)
    # --- Mostrar los datos filtrados ---
    print("\n=== DATOS FILTRADOS ===")
    print(f"Total registros: {len(df)}")
    print(df.head(20).to_string(index=False))  # muestra las primeras 10 filas
    if df.empty:
        print("⚠️ No hay datos para esos filtros.")
        return

    # Estadísticos
    x = df["tiempo_seg"].to_numpy()
    resumen = resumen_estadistico(x)

    print("\n=== Resumen ===")
    for k, v in resumen.items():
        if isinstance(v, float):
            print(f"{k:>12}: {v:.3f}")
        else:
            print(f"{k:>12}: {v}")

    # Bondad de ajuste
    fits = pruebas_ajuste(x)
    if not fits.empty:
        print("\n=== Bondad de ajuste (p-valores) ===")
        print(fits.to_string(index=False))

    # Atípicos por IQR
    lo = resumen["q1"] - 1.5 * resumen["iqr"]
    hi = resumen["q3"] + 1.5 * resumen["iqr"]
    outs = df.loc[(df["tiempo_seg"] < lo) | (df["tiempo_seg"] > hi), ["fecha", "producto", "tiempo_seg"]]
    print("\n=== Posibles atípicos (IQR) ===")
    print("Ninguno" if outs.empty else outs.to_string(index=False))

    # Guardar resultados
    outdir = Path(args.out)
    graficos(x, f"{args.maquina} – {args.tipo}", outdir)
    df.to_csv(outdir / "datos_filtrados.csv", index=False)
    pd.DataFrame([resumen]).to_csv(outdir / "resumen.csv", index=False)
    if not fits.empty:
        fits.to_csv(outdir / "bondad_ajuste.csv", index=False)
    outs.to_csv(outdir / "outliers_IQR.csv", index=False)

    print(f"\n✅ Archivos generados en: {outdir.resolve()}")

if __name__ == "__main__":
    main()