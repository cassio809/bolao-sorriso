import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Configuração inicial da página
st.set_page_config(page_title="Bolão Copa 2026 - CLÍNICA SORRISO DE TODOS", layout="wide")
st.title("🏆 Bolão Mata-Mata - CLÍNICA SORRISO DE TODOS")

# --- CONEXÃO COM GOOGLE SHEETS ---
# O Streamlit gerencia a conexão e o cache automaticamente
conn = st.connection("gsheets", type=GSheetsConnection)

def carregar_dados_sheets():
    """Lê as 3 abas do Google Sheets e inicializa o estado do sistema."""
    try:
        # 1. Carrega Participantes
        df_part = conn.read(worksheet="participantes", ttl=0)
        if not df_part.empty and "Nome" in df_part.columns:
            st.session_state.participantes = dict(zip(df_part["Nome"], df_part["Pontos"]))
        else:
            st.session_state.participantes = {"Cássio": 0, "Carol": 0, "Gabriel": 0}
            
        # 2. Carrega Jogos
        df_jogos = conn.read(worksheet="jogos", ttl=0)
        if not df_jogos.empty and "id" in df_jogos.columns:
            # Converte dataframe de volta para lista de dicionários
            st.session_state.jogos = df_jogos.to_dict(orient="records")
            # Garante que os booleanos e inteiros voltem no formato correto
            for j in st.session_state.jogos:
                j["id"] = int(j["id"])
                j["gols_a_real"] = int(j["gols_a_real"])
                j["gols_b_real"] = int(j["gols_b_real"])
                j["encerrado"] = bool(j["encerrado"])
        else:
            st.session_state.jogos = [
                {"id": 1, "fase": "Oitavas", "time_a": "Alemanha", "time_b": "França", "gols_a_real": 0, "gols_b_real": 0, "encerrado": False, "vencedor": ""},
                {"id": 2, "fase": "Oitavas", "time_a": "Brasil", "time_b": "Argentina", "gols_a_real": 0, "gols_b_real": 0, "encerrado": False, "vencedor": ""}
            ]
            
        # 3. Carrega Palpites
        df_palp = conn.read(worksheet="palpites", ttl=0)
        st.session_state.palpites = {}
        if not df_palp.empty and "jogo_id" in df_palp.columns:
            for _, row in df_palp.iterrows():
                chave = (int(row["jogo_id"]), str(row["participante"]))
                st.session_state.palpites[chave] = [int(row["gols_a"]), int(row["gols_b"]), str(row["vencedor_empate"])]
                
    except Exception as e:
        # Se as abas estiverem totalmente vazias na primeira execução, cria a estrutura padrão
        st.session_state.participantes = {"Cássio": 0, "Carol": 0, "Gabriel": 0}
        st.session_state.jogos = [
            {"id": 1, "fase": "Oitavas", "time_a": "Alemanha", "time_b": "França", "gols_a_real": 0, "gols_b_real": 0, "encerrado": False, "vencedor": ""},
            {"id": 2, "fase": "Oitavas", "time_a": "Brasil", "time_b": "Argentina", "gols_a_real": 0, "gols_b_real": 0, "encerrado": False, "vencedor": ""}
        ]
        st.session_state.palpites = {}
        salvar_dados_sheets()

def salvar_dados_sheets():
    """Transforma o estado atual em DataFrames e atualiza o Google Sheets."""
    # 1. Salva Participantes
    df_part = pd.DataFrame(list(st.session_state.participantes.items()), columns=["Nome", "Pontos"])
    conn.update(worksheet="participantes", data=df_part)
    
    # 2. Salva Jogos
    df_jogos = pd.DataFrame(st.session_state.jogos)
    conn.update(worksheet="jogos", data=df_jogos)
    
    # 3. Salva Palpites
    linhas_palpites = []
    for (jogo_id, part), valores in st.session_state.palpites.items():
        linhas_palpites.append({
            "jogo_id": jogo_id,
            "participante": part,
            "gols_a": valores[0],
            "gols_b": valores[1],
            "vencedor_empate": valores[2]
        })
    if linhas_palpites:
        df_palp = pd.DataFrame(linhas_palpites)
    else:
        df_palp = pd.DataFrame(columns=["jogo_id", "participante", "gols_a", "gols_b", "vencedor_empate"])
    conn.update(worksheet="palpites", data=df_palp)


# Inicializa os dados puxando direto do Google Sheets
if 'dados_carregados' not in st.session_state:
    carregar_dados_sheets()
    st.session_state.dados_carregados = True


