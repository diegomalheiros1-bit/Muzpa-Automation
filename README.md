# TrackHunter

Automacao em Python + Playwright para buscar faixas no Muzpa e baixar arquivos MP3 automaticamente.

## Objetivo

Este projeto automatiza o fluxo de:

1. Acessar o Muzpa
2. Fazer login (automatico ou manual)
3. Buscar musicas de uma tracklist
4. Clicar no botao MP3 do melhor resultado
5. Salvar downloads na pasta `downloads`
6. Gerar log final em `logs`

## Stack

- Python 3.10+
- Playwright (Python)

## Estrutura do Projeto

```text
TrackHunter/
|- muzpa_bot.py      # orquestrador principal (CLI)
|- auth.py           # login e autenticacao
|- search.py         # busca e escolha do melhor candidato
|- download.py       # fluxo de download por faixa
|- report.py         # geracao de log txt final
|- utils.py          # utilitarios (normalizacao, tracklist, fallback)
|- models.py         # dataclasses do dominio
|- requirements.txt
|- tracklist.txt
|- downloads/        # arquivos MP3 baixados
`- logs/             # logs de execucao (.txt)
```

## Instalacao

```bash
pip install -r requirements.txt
playwright install chromium
```

## Uso rapido

```powershell
$env:MUZPA_EMAIL="seu_email"
$env:MUZPA_PASSWORD="sua_senha"
python .\muzpa_bot.py --tracklist .\tracklist.txt --downloads .\downloads --logs .\logs
```
