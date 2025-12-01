"""
Dashboard Interativo para Sistema de Gestão de Estoque Inteligente
Visualização em tempo real com Plotly Dash
"""

import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
sys.path.append('/home/ubuntu/projeto_iot_estoque/src')

from iot_simulator import IoTSensorSimulator
from ai_models import (ManutencaoPreditiva, PrevisaoDemanda, 
                       DeteccaoAnomalias, OtimizacaoEstoque)

# Inicializa simulador e modelos
print("Inicializando sistema...")
simulator = IoTSensorSimulator(num_equipamentos=50)
df_metricas = simulator.gerar_dados_historicos(dias=90, intervalo_horas=6)
df_movimentacoes = simulator.gerar_movimentacoes_historicas(dias=90)

# Treina modelos
modelo_manutencao = ManutencaoPreditiva()
modelo_manutencao.treinar(df_metricas)

modelo_anomalias = DeteccaoAnomalias()
modelo_anomalias.treinar(df_metricas)

modelo_demanda = PrevisaoDemanda()
modelo_otimizacao = OtimizacaoEstoque()

print("✓ Sistema inicializado com sucesso!")

# Inicializa app Dash
app = dash.Dash(__name__)
app.title = "SmartStock IoT - Dashboard"

# Layout do Dashboard
app.layout = html.Div([
    html.Div([
        html.H1("🔧 SmartStock IoT", style={'color': '#2c3e50', 'textAlign': 'center'}),
        html.H3("Sistema Inteligente de Gestão de Estoque com Manutenção Preditiva", 
                style={'color': '#7f8c8d', 'textAlign': 'center', 'marginBottom': '30px'}),
    ]),
    
    # Linha 1: Cards de Resumo
    html.Div([
        html.Div([
            html.H4("📦 Estoque Total"),
            html.H2(f"{len(simulator.equipamentos)}", style={'color': '#3498db'}),
            html.P("equipamentos")
        ], className='card', style={'width': '23%', 'display': 'inline-block', 'margin': '1%', 
                                     'padding': '20px', 'backgroundColor': '#ecf0f1', 'borderRadius': '10px'}),
        
        html.Div([
            html.H4("⚠️ Críticos"),
            html.H2(f"{len(simulator.equipamentos[simulator.equipamentos['estado'] == 'Crítico'])}", 
                    style={'color': '#e74c3c'}),
            html.P("precisam atenção")
        ], className='card', style={'width': '23%', 'display': 'inline-block', 'margin': '1%', 
                                     'padding': '20px', 'backgroundColor': '#ecf0f1', 'borderRadius': '10px'}),
        
        html.Div([
            html.H4("🔄 Em Uso"),
            html.H2(f"{len(simulator.obter_equipamentos_em_uso())}", style={'color': '#f39c12'}),
            html.P("equipamentos ativos")
        ], className='card', style={'width': '23%', 'display': 'inline-block', 'margin': '1%', 
                                     'padding': '20px', 'backgroundColor': '#ecf0f1', 'borderRadius': '10px'}),
        
        html.Div([
            html.H4("✅ Disponíveis"),
            html.H2(f"{len(simulator.obter_nivel_estoque_atual())}", style={'color': '#27ae60'}),
            html.P("no almoxarifado")
        ], className='card', style={'width': '23%', 'display': 'inline-block', 'margin': '1%', 
                                     'padding': '20px', 'backgroundColor': '#ecf0f1', 'borderRadius': '10px'}),
    ]),
    
    html.Hr(),
    
    # Linha 2: Gráficos Principais
    html.Div([
        # Gráfico 1: Distribuição por Estado
        html.Div([
            html.H4("Estado dos Equipamentos"),
            dcc.Graph(id='grafico-estado')
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),
        
        # Gráfico 2: Estoque por Categoria
        html.Div([
            html.H4("Estoque por Categoria"),
            dcc.Graph(id='grafico-categoria')
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),
    ]),
    
    # Linha 3: Manutenção Preditiva
    html.Div([
        html.H3("🔮 Manutenção Preditiva - Equipamentos em Risco", 
                style={'color': '#e74c3c', 'marginTop': '20px'}),
        html.Div(id='tabela-manutencao')
    ]),
    
    html.Hr(),
    
    # Linha 4: Previsão de Demanda
    html.Div([
        html.H3("📈 Previsão de Demanda (Próximos 30 dias)", 
                style={'color': '#3498db', 'marginTop': '20px'}),
        dcc.Graph(id='grafico-demanda')
    ]),
    
    html.Hr(),
    
    # Linha 5: Alertas e Recomendações
    html.Div([
        html.H3("🚨 Alertas e Recomendações", style={'color': '#f39c12', 'marginTop': '20px'}),
        html.Div(id='alertas-container')
    ]),
    
    # Intervalo para atualização (simulação de tempo real)
    dcc.Interval(
        id='interval-component',
        interval=10*1000,  # atualiza a cada 10 segundos
        n_intervals=0
    )
])

# Callbacks para atualização dos gráficos
@app.callback(
    Output('grafico-estado', 'figure'),
    Input('interval-component', 'n_intervals')
)
def atualizar_grafico_estado(n):
    df_estado = simulator.equipamentos.groupby('estado').size().reset_index(name='quantidade')
    
    fig = px.pie(df_estado, values='quantidade', names='estado',
                 color='estado',
                 color_discrete_map={'Novo': '#27ae60', 'Bom': '#3498db', 
                                    'Atenção': '#f39c12', 'Crítico': '#e74c3c'})
    fig.update_layout(showlegend=True)
    return fig

@app.callback(
    Output('grafico-categoria', 'figure'),
    Input('interval-component', 'n_intervals')
)
def atualizar_grafico_categoria(n):
    df_cat = simulator.obter_nivel_estoque_atual()
    
    fig = px.bar(df_cat, x='categoria', y='quantidade',
                 color='quantidade', color_continuous_scale='Blues')
    fig.update_layout(xaxis_title="Categoria", yaxis_title="Quantidade em Estoque")
    return fig

@app.callback(
    Output('tabela-manutencao', 'children'),
    Input('interval-component', 'n_intervals')
)
def atualizar_tabela_manutencao(n):
    # Analisa equipamentos em uso
    equipamentos_risco = []
    
    for _, equip in simulator.obter_equipamentos_em_uso().head(10).iterrows():
        metricas = simulator.gerar_metricas_uso(equip['id'])
        predicao = modelo_manutencao.prever(metricas)
        
        if predicao['probabilidade_falha'] > 0.5:
            equipamentos_risco.append({
                'ID': equip['id'],
                'Categoria': equip['categoria'],
                'Estado': equip['estado'],
                'Idade (meses)': equip['idade_meses'],
                'Prob. Falha': f"{predicao['probabilidade_falha']:.1%}",
                'Risco': predicao['nivel_risco'],
                'Ação': 'Manutenção Urgente' if predicao['probabilidade_falha'] > 0.7 else 'Agendar Manutenção'
            })
    
    if not equipamentos_risco:
        return html.P("✅ Nenhum equipamento em risco crítico no momento.", 
                     style={'color': '#27ae60', 'fontSize': '16px'})
    
    df_risco = pd.DataFrame(equipamentos_risco)
    
    return dash_table.DataTable(
        data=df_risco.to_dict('records'),
        columns=[{'name': col, 'id': col} for col in df_risco.columns],
        style_cell={'textAlign': 'left', 'padding': '10px'},
        style_header={'backgroundColor': '#e74c3c', 'color': 'white', 'fontWeight': 'bold'},
        style_data_conditional=[
            {
                'if': {'filter_query': '{Risco} = "Alto"'},
                'backgroundColor': '#fadbd8',
                'color': '#e74c3c'
            }
        ]
    )

@app.callback(
    Output('grafico-demanda', 'figure'),
    Input('interval-component', 'n_intervals')
)
def atualizar_grafico_demanda(n):
    # Prevê demanda para cada categoria
    categorias = simulator.equipamentos['categoria'].unique()
    previsoes = []
    
    for cat in categorias[:5]:  # Top 5 categorias
        prev = modelo_demanda.prever_demanda(df_movimentacoes, cat, dias_futuros=30)
        if prev:
            previsoes.append({
                'Categoria': cat,
                'Demanda Prevista': prev['demanda_prevista'],
                'Min': prev['intervalo_confianca'][0],
                'Max': prev['intervalo_confianca'][1]
            })
    
    df_prev = pd.DataFrame(previsoes)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_prev['Categoria'],
        y=df_prev['Demanda Prevista'],
        name='Previsão',
        marker_color='#3498db'
    ))
    
    fig.update_layout(
        xaxis_title="Categoria",
        yaxis_title="Unidades (próximos 30 dias)",
        showlegend=True
    )
    
    return fig

