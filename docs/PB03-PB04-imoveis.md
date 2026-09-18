# PB03 e PB04 — Imóveis

## Tasks

| História | Task | Critério de conclusão |
| --- | --- | --- |
| PB03 | T01 — Implementar a entrada dos dados do imóvel | Solicitar identificação, endereço/localidade e tipo |
| PB03 | T02 — Validar os dados do cadastro | Rejeitar campos vazios e valores acima do limite informado |
| PB03 | T03 — Integrar o cadastro à persistência | Salvar o imóvel associado ao usuário e confirmar a gravação |
| PB04 | T01 — Implementar a edição dos dados do imóvel | Selecionar um imóvel da conta e persistir as alterações |
| PB04 | T02 — Implementar a exclusão com confirmação | Excluir apenas após confirmação e tratar imóveis com histórico |
| PB04 | T03 — Testar edição e exclusão | Verificar alterações, cancelamentos, confirmação e preservação do histórico |

Implementação: `imoveis.py`. Testes: `tests/test_imoveis.py`.

## Dependências e integração

PB01 persiste a conta; PB02 autentica e fornece seu ID; PB14 fornece a conexão com
o banco. Após um login válido, o menu principal chama:

```python
from imoveis import executar_menu_imoveis

executar_menu_imoveis(usuario_autenticado['id'], banco)
```

`banco` é uma instância de `persistencia.BancoDados`. Se omitido, o módulo usa a
configuração online existente. O ID deve vir da sessão autenticada. O módulo não
implementa cadastro de usuários nem login. A opção 0 retorna ao menu chamador.

A ligação com o menu principal depende da implementação de PB02.

## Regras

- Cadastro: identificação, endereço/localidade e tipo obrigatórios, até 2.000 caracteres por campo.
- Seleção: mostra somente imóveis da conta; o usuário escolhe uma posição na lista.
- Edição: Enter mantém o valor atual; `:cancelar` descarta a operação.
- Exclusão: exige digitar `EXCLUIR`; qualquer outra resposta cancela.
- Imóvel com consumo registrado não pode ser excluído, conforme a regra de integridade da PB14.
- Falhas de conexão não exibem sucesso. Antes de repetir uma gravação sem resposta, consultar os dados.

## Validação

```powershell
python -m unittest discover -s tests -v
```

Os testes verificam cadastro, validações, edição, cancelamento, exclusão confirmada,
vínculo com o usuário, preservação do histórico e falhas de conexão.
