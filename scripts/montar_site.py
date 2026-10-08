#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monta as páginas finais do site (index.html e professor.html) a partir dos
modelos em modelos/, colocando o CSS e todo o JavaScript DENTRO de cada página.

Assim cada página funciona sozinha: mesmo que alguém abra o index.html
direto de dentro do .zip, ou que a pasta js/ não seja enviada ao GitHub,
o site continua funcionando.

Este script é chamado automaticamente pelo gerar_questoes.py.
Para rodar sozinho (depois de mudar só o visual ou o código):
  Windows:   py scripts\\montar_site.py
  Mac/Linux: python3 scripts/montar_site.py
"""
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGINAS = ["index.html", "professor.html"]
AVISO = ("<!-- ARQUIVO GERADO por scripts/montar_site.py a partir de modelos/{nome}.\n"
         "     Para mudar a página, edite modelos/{nome}, css/ ou js/ e rode o gerador. -->\n")


def ler(caminho):
    with open(os.path.join(RAIZ, caminho), encoding="utf-8") as f:
        return f.read()


def seguro_para_script(codigo):
    # impede que um "</script>" dentro do código feche a tag antes da hora
    return re.sub(r"</(script)", r"<\\/\1", codigo, flags=re.I)


def montar(nome):
    html = ler(os.path.join("modelos", nome))

    def css(m):
        return "<style>\n" + ler(m.group(1)) + "\n</style>"

    def js(m):
        return "<script>\n/* ---- " + m.group(1) + " ---- */\n" + seguro_para_script(ler(m.group(1))) + "\n</script>"

    html, n_css = re.subn(r'<link rel="stylesheet" href="([^"]+\.css)">', css, html)
    html, n_js = re.subn(r'<script src="([^"]+\.js)"[^>]*></script>', js, html)
    if n_css == 0 or n_js == 0:
        raise RuntimeError(f"modelos/{nome}: não encontrei as tags de CSS/JS para embutir.")
    html = html.replace("<!doctype html>\n", "<!doctype html>\n" + AVISO.format(nome=nome), 1)
    with open(os.path.join(RAIZ, nome), "w", encoding="utf-8", newline="\n") as f:
        f.write(html)
    return len(html)


def main():
    for nome in PAGINAS:
        tam = montar(nome)
        print(f"  {nome:16s} montado ({tam // 1024} KB, funciona sozinho)")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # mensagem clara em vez de só o erro técnico
        print("Erro ao montar o site:", e)
        sys.exit(1)
