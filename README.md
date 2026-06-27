# 🏆 Bolão Mata-Mata - Copa 2026

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![JSON](https://img.shields.io/badge/JSON-000000?style=for-the-badge&logo=json&logoColor=white)
![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)

> **Aplicação personalizada para a Clínica Sorriso de Todos acompanhar os jogos e palpites da Copa do Mundo 2026 de forma interativa e em tempo real!**

O sistema foi desenvolvido utilizando **Python** e **Streamlit** para fornecer uma interface web rápida, elegante e de fácil navegação para o gerenciamento de participantes, inserção de palpites de mata-mata e cálculo automatizado do ranking geral.

---

## 🚀 Funcionalidades

- **📊 Ranking Geral:** Tabela dinâmica que ordena os participantes automaticamente com base na pontuação acumulada.
- **👥 Gestão de Participantes:** Interface simples para adicionar ou remover competidores do bolão.
- **⚽ Controle de Confrontos:** Cadastro de novos jogos de mata-mata (2ª Fase, Oitavas, Quartas, Semifinal e Final), com opção para excluir partidas em caso de erro de digitação.
- **📝 Digitação Ágil de Palpites:** Tela otimizada por lote com os nomes dos times em evidência e navegação rápida via tecla `TAB`.
- **🥅 Critério de Desempate:** Dropdown exclusivo para os participantes escolherem quem avança de fase em caso de palpites de empate.
- **💾 Persistência de Dados:** Integração com arquivo local estruturado em `JSON` (`dados_bolao.json`), garantindo que nenhuma informação seja perdida caso o servidor reinicie.

---

## 🎯 Regras de Pontuação

O sistema calcula os pontos de cada rodada de forma automatizada seguindo os seguintes critérios:

| Condição do Palpite | Pontuação |
| :--- | :---: |
| **Acerto exato do placar** (Ex: Palpite 2x1 \| Resultado 2x1) | **25 pontos** |
| **Acerto do vencedor ou empate**, mas com placar incorreto | **10 pontos** |
| **Erro do vencedor**, mas acertou a quantidade de gols de um dos times | **5 pontos** |
| **Erro total** de vencedor e gols | **0 pontos** |
