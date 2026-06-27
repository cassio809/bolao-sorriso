import streamlit as st
import pandas as pd
import json
import os

# Configuração inicial da página
st.set_page_config(page_title="Bolão Copa 2026 - CLÍNICA SORRISO DE TODOS", layout="wide")
st.title("🏆 Bolão Mata-Mata - CLÍNICA SORRISO DE TODOS")

# --- LÓGICA DE PERSISTÊNCIA COM ARQUIVO JSON ---
ARQUIVO_DADOS = "dados_bolao.json"


def carregar_dados():
    """Carrega os dados do arquivo JSON ou cria o estado inicial se não existir."""
    if os.path.exists(ARQUIVO_DADOS):
        with open(ARQUIVO_DADOS, "r", encoding="utf-8") as f:
            dados = json.load(f)

            # O JSON não aceita tuplas como chaves, então convertemos de string para tupla (jogo_id, participante)
            palpites_convertidos = {}
            for k, v in dados.get("palpites", {}).items():
                jogo_id, part = k.split(",")
                # Garante compatibilidade caso o palpite antigo não tivesse o terceiro elemento (vencedor do empate)
                if len(v) == 2:
                    v = [v[0], v[1], ""]
                palpites_convertidos[(int(jogo_id), part)] = v
            dados["palpites"] = palpites_convertidos
            return dados
    else:
        return {
            "participantes": {"Cássio": 0, "Carol": 0, "Gabriel": 0},
            "jogos": [
                {"id": 1, "fase": "Oitavas", "time_a": "Alemanha", "time_b": "França", "gols_a_real": 0,
                 "gols_b_real": 0, "encerrado": False, "vencedor": ""},
                {"id": 2, "fase": "Oitavas", "time_a": "Brasil", "time_b": "Argentina", "gols_a_real": 0,
                 "gols_b_real": 0, "encerrado": False, "vencedor": ""}
            ],
            "palpites": {}
        }


def salvar_dados():
    """Salva o estado atual do st.session_state no arquivo JSON."""
    palpites_salvar = {}
    for (jogo_id, part), valores in st.session_state.palpites.items():
        palpites_salvar[f"{jogo_id},{part}"] = valores

    dados_para_salvar = {
        "participantes": st.session_state.participantes,
        "jogos": st.session_state.jogos,
        "palpites": palpites_salvar
    }

    with open(ARQUIVO_DADOS, "w", encoding="utf-8") as f:
        json.dump(dados_para_salvar, f, indent=4, ensure_ascii=False)


