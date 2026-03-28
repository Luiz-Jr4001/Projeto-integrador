import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(layout="wide", page_title="Gestão Industrial 4.0", page_icon="🏭")

# 2. GERAÇÃO DE DADOS (BASE EXPANDIDA PARA 30 DIAS)
@st.cache_data # Cache para não regerar dados aleatórios a cada clique
def get_data():
    np.random.seed(42)
    dias = [f"{i:02d}/03" for i in range(1, 32)]
    
    data = {
        'Dia': dias,
        'Meta': [1500] * 31,
        'Producao_Realizada': np.random.normal(1380, 120, 31).astype(int),
        'Retrabalho': np.random.poisson(90, 31),
        'Refugo': np.random.poisson(45, 31),
        'Minutos_Parados': np.random.exponential(35, 31).astype(int),
        'Temperatura_C': np.random.uniform(68, 92, 31).round(1),
        'Turno_Principal': np.random.choice(['Manhã', 'Tarde', 'Noite'], 31)
    }
    
    df = pd.DataFrame(data)
    
    # Cálculos de KPIs
    df['Producao_Liquida'] = df['Producao_Realizada'] - (df['Retrabalho'] + df['Refugo'])
    df['Pct_Atingimento_Meta'] = (df['Producao_Realizada'] / df['Meta']) * 100
    df['Pct_Retrabalho'] = (df['Retrabalho'] / df['Producao_Realizada']) * 100
    df['Pct_Refugo'] = (df['Refugo'] / df['Producao_Realizada']) * 100
    df['Eficiencia_Produtiva'] = (df['Producao_Liquida'] / df['Meta']) * 100
    
    # Criar coluna de data real para o filtro de calendário
    df['Data_Filtro'] = pd.to_datetime(df['Dia'] + "/2026", format="%d/%m/%Y").dt.date
    
    return df

df = get_data()

# 3. BARRA LATERAL (FILTROS)
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1063/1063231.png", width=100)
st.sidebar.title("Configurações")

st.sidebar.subheader("📅 Período de Análise")
data_min = df['Data_Filtro'].min()
data_max = df['Data_Filtro'].max()

# Seletor de Calendário (Intervalo)
selecao_data = st.sidebar.date_input(
    "Selecione o intervalo:",
    value=(data_min, data_max),
    min_value=data_min,
    max_value=data_max
)

if st.sidebar.button("Resetar para Mês Inteiro"):
    st.rerun()


# --- LÓGICA DE FILTRAGEM  ---
if isinstance(selecao_data, tuple) and len(selecao_data) == 2:
    start_date, end_date = selecao_data
    df_filtrado = df[(df['Data_Filtro'] >= start_date) & (df['Data_Filtro'] <= end_date)]
else:
    df_filtrado = df[df['Data_Filtro'] == selecao_data]

# --- VERIFICAÇÃO DE DADOS (ADICIONE AQUI) ---
if not df_filtrado.empty:
    
    # 1. Coloque aqui os seus Cartões de KPIs (col1, col2...)
    # 2. Coloque aqui o Gráfico de Evolução (col_a)
    # 3. Coloque aqui o Gráfico de Pizza (col_b)
    # 4. Coloque aqui a Análise Preditiva (col_c, col_d)
    
    # Exemplo rápido do conteúdo interno:
    col1, col2, col3, col4 = st.columns(4)
    # ... resto do código dos KPIs e Gráficos ...

else:
    # Caso o filtro não encontre nenhum dado
    st.warning("⚠️ Nenhum dado encontrado para o período selecionado no calendário.")
    st.info("Dica: Verifique se o intervalo selecionado possui registros de produção na base de dados.")

# --- A TABELA PODE FICAR FORA OU DENTRO (Geralmente fora para depuração) ---
st.markdown("---")
with st.expander("📄 Visualizar Tabela de Dados"):
    st.dataframe(df_filtrado, width='stretch')

# 4. CORPO DO DASHBOARD
st.title("🏭 Dashboard de Performance Industrial")
st.markdown(f"Exibindo dados de **{selecao_data[0] if isinstance(selecao_data, tuple) else selecao_data}** até **{selecao_data[1] if isinstance(selecao_data, tuple) and len(selecao_data)==2 else '---'}**")

# KPIs Consolidados
col1, col2, col3, col4 = st.columns(4)

