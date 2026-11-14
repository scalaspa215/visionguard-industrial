/*
 Verificacion estatica del workflow exportado:
  - toda conexion apunta a un nodo existente;
  - el codigo de cada nodo Code JS compila; expresiones {{ }} de Gmail/Telegram compilan;
  - el archivo PUBLICO no contiene credenciales, correos reales, IDs de chat ni tokens.
 Uso: node verificar_workflow.js
*/
const fs = require('fs');
const path = require('path');
const N8N = path.join(__dirname, '..', 'n8n');
const salida = [];
const ok = (c, msg) => { salida.push((c ? 'OK    ' : 'FALLA ') + msg); return c; };

for (const archivo of ['VisionGuard_v2.2_Hito2_IMPORTAR.json', 'VisionGuard_v2.2_Hito2_PUBLICO.json', 'VisionGuard_v2.2_Error_Handler_PUBLICO.json']) {
  const texto = fs.readFileSync(path.join(N8N, archivo), 'utf8');
  const w = JSON.parse(texto);
  const nombres = new Set(w.nodes.map(n => n.name));
  ok(nombres.size === w.nodes.length, `${archivo}: nombres de nodo unicos (${w.nodes.length})`);
  let malas = [];
  for (const [src, tipos] of Object.entries(w.connections)) {
    if (!nombres.has(src)) malas.push('origen ' + src);
    for (const salidas of Object.values(tipos)) for (const s of salidas || []) for (const c of s || []) if (!nombres.has(c.node)) malas.push(src + '->' + c.node);
  }
  ok(malas.length === 0, `${archivo}: conexiones validas ${malas.join(', ')}`);
  let errores = [];
  for (const n of w.nodes) {
    if (n.type === 'n8n-nodes-base.code' && n.parameters.jsCode) {
      try { new Function('$input', '$', '$now', n.parameters.jsCode); } catch (e) { errores.push(n.name + ': ' + e.message); }
    }
    for (const [k, v] of Object.entries(n.parameters || {})) {
      if (typeof v === 'string' && v.startsWith('=') && v.includes('{{')) {
        const exprs = [...v.matchAll(/\{\{([\s\S]*?)\}\}(?!\})/g)].map(m => m[1]);
        for (const ex of exprs) {
          try { new Function('$json', '$', '$now', 'return (' + ex + ');'); } catch (e) { errores.push(`${n.name}.${k}: ${e.message}`); }
        }
      }
    }
  }
  ok(errores.length === 0, `${archivo}: codigo y expresiones compilan ${errores.join(' | ')}`);
  if (archivo.includes('PUBLICO')) {
    // Valores privados leidos del archivo IMPORTAR (no se escriben aqui para no publicarlos).
    const privados = [];
    try {
      const imp = JSON.parse(fs.readFileSync(path.join(N8N, 'VisionGuard_v2.2_Hito2_IMPORTAR.json'), 'utf8'));
      const cfg = imp.nodes.find(n => n.name === 'Config').parameters.assignments.assignments;
      for (const k of ['email_responsable', 'telegram_chat_id']) privados.push(String(cfg.find(a => a.name === k).value));
      const sheet = (JSON.stringify(imp).match(/spreadsheets\/d\/([A-Za-z0-9_-]{20,})/) || [])[1];
      if (sheet) privados.push(sheet);
    } catch (e) { /* sin archivo IMPORTAR: solo patrones genericos */ }
    const esc = s => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const prohibido = [/@gmail\.com/i, /"credentials"/, /sk-[A-Za-z0-9]{20,}/, /hf_[A-Za-z0-9]{20,}/,
      /\d{8,10}:[A-Za-z0-9_-]{35}/, /BEGIN PRIVATE KEY/, /instanceId/, ...privados.map(p => new RegExp(esc(p)))];
    const hallados = prohibido.filter(r => r.test(texto)).map(String);
    ok(hallados.length === 0, `${archivo}: sin credenciales ni datos personales ${hallados.join(', ')}`);
  }
}
const imp = JSON.parse(fs.readFileSync(path.join(N8N, 'VisionGuard_v2.2_Hito2_IMPORTAR.json'), 'utf8'));
const by = Object.fromEntries(imp.nodes.map(n => [n.name, n]));
ok(!by['Send a message1'].disabled, 'Alerta Gmail de API caida habilitada');
ok(by['Message a model'].disabled && !JSON.stringify(imp.connections['HTTP Request']).includes('Message a model'), 'Rama legado H1 desconectada');
ok(imp.connections['Loop_Inspecciones'].main[1].some(c => c.node === 'Aprobacion_Humana_Integrada'), 'Aprobacion humana dentro del bucle por pieza');
ok(imp.connections['Notificacion_Final_Telegram'].main[0][0].node === 'Loop_Inspecciones', 'Bucle cierra tras notificacion final');
ok(imp.connections['Preparar_Registro_Integrado'].main[0][0].node === 'Evitar_Notificaciones_Duplicadas', 'Dedupe antes de guardar');
ok(by['Clasificar_NLP_Python'].parameters.language === 'pythonNative', 'Nodo NLP en Python');
console.log(salida.join('\n'));
fs.writeFileSync(path.join(__dirname, 'resultado_verificacion_workflow.txt'), salida.join('\n'));
