"""
Simulador de Sensores IoT para Gestão de Estoque
Simula sensores RFID, temperatura, uso de equipamentos, etc.
"""

import random
import time
import json
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

class IoTSensorSimulator:
    """Simula sensores IoT para monitoramento de estoque de equipamentos de TI"""
    
    def __init__(self, num_equipamentos=50):
        self.num_equipamentos = num_equipamentos
        self.equipamentos = self._gerar_equipamentos()
        self.historico_metricas = []
        
    def _gerar_equipamentos(self):
        """Gera lista de equipamentos com características iniciais"""
        categorias = ['Notebook', 'Desktop', 'Monitor', 'Servidor', 'Switch', 'Roteador']
        fabricantes = ['Dell', 'HP', 'Lenovo', 'Cisco', 'Apple']
        localizacoes = ['Almoxarifado A', 'Almoxarifado B', 'Em Uso - TI', 'Em Uso - Vendas', 'Manutenção']
        estados = ['Novo', 'Bom', 'Atenção', 'Crítico']
        
        equipamentos = []
        for i in range(self.num_equipamentos):
            # Idade do equipamento em meses (0 a 60 meses)
            idade_meses = random.randint(0, 60)
            
            # Estado baseado na idade
            if idade_meses < 6:
                estado = 'Novo'
            elif idade_meses < 24:
                estado = 'Bom'
            elif idade_meses < 48:
                estado = 'Atenção'
            else:
                estado = 'Crítico'
            
            equip = {
                'id': f'EQ{i+1:04d}',
                'rfid': f'RFID{random.randint(10000, 99999)}',
                'categoria': random.choice(categorias),
                'fabricante': random.choice(fabricantes),
                'modelo': f'Model-{random.randint(1000, 9999)}',
                'localizacao': random.choice(localizacoes),
                'estado': estado,
                'idade_meses': idade_meses,
                'data_aquisicao': (datetime.now() - timedelta(days=idade_meses*30)).strftime('%Y-%m-%d'),
                'valor_aquisicao': random.randint(1000, 10000),
                'em_uso': random.choice([True, False])
            }
            equipamentos.append(equip)
        
        return pd.DataFrame(equipamentos)
    
    def gerar_metricas_uso(self, equipamento_id):
        """Gera métricas de uso para um equipamento específico"""
        equip = self.equipamentos[self.equipamentos['id'] == equipamento_id].iloc[0]
        
        # Métricas variam baseadas no estado do equipamento
        estado = equip['estado']
        idade = equip['idade_meses']
        
        # Temperatura (°C) - aumenta com idade e estado crítico
        temp_base = 35
        if estado == 'Crítico':
            temperatura = temp_base + random.uniform(15, 25)
        elif estado == 'Atenção':
            temperatura = temp_base + random.uniform(5, 15)
        else:
            temperatura = temp_base + random.uniform(0, 5)
        
        # Uso de CPU (%) - aumenta com degradação
        if estado == 'Crítico':
            cpu_uso = random.uniform(70, 100)
        elif estado == 'Atenção':
            cpu_uso = random.uniform(40, 70)
        else:
            cpu_uso = random.uniform(10, 40)
        
        # Uso de RAM (%)
        if estado == 'Crítico':
            ram_uso = random.uniform(80, 100)
        elif estado == 'Atenção':
            ram_uso = random.uniform(50, 80)
        else:
            ram_uso = random.uniform(20, 50)
        
        # Uso de Disco (%)
        disco_uso = min(100, idade * 1.5 + random.uniform(0, 20))
        
        # Saúde da Bateria (%) - degrada com idade
        if equip['categoria'] in ['Notebook']:
            bateria_saude = max(0, 100 - (idade * 1.5) + random.uniform(-10, 10))
        else:
            bateria_saude = None
        
        # Número de falhas acumuladas
        if estado == 'Crítico':
            num_falhas = random.randint(5, 15)
        elif estado == 'Atenção':
            num_falhas = random.randint(1, 5)
        else:
            num_falhas = random.randint(0, 1)
        
        metricas = {
            'equipamento_id': equipamento_id,
            'timestamp': datetime.now().isoformat(),
            'temperatura_c': round(temperatura, 2),
            'cpu_uso_percent': round(cpu_uso, 2),
            'ram_uso_percent': round(ram_uso, 2),
            'disco_uso_percent': round(disco_uso, 2),
            'bateria_saude_percent': round(bateria_saude, 2) if bateria_saude else None,
            'num_falhas': num_falhas,
            'estado': estado
        }
        
        return metricas
    
    def gerar_sensor_temperatura_ambiente(self, localizacao):
        """Gera leitura de sensor de temperatura do ambiente de armazenamento"""
        # Temperatura ideal: 18-24°C, Umidade ideal: 40-60%
        temperatura = random.uniform(18, 26)
        umidade = random.uniform(35, 65)
        
        return {
            'localizacao': localizacao,
            'timestamp': datetime.now().isoformat(),
            'temperatura_c': round(temperatura, 2),
            'umidade_percent': round(umidade, 2)
        }
    
    def simular_movimentacao(self, equipamento_id, nova_localizacao):
        """Simula movimentação de equipamento (entrada/saída de estoque)"""
        idx = self.equipamentos[self.equipamentos['id'] == equipamento_id].index[0]
        localizacao_anterior = self.equipamentos.at[idx, 'localizacao']
        self.equipamentos.at[idx, 'localizacao'] = nova_localizacao
        
        movimentacao = {
            'equipamento_id': equipamento_id,
            'timestamp': datetime.now().isoformat(),
            'tipo': 'SAIDA' if 'Em Uso' in nova_localizacao else 'ENTRADA',
            'localizacao_origem': localizacao_anterior,
            'localizacao_destino': nova_localizacao
        }
        
        return movimentacao
    
    def gerar_dados_historicos(self, dias=90, intervalo_horas=6):
        """Gera dados históricos para treinamento de modelos de IA"""
        print(f"Gerando dados históricos de {dias} dias...")
        
        historico = []
        data_inicial = datetime.now() - timedelta(days=dias)
        
        # Gera métricas em intervalos regulares
        num_leituras = int((dias * 24) / intervalo_horas)
        
        for i in range(num_leituras):
            timestamp = data_inicial + timedelta(hours=i * intervalo_horas)
            
            # Gera métricas para equipamentos em uso
            for _, equip in self.equipamentos[self.equipamentos['em_uso'] == True].iterrows():
                metricas = self.gerar_metricas_uso(equip['id'])
                metricas['timestamp'] = timestamp.isoformat()
                historico.append(metricas)
        
        df_historico = pd.DataFrame(historico)
        print(f"✓ Gerados {len(df_historico)} registros históricos")
        
        return df_historico
    
    def gerar_movimentacoes_historicas(self, dias=90):
        """Gera histórico de movimentações para análise de demanda"""
        print(f"Gerando movimentações históricas de {dias} dias...")
        
        movimentacoes = []
        data_inicial = datetime.now() - timedelta(days=dias)
        
        # Simula movimentações aleatórias
        num_movimentacoes = random.randint(100, 300)
        
        for i in range(num_movimentacoes):
            timestamp = data_inicial + timedelta(days=random.uniform(0, dias))
            equipamento = self.equipamentos.sample(1).iloc[0]
            
            # Alterna entre entrada e saída
            if random.random() > 0.5:
                tipo = 'SAIDA'
                destino = random.choice(['Em Uso - TI', 'Em Uso - Vendas', 'Em Uso - RH'])
            else:
                tipo = 'ENTRADA'
                destino = random.choice(['Almoxarifado A', 'Almoxarifado B'])
            
            mov = {
                'equipamento_id': equipamento['id'],
                'categoria': equipamento['categoria'],
                'timestamp': timestamp.isoformat(),
                'tipo': tipo,
                'quantidade': 1,
                'localizacao_destino': destino
            }
            movimentacoes.append(mov)
        
        df_movimentacoes = pd.DataFrame(movimentacoes)
        df_movimentacoes = df_movimentacoes.sort_values('timestamp')
        
        print(f"✓ Geradas {len(df_movimentacoes)} movimentações históricas")
        
        return df_movimentacoes
    
    def obter_nivel_estoque_atual(self):
        """Retorna nível de estoque atual por categoria"""
        estoque = self.equipamentos[
            self.equipamentos['localizacao'].str.contains('Almoxarifado')
        ].groupby('categoria').size().reset_index(name='quantidade')
        
        return estoque
    
    def obter_equipamentos_em_uso(self):
        """Retorna equipamentos atualmente em uso"""
        em_uso = self.equipamentos[
            self.equipamentos['localizacao'].str.contains('Em Uso')
        ]
        return em_uso
    
    def simular_tempo_real(self, duracao_segundos=60, intervalo_segundos=5):
        """Simula coleta de dados em tempo real via MQTT"""
        print(f"Iniciando simulação em tempo real por {duracao_segundos} segundos...")
        
        dados_tempo_real = []
        tempo_inicio = time.time()
        
        while (time.time() - tempo_inicio) < duracao_segundos:
            # Gera métricas para equipamentos em uso
            for _, equip in self.equipamentos[self.equipamentos['em_uso'] == True].sample(5).iterrows():
                metricas = self.gerar_metricas_uso(equip['id'])
                dados_tempo_real.append(metricas)
                
                # Simula publicação MQTT
                print(f"[MQTT] Publicado: {equip['id']} | Temp: {metricas['temperatura_c']}°C | CPU: {metricas['cpu_uso_percent']}%")
            
            time.sleep(intervalo_segundos)
        
        print(f"✓ Simulação concluída. {len(dados_tempo_real)} leituras coletadas.")
        return pd.DataFrame(dados_tempo_real)


if __name__ == "__main__":
    # Teste do simulador
    print("=== Teste do Simulador de Sensores IoT ===\n")
    
    # Inicializa simulador
    simulator = IoTSensorSimulator(num_equipamentos=30)
    
    # Exibe equipamentos
    print("Equipamentos cadastrados:")
    print(simulator.equipamentos[['id', 'categoria', 'estado', 'localizacao', 'idade_meses']].head(10))
    print(f"\nTotal: {len(simulator.equipamentos)} equipamentos\n")
    
    # Gera métricas de um equipamento
    print("Métricas de uso de um equipamento:")
    metricas = simulator.gerar_metricas_uso('EQ0001')
    print(json.dumps(metricas, indent=2))
    print()
    
    # Nível de estoque
    print("Nível de estoque atual:")
    print(simulator.obter_nivel_estoque_atual())
    print()
    
    # Gera dados históricos
    df_historico = simulator.gerar_dados_historicos(dias=30, intervalo_horas=12)
    print(f"\nAmostra de dados históricos:")
    print(df_historico.head())
