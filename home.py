from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["home"])

@router.get("/", response_class=HTMLResponse)
def home():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>TPI · Captura de Tiempos</title>

        <!-- Fuente y estilos básicos -->
        <style>
            *{box-sizing:border-box;margin:0;padding:0}
            body{
                font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
                color:#ffffff;
                background:#000;
            }

            /* HERO PRINCIPAL */
            .hero{
                min-height:100vh;
                display:flex;
                flex-direction:column;
                justify-content:space-between;
                background-image:
                    linear-gradient(120deg,rgba(0,0,0,0.65),rgba(0,0,0,0.35)),
                    url("/static/img/hd_hero.jpg");
                background-size:cover;
                background-position:center;
            }

            /* NAVBAR SUPERIOR */
            .navbar{
                display:flex;
                align-items:center;
                justify-content:space-between;
                padding:18px 56px;
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
                height:34px;
            }
            .brand-divider{
                width:1px;
                height:28px;
                background:rgba(255,255,255,0.35);
            }

            .nav-menu{
                list-style:none;
                display:flex;
                align-items:center;
                gap:28px;
                font-size:0.92rem;
                text-transform:uppercase;
                letter-spacing:0.09em;
            }
            .nav-menu > li{
                position:relative;
                cursor:pointer;
                padding-bottom:14px;        
            }
            .nav-link{
                color:#f9fafb;
                text-decoration:none;
                padding-bottom:3px;
            }
            .nav-link:hover{
                border-bottom:2px solid #f97316; /* naranja HD */
            }

            /* DROPDOWN */
            .dropdown{
                display:none;
                position:absolute;
                top:100%;
                left:0;
                margin-top=8px;        
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
                font-size:0.86rem;
                color:#e5e7eb;
                text-decoration:none;
                white-space:nowrap;
            }
            .dropdown a span{
                display:block;
                font-size:0.75rem;
                color:#9ca3af;
            }
            .dropdown a:hover{
                background:rgba(249,115,22,0.08);
                color:#ffffff;
            }

            /* BOTÓN CTA */
            .cta-btn{
                background:#f97316;
                color:#111827;
                border-radius:999px;
                padding:9px 20px;
                font-size:0.84rem;
                font-weight:600;
                border:none;
                text-decoration:none;
                text-transform:uppercase;
                letter-spacing:0.08em;
                box-shadow:0 12px 30px rgba(249,115,22,0.40);
            }
            .cta-btn:hover{
                filter:brightness(1.05);
            }

            /* CONTENIDO CENTRAL */
            .hero-content{
                padding:0 56px 72px 56px;
                max-width:760px;
            }
            .hero-kicker{
                font-size:0.85rem;
                letter-spacing:0.12em;
                text-transform:uppercase;
                color:#fed7aa;
                margin-bottom:10px;
            }
            .hero-title{
                font-size:2.8rem;
                line-height:1.1;
                font-weight:700;
                margin-bottom:14px;
            }
            .hero-subtitle{
                font-size:1rem;
                color:#e5e7eb;
                max-width:620px;
                margin-bottom:24px;
            }
            .hero-tags{
                display:flex;
                flex-wrap:wrap;
                gap:10px;
            }
            .tag-pill{
                border-radius:999px;
                border:1px solid rgba(248,250,252,0.3);
                padding:6px 12px;
                font-size:0.8rem;
                color:#e5e7eb;
                background:rgba(15,23,42,0.4);
            }

            /* FOOTER PEQUEÑO */
            .hero-footer{
                padding:0 56px 22px 56px;
                font-size:0.75rem;
                color:#e5e7eb;
                display:flex;
                justify-content:space-between;
                opacity:0.85;
            }

            /* RESPONSIVE */
            @media (max-width:800px){
                .navbar{
                    padding:15px 20px;
                    flex-wrap:wrap;
                    gap:10px;
                }
                .nav-menu{
                    gap:18px;
                    font-size:0.8rem;
                }
                .hero-content{
                    padding:10px 20px 40px 20px;
                }
                .hero-title{
                    font-size:2rem;
                }
                .hero-footer{
                    padding:0 20px 18px 20px;
                    flex-direction:column;
                    gap:4px;
                }
            }
        </style>
    </head>
                        
    
    
                        
    <body>
        <section class="hero">

            <!-- NAV SUPERIOR -->
            <header class="navbar">
                <!-- Logos -->
                <div class="brand">
                    <div class="brand-logo">
                        <img src="/static/img/logo_hd.png" alt="Hunter Douglas">
                    </div>
                    <div class="brand-divider"></div>
                    <div class="brand-logo">
                        <img src="/static/img/logo_udd.png" alt="Universidad del Desarrollo">
                    </div>
                </div>

                <!-- Menú -->
                <nav>
                    <ul class="nav-menu">
                        <li>
                            <a href="/" class="nav-link">Inicio</a>
                        </li>

                        <!-- TOMAR TIEMPOS -->
                        <li>
                            <span class="nav-link">Tomar tiempos ▾</span>
                            <div class="dropdown">
                                <a href="/app/real">
                                    Tiempos REALES
                                    <span>Captura directa en taller (setup, proceso, postproceso).</span>
                                </a>
                                <a href="/app/experiencia">
                                    Tiempos EXPERIENCIA
                                    <span>Estimación según experiencia de jefes y operarios.</span>
                                </a>
                                <a href="/app/nominal">
                                    Tiempos NOMINALES
                                    <span>Valores estándar para planificación y costos.</span>
                                </a>
                                <a href="/app/analisis">
                                    Análisis de datos
                                    <span>Histogramas, promedios y outliers de tiempos reales.</span>
                                </a>
                            </div>
                        </li>

                        <!-- CALCULADORAS -->
                        <li>
                            <span class="nav-link">Calculadoras ▾</span>
                            <div class="dropdown">
                                <a href="/app/calculo">
                                    Paneles compuestos
                                    <span>Capacidad de producción y días de trabajo por pedido.</span>
                                </a>
                                <!-- cuando tengas más talleres, los agregamos acá -->
                                <a href="/app/pintura-liquida">
                                    Linea de pintura liquida
                                    <span>Tiempo de pintado para un rollo en bruto.</span>
                                </a>
                                <a href="/app/taller-pintura">
                                    Taller de pintura
                                    <span> Tiempo de pintado para linea electroestatica o electroliquida.</span>
                                </a>
                                <a href="/app/sliding-folding">
                                    Taller de Sliding & Folding
                                    <span>Tiempo de fabricación para ventanas correderas.</span>
                            </div>
                        </li>

                        <li>
                            <a href="#sobre" class="nav-link">Sobre el proyecto</a>
                        </li>

                        <li>
                            <a href="/admin/login" class="cta-btn">Modo admin</a>
                        </li>
                    </ul>
                </nav>
            </header>

            <!-- CONTENIDO CENTRAL -->
            <main class="hero-content">
                <div class="hero-kicker">Plataforma TPI · Hunter Douglas</div>
                <h1 class="hero-title">
                    Captura y análisis de tiempos<br>para talleres de producción.
                </h1>
                <p class="hero-subtitle">
                    Esta herramienta permite registrar tiempos reales, nominales y por experiencia en los 
                    distintos procesos de Hunter Douglas, y estimar la capacidad diaria de producción de 
                    sus talleres.
                </p>

                <div class="hero-tags">
                    <div class="tag-pill">Talleres de la linea arquitectonica</div>
                    <div class="tag-pill">Estimación de costos </div>
                    <div class="tag-pill">Proyecto Ingeniería · UDD</div>
                </div>
            </main>

            <!-- PIE -->
            <footer class="hero-footer">
                <span>© Hunter Douglas · Proyecto TPI Universidad del Desarrollo</span>
                <span>Versión interna para análisis de tiempos de producción</span>
            </footer>
        </section>
    </body>
    </html>
    """)
