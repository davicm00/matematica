# 🗃️ Banco de questões: formato e como criar novas

## Onde ficam as questões

| Arquivo | Para quê |
|---|---|
| `scripts/gerar_questoes.py` | **Fonte de verdade.** Todas as questões nascem aqui. |
| `js/questoes.js` | Banco no formato do site (gerado). É embutido dentro do `index.html` e do `professor.html`. |
| `index.html`, `professor.html` | Páginas finais (geradas a partir de `modelos/`), com CSS e JS embutidos. |
| `data/questoes.json` | Banco completo em JSON (gerado). |
| `data/questoes.csv` | Banco completo em planilha (gerado). |
| `docs/questoes/*.md` | Listas legíveis no GitHub, com gabarito (gerado). |

> Não edite os arquivos gerados à mão: eles são sobrescritos sempre que o script roda.

## Formato de uma questão

```json
{
  "id": "PRO-012",
  "tema": "problemas",
  "nivel": 2,
  "tipo": "numero",
  "enunciado": "Ana tinha 21 flores. Ganhou mais 3. Com quantas flores Ana ficou?",
  "resposta": 24,
  "dica": "Ganhar é juntar: use a adição.",
  "explicacao": "21 + 3 = 24 flores.",
  "bncc": "EF01MA08"
}
```

| Campo | Obrigatório | Descrição |
|---|---|---|
| `id` | sim | Sigla do tema + número (gerado automaticamente). |
| `tema` | sim | Um dos ids de `TEMAS` (`contagem`, `dezenas`, `comparar`, `adicao`, `subtracao`, `problemas`, `sequencias`, `parimpar`, `geometria`, `medidas`, `desafios`). |
| `nivel` | sim | `1` fácil, `2` médio, `3` desafio. |
| `tipo` | sim | `numero`, `multipla` ou `ordenar`. |
| `enunciado` | sim | A pergunta. Use `___` para a lacuna. |
| `visual` | não | Emojis mostrados em destaque (ex.: `🍎🍎🍎 ➕ 🍌🍌`). |
| `relogio` | não | `{"h": 3, "m": 30}` desenha um relógio de ponteiros. |
| `opcoes` | se `multipla` | Lista de textos. A resposta precisa estar na lista. |
| `itens` | se `ordenar` | Itens embaralhados que a criança vai tocar. |
| `resposta` | sim | Número (`numero`), texto (`multipla`) ou lista na ordem certa (`ordenar`). |
| `dica` | sim | Aparece no botão 💡 e depois do primeiro erro. |
| `explicacao` | sim | Aparece depois que a criança responde. |
| `bncc` | sim | Código(s) da habilidade. |

## Criar novas questões

### 1. Uma questão escrita à mão

Em qualquer função `tema_...` do script, chame `add(...)`:

```python
add("desafios", 3, "numero",
    "Uma galinha bota 2 ovos por dia. Quantos ovos ela bota em 4 dias?", 8,
    dica="Conte de 2 em 2.",
    explicacao="2 + 2 + 2 + 2 = 8 ovos.",
    bncc="EF01MA08")
```

Múltipla escolha:

```python
add("geometria", 1, "multipla", "Qual figura parece uma pizza inteira?", "círculo",
    opcoes=["círculo", "quadrado", "triângulo"],
    dica="Pense no formato da pizza.", explicacao="A pizza é redonda: círculo.", bncc="EF01MA14")
```

### 2. Um modelo que gera várias

Use um laço com números sorteados (`R.randint`). Exemplo que cria 10 questões:

```python
for _ in range(10):
    a, b = R.randint(2, 9), R.randint(2, 9)
    add("adicao", 2, "numero", f"Quanto é {a} + {b} + 10?", a + b + 10,
        dica="Some os pequenos e depois mais 10.",
        explicacao=f"{a} + {b} = {a + b}; {a + b} + 10 = {a + b + 10}.", bncc="EF01MA06")
```

### 3. Rodar o gerador

- **Windows:** dê dois cliques em `gerar_questoes.bat` (na pasta principal) ou, no Prompt de Comando aberto na pasta do projeto, digite:
  ```
  py scripts\gerar_questoes.py
  ```
- **Mac / Linux:**
  ```bash
  python3 scripts/gerar_questoes.py
  ```

Precisa do [Python 3.8 ou mais novo](https://www.python.org/downloads/) (no Windows, marque **“Add Python to PATH”** ao instalar). Não precisa instalar nenhuma biblioteca.

O script mostra o total por tema e por nível e termina com “Pronto!”. Se algo der errado, ele mostra a mensagem de erro e não fecha a janela. Ele também **confere** as questões: falha se uma resposta de múltipla escolha não estiver entre as opções, se houver opções repetidas ou se o total cair abaixo de 1.000. Questões idênticas são descartadas automaticamente.

A semente aleatória é fixa (`random.Random(2026)`), então o mesmo script gera sempre o mesmo banco. Mudar a semente sorteia números diferentes.

### 4. Criar um assunto novo

1. Acrescente o tema na lista `TEMAS` (id, sigla de 3 letras, nome, ícone, cor, BNCC).
2. Escreva uma função `tema_novo()` com as questões.
3. Inclua a função na lista dentro de `main()`.
4. Rode o gerador. O cartão aparece sozinho no site.

## Cuidados com a linguagem

- Frases curtas, uma ideia por frase.
- Palavras-chave em MAIÚSCULAS quando mudam o sentido (`MAIS`, `MENOS`, `ANTES`, `DEPOIS`, `MAIOR`).
- Concordância: o script usa `quant(g)` para escolher “Quantos/Quantas” conforme o gênero do objeto.
- Use o sinal de menos `−` (e não o hífen `-`) nas contas: fica mais legível e o leitor de voz entende.
