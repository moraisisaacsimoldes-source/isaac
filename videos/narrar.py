#!/usr/bin/env python3
"""Gera a narração no ElevenLabs e os tempos de cada frase.

Uso: python3 videos/narrar.py <pasta-do-video> <saida-audio.mp3>
Lê <pasta>/frases.json (lista de frases) e escreve <pasta>/times.js com
[início, fim] de cada cena, usando o alinhamento por caractere da API.
A chave vem do segredo de rede do ambiente (cabeçalho xi-api-key).
"""
import base64, json, sys, urllib.request

VOZ = "hpp4J3VqNfWAUOO0d1Us"  # Bella
pasta, saida = sys.argv[1], sys.argv[2]
frases = json.load(open(f"{pasta}/frases.json", encoding="utf-8"))
corpo = json.dumps({"text": "\n".join(frases), "model_id": "eleven_multilingual_v2",
                    "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}}).encode()
req = urllib.request.Request(
    f"https://api.elevenlabs.io/v1/text-to-speech/{VOZ}/with-timestamps?output_format=mp3_44100_128",
    data=corpo, headers={"Content-Type": "application/json"}, method="POST")
resp = json.loads(urllib.request.urlopen(req, timeout=180).read())
open(saida, "wb").write(base64.b64decode(resp["audio_base64"]))

al = resp["alignment"]
texto = "".join(al["characters"])
ini, fim, pos = [], [], 0
for f in frases:
    i = texto.index(f, pos)
    ini.append(al["character_start_times_seconds"][i])
    fim.append(al["character_end_times_seconds"][i + len(f) - 1])
    pos = i + len(f)
tempos = []
for k in range(len(frases)):
    a = 0 if k == 0 else max(0, ini[k] - .08)
    b = ini[k + 1] - .08 if k + 1 < len(frases) else fim[-1] + .9
    tempos.append([round(a, 3), round(b, 3)])
open(f"{pasta}/times.js", "w").write("window.TIMES=" + json.dumps(tempos) + ";\n")
for t, f in zip(tempos, frases):
    print(t, f)
