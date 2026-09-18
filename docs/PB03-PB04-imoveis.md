# PB03 e PB04 — Módulo de imóveis

## Escopo e dependências

PB03 cadastra identificação, endereço/localidade e tipo do imóvel.
PB04 edita esses dados ou exclui o imóvel após confirmação.
O módulo usa as operações online da PB14 e recebe o usuário autenticado pela PB02.

**PB01/PB02 continuam com o responsável por usuários:** criar a conta, gerar e
verificar o hash da senha e manter a sessão. Este módulo não implementa login,
não cria contas reais e não permite escolher livremente um ID de usuário.

## As seis tasks

| História | Task | Entrega implementada |
| --- | --- | --- |
| PB03 | T01 — Implementar a entrada dos dados do imóvel | Menu e campos identificação, endereço/localidade e tipo |
| PB03 | T02 — Validar os dados do cadastro | Rejeição de campos vazios e acima de 2.000 caracteres; orientação para corrigir e possibilidade de cancelar |
| PB03 | T03 — Integrar o cadastro à persistência | Gravação na PB14 com vínculo ao usuário; sucesso somente após retorno do banco |
| PB04 | T01 — Implementar a edição dos dados do imóvel | Seleção entre os imóveis da conta, valores atuais, alteração e gravação na PB14 |
| PB04 | T02 — Implementar a exclusão com confirmação | Identificação do imóvel e confirmação digitando EXCLUIR; outras respostas cancelam; histórico bloqueia exclusão |
| PB04 | T03 — Testar os fluxos de edição e exclusão | Testes de gravação, validação, cancelamento, confirmação, seleção por conta e preservação de histórico |

As seis entregas estão implementadas em `imoveis.py` e `tests/test_imoveis.py`.
O aceite integrado do projeto depende de PB02 chamar o módulo depois de um login
válido. Não considerar PB01/PB02 entregues por causa da demonstração abaixo.

## Contrato para o responsável pelo login

A única chamada necessária é:

```python
from imoveis import executar_menu_imoveis

# Neste ponto PB02 já verificou as credenciais e tem a conta da sessão.
executar_menu_imoveis(usuario_autenticado['id'], banco)
```

- `usuario_autenticado['id']` é o ID retornado pelo banco para uma conta já persistida.
  Não deve vir de um campo livre, nome digitado ou ID fixado no código.
- `banco` é a instância de `persistencia.BancoDados` utilizada pelo aplicativo.
  Se omitido, o módulo cria o cliente online usando a configuração da PB14.
- Não é necessário fornecer e-mail ou senha ao módulo de imóveis.
- A opção **0 — Voltar** retorna à função chamadora. O menu principal da equipe
  decide se mostra outras funcionalidades ou encerra a sessão.
- Um ID nulo, textual, booleano ou não positivo gera `ValueError`: o chamador deve
  fornecer uma sessão válida antes de abrir o menu.
- Todas as operações de imóvel carregam o mesmo `usuario_id` recebido. A API
  confere o vínculo entre imóvel e conta; autenticar a sessão permanece com PB02/PB15.

## Comportamento dos fluxos

**Cadastro:** campos obrigatórios, remoção de espaços externos, validação antes de
gravar e mensagem de sucesso após confirmação do banco. `:cancelar` abandona a
operação sem gravar um cadastro incompleto.

**Listagem/seleção:** mostra somente os imóveis da conta. O usuário escolhe a posição
na lista; o módulo resolve o ID real internamente. Opções inválidas não encerram o
programa. Sem imóveis, o menu informa isso e permite voltar ao cadastro.

**Edição:** apresenta os valores atuais. Enter mantém o campo; `:cancelar` descarta
todas as alterações daquela edição. Nenhuma gravação ocorre se os valores não mudaram.

**Exclusão:** mostra qual imóvel será excluído e exige digitar `EXCLUIR`. Enter,
`sim` e qualquer outra resposta cancelam. Imóvel com registros de consumo não é
excluído: a regra da PB14 preserva o histórico e a interface explica o bloqueio.

**Falhas de conexão:** não há confirmação falsa de sucesso nem repetição automática
de gravações. Em caso de timeout, o usuário deve consultar os registros antes de
tentar novamente, pois uma resposta pode se perder depois de uma gravação efetivada.

## Experimentar antes de o login estar pronto

Na raiz do projeto:

```powershell
python imoveis.py --demo
```

Essa demonstração usa o mesmo menu com um usuário fictício e uma base SQLite
temporária, descartada ao sair. Não exige chave e não toca no banco compartilhado.
Serve para testar sua parte enquanto o colega desenvolve PB01/PB02; não substitui
a autenticação do aplicativo.

Para usar o banco online real, configurar a conexão conforme o guia da PB14 e
chamar `executar_menu_imoveis` após autenticação. Não há login alternativo de teste
nem usuário padrão criado na base da equipe.

## Verificação

```powershell
python -m unittest discover -s tests -v
```

Os 13 testes específicos de imóveis cobrem cadastro válido/inválido, persistência,
edição com Enter, edição cancelada, ausência de mudanças, exclusão cancelada e
confirmada, histórico protegido, seleção limitada à conta, menu vazio, falha de
rede, ID de sessão inválido e interrupção antes da confirmação.

Os testes automáticos usam bancos temporários. Os testes de API da PB14 continuam
opcionais e exigem o emulador conforme `PB14-integracao.md`.

Nesta entrega, o menu também foi validado contra o banco online: cadastro, edição,
consulta por outro cliente, cancelamento de exclusão e exclusão confirmada. O
usuário sintético dessa verificação foi removido ao terminar. A demonstração foi
executada em um processo de terminal separado para conferir sua entrada e saída.

O `main.py` original foi preservado. O responsável pela integração do aplicativo
deve adicionar a chamada acima ao menu pós-login; importar `imoveis` não abre menus
nem acessa o banco por conta própria.
