#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador do banco de questões do "Mundo dos Números" (Matemática, 1º ano EF).

Gera:
  - index.html e professor.html (com tudo embutido, via montar_site.py)
  - js/questoes.js      (usado pelo site; funciona até abrindo o index.html direto)
  - data/questoes.json  (banco completo em JSON)
  - data/questoes.csv   (banco completo em planilha)

Uso:
  Windows:      py scripts\\gerar_questoes.py   (ou dois cliques em gerar_questoes.bat)
  Mac/Linux:    python3 scripts/gerar_questoes.py

Precisa do Python 3.8 ou mais novo. Não usa nenhuma biblioteca extra.

O gerador é determinístico (semente fixa): rodar de novo produz o mesmo banco.
Para criar novas questões, edite as funções de cada tema abaixo.
"""
import csv
import json
import os
import random
import sys
import traceback

R = random.Random(2026)
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------------------
# Temas
# ---------------------------------------------------------------------------
TEMAS = [
    {"id": "contagem",   "sigla": "CON", "nome": "Contar e números",          "icone": "🔢", "cor": "#ff8a5c", "bncc": "EF01MA01, EF01MA02, EF01MA04"},
    {"id": "dezenas",    "sigla": "DEZ", "nome": "Dezenas e unidades",        "icone": "🧱", "cor": "#ffb84d", "bncc": "EF01MA07"},
    {"id": "comparar",   "sigla": "COM", "nome": "Maior, menor ou igual",     "icone": "⚖️", "cor": "#f7d046", "bncc": "EF01MA03, EF01MA05"},
    {"id": "adicao",     "sigla": "ADI", "nome": "Adição",                    "icone": "➕", "cor": "#7bd389", "bncc": "EF01MA06, EF01MA08"},
    {"id": "subtracao",  "sigla": "SUB", "nome": "Subtração",                 "icone": "➖", "cor": "#4fc3a1", "bncc": "EF01MA06, EF01MA08"},
    {"id": "problemas",  "sigla": "PRO", "nome": "Probleminhas",              "icone": "🧩", "cor": "#4db6e8", "bncc": "EF01MA08"},
    {"id": "sequencias", "sigla": "SEQ", "nome": "Sequências e padrões",      "icone": "🔁", "cor": "#6d8cf0", "bncc": "EF01MA09, EF01MA10"},
    {"id": "parimpar",   "sigla": "PAR", "nome": "Par, ímpar, dobro e metade","icone": "✌️", "cor": "#9b7be8", "bncc": "EF01MA06, EF01MA08"},
    {"id": "geometria",  "sigla": "GEO", "nome": "Formas geométricas",        "icone": "🔷", "cor": "#d47be0", "bncc": "EF01MA11, EF01MA12, EF01MA13, EF01MA14"},
    {"id": "medidas",    "sigla": "MED", "nome": "Tempo, calendário e dinheiro", "icone": "⏰", "cor": "#ef6f9a", "bncc": "EF01MA15, EF01MA16, EF01MA17, EF01MA18, EF01MA19"},
    {"id": "desafios",   "sigla": "DES", "nome": "Desafios de lógica",        "icone": "🧠", "cor": "#ff6b6b", "bncc": "EF01MA08, EF01MA10"},
]
SIGLA = {t["id"]: t["sigla"] for t in TEMAS}

Q = []
_vistos = set()


def add(tema, nivel, tipo, enunciado, resposta, opcoes=None, dica="", explicacao="",
        visual=None, relogio=None, itens=None, bncc="", ordem_fixa=False):
    """Adiciona uma questão ao banco (ignora duplicadas)."""
    chave = (tema, enunciado, visual, str(relogio), str(itens))
    if chave in _vistos:
        return False
    _vistos.add(chave)
    q = {"tema": tema, "nivel": nivel, "tipo": tipo, "enunciado": enunciado}
    if visual:
        q["visual"] = visual
    if relogio:
        q["relogio"] = relogio
    if tipo == "multipla":
        opcoes = [str(o) for o in opcoes]
        assert str(resposta) in opcoes, (enunciado, resposta, opcoes)
        assert len(set(opcoes)) == len(opcoes), (enunciado, opcoes)
        if not ordem_fixa:
            R.shuffle(opcoes)
        q["opcoes"] = opcoes
        q["resposta"] = str(resposta)
    elif tipo == "numero":
        q["resposta"] = int(resposta)
    elif tipo == "ordenar":
        q["itens"] = [str(i) for i in itens]
        q["resposta"] = [str(r) for r in resposta]
        assert sorted(q["itens"]) == sorted(q["resposta"])
    q["dica"] = dica
    q["explicacao"] = explicacao
    q["bncc"] = bncc
    Q.append(q)
    return True


def opcoes_num(correta, distratores, n=4, minimo=0):
    out = [str(correta)]
    for d in distratores:
        if isinstance(d, int) and d < minimo:
            continue
        if str(d) not in out and len(out) < n:
            out.append(str(d))
    k = 1
    while len(out) < n:  # completa se faltar
        for c in (correta + k, correta - k):
            if c >= minimo and str(c) not in out and len(out) < n:
                out.append(str(c))
        k += 1
    return out


def distr_num(c):
    base = [c + 1, c - 1, c + 10, c - 10, c + 2, c - 2]
    R.shuffle(base)
    return base


# ---------------------------------------------------------------------------
# Vocabulário
# ---------------------------------------------------------------------------
UNI = ["zero", "um", "dois", "três", "quatro", "cinco", "seis", "sete", "oito", "nove",
       "dez", "onze", "doze", "treze", "catorze", "quinze", "dezesseis", "dezessete",
       "dezoito", "dezenove"]
DEZ = ["", "", "vinte", "trinta", "quarenta", "cinquenta", "sessenta", "setenta",
       "oitenta", "noventa"]


def extenso(n):
    if n == 100:
        return "cem"
    if n < 20:
        return UNI[n]
    d, u = divmod(n, 10)
    return DEZ[d] if u == 0 else f"{DEZ[d]} e {UNI[u]}"


NOMES = ["Ana", "Pedro", "Lucas", "Júlia", "Miguel", "Laura", "Davi", "Helena",
         "Gabriel", "Alice", "Theo", "Sofia", "Bernardo", "Valentina", "Arthur",
         "Manuela", "Heitor", "Lorena", "Rafael", "Cecília", "Samuel", "Lívia",
         "Benício", "Isabela", "Enzo", "Maria"]

# (singular, plural, gênero)
OBJ = [("figurinha", "figurinhas", "f"), ("bala", "balas", "f"), ("lápis", "lápis", "m"),
       ("bolinha de gude", "bolinhas de gude", "f"), ("maçã", "maçãs", "f"),
       ("carrinho", "carrinhos", "m"), ("livro", "livros", "m"), ("adesivo", "adesivos", "m"),
       ("biscoito", "biscoitos", "m"), ("flor", "flores", "f"), ("pipa", "pipas", "f"),
       ("tampinha", "tampinhas", "f"), ("chiclete", "chicletes", "m"), ("concha", "conchas", "f"),
       ("botão", "botões", "m"), ("pirulito", "pirulitos", "m")]

EMOJIS = [("🍎", "maçãs", "f"), ("⭐", "estrelas", "f"), ("🐟", "peixinhos", "m"),
          ("🎈", "balões", "m"), ("🌸", "flores", "f"), ("🐞", "joaninhas", "f"),
          ("🚗", "carrinhos", "m"), ("🍓", "morangos", "m"), ("🐤", "pintinhos", "m"),
          ("⚽", "bolas", "f"), ("🦋", "borboletas", "f"), ("🍪", "biscoitos", "m")]


def quant(g):
    return "Quantas" if g == "f" else "Quantos"


def grupos(e, n, tam=5):
    blocos = [e * tam] * (n // tam)
    if n % tam:
        blocos.append(e * (n % tam))
    return " ".join(blocos)


def dois_nomes():
    a, b = R.sample(NOMES, 2)
    return a, b


# ---------------------------------------------------------------------------
# 1. Contar e números
# ---------------------------------------------------------------------------
def tema_contagem():
    T = "contagem"
    for e, nome, g in EMOJIS:
        for faixa, nivel in (((4, 10), 1), ((11, 20), 2), ((21, 32), 3)):
            for _ in range(2):
                n = R.randint(*faixa)
                dica = "Aponte com o dedo e conte um por um." if nivel == 1 else \
                    "Os desenhos estão em grupinhos de 5. Conte de 5 em 5 e depois o que sobrou!"
                exp = f"São {n} {nome}." if nivel == 1 else \
                    f"Há {n // 5} grupos de 5 ({n // 5 * 5}) e mais {n % 5}: {n // 5 * 5} + {n % 5} = {n}."
                add(T, nivel, "numero", f"{quant(g)} {nome} você vê?", n, visual=grupos(e, n),
                    dica=dica, explicacao=exp, bncc="EF01MA02")

    # sucessor / antecessor
    nums = list(range(9, 100))
    R.shuffle(nums)
    for n in nums[:30]:
        cruza = (n + 1) % 10 == 0
        nivel = 3 if cruza else (1 if n < 20 else 2)
        add(T, nivel, "numero", f"Qual número vem logo DEPOIS do {n}?", n + 1,
            dica="Conte para frente: qual é o próximo?",
            explicacao=f"Depois do {n} vem o {n + 1}." + (" Quando a unidade passa do 9, ganhamos mais uma dezena!" if cruza else ""),
            bncc="EF01MA04")
    R.shuffle(nums)
    for n in nums[:30]:
        if n < 11:
            continue
        cruza = n % 10 == 0
        nivel = 3 if cruza else (1 if n < 20 else 2)
        add(T, nivel, "numero", f"Qual número vem logo ANTES do {n}?", n - 1,
            dica="Conte para trás: qual número vem antes?",
            explicacao=f"Antes do {n} vem o {n - 1}." + (" Ao voltar do 0 na unidade, perdemos uma dezena e a unidade vira 9." if cruza else ""),
            bncc="EF01MA04")
    # entre
    for n in R.sample(range(12, 99), 15):
        add(T, 2 if n % 10 not in (0, 9) else 3, "numero", f"Qual número fica entre {n - 1} e {n + 1}?", n,
            dica="É o número que vem logo depois do primeiro.",
            explicacao=f"{n - 1}, {n}, {n + 1}. O número do meio é {n}.", bncc="EF01MA04")
    # por extenso -> número (múltipla)
    for n in R.sample(range(11, 100), 28):
        d, u = divmod(n, 10)
        inv = u * 10 + d
        dis = [inv if u != 0 and inv != n else n + 10, n + 1, n - 10 if n > 20 else n + 20, n - 1]
        add(T, 2 if n < 50 else 3, "multipla", f"Como se escreve o número {n} por extenso?",
            extenso(n), opcoes=[extenso(int(x)) for x in opcoes_num(n, dis, minimo=1) if int(x) <= 100],
            dica="Leia primeiro a dezena e depois a unidade.",
            explicacao=f"{n} = {d} dezenas e {u} unidades → “{extenso(n)}”.", bncc="EF01MA04")
    for n in R.sample(range(11, 100), 18):
        add(T, 2, "numero", f"Escreva com algarismos: “{extenso(n)}”.", n,
            dica="Quantas dezenas? Quantas unidades?",
            explicacao=f"“{extenso(n)}” é o número {n}.", bncc="EF01MA04")
    # quantos números
    fixas = [
        (3, "Contando de 1 até 10, quantos números você falou?", 10, "Conte nos dedos!", "1, 2, 3, 4, 5, 6, 7, 8, 9, 10: são 10 números."),
        (3, "Quantos números existem de 10 até 20, contando o 10 e o 20?", 11, "Cuidado: conte o 10 também!", "10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20: são 11 números."),
        (2, "Qual é o maior número que tem só um algarismo?", 9, "Os números de um algarismo vão do 0 ao 9.", "O 9 é o maior número com um só algarismo."),
        (2, "Qual é o menor número que tem dois algarismos?", 10, "Depois do 9 vem...", "O 10 é o primeiro número com dois algarismos."),
        (3, "Qual é o maior número que tem dois algarismos?", 99, "Pense no número que vem logo antes do 100.", "O 99 é o maior; depois dele vem o 100, que tem três algarismos."),
        (1, "Quantos dedos você tem nas duas mãos?", 10, "Conte os dedos de uma mão e depois da outra.", "5 + 5 = 10 dedos."),
        (2, "Quantos dedos têm 3 mãos?", 15, "Cada mão tem 5 dedos. Conte de 5 em 5.", "5, 10, 15: são 15 dedos."),
        (3, "Quantos dedos têm 4 pessoas, contando só as mãos?", 40, "Cada pessoa tem 10 dedos nas mãos.", "10, 20, 30, 40: são 40 dedos."),
    ]
    for nivel, enun, resp, dica, exp in fixas:
        add(T, nivel, "numero", enun, resp, dica=dica, explicacao=exp, bncc="EF01MA02")
    # posição ordinal
    for nome in NOMES[:10]:
        p = R.randint(2, 6)
        atras = R.randint(2, 6)
        add(T, 3, "numero", f"Numa fila, {nome} é a {p}ª criança e ainda há {atras} crianças atrás. Quantas crianças há na fila?",
            p + atras, dica="Desenhe bolinhas para a fila!",
            explicacao=f"Até {nome} são {p} crianças. Depois vêm mais {atras}: {p} + {atras} = {p + atras}.", bncc="EF01MA01")


# ---------------------------------------------------------------------------
# 2. Dezenas e unidades
# ---------------------------------------------------------------------------
def du_txt(d, u):
    sd = "dezena" if d == 1 else "dezenas"
    su = "unidade" if u == 1 else "unidades"
    return f"{d} {sd} e {u} {su}"


def tema_dezenas():
    T = "dezenas"
    for n in R.sample([x for x in range(11, 100) if x % 10 and x % 11], 30):
        d, u = divmod(n, 10)
        dis = [du_txt(u, d), du_txt(d, d), du_txt(u, u), du_txt(d + 1 if d < 9 else d - 1, u)]
        op = [du_txt(d, u)]
        for x in dis:
            if x not in op and len(op) < 4:
                op.append(x)
        add(T, 1 if n < 40 else 2, "multipla", f"Quantas dezenas e unidades tem o número {n}?", du_txt(d, u), opcoes=op,
            dica="O algarismo da esquerda mostra as dezenas.",
            explicacao=f"{n} = {d * 10} + {u}, ou seja, {du_txt(d, u)}.", bncc="EF01MA07")
    for n in R.sample(range(11, 100), 30):
        d, u = divmod(n, 10)
        add(T, 1 if n < 50 else 2, "numero", f"{du_txt(d, u).capitalize()} formam qual número?", n,
            dica="Cada dezena vale 10.",
            explicacao=f"{d} dezenas = {d * 10}; {d * 10} + {u} = {n}.", bncc="EF01MA07")
    for d in range(1, 10):
        add(T, 1, "numero", f"Quantas dezenas tem o número {d * 10}?", d,
            dica="Conte de 10 em 10 até chegar nele.", explicacao=f"{d * 10} = {d} × 10, então são {d} dezenas.", bncc="EF01MA07")
    # dezena "estourada"
    for _ in range(25):
        d = R.randint(1, 6)
        u = R.randint(10, 19)
        add(T, 3, "numero", f"{d} dezenas e {u} unidades formam qual número?", d * 10 + u,
            dica=f"{u} unidades = 1 dezena e {u - 10} unidades.",
            explicacao=f"{d * 10} + {u} = {d * 10 + u}.", bncc="EF01MA07")
    for n in R.sample(range(21, 100), 18):
        d, u = divmod(n, 10)
        if R.random() < 0.5:
            add(T, 2, "numero", f"Qual é o algarismo das DEZENAS no número {n}?", d,
                dica="É o algarismo da esquerda.", explicacao=f"Em {n}, o {d} está na casa das dezenas.", bncc="EF01MA07")
        else:
            add(T, 2, "numero", f"Qual é o algarismo das UNIDADES no número {n}?", u,
                dica="É o algarismo da direita.", explicacao=f"Em {n}, o {u} está na casa das unidades.", bncc="EF01MA07")
    for n in R.sample([x for x in range(23, 99) if x % 10], 15):
        d, u = divmod(n, 10)
        add(T, 3, "numero", f"Quanto vale o algarismo {d} no número {n}?", d * 10,
            dica="Ele está na casa das dezenas.", explicacao=f"O {d} está nas dezenas, então vale {d * 10}.", bncc="EF01MA07")
    # decomposição
    for n in R.sample([x for x in range(21, 100) if x % 10], 15):
        d, u = divmod(n, 10)
        add(T, 2, "numero", f"Complete: {n} = {d * 10} + ___", u,
            dica="Quanto falta para chegar ao número?", explicacao=f"{d * 10} + {u} = {n}.", bncc="EF01MA07")
    fixas = [
        (1, "Uma dezena tem quantas unidades?", 10, "Pense no número 10.", "1 dezena = 10 unidades."),
        (2, "Meia dezena tem quantas unidades?", 5, "Meia é a metade.", "A metade de 10 é 5."),
        (2, "Quantas unidades têm 3 dezenas?", 30, "Conte de 10 em 10.", "10, 20, 30."),
        (3, "Quantas dezenas cabem em 100?", 10, "Conte de 10 em 10 até 100.", "10, 20, 30... 100: são 10 dezenas."),
        (3, "Tenho 4 pacotes com 10 balas e mais 7 balas soltas. Quantas balas tenho?", 47, "Cada pacote é uma dezena.", "4 dezenas e 7 unidades = 47."),
        (3, "Ana tem 26 lápis. Quantas caixas de 10 lápis ela consegue encher?", 2, "Quantas dezenas há em 26?", "26 = 2 dezenas e 6 unidades: ela enche 2 caixas e sobram 6."),
        (3, "Com 35 ovos, quantas caixas de 10 ovos consigo encher completamente?", 3, "Quantas dezenas inteiras há em 35?", "35 = 3 dezenas e 5 unidades: 3 caixas cheias."),
    ]
    for nivel, enun, resp, dica, exp in fixas:
        add(T, nivel, "numero", enun, resp, dica=dica, explicacao=exp, bncc="EF01MA07")


# ---------------------------------------------------------------------------
# 3. Comparar
# ---------------------------------------------------------------------------
SINAIS = ["<", ">", "="]


def sinal(a, b):
    return ">" if a > b else "<" if a < b else "="


def tema_comparar():
    T = "comparar"
    exp_sinal = "A boquinha do sinal sempre abre para o número MAIOR."
    for i in range(36):
        lim = 20 if i % 2 == 0 else 99
        a = R.randint(1, lim)
        b = a if R.random() < 0.12 else R.randint(1, lim)
        if R.random() < 0.3 and a > 10:
            b = (a % 10) * 10 + a // 10 or b  # números “invertidos” (34 e 43)
        nivel = 1 if max(a, b) < 20 else 2
        add(T, nivel, "multipla", f"Qual sinal completa?  {a} ___ {b}", sinal(a, b), opcoes=SINAIS, ordem_fixa=True,
            dica="Compare primeiro as dezenas.", explicacao=f"{a} {sinal(a, b)} {b}. {exp_sinal}", bncc="EF01MA05")
    for _ in range(25):
        a, b = R.randint(1, 12), R.randint(1, 12)
        c = a + b + R.choice([-2, -1, 0, 0, 1, 2])
        add(T, 2, "multipla", f"Qual sinal completa?  {a} + {b} ___ {c}", sinal(a + b, c), opcoes=SINAIS, ordem_fixa=True,
            dica="Resolva a conta primeiro.", explicacao=f"{a} + {b} = {a + b}, e {a + b} {sinal(a + b, c)} {c}.", bncc="EF01MA05")
    for _ in range(18):
        a, b, c, d = [R.randint(2, 10) for _ in range(4)]
        if a + b == c + d and R.random() < 0.5:
            d += 1
        add(T, 3, "multipla", f"Qual sinal completa?  {a} + {b} ___ {c} + {d}", sinal(a + b, c + d), opcoes=SINAIS, ordem_fixa=True,
            dica="Resolva as duas contas e compare os resultados.",
            explicacao=f"{a} + {b} = {a + b} e {c} + {d} = {c + d}. Então {a + b} {sinal(a + b, c + d)} {c + d}.", bncc="EF01MA05")
    for _ in range(20):
        base = R.randint(1, 8)
        ns = R.sample(range(base * 10, min(base * 10 + 25, 100)), 4)
        add(T, 1 if max(ns) < 20 else 2, "multipla", "Qual é o MAIOR número?", max(ns), opcoes=ns,
            dica="Olhe primeiro as dezenas; se forem iguais, olhe as unidades.",
            explicacao=f"Em ordem: {', '.join(map(str, sorted(ns)))}. O maior é {max(ns)}.", bncc="EF01MA05")
    for _ in range(18):
        base = R.randint(1, 8)
        ns = R.sample(range(base * 10, min(base * 10 + 25, 100)), 4)
        add(T, 1 if max(ns) < 20 else 2, "multipla", "Qual é o MENOR número?", min(ns), opcoes=ns,
            dica="Olhe primeiro as dezenas; se forem iguais, olhe as unidades.",
            explicacao=f"Em ordem: {', '.join(map(str, sorted(ns)))}. O menor é {min(ns)}.", bncc="EF01MA05")
    # quem tem mais
    for _ in range(14):
        a, b = dois_nomes()
        s, p, g = R.choice(OBJ)
        x, y = R.sample(range(8, 60), 2)
        add(T, 2, "multipla", f"{a} tem {x} {p}. {b} tem {y} {p}. Quem tem MAIS {p}?",
            a if x > y else b, opcoes=[a, b], ordem_fixa=True,
            dica="Compare os dois números.", explicacao=f"{max(x, y)} é maior que {min(x, y)}.", bncc="EF01MA05")
    # verdadeiro ou falso
    for _ in range(15):
        a = R.randint(10, 99)
        b = R.randint(10, 99)
        s = R.choice(["<", ">"])
        verd = (a < b) if s == "<" else (a > b)
        add(T, 2, "multipla", f"Verdadeiro ou falso?  {a} {s} {b}", "Verdadeiro" if verd else "Falso",
            opcoes=["Verdadeiro", "Falso"], ordem_fixa=True,
            dica=exp_sinal, explicacao=f"O certo é {a} {sinal(a, b)} {b}.", bncc="EF01MA05")


# ---------------------------------------------------------------------------
# 4. Adição
# ---------------------------------------------------------------------------
def tema_adicao():
    T = "adicao"
    pares = [(a, b) for a in range(1, 10) for b in range(1, 10) if a + b <= 10]
    R.shuffle(pares)
    for a, b in pares[:28]:
        tipo = "multipla" if R.random() < 0.35 else "numero"
        kw = dict(opcoes=opcoes_num(a + b, distr_num(a + b), minimo=0)) if tipo == "multipla" else {}
        add(T, 1, tipo, f"Quanto é {a} + {b}?", a + b, dica="Guarde o maior número na cabeça e conte para frente nos dedos.",
            explicacao=f"{a} + {b} = {a + b}.", bncc="EF01MA06", **kw)
    # visual
    for _ in range(16):
        (e1, n1, _g1), (e2, n2, _g2) = R.sample(EMOJIS, 2)
        a, b = R.randint(2, 8), R.randint(2, 8)
        add(T, 1, "numero", "Quantos desenhos há ao todo?", a + b, visual=f"{e1 * a}  ➕  {e2 * b}",
            dica="Conte os primeiros e continue contando os outros.",
            explicacao=f"{a} {n1} + {b} {n2} = {a + b}.", bncc="EF01MA06")
    pares = [(a, b) for a in range(2, 13) for b in range(2, 13) if 11 <= a + b <= 20]
    R.shuffle(pares)
    for a, b in pares[:34]:
        tipo = "multipla" if R.random() < 0.3 else "numero"
        kw = dict(opcoes=opcoes_num(a + b, distr_num(a + b))) if tipo == "multipla" else {}
        falta = 10 - max(a, b)
        dica = f"Complete o 10: {max(a, b)} + {falta} = 10 e depois some o resto." if 0 < falta < min(a, b) else "Comece pelo número maior e conte para frente."
        add(T, 2, tipo, f"Quanto é {a} + {b}?", a + b, dica=dica, explicacao=f"{a} + {b} = {a + b}.", bncc="EF01MA06", **kw)
    # dezenas exatas
    for _ in range(12):
        a, b = R.randint(1, 6) * 10, R.randint(1, 3) * 10
        add(T, 2, "numero", f"Quanto é {a} + {b}?", a + b, dica="Some as dezenas como se fossem unidades: 3 + 2 = 5 → 30 + 20 = 50.",
            explicacao=f"{a // 10} dezenas + {b // 10} dezenas = {(a + b) // 10} dezenas = {a + b}.", bncc="EF01MA06")
    # dois dígitos sem reserva
    for _ in range(20):
        a = R.randint(11, 60)
        b = R.randint(1, 30)
        if a % 10 + b % 10 >= 10:
            continue
        add(T, 3, "numero", f"Quanto é {a} + {b}?", a + b, dica="Some unidades com unidades e dezenas com dezenas.",
            explicacao=f"Unidades: {a % 10} + {b % 10} = {a % 10 + b % 10}. Dezenas: {a // 10} + {b // 10} = {a // 10 + b // 10}. Resultado: {a + b}.", bncc="EF01MA06")
    # com reserva (desafio)
    for _ in range(16):
        a = R.randint(15, 59)
        b = R.randint(5, 9)
        if a % 10 + b < 10:
            continue
        falta = 10 - a % 10
        add(T, 3, "numero", f"Quanto é {a} + {b}?", a + b, dica=f"Primeiro chegue na dezena: {a} + {falta} = {a + falta}.",
            explicacao=f"{a} + {falta} = {a + falta}; ainda faltam {b - falta}: {a + falta} + {b - falta} = {a + b}.", bncc="EF01MA06")
    # parcela faltando
    for _ in range(24):
        a = R.randint(2, 12)
        s = R.randint(a + 1, 20)
        b = s - a
        if R.random() < 0.5:
            enun = f"Complete: {a} + ___ = {s}"
        else:
            enun = f"Complete: ___ + {a} = {s}"
        add(T, 2 if s <= 12 else 3, "numero", enun, b, dica=f"Comece no {a} e conte até chegar no {s}.",
            explicacao=f"{a} + {b} = {s}.", bncc="EF01MA06")
    # três parcelas
    for _ in range(18):
        a, b, c = R.randint(1, 9), R.randint(1, 9), R.randint(1, 9)
        if a + b + c > 20:
            continue
        dica = "Procure dois números que juntos dão 10!" if 10 in (a + b, a + c, b + c) else "Some os dois primeiros e depois some o terceiro."
        add(T, 2 if a + b + c <= 15 else 3, "numero", f"Quanto é {a} + {b} + {c}?", a + b + c, dica=dica,
            explicacao=f"{a} + {b} = {a + b}; {a + b} + {c} = {a + b + c}.", bncc="EF01MA06")
    # amigos do 10
    for a in range(1, 10):
        add(T, 1, "numero", f"Amigos do 10: {a} + ___ = 10", 10 - a, dica="Use os dedos: levante quantos já tem e conte os que faltam.",
            explicacao=f"{a} + {10 - a} = 10.", bncc="EF01MA06")
    # qual conta dá
    for _ in range(14):
        alvo = R.randint(7, 18)
        a = R.randint(1, alvo - 1)
        certa = f"{a} + {alvo - a}"
        erradas = []
        while len(erradas) < 3:
            x, y = R.randint(1, 12), R.randint(1, 12)
            if x + y != alvo and f"{x} + {y}" not in erradas:
                erradas.append(f"{x} + {y}")
        add(T, 2, "multipla", f"Qual destas contas dá {alvo}?", certa, opcoes=[certa] + erradas,
            dica="Resolva cada conta.", explicacao=f"{certa} = {alvo}.", bncc="EF01MA06")
    # dobros vizinhos
    for a in range(3, 10):
        add(T, 3, "numero", f"Se {a} + {a} = {2 * a}, quanto é {a} + {a + 1}?", 2 * a + 1,
            dica="É só um a mais!", explicacao=f"{a} + {a + 1} é 1 a mais que {a} + {a}: {2 * a} + 1 = {2 * a + 1}.", bncc="EF01MA06")


# ---------------------------------------------------------------------------
# 5. Subtração
# ---------------------------------------------------------------------------
def tema_subtracao():
    T = "subtracao"
    pares = [(a, b) for a in range(2, 11) for b in range(1, a + 1)]
    R.shuffle(pares)
    for a, b in pares[:28]:
        tipo = "multipla" if R.random() < 0.35 else "numero"
        kw = dict(opcoes=opcoes_num(a - b, distr_num(a - b), minimo=0)) if tipo == "multipla" else {}
        add(T, 1, tipo, f"Quanto é {a} − {b}?", a - b, dica=f"Levante {a} dedos e abaixe {b}.",
            explicacao=f"{a} − {b} = {a - b}.", bncc="EF01MA06", **kw)
    for _ in range(14):
        e, nome, g = R.choice(EMOJIS)
        a = R.randint(5, 12)
        b = R.randint(1, a - 1)
        add(T, 1, "numero", f"Havia {a} desenhos. {b} foram embora (riscados). {quant(g)} {nome} ficaram?", a - b,
            visual=f"{e * (a - b)}{'❌' * b}", dica="Conte só os que não estão riscados.",
            explicacao=f"{a} − {b} = {a - b}.", bncc="EF01MA06")
    pares = [(a, b) for a in range(11, 21) for b in range(2, 11) if a - b >= 1]
    R.shuffle(pares)
    for a, b in pares[:34]:
        tipo = "multipla" if R.random() < 0.3 else "numero"
        kw = dict(opcoes=opcoes_num(a - b, distr_num(a - b), minimo=0)) if tipo == "multipla" else {}
        dica = f"Volte até o 10 primeiro: {a} − {a - 10} = 10." if b > a - 10 else "Tire das unidades."
        add(T, 2, tipo, f"Quanto é {a} − {b}?", a - b, dica=dica, explicacao=f"{a} − {b} = {a - b}.", bncc="EF01MA06", **kw)
    for _ in range(12):
        a = R.randint(4, 9) * 10
        b = R.randint(1, a // 10 - 1) * 10
        add(T, 2, "numero", f"Quanto é {a} − {b}?", a - b, dica="Pense em dezenas: 7 − 3 = 4, então 70 − 30 = 40.",
            explicacao=f"{a // 10} dezenas − {b // 10} dezenas = {(a - b) // 10} dezenas = {a - b}.", bncc="EF01MA06")
    for _ in range(22):
        a = R.randint(25, 99)
        b = R.randint(1, a - 10)
        if b % 10 > a % 10 or b > 40:
            continue
        add(T, 3, "numero", f"Quanto é {a} − {b}?", a - b, dica="Tire unidades das unidades e dezenas das dezenas.",
            explicacao=f"Unidades: {a % 10} − {b % 10} = {a % 10 - b % 10}. Dezenas: {a // 10} − {b // 10} = {a // 10 - b // 10}. Resultado: {a - b}.", bncc="EF01MA06")
    for _ in range(14):
        a = R.randint(21, 52)
        b = R.randint(3, 9)
        if b <= a % 10:
            continue
        u = a % 10
        add(T, 3, "numero", f"Quanto é {a} − {b}?", a - b,
            dica=f"Primeiro volte até a dezena: {a} − {u} = {a - u}." if u else "Volte uma dezena.",
            explicacao=f"{a} − {u} = {a - u}; ainda faltam tirar {b - u}: {a - u} − {b - u} = {a - b}.", bncc="EF01MA06")
    for _ in range(24):
        a = R.randint(6, 20)
        b = R.randint(1, a - 1)
        enun = f"Complete: {a} − ___ = {a - b}" if R.random() < 0.6 else f"Complete: ___ − {b} = {a - b}"
        resp = b if enun.startswith(f"Complete: {a}") else a
        add(T, 2 if a <= 12 else 3, "numero", enun, resp, dica="Use a adição para conferir!",
            explicacao=f"{a} − {b} = {a - b}. Confira: {a - b} + {b} = {a}.", bncc="EF01MA06")
    for _ in range(14):
        alvo = R.randint(3, 12)
        a = R.randint(alvo + 1, 20)
        certa = f"{a} − {a - alvo}"
        erradas = []
        while len(erradas) < 3:
            x = R.randint(5, 20)
            y = R.randint(1, x)
            if x - y != alvo and f"{x} − {y}" not in erradas:
                erradas.append(f"{x} − {y}")
        add(T, 2, "multipla", f"Qual destas contas dá {alvo}?", certa, opcoes=[certa] + erradas,
            dica="Resolva cada conta.", explicacao=f"{certa} = {alvo}.", bncc="EF01MA06")
    for _ in range(12):
        a, b = R.randint(5, 9), R.randint(5, 9)
        s = a + b
        add(T, 3, "numero", f"Se {a} + {b} = {s}, quanto é {s} − {b}?", a,
            dica="A subtração desfaz a adição!", explicacao=f"Se {a} + {b} = {s}, então {s} − {b} = {a}.", bncc="EF01MA06")
    for _ in range(8):
        n = R.randint(3, 50)
        add(T, 1, "numero", f"Quanto é {n} − {n}?", 0, dica="Se eu tiro tudo, sobra...",
            explicacao="Quando tiramos tudo o que temos, sobra zero.", bncc="EF01MA06")
        m = R.randint(3, 50)
        add(T, 1, "numero", f"Quanto é {m} − 0?", m, dica="Se eu não tiro nada...",
            explicacao=f"Tirar zero não muda nada: continua {m}.", bncc="EF01MA06")


# ---------------------------------------------------------------------------
# 6. Probleminhas
# ---------------------------------------------------------------------------
def tema_problemas():
    T = "problemas"
    B = "EF01MA08"
    for _ in range(26):  # juntar / ganhar
        a = dois_nomes()[0]
        s, p, g = R.choice(OBJ)
        x, y = R.randint(3, 25), R.randint(2, 15)
        if x + y > 40:
            continue
        add(T, 1 if x + y <= 15 else 2, "numero", f"{a} tinha {x} {p}. Ganhou mais {y}. Com {quant(g).lower()} {p} {a} ficou?", x + y,
            dica="Ganhar é juntar: use a adição.", explicacao=f"{x} + {y} = {x + y} {p}.", bncc=B)
    for _ in range(26):  # tirar
        a, b = dois_nomes()
        s, p, g = R.choice(OBJ)
        x = R.randint(6, 35)
        y = R.randint(2, min(x - 1, 15))
        add(T, 1 if x <= 15 else 2, "numero", f"{a} tinha {x} {p} e deu {y} para {b}. Com {quant(g).lower()} {p} {a} ficou?", x - y,
            dica="Dar é tirar: use a subtração.", explicacao=f"{x} − {y} = {x - y} {p}.", bncc=B)
    for _ in range(22):  # comparar
        a, b = dois_nomes()
        s, p, g = R.choice(OBJ)
        x, y = R.sample(range(4, 30), 2)
        if x < y:
            x, y = y, x
        add(T, 3, "numero", f"{a} tem {x} {p} e {b} tem {y}. {quant(g)} {p} {a} tem A MAIS que {b}?", x - y,
            dica=f"Quanto falta para {y} chegar em {x}?", explicacao=f"{x} − {y} = {x - y}. {a} tem {x - y} a mais.", bncc=B)
    for _ in range(20):  # completar
        a = dois_nomes()[0]
        s, p, g = R.choice(OBJ)
        meta = R.randint(10, 30)
        tem = R.randint(3, meta - 2)
        add(T, 2 if meta <= 15 else 3, "numero", f"{a} quer juntar {meta} {p}. Já tem {tem}. {quant(g)} ainda faltam?", meta - tem,
            dica=f"Conte do {tem} até o {meta}.", explicacao=f"{tem} + {meta - tem} = {meta}. Faltam {meta - tem}.", bncc=B)
    for _ in range(22):  # dois passos
        a, b = dois_nomes()
        s, p, g = R.choice(OBJ)
        x, y = R.randint(5, 20), R.randint(2, 10)
        z = R.randint(2, x + y - 1)
        add(T, 3, "numero", f"{a} tinha {x} {p}. Ganhou {y} de {b} e depois perdeu {z}. Com {quant(g).lower()} {p} ficou?", x + y - z,
            dica="Faça uma parte de cada vez: primeiro o que ganhou, depois o que perdeu.",
            explicacao=f"{x} + {y} = {x + y}; {x + y} − {z} = {x + y - z}.", bncc=B)
    # grupos iguais (ideia de multiplicação)
    recipientes = [("prato", "pratos"), ("caixa", "caixas"), ("saquinho", "saquinhos"), ("pote", "potes")]
    for _ in range(18):
        r1, r2 = R.choice(recipientes)
        s, p, g = R.choice(OBJ)
        k, n = R.randint(2, 5), R.randint(2, 5)
        add(T, 3, "numero", f"Há {k} {r2} com {n} {p} em cada. {quant(g)} {p} há ao todo?", k * n,
            dica=f"Some {n} várias vezes: uma vez para cada {r1}.",
            explicacao=f"{' + '.join([str(n)] * k)} = {k * n}.", bncc=B)
    # divisão justa
    for _ in range(14):
        s, p, g = R.choice(OBJ)
        k = R.randint(2, 4)
        n = R.randint(2, 5)
        add(T, 3, "numero", f"{k * n} {p} foram divididos igualmente entre {k} crianças. {quant(g)} {p} cada uma ganhou?".replace("divididos", "divididas" if g == "f" else "divididos"),
            n, dica="Distribua um para cada criança, de novo e de novo, até acabar.",
            explicacao=f"{' + '.join([str(n)] * k)} = {k * n}, então cada criança ganhou {n}.", bncc=B)
    # patas e rodas
    seres = [("cachorro", "cachorros", 4, "patas"), ("galinha", "galinhas", 2, "patas"), ("gato", "gatos", 4, "patas"),
             ("pato", "patos", 2, "patas"), ("bicicleta", "bicicletas", 2, "rodas"), ("carro", "carros", 4, "rodas"),
             ("triciclo", "triciclos", 3, "rodas"), ("aranha", "aranhas", 8, "patas"), ("joaninha", "joaninhas", 6, "patas")]
    for s1, p1, k, parte in seres:
        for n in (2, 3):
            if k * n > 24:
                continue
            add(T, 3, "numero", f"Um(a) {s1} tem {k} {parte}. Quantas {parte} têm {n} {p1}?".replace("Um(a) ", "Uma " if s1 in ("galinha", "bicicleta", "aranha", "joaninha") else "Um "),
                k * n, dica="Desenhe e conte!", explicacao=f"{' + '.join([str(k)] * n)} = {k * n} {parte}.", bncc=B)
    # sala de aula
    for _ in range(12):
        m, f = R.randint(8, 15), R.randint(8, 15)
        add(T, 2, "numero", f"Numa sala há {m} meninos e {f} meninas. Quantas crianças há na sala?", m + f,
            dica="Junte os meninos e as meninas.", explicacao=f"{m} + {f} = {m + f} crianças.", bncc=B)
        total = m + f
        faltou = R.randint(2, 6)
        add(T, 2, "numero", f"Numa turma de {total} alunos, {faltou} faltaram hoje. Quantos alunos vieram?", total - faltou,
            dica="Tire os que faltaram.", explicacao=f"{total} − {faltou} = {total - faltou} alunos.", bncc=B)
    # ônibus
    for _ in range(10):
        a, sobe, desce = R.randint(5, 20), R.randint(2, 9), R.randint(2, 9)
        add(T, 3, "numero", f"Um ônibus tinha {a} passageiros. No ponto, {sobe} subiram e {desce} desceram. Quantos passageiros há agora?",
            a + sobe - desce, dica="Quem sobe, soma. Quem desce, tira.",
            explicacao=f"{a} + {sobe} = {a + sobe}; {a + sobe} − {desce} = {a + sobe - desce}.", bncc=B)
    # escolha da operação
    for _ in range(12):
        a, b = dois_nomes()
        s, p, g = R.choice(OBJ)
        x, y = R.randint(8, 20), R.randint(2, 7)
        if R.random() < 0.5:
            enun, cert = f"{a} tinha {x} {p} e ganhou {y}. Qual conta mostra com quantas ficou?", f"{x} + {y}"
        else:
            enun, cert = f"{a} tinha {x} {p} e perdeu {y}. Qual conta mostra com quantas ficou?", f"{x} − {y}"
        op = [f"{x} + {y}", f"{x} − {y}", f"{y} − {x}" if y != x else f"{x} + {x}", f"{y} + {y}"]
        add(T, 2, "multipla", enun, cert, opcoes=op, dica="Ganhar aumenta; perder diminui.",
            explicacao=f"A conta certa é {cert}.", bncc=B)


# ---------------------------------------------------------------------------
# 7. Sequências e padrões
# ---------------------------------------------------------------------------
def tema_sequencias():
    T = "sequencias"
    configs = [(1, 1, 30), (2, 2, 40), (5, 2, 80), (10, 1, 90), (3, 3, 40), (4, 3, 50)]
    for passo, nivel, lim in configs:
        for _ in range(9):
            ini = R.randint(0, lim - passo * 5)
            if passo == 10:
                ini = R.randint(0, 4) * 10 + R.choice([0, 0, 3, 5])
            seq = [ini + passo * i for i in range(6)]
            if seq[-1] > 100:
                continue
            pos = R.randint(2, 5)
            vis = [str(v) if i != pos else "___" for i, v in enumerate(seq)]
            add(T, nivel, "numero", f"Complete a sequência: {', '.join(vis)}", seq[pos],
                dica="Veja quanto aumenta de um número para o outro.",
                explicacao=f"A sequência aumenta de {passo} em {passo}: {', '.join(map(str, seq))}.", bncc="EF01MA10")
    for passo, nivel in ((1, 1), (2, 2), (5, 2), (10, 2), (3, 3)):
        for _ in range(6):
            ini = R.randint(passo * 6, 60)
            seq = [ini - passo * i for i in range(6)]
            if seq[-1] < 0:
                continue
            pos = R.randint(2, 5)
            vis = [str(v) if i != pos else "___" for i, v in enumerate(seq)]
            add(T, nivel, "numero", f"Complete a sequência: {', '.join(vis)}", seq[pos],
                dica="Os números estão diminuindo. De quanto em quanto?",
                explicacao=f"A sequência diminui de {passo} em {passo}: {', '.join(map(str, seq))}.", bncc="EF01MA10")
    # qual a regra
    for passo in (2, 3, 5, 10):
        for _ in range(3):
            ini = R.randint(0, 20)
            seq = [ini + passo * i for i in range(5)]
            op = [f"de {k} em {k}" for k in (2, 3, 5, 10)]
            add(T, 2, "multipla", f"Qual é a regra da sequência {', '.join(map(str, seq))}?", f"de {passo} em {passo}",
                opcoes=op, ordem_fixa=True, dica="Faça a conta: segundo número menos o primeiro.",
                explicacao=f"{seq[1]} − {seq[0]} = {passo}. Ela pula de {passo} em {passo}.", bncc="EF01MA10")
    # padrões de figuras
    simb = ["🔴", "🔵", "🟡", "🟢", "⭐", "🌙", "🍎", "🍌", "🐱", "🐶", "🔺", "🟦"]
    moldes = [("AB", 1), ("ABC", 2), ("AAB", 2), ("ABB", 2), ("AABB", 3), ("ABCC", 3), ("ABAC", 3)]
    for molde, nivel in moldes:
        for _ in range(6):
            letras = sorted(set(molde))
            esc = dict(zip(letras, R.sample(simb, len(letras))))
            rep = [esc[c] for c in molde]
            tam = len(rep) * 2 + R.randint(0, len(rep) - 1)
            seq = [rep[i % len(rep)] for i in range(tam)]
            prox = rep[tam % len(rep)]
            op = list(dict.fromkeys(list(esc.values()) + [s for s in simb if s not in esc.values()]))[:4]
            if prox not in op:
                op[-1] = prox
            add(T, nivel, "multipla", "Qual figura vem a seguir?", prox, opcoes=op,
                visual=" ".join(seq) + " ❓", dica="Encontre o pedacinho que se repete.",
                explicacao=f"O padrão que se repete é {' '.join(rep)}. Depois vem {prox}.", bncc="EF01MA09")
    # ordenar
    for _ in range(22):
        nivel = R.choice([1, 2, 2, 3])
        lim = {1: 20, 2: 60, 3: 99}[nivel]
        ns = R.sample(range(1, lim + 1), 4 if nivel < 3 else 5)
        cres = R.random() < 0.65
        resp = sorted(ns, reverse=not cres)
        add(T, nivel, "ordenar", f"Toque nos números em ordem {'CRESCENTE (do menor para o maior)' if cres else 'DECRESCENTE (do maior para o menor)'}.",
            resp, itens=ns, dica="Ache primeiro o " + ("menor." if cres else "maior."),
            explicacao=f"A ordem certa é {', '.join(map(str, resp))}.", bncc="EF01MA09")
    # ordenar expressões (desafio)
    for _ in range(8):
        exprs = []
        while len(exprs) < 4:
            a, b = R.randint(1, 10), R.randint(1, 10)
            if all(a + b != v for _, v in exprs):
                exprs.append((f"{a} + {b}", a + b))
        resp = [e for e, _ in sorted(exprs, key=lambda x: x[1])]
        add(T, 3, "ordenar", "Toque nas contas da que dá o MENOR resultado até a que dá o MAIOR.", resp,
            itens=[e for e, _ in exprs], dica="Resolva cada conta antes.",
            explicacao="Resultados: " + ", ".join(f"{e} = {v}" for e, v in sorted(exprs, key=lambda x: x[1])) + ".", bncc="EF01MA09")


# ---------------------------------------------------------------------------
# 8. Par, ímpar, dobro e metade
# ---------------------------------------------------------------------------
def tema_parimpar():
    T = "parimpar"
    for n in R.sample(range(1, 100), 30):
        par = n % 2 == 0
        add(T, 1 if n < 20 else 2, "multipla", f"O número {n} é par ou ímpar?", "Par" if par else "Ímpar",
            opcoes=["Par", "Ímpar"], ordem_fixa=True, dica="Olhe só a unidade: 0, 2, 4, 6, 8 são pares.",
            explicacao=f"{n} termina em {n % 10}, então é {'par' if par else 'ímpar'}." + (" Dá para formar duplinhas sem sobrar ninguém!" if par and n <= 20 else ""), bncc="EF01MA06")
    for n in range(1, 26):
        add(T, 1 if n <= 5 else (2 if n <= 12 else 3), "numero", f"Qual é o DOBRO de {n}?", 2 * n,
            dica="Dobro é o número somado com ele mesmo.", explicacao=f"{n} + {n} = {2 * n}.", bncc="EF01MA06")
    for n in range(2, 41, 2):
        add(T, 1 if n <= 10 else (2 if n <= 20 else 3), "numero", f"Qual é a METADE de {n}?", n // 2,
            dica="Que número somado com ele mesmo dá esse?", explicacao=f"{n // 2} + {n // 2} = {n}, então a metade de {n} é {n // 2}.", bncc="EF01MA06")
    fixas = [
        (2, "Quantos números pares existem de 1 até 10?", 5, "Liste: 2, 4...", "2, 4, 6, 8, 10: são 5 números pares."),
        (2, "Quantos números ímpares existem de 1 até 10?", 5, "Liste: 1, 3...", "1, 3, 5, 7, 9: são 5 números ímpares."),
        (3, "Qual é o maior número par menor que 30?", 28, "Volte de 30 para trás.", "29 é ímpar; 28 é par."),
        (3, "Qual é o menor número ímpar maior que 40?", 41, "Conte para frente a partir de 40.", "41 é ímpar."),
        (3, "Qual é o dobro do dobro de 3?", 12, "Primeiro o dobro de 3, depois o dobro desse resultado.", "Dobro de 3 = 6; dobro de 6 = 12."),
        (3, "Qual é a metade da metade de 20?", 5, "Primeiro a metade de 20, depois a metade do resultado.", "Metade de 20 = 10; metade de 10 = 5."),
        (2, "Quantos sapatos há em 6 pares de sapatos?", 12, "Um par são 2.", "6 pares = 6 + 6 = 12 sapatos."),
        (2, "Quantas meias há em 4 pares de meias?", 8, "Um par são 2.", "4 pares = 2 + 2 + 2 + 2 = 8 meias."),
        (3, "Ana tem 9 anos. O irmão tem o dobro da idade dela. Quantos anos tem o irmão?", 18, "Dobro é somar duas vezes.", "9 + 9 = 18 anos."),
        (3, "Um bolo tinha 16 pedaços. Metade foi comida no almoço. Quantos pedaços sobraram?", 8, "Divida 16 em duas partes iguais.", "8 + 8 = 16, então sobraram 8."),
    ]
    for nivel, enun, resp, dica, exp in fixas:
        add(T, nivel, "numero", enun, resp, dica=dica, explicacao=exp, bncc="EF01MA06")
    # problemas de dobro/metade
    for _ in range(10):
        a = dois_nomes()[0]
        s, p, g = R.choice(OBJ)
        n = R.randint(3, 12)
        if R.random() < 0.5:
            add(T, 3, "numero", f"{a} tinha {n} {p}. Ganhou o dobro disso. Com {quant(g).lower()} {p} ficou?".replace("o dobro disso", "mais o dobro disso"),
                3 * n, dica="Primeiro descubra o dobro; depois some com o que já tinha.",
                explicacao=f"Dobro de {n} = {2 * n}. {n} + {2 * n} = {3 * n}.", bncc="EF01MA06")
        else:
            add(T, 3, "numero", f"{a} tinha {2 * n} {p} e deu metade para a irmã. Com {quant(g).lower()} {p} ficou?", n,
                dica="Metade é dividir em duas partes iguais.", explicacao=f"Metade de {2 * n} é {n}.", bncc="EF01MA06")
    for _ in range(10):
        a, b = R.randint(1, 30), R.randint(1, 30)
        soma = a + b
        verd = soma % 2 == 0
        add(T, 3, "multipla", f"O resultado de {a} + {b} é par ou ímpar?", "Par" if verd else "Ímpar",
            opcoes=["Par", "Ímpar"], ordem_fixa=True, dica="Faça a conta e olhe a unidade.",
            explicacao=f"{a} + {b} = {soma}, que é {'par' if verd else 'ímpar'}.", bncc="EF01MA06")


# ---------------------------------------------------------------------------
# 9. Geometria
# ---------------------------------------------------------------------------
LADOS = {"triângulo": 3, "quadrado": 4, "retângulo": 4, "pentágono": 5, "hexágono": 6}
PLURAL = {"triângulo": "triângulos", "quadrado": "quadrados", "retângulo": "retângulos", "pentágono": "pentágonos", "hexágono": "hexágonos"}


def tema_geometria():
    T = "geometria"
    for f, n in LADOS.items():
        nivel = 1 if n <= 4 else 2
        add(T, nivel, "numero", f"Quantos lados tem um {f}?", n, dica="Desenhe a figura no papel e conte os lados.",
            explicacao=f"O {f} tem {n} lados.", bncc="EF01MA14")
        add(T, nivel, "numero", f"Quantos cantos (vértices) tem um {f}?", n, dica="Os cantos são as pontinhas.",
            explicacao=f"O {f} tem {n} cantos — o mesmo número de lados!", bncc="EF01MA14")
    add(T, 2, "numero", "Quantos lados retos tem um círculo?", 0, dica="O círculo é todo redondinho.",
        explicacao="O círculo não tem lados retos nem cantos: 0.", bncc="EF01MA14")
    add(T, 2, "multipla", "Qual figura tem 4 lados todos do mesmo tamanho?", "quadrado",
        opcoes=["quadrado", "retângulo", "triângulo", "círculo"], dica="Os lados são iguaizinhos.",
        explicacao="O quadrado tem 4 lados iguais. O retângulo tem 4 lados, mas 2 compridos e 2 curtos.", bncc="EF01MA14")
    add(T, 2, "multipla", "Qual figura não tem nenhum canto?", "círculo",
        opcoes=["círculo", "quadrado", "triângulo", "retângulo"], dica="Pense em uma roda.",
        explicacao="O círculo é redondo: não tem cantos.", bncc="EF01MA14")
    for f in LADOS:
        add(T, 1, "multipla", f"Qual figura tem {LADOS[f]} lados?", f,
            opcoes=[f] + [x for x in LADOS if LADOS[x] != LADOS[f]][:2] + ["círculo"],
            dica="Conte os lados de cada uma.", explicacao=f"O {f} tem {LADOS[f]} lados.", bncc="EF01MA14")
    # soma de lados
    nomes = list(LADOS)
    for _ in range(26):
        f1, f2 = R.sample(nomes, 2)
        k1, k2 = R.randint(1, 3), R.randint(1, 2)
        tot = k1 * LADOS[f1] + k2 * LADOS[f2]
        t1 = f"1 {f1}" if k1 == 1 else f"{k1} {PLURAL[f1]}"
        t2 = f"1 {f2}" if k2 == 1 else f"{k2} {PLURAL[f2]}"
        add(T, 3, "numero", f"Quantos lados há ao todo em {t1} e {t2}?", tot,
            dica="Descubra quantos lados tem cada figura e some tudo.",
            explicacao=f"{k1} × {LADOS[f1]} = {k1 * LADOS[f1]} e {k2} × {LADOS[f2]} = {k2 * LADOS[f2]}; {k1 * LADOS[f1]} + {k2 * LADOS[f2]} = {tot}.", bncc="EF01MA14")
    solidos = [
        ("uma bola de futebol", "esfera"), ("um dado", "cubo"), ("uma lata de refrigerante", "cilindro"),
        ("um chapéu de aniversário", "cone"), ("uma caixa de sapato", "bloco retangular"), ("uma laranja", "esfera"),
        ("um cubo mágico", "cubo"), ("um rolo de papel", "cilindro"), ("uma casquinha de sorvete", "cone"),
        ("um tijolo", "bloco retangular"), ("uma bolinha de gude", "esfera"), ("uma caixa de leite", "bloco retangular"),
    ]
    todos = ["esfera", "cubo", "cilindro", "cone", "bloco retangular", "pirâmide"]
    for obj, sol in solidos:
        add(T, 2, "multipla", f"{obj[0].upper() + obj[1:]} parece com qual forma?", sol,
            opcoes=[sol] + [x for x in R.sample(todos, 4) if x != sol][:3],
            dica="Imagine o objeto na sua mão.", explicacao=f"{obj[0].upper() + obj[1:]} tem forma de {sol}.", bncc="EF01MA13")
    fixas = [
        (2, "Quantas faces (lados quadrados) tem um dado?", 6, "Os números do dado vão de 1 a...", "O dado é um cubo: tem 6 faces."),
        (3, "Juntando 2 triângulos iguais, posso formar um quadrado. Quantos lados tinham os 2 triângulos juntos, antes de juntar?", 6, "Cada triângulo tem 3 lados.", "3 + 3 = 6 lados."),
        (2, "Quantos cantos há em 2 quadrados?", 8, "Cada quadrado tem 4 cantos.", "4 + 4 = 8 cantos."),
        (3, "Uma mesa quadrada tem uma cadeira em cada lado. Quantas cadeiras há?", 4, "Quantos lados tem o quadrado?", "O quadrado tem 4 lados: 4 cadeiras."),
        (3, "Uma mesa hexagonal tem 2 cadeiras em cada lado. Quantas cadeiras há?", 12, "O hexágono tem 6 lados.", "6 lados × 2 cadeiras = 12 cadeiras."),
        (3, "Uma pirâmide de base quadrada tem quantas faces? (a base + os triângulos)", 5, "1 quadrado embaixo + 4 triângulos.", "1 + 4 = 5 faces."),
    ]
    for nivel, enun, resp, dica, exp in fixas:
        add(T, nivel, "numero", enun, resp, dica=dica, explicacao=exp, bncc="EF01MA13")
    # posição
    posic = [
        ("Na fila 🐶 🐱 🐰, quem está no MEIO?", "🐱", ["🐶", "🐱", "🐰"]),
        ("Na fila 🍎 🍌 🍇 🍓, quem está logo à DIREITA da 🍌?", "🍇", ["🍎", "🍇", "🍓"]),
        ("Na fila 🍎 🍌 🍇 🍓, quem está logo à ESQUERDA da 🍇?", "🍌", ["🍎", "🍌", "🍓"]),
        ("Na fila ⭐ 🌙 ☀️ ☁️ ⚡, quem é o 4º?", "☁️", ["🌙", "☀️", "☁️", "⚡"]),
        ("Na fila 🚗 🚌 🚲 🚂 ✈️, quem é o último?", "✈️", ["🚗", "🚂", "✈️", "🚲"]),
        ("Na fila 🐸 🐢 🐍 🦎 🐊, quem é o 2º contando da DIREITA?", "🦎", ["🐢", "🦎", "🐍", "🐊"]),
        ("Na fila 🔴 🟠 🟡 🟢 🔵 🟣, quem está entre o 🟡 e o 🔵?", "🟢", ["🟠", "🟢", "🟣", "🔴"]),
        ("Na fila 🍰 🍩 🍪 🍫 🍬, quantos doces estão à direita do 🍪?", "2", ["1", "2", "3", "4"]),
    ]
    for enun, resp, op in posic:
        add(T, 2, "multipla", enun, resp, opcoes=op, dica="A direita é a mão que muitos usam para escrever. Comece a contar pela esquerda.",
            explicacao=f"A resposta é {resp}.", bncc="EF01MA11")
    for _ in range(10):
        fila = R.sample(["🐶", "🐱", "🐰", "🦊", "🐻", "🐼", "🐨", "🐯", "🦁", "🐮"], 6)
        p = R.randint(1, 5)
        add(T, 2, "multipla", f"Na fila {' '.join(fila)}, qual animal é o {p + 1}º (contando da esquerda)?", fila[p],
            opcoes=[fila[p]] + R.sample([x for x in fila if x != fila[p]], 3),
            dica="Aponte e conte: 1º, 2º, 3º...", explicacao=f"Contando da esquerda, o {p + 1}º é {fila[p]}.", bncc="EF01MA11")


# ---------------------------------------------------------------------------
# 10. Tempo, calendário e dinheiro
# ---------------------------------------------------------------------------
DIAS = ["domingo", "segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado"]
MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]


def hora_txt(h, m):
    base = "1 hora" if h == 1 else f"{h} horas"
    return base if m == 0 else (f"{h} e meia")


def tema_medidas():
    T = "medidas"
    for h in range(1, 13):
        for m in (0, 30):
            certa = hora_txt(h, m)
            hp, ha = h % 12 + 1, (h - 2) % 12 + 1
            dis = [hora_txt(hp, m), hora_txt(h, 30 - m), hora_txt(ha, m), hora_txt(hp, 30 - m)]
            op = [certa] + [d for d in dict.fromkeys(dis) if d != certa][:3]
            exp = (f"O ponteiro grande está no 12 (hora exata) e o pequeno no {h}: {certa}." if m == 0 else
                   f"O ponteiro grande está no 6 (meia hora) e o pequeno entre o {h} e o {hp}: {certa}.")
            add(T, 1 if m == 0 else 2, "multipla", "Que horas o relógio está marcando?", certa, opcoes=op,
                relogio={"h": h, "m": m}, dica="O ponteiro PEQUENO mostra a hora. O GRANDE mostra os minutos.",
                explicacao=exp, bncc="EF01MA16")
    for _ in range(16):
        h = R.randint(1, 9)
        k = R.randint(1, 3)
        add(T, 2, "numero", f"Agora são {hora_txt(h, 0)}. Que horas serão daqui a {k} {'hora' if k == 1 else 'horas'}? (só o número)", h + k,
            dica="Conte para frente no relógio.", explicacao=f"{h} + {k} = {h + k}: serão {h + k} horas.", bncc="EF01MA16")
    for _ in range(8):
        h1 = R.randint(1, 6)
        h2 = R.randint(h1 + 1, 11)
        add(T, 3, "numero", f"A festa começou às {h1} horas e terminou às {h2} horas. Quantas horas durou?", h2 - h1,
            dica=f"Conte de {h1} até {h2}.", explicacao=f"{h2} − {h1} = {h2 - h1} horas.", bncc="EF01MA16")
    # dias da semana
    for i, d in enumerate(DIAS):
        prox, ant = DIAS[(i + 1) % 7], DIAS[(i - 1) % 7]
        add(T, 1, "multipla", f"Que dia da semana vem logo depois de {d}?", prox,
            opcoes=[prox, ant, DIAS[(i + 2) % 7], DIAS[(i + 3) % 7]], dica="Domingo, segunda, terça, quarta, quinta, sexta, sábado.",
            explicacao=f"Depois de {d} vem {prox}.", bncc="EF01MA17")
        add(T, 2, "multipla", f"Que dia da semana vem logo antes de {d}?", ant,
            opcoes=[ant, prox, DIAS[(i - 2) % 7], DIAS[(i + 2) % 7]], dica="Volte um dia.",
            explicacao=f"Antes de {d} vem {ant}.", bncc="EF01MA17")
        k = R.randint(2, 5)
        alvo = DIAS[(i + k) % 7]
        add(T, 3, "multipla", f"Hoje é {d}. Que dia será daqui a {k} dias?", alvo,
            opcoes=list(dict.fromkeys([alvo, DIAS[(i + k - 1) % 7], DIAS[(i + k + 1) % 7], DIAS[(i - k) % 7]])),
            dica="Conte nos dedos um dia de cada vez.", explicacao=f"Contando {k} dias depois de {d}, chegamos em {alvo}.", bncc="EF01MA17")
        alvo2 = prox
        add(T, 3, "multipla", f"Ontem foi {ant}. Que dia será amanhã?", alvo2,
            opcoes=[alvo2, d, DIAS[(i + 2) % 7], ant],
            dica="Descubra primeiro que dia é hoje.", explicacao=f"Se ontem foi {ant}, hoje é {d} e amanhã será {alvo2}.", bncc="EF01MA17")
    for i, m in enumerate(MESES):
        prox = MESES[(i + 1) % 12]
        add(T, 2, "multipla", f"Que mês vem logo depois de {m}?", prox,
            opcoes=[prox, MESES[(i - 1) % 12], MESES[(i + 2) % 12], MESES[(i + 6) % 12]],
            dica="Janeiro, fevereiro, março, abril...", explicacao=f"Depois de {m} vem {prox}.", bncc="EF01MA17")
    fixas = [
        (1, "Quantos dias tem uma semana?", 7, "Conte de domingo a sábado.", "Domingo, segunda, terça, quarta, quinta, sexta e sábado: 7 dias."),
        (1, "Quantos meses tem um ano?", 12, "De janeiro a dezembro.", "Um ano tem 12 meses."),
        (2, "Quantos dias têm 2 semanas?", 14, "Cada semana tem 7 dias.", "7 + 7 = 14 dias."),
        (3, "Quantos dias têm 3 semanas?", 21, "Some 7 três vezes.", "7 + 7 + 7 = 21 dias."),
        (2, "Quantos dias da semana começam com a letra S?", 3, "Leia os nomes com atenção.", "Segunda, sexta e sábado: 3 dias."),
        (2, "Quantos dias de aula há de segunda a sexta-feira?", 5, "Conte: segunda, terça...", "Segunda, terça, quarta, quinta e sexta: 5 dias."),
        (3, "Lucas faz aniversário em 20 de maio. Hoje é 12 de maio. Quantos dias faltam?", 8, "Conte de 12 até 20.", "20 − 12 = 8 dias."),
        (3, "Uma viagem começou dia 5 e voltou dia 9 do mesmo mês. Quantas noites a família dormiu fora?", 4, "Conte as noites: do 5 para o 6...", "5→6, 6→7, 7→8, 8→9: 4 noites."),
        (1, "Quantos minutos tem uma hora?", 60, "O ponteiro grande dá uma volta inteira.", "Uma hora tem 60 minutos."),
        (2, "Meia hora tem quantos minutos?", 30, "Metade de 60.", "30 + 30 = 60, então meia hora tem 30 minutos."),
    ]
    for nivel, enun, resp, dica, exp in fixas:
        add(T, nivel, "numero", enun, resp, dica=dica, explicacao=exp, bncc="EF01MA17")
    add(T, 2, "multipla", "Qual é o primeiro mês do ano?", "janeiro", opcoes=["janeiro", "dezembro", "março", "fevereiro"],
        dica="O ano novo começa nele.", explicacao="Janeiro é o 1º mês.", bncc="EF01MA17")
    add(T, 2, "multipla", "Qual é o último mês do ano?", "dezembro", opcoes=["janeiro", "dezembro", "novembro", "outubro"],
        dica="É o mês do Natal.", explicacao="Dezembro é o 12º mês.", bncc="EF01MA17")
    # dinheiro
    valores = [1, 2, 5, 10, 20]
    def peca(v):
        return "1 moeda de 1 real" if v == 1 else f"1 nota de {v} reais"
    for _ in range(22):
        k = R.randint(2, 3)
        vs = sorted(R.choices(valores, k=k), reverse=True)
        tot = sum(vs)
        if tot > 50:
            continue
        txt = ", ".join(peca(v) for v in vs[:-1]) + " e " + peca(vs[-1])
        add(T, 2 if k == 2 else 3, "numero", f"Tenho {txt}. Quantos reais tenho ao todo?", tot,
            dica="Some o valor de cada nota e moeda.", explicacao=f"{' + '.join(map(str, vs))} = {tot} reais.", bncc="EF01MA19")
    for _ in range(18):
        pg = R.choice([5, 10, 10, 20])
        preco = R.randint(1, pg - 1)
        add(T, 3 if pg == 20 else 2, "numero", f"Um brinquedo custa {preco} {'real' if preco == 1 else 'reais'}. Paguei com uma nota de {pg} reais. Quanto recebo de troco?",
            pg - preco, dica=f"Conte do {preco} até o {pg}.", explicacao=f"{pg} − {preco} = {pg - preco} reais de troco.", bncc="EF01MA19")
    for v in (2, 5, 10, 20):
        add(T, 1 if v <= 5 else 2, "numero", f"Quantas moedas de 1 real valem o mesmo que uma nota de {v} reais?", v,
            dica="Cada moeda vale 1.", explicacao=f"{v} moedas de 1 real = {v} reais.", bncc="EF01MA19")
    trocas = [(10, 5, 2), (10, 2, 5), (20, 10, 2), (20, 5, 4)]
    for g, p, r in trocas:
        add(T, 3, "numero", f"Quantas notas de {p} reais valem o mesmo que uma nota de {g} reais?",
            r, dica=f"Conte de {p} em {p} até chegar em {g}.", explicacao=f"{' + '.join([str(p)] * r)} = {g}.", bncc="EF01MA19")
    for _ in range(10):
        a, b = R.randint(2, 9), R.randint(2, 9)
        add(T, 2, "numero", f"Comprei um suco por {a} reais e um lanche por {b} reais. Quanto gastei?", a + b,
            dica="Junte os dois preços.", explicacao=f"{a} + {b} = {a + b} reais.", bncc="EF01MA19")
    for _ in range(8):
        tem = R.randint(5, 15)
        preco = R.randint(tem + 1, 25)
        add(T, 3, "numero", f"Um livro custa {preco} reais. Tenho {tem} reais. Quantos reais ainda faltam?", preco - tem,
            dica=f"Conte de {tem} até {preco}.", explicacao=f"{preco} − {tem} = {preco - tem} reais.", bncc="EF01MA19")
    # medidas de comprimento/massa/capacidade
    med = [
        ("Para medir o comprimento de uma mesa, usamos…", "metro", ["metro", "quilo", "litro", "hora"]),
        ("Para saber quanto você pesa, usamos…", "quilo", ["metro", "quilo", "litro", "dia"]),
        ("Para medir quanto leite cabe numa garrafa, usamos…", "litro", ["metro", "quilo", "litro", "real"]),
        ("O que é mais PESADO?", "um elefante", ["um elefante", "um gato", "uma pena", "uma formiga"]),
        ("O que é mais COMPRIDO?", "um ônibus", ["um lápis", "um ônibus", "uma borracha", "um sapato"]),
        ("Em qual cabe MAIS água?", "uma piscina", ["um copo", "um balde", "uma piscina", "uma xícara"]),
        ("O que é mais LEVE?", "uma folha de papel", ["uma folha de papel", "um tijolo", "uma melancia", "uma mochila"]),
        ("Qual dura MAIS tempo?", "um ano", ["um dia", "uma semana", "um mês", "um ano"]),
        ("Qual dura MENOS tempo?", "um minuto", ["um minuto", "uma hora", "um dia", "uma semana"]),
    ]
    for enun, resp, op in med:
        add(T, 1, "multipla", enun, resp, opcoes=op, dica="Imagine cada coisa.", explicacao=f"Resposta: {resp}.", bncc="EF01MA15")
    for _ in range(8):
        a, b = R.sample(range(5, 30), 2)
        n1, n2 = dois_nomes()
        add(T, 2, "multipla", f"A fita de {n1} mede {a} palmos. A de {n2} mede {b} palmos. Qual fita é mais comprida?",
            f"a de {n1}" if a > b else f"a de {n2}", opcoes=[f"a de {n1}", f"a de {n2}"], ordem_fixa=True,
            dica="Mais palmos = mais comprida.", explicacao=f"{max(a, b)} palmos é mais que {min(a, b)}.", bncc="EF01MA15")


# ---------------------------------------------------------------------------
# 11. Desafios de lógica
# ---------------------------------------------------------------------------
def tema_desafios():
    T = "desafios"
    for _ in range(24):
        n = R.randint(2, 20)
        k = R.randint(2, 10)
        if R.random() < 0.5:
            add(T, 3, "numero", f"Pensei em um número. Somei {k} e deu {n + k}. Em que número pensei?", n,
                dica="Faça o caminho de volta: tire o que foi somado.", explicacao=f"{n + k} − {k} = {n}. Confira: {n} + {k} = {n + k}.", bncc="EF01MA08")
        elif n > k:
            add(T, 3, "numero", f"Pensei em um número. Tirei {k} e sobrou {n - k}. Em que número pensei?", n,
                dica="Faça o caminho de volta: some o que foi tirado.", explicacao=f"{n - k} + {k} = {n}. Confira: {n} − {k} = {n - k}.", bncc="EF01MA08")
    frutas = ["🍎", "🍌", "🍇", "🍓", "🍐", "🍒", "🥝", "🍊"]
    for _ in range(14):
        f = R.choice(frutas)
        v = R.randint(2, 10)
        add(T, 2, "numero", f"{f} + {f} = {2 * v}. Quanto vale {f}?", v,
            dica="Dois números iguais que somados dão isso.", explicacao=f"{v} + {v} = {2 * v}, então {f} = {v}.", bncc="EF01MA08")
    for _ in range(14):
        f1, f2 = R.sample(frutas, 2)
        a, b = R.randint(2, 9), R.randint(2, 9)
        add(T, 3, "numero", f"{f1} + {f2} = {a + b}. Se {f1} = {a}, quanto vale {f2}?", b,
            dica=f"Troque {f1} por {a}: {a} + ? = {a + b}.", explicacao=f"{a} + {b} = {a + b}, então {f2} = {b}.", bncc="EF01MA08")
    for _ in range(8):
        f = R.choice(frutas)
        v = R.randint(2, 6)
        add(T, 3, "numero", f"{f} + {f} + {f} = {3 * v}. Quanto vale {f}?", v,
            dica="Três números iguais. Experimente valores!", explicacao=f"{v} + {v} + {v} = {3 * v}, então {f} = {v}.", bncc="EF01MA08")
    for d in range(1, 10):
        add(T, 3, "numero", f"Sou um número maior que {d * 10} e menor que {d * 10 + 10}. Meus dois algarismos são iguais. Quem sou eu?", d * 11,
            dica=f"Os números entre {d * 10} e {d * 10 + 10} começam com {d}.", explicacao=f"O número é {d * 11}: tem dois algarismos {d}.", bncc="EF01MA04")
    for d in range(1, 5):
        add(T, 3, "numero", f"Sou um número de dois algarismos. Minha dezena é {d} e minha unidade é o dobro da dezena. Quem sou eu?", d * 10 + 2 * d,
            dica=f"O dobro de {d} é {2 * d}.", explicacao=f"Dezena {d} e unidade {2 * d}: {d * 10 + 2 * d}.", bncc="EF01MA07")
    for _ in range(10):
        a, b = R.sample(range(1, 10), 2)
        add(T, 3, "numero", f"Com os algarismos {a} e {b} (usando cada um uma vez), qual é o MAIOR número que posso formar?", max(a, b) * 10 + min(a, b),
            dica="Coloque o algarismo maior na casa das dezenas.", explicacao=f"{max(a, b)}{min(a, b)} é maior que {min(a, b)}{max(a, b)}.", bncc="EF01MA07")
    for _ in range(6):
        a, b = R.sample(range(1, 10), 2)
        add(T, 3, "numero", f"Com os algarismos {a} e {b} (usando cada um uma vez), qual é o MENOR número que posso formar?", min(a, b) * 10 + max(a, b),
            dica="Coloque o algarismo menor na casa das dezenas.", explicacao=f"{min(a, b)}{max(a, b)} é menor que {max(a, b)}{min(a, b)}.", bncc="EF01MA07")
    for _ in range(10):
        a, b, c = R.randint(1, 6), R.randint(1, 6), R.randint(1, 6)
        tot = a + b + c
        add(T, 3, "numero", f"Complete: {tot} = {a} + ___ + {c}", b, dica=f"Some {a} + {c} primeiro.",
            explicacao=f"{a} + {c} = {a + c}; falta {b} para chegar a {tot}.", bncc="EF01MA06")
    # patas mistas
    for _ in range(10):
        g, gal = R.randint(1, 3), R.randint(1, 3)
        add(T, 3, "numero", f"No quintal há {g} {'gato' if g == 1 else 'gatos'} e {gal} {'galinha' if gal == 1 else 'galinhas'}. Quantas patas há ao todo?",
            4 * g + 2 * gal, dica="Gato tem 4 patas; galinha tem 2.",
            explicacao=f"Gatos: {4 * g} patas. Galinhas: {2 * gal} patas. Total: {4 * g + 2 * gal}.", bncc="EF01MA08")
    charadas = [
        (3, "Uma escada tem 10 degraus. Pedro está no 4º degrau e sobe mais 3. Em qual degrau ele está?", 7, "Conte a partir do 4.", "4 + 3 = 7: ele está no 7º degrau."),
        (3, "Uma lagarta sobe 3 galhos e desce 1 galho por dia. Depois de 2 dias, quantos galhos acima do chão ela está?", 4, "Cada dia ela sobe 2 de verdade.", "Dia 1: 3 − 1 = 2. Dia 2: 2 + 3 − 1 = 4."),
        (3, "Tenho 5 balas a mais que Ana. Ana tem 7. Quantas balas eu tenho?", 12, "Eu tenho o que Ana tem e mais 5.", "7 + 5 = 12 balas."),
        (3, "Tenho 4 balas a menos que Davi. Davi tem 13. Quantas balas eu tenho?", 9, "Tire 4 do que Davi tem.", "13 − 4 = 9 balas."),
        (3, "Cortei uma fita em 3 pedaços. Quantos cortes eu fiz?", 2, "Desenhe a fita e os cortes.", "Com 2 cortes a fita fica em 3 pedaços."),
        (3, "Cortei um barbante em 5 pedaços. Quantos cortes eu fiz?", 4, "Desenhe e conte os cortes.", "Sempre há um corte a menos que o número de pedaços: 4."),
        (3, "Plantei 5 árvores em fila, uma a cada 2 passos. Quantos passos há da primeira até a última?", 8, "Entre 5 árvores há 4 espaços.", "4 espaços × 2 passos = 8 passos."),
        (3, "Duas irmãs têm juntas 10 anos. Uma tem 2 anos a mais que a outra. Quantos anos tem a mais nova?", 4, "Experimente: 5 e 5? 4 e 6?", "4 + 6 = 10 e 6 é 2 a mais que 4. A mais nova tem 4 anos."),
        (2, "Numa corrida, passei a pessoa que estava em 2º lugar. Em que lugar eu fiquei?", 2, "Cuidado com a pegadinha!", "Se passei o 2º, fiquei no lugar dele: 2º!"),
        (3, "Quantos números de dois algarismos terminam em 5?", 9, "15, 25, 35...", "15, 25, 35, 45, 55, 65, 75, 85, 95: são 9."),
        (3, "Quantas vezes o algarismo 1 aparece quando escrevemos de 1 até 12?", 5, "Escreva os números e procure o 1.", "1, 10, 11 (duas vezes), 12: são 5 vezes."),
        (2, "Um gato tem 4 patas. Quantas patas tem meio gato desenhado de lado, se só aparecem as patas da frente?", 2, "As patas da frente são...", "Aparecem as 2 patas da frente."),
        (3, "Numa mesa há 3 pratos com 2 bananas e 1 maçã em cada. Quantas frutas há na mesa?", 9, "Quantas frutas há em cada prato?", "Cada prato tem 3 frutas: 3 + 3 + 3 = 9."),
        (3, "Um caracol sobe 2 cm por minuto. Quantos centímetros ele sobe em 5 minutos?", 10, "Conte de 2 em 2.", "2, 4, 6, 8, 10 cm."),
        (2, "Se hoje é sábado, depois de amanhã será que dia? Responda com o número: 1 = domingo, 2 = segunda.", 2, "Amanhã é domingo...", "Amanhã é domingo; depois de amanhã é segunda (2)."),
    ]
    for nivel, enun, resp, dica, exp in charadas:
        add(T, nivel, "numero", enun, resp, dica=dica, explicacao=exp, bncc="EF01MA08")
    logicas = [
        ("Quem é mais alto? Ana é mais alta que Bia. Bia é mais alta que Caio.", "Ana", ["Ana", "Bia", "Caio"]),
        ("Quem é o mais baixo? Ana é mais alta que Bia. Bia é mais alta que Caio.", "Caio", ["Ana", "Bia", "Caio"]),
        ("Davi chegou antes de Enzo. Enzo chegou antes de Lia. Quem chegou por último?", "Lia", ["Davi", "Enzo", "Lia"]),
        ("Theo tem mais figurinhas que Gabi. Gabi tem mais que Nina. Quem tem menos?", "Nina", ["Theo", "Gabi", "Nina"]),
        ("Uma caixa tem só bolas vermelhas. Se eu tirar uma bola sem olhar, ela será…", "vermelha com certeza", ["vermelha com certeza", "azul com certeza", "talvez azul"]),
        ("Uma caixa tem 9 bolas azuis e 1 amarela. Tirando uma sem olhar, é mais provável sair…", "azul", ["azul", "amarela", "verde"]),
        ("Jogando um dado comum, é possível tirar o número 7?", "Impossível", ["Impossível", "Com certeza", "Talvez"]),
        ("Amanhã o sol vai nascer. Isso é…", "Com certeza", ["Impossível", "Com certeza", "Talvez"]),
    ]
    for enun, resp, op in logicas:
        add(T, 2, "multipla", enun, resp, opcoes=op, dica="Leia devagar e imagine a cena.", explicacao=f"Resposta: {resp}.", bncc="EF01MA20")


def main():
    for f in (tema_contagem, tema_dezenas, tema_comparar, tema_adicao, tema_subtracao, tema_problemas,
              tema_sequencias, tema_parimpar, tema_geometria, tema_medidas, tema_desafios):
        f()
    cont = {}
    for q in Q:
        s = SIGLA[q["tema"]]
        cont[s] = cont.get(s, 0) + 1
        q["id"] = f"{s}-{cont[s]:03d}"
    # ordem das chaves
    ordem = ["id", "tema", "nivel", "tipo", "enunciado", "visual", "relogio", "opcoes", "itens", "resposta", "dica", "explicacao", "bncc"]
    banco = [{k: q[k] for k in ordem if k in q} for q in Q]
    assert len(banco) >= 1000, f"Só {len(banco)} questões!"

    os.makedirs(os.path.join(RAIZ, "data"), exist_ok=True)
    os.makedirs(os.path.join(RAIZ, "js"), exist_ok=True)
    meta = {"versao": "1.0.0", "total": len(banco), "temas": TEMAS}
    with open(os.path.join(RAIZ, "data", "questoes.json"), "w", encoding="utf-8") as f:
        json.dump({**meta, "questoes": banco}, f, ensure_ascii=False, indent=1)
    with open(os.path.join(RAIZ, "js", "questoes.js"), "w", encoding="utf-8") as f:
        f.write("// Arquivo gerado automaticamente por scripts/gerar_questoes.py — não edite à mão.\n")
        f.write("window.TEMAS = " + json.dumps(TEMAS, ensure_ascii=False) + ";\n")
        f.write("window.QUESTOES = [\n")
        f.write(",\n".join(json.dumps(q, ensure_ascii=False) for q in banco))
        f.write("\n];\n")
    with open(os.path.join(RAIZ, "data", "questoes.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["id", "tema", "nivel", "tipo", "enunciado", "visual", "opcoes_ou_itens", "resposta", "dica", "explicacao", "bncc"])
        for q in banco:
            vis = q.get("visual", "")
            if "relogio" in q:
                vis = f"[relógio {q['relogio']['h']}:{q['relogio']['m']:02d}]"
            op = " | ".join(q.get("opcoes", q.get("itens", [])))
            resp = " → ".join(q["resposta"]) if isinstance(q["resposta"], list) else q["resposta"]
            w.writerow([q["id"], q["tema"], q["nivel"], q["tipo"], q["enunciado"], vis, op, resp, q["dica"], q["explicacao"], q["bncc"]])

    # listas em Markdown para ler direto no GitHub
    pasta = os.path.join(RAIZ, "docs", "questoes")
    os.makedirs(pasta, exist_ok=True)
    niveis = {1: "🌱 Fácil", 2: "🌿 Médio", 3: "🌳 Desafio"}
    indice = ["# Banco de questões por assunto", "", f"Total: **{len(banco)} questões**. Cada arquivo traz as perguntas com resposta, dica e explicação.", "",
              "| Assunto | Questões | 🌱 Fácil | 🌿 Médio | 🌳 Desafio | BNCC |", "|---|---:|---:|---:|---:|---|"]
    for t in TEMAS:
        qs = [q for q in banco if q["tema"] == t["id"]]
        n = {k: sum(1 for q in qs if q["nivel"] == k) for k in (1, 2, 3)}
        indice.append(f"| {t['icone']} [{t['nome']}]({t['id']}.md) | {len(qs)} | {n[1]} | {n[2]} | {n[3]} | {t['bncc']} |")
        linhas = [f"# {t['icone']} {t['nome']}", "", f"{len(qs)} questões • BNCC: {t['bncc']} • [voltar ao índice](README.md)", ""]
        for nv in (1, 2, 3):
            sel = [q for q in qs if q["nivel"] == nv]
            if not sel:
                continue
            linhas += [f"## {niveis[nv]} ({len(sel)})", ""]
            for q in sel:
                enun = q["enunciado"].replace("|", "\\|")
                linhas.append(f"**{q['id']}** — {enun}  ")
                if q.get("visual"):
                    linhas.append(f"{q['visual']}  ")
                if q.get("relogio"):
                    linhas.append(f"🕒 *(relógio marcando {q['relogio']['h']}:{q['relogio']['m']:02d})*  ")
                if q.get("opcoes"):
                    linhas.append("Opções: " + " • ".join(q["opcoes"]) + "  ")
                if q.get("itens"):
                    linhas.append("Números: " + " • ".join(q["itens"]) + "  ")
                resp = " → ".join(q["resposta"]) if isinstance(q["resposta"], list) else q["resposta"]
                linhas.append(f"✅ **{resp}** — {q['explicacao']}")
                linhas.append("")
        with open(os.path.join(pasta, f"{t['id']}.md"), "w", encoding="utf-8") as f:
            f.write("\n".join(linhas))
    with open(os.path.join(pasta, "README.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(indice) + "\n")

    print(f"Total: {len(banco)} questões")
    for t in TEMAS:
        qs = [q for q in banco if q["tema"] == t["id"]]
        niv = {n: sum(1 for q in qs if q["nivel"] == n) for n in (1, 2, 3)}
        print(f"  {t['nome']:32s} {len(qs):4d}   nível 1/2/3: {niv[1]}/{niv[2]}/{niv[3]}")
    tipos = {}
    for q in banco:
        tipos[q["tipo"]] = tipos.get(q["tipo"], 0) + 1
    print("  Tipos:", tipos)


def _pausar_se_dois_cliques():
    """No Windows, a janela fecha sozinha quando o script é aberto com dois cliques."""
    if os.name == "nt" and "PROMPT" not in os.environ:
        try:
            input("\nPressione Enter para fechar...")
        except EOFError:
            pass


if __name__ == "__main__":
    # Evita erro de acentuação em terminais antigos do Windows
    for fluxo in (sys.stdout, sys.stderr):
        try:
            fluxo.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass
    if sys.version_info < (3, 8):
        print("Este script precisa do Python 3.8 ou mais novo. Baixe em https://www.python.org/downloads/")
        _pausar_se_dois_cliques()
        sys.exit(1)
    try:
        main()
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import montar_site
        print("\nMontando as páginas do site:")
        montar_site.main()
        print("\nPronto! Atualizados: index.html, professor.html, js/questoes.js, data/ e docs/questoes/")
    except Exception:
        traceback.print_exc()
        print("\nAlgo deu errado ao gerar as questões. Copie a mensagem acima e envie para quem mantém o projeto.")
        _pausar_se_dois_cliques()
        sys.exit(1)
    _pausar_se_dois_cliques()
