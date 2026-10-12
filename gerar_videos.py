#!/usr/bin/env python3
"""Gera vídeos verticais (9:16) em lote para YouTube Shorts e Instagram Reels.

Lê os temas de temas.txt, pede cada vídeo à API do MoneyPrinterTurbo,
espera ficar pronto e salva o .mp4 em saida/.

Uso:
    python3 gerar_videos.py                 # usa temas.txt
    python3 gerar_videos.py meus_temas.txt
    python3 gerar_videos.py --voz pt-BR-AntonioNeural-Male

Não precisa instalar nada além do Python 3.
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

API_URL = os.environ.get("MPT_API_URL", "http://127.0.0.1:8080").rstrip("/")
# Só é necessário se você preencher api_key na seção [app] do config.toml.
API_KEY = os.environ.get("MPT_API_KEY", "")

STATE_FAILED = -1
STATE_COMPLETE = 1


def request(method, path, body=None):
    headers = {"Content-Type": "application/json"}
    if API_KEY:
        headers["x-api-key"] = API_KEY
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(API_URL + path, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read())


def download(url, destino):
    if url.startswith("/"):
        url = API_URL + url
    headers = {"x-api-key": API_KEY} if API_KEY else {}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=300) as resp, open(destino, "wb") as f:
        while chunk := resp.read(1 << 20):
            f.write(chunk)


def nome_arquivo(tema):
    nome = re.sub(r"[^\w\s-]", "", tema).strip().lower()
    return re.sub(r"[\s-]+", "-", nome)[:60] or "video"


def parametros(tema, args):
    return {
        "video_subject": tema,
        "video_language": "pt-BR",
        "video_aspect": "9:16",  # vertical: Shorts e Reels
        "video_source": "pexels",
        "video_concat_mode": "random",
        "video_clip_duration": 3,  # cortes rápidos prendem mais a atenção
        "video_count": 1,
        "paragraph_number": args.paragrafos,
        "voice_name": args.voz,
        "voice_rate": 1.1,
        "bgm_type": "random",
        "bgm_volume": 0.2,
        "subtitle_enabled": True,
        "subtitle_position": "two_thirds_bottom",
        "font_name": "BeVietnamPro-Bold.ttf",  # suporta acentos (ç, ã, é...)
        "font_size": 70,
        "text_fore_color": "#FFFFFF",
        "stroke_color": "#000000",
        "stroke_width": 2.5,
    }


def gerar(tema, args):
    print(f"\n▶ {tema}")
    resp = request("POST", "/api/v1/videos", parametros(tema, args))
    task_id = resp["data"]["task_id"]
    print(f"  tarefa {task_id} criada")

    inicio = time.time()
    while True:
        time.sleep(10)
        task = request("GET", f"/api/v1/tasks/{task_id}")["data"]
        state = task.get("state")
        print(f"  progresso: {task.get('progress', 0)}%", end="\r", flush=True)
        if state == STATE_COMPLETE:
            break
        if state == STATE_FAILED:
            etapa = task.get("failed_stage") or "?"
            raise RuntimeError(f"falhou na etapa '{etapa}': {task.get('error')}")
        if time.time() - inicio > args.timeout:
            raise RuntimeError(f"demorou mais de {args.timeout}s")

    os.makedirs(args.saida, exist_ok=True)
    arquivos = []
    for i, url in enumerate(task.get("videos") or [], start=1):
        sufixo = f"-{i}" if i > 1 else ""
        destino = os.path.join(args.saida, f"{nome_arquivo(tema)}{sufixo}.mp4")
        download(url, destino)
        arquivos.append(destino)
    print(f"  ✔ pronto: {', '.join(arquivos)}        ")
    return arquivos


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("temas", nargs="?", default="temas.txt", help="arquivo com um tema por linha")
    p.add_argument("--voz", default="pt-BR-FranciscaNeural-Female",
                   help="voz do Edge TTS (grátis). Ex.: pt-BR-AntonioNeural-Male, pt-BR-ThalitaMultilingualNeural-Female")
    p.add_argument("--paragrafos", type=int, default=1, help="tamanho do roteiro (1 = ~30-45s, ideal para Shorts/Reels)")
    p.add_argument("--saida", default="saida", help="pasta onde salvar os vídeos")
    p.add_argument("--timeout", type=int, default=1200, help="tempo máximo por vídeo, em segundos")
    args = p.parse_args()

    with open(args.temas, encoding="utf-8") as f:
        temas = [l.strip() for l in f if l.strip() and not l.lstrip().startswith("#")]
    if not temas:
        sys.exit(f"Nenhum tema encontrado em {args.temas}")

    try:
        request("GET", "/api/v1/musics")
    except (urllib.error.URLError, OSError) as e:
        sys.exit(f"Não consegui falar com a API em {API_URL} ({e}).\n"
                 "Ela está rodando? Veja o passo 3 do README.")

    falhas = []
    for tema in temas:
        try:
            gerar(tema, args)
        except Exception as e:  # um tema com erro não interrompe os outros
            print(f"\n  ✘ erro: {e}")
            falhas.append(tema)

    print(f"\nConcluído: {len(temas) - len(falhas)}/{len(temas)} vídeos em '{args.saida}/'.")
    if falhas:
        print("Falharam:\n  - " + "\n  - ".join(falhas))
        sys.exit(1)


if __name__ == "__main__":
    main()
