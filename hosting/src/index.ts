import { timingSafeEqual } from "node:crypto";

class Falha extends Error {
  constructor(public status: number, mensagem: string) { super(mensagem); }
}

type Dados = Record<string, unknown>;

function texto(dados: Dados, campo: string): string {
  const valor = dados[campo];
  if (typeof valor !== "string" || !valor.trim() || valor.length > 2000) {
    throw new Falha(400, `Campo inválido: ${campo}`);
  }
  return valor.trim();
}

function inteiro(dados: Dados, campo: string, max = Number.MAX_SAFE_INTEGER): number {
  const valor = dados[campo];
  if (typeof valor !== "number" || !Number.isSafeInteger(valor) || valor < 1 || valor > max) {
    throw new Falha(400, `Campo inválido: ${campo}`);
  }
  return valor;
}

function existe<T>(registro: T | null): T {
  if (registro === null) throw new Falha(404, "Registro não encontrado para este usuário.");
  return registro;
}

async function corpo(request: Request): Promise<Dados> {
  if (!request.headers.get("content-type")?.startsWith("application/json")) {
    throw new Falha(400, "Envie JSON.");
  }
  const reader = request.body?.getReader();
  if (!reader) throw new Falha(400, "Corpo ausente.");
  const chunks: Uint8Array[] = [];
  let tamanho = 0;
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    tamanho += value.byteLength;
    if (tamanho > 8192) { await reader.cancel(); throw new Falha(413, "Corpo muito grande."); }
    chunks.push(value);
  }
  const bytes = new Uint8Array(tamanho);
  let offset = 0;
  for (const chunk of chunks) { bytes.set(chunk, offset); offset += chunk.length; }
  let dados: unknown;
  try { dados = JSON.parse(new TextDecoder().decode(bytes)); }
  catch { throw new Falha(400, "JSON inválido."); }
  if (!dados || typeof dados !== "object" || Array.isArray(dados)) throw new Falha(400, "Envie um objeto JSON.");
  return dados as Dados;
}

async function executar(db: D1Database, operacao: string, d: Dados): Promise<unknown> {
  switch (operacao) {
    case "verificar_conexao":
      await db.prepare("SELECT id FROM usuarios LIMIT 1").all();
      await db.prepare("SELECT id FROM imoveis LIMIT 1").all();
      await db.prepare("SELECT id FROM consumos LIMIT 1").all();
      return { conectado: true };
    case "salvar_usuario": {
      const r = await db.prepare("INSERT INTO usuarios (nome, email, senha_hash) VALUES (?, ?, ?) RETURNING id")
        .bind(texto(d, "nome"), texto(d, "email").toLowerCase(), texto(d, "senha_hash")).first<{ id: number }>();
      return existe(r).id;
    }
    case "buscar_usuario_por_email":
      return db.prepare("SELECT id, nome, email, senha_hash FROM usuarios WHERE email = ?")
        .bind(texto(d, "email").toLowerCase()).first();
    case "salvar_imovel": {
      const r = await db.prepare("INSERT INTO imoveis (usuario_id, identificacao, localidade, tipo) VALUES (?, ?, ?, ?) RETURNING id")
        .bind(inteiro(d, "usuario_id"), texto(d, "identificacao"), texto(d, "localidade"), texto(d, "tipo"))
        .first<{ id: number }>();
      return existe(r).id;
    }
    case "listar_imoveis":
      return (await db.prepare("SELECT * FROM imoveis WHERE usuario_id = ? ORDER BY id")
        .bind(inteiro(d, "usuario_id")).all()).results;
    case "buscar_imovel":
      return existe(await db.prepare("SELECT * FROM imoveis WHERE id = ? AND usuario_id = ?")
        .bind(inteiro(d, "imovel_id"), inteiro(d, "usuario_id")).first());
    case "atualizar_imovel":
      existe(await db.prepare("UPDATE imoveis SET identificacao = ?, localidade = ?, tipo = ? WHERE id = ? AND usuario_id = ? RETURNING id")
        .bind(texto(d, "identificacao"), texto(d, "localidade"), texto(d, "tipo"), inteiro(d, "imovel_id"), inteiro(d, "usuario_id")).first());
      return null;
    case "excluir_imovel":
      existe(await db.prepare("DELETE FROM imoveis WHERE id = ? AND usuario_id = ? RETURNING id")
        .bind(inteiro(d, "imovel_id"), inteiro(d, "usuario_id")).first());
      return null;
    case "salvar_consumo": {
      const consumo = d.consumo_kwh;
      if (typeof consumo !== "number" || !Number.isFinite(consumo) || consumo < 0) throw new Falha(400, "Consumo inválido.");
      const r = await db.prepare("INSERT INTO consumos (imovel_id, ano, mes, consumo_kwh) SELECT id, ?, ?, ? FROM imoveis WHERE id = ? AND usuario_id = ? RETURNING id")
        .bind(inteiro(d, "ano", 9999), inteiro(d, "mes", 12), consumo, inteiro(d, "imovel_id"), inteiro(d, "usuario_id"))
        .first<{ id: number }>();
      return existe(r).id;
    }
    case "listar_consumos": {
      const imovel = inteiro(d, "imovel_id");
      const usuario = inteiro(d, "usuario_id");
      existe(await db.prepare("SELECT id FROM imoveis WHERE id = ? AND usuario_id = ?").bind(imovel, usuario).first());
      return (await db.prepare("SELECT c.* FROM consumos c JOIN imoveis i ON i.id = c.imovel_id WHERE i.id = ? AND i.usuario_id = ? ORDER BY c.ano, c.mes")
        .bind(imovel, usuario).all()).results;
    }
    default: throw new Falha(404, "Operação não encontrada.");
  }
}

function resposta(dados: unknown, status = 200): Response {
  return Response.json(dados, { status, headers: { "Cache-Control": "no-store" } });
}

export default {
  async fetch(request, env): Promise<Response> {
    try {
      if (!env.TEAM_TOKEN || env.TEAM_TOKEN.length < 32) throw new Falha(503, "Acesso ainda não configurado.");
      const enviado = new TextEncoder().encode(request.headers.get("Authorization") || "");
      const esperado = new TextEncoder().encode(`Bearer ${env.TEAM_TOKEN}`);
      if (enviado.length !== esperado.length || !timingSafeEqual(enviado, esperado)) throw new Falha(401, "Acesso não autorizado.");
      if (request.method !== "POST") throw new Falha(405, "Use POST.");
      const caminho = new URL(request.url).pathname;
      if (!/^\/rpc\/[a-z_]+$/.test(caminho)) throw new Falha(404, "Rota não encontrada.");
      const resultado = await executar(env.DB, caminho.slice(5), await corpo(request));
      return resposta({ resultado });
    } catch (erro) {
      if (erro instanceof Falha) return resposta({ erro: erro.message }, erro.status);
      const mensagem = erro instanceof Error ? erro.message : "";
      if (/UNIQUE constraint|FOREIGN KEY constraint|CHECK constraint|NOT NULL constraint/i.test(mensagem)) {
        return resposta({ erro: "Registro duplicado, vínculo inválido ou imóvel com histórico." }, 409);
      }
      console.error(JSON.stringify({ evento: "falha_persistencia", tipo: "erro_interno" }));
      return resposta({ erro: "Falha ao acessar o banco central." }, 500);
    }
  },
} satisfies ExportedHandler<Env>;
