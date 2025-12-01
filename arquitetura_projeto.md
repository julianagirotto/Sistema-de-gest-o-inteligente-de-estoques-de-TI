# Arquitetura do Projeto: Sistema de Estoque Inteligente com Manutenção Preditiva

## 1. Visão Geral do Projeto

**Nome**: SmartStock IoT - Sistema Inteligente de Gestão de Estoque com Manutenção Preditiva

**Objetivo**: Desenvolver uma solução completa de IoT + IA para gestão de estoque de equipamentos de TI, com capacidade de monitoramento em tempo real, previsão de demanda, manutenção preditiva e otimização de custos.

---

## 2. Arquitetura em 5 Camadas (Baseada no Conteúdo da Disciplina)

### **Camada 1: Percepção (Sensores e Dispositivos IoT)**

**Componentes**:
- Sensores RFID para rastreamento de itens
- Sensores de temperatura e umidade (condições de armazenamento)
- Sensores de uso (simulando métricas de equipamentos em operação)
- Leitores de código de barras/QR Code

**Dados Coletados**:
- ID do equipamento (RFID)
- Localização no estoque
- Temperatura do ambiente
- Métricas de uso (CPU, RAM, Disco, Bateria) - para equipamentos em operação
- Timestamp de movimentações
- Estado operacional

**Implementação**:
- Simulação em Python de sensores IoT gerando dados realistas
- Protocolo MQTT para transmissão de dados

---

### **Camada 2: Rede (Comunicação)**

**Protocolos Utilizados**:
- **MQTT**: Comunicação leve entre sensores e gateway (principal)
- **HTTP/REST**: APIs para integração com sistemas externos
- **WebSocket**: Atualizações em tempo real no dashboard

**Topologia**:
- Gateway IoT central recebe dados de múltiplos sensores
- Edge computing para pré-processamento local
- Transmissão para servidor central via internet

**Implementação**:
- Broker MQTT (Mosquitto simulado ou Paho MQTT em Python)
- APIs REST com Flask/FastAPI

---

### **Camada 3: Middleware (Processamento e Armazenamento)**

**Processamento**:
- **Edge Computing**: Filtragem e agregação inicial de dados
- **Stream Processing**: Processamento de dados em tempo real
- **Batch Processing**: Análises históricas e treinamento de modelos

**Armazenamento**:
- **MongoDB**: Dados de inventário (não estruturados, flexíveis)
- **InfluxDB**: Séries temporais (métricas de uso ao longo do tempo)
- **PostgreSQL**: Dados transacionais (pedidos, movimentações, fornecedores)

**Implementação**:
- Pandas para manipulação de dados
- Simulação de bancos de dados com arquivos JSON/CSV
- Pipeline de ETL (Extract, Transform, Load)

---

### **Camada 4: Aplicação (Inteligência Artificial)**

**Modelos de IA Implementados**:

1. **Previsão de Demanda**:
   - Modelo: ARIMA, Prophet ou LSTM
   - Input: Histórico de movimentações
   - Output: Previsão de necessidade para próximos 30/60/90 dias

2. **Manutenção Preditiva**:
   - Modelo: Random Forest, XGBoost ou Redes Neurais
   - Input: Métricas de uso (temperatura, CPU, RAM, disco, idade)
   - Output: Probabilidade de falha, tempo estimado até falha

3. **Classificação de Estado**:
   - Modelo: K-Means (clustering) ou Classificação Supervisionada
   - Input: Métricas de performance
   - Output: Estado (Novo, Bom, Atenção, Crítico, Descarte)

4. **Detecção de Anomalias**:
   - Modelo: Isolation Forest ou Autoencoder
   - Input: Padrões de uso e movimentação
   - Output: Alertas de comportamento anômalo

5. **Otimização de Estoque**:
   - Modelo: Regressão Linear ou Algoritmos de Otimização
   - Input: Histórico de uso, lead time de fornecedores, custos
   - Output: Ponto de reposição ideal, quantidade de pedido

**Bibliotecas Python**:
- Scikit-learn: Modelos de ML
- TensorFlow/Keras: Deep Learning (LSTM)
- Prophet: Previsão de séries temporais
- Pandas, NumPy: Manipulação de dados
- Statsmodels: Análise estatística

---

### **Camada 5: Negócio (Interface e Visualização)**

**Dashboard Interativo**:
- Visão geral do estoque em tempo real
- Alertas de ruptura iminente
- Previsões de demanda
- Equipamentos com risco de falha
- Recomendações de ação (comprar, substituir, reparar)
- Análise de custos (TCO - Total Cost of Ownership)
- Relatórios gerenciais

**Funcionalidades**:
- Filtros por categoria, localização, estado
- Gráficos interativos (Plotly)
- Tabelas dinâmicas
- Exportação de relatórios (PDF, Excel)
- Sistema de alertas (e-mail simulado)

**Implementação**:
- Plotly Dash ou Streamlit para dashboard web
- Matplotlib/Seaborn para visualizações estáticas
- Jupyter Notebook para análises exploratórias

---

## 3. Fluxo de Dados (Data Pipeline)

