# Fábrica de vídeos curtos: YouTube Shorts + Instagram Reels

Gera vídeos verticais (9:16, 1080×1920) automaticamente a partir de um **tema**,
usando o [MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo).
Para cada tema ele cria o roteiro com IA, a narração em português, busca imagens
de banco gratuitas, coloca legendas e música de fundo e entrega o `.mp4` pronto
para postar no **YouTube Shorts** e no **Instagram Reels** (o mesmo arquivo serve
para os dois).

## O que você precisa

| Item | Custo | Onde conseguir |
| --- | --- | --- |
| [Docker Desktop](https://www.docker.com/products/docker-desktop/) | grátis | instale no seu PC (Windows, Mac ou Linux) |
| Chave do **Pixabay** (imagens/vídeos de banco) | grátis | https://pixabay.com/api/docs/ (o Pexels suspendeu chaves novas) |
| Chave de um **LLM** (escreve o roteiro) | grátis ou centavos | recomendado: [Groq](https://console.groq.com/keys) (grátis, sem cartão). Outros: [DeepSeek](https://platform.deepseek.com/api_keys), [Gemini](https://aistudio.google.com/app/apikey), [OpenAI](https://platform.openai.com/api-keys) |
| Narração | grátis | Edge TTS, já vem incluso, sem chave |

## Passo a passo

### 1. Baixe este repositório e entre na pasta

```bash
git clone https://github.com/moraisisaacsimoldes-source/isaac.git
cd isaac
```

### 2. Crie o `config.toml` com suas chaves

Baixe o arquivo de exemplo oficial:

```bash
curl -o config.toml https://raw.githubusercontent.com/harry0703/MoneyPrinterTurbo/main/config.example.toml
```

Abra `config.toml` num editor de texto e preencha:

```toml
pixabay_api_keys = ["SUA_CHAVE_PIXABAY"]

# Escolha UM provedor de LLM e preencha a chave dele. Exemplos:
llm_provider = "groq"
groq_api_key = "SUA_CHAVE_GROQ"

# ou
# llm_provider = "deepseek"
# deepseek_api_key = "SUA_CHAVE_DEEPSEEK"
```

> ⚠️ O `config.toml` tem suas chaves secretas. Ele já está no `.gitignore`;
> **nunca** suba esse arquivo para o GitHub.

### 3. Ligue o MoneyPrinterTurbo

```bash
docker compose up -d
```

- Interface web: http://127.0.0.1:8501 (bom para testar e ajustar visualmente)
- API: http://127.0.0.1:8080/docs

### 4. Gere os vídeos em lote

Edite `temas.txt` (um tema por linha) e rode:

```bash
python3 gerar_videos.py
```

Os vídeos aparecem na pasta `saida/`. Cada um leva de 1 a 5 minutos.

Opções úteis:

```bash
python3 gerar_videos.py --voz pt-BR-AntonioNeural-Male      # voz masculina
python3 gerar_videos.py --paragrafos 2                       # vídeo mais longo (~60s)
python3 gerar_videos.py outros_temas.txt --saida semana2     # outra lista/pasta
```

Vozes grátis em português: `pt-BR-FranciscaNeural-Female` (padrão),
`pt-BR-AntonioNeural-Male`, `pt-BR-ThalitaMultilingualNeural-Female`.

### 5. Poste

- **YouTube Shorts**: no app do YouTube, toque em **+ → Short → Enviar** (ou pelo
  YouTube Studio no computador; vídeos verticais com menos de 3 min viram Short).
- **Instagram Reels**: **+ → Reel**, escolha o vídeo. Dá para marcar "Recomendar
  no Facebook" para alcance extra.
- Para **agendar** os dois de uma vez: [Meta Business Suite](https://business.facebook.com/)
  (Instagram) e o agendamento do YouTube Studio, ambos grátis.

O MoneyPrinterTurbo também consegue publicar direto no YouTube, Instagram e
TikTok (configuração na interface web), mas recomendo revisar cada vídeo antes.

## Dicas para crescer (e não ser penalizado)

- **Escolha um nicho** e mantenha: curiosidades, finanças, história, saúde,
  motivação... O algoritmo precisa entender para quem mostrar seus vídeos.
- **Gancho nos 2 primeiros segundos.** Temas em forma de pergunta ou número
  ("3 erros que…", "Por que…?") funcionam melhor.
- **Revise o roteiro.** O YouTube e o Instagram reduzem o alcance e a
  monetização de conteúdo repetitivo ou "produzido em massa" sem valor
  agregado. Use a interface web para editar o roteiro antes de gerar quando
  quiser mais qualidade.
- **Constância > volume**: 1 a 2 vídeos por dia, todo dia, rende mais que 30 de
  uma vez.
- **Título e legenda**: escreva um título curto + 3 a 5 hashtags do nicho
  (ex.: `#curiosidades #shorts #reels`).
- **Direitos autorais**: as imagens do Pexels e a música inclusa são livres
  para uso; evite trocar a música por faixas comerciais.

## Problemas comuns

| Mensagem | Solução |
| --- | --- |
| `Não consegui falar com a API` | rode `docker compose up -d` e espere ~30s |
| falhou na etapa `script` | chave do LLM errada ou sem crédito em `config.toml` |
| falhou na etapa `material`/`video` | chave do Pixabay faltando ou tema muito específico (tente outro) |
| Gemini: "Failed to create project" | crie um projeto em https://console.cloud.google.com/projectcreate e escolha-o ao criar a chave, ou use o Groq |
| mudou o `config.toml` e nada mudou | `docker compose restart` |
