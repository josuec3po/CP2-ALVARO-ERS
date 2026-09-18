# PB14 — Banco central e integração da equipe

**User Story:** Como usuário, quero que os dados permaneçam disponíveis após sair do sistema.

**Critério de aceite:** imóveis e consumos persistidos em banco de dados e associados ao usuário.

Os cinco integrantes usam **o mesmo banco online**, `cp2-alvaro-ers`, hospedado no
Cloudflare D1. A aplicação Python acessa o banco pela API HTTPS autenticada:

`https://cp2-alvaro-pb14.atzagenda.workers.dev`

A chave é necessária para todas as operações. Abrir o endereço no navegador sem
credencial não mostra os dados; isso é esperado. O programa Python continua local,
mas os registros de usuários, imóveis e consumos ficam centralizados na nuvem.

## As três tasks

| Task | Entrega verificável | Situação |
| --- | --- | --- |
| PB14-T01 — Definir o modelo compartilhado e criar o banco hospedado | Tabelas de usuários, imóveis e consumos com vínculos e restrições | Banco e estrutura criados na Cloudflare; contratos abaixo propostos para a equipe |
| PB14-T02 — Implementar a conexão e as rotinas de persistência | Cliente Python e API protegida, com gravação, leitura, edição e exclusão de imóveis | Implementados; chave fora do Git |
| PB14-T03 — Validar a persistência e orientar a integração | Gravar e consultar em processos diferentes, testar integridade e documentar uso | Testes da camada e guia disponíveis; conexão dos menus da equipe ainda pendente |

## Como cada colega conecta

1. Incorporar esta entrega à sua branch. Quem ainda não tem o projeto pode clonar:

   ```powershell
   git clone --branch feature/pb03-04-14-imoveis https://github.com/josuec3po/CP2-ALVARO-ERS.git
   cd CP2-ALVARO-ERS
   ```

   Quem já trabalha em outra branch pode integrar a branch compartilhada:

   ```powershell
   git fetch origin
   git merge origin/feature/pb03-04-14-imoveis
   ```

2. Receber a chave da equipe do mantenedor por um canal privado.
3. Com Python 3.10 ou superior, executar na raiz:

   ```powershell
   python configurar_conexao.py
   python persistencia.py
   ```

O primeiro comando solicita a chave sem exibi-la, verifica o acesso e salva
`.pb14.local.json`. Esse arquivo é ignorado pelo Git. O segundo confirma a conexão.
Não é necessário instalar pacotes Python nem ter conta Cloudflare para usar o banco.
Não envie a chave em commits, issues ou mensagens públicas.

O mantenedor encontra a configuração de acesso local em `.pb14.local.json`.
Também é possível configurar `PB14_API_URL` e `PB14_API_TOKEN` como variáveis de
ambiente. A URL pública padrão está em `database/servidor.json`.

## Como usar no código

```python
from persistencia import BancoDados

banco = BancoDados()
banco.inicializar()  # Confere a conexão, não recria nem apaga tabelas.

# usuario_id deve vir do módulo de autenticação da equipe.
imovel_id = banco.salvar_imovel(usuario_id, 'Minha casa', 'São Paulo', 'Casa')
banco.salvar_consumo(usuario_id, imovel_id, 2026, 1, 320.0)
consumos = banco.listar_consumos(usuario_id, imovel_id)
```

O cliente não usa banco local como alternativa se a conexão falhar. Uma falha de
rede gera `ErroConexao`; o chamador deve avisar o usuário. Gravações não são
repetidas automaticamente em caso de timeout, para evitar duplicações.

## Contratos para os módulos

| Método de `banco` | Retorno |
| --- | --- |
| `salvar_usuario(nome, email, senha_hash)` | ID inteiro criado; recebe hash já gerado pelo módulo de usuários |
| `buscar_usuario_por_email(email)` | Dicionário de usuário, incluindo hash, ou `None`; uso interno do login |
| `salvar_imovel(usuario_id, identificacao, localidade, tipo)` | ID inteiro criado |
| `listar_imoveis(usuario_id)` | Lista de imóveis do usuário, ordenada por ID |
| `buscar_imovel(usuario_id, imovel_id)` | Dicionário de imóvel |
| `atualizar_imovel(usuario_id, imovel_id, identificacao, localidade, tipo)` | `None` após sucesso; enviar todos os três campos |
| `excluir_imovel(usuario_id, imovel_id)` | `None` após sucesso; PB04 pede confirmação antes de chamar |
| `salvar_consumo(usuario_id, imovel_id, ano, mes, consumo_kwh)` | ID inteiro criado |
| `listar_consumos(usuario_id, imovel_id)` | Lista de consumos em ordem de ano/mês |

Listagens vazias retornam `[]`. Ausência de imóvel ou vínculo incorreto gera
`RegistroNaoEncontrado`; dados inválidos geram `ValueError`; duplicatas e conflitos
de relacionamento geram `sqlite3.IntegrityError`; falhas de conexão/autorização
geram `ErroConexao`. As interfaces devem tratar esses erros e só confirmar sucesso
após o retorno da função.

