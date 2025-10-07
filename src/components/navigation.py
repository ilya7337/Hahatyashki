from dash import html
import dash_bootstrap_components as dbc

def create_navigation():
    """Создать навигационное меню"""
    return dbc.Navbar(
        dbc.Container([
            # Бренд
            dbc.NavbarBrand(
                "📊 Малинка Analytics",
                href="/",
                style={
                    'fontSize': '1.5rem',
                    'fontWeight': '700',
                    'color': 'white'
                }
            ),
            
            # Навигационные ссылки
            dbc.Nav([
                dbc.NavItem(
                    dbc.NavLink(
                        "💰 Бизнес-аналитика",
                        href="/",
                        active="exact",
                        style={
                            'fontWeight': '600',
                            'color': 'rgba(255,255,255,0.9)'
                        }
                    )
                ),
                dbc.NavItem(
                    dbc.NavLink(
                        "👥 Клиенты и поведение", 
                        href="/customer-behavior",
                        active="exact",
                        style={
                            'fontWeight': '600', 
                            'color': 'rgba(255,255,255,0.9)'
                        }
                    )
                ),
                dbc.NavItem(
                    dbc.NavLink(
                        "📢 Реклама и маркетинг",
                        href="/advertising-marketing", 
                        active="exact",
                        style={
                            'fontWeight': '600',
                            'color': 'rgba(255,255,255,0.9)'
                        }
                    )
                ),
                dbc.NavItem(
                    dbc.NavLink(
                        "⭐ Качество обслуживания",
                        href="/service-quality",
                        active="exact", 
                        style={
                            'fontWeight': '600',
                            'color': 'rgba(255,255,255,0.9)'
                        }
                    )
                ),
            ], className="ms-auto", navbar=True),
        ], fluid=True),
        color="primary",
        dark=True,
        sticky="top",
        style={
            'boxShadow': '0 2px 10px rgba(0,0,0,0.1)',
            'marginBottom': '20px'
        }
    )