```
[Sensores IoT] 
    ↓ (MQTT)
[Gateway/Edge Computing] 
    ↓ (Pré-processamento)
[Armazenamento] (MongoDB, InfluxDB, PostgreSQL)
    ↓
[Processamento Batch/Stream]
    ↓
[Modelos de IA] (Treinamento e Inferência)
    ↓
[Dashboard/Alertas] (Visualização e Ações)
```

---

## 4. Casos de Uso Principais

### **Caso de Uso 1: Alerta de Ruptura de Estoque**
1. Sensores detectam saída de equipamentos
2. Sistema atualiza nível de estoque em tempo real
3. IA prevê demanda futura
4. Se estoque atual < ponto de reposição: gera alerta
5. Dashboard exibe alerta e sugere quantidade de compra

### **Caso de Uso 2: Manutenção Preditiva**
1. Equipamentos em uso enviam métricas continuamente
2. IA analisa padrões de degradação
3. Modelo prevê probabilidade de falha
4. Se risco > threshold: gera alerta de manutenção preventiva
5. Sistema sugere substituição ou reparo

### **Caso de Uso 3: Otimização de Layout**
1. Sensores rastreiam movimentações de itens
2. IA analisa frequência de acesso
3. Sistema recomenda reorganização do almoxarifado
4. Itens mais usados ficam mais acessíveis

### **Caso de Uso 4: Análise de Fornecedores**
1. Sistema registra equipamentos por fornecedor
2. IA analisa taxa de falha por fornecedor
3. Calcula vida útil média por marca/modelo
4. Gera ranking de fornecedores
5. Recomenda fornecedores com melhor custo-benefício

---

## 5. Requisitos Técnicos

### **Hardware (Simulado)**
- Sensores RFID (simulados em Python)
- Gateway IoT (Raspberry Pi simulado)
- Servidor central (ambiente local)

### **Software**
- Python 3.11+
- Jupyter Notebook/Lab
- Bibliotecas: pandas, numpy, scikit-learn, plotly, dash, paho-mqtt, flask
- Banco de dados: MongoDB (ou simulação com JSON), InfluxDB (ou CSV)

### **Ambiente de Desenvolvimento**
- Anaconda/Miniconda
- VS Code ou Jupyter Lab
- Git para controle de versão
- GitHub para repositório

---

## 6. Segurança e Privacidade (Módulo 3 da Disciplina)

**Medidas Implementadas**:
- Criptografia de dados em trânsito (TLS/SSL simulado)
- Autenticação de dispositivos IoT (tokens)
- Controle de acesso baseado em roles
- Logs de auditoria de movimentações
- Conformidade com LGPD (dados anonimizados quando necessário)

---

## 7. Escalabilidade e Elasticidade (Módulo 3 da Disciplina)

**Estratégias**:
- Arquitetura modular (microserviços simulados)
- Processamento distribuído (conceito de Hadoop/Spark)
- Cache de dados frequentes
- Balanceamento de carga (conceitual)
- Computação em nuvem (AWS/Azure/GCP - conceitual)

---

## 8. Métricas de Sucesso

**KPIs do Sistema**:
- Acurácia da previsão de demanda (> 85%)
- Precisão da manutenção preditiva (> 80%)
- Redução de ruptura de estoque (> 50%)
- Redução de custos de manutenção emergencial (> 40%)
- Tempo de resposta do sistema (< 2 segundos)
- Disponibilidade do sistema (> 99%)

---

## 9. Roadmap de Desenvolvimento

**Fase 1**: Simulação de Sensores IoT e Coleta de Dados
**Fase 2**: Armazenamento e Pipeline de Dados
**Fase 3**: Desenvolvimento de Modelos de IA
**Fase 4**: Dashboard e Visualização
**Fase 5**: Integração e Testes
**Fase 6**: Documentação e Apresentação

---

## 10. Tecnologias por Módulo da Disciplina

| Módulo | Conceito | Tecnologia Utilizada |
|--------|----------|---------------------|
| 1 | Protocolos IoT | MQTT, HTTP/REST |
| 1 | Edge Computing | Pré-processamento local |
| 2 | Big Data | Pandas, simulação de Hadoop/Spark |
| 2 | NoSQL | MongoDB (simulado) |
| 2 | Séries Temporais | InfluxDB (simulado) |
| 2 | IA/ML | Scikit-learn, Prophet, TensorFlow |
| 3 | Arquitetura 5 Camadas | Implementação completa |
| 3 | Segurança | Criptografia, autenticação |
| 3 | Elasticidade | Arquitetura escalável |
| 4 | Manutenção Preditiva | Random Forest, XGBoost |
| 4 | Indústria 4.0 | Aplicação prática |

---

## 11. Diferenciais do Projeto

✅ Arquitetura completa em 5 camadas
✅ Múltiplos modelos de IA integrados
✅ Simulação realista de ambiente IoT
✅ Dashboard interativo e profissional
✅ Aplicação prática em Engenharia de Produção
✅ Alinhamento total com conteúdo da disciplina
✅ Código bem documentado e modular
✅ Potencial de aplicação real em empresas