total_realizado = df_filtrado['Producao_Realizada'].sum()
total_meta = df_filtrado['Meta'].sum()
avg_eficiencia = df_filtrado['Eficiencia_Produtiva'].mean()
total_refugo = df_filtrado['Refugo'].sum()
avg_retrabalho = (df_filtrado['Retrabalho'].sum() / total_realizado) * 100 if total_realizado > 0 else 0

with col1:
    st.metric("Produção Total", f"{float(total_realizado):,.0f}".replace(",", "."), f"{total_realizado - total_meta:,.0f} vs Meta")
with col2:
    st.metric("Eficiência Líquida Média", f"{avg_eficiencia:.1f}%", delta=f"{avg_eficiencia - 85:.1f}%", delta_color="normal" if avg_eficiencia >= 85 else "inverse")
with col3:
    st.metric("Taxa de Retrabalho", f"{avg_retrabalho:.1f}%", f"{df_filtrado['Retrabalho'].sum()} peças", delta_color="inverse")
with col4:
    st.metric("Total de Refugo", f"{total_refugo}", "Peças descartadas", delta_color="inverse")

st.markdown("---")

# 5. GRÁFICOS PRINCIPAIS
col_a, col_b = st.columns([2, 1])

with col_a:
    st.subheader("📈 Evolução Diária: Realizado vs Meta")
    fig, ax = plt.subplots(figsize=(10, 4.5))
    sns.lineplot(data=df_filtrado, x='Dia', y='Meta', label='Meta', color='red', linestyle='--')
    sns.barplot(data=df_filtrado, x='Dia', y='Producao_Realizada', color='skyblue', label='Realizado', alpha=0.7)
    plt.xticks(rotation=45)
    plt.legend()
    st.pyplot(fig)
    

with col_b:
    st.subheader("🎯 Qualidade Geral")
    
    # Calculando os valores para o gráfico
    valores = [df_filtrado['Producao_Liquida'].sum(), df_filtrado['Retrabalho'].sum(), df_filtrado['Refugo'].sum()]
    labels = ['Líquida', 'Retrabalho', 'Refugo']
    
    # SÓ DESENHA SE A SOMA FOR MAIOR QUE ZERO
    if sum(valores) > 0:
        fig2, ax2 = plt.subplots()
        ax2.pie(valores, labels=labels, autopct='%1.1f%%', startangle=90, 
                colors=['#2ecc71', '#f1c40f', '#e74c3c'], pctdistance=0.85)
        
        centre_circle = plt.Circle((0,0),0.70,fc='white')
        fig2.gca().add_artist(centre_circle)
        st.pyplot(fig2)
    else:
        st.warning("Sem dados de produção para o período selecionado.")

# 6. ANÁLISE PREDITIVA (TEMPERATURA)
st.markdown("---")
st.subheader("⚠️ Análise Preditiva e Diagnóstico de Falhas")

col_c, col_d = st.columns([1.5, 1])

with col_c:
    st.write("**Correlação: Temperatura vs. Perda por Refugo**")
    fig3, ax3 = plt.subplots(figsize=(8, 4))
    sns.scatterplot(data=df_filtrado, x='Temperatura_C', y='Pct_Refugo', hue='Turno_Principal', s=100)
    ax3.axvline(x=85, color='red', linestyle='--', label='Limite de Calor')
    plt.legend()
    st.pyplot(fig3)

with col_d:
    temp_media = df_filtrado['Temperatura_C'].mean()
    st.write(f"**Status Térmico Médio:** {temp_media:.1f}°C")
    
    if temp_media > 85:
        st.error("🚨 ALERTA CRÍTICO: Superaquecimento detectado no período selecionado. Risco alto de quebra de componentes.")
    elif temp_media > 78:
        st.warning("⚠️ AVISO: Temperatura acima do ideal. Verificar sistema de lubrificação/resfriamento.")
    else:
        st.success("✅ OPERAÇÃO ESTÁVEL: Temperatura dentro dos parâmetros de segurança.")
    
    st.info("💡 **Insight:** Historicamente, o Turno da Noite apresenta menor refugo devido à temperatura ambiente reduzida, facilitando a troca térmica das máquinas.")

# 7. TABELA DE DADOS
st.markdown("---")
with st.expander("📄 Visualizar Tabela de Dados Completa"):
    st.dataframe(df_filtrado.drop(columns=['Data_Filtro']), width='stretch')
