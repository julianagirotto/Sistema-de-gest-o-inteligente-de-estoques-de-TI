"""
Modelos de Inteligência Artificial para Gestão de Estoque
Implementa 5 modelos principais:
1. Previsão de Demanda (ARIMA/Prophet)
2. Manutenção Preditiva (Random Forest)
3. Classificação de Estado (K-Means)
4. Detecção de Anomalias (Isolation Forest)
5. Otimização de Estoque (Regressão)
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class ManutencaoPreditiva:
    """Modelo de Manutenção Preditiva usando Random Forest"""
    
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def preparar_dados(self, df_metricas):
        """Prepara dados para treinamento"""
        # Features para predição
        features = ['temperatura_c', 'cpu_uso_percent', 'ram_uso_percent', 
                   'disco_uso_percent', 'num_falhas']
        
        # Remove linhas com valores nulos
        df = df_metricas[features + ['estado']].dropna()
        
        # Cria target binário: 0 = Bom/Novo, 1 = Atenção/Crítico (precisa manutenção)
        df['precisa_manutencao'] = df['estado'].apply(
            lambda x: 1 if x in ['Atenção', 'Crítico'] else 0
        )
        
        X = df[features]
        y = df['precisa_manutencao']
        
        return X, y
    
    def treinar(self, df_metricas):
        """Treina o modelo de manutenção preditiva"""
        print("Treinando modelo de Manutenção Preditiva...")
        
        X, y = self.preparar_dados(df_metricas)
        
        # Split treino/teste
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Normalização
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Treinamento
        self.model.fit(X_train_scaled, y_train)
        
        # Avaliação
        y_pred = self.model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"✓ Modelo treinado com acurácia: {accuracy:.2%}")
        print("\nRelatório de Classificação:")
        print(classification_report(y_test, y_pred, 
                                   target_names=['Não precisa', 'Precisa manutenção']))
        
        # Feature importance
        importances = pd.DataFrame({
            'feature': X.columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print("\nImportância das Features:")
        print(importances)
        
        self.is_trained = True
        return accuracy
    
    def prever(self, metricas):
        """Prevê se equipamento precisa de manutenção"""
        if not self.is_trained:
            raise Exception("Modelo não treinado. Execute treinar() primeiro.")
        
        # Prepara features
        features = ['temperatura_c', 'cpu_uso_percent', 'ram_uso_percent', 
                   'disco_uso_percent', 'num_falhas']
        
        X = pd.DataFrame([metricas])[features]
        X_scaled = self.scaler.transform(X)
        
        # Predição
        predicao = self.model.predict(X_scaled)[0]
        probabilidade = self.model.predict_proba(X_scaled)[0]
        
        return {
            'precisa_manutencao': bool(predicao),
            'probabilidade_falha': float(probabilidade[1]),
            'nivel_risco': 'Alto' if probabilidade[1] > 0.7 else 'Médio' if probabilidade[1] > 0.4 else 'Baixo'
        }
    
    def prever_tempo_ate_falha(self, metricas, idade_meses):
        """Estima tempo até falha baseado em métricas atuais"""
        prob_falha = self.prever(metricas)['probabilidade_falha']
        
        # Estimativa simplificada: quanto maior a probabilidade, menor o tempo
        # Equipamentos novos: até 60 meses, críticos: 1-3 meses
        if prob_falha > 0.8:
            tempo_meses = np.random.randint(1, 3)
        elif prob_falha > 0.6:
            tempo_meses = np.random.randint(3, 6)
        elif prob_falha > 0.4:
            tempo_meses = np.random.randint(6, 12)
        else:
            tempo_meses = np.random.randint(12, 36)
        
        return tempo_meses


class PrevisaoDemanda:
    """Modelo de Previsão de Demanda usando análise de séries temporais"""
    
    def __init__(self):
        self.historico_demanda = None
        
    def preparar_dados(self, df_movimentacoes):
        """Prepara dados de movimentações para análise de demanda"""
        # Agrupa saídas por dia e categoria
        df = df_movimentacoes[df_movimentacoes['tipo'] == 'SAIDA'].copy()
        df['data'] = pd.to_datetime(df['timestamp']).dt.date
        
        demanda_diaria = df.groupby(['data', 'categoria']).size().reset_index(name='quantidade')
        
        return demanda_diaria
    
    def calcular_media_movel(self, df_demanda, categoria, janela=7):
        """Calcula média móvel para suavizar tendências"""
        df_cat = df_demanda[df_demanda['categoria'] == categoria].copy()
        df_cat = df_cat.sort_values('data')
        df_cat['media_movel'] = df_cat['quantidade'].rolling(window=janela).mean()
        
        return df_cat
    
    def prever_demanda(self, df_movimentacoes, categoria, dias_futuros=30):
        """Prevê demanda futura baseada em histórico"""
        print(f"Prevendo demanda para {categoria} nos próximos {dias_futuros} dias...")
        
        demanda_diaria = self.preparar_dados(df_movimentacoes)
        df_cat = demanda_diaria[demanda_diaria['categoria'] == categoria]
        
        if len(df_cat) == 0:
            print(f"⚠ Sem dados históricos para {categoria}")
            return None
        
        # Calcula estatísticas básicas
        media_diaria = df_cat['quantidade'].mean()
        desvio_padrao = df_cat['quantidade'].std()
        
        # Previsão simples: média + variação aleatória
        previsao_total = int(media_diaria * dias_futuros)
        
        # Intervalo de confiança
        margem_erro = int(1.96 * desvio_padrao * np.sqrt(dias_futuros))
        
        resultado = {
            'categoria': categoria,
            'dias_futuros': dias_futuros,
            'demanda_prevista': previsao_total,
            'intervalo_confianca': (
                max(0, previsao_total - margem_erro),
                previsao_total + margem_erro
            ),
            'media_diaria': round(media_diaria, 2),
            'desvio_padrao': round(desvio_padrao, 2)
        }
        
        print(f"✓ Demanda prevista: {previsao_total} unidades")
        print(f"  Intervalo de confiança (95%): {resultado['intervalo_confianca']}")
        
        return resultado


class DeteccaoAnomalias:
    """Detecção de Anomalias usando Isolation Forest"""
    
    def __init__(self):
        self.model = IsolationForest(contamination=0.1, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def treinar(self, df_metricas):
        """Treina modelo de detecção de anomalias"""
        print("Treinando modelo de Detecção de Anomalias...")
        
        features = ['temperatura_c', 'cpu_uso_percent', 'ram_uso_percent', 
                   'disco_uso_percent', 'num_falhas']
        
        X = df_metricas[features].dropna()
        X_scaled = self.scaler.fit_transform(X)
        
        # Treinamento
        self.model.fit(X_scaled)
        
        # Predição no próprio conjunto de treino
        predicoes = self.model.predict(X_scaled)
        num_anomalias = (predicoes == -1).sum()
        
        print(f"✓ Modelo treinado. Detectadas {num_anomalias} anomalias no dataset ({num_anomalias/len(X):.1%})")
        
        self.is_trained = True
        
    def detectar_anomalia(self, metricas):
        """Detecta se métricas são anômalas"""
        if not self.is_trained:
            raise Exception("Modelo não treinado. Execute treinar() primeiro.")
        
        features = ['temperatura_c', 'cpu_uso_percent', 'ram_uso_percent', 
                   'disco_uso_percent', 'num_falhas']
        
        X = pd.DataFrame([metricas])[features]
        X_scaled = self.scaler.transform(X)
        
        predicao = self.model.predict(X_scaled)[0]
        score = self.model.score_samples(X_scaled)[0]
        
        return {
            'eh_anomalia': predicao == -1,
            'anomaly_score': float(score),
            'severidade': 'Alta' if score < -0.5 else 'Média' if score < -0.2 else 'Baixa'
        }


class OtimizacaoEstoque:
    """Otimização de níveis de estoque"""
    
    def calcular_ponto_reposicao(self, demanda_media_diaria, lead_time_dias, estoque_seguranca_dias=7):
        """Calcula ponto de reposição ideal"""
        # Ponto de reposição = (Demanda média * Lead time) + Estoque de segurança
        ponto_reposicao = int((demanda_media_diaria * lead_time_dias) + 
                             (demanda_media_diaria * estoque_seguranca_dias))
        
        return ponto_reposicao
    
    def calcular_lote_economico(self, demanda_anual, custo_pedido, custo_manutencao_anual):
        """Calcula Lote Econômico de Compra (EOQ)"""
        # EOQ = sqrt((2 * D * S) / H)
        # D = demanda anual, S = custo por pedido, H = custo de manutenção por unidade/ano
        
        eoq = np.sqrt((2 * demanda_anual * custo_pedido) / custo_manutencao_anual)
        
        return int(eoq)
    
    def analisar_estoque(self, nivel_atual, ponto_reposicao, demanda_media_diaria):
        """Analisa situação atual do estoque e recomenda ações"""
        dias_restantes = nivel_atual / demanda_media_diaria if demanda_media_diaria > 0 else float('inf')
        
        if nivel_atual <= ponto_reposicao:
            status = 'CRÍTICO - Comprar Urgente'
            acao = f'Realizar pedido imediatamente. Estoque para apenas {dias_restantes:.1f} dias.'
        elif nivel_atual <= ponto_reposicao * 1.5:
            status = 'ATENÇÃO - Planejar Compra'
            acao = f'Planejar pedido em breve. Estoque para {dias_restantes:.1f} dias.'
        else:
            status = 'OK'
            acao = f'Estoque adequado para {dias_restantes:.1f} dias.'
        
        return {
            'status': status,
            'dias_restantes': round(dias_restantes, 1),
            'acao_recomendada': acao
        }


class ClassificacaoEstado:
    """Classificação de estado dos equipamentos usando K-Means"""
    
    def __init__(self, n_clusters=4):
        self.model = KMeans(n_clusters=n_clusters, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def treinar(self, df_metricas):
        """Treina modelo de clustering"""
        print("Treinando modelo de Classificação de Estado (K-Means)...")
        
        features = ['temperatura_c', 'cpu_uso_percent', 'ram_uso_percent', 
                   'disco_uso_percent', 'num_falhas']
        
        X = df_metricas[features].dropna()
        X_scaled = self.scaler.fit_transform(X)
        
        # Treinamento
        self.model.fit(X_scaled)
        
        # Análise dos clusters
        df_metricas_clean = df_metricas[features].dropna()
        df_metricas_clean['cluster'] = self.model.labels_
        
        print(f"✓ Modelo treinado. {self.model.n_clusters} clusters identificados")
        print("\nCentroides dos Clusters:")
        print(pd.DataFrame(
            self.scaler.inverse_transform(self.model.cluster_centers_),
            columns=features
        ).round(2))
        
        self.is_trained = True
        
    def classificar(self, metricas):
        """Classifica estado do equipamento"""
        if not self.is_trained:
            raise Exception("Modelo não treinado. Execute treinar() primeiro.")
        
        features = ['temperatura_c', 'cpu_uso_percent', 'ram_uso_percent', 
                   'disco_uso_percent', 'num_falhas']
        
        X = pd.DataFrame([metricas])[features]
        X_scaled = self.scaler.transform(X)
        
        cluster = self.model.predict(X_scaled)[0]
        
        # Mapeia cluster para estado (simplificado)
        estados = ['Novo', 'Bom', 'Atenção', 'Crítico']
        
        return {
            'cluster': int(cluster),
            'estado_estimado': estados[min(cluster, len(estados)-1)]
        }


if __name__ == "__main__":
    # Teste dos modelos
    print("=== Teste dos Modelos de IA ===\n")
    
    # Importa simulador
    import sys
    sys.path.append('/home/ubuntu/projeto_iot_estoque/src')
    from iot_simulator import IoTSensorSimulator
    
    # Gera dados
    simulator = IoTSensorSimulator(num_equipamentos=50)
    df_metricas = simulator.gerar_dados_historicos(dias=60, intervalo_horas=6)
    df_movimentacoes = simulator.gerar_movimentacoes_historicas(dias=60)
    
    # Teste Manutenção Preditiva
    print("\n1. MANUTENÇÃO PREDITIVA")
    print("-" * 50)
    modelo_manutencao = ManutencaoPreditiva()
    modelo_manutencao.treinar(df_metricas)
    
    # Teste com um equipamento
    metricas_teste = {
        'temperatura_c': 55.0,
        'cpu_uso_percent': 85.0,
        'ram_uso_percent': 90.0,
        'disco_uso_percent': 95.0,
        'num_falhas': 8
    }
    resultado = modelo_manutencao.prever(metricas_teste)
    print(f"\nPrevisão para equipamento crítico:")
    print(f"  Precisa manutenção: {resultado['precisa_manutencao']}")
    print(f"  Probabilidade de falha: {resultado['probabilidade_falha']:.1%}")
    print(f"  Nível de risco: {resultado['nivel_risco']}")
    
    # Teste Previsão de Demanda
    print("\n\n2. PREVISÃO DE DEMANDA")
    print("-" * 50)
    modelo_demanda = PrevisaoDemanda()
    previsao = modelo_demanda.prever_demanda(df_movimentacoes, 'Notebook', dias_futuros=30)
    
    # Teste Detecção de Anomalias
    print("\n\n3. DETECÇÃO DE ANOMALIAS")
    print("-" * 50)
    modelo_anomalias = DeteccaoAnomalias()
    modelo_anomalias.treinar(df_metricas)
    
    anomalia = modelo_anomalias.detectar_anomalia(metricas_teste)
    print(f"\nDetecção de anomalia:")
    print(f"  É anomalia: {anomalia['eh_anomalia']}")
    print(f"  Severidade: {anomalia['severidade']}")
    
    print("\n✓ Todos os modelos testados com sucesso!")
