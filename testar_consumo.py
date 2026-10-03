"""Script de teste manual pra cadastrar_consumo e consultar_historico."""
from persistencia import BancoDados
from consumo import cadastrar_consumo, consultar_historico

banco = BancoDados()

# usuário e imóvel de teste, identificáveis
usuario_id = banco.salvar_usuario("TESTE Enrico", "teste.enrico.pb0507@example.test", "hash-fake")
imovel_id = banco.salvar_imovel(usuario_id, "TESTE Imovel PB05-07", "São Paulo", "Casa")
print(f"usuario_id={usuario_id}, imovel_id={imovel_id}")

print("Válido:      ", cadastrar_consumo(usuario_id, imovel_id, 2026, 1, 150.5))
print("Negativo:    ", cadastrar_consumo(usuario_id, imovel_id, 2026, 2, -10))
print("Duplicado:   ", cadastrar_consumo(usuario_id, imovel_id, 2026, 1, 999))
print("Zero (ok):   ", cadastrar_consumo(usuario_id, imovel_id, 2026, 3, 0))
print("Histórico:   ", consultar_historico(usuario_id, imovel_id))