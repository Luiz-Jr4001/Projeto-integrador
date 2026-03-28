import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Configuração da página (deve ser a primeira linha após os imports)
st.set_page_config(layout="wide", page_title="Dashboard de Produção Industrial")

# --- SIMULAÇÃO DE DADOS ---
# Em um cenário real, você carregaria de um CSV, Excel ou Banco de Dados
# pd.read_csv('dados_producao.csv')

def get_data():
    data = {
        'Dia': [f'0{i}/10' if i < 10 else f'{i}/10' for i in range(1, 11)],
        'Meta': [1500] * 10,
        'Producao_Realizada': [1200, 1450, 1550, 1100, 1300, 1600, 900, 1480, 1520, 1180],
        'Retrabalho': [150, 80, 50, 200, 100, 40, 250, 90, 60, 160],
        'Refugo': [80, 20, 10, 120, 60, 15, 180, 40, 30, 90]
    }
    df = pd.DataFrame(data)
    
    # --- CÁLCULO DOS KPIs (FÓRMULAS FORNECIDAS) ---
    df['Producao_Liquida'] = df['Producao_Realizada'] - (df['Retrabalho'] + df['Refugo'])
    df['Pct_Atingimento_Meta'] = (df['Producao_Realizada'] / df['Meta']) * 100
    df['Pct_Retrabalho'] = (df['Retrabalho'] / df['Producao_Realizada']) * 100
    df['Pct_Refugo'] = (df['Refugo'] / df['Producao_Realizada']) * 100
    df['Eficiencia_Produtiva'] = (df['Producao_Liquida'] / df['Meta']) * 100
    df['Gap_Producao'] = df['Meta'] - df['Producao_Realizada']
    
    return df

# Carregar dados
df = get_data()

# --- ESTRUTURA DO DASHBOARD (STREAMLIT) ---

st.title("🏭 Painel de Monitoramento de Produção")
st.markdown("---")

# Filtro de Dia na Barra Lateral
st.sidebar.header("Filtros")
dias_selecionados = st.sidebar.multiselect(
    "Selecione os dias para análise:",
    options=df['Dia'].unique(),
    default=df['Dia'].unique()
)

# Filtrar o DataFrame com base na seleção
df_filtrado = df[df['Dia'].isin(dias_selecionados)]

# Se nenhum dia for selecionado, mostrar aviso
if df_filtrado.empty:
    st.warning("Por favor, selecione pelo menos um dia na barra lateral.")
    st.stop()

# --- 1. CARTÕES DE KPIs (Totais Consolidados) ---
st.subheader("📊 Indicadores de Desempenho")

# Cálculos Consolidados
total_meta = df_filtrado['Meta'].sum()
total_realizado = df_filtrado['Producao_Realizada'].sum()
total_liquido = df_filtrado['Producao_Liquida'].sum()
total_retrabalho = df_filtrado['Retrabalho'].sum()
total_refugo = df_filtrado['Refugo'].sum()

avg_atingimento = (total_realizado / total_meta) * 100 if total_meta > 0 else 0
avg_retrabalho = (total_retrabalho / total_realizado) * 100 if total_realizado > 0 else 0
avg_refugo = (total_refugo / total_realizado) * 100 if total_realizado > 0 else 0
avg_eficiencia = (total_liquido / total_meta) * 100 if total_meta > 0 else 0

# Layout em Colunas para Cartões
col1, col2, col3, col4, col5 = st.columns(5)

# Função para definir a cor com base no desempenho
def get_color(value, target, is_loss=False):
    if is_loss: # Para Retrabalho/Refugo (quanto menor, melhor)
        return "normal" if value <= target else "inverse"
    else: # Para Eficiência (quanto maior, melhor)
        return "normal" if value >= target else "inverse"

with col1:
    st.metric(
        label="Produção Realizada", 
        value=f"{total_realizado:,.0f}", 
        delta=f"{avg_atingimento:.1f}% da Meta",
        help="Soma total de peças produzidas."  
    )

with col2:
    # Definindo uma meta de exemplo para eficiência (ex: 85%)
    cor_eficiencia = "off" if avg_eficiencia < 80 else "normal"
    st.metric(
        label="Eficiência Produtiva", 
        value=f"{avg_eficiencia:.1f}%",
        help="Produção Líquida / Meta total. Mostra a capacidade real aproveitada."
    )

with col3:
    # Meta de exemplo para retrabalho (ex: max 5%)
    st.metric(
        label="Taxa de Retrabalho", 
        value=f"{avg_retrabalho:.1f}%", 
        delta=f"{total_retrabalho:,.0f} peças",
        delta_color="off" if avg_retrabalho < 10 else "inverse",
        help="Proporção de peças que precisaram ser refeitas."
    )

