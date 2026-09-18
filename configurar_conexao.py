"""Configura a conexão individual sem colocar a chave no Git."""
from getpass import getpass
import json
from persistencia import BancoDados, RAIZ


def main():
    servidor = json.loads((RAIZ / "database" / "servidor.json").read_text(encoding="utf-8"))
    url = servidor.get("url") or input("URL HTTPS fornecida pelo mantenedor: ").strip()
    token = getpass("Chave da equipe (entrada oculta): ").strip()
    BancoDados(url=url, token=token).inicializar()
    arquivo = RAIZ / ".pb14.local.json"
    arquivo.write_text(json.dumps({"url": url, "token": token}, indent=2), encoding="utf-8")
    print("Conexão validada e salva em .pb14.local.json (ignorado pelo Git).")


if __name__ == "__main__":
    main()
