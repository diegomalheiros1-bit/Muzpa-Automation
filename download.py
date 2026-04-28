from typing import Iterable, List

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from models import TrackResult
from search import best_download_candidate_for_track, find_search_input
from utils import build_fallback_query, normalize_text


def click_download(page: Page, candidate):
    """
    Envolve o clique em um contexto expect_download para capturar o arquivo.
    """
    with page.expect_download(timeout=15000) as dl_info:
        candidate.click(timeout=3000, force=True)
    return dl_info.value


def process_tracks(page: Page, tracks: Iterable[str], downloads_dir) -> List[TrackResult]:
    """
    Processa a tracklist faixa a faixa.
    Fluxo por faixa:
    1) busca completa
    2) fallback "titulo + versao" (sem artista), se aplicavel
    3) tenta baixar via melhor candidato
    4) registra status final
    """
    results: List[TrackResult] = []

    for idx, track in enumerate(tracks, start=1):
        print(f"[{idx}] Buscando: {track}")
        try:
            search_input = find_search_input(page)
            if not search_input:
                results.append(TrackResult(track, "erro", "Campo de busca nao encontrado"))
                continue

            # Primeira tentativa usa texto completo da tracklist.
            attempts = [("busca_completa", track)]
            fallback_query = build_fallback_query(track)
            # Segunda tentativa remove artista quando a consulta muda de fato.
            if normalize_text(fallback_query) != normalize_text(track):
                attempts.append(("fallback_titulo_versao", fallback_query))

            downloaded = False
            last_detail = "Sem correspondencia relevante"

            for attempt_name, query in attempts:
                # Digita consulta e dispara busca.
                search_input.click()
                search_input.fill("")
                search_input.fill(query)
                search_input.press("Enter")
                page.wait_for_timeout(2500)

                row, score = best_download_candidate_for_track(page, track)
                if row is None or score < 6:
                    last_detail = f"Sem correspondencia relevante ({attempt_name})"
                    continue

                download = click_download(page, row)
                if not download:
                    last_detail = f"Correspondencia sem botao de download ({attempt_name})"
                    continue

                file_name = download.suggested_filename or ""
                # Persistencia fisica na pasta downloads.
                target = downloads_dir / file_name if file_name else downloads_dir / f"download_{idx}.bin"
                download.save_as(target)
                results.append(TrackResult(track, "baixada", f"OK ({attempt_name})", file_name=file_name))
                print(f"    Download iniciado: {file_name}")
                page.wait_for_timeout(1200)
                downloaded = True
                break

            if not downloaded:
                results.append(TrackResult(track, "nao_encontrada", last_detail))
        except PlaywrightTimeoutError:
            # Timeout Playwright (espera de elementos/download).
            results.append(TrackResult(track, "erro", "Timeout durante busca/download"))
        except Exception as exc:
            # Qualquer erro inesperado e registrado para auditoria.
            results.append(TrackResult(track, "erro", f"Falha inesperada: {exc}"))

    return results
