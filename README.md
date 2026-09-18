# Checkpoint 2 - Energias Renováveis e Sustentáveis (ERS)

**Integrantes:** 
* Josué Franco Braga - RM 569174
* Andrei Henrique Santos - RM 569440
* Heitor Maxímus Mucha - RM 571407
* Enrico Marinho de Aquino - RM 569338
* Gabriel Cavaloti RM - 571643


<br>
**Disciplina:** Enterprise Resilience and Security  

## Descrição do Projeto
Este repositório contém a entrega do Checkpoint 2 (CP2).

Trello: https://trello.com/b/zAVDuqLe/fiap-cp-alvaro

## PB14 — Banco de dados e persistência

A equipe usa **um único banco online**, hospedado no Cloudflare D1, com tabelas
de usuários, imóveis e consumos. O Python (3.10+) acessa esse banco por uma API HTTPS.
Não é necessário instalar pacotes Python, Node.js ou Wrangler para usar a conexão.

Cada integrante recebe a chave de acesso do mantenedor por um canal privado e executa:

```powershell
python configurar_conexao.py
python persistencia.py
```

O primeiro comando solicita a chave com entrada oculta e salva a configuração
local em `.pb14.local.json`, ignorado pelo Git. O segundo verifica a conexão online.
O endereço da API está em `database/servidor.json`. **Não publique a chave no GitHub.**

As três tasks, os contratos e as instruções de integração estão em
[docs/PB14-integracao.md](docs/PB14-integracao.md).

## PB03/PB04 — Cadastro e manutenção de imóveis

O módulo `imoveis.py` implementa cadastro, listagem, edição e exclusão com
confirmação, usando o banco da PB14. A entrada é o ID da conta autenticada por PB02:

```python
from imoveis import executar_menu_imoveis

# Após o login validar as credenciais:
executar_menu_imoveis(usuario_autenticado['id'], banco)
```

Para experimentar o menu com dados fictícios descartáveis, sem depender do login:

```powershell
python imoveis.py --demo
```

As seis tasks e o contrato com o responsável por PB01/PB02 estão em
[docs/PB03-PB04-imoveis.md](docs/PB03-PB04-imoveis.md).

O `main.py` original foi preservado. A ligação do menu principal/login ao módulo
de imóveis ainda depende da integração das histórias de usuários da equipe.
