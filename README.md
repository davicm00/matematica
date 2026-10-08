# 🦉 Mundo dos Números

Site de **Matemática para o 1º ano do Ensino Fundamental** (crianças de 6 e 7 anos), com um banco de **1.627 questões** em 11 assuntos e 3 níveis de dificuldade.

Foi pensado para crianças com **raciocínio acima da média**: além das contas básicas, traz probleminhas de duas etapas, sequências, padrões, “pensei em um número”, balanças de frutas e charadas de lógica — sempre com linguagem de criança, dica e explicação em cada pergunta.

> Funciona 100% no navegador, sem servidor, sem cadastro e sem coletar dados. O progresso fica salvo só no aparelho da criança.

---

## ✨ O que tem no site

**Para a criança** (`index.html`)
- Escolhe o **nível** (🌱 Fácil, 🌿 Médio, 🌳 Desafio ou 🎲 Misturado) e o **assunto**.
- Rodadas de **10 perguntas**, priorizando as que ela ainda não viu.
- Três tipos de resposta: **teclado numérico** grande, **múltipla escolha** e **ordenar números** tocando neles.
- **Relógio de ponteiros** desenhado na tela para as questões de horas.
- Botão **🔊 Ouvir** — lê a pergunta em voz alta (ótimo para quem ainda está aprendendo a ler).
- Errou? Ganha uma **segunda chance com dica**. Errou de novo? Vê a resposta **explicada**.
- Estrelas ⭐, confete no final e lista de revisão das perguntas que errou.

**Para o professor e a família** (`professor.html`)
- Banco completo com **gabarito, dica e explicação**, filtrável por assunto, nível, tipo e busca.
- **Gerador de folhas para imprimir** (com gabarito na última página).
- Download do banco em **CSV** (abre no Excel/Google Planilhas) e **JSON**.

## 📚 Assuntos

| Assunto | Questões | BNCC (sugestão) |
|---|---:|---|
| 🔢 Contar e números | 204 | EF01MA01, EF01MA02, EF01MA04 |
| 🧱 Dezenas e unidades | 145 | EF01MA07 |
| ⚖️ Maior, menor ou igual | 110 | EF01MA03, EF01MA05 |
| ➕ Adição | 168 | EF01MA06, EF01MA08 |
| ➖ Subtração | 159 | EF01MA06, EF01MA08 |
| 🧩 Probleminhas | 207 | EF01MA08 |
| 🔁 Sequências e padrões | 164 | EF01MA09, EF01MA10 |
| ✌️ Par, ímpar, dobro e metade | 105 | EF01MA06, EF01MA08 |
| 🔷 Formas geométricas | 75 | EF01MA11 a EF01MA14 |
| ⏰ Tempo, calendário e dinheiro | 169 | EF01MA15 a EF01MA19 |
| 🧠 Desafios de lógica | 121 | EF01MA08, EF01MA10, EF01MA20 |
| **Total** | **1.627** | |

Tipos: 1.130 de resposta numérica, 467 de múltipla escolha e 30 de ordenar.
A lista completa, com respostas, está em [`docs/questoes/`](docs/questoes/README.md).

## 🚀 Como usar

**No computador, sem internet:** descompacte o `.zip` (botão direito → **Extrair tudo**) e dê dois cliques em `index.html`, dentro da pasta extraída. Abrir direto de dentro do `.zip` não funciona.

**Publicar de graça no GitHub Pages:** veja o passo a passo em [`docs/PUBLICAR_NO_GITHUB.md`](docs/PUBLICAR_NO_GITHUB.md). O endereço fica assim:
`https://SEU-USUARIO.github.io/mundo-dos-numeros/`

## 🗂️ Estrutura

```
mundo-dos-numeros/
├── index.html              ← site das crianças
├── professor.html          ← banco com gabarito + folhas para imprimir
├── css/style.css           ← visual (cores nas variáveis do topo)
├── js/
│   ├── questoes.js         ← banco de questões (gerado pelo script)
│   ├── comum.js            ← relógio, utilidades, memória local
│   ├── app.js              ← lógica do jogo
│   └── professor.js        ← lógica da área do professor
├── data/
│   ├── questoes.json       ← banco completo (JSON)
│   └── questoes.csv        ← banco completo (planilha, separador ;)
├── scripts/
│   └── gerar_questoes.py   ← gera todas as questões
├── gerar_questoes.bat      ← atalho para o Windows (dois cliques)
└── docs/
    ├── GUIA_DO_PROFESSOR.md
    ├── BANCO_DE_QUESTOES.md  ← formato das questões e como criar novas
    ├── PUBLICAR_NO_GITHUB.md
    └── questoes/             ← todas as questões por assunto, com gabarito
```

## 🛠️ Mudar ou criar questões

As questões são geradas por um script em Python:

- **Windows:** dê dois cliques em `gerar_questoes.bat` (na pasta principal) ou, no Prompt de Comando aberto na pasta do projeto, digite:
  ```
  py scripts\gerar_questoes.py
  ```
- **Mac / Linux:**
  ```bash
  python3 scripts/gerar_questoes.py
  ```

Precisa do [Python 3.8 ou mais novo](https://www.python.org/downloads/) (no Windows, marque **“Add Python to PATH”** ao instalar). Não precisa instalar nenhuma biblioteca.

Ele recria `js/questoes.js`, `data/questoes.json`, `data/questoes.csv` e `docs/questoes/`. Detalhes em [`docs/BANCO_DE_QUESTOES.md`](docs/BANCO_DE_QUESTOES.md).

## ❓ Problemas comuns

| O que acontece | Solução |
|---|---|
| Aparece um aviso vermelho “O site não carregou direito” | Descompacte o `.zip` e abra o `index.html` da pasta extraída. No GitHub, confira se a pasta `js/` foi enviada junto. |
| `python3` não é reconhecido (Windows) | Use `py scripts\gerar_questoes.py` ou dê dois cliques em `gerar_questoes.bat`. |
| “Python não encontrado” | Instale o Python em <https://www.python.org/downloads/> marcando **Add Python to PATH**. |
| O botão 🔊 não fala | O aparelho precisa ter uma voz em português instalada (configurações de acessibilidade / fala). |
| O GitHub Pages mostra o README em vez do site | O `index.html` precisa estar na raiz do repositório, não dentro de outra pasta. |

## 🎨 Mudar o visual

Todas as cores e fontes estão no início de `css/style.css`, em `:root`. A cor de cada assunto fica na lista `TEMAS` do script gerador.

## 🔒 Privacidade

O site não usa cookies, não tem login e não envia nada para nenhum servidor. Nome, estrelas e progresso ficam no `localStorage` do próprio navegador. As fontes são carregadas do Google Fonts; sem internet, o site usa fontes do sistema e continua funcionando.

## 📄 Licença

Código sob licença [MIT](LICENSE). Questões sob [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.pt_BR): pode usar, copiar e adaptar, inclusive em sala de aula, citando a fonte.
