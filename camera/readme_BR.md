# 📸 Câmera Mágica (projetoDeCamera)

🌐 **Idiomas / Languages:** [Português 🇧🇷](./README.md) | [English 🇺🇸](./README.en.md)

Uma câmera interativa feita em **Python**, controlada **só com as mãos e o rosto**. Você pinta no ar com o dedo, troca de cor mostrando dedos, tira foto fechando o punho, abre o menu segurando o dedo em cima de um botão e ainda pode jogar estourando bolhas. Tudo em tempo real pela webcam, usando **OpenCV** e **MediaPipe**.

---

## 📑 Índice

- [Funcionalidades](#-funcionalidades)
- [Requisitos](#-requisitos)
- [Instalação](#-instalação)
- [Como usar](#-como-usar)
- [Gestos](#-gestos)
- [Interface da tela](#-interface-da-tela)
- [Menu](#-menu)
- [Atalhos do teclado](#-atalhos-do-teclado)
- [Jogo de bolhas](#-jogo-de-bolhas)
- [Arquivos gerados](#-arquivos-gerados)
- [Configurações no código](#-configurações-no-código)
- [Solução de problemas](#-solução-de-problemas)

---

## ✨ Funcionalidades

- 🎨 **Pintura no ar** com o dedo indicador, com 4 tipos de pincel, 5 tamanhos e simetria (caleidoscópio).
- 🌈 **Troca de cor com a outra mão**, mostrando um dedo (inclui cor arco-íris animada).
- 📏 **Tamanho do pincel e borracha por gestos**.
- 📷 **Foto com o punho**, com timer opcional de 3 ou 5 segundos.
- 🎥 **Gravação de vídeo** em MP4.
- 🖼️ **Fundos, filtros e luz extra** (inclui fundo desfocado e "só você").
- 🧑 **Malha do rosto e esqueleto das mãos** em 3 estilos (malha, neon, pontos).
- 😮 **Efeito da boca:** abrir a boca solta confete.
- 😉 **Piscadinha** para desfazer e refazer (opcional).
- 🫧 **Jogo de bolhas** de 30 segundos, com combo e recorde salvo.
- 🖐️ **Menu controlado por gestos**: nada de mouse.

---

## 🧰 Requisitos

- **Python 3.9 a 3.12** (recomendado, por compatibilidade com o MediaPipe).
- **Webcam** funcionando.
- Bibliotecas:
  - `opencv-python`
  - `numpy`
  - `mediapipe==0.10.14` (versões muito novas podem não funcionar com este código)
- Boa iluminação e as mãos visíveis para a câmera ajudam bastante.
- Os **sons** funcionam **somente no Windows** (usam o `winsound`). Em outros sistemas o programa funciona normalmente, só sem som.

---

## 📥 Instalação

1. **Baixe o projeto** (clone o repositório ou baixe o arquivo `projetoDeCamera.py`).

   ```bash
   git clone https://github.com/ArthurRabeloNS/Interativo.git
   ```

   O projeto está dentro da pasta `camera`:

   ```bash
   cd Interativo/camera
   ```

2. **(Opcional) Crie um ambiente virtual:**

   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux / macOS
   source venv/bin/activate
   ```

3. **Instale as dependências:**

   ```bash
   python -m pip install opencv-python numpy mediapipe==0.10.14
   ```

4. **Execute:**

   ```bash
   python projetoDeCamera.py
   ```

Uma janela chamada **"Camera"** vai abrir com a imagem da câmera. Para sair, aperte **Q** ou **Esc** (ou feche a janela).

---

## ▶️ Como usar

1. Abra o programa e fique de frente para a câmera, com as duas mãos visíveis.
2. Faça o **V de paz** com a mão do pincel para ligar a pintura e depois levante **só o indicador** para desenhar.
3. Com a outra mão, mostre **um dedo** para escolher a cor.
4. Para mexer nas configurações, **segure o indicador por 2 segundos** em cima do botão **MENU** (canto superior direito) ou aperte **M**.
5. Para ver o guia rápido dentro do programa, aperte **H**.

> 💡 **Mão do pincel:** por padrão, é a **mão direita** (modo destro). Se você é canhoto, troque no menu (**Voce e**) ou aperte **T**. A outra mão passa a ser a **mão da cor**.

---

## 🖐️ Gestos

### Mão do pincel (a dominante)

| Gesto | O que faz |
|---|---|
| ✌️ **V de paz** | Liga a pintura ("arma" o pincel). |
| ☝️ **Só o indicador levantado** | Pinta enquanto você mexe o dedo. |
| 🖐️ **Tirar o dedo** (abrir a mão ou baixar o dedo) | Para o traço atual. Há uma tolerância de 0,3 s para não cortar o traço sem querer. |
| ✊ **Punho** (vindo da mão aberta) | Tira uma **foto**. |

Se você ligar a pintura e não desenhar por **8 segundos**, ela desliga sozinha (basta fazer o V de novo).

### Mão da cor (a outra)

| Gesto | O que faz |
|---|---|
| ☝️ **1 dedo levantado** | Escolhe a cor: **polegar** = amarelo, **indicador** = vermelho, **médio** = verde, **anelar** = azul, **mindinho** = arco-íris. |
| 🤏 **"L"** (polegar + indicador) | Ajusta o **tamanho** do pincel. Quanto mais aberto o L, maior o pincel. |
| ✊ **Punho** (nenhum dedo levantado) | Vira **borracha**. Ela apaga com um círculo maior que o pincel. |

### Rosto

| Gesto | O que faz |
|---|---|
| 😮 **Abrir a boca** | Solta confete e mostra o medidor de boca (e a palavra "AAAAAH!"). |
| 😉 **Piscar o olho esquerdo** | Desfaz o último traço. |
| 😉 **Piscar o olho direito** | Refaz o traço desfeito. |

> A piscadinha precisa ser mantida por cerca de meio segundo e vem **desligada** por padrão (ative em **EXTRAS > Piscadinha**).

---

## 🖥️ Interface da tela

| Elemento | Onde fica | Para que serve |
|---|---|---|
| **Botão MENU** | Canto superior direito | Segure o indicador por 2 s para abrir. Quando o menu está aberto, vira **FECHAR**. A barra enche mostrando o progresso. |
| **Paleta de cores** | Embaixo, à esquerda | 5 bolinhas (`pol`, `ind`, `med`, `ane`, `min`) mostrando as cores. A cor ativa tem um anel branco. |
| **Cursor azul-ciano** | Ponta do indicador | Aparece quando você aponta com o indicador (para mexer no menu). |
| **Círculo branco** | Ponta do indicador | Mostra o tamanho do pincel quando a pintura está ligada. Fica **vermelho** quando é a borracha. |
| **Bolinhas coloridas nos dedos** | Mão da cor | Mostram qual dedo é qual cor. O dedo escolhido tem um anel branco. |
| **Medidor de boca** | Lado direito | Barra que sobe conforme você abre a boca. |
| **REC 00:00** | Topo, no centro | Aparece enquanto o vídeo está sendo gravado. |
| **Contagem regressiva** | Centro da tela | Número grande do timer antes da foto. |
| **Avisos** | Parte de baixo | Mensagens rápidas ("Foto salva", "DESFEITO" etc.). |
| **Textos e FPS** | Topo, à esquerda | Estilo, pincel e tamanho (e a simetria, se estiver ligada), o gesto detectado na mão do pincel, o **FPS** e o nome da cor atual. Podem ser escondidos em **Textos na tela**. |
| **Etiquetas PINCEL / COR** | Perto do pulso de cada mão | Mostram qual mão é a do pincel e qual é a da cor. |
| **Status da pintura** | Topo, à esquerda (verde) | `PINTURA LIGADA: levante so o indicador`, `PINTANDO...` ou `BORRACHA...`. |
| **Dica do item** | Dentro do menu | Explicação curta do botão em que você está. |
| **Botão X** | Canto do painel do menu | Fecha o menu (segure 0,8 s). |
| **Flash branco** | Tela toda | Efeito rápido ao tirar uma foto. |

---

## 📋 Menu

**Como abrir:** segure o indicador no botão **MENU** por **2 s** (ou aperte **M**).

**Como usar:**
- Aponte com **um dedo só** da mão do pincel e **segure em cima do botão desejado**. Uma barra enche e, quando completa, a ação acontece.
- **Abas** e **FECHAR** levam cerca de **0,8 s**. Os **itens** levam cerca de **1,1 s**.
- Nos itens que **alternam opções** (marcados com 🔁 abaixo), se você continuar segurando, ele passa para a próxima opção repetidamente.

O menu tem 3 abas:

### 🎨 Aba DESENHO

| Item na tela | O que faz |
|---|---|
| **Voce e** | Alterna entre `DESTRO` (pincel na mão direita) e `CANHOTO` (pincel na mão esquerda). |
| **Pincel** 🔁 | Muda o tipo: `LISO`, `NEON` (brilha), `SPRAY` (aerógrafo) ou `FAISCAS` (solta faíscas ao desenhar). |
| **Tamanho** 🔁 | Passa pelos tamanhos `4`, `8`, `14`, `24` e `36 px`. Também dá para ajustar com o gesto do "L". |
| **Simetria** 🔁 | `OFF`, `ESPELHO`, `4x`, `6x`, `8x` e `8x ESPELHO`. Repete o traço em volta do centro, como um caleidoscópio. |
| **Desfazer** | Desfaz o último traço (tecla **Z**). |
| **Refazer** | Refaz o traço desfeito (tecla **Y**). |
| **Limpar tudo** | Apaga o desenho inteiro (dá para desfazer com **Z**). |
| **Salvar desenho** | Salva só o desenho em **PNG transparente** (tecla **S**). |

### 🖼️ Aba VISUAL

| Item na tela | O que faz |
|---|---|
| **Estilo** 🔁 | Como rosto e mãos aparecem: `MALHA`, `NEON` ou `PONTOS` (teclas **1**, **2**, **3**). |
| **Fundo** 🔁 | `AUTO`, `CAMERA`, `ESCURO`, `PRETO`, `BRANCO`, `DESFOCADO` ou `SO VOCE`. |
| **Filtro** 🔁 | `NORMAL`, `P&B`, `SEPIA`, `NEGATIVO`, `TERMICO`, `PIXEL`, `ESBOCO` ou `CARTUM`. |
| **Luz extra** 🔁 | `OFF`, `AUTO` ou `FORTE`. Clareia o vídeo em ambientes escuros e ajuda a câmera a achar suas mãos. |
| **Mostrar rosto** | Liga ou desliga a malha do rosto. |
| **Mostrar maos** | Liga ou desliga o esqueleto das mãos. |
| **Textos na tela** | Liga ou desliga os textos e o FPS. |
| **Efeito da boca** | Liga ou desliga o confete e o medidor da boca. |

**Sobre os fundos:**

| Opção | Resultado |
|---|---|
| `AUTO` | Usa fundo **preto** no estilo NEON e a **câmera** nos outros estilos. |
| `CAMERA` | Mostra a imagem normal da câmera. |
| `ESCURO` | Escurece a imagem da câmera. |
| `PRETO` / `BRANCO` | Fundo de cor lisa. |
| `DESFOCADO` | Mantém você nítido e borra o resto do cenário. |
| `SO VOCE` | Mantém só você e deixa o resto preto. |

### ⭐ Aba EXTRAS

| Item na tela | O que faz |
|---|---|
| **Jogo de bolhas** | Começa (`JOGAR`) ou para (`PARAR`) o jogo de bolhas. O menu fecha ao iniciar. |
| **Gravar video** | Começa ou para a gravação em MP4 (tecla **R**). |
| **Timer da foto** 🔁 | `OFF`, `3 s` ou `5 s` de contagem antes da foto do punho. |
| **Foto (punho)** | Liga ou desliga a foto ao fechar o punho. |
| **Pintura (V)** | Liga ou desliga a pintura com o gesto de V. |
| **Piscadinha** | Liga ou desliga desfazer/refazer piscando (vem desligado). |
| **Sons** | Liga ou desliga os efeitos sonoros (somente Windows). |
| **Ajuda** | Abre o guia rápido de gestos e teclas (tecla **H**). |

> Os itens **Foto (punho)**, **Pintura (V)**, **Piscadinha**, **Sons**, **Mostrar rosto**, **Mostrar maos**, **Textos na tela** e **Efeito da boca** mostram `LIGADO` (verde) ou `DESLIGADO` (vermelho).

---

## ⌨️ Atalhos do teclado

| Tecla | Ação |
|---|---|
| **1 / 2 / 3** | Estilo: malha, neon, pontos |
| **P** | Liga a pintura (sem precisar fazer o V) |
| **Z** | Desfazer |
| **Y** | Refazer |
| **C** | Limpar o desenho |
| **S** | Salvar o desenho em PNG transparente |
| **R** | Começar/parar a gravação de vídeo |
| **Espaço** | Tirar foto na hora |
| **T** | Trocar a mão do pincel (destro/canhoto) |
| **M** | Abrir/fechar o menu |
| **H** | Mostrar/esconder a ajuda |
| **F** | Tela cheia |
| **Q** ou **Esc** | Sair |

---

## 🫧 Jogo de bolhas

Abra pelo menu em **EXTRAS > Jogo de bolhas**.

- ⏱️ Duração: **30 segundos**.
- 👆 Estoure as bolhas encostando as **pontas dos dedos** (de qualquer mão) nelas. Também dá para estourar com a **boca aberta**.
- 🫧 **Bolhas normais:** +1 ponto.
- 🟡 **Bolhas douradas:** +5 pontos.
- 🔴 **Bolhas vermelhas (bombas):** −3 pontos e zeram o combo. **Fuja delas!**
- 🔥 **Combo:** estourar várias em sequência (menos de 1,2 s entre elas) dá pontos extras. A partir do combo 3 o jogo mostra `COMBO xN`.
- 🚀 As bolhas vão ficando **mais rápidas e mais frequentes** com o tempo.
- 🏆 O **recorde** é salvo no arquivo `recorde.txt`, na pasta do programa.

Enquanto o jogo está ativo, a pintura e a foto por punho ficam desativadas.

---

## 📂 Arquivos gerados

Tudo é salvo automaticamente na pasta **`fotos/`**, criada ao lado do programa:

| Arquivo | Origem |
|---|---|
| `foto_AAAAMMDD_HHMMSS.png` | Foto (punho ou tecla **Espaço**), com desenho e efeitos, sem os botões do menu. |
| `desenho_AAAAMMDD_HHMMSS.png` | Só o desenho, com fundo transparente. |
| `video_AAAAMMDD_HHMMSS.mp4` | Gravação de vídeo. |

Além disso, o arquivo **`recorde.txt`** (na pasta do programa) guarda a maior pontuação do jogo de bolhas.

---

## ⚙️ Configurações no código

No topo do arquivo `projetoDeCamera.py` você pode ajustar:

| Variável | O que faz |
|---|---|
| `CAMERA_INDEX` | Número da câmera a usar (`0` é a padrão). Mude se tiver mais de uma. |
| `RESOLUCAO` | Resolução da câmera, por exemplo `(1280, 720)`. `None` usa a padrão. |
| `DWELL_MENU` | Tempo para abrir o menu (padrão `2.0` s). |
| `DWELL_ITEM` | Tempo para ativar um item do menu (padrão `1.1` s). |
| `DWELL_ABA` | Tempo para trocar de aba ou fechar (padrão `0.8` s). |
| `GRACA_TRACO` | Tolerância antes de cortar o traço (padrão `0.30` s). |
| `TEMPO_ARMADA` | Tempo até a pintura desligar sozinha (padrão `8.0` s). |
| `DURACAO_JOGO` | Duração do jogo de bolhas (padrão `30` s). |

---

## 🛠️ Solução de problemas

| Problema | O que fazer |
|---|---|
| **"Nao consegui abrir a camera"** | Feche outros programas que usam a câmera (Zoom, Teams, navegador...) ou mude o `CAMERA_INDEX`. |
| **"Seu mediapipe e novo demais"** | Rode `python -m pip install mediapipe==0.10.14`. |
| **Os gestos não são reconhecidos** | Melhore a iluminação, deixe a mão inteira visível e ative **Luz extra** no menu. |
| **A pintura não liga** | Confira se **Pintura (V)** está `LIGADO`, se o menu está fechado e se o jogo não está rodando. |
| **Pinto com a mão errada** | Troque em **Voce e** ou aperte **T**. |
| **Aviso "Fundo indisponivel neste mediapipe"** | `DESFOCADO` e `SO VOCE` dependem da segmentação do MediaPipe. O programa volta para o fundo `AUTO`. |
| **Sem som** | Os sons só funcionam no Windows e precisam estar `LIGADO` em **Sons**. |
| **Está lento** | Feche outros programas, use uma `RESOLUCAO` menor e deixe o **Filtro** em `NORMAL`. |

---

## 🧱 Tecnologias

- [Python](https://www.python.org/)
- [OpenCV](https://opencv.org/)
- [MediaPipe](https://developers.google.com/mediapipe) (rosto, mãos e segmentação)
- [NumPy](https://numpy.org/)

---

Feito por **Arthur Rabelo** 💻 · [GitHub](https://github.com/ArthurRabeloNS)
