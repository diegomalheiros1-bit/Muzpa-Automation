from datetime import datetime
from typing import List

from models import TrackResult


def write_results(logs_dir, results: List[TrackResult]) -> None:
    """
    Gera apenas o log textual da execucao.
    Nao gera CSV/Excel.
    """
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = logs_dir / f"log_execucao_{ts}.txt"

    # Contadores de resumo.
    total = len(results)
    downloaded = sum(1 for x in results if x.status == "baixada")
    not_found = sum(1 for x in results if x.status == "nao_encontrada")
    errors = sum(1 for x in results if x.status == "erro")

    with log_file.open("w", encoding="utf-8-sig") as fh:
        # Cabecalho de resumo rapido.
        fh.write("Resumo da execucao\n")
        fh.write(f"Data/Hora: {datetime.now().isoformat()}\n")
        fh.write(f"Total: {total}\n")
        fh.write(f"Baixadas: {downloaded}\n")
        fh.write(f"Nao encontradas: {not_found}\n")
        fh.write(f"Erros: {errors}\n")
        # Lista detalhada com uma linha por faixa.
        fh.write("\nDetalhes\n")
        for row in results:
            fh.write(f"- [{row.status}] {row.track} | {row.detail} | {row.file_name}\n")

    print("\nArquivos gerados:")
    print(f"- {log_file}")
