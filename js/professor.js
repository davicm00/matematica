/* Mundo dos Números — área do professor */
(function () {
  "use strict";
  var MN = window.MN, QUESTOES = window.QUESTOES, TEMAS = window.TEMAS;
  if (!MN || !QUESTOES || !TEMAS) {
    if (window.mostrarProblema) window.mostrarProblema("não encontrei os arquivos da pasta js/ (questoes.js ou comum.js).");
    return;
  }
  var $ = function (id) { return document.getElementById(id); };
  var PASSO = 60, mostrando = PASSO, filtradas = [];

  // resumo
  var r = '<div><b>' + QUESTOES.length + '</b>questões no total</div>';
  TEMAS.forEach(function (t) {
    var n = QUESTOES.filter(function (q) { return q.tema === t.id; }).length;
    r += '<div>' + t.icone + ' ' + MN.esc(t.nome) + '<b>' + n + '</b></div>';
    $("fTema").insertAdjacentHTML("beforeend", '<option value="' + t.id + '">' + t.icone + " " + MN.esc(t.nome) + "</option>");
  });
  $("resumo").innerHTML = r;

  function filtrar() {
    var tema = $("fTema").value, nivel = $("fNivel").value, tipo = $("fTipo").value;
    var busca = $("fBusca").value.trim().toLowerCase();
    filtradas = QUESTOES.filter(function (q) {
      if (tema && q.tema !== tema) return false;
      if (nivel && String(q.nivel) !== nivel) return false;
      if (tipo && q.tipo !== tipo) return false;
      if (busca) {
        var alvo = (q.id + " " + q.enunciado + " " + (q.visual || "") + " " + q.explicacao + " " +
          (q.relogio ? "relógio" : "")).toLowerCase();
        if (alvo.indexOf(busca) < 0) return false;
      }
      return true;
    });
    mostrando = PASSO;
    desenhar();
  }

  function itemHTML(q) {
    var t = MN.temaPorId(q.tema);
    var h = '<li><div class="cab"><span>' + q.id + '</span><span>' + t.icone + " " + MN.esc(t.nome) + '</span><span>' +
      MN.NIVEIS[q.nivel] + '</span><span>' + MN.TIPOS[q.tipo] + '</span><span>BNCC ' + q.bncc + '</span></div>';
    h += '<div class="q-enun">' + MN.esc(q.enunciado) + '</div>';
    if (q.visual) h += '<div class="q-vis">' + MN.esc(q.visual) + '</div>';
    if (q.relogio) h += MN.relogioSVG(q.relogio.h, q.relogio.m);
    if (q.opcoes) h += '<div class="q-op">Opções: ' + q.opcoes.map(MN.esc).join(" • ") + '</div>';
    if (q.itens) h += '<div class="q-op">Números: ' + q.itens.map(MN.esc).join(" • ") + '</div>';
    h += '<div class="q-resp">✔ ' + MN.esc(MN.respostaTexto(q)) + '</div>';
    h += '<div class="q-exp">💡 ' + MN.esc(q.dica) + '<br>📝 ' + MN.esc(q.explicacao) + '</div></li>';
    return h;
  }

  function desenhar() {
    $("contagem").textContent = filtradas.length + " questões encontradas";
    $("lista").innerHTML = filtradas.slice(0, mostrando).map(itemHTML).join("");
    $("btnMais").classList.toggle("oculto", mostrando >= filtradas.length);
  }

  function gerarFolha() {
    var qtd = Math.max(1, Math.min(60, Number($("fQtd").value) || 12));
    var escolhidas = MN.embaralhar(filtradas).slice(0, qtd).sort(function (a, b) { return a.nivel - b.nivel; });
    if (!escolhidas.length) { alert("Nenhuma questão com esses filtros."); return; }
    var h = '<div class="cabecalho"><h1>' + MN.esc($("fTitulo").value || "Atividade de Matemática") + '</h1>' +
      'Nome: ______________________________________ &nbsp; Data: ____/____/______</div><ol>';
    escolhidas.forEach(function (q) {
      h += "<li>" + MN.esc(q.enunciado);
      if (q.visual) h += '<div class="vis">' + MN.esc(q.visual) + "</div>";
      if (q.relogio) h += MN.relogioSVG(q.relogio.h, q.relogio.m);
      if (q.tipo === "multipla") h += "<div>" + q.opcoes.map(function (o) { return '<span class="op">( ) ' + MN.esc(o) + "</span>"; }).join(" &nbsp; ") + "</div>";
      else if (q.tipo === "ordenar") h += "<div>" + q.itens.map(MN.esc).join(" &nbsp; ") + '</div><div>Resposta: <span class="linha-resp" style="min-width:220pt"></span></div>';
      else h += '<div>Resposta: <span class="linha-resp"></span></div>';
      h += "</li>";
    });
    h += "</ol>";
    if ($("fGab").value === "1") {
      h += '<div class="gabarito"><h1>Gabarito</h1><ol>' + escolhidas.map(function (q) {
        return "<li><b>" + MN.esc(MN.respostaTexto(q)) + "</b> — " + MN.esc(q.explicacao) + " <small>(" + q.id + ")</small></li>";
      }).join("") + "</ol></div>";
    }
    $("folha").innerHTML = h;
    window.print();
  }

  ["fTema", "fNivel", "fTipo"].forEach(function (id) { $(id).addEventListener("change", filtrar); });
  $("fBusca").addEventListener("input", filtrar);
  $("btnMais").addEventListener("click", function () { mostrando += PASSO; desenhar(); });
  $("btnFolha").addEventListener("click", gerarFolha);
  filtrar();
  window.MN_OK = true;
})();
