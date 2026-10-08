# 🚀 Publicar no GitHub (e deixar o site no ar de graça)

## Jeito mais fácil: pelo navegador, sem instalar nada

1. Entre em <https://github.com> e faça login.
2. Clique em **New repository** (botão verde ou “+” no canto superior direito).
3. Nome: `mundo-dos-numeros` • marque **Public** • clique em **Create repository**.
4. Na página que abrir, clique em **uploading an existing file**.
5. Descompacte o `.zip` no seu computador, abra a pasta `mundo-dos-numeros` e **arraste todo o conteúdo** dela (as pastas `css`, `js`, `data`, `docs`, `scripts` e os arquivos) para a janela do GitHub.
   > Arraste o que está **dentro** da pasta, não a pasta em si — o `index.html` precisa ficar na raiz do repositório.
6. Clique em **Commit changes**.
7. Confira se a lista do repositório mostra `index.html` e `professor.html` na raiz. Eles funcionam sozinhos; as outras pastas servem para editar o projeto e baixar o banco (CSV/JSON).

### Ligar o GitHub Pages

1. No repositório, vá em **Settings → Pages**.
2. Em **Source**, escolha **Deploy from a branch**.
3. Branch: **main** • pasta: **/ (root)** • **Save**.
4. Aguarde 1 a 2 minutos e recarregue a página. Aparecerá o endereço:
   `https://SEU-USUARIO.github.io/mundo-dos-numeros/`

A área do professor fica em `.../mundo-dos-numeros/professor.html`.

## Pelo terminal (para quem usa Git)

```bash
cd mundo-dos-numeros
git init
git add .
git commit -m "Mundo dos Números: site de matemática do 1º ano"
git branch -M main
git remote add origin https://github.com/SEU-USUARIO/mundo-dos-numeros.git
git push -u origin main
```

Depois, ligue o GitHub Pages como explicado acima.

## Atualizar depois

Mudou questões no script? Rode o gerador (Windows: dois cliques em `gerar_questoes.bat`; Mac/Linux: `python3 scripts/gerar_questoes.py`) e envie de novo os arquivos alterados (principalmente `index.html` e `professor.html`, além de `js/`, `data/` e `docs/questoes/`). O site atualiza sozinho em 1 ou 2 minutos.

## Juntar com o site de interpretação de texto

Se você já tem o site de interpretação de texto publicado, há duas opções:

- **Repositórios separados** (mais simples): cada um com seu endereço. Coloque um link de um para o outro no rodapé.
- **Mesmo repositório:** crie uma pasta `matematica/` no repositório existente e coloque este projeto dentro dela. O endereço vira `.../seu-site/matematica/`. Todos os caminhos deste projeto são relativos, então funciona sem mudar nada.