## Modelo e regras iniciais

| Tabela | Campos | Relacionamento |
| --- | --- | --- |
| `usuarios` | `id`, `nome`, `email`, `senha_hash` | E-mail único, sem diferenciar maiúsculas/minúsculas |
| `imoveis` | `id`, `usuario_id`, `identificacao`, `localidade`, `tipo` | Pertence a um usuário existente |
| `consumos` | `id`, `imovel_id`, `ano`, `mes`, `consumo_kwh` | Pertence a um imóvel; proprietário obtido pelo vínculo com o imóvel |

- Campos de texto obrigatórios não podem ser vazios; a API aceita até 2.000 caracteres por campo.
- Consumo zero é válido; números negativos, infinitos ou não numéricos são rejeitados.
- Ano: inteiro de 1 a 9999; mês: inteiro de 1 a 12. Meses futuros não são bloqueados.
- Só existe um consumo por imóvel/mês/ano. Duplicatas geram erro sem sobrescrever dados.
- Imóvel com histórico tem a exclusão bloqueada. Essa regra evita perder os consumos;
  se a equipe optar por exclusão conjunta, precisa ajustar a regra e os testes.
- `localidade` recebe o endereço/localidade de PB03. `tipo` aceita texto livre não vazio.

## Trabalho em paralelo

Usuários implementa cadastro/login e fornece `usuario_id`; imóveis implementa os
fluxos de PB03/PB04; consumo implementa entrada/consulta; cálculos e resultados
consomem a lista de dicionários abaixo. Cada módulo pode começar com dados de exemplo:

```python
consumos = [
    {'id': 1, 'imovel_id': 10, 'ano': 2026, 'mes': 1, 'consumo_kwh': 320.0},
    {'id': 2, 'imovel_id': 10, 'ano': 2026, 'mes': 2, 'consumo_kwh': 295.0},
]
```

A chave é uma credencial técnica da equipe, equivalente ao acesso de desenvolvimento
à base; não é a senha nem a sessão de um usuário final. Quem possui a chave pode
operar o banco pelos métodos da API. O módulo de login deve validar a senha e fornecer
o ID da sessão, e PB15 deve completar o controle de acesso do produto. Não embutir a
chave em frontend público. `senha_hash` deve ser produzido e verificado por PB01/PB02;
a persistência não gera hashes nem implementa login.

## Testes

Validação desta entrega: 19 testes passaram com a API no emulador. Na hospedagem
real foram verificadas gravação, edição, leitura em outro processo, exclusão de
imóvel sem histórico e rejeição de duplicatas, chave inválida e vínculo incorreto.
Os registros sintéticos dessa verificação online foram removidos; a base foi
entregue vazia, com as três tabelas prontas para os dados da equipe.

Testes do adaptador local e do cliente Python, sem acessar o banco online:

```powershell
python -m unittest discover -s tests -v
```

Os três testes reais de API ficam desabilitados sem `PB14_TEST_URL`. Para executá-los
contra o emulador local, o mantenedor usa Node.js e, na pasta `hosting`:

```powershell
npm ci
Copy-Item .dev.vars.example .dev.vars
npx wrangler d1 execute cp2-alvaro-ers --local --file ../database/schema.sql
npm run dev -- --local --port 8789
```

Em outro terminal, na raiz, configure `PB14_TEST_URL` para `http://127.0.0.1:8789`
e `PB14_TEST_TOKEN` com o valor de teste de `.dev.vars`, então execute o unittest.
Esses testes criam registros sintéticos: use o emulador, não a base compartilhada.

## Administração da hospedagem

Arquivos da API em `hosting`; estrutura SQL em `database/schema.sql`.
Somente o mantenedor precisa de Wrangler e acesso à conta Cloudflare.

```powershell
cd hosting
npm ci
npm run types
npm run check
npx wrangler deploy --dry-run
npm run deploy
```

A chave de produção é um secret `TEAM_TOKEN` do Worker. Para trocar, gere uma chave
aleatória forte e use `wrangler secret put TEAM_TOKEN`, avisando os colegas por canal
privado para atualizar a configuração. `.dev.vars` contém apenas a chave de teste
local e não é enviada como secret no deploy.

Para backup: `npx wrangler d1 export cp2-alvaro-ers --remote --output backup.sql`.
Guarde o backup fora do repositório porque ele contém os dados e hashes.
Mudanças futuras de estrutura precisam de migrações: o script inicial não altera
colunas de tabelas existentes. Não apague/recrie tabelas para atualizar a base compartilhada.

O módulo `imoveis.py` (PB03/PB04) já utiliza esta camada para cadastro, edição e
exclusão com confirmação. As seis tasks e a chamada pós-login estão em
[PB03-PB04-imoveis.md](PB03-PB04-imoveis.md).

O `main.py` original ainda não chama esses módulos. A integração do login e do
fluxo de consumo depende dos responsáveis por essas histórias. O aceite completo
do produto exige entrar na conta, cadastrar imóvel/consumo, sair e recuperar os
registros na conta correta pela interface integrada.
