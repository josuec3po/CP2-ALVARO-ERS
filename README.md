# Checkpoint 2 - Energias Renováveis e Sustentáveis (ERS)

**Disciplina:** Enterprise Resilience and Security

**Integrantes:**

- Josué Franco Braga - RM 569174
- Andrei Henrique Santos - RM 569440
- Heitor Maxímus Mucha - RM 571407
- Enrico Marinho de Aquino - RM 569338
- Gabriel Cavaloti - RM 571643

[Trello da equipe](https://trello.com/b/zAVDuqLe/fiap-cp-alvaro)

## Funcionalidades desta branch

- **PB03:** cadastro de imóveis com identificação, endereço/localidade e tipo.
- **PB04:** edição e exclusão com confirmação.
- **PB14:** persistência em banco compartilhado hospedado no Cloudflare D1.

## Configuração

Requisito: Python 3.10 ou superior. Na raiz do projeto:

```powershell
python configurar_conexao.py
python persistencia.py
```

Informar a chave de acesso fornecida pela equipe. Ela fica em `.pb14.local.json`,
ignorado pelo Git. O segundo comando verifica a conexão com o banco online.

## Integração

Após autenticar o usuário pela PB02, o menu principal chama:

```python
from imoveis import executar_menu_imoveis

executar_menu_imoveis(usuario_autenticado['id'], banco)
```

`banco` é a conexão da PB14. A integração com o menu principal depende de PB01/PB02.

## Documentação e testes

- [Tasks e regras de PB03/PB04](docs/PB03-PB04-imoveis.md)
- [Tasks, banco e interface de PB14](docs/PB14-integracao.md)

```powershell
python -m unittest discover -s tests -v
```
