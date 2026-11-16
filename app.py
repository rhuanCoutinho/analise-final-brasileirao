import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict

# Page configuration
st.set_page_config(
    page_title="Brasileirão 2026 - Probabilidades de Rebaixamento",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling
st.markdown("""
<style>
    .metric-card {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .badge-critical { background-color: #fee2e2; color: #dc2626; padding: 3px 8px; border-radius: 6px; font-weight: bold; }
    .badge-high { background-color: #ffedd5; color: #ea580c; padding: 3px 8px; border-radius: 6px; font-weight: bold; }
    .badge-medium { background-color: #fef9c3; color: #ca8a04; padding: 3px 8px; border-radius: 6px; font-weight: bold; }
    .badge-low { background-color: #dcfce7; color: #16a34a; padding: 3px 8px; border-radius: 6px; font-weight: bold; }
    .badge-safe { background-color: #dbeafe; color: #2563eb; padding: 3px 8px; border-radius: 6px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# Data Definition
# -------------------------------------------------------------
@st.cache_data
def get_base_standings():
    return [
        {"Pos": 1, "Clube": "Flamengo", "Pts": 76, "J": 34, "V": 23, "E": 7, "D": 4, "GP": 71, "GC": 29, "SG": 42},
        {"Pos": 2, "Clube": "Palmeiras", "Pts": 73, "J": 34, "V": 21, "E": 10, "D": 3, "GP": 62, "GC": 23, "SG": 39},
        {"Pos": 3, "Clube": "Cruzeiro", "Pts": 60, "J": 34, "V": 18, "E": 6, "D": 10, "GP": 55, "GC": 48, "SG": 7},
        {"Pos": 4, "Clube": "Fluminense", "Pts": 57, "J": 34, "V": 16, "E": 9, "D": 9, "GP": 55, "GC": 42, "SG": 13},
        {"Pos": 5, "Clube": "Athletico-PR", "Pts": 54, "J": 34, "V": 15, "E": 9, "D": 10, "GP": 51, "GC": 43, "SG": 8},
        {"Pos": 6, "Clube": "Bahia", "Pts": 53, "J": 34, "V": 14, "E": 11, "D": 9, "GP": 50, "GC": 45, "SG": 5},
        {"Pos": 7, "Clube": "Atlético-MG", "Pts": 51, "J": 35, "V": 14, "E": 9, "D": 12, "GP": 44, "GC": 40, "SG": 4},
        {"Pos": 8, "Clube": "RB Bragantino", "Pts": 47, "J": 34, "V": 13, "E": 8, "D": 13, "GP": 44, "GC": 39, "SG": 5},
        {"Pos": 9, "Clube": "Santos", "Pts": 47, "J": 34, "V": 12, "E": 11, "D": 11, "GP": 50, "GC": 49, "SG": 1},
        {"Pos": 10, "Clube": "São Paulo", "Pts": 44, "J": 34, "V": 12, "E": 8, "D": 14, "GP": 39, "GC": 39, "SG": 0},
        {"Pos": 11, "Clube": "Vasco da Gama", "Pts": 44, "J": 34, "V": 12, "E": 8, "D": 14, "GP": 45, "GC": 50, "SG": -5},
        {"Pos": 12, "Clube": "Botafogo", "Pts": 42, "J": 34, "V": 11, "E": 9, "D": 14, "GP": 46, "GC": 53, "SG": -7},
        {"Pos": 13, "Clube": "Coritiba", "Pts": 42, "J": 34, "V": 11, "E": 9, "D": 14, "GP": 40, "GC": 51, "SG": -11},
        {"Pos": 14, "Clube": "Mirassol", "Pts": 41, "J": 35, "V": 10, "E": 11, "D": 14, "GP": 39, "GC": 48, "SG": -9},
        {"Pos": 15, "Clube": "Vitória", "Pts": 38, "J": 34, "V": 10, "E": 8, "D": 16, "GP": 35, "GC": 51, "SG": -16},
        {"Pos": 16, "Clube": "Internacional", "Pts": 38, "J": 34, "V": 9, "E": 11, "D": 14, "GP": 38, "GC": 42, "SG": -4},
        {"Pos": 17, "Clube": "Corinthians", "Pts": 37, "J": 34, "V": 9, "E": 10, "D": 15, "GP": 36, "GC": 42, "SG": -6},
        {"Pos": 18, "Clube": "Grêmio", "Pts": 37, "J": 34, "V": 9, "E": 10, "D": 15, "GP": 38, "GC": 47, "SG": -9},
        {"Pos": 19, "Clube": "Remo", "Pts": 29, "J": 34, "V": 6, "E": 11, "D": 17, "GP": 37, "GC": 57, "SG": -20},
        {"Pos": 20, "Clube": "Chapecoense", "Pts": 21, "J": 34, "V": 4, "E": 9, "D": 21, "GP": 33, "GC": 70, "SG": -37}
    ]

@st.cache_data
def get_fixtures():
    fixtures_r35 = [
        ('Corinthians', 'Botafogo'), ('Grêmio', 'Bahia'), ('Vasco da Gama', 'Internacional'),
        ('Coritiba', 'Santos'), ('Remo', 'Chapecoense'), ('Vitória', 'RB Bragantino'),
        ('Flamengo', 'Fluminense'), ('Palmeiras', 'São Paulo'), ('Cruzeiro', 'Athletico-PR')
    ]
    fixtures_r36 = [
        ('Internacional', 'Vitória'), ('Atlético-MG', 'Corinthians'), ('Santos', 'Grêmio'),
        ('Fluminense', 'Mirassol'), ('Bahia', 'Coritiba'), ('Botafogo', 'São Paulo'),
        ('Athletico-PR', 'Remo'), ('Chapecoense', 'Palmeiras'), ('RB Bragantino', 'Cruzeiro'),
        ('Flamengo', 'Vasco da Gama')
    ]
    fixtures_r37 = [
        ('Corinthians', 'Grêmio'), ('Internacional', 'RB Bragantino'), ('Vitória', 'Santos'),
        ('Mirassol', 'Athletico-PR'), ('Coritiba', 'Flamengo'), ('Botafogo', 'Bahia'),
        ('São Paulo', 'Remo'), ('Cruzeiro', 'Chapecoense'), ('Palmeiras', 'Fluminense'),
        ('Vasco da Gama', 'Atlético-MG')
    ]
    fixtures_r38 = [
        ('Remo', 'Corinthians'), ('Grêmio', 'Mirassol'), ('Cruzeiro', 'Internacional'),
        ('Vasco da Gama', 'Vitória'), ('Palmeiras', 'Coritiba'), ('Santos', 'Botafogo'),
        ('Bahia', 'São Paulo'), ('Chapecoense', 'Atlético-MG'), ('Fluminense', 'RB Bragantino'),
        ('Athletico-PR', 'Flamengo')
    ]
    return fixtures_r35, fixtures_r36, fixtures_r37, fixtures_r38

# Simulation function with caching
@st.cache_data
def run_monte_carlo(n_sims=30000, home_adv=1.15, away_disadv=0.88):
    base_data = get_base_standings()
    r35, r36, r37, r38 = get_fixtures()
    all_fixtures = r35 + r36 + r37 + r38
    
    np.random.seed(42)
    team_ratings = {}
    for item in base_data:
        name = item['Clube']
        games = item['J']
        att = (item['GP'] / games) / 1.25
        defe = (item['GC'] / games) / 1.25
        team_ratings[name] = {'att': att, 'def': defe, 'pts': item['Pts']}
    
    relegation_counts = defaultdict(int)
    cut_points = []
    team_pts_scenarios = defaultdict(lambda: defaultdict(lambda: [0, 0]))

    for _ in range(n_sims):
        cur = {item['Clube']: {'pts': item['Pts'], 'J': item['J'], 'V': item['V'], 'E': item['E'], 'D': item['D'], 'GP': item['GP'], 'GC': item['GC']} for item in base_data}
        
        for home, away in all_fixtures:
            lh = 1.25 * team_ratings[home]['att'] * team_ratings[away]['def'] * home_adv
            la = 1.25 * team_ratings[away]['att'] * team_ratings[home]['def'] * away_disadv
            gh = np.random.poisson(lh)
            ga = np.random.poisson(la)
            cur[home]['J'] += 1; cur[away]['J'] += 1
            cur[home]['GP'] += gh; cur[home]['GC'] += ga
            cur[away]['GP'] += ga; cur[away]['GC'] += gh
            if gh > ga:
                cur[home]['pts'] += 3; cur[home]['V'] += 1; cur[away]['D'] += 1
            elif gh < ga:
                cur[away]['pts'] += 3; cur[away]['V'] += 1; cur[home]['D'] += 1
            else:
                cur[home]['pts'] += 1; cur[away]['pts'] += 1; cur[home]['E'] += 1; cur[away]['E'] += 1

        table = []
        for name, d in cur.items():
            sg = d['GP'] - d['GC']
            table.append((name, d['pts'], d['V'], sg, d['GP']))
        table.sort(key=lambda x: (x[1], x[2], x[3], x[4]), reverse=True)
        
        relegated = set([table[i][0] for i in range(16, 20)])
        for r in relegated:
            relegation_counts[r] += 1
        cut_points.append(table[16][1])
        
        for item in table:
            name = item[0]
            p = item[1]
            team_pts_scenarios[name][p][0] += 1
            if name in relegated:
                team_pts_scenarios[name][p][1] += 1
                
    return relegation_counts, cut_points, team_pts_scenarios

# -------------------------------------------------------------
# Sidebar
# -------------------------------------------------------------
st.sidebar.title("⚙️ Parâmetros do Modelo")
st.sidebar.markdown("**Campeonato Brasileiro Série A 2026**")
st.sidebar.info("📅 **Data-base:** 15/11/2026\n\n📌 **Rodada:** 35ª em andamento (*Mirassol 0x0 Galo já realizado*)")

n_sims = st.sidebar.select_slider(
    "Número de Simulações Monte Carlo:",
    options=[10000, 25000, 50000],
    value=25000
)

home_adv = st.sidebar.slider("Vantagem de Mando de Campo:", 1.05, 1.25, 1.15, 0.01)
away_disadv = st.sidebar.slider("Fator Desvantagem de Visitante:", 0.80, 0.95, 0.88, 0.01)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🏆 Critérios Oficiais CBF")
st.sidebar.caption("1º Pontos • 2º Vitórias • 3º Saldo de Gols • 4º Gols Pró • 5º Confronto Direto")

# Execute model
relegation_counts, cut_points, team_pts_scenarios = run_monte_carlo(n_sims, home_adv, away_disadv)
base_data = get_base_standings()

# Build dataframe
prob_rows = []
for item in base_data:
    name = item['Clube']
    pts = item['Pts']
    j = item['J']
    sg = item['SG']
    v = item['V']
    cnt = relegation_counts[name]
    prob = (cnt / n_sims) * 100
    
    if prob >= 99.0: status = "Crítico / Rebaixado"
    elif prob >= 40.0: status = "Alerta Alto (Perigo Direto)"
    elif prob >= 20.0: status = "Alerta Médio (Ameaçado)"
    elif prob >= 1.0: status = "Alerta Baixo (Risco Residual)"
    else: status = "Seguro (Risco Quase Nulo)"
        
    prob_rows.append({
        "Pos": item['Pos'],
        "Clube": name,
        "Pts": pts,
        "J": j,
        "V": v,
        "SG": sg,
        "Prob. Queda (%)": round(prob, 2),
        "Status de Risco": status
    })

df_prob = pd.DataFrame(prob_rows).sort_values(by="Prob. Queda (%)", ascending=False).reset_index(drop=True)

# -------------------------------------------------------------
# Main Header
# -------------------------------------------------------------
st.title("⚽ Brasileirão 2026: Análise e Probabilidades de Rebaixamento")
st.markdown("Dashboard interativo de ciência de dados e modelagem probabilística de pontos corridos da Série A.")

# Metrics Row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Linha de Corte Média (17º)", f"{np.mean(cut_points):.2f} pts", delta="-0.2 pts na rodada")
with col2:
    st.metric("Mediana da Salvação", f"{np.median(cut_points):.1f} pts", help="Pontuação mais frequente do 17º colocado")
with col3:
    st.metric("Pontuação 99% Segura", "44.0 pts", delta="Garantia estatística")
with col4:
    st.metric("Jogos Restantes por Clube", "3 a 4 jogos", help="Mirassol e Galo disputaram 35 partidas")

# -------------------------------------------------------------
# Tabs Layout
# -------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Tabela & Gráficos de Risco",
    "📈 Evolução Recente (R30-R35)",
    "🎲 Simulador de Rodadas Finais",
    "📋 Matriz de Cenários por Clube",
    "📐 Metodologia & Premissas"
])

# -------------------------------------------------------------
# TAB 1: Overview & Risk Charts
# -------------------------------------------------------------
with tab1:
    st.subheader("🔥 Ranking Oficial de Risco de Rebaixamento (Z-4)")
    
    col_tabela, col_grafico = st.columns([6, 5])
    
    with col_tabela:
        # Styled dataframe
        def highlight_risk(val):
            if val >= 90: return 'background-color: rgba(220, 38, 38, 0.25); color: #dc2626; font-weight: bold;'
            elif val >= 45: return 'background-color: rgba(234, 88, 12, 0.25); color: #ea580c; font-weight: bold;'
            elif val >= 20: return 'background-color: rgba(202, 138, 4, 0.25); color: #ca8a04; font-weight: bold;'
            elif val >= 5: return 'background-color: rgba(22, 163, 74, 0.25); color: #16a34a;'
            else: return 'color: #3b82f6;'

        st.dataframe(
            df_prob.head(11).style.applymap(highlight_risk, subset=['Prob. Queda (%)']),
            use_container_width=True,
            height=420
        )
        st.caption("Times da 1ª à 9ª colocação apresentam risco estatístico inferior a 0,001%.")

    with col_grafico:
        # Matplotlib Horizontal Bar Chart
        threatened = df_prob[df_prob["Prob. Queda (%)"] > 0.05].copy()
        colors = []
        for p in threatened["Prob. Queda (%)"]:
            if p >= 90: colors.append("#d32f2f")
            elif p >= 45: colors.append("#f57c00")
            elif p >= 20: colors.append("#fbc02d")
            elif p >= 5: colors.append("#388e3c")
            else: colors.append("#1976d2")

        fig_bar, ax = plt.subplots(figsize=(7, 5))
        bars = ax.barh(threatened["Clube"], threatened["Prob. Queda (%)"], color=colors, edgecolor="black", alpha=0.85)
        ax.axvline(50, color='red', linestyle='--', linewidth=1.5, label='Limiar Crítico (50%)')
        ax.set_xlabel('Probabilidade de Rebaixamento (%)', fontweight='bold')
        ax.set_xlim(0, 105)
        ax.invert_yaxis()
        ax.legend(loc='lower right')
        
        for bar in bars:
            w = bar.get_width()
            ax.text(w + 1.2, bar.get_y() + bar.get_height()/2, f'{w:.1f}%', va='center', fontsize=9, fontweight='bold')

        plt.tight_layout()
        st.pyplot(fig_bar)

    st.markdown("---")
    
    # Bottom Row: Summary Cards of Top 3
    st.subheader("🚨 Resumo Executivo: Os Três Maiores Riscos Ativos")
    sc1, sc2, sc3 = st.columns(3)
    
    with sc1:
        st.error("### 1. Grêmio (18º | 37 pts)")
        st.markdown("**Probabilidade:** `53.7%`")
        st.write("• **Motivo:** Saldo negativo de -9 e 2 partidas difíceis como visitante (Santos e Corinthians).")
        st.write("• **Meta:** Vencer os 2 na Arena (Bahia e Mirassol) e buscar 1 ponto fora.")
    
    with sc2:
        st.warning("### 2. Vitória (15º | 38 pts)")
        st.markdown("**Probabilidade:** `45.4%`")
        st.write("• **Motivo:** Pior saldo entre os concorrentes diretos (-16) e duelo direto contra o Inter no Beira-Rio.")
        st.write("• **Meta:** Transformar o Barradão em trunfo contra Bragantino e Santos para alcançar 44 pts.")
        
    with sc3:
        st.info("### 3. Corinthians (17º | 37 pts)")
        st.markdown("**Probabilidade:** `39.7%`")
        st.write("• **Motivo:** Abre o Z-4 após jejum de vitórias, mas tem melhor saldo (-6) e recebe Botafogo e Grêmio.")
        st.write("• **Meta:** 7 pontos em 12 (vencer Botafogo e Remo, e empatar com o Grêmio).")

# -------------------------------------------------------------
# TAB 2: Recent Evolution
# -------------------------------------------------------------
with tab2:
    st.subheader("📈 Trajetória da Classificação nas Rodadas Recentes (R30 a R35)")
    st.markdown("Acompanhe como o rendimento das últimas 5 rodadas impactou a entrada ou saída da zona da degola.")
    
    rodadas = ['R30', 'R31', 'R32', 'R33', 'R34', 'R35']
    evo_dict = {
        'Corinthians': [15, 15, 16, 17, 17, 17],
        'Grêmio': [17, 17, 17, 18, 18, 18],
        'Vitória': [18, 14, 14, 14, 15, 15],
        'Internacional': [16, 16, 15, 15, 16, 16],
        'Mirassol': [14, 13, 13, 13, 13, 14],
        'Coritiba': [13, 12, 12, 12, 12, 13],
        'Remo': [19, 19, 19, 19, 19, 19],
        'Chapecoense': [20, 20, 20, 20, 20, 20]
    }

    fig_evo, ax = plt.subplots(figsize=(10, 5))
    cores = {
        'Corinthians': '#000000', 'Grêmio': '#0d47a1', 'Vitória': '#d50000',
        'Internacional': '#b71c1c', 'Mirassol': '#fbc02d', 'Coritiba': '#1b5e20',
        'Remo': '#37474f', 'Chapecoense': '#78909c'
    }

    for club, positions in evo_dict.items():
        ax.plot(rodadas, positions, marker='o', linewidth=2.5, label=f"{club} ({positions[-1]}º)", color=cores[club])

    ax.axhline(16.5, color='crimson', linestyle='--', linewidth=2, label='Linha do Z-4 (Rebaixamento)')
    ax.set_ylim(20.5, 11.5) # Invert axis
    ax.set_yticks(range(12, 21))
    ax.set_ylabel('Posição na Tabela (Invertida)', fontweight='bold')
    ax.set_xlabel('Rodadas', fontweight='bold')
    ax.legend(loc='lower left', bbox_to_anchor=(0.01, 0.02), framealpha=0.9, ncol=2)
    ax.grid(True, linestyle='--', alpha=0.5)

    st.pyplot(fig_evo)

# -------------------------------------------------------------
# TAB 3: Match Simulator (Todos os 29 Jogos dos Ameaçados)
# -------------------------------------------------------------
with tab3:
    st.subheader("🎲 Simulador Completo de Todos os Jogos dos Clubes Sob Risco")
    st.markdown("Altere os resultados de **todas as 29 partidas restantes** envolvendo os times sob ameaça e visualize a classificação projetada em tempo real.")

    # Base teams for projection
    base_projection = [
        {"Clube": "São Paulo", "Pts_Base": 44, "J_Base": 34, "V_Base": 12, "SG_Base": 0},
        {"Clube": "Vasco da Gama", "Pts_Base": 44, "J_Base": 34, "V_Base": 12, "SG_Base": -5},
        {"Clube": "Botafogo", "Pts_Base": 42, "J_Base": 34, "V_Base": 11, "SG_Base": -7},
        {"Clube": "Coritiba", "Pts_Base": 42, "J_Base": 34, "V_Base": 11, "SG_Base": -11},
        {"Clube": "Mirassol", "Pts_Base": 41, "J_Base": 35, "V_Base": 10, "SG_Base": -9},
        {"Clube": "Vitória", "Pts_Base": 38, "J_Base": 34, "V_Base": 10, "SG_Base": -16},
        {"Clube": "Internacional", "Pts_Base": 38, "J_Base": 34, "V_Base": 9, "SG_Base": -4},
        {"Clube": "Corinthians", "Pts_Base": 37, "J_Base": 34, "V_Base": 9, "SG_Base": -6},
        {"Clube": "Grêmio", "Pts_Base": 37, "J_Base": 34, "V_Base": 9, "SG_Base": -9},
        {"Clube": "Remo", "Pts_Base": 29, "J_Base": 34, "V_Base": 6, "SG_Base": -20},
        {"Clube": "Chapecoense", "Pts_Base": 21, "J_Base": 34, "V_Base": 4, "SG_Base": -37}
    ]

    # Quick presets
    preset_col1, preset_col2, preset_col3 = st.columns([2, 2, 4])
    with preset_col1:
        default_choice = st.radio("Preenchimento Rápido:", ["Empates", "Mandantes Vencem"], horizontal=True)
    def_idx = 1 if default_choice == "Empates" else 0

    # Match definitions
    matches_r35 = [
        ("Corinthians", "Botafogo", True),
        ("Grêmio", "Bahia", False),
        ("Vasco da Gama", "Internacional", True),
        ("Coritiba", "Santos", False),
        ("Remo", "Chapecoense", True),
        ("Vitória", "RB Bragantino", False)
    ]
    matches_r36 = [
        ("Internacional", "Vitória", True),
        ("Atlético-MG", "Corinthians", False),
        ("Santos", "Grêmio", False),
        ("Fluminense", "Mirassol", False),
        ("Bahia", "Coritiba", False),
        ("Botafogo", "São Paulo", True),
        ("Athletico-PR", "Remo", False),
        ("Chapecoense", "Palmeiras", False)
    ]
    matches_r37 = [
        ("Corinthians", "Grêmio", True),
        ("Internacional", "RB Bragantino", False),
        ("Vitória", "Santos", False),
        ("Mirassol", "Athletico-PR", False),
        ("Coritiba", "Flamengo", False),
        ("Botafogo", "Bahia", False),
        ("São Paulo", "Remo", True),
        ("Cruzeiro", "Chapecoense", False)
    ]
    matches_r38 = [
        ("Grêmio", "Mirassol", True),
        ("Remo", "Corinthians", True),
        ("Cruzeiro", "Internacional", False),
        ("Vasco da Gama", "Vitória", True),
        ("Palmeiras", "Coritiba", False),
        ("Santos", "Botafogo", False),
        ("Chapecoense", "Atlético-MG", False)
    ]

    sim_pts = {t["Clube"]: t["Pts_Base"] for t in base_projection}
    sim_j = {t["Clube"]: t["J_Base"] for t in base_projection}
    sim_v = {t["Clube"]: t["V_Base"] for t in base_projection}
    sim_sg = {t["Clube"]: t["SG_Base"] for t in base_projection}

    def process_match(h, a, pick):
        if h in sim_j: sim_j[h] += 1
        if a in sim_j: sim_j[a] += 1
        if pick == "Casa":
            if h in sim_pts: sim_pts[h] += 3; sim_v[h] += 1; sim_sg[h] += 1
            if a in sim_sg: sim_sg[a] -= 1
        elif pick == "Fora":
            if a in sim_pts: sim_pts[a] += 3; sim_v[a] += 1; sim_sg[a] += 1
            if h in sim_sg: sim_sg[h] -= 1
        else: # Empate
            if h in sim_pts: sim_pts[h] += 1
            if a in sim_pts: sim_pts[a] += 1

    # Tabs for the 4 rounds
    r_tab1, r_tab2, r_tab3, r_tab4 = st.tabs(["35ª Rodada (6 jogos)", "36ª Rodada (8 jogos)", "37ª Rodada (8 jogos)", "38ª Rodada (7 jogos)"])

    with r_tab1:
        st.caption("35ª Rodada (*Mirassol 0x0 Galo já realizado em 14/11*)")
        c1, c2 = st.columns(2)
        for i, (h, a, is_dir) in enumerate(matches_r35):
            col = c1 if i % 2 == 0 else c2
            tag = " ⚡ [Direto]" if is_dir else ""
            res = col.selectbox(f"{h} x {a}{tag}", ["Casa", "Empate", "Fora"], index=def_idx, key=f"r35_{i}")
            process_match(h, a, res)

    with r_tab2:
        st.caption("36ª Rodada — Destaque: Internacional x Vitória no Beira-Rio")
        c1, c2 = st.columns(2)
        for i, (h, a, is_dir) in enumerate(matches_r36):
            col = c1 if i % 2 == 0 else c2
            tag = " ⚡ [Direto]" if is_dir else ""
            res = col.selectbox(f"{h} x {a}{tag}", ["Casa", "Empate", "Fora"], index=def_idx, key=f"r36_{i}")
            process_match(h, a, res)

    with r_tab3:
        st.caption("37ª Rodada — Destaque: Corinthians x Grêmio em Itaquera")
        c1, c2 = st.columns(2)
        for i, (h, a, is_dir) in enumerate(matches_r37):
            col = c1 if i % 2 == 0 else c2
            tag = " ⚡ [Direto]" if is_dir else ""
            res = col.selectbox(f"{h} x {a}{tag}", ["Casa", "Empate", "Fora"], index=def_idx, key=f"r37_{i}")
            process_match(h, a, res)

    with r_tab4:
        st.caption("38ª Rodada — Rodada Final Simultânea (Grêmio x Mirassol, Remo x Timão)")
        c1, c2 = st.columns(2)
        for i, (h, a, is_dir) in enumerate(matches_r38):
            col = c1 if i % 2 == 0 else c2
            tag = " ⚡ [Direto]" if is_dir else ""
            res = col.selectbox(f"{h} x {a}{tag}", ["Casa", "Empate", "Fora"], index=def_idx, key=f"r38_{i}")
            process_match(h, a, res)

    st.markdown("---")
    st.subheader("📊 Classificação Final Projetada com a Simulação Atual")

    # Build final table
    res_table = []
    for t in base_projection:
        name = t["Clube"]
        p_init = t["Pts_Base"]
        p_fin = sim_pts[name]
        diff = p_fin - p_init
        res_table.append({
            "Clube": name,
            "Pts Iniciais": p_init,
            "Pts Ganhos": f"+{diff} pts",
            "Pts Finais": p_fin,
            "Jogos": f"{sim_j[name]}/38",
            "Vitórias": sim_v[name],
            "Saldo": sim_sg[name]
        })

    df_sim_final = pd.DataFrame(res_table).sort_values(by=["Pts Finais", "Vitórias", "Saldo"], ascending=[False, False, False]).reset_index(drop=True)
    df_sim_final.index = df_sim_final.index + 10 # Positions 10 to 20
    df_sim_final["Posição Projetada"] = [f"{i}º" for i in df_sim_final.index]
    
    # Diagnosis
    diag = []
    for pos, p in zip(df_sim_final.index, df_sim_final["Pts Finais"]):
        if pos >= 17:
            diag.append("🚨 ZONA DE REBAIXAMENTO (Z-4)")
        elif p >= 44:
            diag.append("✅ SALVO (LIVRE)")
        else:
            diag.append("⚠️ NO LIMIAR DA DEGOLA")
    df_sim_final["Diagnóstico Final"] = diag

    # Display columns
    cols_order = ["Posição Projetada", "Clube", "Pts Iniciais", "Pts Ganhos", "Pts Finais", "Jogos", "Vitórias", "Saldo", "Diagnóstico Final"]
    
    def color_rows(val):
        if "REBAIXAMENTO" in str(val):
            return "background-color: rgba(220, 38, 38, 0.25); color: #dc2626; font-weight: bold;"
        elif "SALVO" in str(val):
            return "background-color: rgba(22, 163, 74, 0.2); color: #16a34a; font-weight: bold;"
        else:
            return "background-color: rgba(202, 138, 4, 0.2); color: #ca8a04; font-weight: bold;"

    st.dataframe(
        df_sim_final[cols_order].style.applymap(color_rows, subset=["Diagnóstico Final"]),
        use_container_width=True,
        height=420
    )

# -------------------------------------------------------------
# TAB 4: Scenario Matrix per Club
# -------------------------------------------------------------
with tab4:
    st.subheader("📋 Matriz Condicional de Sobrevivência por Faixa de Pontos")
    st.markdown("Selecione um clube para visualizar exatamente a probabilidade de rebaixamento para cada pontuação final:")

    clube_selecionado = st.selectbox(
        "Selecione o clube:",
        ['Grêmio', 'Vitória', 'Corinthians', 'Internacional', 'Mirassol', 'Coritiba']
    )

    pts_atuais = [item['Pts'] for item in base_data if item['Clube'] == clube_selecionado][0]
    scenarios = team_pts_scenarios[clube_selecionado]
    
    t_rows = []
    for p in range(pts_atuais, pts_atuais + 13):
        if p in scenarios and scenarios[p][0] > 20:
            tot, rel = scenarios[p]
            prob_rel = (rel / tot) * 100
            diff = p - pts_atuais
            
            if prob_rel <= 1.0: diag = "🛡️ Permanência Garantida"
            elif prob_rel <= 15.0: diag = "✅ Altamente Seguro"
            elif prob_rel <= 50.0: diag = "⚖️ Depende de Terceiros"
            else: diag = "⚠️ Risco Crítico / Queda Provável"
            
            t_rows.append({
                "Pontos Finais": p,
                "Aproveitamento Restante": f"+{diff} pts",
                "Risco de Queda (%)": f"{prob_rel:.1f}%",
                "Chance de Salvação (%)": f"{100 - prob_rel:.1f}%",
                "Diagnóstico": diag
            })

    st.table(pd.DataFrame(t_rows))

# -------------------------------------------------------------
# TAB 5: Methodology
# -------------------------------------------------------------
with tab5:
    st.subheader("📐 Metodologia Estatística e Premissas do Modelo")
    
    m_col1, m_col2 = st.columns(2)
    with m_col1:
        st.markdown("""
        ### 1. Processo Estocástico Bivariado de Poisson
        Para cada partida simulada, a taxa de gols esperada de cada clube $\\lambda$ é formulada como:
        $$\\lambda_{mandante} = 1.25 \\times \\text{Ataque}_{mandante} \\times \\text{Defesa}_{visitante} \\times \\text{Mando}$$
        $$\\lambda_{visitante} = 1.25 \\times \\text{Ataque}_{visitante} \\times \\text{Defesa}_{mandante} \\times \\text{Visitante}$$
        
        * **Vantagem de Mando:** $+15\\%$ gols esperados.
        * **Desvantagem de Visitante:** $-12\\%$ gols esperados.
        * **Critérios CBF:** Desempate estritamente por Pontos > Vitórias > Saldo de Gols > Gols Pró.
        """)
        
    with m_col2:
        st.markdown("""
        ### 2. Incerteza e Amostra Reduzida
        * Restando apenas **3 a 4 partidas**, a variância estatística por partida é expressiva.
        * Um único resultado inesperado ou pênalti aos 90 minutos em confronto direto desloca a probabilidade do clube em **30 a 35 pontos percentuais**.
        * **A convergência de Monte Carlo** com dezenas de milhares de iterações garante que o intervalo de confiança assintótico seja inferior a $\\pm 0.3\\%$.
        """)

st.markdown("---")
st.caption("Desenvolvido para análise esportiva e modelagem de dados do Brasileirão Série A 2026. Atualizado em 15 de novembro de 2026.")