# --- FUNÇÃO DE CÁLCULO DE PONTOS ---
def calcular_pontos(g_a_p, g_b_p, g_a_r, g_b_r):
    if g_a_p == g_a_r and g_b_p == g_b_r: return 25
    v_real = 1 if g_a_r > g_b_r else (2 if g_b_r > g_a_r else 0)
    v_palp = 1 if g_a_p > g_b_p else (2 if g_b_p > g_a_p else 0)
    if v_real == v_palp: return 10
    if g_a_p == g_a_r or g_b_p == g_b_r: return 5
    return 0


# --- CRIAÇÃO DAS ABAS (LAYOUT) ---
tab_ranking, tab_part, tab_jogos, tab_palpites = st.tabs([
    "📊 Ranking Geral", "👥 Participantes", "⚽ Cadastrar/Encerrar Jogos", "📝 Input de Palpites"
])

# ==========================================
# ABA 1: RANKING GERAL
# ==========================================
with tab_ranking:
    st.header("Classificação Atual dos Participantes")
    
    # Botão para forçar atualização caso você altere algo direto na planilha do Google
    if st.button("🔄 Atualizar Dados da Planilha"):
        st.cache_data.clear() # Limpa o cache do Streamlit
        carregar_dados_sheets()
        st.rerun()
        
    if st.session_state.participantes:
        df_ranking = pd.DataFrame(list(st.session_state.participantes.items()), columns=["Nome", "Pontos"])
        df_ranking = df_ranking.sort_values(by="Pontos", ascending=False).reset_index(drop=True)
        df_ranking.index += 1
        st.table(df_ranking)
    else:
        st.info("Nenhum participante cadastrado ainda.")

# ==========================================
# ABA 2: PARTICIPANTES
# ==========================================
with tab_part:
    st.header("Gerenciar Participantes")

    with st.form("novo_participante", clear_on_submit=True):
        nome_novo = st.text_input("Nome do Participante:")
        if st.form_submit_button("Adicionar no Bolão") and nome_novo:
            if nome_novo not in st.session_state.participantes:
                st.session_state.participantes[nome_novo] = 0
                salvar_dados_sheets()
                st.success(f"{nome_novo} adicionado com sucesso!")
                st.rerun()
            else:
                st.error("Esse nome já está cadastrado.")

    st.subheader("Lista de Cadastrados")
    for p in list(st.session_state.participantes.keys()):
        col1, col2 = st.columns([4, 1])
        col1.write(f"• {p}")
        if col2.button("Remover", key=f"rem_{p}"):
            del st.session_state.participantes[p]
            salvar_dados_sheets()
            st.rerun()

