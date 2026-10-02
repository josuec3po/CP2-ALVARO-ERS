# Checkpoint 2 - Energias Renováveis e Sustentáveis (ERS)

**Integrantes:** 
* Josué Franco Braga - RM 569174
* Andrei Henrique Santos - RM 569440
* Heitor Maxímus Mucha - RM 571407
* Enrico Marinho de Aquino - RM 569338
* Gabriel Cavaloti RM - 571643


<br>

**Disciplina:** ERS

## Descrição do Projeto
Este repositório contém a entrega do Checkpoint 2 (CP2).

Trello: https://trello.com/b/zAVDuqLe/fiap-cp-alvaro

## PB21 - Orçamento e resumo da proposta solar

Implementação na branch `feature/pb21-orcamento-resumo`.

- `orcamento.py`: custos, validações e resumo técnico/orçamental.
- `proposta_solar.py`: execução independente pelo console.
- `main.py`: opção de gerar a proposta após o relatório de consumo positivo,
  reaproveitando o consumo mensal estimado como referência.
- `tests/test_orcamento.py`: testes de cálculo e validação.

Execute com Python 3, sem instalar dependências adicionais para a PB21:

```bash
python proposta_solar.py
python -m unittest discover -s tests -v
```

Para usar o fluxo de consumo já existente, execute `python main.py` e escolha
`s` na opção de gerar proposta. Para informar diretamente um consumo de referência
obtido do histórico, use `proposta_solar.py`.

Os resultados do dimensionamento das PB18-20 são informados pelo console ou
passados à função `gerar_proposta`. A PB21 não seleciona equipamentos nem substitui
as verificações de compatibilidade elétrica das PB19-20. O contrato e os critérios
de aceite estão em [docs/PB21.md](docs/PB21.md).
