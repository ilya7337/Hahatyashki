from .business_sales import create_business_sales_layout
from .customer_behavior import create_customer_behavior_layout
from .advertising_marketing import create_advertising_marketing_layout
from .service_quality import create_service_quality_layout

def create_home_layout():
    """Создать layout для домашней страницы"""
    from dash import html
    import dash_bootstrap_components as dbc
    
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H1("📊 Малинка Analytics", 
                           className="text-center mb-4",
                           style={'color': '#2C3E50'}),
                    html.P("Комплексная аналитика маркетплейса", 
                          className="text-center text-muted mb-5",
                          style={'fontSize': '1.2rem'})
                ])
            ])
        ]),
        
        dbc.Row([
            dbc.Col(
                dbc.Card([
                    dbc.CardBody([
                        html.H4("💰 Бизнес-аналитика", className="card-title"),
                        html.P("Продажи, выручка, поставщики и запасы", className="card-text"),
                        dbc.Button("Перейти", href="/business-sales", color="primary")
                    ])
                ], className="h-100 text-center"),
                lg=3, md=6, className="mb-4"
            ),
            dbc.Col(
                dbc.Card([
                    dbc.CardBody([
                        html.H4("👥 Клиенты и поведение", className="card-title"),
                        html.P("Сегментация, воронка, лояльность", className="card-text"),
                        dbc.Button("Перейти", href="/customer-behavior", color="primary")
                    ])
                ], className="h-100 text-center"),
                lg=3, md=6, className="mb-4"
            ),
            dbc.Col(
                dbc.Card([
                    dbc.CardBody([
                        html.H4("📢 Реклама и маркетинг", className="card-title"),
                        html.P("ROI кампаний, конверсия, эффективность", className="card-text"),
                        dbc.Button("Перейти", href="/advertising-marketing", color="primary")
                    ])
                ], className="h-100 text-center"),
                lg=3, md=6, className="mb-4"
            ),
            dbc.Col(
                dbc.Card([
                    dbc.CardBody([
                        html.H4("⭐ Качество обслуживания", className="card-title"),
                        html.P("Поддержка, возвраты, удовлетворенность", className="card-text"),
                        dbc.Button("Перейти", href="/service-quality", color="primary")
                    ])
                ], className="h-100 text-center"),
                lg=3, md=6, className="mb-4"
            ),
        ])
    ], fluid=True)