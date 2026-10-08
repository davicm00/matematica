/* Mundo dos Números — lógica da página do aluno */
(function () {
  "use strict";
  var MN = window.MN, QUESTOES = window.QUESTOES, TEMAS = window.TEMAS;
  if (!MN || !QUESTOES || !TEMAS) {
    if (window.mostrarProblema) window.mostrarProblema("não encontrei os arquivos da pasta js/ (questoes.js ou comum.js).");
    return;
  }
  var POR_RODADA = 10;
  var $ = function (id) { return document.getElementById(id); };

  var estado = {
    nivel: MN.memoria.ler("mn_nivel", 0),
    tema: null,
    fila: [], idx: 0, tentativas: 0, usouDica: false,
    resultados: [], escolha: null, digitado: "", ordem: [], respondida: false
  };
  var vistas = {};
  MN.memoria.ler("mn_vistas", []).forEach(function (id) { vistas[id] = true; });
  var progresso = MN.memoria.ler("mn_progresso", {});
  var estrelas = MN.memoria.ler("mn_estrelas", 0);

  /* ----------------------------- início ----------------------------- */
  function mostrarTela(id) {
    ["telaInicio", "telaQuiz", "telaResultado"].forEach(function (t) { $(t).classList.toggle("oculto", t !== id); });
    window.scrollTo(0, 0);
  }

  function atualizarEstrelas() { $("estrelasTotal").textContent = "⭐ " + estrelas; }

  function saudacao() {
    var nome = MN.memoria.ler("mn_nome", "");
    $("nome").value = nome;
    $("saudacao").textContent = nome ? "Olá, " + nome + "! Vamos contar? 🦉" : "Olá! Eu sou a Corujinha Conta! 🦉";
  }

  function desenharTemas() {
    var html = "";
    TEMAS.forEach(function (t) {
      var doTema = QUESTOES.filter(function (q) { return q.tema === t.id; });
      var vistasTema = doTema.filter(function (q) { return vistas[q.id]; }).length;
      var pct = Math.round((vistasTema / doTema.length) * 100);
      var p = progresso[t.id];
      var acertoTxt = p && p.respondidas ? " • " + Math.round((p.acertos / p.respondidas) * 100) + "% de acertos" : "";
      html += '<button class="tema" style="--cor:' + t.cor + '" data-tema="' + t.id + '">' +
        '<span class="icone" aria-hidden="true">' + t.icone + '</span>' +
        '<span class="nome">' + MN.esc(t.nome) + '</span>' +
        '<span class="info">' + vistasTema + ' de ' + doTema.length + ' perguntas' + acertoTxt + '</span>' +
        '<span class="barra" aria-hidden="true"><span style="width:' + pct + '%"></span></span>' +
        '</button>';
    });
    $("listaTemas").innerHTML = html;
  }

  function marcarNivel() {
    document.querySelectorAll(".nivel").forEach(function (b) {
      b.setAttribute("aria-pressed", String(Number(b.dataset.nivel) === estado.nivel));
    });
  }

  /* --------------------------- montar rodada --------------------------- */
  function sortearFila(temaId) {
    var doTema = QUESTOES.filter(function (q) { return !temaId || q.tema === temaId; });
    var pool = doTema.filter(function (q) { return !estado.nivel || q.nivel === estado.nivel; });
    if (pool.length < POR_RODADA) {
      // poucas questões nesse nível: completa com o nível mais próximo
      var extra = doTema.filter(function (q) { return pool.indexOf(q) < 0; })
        .sort(function (a, b) { return Math.abs(a.nivel - estado.nivel) - Math.abs(b.nivel - estado.nivel); });
      pool = pool.concat(extra.slice(0, POR_RODADA - pool.length));
    }
    // prioriza perguntas que a criança ainda não viu
    var novas = MN.embaralhar(pool.filter(function (q) { return !vistas[q.id]; }));
    var velhas = MN.embaralhar(pool.filter(function (q) { return vistas[q.id]; }));
    var fila = novas.concat(velhas).slice(0, POR_RODADA);
    if (!temaId) {
      // na rodada misturada, evita repetir tema seguido quando possível
      fila.sort(function () { return Math.random() - 0.5; });
    } else if (estado.nivel === 0) {
      fila.sort(function (a, b) { return a.nivel - b.nivel; }); // do mais fácil ao mais difícil
    }
    return fila;
  }

  function comecar(temaId) {
    estado.tema = temaId;
    estado.fila = sortearFila(temaId);
    estado.idx = 0;
    estado.resultados = [];
    var t = temaId ? MN.temaPorId(temaId) : null;
    $("quizTitulo").textContent = t ? t.icone + " " + t.nome : "🌈 Todos os assuntos";
    mostrarTela("telaQuiz");
    mostrarQuestao();
  }

  /* --------------------------- questão --------------------------- */
  function atual() { return estado.fila[estado.idx]; }

  function desenharBolinhas() {
    var h = "";
    for (var i = 0; i < estado.fila.length; i++) {
      var c = estado.resultados[i] || (i === estado.idx ? "atual" : "");
      h += '<span class="' + c + '" title="Pergunta ' + (i + 1) + '"></span>';
    }
    $("bolinhas").innerHTML = h;
  }

  function mostrarQuestao() {
    var q = atual();
    estado.tentativas = 0; estado.usouDica = false; estado.escolha = null;
    estado.digitado = ""; estado.ordem = []; estado.respondida = false;
    desenharBolinhas();
    $("cartao").dataset.id = q.id;

    var t = MN.temaPorId(q.tema);
    $("etiquetas").innerHTML =
      '<span class="etiqueta">Pergunta ' + (estado.idx + 1) + ' de ' + estado.fila.length + '</span>' +
      '<span class="etiqueta">' + MN.NIVEIS[q.nivel] + '</span>' +
      (estado.tema ? "" : '<span class="etiqueta">' + t.icone + " " + MN.esc(t.nome) + '</span>');
    $("enunciado").textContent = q.enunciado;
    $("visual").classList.toggle("oculto", !q.visual);
    $("visual").textContent = q.visual || "";
    $("relogio").classList.toggle("oculto", !q.relogio);
    $("relogio").innerHTML = q.relogio ? MN.relogioSVG(q.relogio.h, q.relogio.m) : "";
    $("caixaDica").classList.add("oculto");
    $("retorno").classList.add("oculto");
    $("btnDica").classList.remove("oculto");
    $("btnDica").disabled = !q.dica;
    $("btnConferir").classList.remove("oculto");
    $("btnProxima").classList.add("oculto");

    if (q.tipo === "multipla") desenharOpcoes(q);
    else if (q.tipo === "numero") desenharTeclado();
    else desenharOrdenar(q);
    atualizarConferir();
  }

  function desenharOpcoes(q) {
    var sinais = q.opcoes.every(function (o) { return o.length === 1; });
    var h = '<div class="opcoes' + (sinais ? " sinais" : "") + '">';
    q.opcoes.forEach(function (o, i) {
      h += '<button class="opcao" data-i="' + i + '">' + MN.esc(o) + '</button>';
    });
    $("areaResposta").innerHTML = h + "</div>";
    $("areaResposta").querySelectorAll(".opcao").forEach(function (b) {
      b.addEventListener("click", function () {
        if (estado.respondida) return;
        estado.escolha = q.opcoes[Number(b.dataset.i)];
        $("areaResposta").querySelectorAll(".opcao").forEach(function (x) { x.classList.remove("marcada", "errada"); });
        b.classList.add("marcada");
        atualizarConferir();
      });
    });
  }

  function desenharTeclado() {
    var h = '<div class="numero-area"><div class="visor vazio" id="visor" aria-live="polite">?</div><div class="teclado">';
    [1, 2, 3, 4, 5, 6, 7, 8, 9].forEach(function (n) { h += '<button class="tecla" data-t="' + n + '">' + n + '</button>'; });
    h += '<button class="tecla apagar" data-t="limpar" aria-label="Limpar">🧽</button>';
    h += '<button class="tecla" data-t="0">0</button>';
    h += '<button class="tecla apagar" data-t="apagar" aria-label="Apagar">⌫</button></div></div>';
    $("areaResposta").innerHTML = h;
    $("areaResposta").querySelectorAll(".tecla").forEach(function (b) {
      b.addEventListener("click", function () { teclar(b.dataset.t); });
    });
  }

  function teclar(t) {
    if (estado.respondida) return;
    if (t === "apagar") estado.digitado = estado.digitado.slice(0, -1);
    else if (t === "limpar") estado.digitado = "";
    else if (estado.digitado.length < 3) estado.digitado = (estado.digitado === "0" ? "" : estado.digitado) + t;
    var v = $("visor");
    v.textContent = estado.digitado || "?";
    v.classList.toggle("vazio", !estado.digitado);
    v.classList.remove("errada");
    atualizarConferir();
  }

  function desenharOrdenar(q) {
    var embaralhados = q.itens.slice();
    var h = '<div class="ordenar-resp" id="ordResp"><span class="vazio">Toque nos números abaixo 👇</span></div>' +
      '<div class="ordenar-itens" id="ordItens">';
    embaralhados.forEach(function (it, i) { h += '<button class="ficha" data-i="' + i + '">' + MN.esc(it) + '</button>'; });
    $("areaResposta").innerHTML = h + "</div>";
    $("ordItens").querySelectorAll(".ficha").forEach(function (b) {
      b.addEventListener("click", function () {
        if (estado.respondida || b.disabled) return;
        estado.ordem.push(Number(b.dataset.i));
        b.disabled = true;
        desenharOrdem(q);
      });
    });
  }

  function desenharOrdem(q) {
    var r = $("ordResp");
    if (!estado.ordem.length) { r.innerHTML = '<span class="vazio">Toque nos números abaixo 👇</span>'; atualizarConferir(); return; }
    r.innerHTML = estado.ordem.map(function (i, pos) {
      return '<button class="ficha" data-pos="' + pos + '" title="Tirar">' + MN.esc(q.itens[i]) + '</button>';
    }).join("");
    r.querySelectorAll(".ficha").forEach(function (b) {
      b.addEventListener("click", function () {
        if (estado.respondida) return;
        var i = estado.ordem.splice(Number(b.dataset.pos), 1)[0];
        $("ordItens").querySelector('[data-i="' + i + '"]').disabled = false;
        desenharOrdem(q);
      });
    });
    atualizarConferir();
  }

  function temResposta() {
    var q = atual();
    if (q.tipo === "multipla") return estado.escolha !== null;
    if (q.tipo === "numero") return estado.digitado !== "";
    return estado.ordem.length === q.itens.length;
  }

  function atualizarConferir() { $("btnConferir").disabled = !temResposta(); }

  function estaCerta() {
    var q = atual();
    if (q.tipo === "multipla") return estado.escolha === q.resposta;
    if (q.tipo === "numero") return Number(estado.digitado) === q.resposta;
    return estado.ordem.map(function (i) { return q.itens[i]; }).join("|") === q.resposta.join("|");
  }

  /* --------------------------- conferir --------------------------- */
  var ELOGIOS = ["Muito bem!", "Isso aí!", "Arrasou!", "Que cabeça boa!", "Mandou bem!", "Perfeito!", "Show de bola!", "Você é fera!"];

  function conferir() {
    if (!temResposta() || estado.respondida) return;
    var q = atual(), ok = estaCerta();
    estado.tentativas++;
    var ret = $("retorno");
    ret.classList.remove("oculto", "certo", "errado", "quase");

    if (ok) {
      finalizar(estado.tentativas === 1 ? "ok" : "quase", true);
      ret.classList.add("certo");
      ret.innerHTML = "<strong>🎉 " + ELOGIOS[Math.floor(Math.random() * ELOGIOS.length)] + "</strong>" + MN.esc(q.explicacao);
      $("cartao").classList.remove("pular"); void $("cartao").offsetWidth; $("cartao").classList.add("pular");
      marcarCertaNaTela(q);
    } else if (estado.tentativas === 1) {
      ret.classList.add("quase");
      ret.innerHTML = "<strong>🤔 Quase! Tente outra vez.</strong>Leia a dica com calma.";
      mostrarDica();
      $("cartao").classList.remove("tremer"); void $("cartao").offsetWidth; $("cartao").classList.add("tremer");
      limparTentativa(q);
    } else {
      finalizar("erro", false);
      ret.classList.add("errado");
      ret.innerHTML = "<strong>💪 Não foi dessa vez!</strong>A resposta certa é <b>" + MN.esc(MN.respostaTexto(q)) +
        "</b>. " + MN.esc(q.explicacao);
      marcarCertaNaTela(q);
    }
  }

  function limparTentativa(q) {
    if (q.tipo === "multipla") {
      $("areaResposta").querySelectorAll(".opcao.marcada").forEach(function (b) {
        b.classList.remove("marcada"); b.classList.add("errada");
      });
      estado.escolha = null;
    } else if (q.tipo === "numero") {
      estado.digitado = "";
      $("visor").textContent = "?"; $("visor").classList.add("vazio");
    } else {
      estado.ordem = [];
      $("ordItens").querySelectorAll(".ficha").forEach(function (b) { b.disabled = false; });
      desenharOrdem(q);
    }
    atualizarConferir();
  }

  function marcarCertaNaTela(q) {
    if (q.tipo === "multipla") {
      $("areaResposta").querySelectorAll(".opcao").forEach(function (b) {
        b.disabled = true;
        b.classList.remove("marcada");
        if (b.textContent === q.resposta) b.classList.add("certa");
        else if (b.textContent === estado.escolha) b.classList.add("errada");
      });
    } else if (q.tipo === "numero") {
      $("visor").textContent = q.resposta; $("visor").classList.remove("vazio");
    } else {
      $("ordResp").innerHTML = q.resposta.map(function (r) { return '<span class="ficha">' + MN.esc(r) + '</span>'; }).join("");
      $("ordItens").innerHTML = "";
    }
  }

  function finalizar(status, acertou) {
    var q = atual();
    estado.respondida = true;
    estado.resultados[estado.idx] = status;
    vistas[q.id] = true;
    MN.memoria.gravar("mn_vistas", Object.keys(vistas));
    var p = progresso[q.tema] || { acertos: 0, respondidas: 0 };
    p.respondidas++; if (acertou) p.acertos++;
    progresso[q.tema] = p;
    MN.memoria.gravar("mn_progresso", progresso);
    if (acertou) { estrelas++; MN.memoria.gravar("mn_estrelas", estrelas); atualizarEstrelas(); }
    desenharBolinhas();
    $("btnConferir").classList.add("oculto");
    $("btnDica").classList.add("oculto");
    var ultima = estado.idx === estado.fila.length - 1;
    $("btnProxima").textContent = ultima ? "Ver resultado 🏁" : "Próxima ➜";
    $("btnProxima").classList.remove("oculto");
    $("btnProxima").focus();
  }

  function mostrarDica() {
    var q = atual();
    if (!q.dica) return;
    estado.usouDica = true;
    $("caixaDica").innerHTML = "💡 <b>Dica:</b> " + MN.esc(q.dica);
    $("caixaDica").classList.remove("oculto");
  }

  function proxima() {
    if (estado.idx < estado.fila.length - 1) { estado.idx++; mostrarQuestao(); window.scrollTo(0, 0); }
    else mostrarResultado();
  }

  /* --------------------------- resultado --------------------------- */
  function mostrarResultado() {
    var total = estado.fila.length;
    var acertos = estado.resultados.filter(function (r) { return r !== "erro"; }).length;
    var deprimeira = estado.resultados.filter(function (r) { return r === "ok"; }).length;
    var nome = MN.memoria.ler("mn_nome", "");
    var titulo, emoji;
    if (acertos === total) { emoji = "🏆"; titulo = "Incrível" + (nome ? ", " + nome : "") + "! Acertou tudo!"; }
    else if (acertos >= total * 0.7) { emoji = "🥳"; titulo = "Muito bem" + (nome ? ", " + nome : "") + "!"; }
    else if (acertos >= total * 0.4) { emoji = "😊"; titulo = "Bom trabalho!"; }
    else { emoji = "🌱"; titulo = "Continue treinando, você vai longe!"; }
    $("resEmoji").textContent = emoji;
    $("resTitulo").textContent = titulo;
    $("resTexto").textContent = "Você acertou " + acertos + " de " + total + " perguntas (" + deprimeira + " de primeira!).";
    $("resEstrelas").textContent = new Array(acertos + 1).join("⭐") || "🌱";

    var erros = estado.fila.filter(function (q, i) { return estado.resultados[i] === "erro"; });
    if (erros.length) {
      $("revisao").innerHTML = "<h3>Vamos revisar?</h3><ol>" + erros.map(function (q) {
        return "<li><b>" + MN.esc(q.enunciado) + "</b>" + (q.visual ? "<br>" + MN.esc(q.visual) : "") +
          "<br>Resposta: <b>" + MN.esc(MN.respostaTexto(q)) + "</b> — " + MN.esc(q.explicacao) + "</li>";
      }).join("") + "</ol>";
      $("revisao").classList.remove("oculto");
    } else {
      $("revisao").classList.add("oculto");
    }
    mostrarTela("telaResultado");
    if (acertos >= total * 0.7) confete();
  }

  function confete() {
    var simbolos = ["⭐", "🎉", "✨", "🎈", "🌟", "🔢"];
    for (var i = 0; i < 28; i++) {
      var s = document.createElement("span");
      s.className = "confete";
      s.textContent = simbolos[i % simbolos.length];
      s.style.left = Math.random() * 100 + "vw";
      s.style.animationDelay = Math.random() * 0.8 + "s";
      document.body.appendChild(s);
      setTimeout(function (el) { el.remove(); }, 2600, s);
    }
  }

  /* --------------------------- ouvir --------------------------- */
  function falar() {
    if (!("speechSynthesis" in window)) return;
    var q = atual();
    var t = q.enunciado
      .replace(/___/g, " quanto ")
      .replace(/−/g, " menos ").replace(/\+/g, " mais ").replace(/=/g, " igual a ")
      .replace(/ < /g, " menor que ").replace(/ > /g, " maior que ")
      .replace(/[\uD800-\uDFFF]/g, " ").replace(/[\u2190-\u2BFF\uFE0F\u200D]/g, " ");
    if (q.tipo === "multipla") t += ". As opções são: " + q.opcoes.map(function (o) {
      return o === "<" ? "menor que" : o === ">" ? "maior que" : o === "=" ? "igual" : o.replace(/−/g, " menos ").replace(/\+/g, " mais ");
    }).join("; ");
    window.speechSynthesis.cancel();
    var u = new SpeechSynthesisUtterance(t);
    u.lang = "pt-BR"; u.rate = 0.9;
    var vozes = window.speechSynthesis.getVoices().filter(function (v) { return /pt(-|_)BR/i.test(v.lang); });
    if (vozes.length) u.voice = vozes[0];
    window.speechSynthesis.speak(u);
  }

  /* --------------------------- eventos --------------------------- */
  $("listaTemas").addEventListener("click", function (e) {
    var b = e.target;
    while (b && b !== this && !(b.classList && b.classList.contains("tema"))) b = b.parentNode;
    if (b === this) b = null;
    if (b) comecar(b.dataset.tema);
  });
  $("btnMisturar").addEventListener("click", function () { comecar(null); });
  document.querySelectorAll(".nivel").forEach(function (b) {
    b.addEventListener("click", function () {
      estado.nivel = Number(b.dataset.nivel);
      MN.memoria.gravar("mn_nivel", estado.nivel);
      marcarNivel();
    });
  });
  $("nome").addEventListener("input", function () {
    MN.memoria.gravar("mn_nome", $("nome").value.trim());
    var n = $("nome").value.trim();
    $("saudacao").textContent = n ? "Olá, " + n + "! Vamos contar? 🦉" : "Olá! Eu sou a Corujinha Conta! 🦉";
  });
  $("btnConferir").addEventListener("click", conferir);
  $("btnDica").addEventListener("click", mostrarDica);
  $("btnProxima").addEventListener("click", proxima);
  $("btnOuvir").addEventListener("click", falar);
  $("btnSair").addEventListener("click", function () { desenharTemas(); mostrarTela("telaInicio"); });
  $("btnDeNovo").addEventListener("click", function () { comecar(estado.tema); });
  $("btnInicio").addEventListener("click", function () { desenharTemas(); mostrarTela("telaInicio"); });

  document.addEventListener("keydown", function (e) {
    if ($("telaQuiz").classList.contains("oculto") || e.target.tagName === "INPUT") return;
    var q = atual();
    if (!q) return;
    var k = e.key || "", c = e.keyCode || 0;
    if (!k && c >= 48 && c <= 57) k = String(c - 48);
    if (!k && c >= 96 && c <= 105) k = String(c - 96);
    if (c === 8) k = "Backspace";
    if (c === 13) k = "Enter";
    if (/^[0-9]$/.test(k) && q.tipo === "numero") { teclar(k); e.preventDefault(); }
    else if (k === "Backspace" && q.tipo === "numero") { teclar("apagar"); e.preventDefault(); }
    else if (k === "Enter") {
      if (estado.respondida) proxima(); else conferir();
      e.preventDefault();
    }
  });

  saudacao();
  marcarNivel();
  desenharTemas();
  atualizarEstrelas();
  window.MN_OK = true;
})();
