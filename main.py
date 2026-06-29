import streamlit as st
import pandas as pd
from supabase import create_client, Client

# Configuração inicial da página
st.set_page_config(page_title="Bolão Copa 2026 - CLÍNICA SORRISO DE TODOS", layout="wide")
st.title("🏆 Bolão Mata-Mata - CLÍNICA SORRISO DE TODOS")

# --- CONEXÃO COM O SUPABASE ---
@st.cache_resource
def init_connection():
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

supabase: Client = init_connection()

def carregar_dados_supabase():
    """Puxa os dados atualizados das tabelas do Supabase para o st.session_state."""
    # 1. Carrega Participantes
    res_part = supabase.table("participantes").select("*").execute()
    st.session_state.participantes = {row["nome"]: row["pontos"] for row in res_part.data}
        
    # 2. Carrega Jogos (Ordenados por ID)
    res_jogos = supabase.table("jogos").select("*").order("id").execute()
    st.session_state.jogos = res_jogos.data
        
    # 3. Carrega Palpites
    res_palp = supabase.table("palpites").select("*").execute()
    st.session_state.palpites = {}
    for row in res_palp.data:
        chave = (int(row["jogo_id"]), str(row["participante"]))
        st.session_state.palpites[chave] = [int(row["gols_a"]), int(row["gols_b"]), str(row["vencedor_empate"])]

# Inicializa os dados na primeira execução
if 'dados_carregados' not in st.session_state:
    carregar_dados_supabase()
    st.session_state.dados_carregados = True

# --- FUNÇÃO DE CÁLCULO DE PONTOS ---
def calcular_pontos(g_a_p, g_b_p, g_a_r, g_b_r):
    if g_a_p == g_a_r and g_b_p == g_b_r: return 25
    v_real = 1 if g_a_r > g_b_r else (2 if g_b_r > g_a_r else 0)
    v_palp = 1 if g_a_p > g_b_p else (2 if g_b_p > g_a_p else 0)
    if v_real == v_palp: return 10
    if g_a_p == g_a_r or g_b_p == g_b_r: return 5
    return 0

# --- CRIAÇÃO DAS ABAS ---
tab_ranking, tab_part, tab_jogos, tab_palpites = st.tabs([
    "📊 Ranking Geral", "👥 Participantes", "⚽ Cadastrar/Encerrar Jogos", "📝 Input de Palpites"
])

# ==========================================
# ABA 1: RANKING GERAL
# ==========================================
with tab_ranking:
    st.header("Classificação Atual dos Participantes")
    if st.button("🔄 Sincronizar Banco de Dados"):
        carregar_dados_supabase()
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
                # Grava no Supabase
                supabase.table("participantes").insert({"nome": nome_novo, "pontos": 0}).execute()
                carregar_dados_supabase()
                st.success(f"{nome_novo} adicionado com sucesso!")
                st.rerun()
            else:
                st.error("Esse nome já está cadastrado.")

    st.subheader("Lista de Cadastrados")
    for p in list(st.session_state.participantes.keys()):
        col1, col2 = st.columns([4, 1])
        col1.write(f"• {p}")
        if col2.button("Remover", key=f"rem_{p}"):
            supabase.table("participantes").delete().eq("nome", p).execute()
            carregar_dados_supabase()
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
            # Grava no Supabase
            supabase.table("jogos").insert({
                "id": novo_id, "fase": fase, "time_a": t_a, "time_b": t_b,
                "gols_a_real": 0, "gols_b_real": 0, "encerrado": False, "vencedor": ""
            }).execute()
            carregar_dados_supabase()
            st.success(f"Jogo {t_a} x {t_b} criado!")
            st.rerun()

    st.subheader("Jogos Cadastrados")
    for idx, jogo in enumerate(st.session_state.jogos):
        status = "🔴 Aberto" if not jogo["encerrado"] else f"🟢 Encerrado (Vencedor: {jogo['vencedor']})"
        
        col_tit, col_del = st.columns([5, 1])
        col_tit.markdown(f"**Jogo #{jogo['id']} ({jogo['fase']})** - {status}")
        
        if col_del.button("🗑️ Excluir Jogo", key=f"del_jogo_{jogo['id']}"):
            supabase.table("jogos").delete().eq("id", jogo['id']).execute()
            carregar_dados_supabase()
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
                # 1. Atualiza jogo no Supabase
                supabase.table("jogos").update({
                    "gols_a_real": gols_a, "gols_b_real": gols_b, "encerrado": True, "vencedor": vencedor_p
                }).eq("id", jogo['id']).execute()

                # 2. Varre os palpites e calcula a pontuação
                for part in st.session_state.participantes.keys():
                    chave_palpite = (jogo['id'], part)
                    if chave_palpite in st.session_state.palpites:
                        g_a_p, g_b_p, _ = st.session_state.palpites[chave_palpite]
                        pontos_ganhos = calcular_pontos(g_a_p, g_b_p, gols_a, gols_b)
                        
                        # Atualiza os pontos somados do participante direto no banco
                        novos_pontos = st.session_state.participantes[part] + pontos_ganhos
                        supabase.table("participantes").update({"pontos": novos_pontos}).eq("nome", part).execute()

                carregar_dados_supabase()
                st.success("Pontuações calculadas e salvas no Supabase!")
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
            novos_palpites_temp = []

            for part in st.session_state.participantes.keys():
                col_nome, col_inp1, col_inp2, col_venc = st.columns([2, 1, 1, 2])
                col_nome.write(f"**{part}**")

                valor_antigo = st.session_state.palpites.get((jogo_id_sel, part), [0, 0, jogo_atual["time_a"]])
                
                p_a = col_inp1.number_input(f"Gols {jogo_atual['time_a']}", min_value=0, value=int(valor_antigo[0]), key=f"p_a_{jogo_id_sel}_{part}")
                p_b = col_inp2.number_input(f"Gols {jogo_atual['time_b']}", min_value=0, value=int(valor_antigo[1]), key=f"p_b_{jogo_id_sel}_{part}")
                
                opcoes_desempate = [jogo_atual["time_a"], jogo_atual["time_b"]]
                default_v_idx = opcoes_desempate.index(valor_antigo[2]) if valor_antigo[2] in opcoes_desempate else 0
                v_p = col_venc.selectbox(f"Se empate, avança:", opcoes_desempate, index=default_v_idx, key=f"v_p_{jogo_id_sel}_{part}")

                novos_palpites_temp.append({
                    "jogo_id": jogo_id_sel, "participante": part, "gols_a": p_a, "gols_b": p_b, "vencedor_empate": v_p
                })

            if st.form_submit_button("💾 Salvar Todos os Palpites Deste Jogo"):
                # Salva usando a função upsert (insere novo ou atualiza o existente se houver conflito de jogo_id e participante)
                supabase.table("palpites").upsert(novos_palpites_temp, on_conflict="jogo_id,participante").execute()
                carregar_dados_supabase()
                st.success("Todos os palpites foram guardados com sucesso no Supabase!")
                st.rerun()
    else:
        st.info("Cadastre participantes e certifique-se de que há jogos abertos para palpites.")