# Inicializa o session_state carregando do arquivo JSON definitivo
if 'dados_carregados' not in st.session_state:
    dados_iniciais = carregar_dados()
    st.session_state.participantes = dados_iniciais["participantes"]
    st.session_state.jogos = dados_iniciais["jogos"]
    st.session_state.palpites = dados_iniciais["palpites"]
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
                salvar_dados()
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
            salvar_dados()
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
            # Garante ID único baseado no maior ID existente para evitar conflitos após exclusões
            novo_id = max([j["id"] for j in st.session_state.jogos]) + 1 if st.session_state.jogos else 1
            st.session_state.jogos.append({
                "id": novo_id, "fase": fase, "time_a": t_a, "time_b": t_b,
                "gols_a_real": 0, "gols_b_real": 0, "encerrado": False, "vencedor": ""
            })
            salvar_dados()
            st.success(f"Jogo {t_a} x {t_b} criado!")
            st.rerun()

    st.subheader("Jogos Cadastrados")
    for idx, jogo in enumerate(st.session_state.jogos):
        status = "🔴 Aberto" if not jogo["encerrado"] else f"🟢 Encerrado (Vencedor: {jogo['vencedor']})"

        # Grid para o cabeçalho do jogo contendo o título e o botão de exclusão
        col_tit, col_del = st.columns([5, 1])
        col_tit.markdown(f"**Jogo #{jogo['id']} ({jogo['fase']})** - {status}")

        if col_del.button("🗑️ Excluir Jogo", key=f"del_jogo_{jogo['id']}", help="Remove permanentemente este jogo"):
            st.session_state.jogos.pop(idx)
            # Remove também os palpites atrelados a esse jogo para limpar o arquivo
            chaves_para_deletar = [k for k in st.session_state.palpites.keys() if k[0] == jogo['id']]
            for kh in chaves_para_deletar:
                del st.session_state.palpites[kh]
            salvar_dados()
            st.warning(f"Jogo #{jogo['id']} excluído com sucesso.")
            st.rerun()

        col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
        gols_a = col1.number_input(f"Gols {jogo['time_a']}", min_value=0, value=jogo['gols_a_real'],
                                   key=f"real_a_{jogo['id']}", disabled=jogo['encerrado'])
        gols_b = col2.number_input(f"Gols {jogo['time_b']}", min_value=0, value=jogo['gols_b_real'],
                                   key=f"real_b_{jogo['id']}", disabled=jogo['encerrado'])

        vencedor_opcoes = [jogo['time_a'], jogo['time_b']]

        # Tenta definir o índice padrão do selectbox do vencedor baseado no que já foi salvo
        default_venc_idx = 0
        if jogo['vencedor'] in vencedor_opcoes:
            default_venc_idx = vencedor_opcoes.index(jogo['vencedor'])

        vencedor_p = col3.selectbox("Quem avança?", vencedor_opcoes, index=default_venc_idx, key=f"venc_{jogo['id']}",
                                    disabled=jogo['encerrado'])

        if not jogo["encerrado"]:
            if col4.button("Encerrar Jogo e Rodar Pontos", key=f"btn_encerrar_{jogo['id']}"):
                st.session_state.jogos[idx]["gols_a_real"] = gols_a
                st.session_state.jogos[idx]["gols_b_real"] = gols_b
                st.session_state.jogos[idx]["encerrado"] = True
                st.session_state.jogos[idx]["vencedor"] = vencedor_p

                for part in st.session_state.participantes.keys():
                    chave_palpite = (jogo['id'], part)
                    if chave_palpite in st.session_state.palpites:
                        # Estrutura do palpite: [gols_a, gols_b, quem_avanca]
                        g_a_p, g_b_p, venc_palp = st.session_state.palpites[chave_palpite]
                        pontos_ganhos = calcular_pontos(g_a_p, g_b_p, gols_a, gols_b)

                        # Bônus ou validação extra se houver empate real e no palpite
                        # Se houver empate real e a pessoa acertou quem passa nos pênaltis, pode manter ou ajustar regras
                        st.session_state.participantes[part] += pontos_ganhos

                salvar_dados()
                st.success("Pontuações calculadas e salvas definitivamente!")
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

        # Encontra os dados do jogo selecionado para usar os nomes dos times
        jogo_atual = next(j for j in st.session_state.jogos if j["id"] == jogo_id_sel)

        with st.form(key=f"form_palpites_{jogo_id_sel}"):
            st.write("Digite os palpites da galera (Use TAB para navegar rápido):")
            novos_palpites_temp = {}

            for part in st.session_state.participantes.keys():
                col_nome, col_inp1, col_inp2, col_venc = st.columns([2, 1, 1, 2])
                col_nome.write(f"**{part}**")

                # Resgata valor antigo se já existir: [gols_a, gols_b, quem_avanca]
                valor_antigo = st.session_state.palpites.get((jogo_id_sel, part), [0, 0, jogo_atual["time_a"]])

                p_a = col_inp1.number_input(f"Gols {jogo_atual['time_a']}", min_value=0, value=int(valor_antigo[0]),
                                            key=f"p_a_{jogo_id_sel}_{part}")
                p_b = col_inp2.number_input(f"Gols {jogo_atual['time_b']}", min_value=0, value=int(valor_antigo[1]),
                                            key=f"p_b_{jogo_id_sel}_{part}")

                # Se der empate no palpite, define o dropdown de desempate ativo
                opcoes_desempate = [jogo_atual["time_a"], jogo_atual["time_b"]]
                default_v_idx = opcoes_desempate.index(valor_antigo[2]) if valor_antigo[2] in opcoes_desempate else 0

                v_p = col_venc.selectbox(f"Se empate, avança:", opcoes_desempate, index=default_v_idx,
                                         key=f"v_p_{jogo_id_sel}_{part}")

                novos_palpites_temp[(jogo_id_sel, part)] = [p_a, p_b, v_p]

            if st.form_submit_button("💾 Salvar Todos os Palpites Deste Jogo"):
                st.session_state.palpites.update(novos_palpites_temp)
                salvar_dados()
                st.success("Todos os palpites foram guardados no arquivo local!")
                st.rerun()
    else:
        st.info("Cadastre participantes e certifique-se de que há jogos abertos para palpites.")