@app.callback(
    Output('alertas-container', 'children'),
    Input('interval-component', 'n_intervals')
)
def atualizar_alertas(n):
    alertas = []
    
    # Alerta 1: Estoque baixo
    estoque = simulator.obter_nivel_estoque_atual()
    for _, row in estoque.iterrows():
        if row['quantidade'] < 3:
            alertas.append(
                html.Div([
                    html.H5(f"⚠️ Estoque Baixo: {row['categoria']}", style={'color': '#e74c3c'}),
                    html.P(f"Apenas {row['quantidade']} unidades disponíveis. Recomenda-se compra urgente.")
                ], style={'backgroundColor': '#fadbd8', 'padding': '15px', 'borderRadius': '5px', 'margin': '10px'})
            )
    
    # Alerta 2: Equipamentos críticos
    criticos = simulator.equipamentos[simulator.equipamentos['estado'] == 'Crítico']
    if len(criticos) > 0:
        alertas.append(
            html.Div([
                html.H5(f"🔴 {len(criticos)} Equipamentos Críticos", style={'color': '#e74c3c'}),
                html.P(f"Equipamentos precisam de substituição ou manutenção imediata.")
            ], style={'backgroundColor': '#fadbd8', 'padding': '15px', 'borderRadius': '5px', 'margin': '10px'})
        )
    
    # Alerta 3: Anomalias detectadas
    alertas.append(
        html.Div([
            html.H5(f"🔍 Sistema de Detecção Ativo", style={'color': '#3498db'}),
            html.P(f"Monitoramento contínuo de anomalias em {len(simulator.obter_equipamentos_em_uso())} equipamentos.")
        ], style={'backgroundColor': '#d6eaf8', 'padding': '15px', 'borderRadius': '5px', 'margin': '10px'})
    )
    
    if not alertas:
        return html.P("✅ Nenhum alerta no momento. Sistema operando normalmente.", 
                     style={'color': '#27ae60', 'fontSize': '16px'})
    
    return html.Div(alertas)


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Iniciando Dashboard SmartStock IoT")
    print("="*60)
    print("\n📊 Acesse o dashboard em: http://localhost:8050")
    print("\n⚠️  Pressione Ctrl+C para encerrar\n")
    
    app.run_server(debug=False, host='0.0.0.0', port=8050)
