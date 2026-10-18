# GestureFlow 🖐️
### Controle do computador por gestos com visão computacional

O **GestureFlow** é um projeto desenvolvido em Python que permite controlar o mouse e interagir com o teclado do computador utilizando apenas uma câmera e gestos das mãos.

Utilizando visão computacional e reconhecimento de mãos, o sistema interpreta os movimentos e gestos realizados diante da câmera e os transforma em ações no computador, como mover o cursor, clicar, arrastar objetos, rolar páginas e digitar por meio de um teclado virtual.

O projeto foi desenvolvido como uma experiência prática com Python, automação de desktop e reconhecimento de gestos.

**Documentação:** [English version](README.md) | Português

---

## ✨ Funcionalidades

- 🖱️ **Controle do mouse:** mova o cursor com o dedo indicador.
- 👆 **Clique esquerdo:** aproxime o polegar do indicador para clicar.
- ✋ **Arrastar objetos:** mantenha o gesto de pinça para arrastar elementos.
- 👉 **Clique direito:** aproxime o polegar do dedo médio.
- 🤘 **Rolagem de páginas:** utilize os dedos indicador e mindinho para controlar a rolagem. (para cima e para baixo)
- ⌨️ **Teclado virtual:** abra um teclado na tela e digite usando gestos.
- 🔄 **Alternância de mão:** alterne entre a mão direita e a esquerda.
- ⏸️ **Pausar o controle:** suspenda temporariamente a movimentação.
- 📷 **Visualização da câmera:** acompanhe o reconhecimento das mãos e o estado do sistema em tempo real.

## 🛠️ Tecnologias utilizadas

- **Python** — linguagem principal do projeto.
- **OpenCV** — captura e processamento das imagens da câmera.
- **MediaPipe** — detecção e rastreamento das mãos.
- **NumPy** — suporte a operações numéricas.
- **pynput** — controle do mouse, do teclado e captura de atalhos.
- **Tkinter** — interface do teclado virtual.

## 📋 Requisitos

Antes de executar o projeto, você precisará de:

- Python instalado.
- Uma webcam funcional.
- Windows recomendado, pois o projeto contém ajustes específicos para esse sistema operacional.
- Conexão com a internet para instalar as dependências.

## 📥 Como baixar o projeto

### 1. Clone o repositório

Abra o terminal e execute:

```bash
git clone https://github.com/ArthurRabeloNS/GestureFlow.git
```

Entre na pasta do projeto:

```bash
cd GestureFlow
```

Você também pode baixar o projeto pelo botão **Code → Download ZIP** na página do repositório.

### 2. Crie um ambiente virtual (opcional, mas recomendado)

```bash
python -m venv .venv
```

No Windows, ative o ambiente virtual:

```bash
.venv\Scripts\activate
```

### 3. Instale as dependências

```bash
python -m pip install -r requirements.txt
```

```bash
python -m pip install opencv-python numpy mediapipe==0.10.14 pynput
```

A versão do MediaPipe foi fixada para manter compatibilidade com a API `solutions` utilizada pelo código.

### 4. Execute o programa

```bash
python controleDeDesktop.py
```

A câmera será aberta e o sistema começará a reconhecer a mão selecionada.

## 🖐️ Como utilizar

### Gestos principais

| Gesto | Ação |
|---|---|
| Indicador estendido | Move o cursor |
| Pinça entre polegar e indicador | Clique esquerdo ao soltar |
| Manter a pinça por aproximadamente 0,45 segundo | Arrastar objetos |
| Pinça entre polegar e dedo médio | Clique direito |
| Indicador e mínimo estendidos | Rolar a página inclinando os dedos para cima ou para baixo |
| Mão fechada por aproximadamente 1,2 segundo | Mostrar ou ocultar o teclado virtual |
| Mão aberta | Reconhecida pelo sistema, sem pausar automaticamente o programa |

### Atalhos do teclado

| Tecla | Função |
|---|---|
| `F8` | Alternar entre mão direita e esquerda |
| `F9` | Pausar ou retomar o controle |
| `F10` | Mostrar ou ocultar o teclado virtual |
| `F12` | Encerrar o programa |
| `Q` ou `ESC` | Sair pela janela da câmera |
| `M` | Alternar a mão pela janela da câmera |

**Dica:** mantenha a mão dentro da área de controle indicada na imagem da câmera e evite movimentos muito bruscos para obter um controle mais estável.

## ⚙️ Personalização

O código possui configurações que podem ser modificadas para ajustar o comportamento do sistema, como:

- Índice da câmera utilizada.
- Resolução de captura.
- Mão selecionada inicialmente.
- Área da imagem utilizada para controlar o cursor.
- Sensibilidade da pinça.
- Tempo necessário para iniciar o arraste.
- Velocidade da rolagem.

Essas opções estão definidas no início do arquivo `controleDeDesktop.py`.

## 🔒 Privacidade e segurança

O programa utiliza a câmera para reconhecer gestos e executar ações locais no computador. O código atual não implementa envio de imagens para servidores nem gravação de vídeos.

Como o sistema controla o mouse e o teclado reais, recomenda-se testar os gestos em um ambiente seguro e manter o programa pausado quando não estiver em uso.

## 🎯 Objetivo do projeto

O GestureFlow tem como objetivo explorar a interação entre pessoas e computadores por meio de visão computacional, reconhecimento de gestos e automação de desktop.

É também uma oportunidade de estudar bibliotecas Python, rastreamento de mãos e criação de interfaces alternativas de controle.
---

Desenvolvido como projeto de estudo com Python e visão computacional. 💻