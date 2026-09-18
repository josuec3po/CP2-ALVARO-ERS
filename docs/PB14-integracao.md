# PB14 — Persistência

Banco central: **Cloudflare D1**, `cp2-alvaro-ers`.
API: `https://cp2-alvaro-pb14.atzagenda.workers.dev`.

## Tasks

| Task | Critério de conclusão |
| --- | --- |
| T01 — Definir o modelo e criar o banco hospedado | Tabelas de usuários, imóveis e consumos com relacionamentos |
| T02 — Implementar as rotinas de persistência | Conexão Python e gravação, consulta, atualização e exclusão de imóveis |
| T03 — Validar a persistência e a integração | Recuperar registros após encerrar o programa e verificar os vínculos entre módulos |

A persistência está implementada e integrada a PB03/PB04. O aceite completo do
sistema depende da integração dos módulos de autenticação e consumo.

## Configuração

Requisito: Python 3.10 ou superior, sem dependências externas para o cliente.
Cada integrante recebe a chave de acesso por canal privado e executa:

```powershell
python configurar_conexao.py
python persistencia.py
```

A configuração fica em `.pb14.local.json`, ignorado pelo Git. A URL padrão está em
`database/servidor.json`. Também são aceitas `PB14_API_URL` e `PB14_API_TOKEN`.
A chave não deve ser publicada no repositório ou incorporada a frontend público.

## Modelo

| Tabela | Campos e vínculos |
| --- | --- |
| `usuarios` | `id`, `nome`, `email` único, `senha_hash` |
| `imoveis` | `id`, `usuario_id`, `identificacao`, `localidade`, `tipo` |
| `consumos` | `id`, `imovel_id`, `ano`, `mes`, `consumo_kwh`; combinação imóvel/ano/mês única |

Consumo deve ser finito e não negativo; mês de 1 a 12; ano de 1 a 9999.
Imóveis com histórico têm exclusão bloqueada. Campos obrigatórios não aceitam vazio.

## Interface Python

```python
from persistencia import BancoDados

banco = BancoDados()
banco.inicializar()  # Verifica a conexão; não recria as tabelas.
```

| Método | Retorno |
| --- | --- |
| `salvar_usuario(nome, email, senha_hash)` | ID criado |
| `buscar_usuario_por_email(email)` | Usuário com hash, ou `None`; uso interno do login |
| `salvar_imovel(usuario_id, identificacao, localidade, tipo)` | ID criado |
| `listar_imoveis(usuario_id)` | Lista de imóveis da conta |
| `buscar_imovel(usuario_id, imovel_id)` | Imóvel da conta |
| `atualizar_imovel(usuario_id, imovel_id, identificacao, localidade, tipo)` | `None` após sucesso |
| `excluir_imovel(usuario_id, imovel_id)` | `None` após sucesso |
| `salvar_consumo(usuario_id, imovel_id, ano, mes, consumo_kwh)` | ID criado |
| `listar_consumos(usuario_id, imovel_id)` | Lista em ordem de ano/mês |

Listagens vazias retornam `[]`. Erros: `RegistroNaoEncontrado` para imóvel ausente ou
vínculo incorreto; `ValueError` para entrada inválida; `sqlite3.IntegrityError` para
conflitos de integridade; `ErroConexao` para falha de acesso ao serviço.

PB01/PB02 geram/verificam hashes e fornecem o ID da sessão. A chave da API é uma
credencial técnica da equipe e não autentica o usuário final. O cliente não usa
um banco local como alternativa quando a rede falha.

## Manutenção da API

O diretório `hosting` contém o código e a configuração necessários para manter a
API. Apenas sua manutenção exige Node.js e autenticação na Cloudflare:

```powershell
cd hosting
npm ci
npm run check
npm run deploy
```

A chave de produção é o secret `TEAM_TOKEN` do Worker. Mudanças no banco existente
exigem migrações; `database/schema.sql` define a estrutura inicial.

## Testes

`python -m unittest discover -s tests -v` executa os testes locais isolados.
Os testes HTTP de `tests/test_api.py` são opcionais. Para executá-los no emulador:

```powershell
cd hosting
npm ci
Copy-Item .dev.vars.example .dev.vars
npx wrangler d1 execute cp2-alvaro-ers --local --file ../database/schema.sql
npm run dev -- --local --port 8789
```

Em outro terminal, na raiz, definir `PB14_TEST_URL=http://127.0.0.1:8789` e
`PB14_TEST_TOKEN` com a chave de teste de `.dev.vars`; executar o unittest.
Esses testes criam registros sintéticos e devem usar o emulador.
