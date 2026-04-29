import argparse
import os
import sys
from pathlib import Path

# Ponto de entrada do Playwright sincronizado.
from playwright.sync_api import sync_playwright

# Modulos internos separados por responsabilidade.
from auth import do_login
from download import process_tracks
from history import load_history, missing_tracks, save_history
from report import write_results
from utils import ensure_dir, load_tracklist

# Tela base usada para login e inicio de processamento.
DEFAULT_URL = "https://srv.muzpa.com/#/media/releases"


def main() -> None:
    """
    Orquestrador principal:
    - le argumentos
    - prepara pastas e tracklist
    - abre navegador
    - executa login (manual ou automatico)
    - processa downloads
    - atualiza historico de baixadas/nao encontradas
    - grava log final
    """
    # Garante saida UTF-8 no terminal (acentos e caracteres especiais).
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Robo de busca e download no Muzpa")
    # Arquivo com lista de musicas.
    parser.add_argument("--tracklist", default="automation/tracklist.txt", help="Caminho para tracklist txt")
    # Pasta onde os arquivos baixados serao salvos.
    parser.add_argument("--downloads", default="downloads", help="Pasta para salvar os arquivos baixados")
    # Pasta de logs textuais.
    parser.add_argument("--logs", default="logs", help="Pasta para salvar log de execucao")
    # Compatibilidade com versoes antigas (equivale a downloads).
    parser.add_argument("--output", default=None, help="(Legado) Pasta de downloads")
    # Modo sem interface grafica.
    parser.add_argument("--headless", action="store_true", help="Executa sem interface grafica")
    # Tempo maximo para aguardar login.
    parser.add_argument("--wait-login", type=int, default=90000, help="Timeout de login em ms")
    # Se ativo, usuario faz login manual na janela.
    parser.add_argument("--manual-login", action="store_true", help="Nao preenche login automaticamente")
    # Arquivo JSON usado para evitar downloads duplicados e guardar nao encontradas.
    parser.add_argument("--history", default="state/track_history.json", help="Arquivo JSON de historico")
    # Ignora o historico de baixadas e permite baixar novamente.
    parser.add_argument("--force-download", action="store_true", help="Ignora historico e baixa novamente")
    # Processa somente faixas que ficaram como nao encontradas em execucoes anteriores.
    parser.add_argument("--retry-missing-only", action="store_true", help="Busca somente faixas nao encontradas no historico")
    args = parser.parse_args()

    tracklist_path = Path(args.tracklist).resolve()
    # --output sobrescreve --downloads quando fornecido.
    downloads_dir = Path(args.output if args.output else args.downloads).resolve()
    logs_dir = Path(args.logs).resolve()
    history_path = Path(args.history).resolve()
    ensure_dir(downloads_dir)
    ensure_dir(logs_dir)

    # Historico persistente: baixadas sao puladas; nao encontradas podem ser tentadas de novo.
    history = load_history(history_path)

    if args.retry_missing_only:
        # Neste modo, a fonte de faixas e o historico, nao a tracklist.
        tracks = missing_tracks(history)
        if not tracks:
            print("Nenhuma faixa nao encontrada no historico para tentar novamente.")
            write_results(logs_dir, [])
            return
    else:
        # Carrega tracks do txt.
        tracks = load_tracklist(tracklist_path)

    # Credenciais para login automatico.
    email = os.getenv("MUZPA_EMAIL", "")
    password = os.getenv("MUZPA_PASSWORD", "")

    # Ciclo de vida Playwright: browser -> context -> page.
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=args.headless)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        if args.manual_login:
            # Fluxo manual: usuario autentica na janela.
            page.goto(DEFAULT_URL, wait_until="domcontentloaded")
            print("Login manual habilitado. Faca o login na janela e aguarde...")
            try:
                page.wait_for_url("**/media/releases**", timeout=args.wait_login)
            except Exception:
                print("Nao confirmou URL de releases no login manual; seguindo com tentativa de processamento.")
        else:
            # Fluxo automatico: valida variaveis e chama modulo de autenticacao.
            if not email or not password:
                raise ValueError("Defina MUZPA_EMAIL e MUZPA_PASSWORD no ambiente, ou use --manual-login")
            do_login(page, email, password, args.wait_login, DEFAULT_URL)

        # Garante inicio na pagina base antes da busca.
        page.goto(DEFAULT_URL, wait_until="domcontentloaded")
        page.wait_for_timeout(2000)

        # Processa a lista e retorna resultados estruturados.
        results = process_tracks(page, tracks, downloads_dir, history, force_download=args.force_download)
        save_history(history_path, history)
        # Salva log final da execucao.
        write_results(logs_dir, results)

        # Encerramento explicito de recursos.
        context.close()
        browser.close()


if __name__ == "__main__":
    main()
