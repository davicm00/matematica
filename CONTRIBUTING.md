# Como contribuir

Achou uma questão com erro, frase confusa ou quer sugerir novas? Ótimo!

1. **Erro em uma questão:** abra uma *Issue* com o código da questão (ex.: `SUB-042`), o que está errado e a correção sugerida.
2. **Novas questões:** edite `scripts/gerar_questoes.py` (veja [`docs/BANCO_DE_QUESTOES.md`](docs/BANCO_DE_QUESTOES.md)), rode `python3 scripts/gerar_questoes.py` e envie um *Pull Request* com o script **e** os arquivos gerados.
3. **Visual e funcionamento:** edite `modelos/*.html`, `css/style.css`, `js/app.js` ou `js/professor.js` e rode o gerador para montar de novo o `index.html` e o `professor.html` (não edite esses dois direto: eles são gerados). Teste no computador e no celular.

## Combinados

- Linguagem simples, positiva e adequada a crianças de 6 e 7 anos.
- Toda questão precisa de **dica** e **explicação**.
- Nada de dados pessoais, cadastro, propaganda ou rastreamento.
