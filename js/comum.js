/* Funções usadas pelas duas páginas (aluno e professor). */
(function () {
  "use strict";

  /* Compatibilidade com navegadores antigos (tablets e computadores de escola). */
  if (window.NodeList && !NodeList.prototype.forEach) NodeList.prototype.forEach = Array.prototype.forEach;

  /** Desenha um relógio de ponteiros em SVG. */
  function relogioSVG(h, m) {
    var cx = 100, cy = 100, s = "";
    s += '<svg viewBox="0 0 200 200" role="img" aria-label="Relógio de ponteiros">';
    s += '<circle cx="100" cy="100" r="92" fill="#fff" stroke="#2d2a4a" stroke-width="7"/>';
    for (var i = 0; i < 60; i++) {
      var a = (i / 60) * 2 * Math.PI, grande = i % 5 === 0;
      var r1 = grande ? 76 : 82, r2 = 86;
      s += '<line x1="' + (cx + r1 * Math.sin(a)).toFixed(1) + '" y1="' + (cy - r1 * Math.cos(a)).toFixed(1) +
        '" x2="' + (cx + r2 * Math.sin(a)).toFixed(1) + '" y2="' + (cy - r2 * Math.cos(a)).toFixed(1) +
        '" stroke="#2d2a4a" stroke-width="' + (grande ? 3 : 1) + '" stroke-linecap="round"/>';
    }
    for (var n = 1; n <= 12; n++) {
      var an = (n / 12) * 2 * Math.PI;
      s += '<text x="' + (cx + 64 * Math.sin(an)).toFixed(1) + '" y="' + (cy - 64 * Math.cos(an) + 7).toFixed(1) +
        '" text-anchor="middle" font-family="Baloo 2, sans-serif" font-size="20" font-weight="700" fill="#2d2a4a">' + n + '</text>';
    }
    var ah = ((h % 12) + m / 60) / 12 * 2 * Math.PI;
    var am = (m / 60) * 2 * Math.PI;
    s += '<line x1="100" y1="100" x2="' + (cx + 36 * Math.sin(ah)).toFixed(1) + '" y2="' + (cy - 36 * Math.cos(ah)).toFixed(1) +
      '" stroke="#ef5b6c" stroke-width="9" stroke-linecap="round"/>';
    s += '<line x1="100" y1="100" x2="' + (cx + 52 * Math.sin(am)).toFixed(1) + '" y2="' + (cy - 52 * Math.cos(am)).toFixed(1) +
      '" stroke="#6d5df0" stroke-width="6" stroke-linecap="round"/>';
    s += '<circle cx="100" cy="100" r="7" fill="#2d2a4a"/></svg>';
    return s;
  }

  function esc(t) {
    return String(t).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function embaralhar(lista) {
    var a = lista.slice();
    for (var i = a.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var t = a[i]; a[i] = a[j]; a[j] = t;
    }
    return a;
  }

  function respostaTexto(q) {
    return Array.isArray(q.resposta) ? q.resposta.join(" → ") : String(q.resposta);
  }

  var NIVEIS = { 1: "🌱 Fácil", 2: "🌿 Médio", 3: "🌳 Desafio" };
  var TIPOS = { multipla: "Múltipla escolha", numero: "Resposta numérica", ordenar: "Ordenar" };

  function temaPorId(id) {
    for (var i = 0; i < window.TEMAS.length; i++) if (window.TEMAS[i].id === id) return window.TEMAS[i];
    return null;
  }

  /* localStorage pode falhar (aba anônima, bloqueios) — o site continua funcionando sem ele. */
  var memoria = {
    ler: function (chave, padrao) {
      try { var v = localStorage.getItem(chave); return v ? JSON.parse(v) : padrao; } catch (e) { return padrao; }
    },
    gravar: function (chave, valor) {
      try { localStorage.setItem(chave, JSON.stringify(valor)); } catch (e) { /* sem memória */ }
    }
  };

  window.MN = { relogioSVG: relogioSVG, esc: esc, embaralhar: embaralhar, respostaTexto: respostaTexto,
    NIVEIS: NIVEIS, TIPOS: TIPOS, temaPorId: temaPorId, memoria: memoria };
})();