with col4:
    st.metric(
        label="Taxa de Refugo", 
        value=f"{avg_refugo:.1f}%", 
        delta=f"{total_refugo:,.0f} peças",
        delta_color="off" if avg_refugo < 5 else "inverse",
        help="Proporção de peças perdidas."
    )

with col5:
    total_gap = total_meta - total_realizado
    status_gap = "🔴 Abaixo" if total_gap > 0 else "🟢 Batida"
    st.metric(
        label="Status da Meta", 
        value=status_gap, 
        delta=f"{total_gap:,.0f} peças (Gap)" if total_gap > 0 else f"{abs(total_gap):,.0f} peças (Excesso)",
        delta_color="inverse" if total_gap > 0 else "normal"
    )

st.markdown("---")

# --- 2. GRÁFICOS DE ANÁLISE ---
st.subheader("📈 Análise de Tendência e Comparação Diária")

col_left, col_right = st.columns([2, 1])

with col_left:
    st.write("**Evolução Diária: Produção Realizada vs Meta**")
    # Usando Matplotlib para um gráfico mais customizado
    fig, ax = plt.subplots(figsize=(10, 4))
    sns.set_style("whitegrid")
    
    # Linha da Meta
    ax.plot(df_filtrado['Dia'], df_filtrado['Meta'], label='Meta', color='#E74C3C', linestyle='--', linewidth=2)
    
    # Barras da Produção Realizada (com cor condicional básica)
    colors = ['#2ECC71' if r >= m else '#F39C12' for r, m in zip(df_filtrado['Producao_Realizada'], df_filtrado['Meta'])]
    ax.bar(df_filtrado['Dia'], df_filtrado['Producao_Realizada'], label='Realizado', color=colors, alpha=0.8)
    
    # Ajustes do Gráfico
    ax.set_ylabel("Quantidade de Peças")
    ax.set_title("Atingimento da Meta por Dia")
    ax.legend()
    plt.xticks(rotation=45)
    
    st.pyplot(fig)

with col_right:
    st.write("**Composição da Produção (Total)**")
    # Gráfico de Rosca para Perdas
    perdas_data = [total_liquido, total_retrabalho, total_refugo]
    perdas_labels = ['Líquida', 'Retrabalho', 'Refugo']
    perdas_colors = ['#2ECC71', '#F39C12', '#E74C3C']
    
    fig2, ax2 = plt.subplots(figsize=(5, 5))
    ax2.pie(perdas_data, labels=perdas_labels, colors=perdas_colors, autopct='%1.1f%%', startangle=90, pctdistance=0.85, textprops={'fontsize': 10})
    
    # Desenhar círculo branco no centro (efeito rosca)
    centre_circle = plt.Circle((0,0),0.70,fc='white')
    fig2.gca().add_artist(centre_circle)
    
    ax2.axis('equal')  
    ax2.set_title("Qualidade da Produção")
    
    st.pyplot(fig2)

st.markdown("---")

# --- 3. TABELA DETALHADA ---
st.subheader("📄 Detalhamento dos Dados")
with st.expander("Clique para visualizar os dados absolutos e percentuais diários"):
    # Formatação da Tabela
    st.dataframe(
        df_filtrado.style.format({
            'Meta': '{:,.0f}',
            'Producao_Realizada': '{:,.0f}',
            'Retrabalho': '{:,.0f}',
            'Refugo': '{:,.0f}',
            'Producao_Liquida': '{:,.0f}',
            'Gap_Producao': '{:,.0f}',
            'Pct_Atingimento_Meta': '{:.1f}%',
            'Pct_Retrabalho': '{:.1f}%',
            'Pct_Refugo': '{:.1f}%',
            'Eficiencia_Produtiva': '{:.1f}%'
        }).bar(subset=['Eficiencia_Produtiva'], color='#2ECC71', vmin=0, vmax=100)
    )

# --- 4. SEÇÃO DE INSIGHTS AUTOMÁTICOS ---
st.sidebar.markdown("---")
st.sidebar.subheader("💡 Insights Rápidos")

if avg_eficiencia < 70:
    st.sidebar.error(f"⚠️ Atenção! A eficiência líquida média ({avg_eficiencia:.1f}%) está baixa. Alto volume de perdas.")

if avg_retrabalho > 10:
    st.sidebar.warning(f"🟧 Alerta de Retrabalho: {avg_retrabalho:.1f}% das peças precisam ser refeitas. Verificar processo.")

if total_gap > 0:
    st.sidebar.info(f"📉 Gap Total: Faltam {total_gap:,.0f} peças para bater a meta acumulada.")
else:
    st.sidebar.success(f"✅ Parabéns! A meta acumulada foi superada em {abs(total_gap):,.0} peças.")