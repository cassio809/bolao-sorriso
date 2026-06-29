# 🏆 Bolão Mata-Mata — Clínica Sorriso de Todos

Um sistema web dinâmico e responsivo desenvolvido em Python para gestão de palpites e pontuações do mata-mata da Copa do Mundo 2026. Projetado inicialmente para integrar e descontrair a equipe da **Clínica Sorriso de Todos**, o projeto utiliza uma arquitetura serverless moderna conectada diretamente a um banco de dados relacional na nuvem.

## 🚀 Tecnologias Utilizadas

* **[Python 3.14+](https://www.python.org/):** Linguagem base para desenvolvimento da lógica de negócio.
* **[Streamlit](https://streamlit.io/):** Framework web utilizado para construir a interface do utilizador de forma rápida, limpa e interativa.
* **[Supabase](https://supabase.com/):** Plataforma Backend-as-a-Service (BaaS) baseada em **PostgreSQL**, utilizada para persistência confiável de dados, substituindo integrações legadas e instáveis.
* **[Pandas](https://pandas.pydata.org/):** Biblioteca para manipulação de estruturas de dados e geração do ranking de participantes.

## 🛠️ Arquitetura e Estrutura do Banco de Dados

O ecossistema do banco de dados no Supabase é composto por três tabelas principais com relacionamentos de integridade referencial (`FOREIGN KEY` com ações `ON DELETE CASCADE`):

1.  **`participantes`:** Regista os jogadores do bolão e a soma de pontos.
2.  **`jogos`:** Armazena os confrontos, fases do torneio, resultados reais e o status da partida.
3.  **`palpites`:** Guarda os placares previstos por cada participante para cada jogo específico, garantindo um único palpite por participante/confronto.

## ✨ Funcionalidades Principais

* **📊 Ranking Geral:** Tabela classificativa atualizada em tempo real e ordenada de forma decrescente com base nas pontuações calculadas.
* **👥 Gestão de Participantes:** Interface CRUD simples para adicionar novos membros ao bolão ou remover participantes existentes.
* **⚽ Painel de Arbitragem:** Área administrativa dedicada a cadastrar novos jogos do mata-mata, introduzir resultados oficiais e encerrar partidas, disparando o gatilho de cálculo de pontos.
* **📝 Input Rápido de Palpites:** Formulário estruturado por jogo que permite preencher e atualizar os palpites de todos os jogadores rapidamente.

## 🧮 Regras de Pontuação

A distribuição de pontos segue critérios fixos após o encerramento oficial de cada partida:
* **Acerto em cheio do placar:** `25 pontos` .
* **Acerto do vencedor/empate:** `10 pontos` .
* **Acerto de gol isolado de uma das equipes:** `5 pontos` (Ex: Palpite 1x1, Placar Real 1x3 — acertou os golos de uma equipe).