# ==========================================
# ABA 3: CADASTRAR / ENCERRAR JOGOS
# ==========================================
with tab_jogos:
    st.header("Gerenciar Confrontos do Mata-Mata")

    with st.expander("➕ Cadastrar Novo Jogo"):
        fase = st.selectbox("Fase:", ["2ª Fase", "Oitavas de Final", "Quartas de Final", "Semifinal", "Final"])
        t_a = st.text_input("Time A:")
        t_b = st.text_input("Time B:")
        if st.button("Salvar Jogo") and t_a and t_b:
            novo_id = max([j["id"] for j in st.session_state.jogos]) + 1 if st.session_state.jogos else 1
            st.session_state.jogos.append({
                "id": novo_id, "fase": fase, "time_a": t_a, "time_b": t_b,
                "gols_a_real": 0, "gols_b_real": 0, "encerrado": False, "vencedor": ""
            })
            salvar_dados_sheets()
            st.success(f"Jogo {t_a} x {t_b} criado!")
            st.rerun()

    st.subheader("Jogos Cadastrados")
    # Copiamos a lista para evitar problemas ao usar o pop(idx) durante a iteração
    jogos_loop = list(st.session_state.jogos)
    for idx, jogo in enumerate(jogos_loop):
        status = "🔴 Aberto" if not jogo["encerrado"] else f"🟢 Encerrado (Vencedor: {jogo['vencedor']})"
        
        col_tit, col_del = st.columns([5, 1])
        col_tit.markdown(f"**Jogo #{jogo['id']} ({jogo['fase']})** - {status}")
        
        if col_del.button("🗑️ Excluir Jogo", key=f"del_jogo_{jogo['id']}"):
            st.session_state.jogos.pop(idx)
            chaves_para_deletar = [k for k in st.session_state.palpites.keys() if k[0] == jogo['id']]
            for kh in chaves_para_deletar:
                del st.session_state.palpites[kh]
            salvar_dados_sheets()
            st.warning(f"Jogo #{jogo['id']} excluído.")
            st.rerun()

        col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
        gols_a = col1.number_input(f"Gols {jogo['time_a']}", min_value=0, value=int(jogo['gols_a_real']), key=f"real_a_{jogo['id']}", disabled=jogo['encerrado'])
        gols_b = col2.number_input(f"Gols {jogo['time_b']}", min_value=0, value=int(jogo['gols_b_real']), key=f"real_b_{jogo['id']}", disabled=jogo['encerrado'])

        vencedor_opcoes = [jogo['time_a'], jogo['time_b']]
        default_venc_idx = vencedor_opcoes.index(jogo['vencedor']) if jogo['vencedor'] in vencedor_opcoes else 0
        vencedor_p = col3.selectbox("Quem avança?", vencedor_opcoes, index=default_venc_idx, key=f"venc_{jogo['id']}", disabled=jogo['encerrado'])

        if not jogo["encerrado"]:
            if col4.button("Encerrar Jogo e Rodar Pontos", key=f"btn_encerrar_{jogo['id']}"):
                st.session_state.jogos[idx]["gols_a_real"] = gols_a
                st.session_state.jogos[idx]["gols_b_real"] = gols_b
                st.session_state.jogos[idx]["encerrado"] = True
                st.session_state.jogos[idx]["vencedor"] = vencedor_p

                for part in st.session_state.participantes.keys():
                    chave_palpite = (jogo['id'], part)
                    if chave_palpite in st.session_state.palpites:
                        g_a_p, g_b_p, venc_palp = st.session_state.palpites[chave_palpite]
                        pontos_ganhos = calcular_pontos(g_a_p, g_b_p, gols_a, gols_b)
                        st.session_state.participantes[part] += pontos_ganhos

                salvar_dados_sheets()
                st.success("Pontuações calculadas e salvas no Google Sheets!")
                st.rerun()
        st.markdown("---")

# ==========================================
# ABA 4: INPUT DE PALPITES
# ==========================================
with tab_palpites:
    st.header("Digitação Rápida de Palpites por Jogo")

    jogos_abertos = [j for j in st.session_state.jogos if not j["encerrado"]]

    if jogos_abertos and st.session_state.participantes:
        opcoes_jogos = {f"Jogo #{j['id']}: {j['time_a']} x {j['time_b']} ({j['fase']})": j['id'] for j in jogos_abertos}
        selecao = st.selectbox("Escolha o Jogo para preencher:", list(opcoes_jogos.keys()))
        jogo_id_sel = opcoes_jogos[selecao]
        
        jogo_atual = next(j for j in st.session_state.jogos if j["id"] == jogo_id_sel)

        with st.form(key=f"form_palpites_{jogo_id_sel}"):
            st.write("Digite os palpites da galera (Use TAB para navegar rápido):")
            novos_palpites_temp = {}

            for part in st.session_state.participantes.keys():
                col_nome, col_inp1, col_inp2, col_venc = st.columns([2, 1, 1, 2])
                col_nome.write(f"**{part}**")

                valor_antigo = st.session_state.palpites.get((jogo_id_sel, part), [0, 0, jogo_atual["time_a"]])
                
                p_a = col_inp1.number_input(f"Gols {jogo_atual['time_a']}", min_value=0, value=int(valor_antigo[0]), key=f"p_a_{jogo_id_sel}_{part}")
                p_b = col_inp2.number_input(f"Gols {jogo_atual['time_b']}", min_value=0, value=int(valor_antigo[1]), key=f"p_b_{jogo_id_sel}_{part}")
                
                opcoes_desempate = [jogo_atual["time_a"], jogo_atual["time_b"]]
                default_v_idx = opcoes_desempate.index(valor_antigo[2]) if valor_antigo[2] in opcoes_desempate else 0
                v_p = col_venc.selectbox(f"Se empate, avança:", opcoes_desempate, index=default_v_idx, key=f"v_p_{jogo_id_sel}_{part}")

                novos_palpites_temp[(jogo_id_sel, part)] = [p_a, p_b, v_p]

            if st.form_submit_button("💾 Salvar Todos os Palpites Deste Jogo"):
                st.session_state.palpites.update(novos_palpites_temp)
                salvar_dados_sheets()
                st.success("Todos os palpites foram guardados com sucesso no Google Sheets!")
                st.rerun()
    else:
        st.info("Cadastre participantes e certifique-se de que há jogos abertos para palpites.")
