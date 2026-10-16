import os
import time
import math
import random
import queue
import threading
import warnings
from collections import deque

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")
os.environ.setdefault("GLOG_minloglevel", "2")
warnings.filterwarnings("ignore")

import cv2
import numpy as np
import mediapipe as mp

# CONFIGURACOES
CAMERA_INDEX = 0          
RESOLUCAO = None 
JANELA = "Camera"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PASTA = os.path.join(BASE_DIR, "fotos")
ARQ_RECORDE = os.path.join(BASE_DIR, "recorde.txt")

DWELL_MENU = 2.0     
DWELL_ITEM = 1.1          
DWELL_ABA = 0.8        
GRACA_TRACO = 0.30      
TEMPO_ARMADA = 8.0        
DURACAO_JOGO = 30      

FONTE = cv2.FONT_HERSHEY_SIMPLEX
VERDE, VERMELHO, BRANCO = (0, 255, 0), (0, 0, 255), (255, 255, 255)
CIANO, AMARELO, CINZA = (255, 255, 0), (0, 255, 255), (170, 170, 170)

ESTILOS = {1: "MALHA", 2: "NEON", 3: "PONTOS"}
PINCEIS = ["LISO", "NEON", "SPRAY", "FAISCAS"]
TAMANHOS = [4, 8, 14, 24, 36]
SIMETRIAS = [("OFF", 1, False), ("ESPELHO", 1, True), ("4x", 4, False),
             ("6x", 6, False), ("8x", 8, False), ("8x ESPELHO", 8, True)]
FUNDOS = ["AUTO", "CAMERA", "ESCURO", "PRETO", "BRANCO", "DESFOCADO", "SO VOCE"]
FILTROS = ["NORMAL", "P&B", "SEPIA", "NEGATIVO", "TERMICO", "PIXEL", "ESBOCO", "CARTUM"]
LUZ_MODOS = ["OFF", "AUTO", "FORTE"]
TIMERS = [0, 3, 5]

PONTAS = {"indicador": 8, "medio": 12, "anelar": 16, "mindinho": 20}
JUNTAS = {"indicador": 6, "medio": 10, "anelar": 14, "mindinho": 18}

# Mao da cor: 1 dedo levantado = 1 cor
DEDOS_ORDEM = ["polegar", "indicador", "medio", "anelar", "mindinho"]
PONTA_DEDO = {"polegar": 4, "indicador": 8, "medio": 12, "anelar": 16, "mindinho": 20}
SIGLAS = ["pol", "ind", "med", "ane", "min"]
COR_OPCOES = [                   
    ("AMARELO", (0, 255, 255)), # polegar
    ("VERMELHO", (0, 0, 255)), # indicador
    ("VERDE", (0, 255, 0)), # medio
    ("AZUL", (255, 120, 0)), # anelar
    ("ARCO-IRIS", None), # mindinho
]

OLHO_A = (33, 160, 158, 133, 153, 144)
OLHO_B = (362, 385, 387, 263, 373, 380)

ABAS = ["DESENHO", "VISUAL", "EXTRAS"]
REPETE = {"pincel", "tamanho", "simetria", "estilo", "fundo", "filtro", "luz", "timer"}

DICAS = {
    "dominante": "Destro: pincel na mao direita. Canhoto: na esquerda.",
    "pincel": "LISO, NEON (brilha), SPRAY (aerografo) ou FAISCAS.",
    "tamanho": "Na mao da cor, faca um L (polegar+indicador) p/ ajustar.",
    "simetria": "Espelha o traco: caleidoscopio!",
    "desfazer": "Desfaz o ultimo traco (tecla Z).",
    "refazer": "Refaz o traco desfeito (tecla Y).",
    "limpar": "Apaga o desenho todo (da pra desfazer com Z).",
    "salvar": "Salva so o desenho em PNG transparente (tecla S).",
    "estilo": "MALHA, NEON ou PONTOS: como rosto e maos aparecem.",
    "fundo": "AUTO, CAMERA, ESCURO, PRETO, BRANCO, DESFOCADO, SO VOCE.",
    "filtro": "Efeito aplicado na imagem da camera.",
    "luz": "Clareia o video no escuro (ajuda a achar as maos).",
    "rosto": "Mostra ou esconde a malha do rosto.",
    "maos": "Mostra ou esconde o esqueleto das maos.",
    "textos": "Mostra ou esconde os textos e o FPS.",
    "boca": "Abrir a boca solta confete e mostra o medidor.",
    "jogo": "Estoure bolhas com os dedos por 30s. Fuja das vermelhas!",
    "gravar": "Grava video MP4 na pasta fotos (tecla R).",
    "timer": "Contagem antes da foto do punho.",
    "foto": "Fechar o punho da mao do pincel tira foto.",
    "pintura": "O V de paz liga a pintura.",
    "piscada": "Piscar o olho esquerdo desfaz, o direito refaz.",
    "sons": "Efeitos sonoros (so no Windows).",
    "ajuda": "Mostra o guia de gestos e teclas (tecla H).",
}

AJUDA = [
    "GUIA RAPIDO",
    "",
    "MAO DO PINCEL (a dominante)",
    "  V de paz = liga a pintura   |   1 dedo = pinta",
    "  tirar o dedo = para de pintar   |   punho = foto",
    "MAO DA COR (a outra)",
    "  1 dedo = cor (polegar amarelo, indicador vermelho,",
    "  medio verde, anelar azul, mindinho arco-iris)",
    "  L (polegar+indicador) = tamanho   |   punho = borracha",
    "ROSTO   abrir a boca = confete",
    "MENU    segure o indicador no botao MENU por 2 s",
    "",
    "TECLAS  1/2/3 estilo | Z desfaz | Y refaz | C limpa | S salva",
    "        R grava | F tela cheia | T troca mao | ESPACO foto",
    "        M menu | H ajuda | Q sai",
]


# FUNCOES BASICAS
def dist(a, b):
    return math.hypot(a.x - b.x, a.y - b.y)


def dedos_esticados(mao):
    """4 dedos (sem polegar): True se a ponta esta mais longe do pulso que a junta."""
    pulso = mao.landmark[0]
    return {d: dist(mao.landmark[PONTAS[d]], pulso) > dist(mao.landmark[JUNTAS[d]], pulso)
            for d in PONTAS}


def polegar_esticado(mao):
    l = mao.landmark
    return dist(l[4], l[17]) > dist(l[3], l[17]) * 1.1


def dedos5(mao):
    d = dedos_esticados(mao)
    d["polegar"] = polegar_esticado(mao)
    return d


def mao_fechada(mao):
    return not any(dedos_esticados(mao).values())


def gesto_paz(mao):
    d = dedos_esticados(mao)
    return d["indicador"] and d["medio"] and not d["anelar"] and not d["mindinho"]


def um_dedo(mao):
    d = dedos_esticados(mao)
    return d["indicador"] and not d["medio"] and not d["anelar"] and not d["mindinho"]


def tamanho_L(mao):
    """Abertura entre polegar e indicador -> tamanho do pincel (2 a 40)."""
    l = mao.landmark
    palma = dist(l[0], l[9]) + 1e-6
    r = dist(l[4], l[8]) / palma
    return float(np.interp(r, [0.25, 1.4], [2, 40]))


def abertura_boca(rosto):
    l = rosto.landmark
    return dist(l[13], l[14]) / (dist(l[78], l[308]) + 1e-6)


def ear_olho(lm, ids, w, h):
    """Retorna (EAR, x_medio_em_pixels) do olho."""
    p = [(lm[i].x * w, lm[i].y * h) for i in ids]

    def d(a, b):
        return math.hypot(a[0] - b[0], a[1] - b[1])

    ear = (d(p[1], p[5]) + d(p[2], p[4])) / (2.0 * d(p[0], p[3]) + 1e-6)
    return ear, (p[0][0] + p[3][0]) / 2


def separar_maos(res):
    """Devolve (mao_direita, mao_esquerda) DO USUARIO. A imagem esta espelhada."""
    maos = res.multi_hand_landmarks
    if not maos:
        return None, None
    if len(maos) >= 2:
        esq, dir_ = sorted(maos[:2], key=lambda m: m.landmark[0].x)
        return dir_, esq
    hd = res.multi_handedness
    rotulo = hd[0].classification[0].label if hd else "Right"
    return (maos[0], None) if rotulo == "Right" else (None, maos[0])


_cache_hsv = {}


def cor_hsv(h):
    h = int(h) % 180
    if h not in _cache_hsv:
        bgr = cv2.cvtColor(np.uint8([[[h, 255, 255]]]), cv2.COLOR_HSV2BGR)[0][0]
        _cache_hsv[h] = tuple(int(c) for c in bgr)
    return _cache_hsv[h]


def cor_arco_iris():
    return cor_hsv((time.time() * 60) % 180)


# DESENHO DE TEXTO / CAIXAS
def txt(img, s, org, esc=0.55, cor=BRANCO, esp=1, borda=True):
    org = (int(org[0]), int(org[1]))
    if borda:
        cv2.putText(img, s, org, FONTE, esc, (0, 0, 0), esp + 2, cv2.LINE_AA)
    cv2.putText(img, s, org, FONTE, esc, cor, esp, cv2.LINE_AA)


def tam_txt(s, esc, esp=1):
    (tw, th), _ = cv2.getTextSize(s, FONTE, esc, esp)
    return tw, th


def txt_centro(img, s, cx, cy, esc=0.55, cor=BRANCO, esp=1, borda=True):
    tw, th = tam_txt(s, esc, esp)
    txt(img, s, (cx - tw / 2, cy + th / 2), esc, cor, esp, borda)


def rrect(img, p0, p1, cor, r=8, esp=-1, alpha=1.0):
    """Retangulo de cantos arredondados (preenchido se esp<0), com transparencia."""
    H, W = img.shape[:2]
    x0, y0, x1, y1 = int(p0[0]), int(p0[1]), int(p1[0]), int(p1[1])
    if x1 <= x0 or y1 <= y0:
        return
    cx0, cy0, cx1, cy1 = max(0, x0), max(0, y0), min(W, x1 + 1), min(H, y1 + 1)
    if cx1 <= cx0 or cy1 <= cy0:
        return
    roi = img[cy0:cy1, cx0:cx1]
    ov = roi.copy()
    lx0, ly0, lx1, ly1 = x0 - cx0, y0 - cy0, x1 - cx0, y1 - cy0
    r = int(max(0, min(r, (x1 - x0) // 2, (y1 - y0) // 2)))
    if esp < 0:
        cv2.rectangle(ov, (lx0 + r, ly0), (lx1 - r, ly1), cor, -1)
        cv2.rectangle(ov, (lx0, ly0 + r), (lx1, ly1 - r), cor, -1)
        if r > 0:
            for cx, cy in ((lx0 + r, ly0 + r), (lx1 - r, ly0 + r),
                           (lx0 + r, ly1 - r), (lx1 - r, ly1 - r)):
                cv2.circle(ov, (cx, cy), r, cor, -1, cv2.LINE_AA)
    else:
        cv2.line(ov, (lx0 + r, ly0), (lx1 - r, ly0), cor, esp, cv2.LINE_AA)
        cv2.line(ov, (lx0 + r, ly1), (lx1 - r, ly1), cor, esp, cv2.LINE_AA)
        cv2.line(ov, (lx0, ly0 + r), (lx0, ly1 - r), cor, esp, cv2.LINE_AA)
        cv2.line(ov, (lx1, ly0 + r), (lx1, ly1 - r), cor, esp, cv2.LINE_AA)
        if r > 0:
            for cx, cy, a0 in ((lx0 + r, ly0 + r, 180), (lx1 - r, ly0 + r, 270),
                               (lx1 - r, ly1 - r, 0), (lx0 + r, ly1 - r, 90)):
                cv2.ellipse(ov, (cx, cy), (r, r), 0, a0, a0 + 90, cor, esp, cv2.LINE_AA)
    if alpha >= 0.999:
        roi[:] = ov
    else:
        roi[:] = cv2.addWeighted(ov, alpha, roi, 1 - alpha, 0)


def dentro(p, box):
    return box[0] <= p[0] <= box[2] and box[1] <= p[1] <= box[3]


# FILTROS DE IMAGEM
_SEPIA = np.array([[0.131, 0.534, 0.272],
                   [0.168, 0.686, 0.349],
                   [0.189, 0.769, 0.393]], np.float32)


def aplicar_filtro(img, nome):
    if nome == "NORMAL":
        return img
    if nome == "P&B":
        return cv2.cvtColor(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2BGR)
    if nome == "SEPIA":
        return cv2.transform(img, _SEPIA)
    if nome == "NEGATIVO":
        return cv2.bitwise_not(img)
    if nome == "TERMICO":
        g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return cv2.applyColorMap(g, getattr(cv2, "COLORMAP_INFERNO", cv2.COLORMAP_JET))
    h, w = img.shape[:2]
    if nome == "PIXEL":
        p = cv2.resize(img, (max(1, w // 18), max(1, h // 18)), interpolation=cv2.INTER_AREA)
        return cv2.resize(p, (w, h), interpolation=cv2.INTER_NEAREST)
    if nome == "ESBOCO":
        g = cv2.GaussianBlur(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), (5, 5), 0)
        ed = cv2.dilate(cv2.Canny(g, 50, 130), None)
        return cv2.cvtColor(255 - ed, cv2.COLOR_GRAY2BGR)
    if nome == "CARTUM":
        p = cv2.resize(img, (max(1, w // 2), max(1, h // 2)), interpolation=cv2.INTER_AREA)
        p = cv2.bilateralFilter(p, 7, 50, 50)
        q = (p // 43) * 43 + 21
        ed = cv2.Canny(cv2.GaussianBlur(cv2.cvtColor(p, cv2.COLOR_BGR2GRAY), (3, 3), 0), 60, 130)
        q[ed > 0] = 0
        return cv2.resize(q, (w, h), interpolation=cv2.INTER_LINEAR)
    return img


class Luz:
    """Clareia a imagem em ambientes escuros (gamma)."""

    def __init__(self):
        self.modo = 1 
        self.g = 1.0
        self.n = 0
        self.luts = {}

    def _lut(self, g):
        if g not in self.luts:
            x = np.arange(256) / 255.0
            self.luts[g] = np.clip((x ** g) * 255, 0, 255).astype(np.uint8)
        return self.luts[g]

    def aplicar(self, frame):
        modo = LUZ_MODOS[self.modo]
        if modo == "OFF":
            return frame
        if modo == "AUTO":
            self.n += 1
            if self.n % 6 == 1:
                media = float(cv2.resize(frame, (64, 48)).mean())
                alvo = float(np.interp(media, [25, 120], [0.45, 1.0]))
                self.g += (alvo - self.g) * 0.4
            g = self.g
        else:
            g = 0.5
        g = round(g * 20) / 20.0
        if g >= 0.98:
            return frame
        return cv2.LUT(frame, self._lut(g))


# FILTRO DE SUAVIZACAO
class OneEuro:
    """Filtro 1-euro: tira o tremido sem atrasar movimentos rapidos."""

    def __init__(self, mincutoff=1.2, beta=0.015, dcutoff=1.0):
        self.mc, self.beta, self.dc = mincutoff, beta, dcutoff
        self.reset()

    def reset(self):
        self.x = None
        self.dx = np.zeros(2)
        self.t = None

    @staticmethod
    def _alfa(cutoff, dt):
        tau = 1.0 / (2 * math.pi * cutoff)
        return 1.0 / (1.0 + tau / dt)

    def __call__(self, p, t):
        p = np.asarray(p, dtype=float)
        if self.x is None:
            self.x, self.t = p, t
            return float(p[0]), float(p[1])
        dt = max(t - self.t, 1e-3)
        dx = (p - self.x) / dt
        ad = self._alfa(self.dc, dt)
        self.dx = ad * dx + (1 - ad) * self.dx
        cutoff = self.mc + self.beta * float(np.hypot(*self.dx))
        a = self._alfa(cutoff, dt)
        self.x = a * p + (1 - a) * self.x
        self.t = t
        return float(self.x[0]), float(self.x[1])


class Estavel:
    """So devolve True se o gesto aparecer em 'minimo' dos ultimos 'n' quadros."""

    def __init__(self, n=5, minimo=4):
        self.h = deque(maxlen=n)
        self.minimo = minimo

    def __call__(self, v):
        self.h.append(bool(v))
        return sum(self.h) >= self.minimo

    def reset(self):
        self.h.clear()


# SONS
class Sons:
    def __init__(self):
        self.ativo = True
        self.ok = False
        self.q = queue.Queue(maxsize=6)
        try:
            import winsound
            self.ws = winsound
            self.ok = True
            threading.Thread(target=self._loop, daemon=True).start()
        except Exception:
            self.ws = None

    def _loop(self):
        while True:
            f, d = self.q.get()
            try:
                self.ws.Beep(int(f), int(d))
            except Exception:
                pass

    def tocar(self, freq, dur=60):
        if self.ok and self.ativo:
            try:
                self.q.put_nowait((freq, dur))
            except queue.Full:
                pass


# PARTICULAS
class Particulas:
    def __init__(self):
        self.p = []

    def emitir(self, x, y, n, cor=None, vel=(60, 260), ang=(0, 2 * math.pi),
               vida=(0.6, 1.3), raio=(2, 5), grav=300):
        for _ in range(n):
            a = random.uniform(*ang)
            v = random.uniform(*vel)
            c = cor if cor is not None else cor_hsv(random.randint(0, 179))
            vd = random.uniform(*vida)
            self.p.append([x, y, math.cos(a) * v, math.sin(a) * v, vd, vd, c,
                           random.uniform(*raio), grav])
        if len(self.p) > 500:
            self.p = self.p[-500:]

    def atualizar(self, dt):
        vivos = []
        for q in self.p:
            q[4] -= dt
            if q[4] > 0:
                q[0] += q[2] * dt
                q[1] += q[3] * dt
                q[3] += q[8] * dt
                vivos.append(q)
        self.p = vivos

    def desenhar(self, img):
        if not self.p:
            return
        camada = np.zeros_like(img)
        for q in self.p:
            f = q[4] / q[5]
            c = tuple(int(v * f) for v in q[6])
            cv2.circle(camada, (int(q[0]), int(q[1])), max(1, int(q[7] * (0.5 + 0.5 * f))),
                       c, -1, cv2.LINE_AA)
        cv2.add(img, camada, dst=img)


# QUADRO DE PINTURA
class Quadro:
    """Camadas de pintura: guarda os tracos (para desfazer/refazer) e redesenha."""

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.cv = np.zeros((h, w, 3), np.uint8) 
        self.mk = np.zeros((h, w), np.uint8)
        self.bl = np.zeros((h, w, 3), np.uint8)
        self.tracos = []
        self.pilha = []
        self.atual = None
        self.vazio = True
        self.tem_neon = False

    def _zerar(self):
        self.cv[:] = 0
        self.mk[:] = 0
        self.bl[:] = 0
        self.vazio = True
        self.tem_neon = False

    # simetria
    def _copias(self, p0, p1, sim):
        _, n, esp = SIMETRIAS[sim]
        if n == 1 and not esp:
            return [(p0, p1)]
        cx, cy = self.w / 2, self.h / 2
        res = []
        for k in range(n):
            ang = 2 * math.pi * k / n
            c, s = math.cos(ang), math.sin(ang)
            for espelho in ([False, True] if esp else [False]):
                pts = []
                for (x, y) in (p0, p1):
                    if espelho:
                        x = 2 * cx - x
                    dx, dy = x - cx, y - cy
                    pts.append((cx + dx * c - dy * s, cy + dx * s + dy * c))
                res.append((pts[0], pts[1]))
        return res

    # um segmento
    def _seg(self, d, p0, p1, cor, tam):
        estilo = d["estilo"]
        self.vazio = False
        for q0, q1 in self._copias(p0, p1, d["sim"]):
            a = (int(round(q0[0])), int(round(q0[1])))
            b = (int(round(q1[0])), int(round(q1[1])))
            if d["apagar"]:
                t = max(3, int(tam * 2.5))
                cv2.line(self.cv, a, b, (0, 0, 0), t, cv2.LINE_AA)
                cv2.line(self.mk, a, b, 0, t, cv2.LINE_AA)
                cv2.line(self.bl, a, b, (0, 0, 0), t, cv2.LINE_AA)
            elif estilo == "NEON":
                t = max(2, tam)
                nucleo = tuple(int(c * 0.45 + 255 * 0.55) for c in cor)
                cv2.line(self.bl, a, b, cor, int(t * 1.6) + 2, cv2.LINE_AA)
                cv2.line(self.cv, a, b, cor, t + 2, cv2.LINE_AA)
                cv2.line(self.mk, a, b, 255, t + 2, cv2.LINE_AA)
                cv2.line(self.cv, a, b, nucleo, max(1, t // 2), cv2.LINE_AA)
                self.tem_neon = True
            elif estilo == "SPRAY":
                rng = d["rng"]
                comp = math.hypot(b[0] - a[0], b[1] - a[1])
                n = min(60, int(6 + tam * 0.5 + comp * 0.6))
                raio = max(3.0, tam * 1.6)
                for _ in range(n):
                    f = rng.random()
                    cx = a[0] + (b[0] - a[0]) * f
                    cy = a[1] + (b[1] - a[1]) * f
                    ang = rng.random() * 6.283
                    r = (rng.random() ** 0.6) * raio
                    px, py = int(cx + math.cos(ang) * r), int(cy + math.sin(ang) * r)
                    cv2.circle(self.cv, (px, py), 1, cor, -1)
                    cv2.circle(self.mk, (px, py), 1, 255, -1)
            else:
                t = max(1, tam)
                cv2.line(self.cv, a, b, cor, t, cv2.LINE_AA)
                cv2.line(self.mk, a, b, 255, t, cv2.LINE_AA)

    # tracos
    def iniciar(self, estilo, apagar, sim):
        seed = random.randrange(1 << 30)
        d = {"pts": [], "estilo": estilo, "apagar": apagar, "sim": sim,
             "seed": seed, "rng": random.Random(seed)}
        self.tracos.append(d)
        self.pilha.clear()
        self.atual = d
        return d

    def adicionar(self, x, y, cor, tam):
        d = self.atual
        ant = d["pts"][-1] if d["pts"] else None
        d["pts"].append((x, y, cor, tam))
        self._seg(d, (ant[0], ant[1]) if ant else (x, y), (x, y), cor, tam)

    def terminar(self):
        self.atual = None

    def _desenhar_traco(self, d):
        d["rng"] = random.Random(d["seed"])
        ant = None
        for (x, y, cor, tam) in d["pts"]:
            self._seg(d, ant if ant else (x, y), (x, y), cor, tam)
            ant = (x, y)

    def _redesenhar(self):
        self._zerar()
        ini = 0
        for i, d in enumerate(self.tracos):
            if d["estilo"] == "LIMPAR":
                ini = i + 1
        for d in self.tracos[ini:]:
            self._desenhar_traco(d)

    def desfazer(self):
        self.atual = None
        if not self.tracos:
            return False
        self.pilha.append(self.tracos.pop())
        self._redesenhar()
        return True

    def refazer(self):
        if not self.pilha:
            return False
        d = self.pilha.pop()
        self.tracos.append(d)
        if d["estilo"] == "LIMPAR":
            self._zerar()
        else:
            self._desenhar_traco(d)
        return True

    def limpar(self):
        self.atual = None
        if self.vazio:
            return False
        self.tracos.append({"estilo": "LIMPAR", "pts": [], "apagar": False, "sim": 0,
                            "seed": 0, "rng": random.Random(0)})
        self.pilha.clear()
        self._zerar()
        return True

    # composicao
    def componer(self, base):
        if self.vazio:
            return base
        inv = cv2.bitwise_not(self.mk)
        out = cv2.multiply(base, cv2.merge([inv, inv, inv]), scale=1 / 255.0)
        out = cv2.add(out, self.cv)
        if self.tem_neon:
            pq = cv2.resize(self.bl, (max(1, self.w // 4), max(1, self.h // 4)),
                            interpolation=cv2.INTER_AREA)
            pq = cv2.GaussianBlur(pq, (0, 0), 4)
            luz = cv2.resize(pq, (self.w, self.h), interpolation=cv2.INTER_LINEAR)
            out = cv2.add(out, cv2.convertScaleAbs(luz, alpha=1.7))
        return out

    def salvar_png(self, caminho):
        if self.vazio:
            return False
        a = self.mk.astype(np.float32) / 255.0
        rgb = self.cv.astype(np.float32) / np.maximum(a, 1e-3)[..., None]
        rgb = np.clip(rgb, 0, 255).astype(np.uint8)
        return bool(cv2.imwrite(caminho, np.dstack([rgb, self.mk])))


# JOGO DE BOLHAS
class Jogo:
    def __init__(self):
        self.ativo = False
        self.bolhas = []
        self.pops = []
        self.pontos = 0
        self.t0 = 0.0
        self.prox = 0.0
        self.combo = 0
        self.ultimo_pop = 0.0
        self.fim_ate = 0.0
        self.resultado = ""
        self.recorde = self._ler()

    @staticmethod
    def _ler():
        try:
            with open(ARQ_RECORDE) as f:
                return int(f.read().strip())
        except Exception:
            return 0

    def _gravar(self):
        try:
            with open(ARQ_RECORDE, "w") as f:
                f.write(str(self.recorde))
        except Exception:
            pass

    def iniciar(self, agora):
        self.ativo = True
        self.bolhas, self.pops = [], []
        self.pontos, self.combo = 0, 0
        self.t0 = agora
        self.prox = agora + 0.4
        self.fim_ate = 0.0

    def parar(self):
        self.ativo = False
        self.bolhas, self.pops = [], []

    def _spawn(self, w, h, t):
        r = random.randint(int(h * 0.05), int(h * 0.09))
        sorte = random.random()
        tipo = "ouro" if sorte < 0.08 else ("bomba" if sorte < 0.20 else "normal")
        cor = {"normal": cor_hsv(random.choice([85, 100, 110, 130, 150, 20])),
               "ouro": (0, 200, 255), "bomba": (40, 40, 220)}[tipo]
        x0 = random.randint(r + 20, max(r + 21, w - r - 20))
        self.bolhas.append({"x": float(x0), "x0": x0, "y": float(h + r), "r": r,
                            "vy": random.uniform(0.18, 0.32) * h * (1 + t / 60.0),
                            "fase": random.uniform(0, 6.28), "tipo": tipo, "cor": cor})

    def _estourar(self, b, agora, part, sons):
        if b["tipo"] == "bomba":
            ganho, self.combo = -3, 0
            sons.tocar(200, 120)
        else:
            self.combo = self.combo + 1 if agora - self.ultimo_pop < 1.2 else 1
            ganho = (5 if b["tipo"] == "ouro" else 1) + self.combo // 5
            sons.tocar(1500 if b["tipo"] == "ouro" else 650 + 40 * min(self.combo, 10), 45)
        self.pontos = max(0, self.pontos + ganho)
        self.ultimo_pop = agora
        part.emitir(b["x"], b["y"], 16, cor=b["cor"], vel=(80, 320), vida=(0.4, 0.9),
                    raio=(2, 5), grav=200)
        self.pops.append([b["x"], b["y"], ("+%d" % ganho) if ganho > 0 else str(ganho),
                          agora + 0.9, VERDE if ganho > 0 else VERMELHO])

    def atualizar(self, agora, dt, w, h, toques, part, sons):
        self.pops = [p for p in self.pops if p[3] > agora]
        if not self.ativo:
            return
        t = agora - self.t0
        if t >= DURACAO_JOGO:
            self.ativo = False
            novo = self.pontos > self.recorde
            if novo:
                self.recorde = self.pontos
                self._gravar()
            self.fim_ate = agora + 6
            self.resultado = ("NOVO RECORDE!  " if novo else "") + "%d pontos" % self.pontos
            self.bolhas = []
            return
        if agora >= self.prox:
            self._spawn(w, h, t)
            self.prox = agora + max(0.22, 0.85 - t * 0.02)
        for b in self.bolhas:
            b["y"] -= b["vy"] * dt
            b["fase"] += dt * 2
            b["x"] = b["x0"] + math.sin(b["fase"]) * 18
        self.bolhas = [b for b in self.bolhas if b["y"] + b["r"] > -10]
        restantes = []
        for b in self.bolhas:
            if any((b["x"] - tx) ** 2 + (b["y"] - ty) ** 2 <= (b["r"] + tr) ** 2
                   for tx, ty, tr in toques):
                self._estourar(b, agora, part, sons)
            else:
                restantes.append(b)
        self.bolhas = restantes

    def desenhar(self, img, agora, e):
        h, w = img.shape[:2]
        if self.bolhas:
            camada = np.zeros_like(img)
            for b in self.bolhas:
                cv2.circle(camada, (int(b["x"]), int(b["y"])), b["r"], b["cor"], -1, cv2.LINE_AA)
            cv2.add(img, cv2.convertScaleAbs(camada, alpha=0.35), dst=img)
            for b in self.bolhas:
                c = (int(b["x"]), int(b["y"]))
                cv2.circle(img, c, b["r"], b["cor"], 3 if b["tipo"] == "ouro" else 2, cv2.LINE_AA)
                cv2.circle(img, (c[0] - b["r"] // 3, c[1] - b["r"] // 3),
                           max(2, b["r"] // 6), BRANCO, -1, cv2.LINE_AA)
                if b["tipo"] == "bomba":
                    d = b["r"] // 2
                    cv2.line(img, (c[0] - d, c[1] - d), (c[0] + d, c[1] + d), BRANCO, 2, cv2.LINE_AA)
                    cv2.line(img, (c[0] - d, c[1] + d), (c[0] + d, c[1] - d), BRANCO, 2, cv2.LINE_AA)
        for p in self.pops:
            sobe = (1 - (p[3] - agora) / 0.9) * 40 * e
            txt_centro(img, p[2], p[0], p[1] - sobe, 0.9 * e, p[4], 2)
        if self.ativo:
            resta = max(0, int(math.ceil(DURACAO_JOGO - (agora - self.t0))))
            txt_centro(img, "BOLHAS   %d pts   %ds   recorde %d" % (self.pontos, resta, self.recorde),
                       w / 2, 24 * e, 0.65 * e, AMARELO, 2)
            if self.combo >= 3:
                txt_centro(img, "COMBO x%d" % self.combo, w / 2, 52 * e, 0.7 * e, VERDE, 2)
        elif agora < self.fim_ate:
            txt_centro(img, "FIM!", w / 2, h / 2 - 40 * e, 2.0 * e, AMARELO, 4)
            txt_centro(img, self.resultado, w / 2, h / 2 + 15 * e, 0.9 * e, BRANCO, 2)
            txt_centro(img, "recorde: %d" % self.recorde, w / 2, h / 2 + 50 * e, 0.7 * e, CINZA, 1)


# GRAVADOR DE VIDEO
class Gravador:
    def __init__(self):
        self.vw = None
        self.ativo = False
        self.fps = 20
        self.t_prox = 0.0
        self.t0 = 0.0

    def iniciar(self, w, h, agora):
        os.makedirs(PASTA, exist_ok=True)
        nome = time.strftime("video_%Y%m%d_%H%M%S.mp4")
        vw = cv2.VideoWriter(os.path.join(PASTA, nome), cv2.VideoWriter_fourcc(*"mp4v"),
                             self.fps, (w, h))
        if not vw.isOpened():
            return None
        self.vw, self.ativo = vw, True
        self.t0 = self.t_prox = agora
        return nome

    def frame(self, img, agora):
        if not self.ativo:
            return
        n = 0
        while agora >= self.t_prox and n < 3:
            self.vw.write(img)
            self.t_prox += 1.0 / self.fps
            n += 1
        if agora - self.t_prox > 0.5:
            self.t_prox = agora

    def parar(self):
        if self.vw is not None:
            self.vw.release()
        self.vw, self.ativo = None, False


# DESENHO DAS MAOS
def desenhar_mao(img, mao, estilo, cor, w, h):
    mpm = mp.solutions
    if estilo == 1:
        mpm.drawing_utils.draw_landmarks(
            img, mao, mpm.hands.HAND_CONNECTIONS,
            mpm.drawing_styles.get_default_hand_landmarks_style(),
            mpm.drawing_styles.get_default_hand_connections_style())
    elif estilo == 2:
        mpm.drawing_utils.draw_landmarks(
            img, mao, mpm.hands.HAND_CONNECTIONS,
            mpm.drawing_utils.DrawingSpec(color=cor, thickness=3, circle_radius=3),
            mpm.drawing_utils.DrawingSpec(color=cor, thickness=3))
    else:
        for p in mao.landmark:
            cv2.circle(img, (int(p.x * w), int(p.y * h)), 3, AMARELO, -1)


# APLICATIVO
class App:
    def __init__(self, cap, face_mesh, hands):
        self.cap, self.fm, self.hd = cap, face_mesh, hands
        self.agora = time.time()
        self.sons, self.part, self.jogo = Sons(), Particulas(), Jogo()
        self.grav, self.luz = Gravador(), Luz()
        self.quadro = None
        self.seg = None
        self.w = self.h = 0
        self.e = 1.0
        self.g = {}

        self.cfg = {"foto": True, "pintura": True, "rosto": True, "maos": True,
                    "boca": True, "textos": True, "piscada": False, "sons": True}
        self.estilo = 1
        self.fundo_i = 0
        self.filtro_i = 0
        self.pincel_i = 0
        self.sim_i = 0
        self.tamanho = 8.0
        self.timer_i = 0
        self.dominante = "destro"
        self.cor_idx = 4
        self.menu_aberto = False
        self.pagina = 0
        self.hover_alvo = None
        self.hover_inicio = 0.0
        self.hover_ok = False
        self.hover_visto = 0.0

        # gestos
        self.deb_fech, self.deb_paz = Estavel(5, 4), Estavel(5, 4)
        self.deb_borracha, self.deb_L = Estavel(4, 3), Estavel(5, 4)
        self.f_ponta = OneEuro()
        self.cor_cand, self.cor_cont = None, 0
        self.armada, self.armada_desde = False, 0.0
        self.perdido = None
        self.ult_pt = None
        self.t_fim = 0.0
        self.mao_aberta_antes = False
        self.ultima_foto = 0.0
        self.foto_em = None
        self.tick_ant = None
        self.pedir_foto = False
        self.tirar_foto = False
        self.flash = 0
        self.apagando = False
        self.modo_L = False
        self.gesto = "-"
        self.ponteiro = None
        self.cursor = None
        self.mao_dir = self.mao_esq = self.mao_des = self.mao_cor = None
        self.res_mao = None
        self.rosto = None
        self.boca = 0.0
        self.rgb = None
        self.wink = {"E": None, "D": None}
        self.wink_ok = {"E": False, "D": False}

        # interface
        self.avisos = []
        self.ajuda_ate = 0.0
        self.fps = 30.0
        self.tela_cheia = False
        self.cor_anim = BRANCO

    # util
    def toast(self, s, dur=2.0, cor=BRANCO):
        self.avisos.append([s, self.agora + dur, cor])
        self.avisos = self.avisos[-3:]

    @property
    def cor_traco(self):
        c = COR_OPCOES[self.cor_idx][1]
        return self.cor_anim if c is None else c

    # menu
    def itens_pagina(self, p=None):
        p = self.pagina if p is None else p
        c = self.cfg

        def lig(b):
            return ("LIGADO", VERDE) if b else ("DESLIGADO", VERMELHO)

        if p == 0:
            return [("dominante", "Voce e", self.dominante.upper(), BRANCO),
                    ("pincel", "Pincel", PINCEIS[self.pincel_i], BRANCO),
                    ("tamanho", "Tamanho", "%d px" % int(round(self.tamanho)), BRANCO),
                    ("simetria", "Simetria", SIMETRIAS[self.sim_i][0], BRANCO),
                    ("desfazer", "Desfazer", "", BRANCO),
                    ("refazer", "Refazer", "", BRANCO),
                    ("limpar", "Limpar tudo", "", BRANCO),
                    ("salvar", "Salvar desenho", "", BRANCO)]
        if p == 1:
            return [("estilo", "Estilo", ESTILOS[self.estilo], BRANCO),
                    ("fundo", "Fundo", FUNDOS[self.fundo_i], BRANCO),
                    ("filtro", "Filtro", FILTROS[self.filtro_i], BRANCO),
                    ("luz", "Luz extra", LUZ_MODOS[self.luz.modo], BRANCO),
                    ("rosto", "Mostrar rosto") + lig(c["rosto"]),
                    ("maos", "Mostrar maos") + lig(c["maos"]),
                    ("textos", "Textos na tela") + lig(c["textos"]),
                    ("boca", "Efeito da boca") + lig(c["boca"])]
        return [("jogo", "Jogo de bolhas", "JOGAR" if not self.jogo.ativo else "PARAR", VERDE),
                ("gravar", "Gravar video", "PARAR" if self.grav.ativo else "GRAVAR",
                 VERMELHO if self.grav.ativo else BRANCO),
                ("timer", "Timer da foto", "OFF" if TIMERS[self.timer_i] == 0
                 else "%d s" % TIMERS[self.timer_i], BRANCO),
                ("foto", "Foto (punho)") + lig(c["foto"]),
                ("pintura", "Pintura (V)") + lig(c["pintura"]),
                ("piscada", "Piscadinha") + lig(c["piscada"]),
                ("sons", "Sons") + lig(c["sons"]),
                ("ajuda", "Ajuda", "ABRIR", BRANCO)]

    def geometria(self):
        w, h, e = self.w, self.h, self.e
        g = {"btn": (w - int(120 * e), int(10 * e), w - int(10 * e), int(48 * e))}
        pw = int(w * 0.90)
        px0 = (w - pw) // 2
        px1 = px0 + pw
        pad, abah, ih, lin, dica = int(12 * e), int(42 * e), int(60 * e), 4, int(30 * e)
        ph = pad + abah + pad + lin * ih + dica + pad
        py0 = (h - ph) // 2
        g["painel"] = (px0, py0, px1, py0 + ph)
        fechw = int(52 * e)
        ay0, ay1 = py0 + pad, py0 + pad + abah
        aw = (pw - 3 * pad - fechw) // 3
        g["abas"] = [(px0 + pad + i * aw, ay0, px0 + pad + (i + 1) * aw - int(6 * e), ay1)
                     for i in range(3)]
        g["fechar"] = (px1 - pad - fechw, ay0, px1 - pad, ay1)
        iy0 = ay1 + pad
        colw = (pw - 3 * pad) // 2
        g["itens"] = []
        for i in range(8):
            col, l = divmod(i, 4)
            x0 = px0 + pad + col * (colw + pad)
            y0 = iy0 + l * ih
            g["itens"].append((x0, y0, x0 + colw, y0 + ih - int(8 * e)))
        g["dica"] = (px0 + pad, iy0 + lin * ih, px1 - pad, iy0 + lin * ih + dica)
        self.g = g

    def alvo_menu(self, p):
        g = self.g
        if dentro(p, g["btn"]):
            return "menu"
        if not self.menu_aberto:
            return None
        if dentro(p, g["fechar"]):
            return "fechar"
        for i, b in enumerate(g["abas"]):
            if dentro(p, b):
                return "aba%d" % i
        for i, b in enumerate(g["itens"]):
            if dentro(p, b):
                return self.itens_pagina()[i][0]
        return None

    @staticmethod
    def dwell_de(i):
        if i == "menu":
            return DWELL_MENU
        if i == "fechar" or i.startswith("aba"):
            return DWELL_ABA
        return DWELL_ITEM

    # acoes
    def desfazer(self):
        ok = self.quadro is not None and self.quadro.desfazer()
        self.toast("DESFEITO" if ok else "Nada para desfazer", 1.2, CIANO)
        if ok:
            self.sons.tocar(500, 40)

    def refazer(self):
        ok = self.quadro is not None and self.quadro.refazer()
        self.toast("REFEITO" if ok else "Nada para refazer", 1.2, CIANO)
        if ok:
            self.sons.tocar(700, 40)

    def salvar_desenho(self):
        os.makedirs(PASTA, exist_ok=True)
        nome = time.strftime("desenho_%Y%m%d_%H%M%S.png")
        ok = self.quadro is not None and self.quadro.salvar_png(os.path.join(PASTA, nome))
        self.toast("Desenho salvo: " + nome if ok else "Nada desenhado ainda", 2.5, VERDE if ok else CINZA)

    def alternar_gravacao(self):
        if self.grav.ativo:
            self.grav.parar()
            self.toast("Video salvo na pasta fotos", 2.5, VERDE)
        else:
            nome = self.grav.iniciar(self.w, self.h, self.agora)
            self.toast("Gravando " + nome if nome else "Nao consegui gravar video", 2.5,
                       VERMELHO)

    def cancelar_pintura(self):
        if self.quadro is not None:
            self.quadro.terminar()
        self.armada = False
        self.perdido = None
        self.f_ponta.reset()

    def acao(self, i):
        c = self.cfg
        self.sons.tocar(900, 35)
        if i == "menu":
            self.menu_aberto = not self.menu_aberto
        elif i == "fechar":
            self.menu_aberto = False
        elif i.startswith("aba"):
            self.pagina = int(i[3:])
        elif i == "dominante":
            self.dominante = "canhoto" if self.dominante == "destro" else "destro"
            self.cancelar_pintura()
            self.toast("Pincel na mao " + ("DIREITA" if self.dominante == "destro" else "ESQUERDA"))
        elif i == "pincel":
            self.pincel_i = (self.pincel_i + 1) % len(PINCEIS)
        elif i == "tamanho":
            maiores = [t for t in TAMANHOS if t > round(self.tamanho) + 0.5]
            self.tamanho = float(maiores[0] if maiores else TAMANHOS[0])
        elif i == "simetria":
            self.sim_i = (self.sim_i + 1) % len(SIMETRIAS)
        elif i == "desfazer":
            self.desfazer()
        elif i == "refazer":
            self.refazer()
        elif i == "limpar":
            ok = self.quadro is not None and self.quadro.limpar()
            self.toast("Desenho apagado (Z desfaz)" if ok else "Nada para limpar", 1.8, CIANO)
        elif i == "salvar":
            self.salvar_desenho()
        elif i == "estilo":
            self.estilo = self.estilo % 3 + 1
        elif i == "fundo":
            self.fundo_i = (self.fundo_i + 1) % len(FUNDOS)
        elif i == "filtro":
            self.filtro_i = (self.filtro_i + 1) % len(FILTROS)
        elif i == "luz":
            self.luz.modo = (self.luz.modo + 1) % len(LUZ_MODOS)
        elif i == "timer":
            self.timer_i = (self.timer_i + 1) % len(TIMERS)
        elif i == "jogo":
            self.menu_aberto = False
            if self.jogo.ativo:
                self.jogo.parar()
            else:
                self.cancelar_pintura()
                self.jogo.iniciar(self.agora)
                self.toast("Estoure as bolhas com os dedos!", 2.5, AMARELO)
        elif i == "gravar":
            self.alternar_gravacao()
        elif i == "ajuda":
            self.menu_aberto = False
            self.ajuda_ate = self.agora + 20
        elif i in c:
            c[i] = not c[i]
            if i == "sons":
                self.sons.ativo = c[i]

    # camera
    def ler_frame(self):
        ok, frame = self.cap.read()
        if not ok:
            return None
        frame = cv2.flip(frame, 1)
        frame = self.luz.aplicar(frame)
        h, w = frame.shape[:2]
        if self.quadro is None or (self.w, self.h) != (w, h):
            self.w, self.h = w, h
            self.quadro = Quadro(w, h)
        self.e = h / 480.0
        return frame

    def detectar(self, frame):
        self.rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res_rosto = self.fm.process(self.rgb)
        self.res_mao = self.hd.process(self.rgb)
        self.rosto = res_rosto.multi_face_landmarks[0] if res_rosto.multi_face_landmarks else None
        self.mao_dir, self.mao_esq = separar_maos(self.res_mao)
        if self.dominante == "destro":
            self.mao_des, self.mao_cor = self.mao_dir, self.mao_esq
        else:
            self.mao_des, self.mao_cor = self.mao_esq, self.mao_dir

    # rosto
    def logica_rosto(self, agora):
        r = self.rosto
        w, h = self.w, self.h
        if r is None:
            self.boca = 0.0
            self.wink = {"E": None, "D": None}
            self.wink_ok = {"E": False, "D": False}
            return
        self.boca = abertura_boca(r)
        lm = r.landmark
        if self.cfg["boca"] and not self.menu_aberto and self.boca > 0.35:
            mx, my = (lm[13].x + lm[14].x) / 2 * w, (lm[13].y + lm[14].y) / 2 * h
            self.part.emitir(mx, my, 3, vel=(120, 380),
                             ang=(math.radians(30), math.radians(150)), grav=400)
        if self.cfg["piscada"] and not self.menu_aberto:
            ea, xa = ear_olho(lm, OLHO_A, w, h)
            eb, xb = ear_olho(lm, OLHO_B, w, h)
            (e_esq, e_dir) = (ea, eb) if xa < xb else (eb, ea)
            fecha = {"E": e_esq < 0.18 and e_dir > 0.24, "D": e_dir < 0.18 and e_esq > 0.24}
            for lado in ("E", "D"):
                if fecha[lado]:
                    if self.wink[lado] is None:
                        self.wink[lado] = agora
                    elif agora - self.wink[lado] > 0.5 and not self.wink_ok[lado]:
                        self.wink_ok[lado] = True
                        self.desfazer() if lado == "E" else self.refazer()
                else:
                    self.wink[lado] = None
                    self.wink_ok[lado] = False

    # maos
    def logica_maos(self, agora, dt):
        c = self.cfg
        w, h, e = self.w, self.h, self.e
        des, cor_m = self.mao_des, self.mao_cor

        # MAO DA COR
        self.apagando = False
        self.modo_L = False
        if cor_m is not None:
            d5 = dedos5(cor_m)
            ativos = [n for n in DEDOS_ORDEM if d5[n]]
            dedo = ativos[0] if len(ativos) == 1 else None
            if dedo is not None and dedo == self.cor_cand:
                self.cor_cont += 1
            else:
                self.cor_cand = dedo
                self.cor_cont = 1 if dedo else 0
            if self.cor_cand and self.cor_cont >= 5:
                self.cor_idx = DEDOS_ORDEM.index(self.cor_cand)
            self.apagando = self.deb_borracha(len(ativos) == 0)
            self.modo_L = self.deb_L(set(ativos) == {"polegar", "indicador"})
            if self.modo_L:
                self.tamanho += (tamanho_L(cor_m) - self.tamanho) * 0.35
        else:
            self.cor_cand, self.cor_cont = None, 0
            self.deb_borracha.reset()
            self.deb_L.reset()

        # MAO DO PINCEL
        ap = False
        fech = paz = False
        ponteiro = None
        if des is not None:
            ap = um_dedo(des)
            fech = self.deb_fech(mao_fechada(des))
            paz = self.deb_paz(gesto_paz(des))
            p8 = des.landmark[8]
            ponteiro = self.f_ponta((p8.x * w, p8.y * h), agora)
            self.gesto = ("PUNHO" if fech else "PAZ" if paz else "APONTANDO" if ap else "ABERTA")
        else:
            self.deb_fech.reset()
            self.deb_paz.reset()
            self.f_ponta.reset()
            self.gesto = "-"
        self.ponteiro = ponteiro

        # menu: segurar o indicador em cima de um botao
        alvo = None
        if ap and not self.armada and ponteiro is not None:
            alvo = self.alvo_menu(ponteiro)
        self.cursor = ponteiro if (ap and not self.armada) else None
        if alvo is not None:
            self.hover_visto = agora
        if alvo != self.hover_alvo:
            if alvo is None and self.hover_alvo is not None and agora - self.hover_visto < 0.25:
                pass
            else:
                self.hover_alvo, self.hover_inicio, self.hover_ok = alvo, agora, False
        if self.hover_alvo is not None and alvo == self.hover_alvo and not self.hover_ok:
            if agora - self.hover_inicio >= self.dwell_de(alvo):
                self.acao(alvo)
                if alvo in REPETE:
                    self.hover_inicio = agora
                else:
                    self.hover_ok = True

        # pintura 
        permitido = c["pintura"] and not self.menu_aberto and not self.jogo.ativo
        terminou = False
        if self.armada and not permitido:
            self.cancelar_pintura()
        if self.armada:
            if ap and ponteiro is not None:
                self.perdido = None
                apagar = self.apagando
                at = self.quadro.atual
                if at is not None and at["apagar"] != apagar:
                    self.quadro.terminar()
                    at = None
                if at is None:
                    self.quadro.iniciar(PINCEIS[self.pincel_i], apagar, self.sim_i)
                    self.ult_pt = None
                x, y = ponteiro
                if self.ult_pt is None or math.hypot(x - self.ult_pt[0], y - self.ult_pt[1]) >= 1.5:
                    self.quadro.adicionar(x, y, self.cor_traco, max(1, int(round(self.tamanho))))
                    self.ult_pt = (x, y)
                    if PINCEIS[self.pincel_i] == "FAISCAS" and not apagar:
                        self.part.emitir(x, y, 2, cor=self.cor_traco, vel=(20, 120),
                                         vida=(0.3, 0.8), raio=(1, 3), grav=250)
            elif self.quadro.atual is not None:
                if self.perdido is None:
                    self.perdido = agora
                elif agora - self.perdido > GRACA_TRACO:
                    self.cancelar_pintura()
                    terminou = True
                    self.t_fim = agora
            elif agora - self.armada_desde > TEMPO_ARMADA:
                self.cancelar_pintura()
                self.toast("Pintura desligada (faca o V de novo)", 2, CINZA)

        # V com a mao: liga a pintura
        if (permitido and paz and not self.armada and not terminou
                and agora - self.t_fim > 0.8 and des is not None):
            self.armada, self.armada_desde, self.perdido = True, agora, None
            self.sons.tocar(1000, 40)

        # foto (fechar o punho)
        self.tirar_foto = False
        pode = (c["foto"] and not self.menu_aberto and not self.jogo.ativo
                and not self.armada and not terminou)
        if (des is not None and pode and fech and self.mao_aberta_antes
                and self.foto_em is None and agora - self.ultima_foto > 2.0):
            if TIMERS[self.timer_i] == 0:
                self.tirar_foto = True
            else:
                self.foto_em = agora + TIMERS[self.timer_i]
                self.tick_ant = None
        if self.pedir_foto and self.foto_em is None:
            self.tirar_foto, self.pedir_foto = True, False
        if self.foto_em is not None:
            if agora >= self.foto_em:
                self.foto_em = None
                self.tirar_foto = True
            else:
                n = int(math.ceil(self.foto_em - agora))
                if n != self.tick_ant:
                    self.tick_ant = n
                    self.sons.tocar(800, 60)
        if self.tirar_foto:
            self.ultima_foto = agora
        self.mao_aberta_antes = des is not None and not fech and not terminou

    # jogo
    def logica_jogo(self, agora, dt):
        w, h, e = self.w, self.h, self.e
        toques = []
        for m in (self.mao_dir, self.mao_esq):
            if m is not None:
                for idx in (4, 8, 12, 16, 20):
                    toques.append((m.landmark[idx].x * w, m.landmark[idx].y * h, int(10 * e)))
        if self.rosto is not None and self.boca > 0.35:
            lm = self.rosto.landmark
            toques.append(((lm[13].x + lm[14].x) / 2 * w, (lm[13].y + lm[14].y) / 2 * h, int(26 * e)))
        self.jogo.atualizar(agora, dt, w, h, toques, self.part, self.sons)

    # desenho
    def mascara(self):
        try:
            if self.seg is None:
                self.seg = mp.solutions.selfie_segmentation.SelfieSegmentation(model_selection=1)
            m = self.seg.process(self.rgb).segmentation_mask
            if m is None:
                return None
            m = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 2)
            return np.clip(m, 0, 1)[..., None]
        except Exception:
            self.fundo_i = 0
            self.toast("Fundo indisponivel neste mediapipe", 3, VERMELHO)
            return None

    def desenhar_rosto(self, img, cor):
        r, w, h = self.rosto, self.w, self.h
        m = mp.solutions
        du, st = m.drawing_utils, m.drawing_styles
        if self.estilo == 1:
            du.draw_landmarks(img, r, m.face_mesh.FACEMESH_TESSELATION, None,
                              st.get_default_face_mesh_tesselation_style())
            du.draw_landmarks(img, r, m.face_mesh.FACEMESH_CONTOURS, None,
                              st.get_default_face_mesh_contours_style())
            du.draw_landmarks(img, r, m.face_mesh.FACEMESH_IRISES, None,
                              st.get_default_face_mesh_iris_connections_style())
        elif self.estilo == 2:
            spec = du.DrawingSpec(color=cor, thickness=2)
            du.draw_landmarks(img, r, m.face_mesh.FACEMESH_CONTOURS, None, spec)
            du.draw_landmarks(img, r, m.face_mesh.FACEMESH_IRISES, None, spec)
        else:
            for p in r.landmark:
                cv2.circle(img, (int(p.x * w), int(p.y * h)), 1, VERDE, -1)

    def desenhar(self, frame, agora):
        w, h, e = self.w, self.h, self.e
        c = self.cfg
        cor = self.cor_anim
        neon = self.estilo == 2

        # 1) base: filtro + fundo
        base = aplicar_filtro(frame, FILTROS[self.filtro_i])
        fundo = FUNDOS[self.fundo_i]
        if fundo == "AUTO":
            fundo = "PRETO" if neon else "CAMERA"
        if fundo == "CAMERA":
            saida = base.copy()
        elif fundo == "ESCURO":
            saida = cv2.convertScaleAbs(base, alpha=0.3)
        elif fundo == "PRETO":
            saida = np.zeros_like(frame)
        elif fundo == "BRANCO":
            saida = np.full_like(frame, 245)
        else:
            m = self.mascara()
            if m is None:
                saida = base.copy()
            else:
                bg = cv2.GaussianBlur(base, (0, 0), 14) if fundo == "DESFOCADO" else np.zeros_like(base)
                saida = (base * m + bg * (1 - m)).astype(np.uint8)

        # 2) tracos da pintura
        saida = self.quadro.componer(saida)

        # 3) esqueleto do rosto e das maos
        alvo = np.zeros_like(saida) if neon else saida
        if self.rosto is not None and c["rosto"]:
            self.desenhar_rosto(alvo, cor)
        if c["maos"]:
            for m in (self.mao_dir, self.mao_esq):
                if m is not None:
                    desenhar_mao(alvo, m, self.estilo, cor, w, h)

        # 4) bolinhas de cor nos dedos da mao da cor
        if self.mao_cor is not None:
            for i, nome in enumerate(DEDOS_ORDEM):
                cc = cor if COR_OPCOES[i][1] is None else COR_OPCOES[i][1]
                lm = self.mao_cor.landmark[PONTA_DEDO[nome]]
                pt = (int(lm.x * w), int(lm.y * h))
                cv2.circle(alvo, pt, int(10 * e), cc, -1, cv2.LINE_AA)
                if i == self.cor_idx:
                    cv2.circle(alvo, pt, int(15 * e), BRANCO, 2, cv2.LINE_AA)
            if self.modo_L:
                l = self.mao_cor.landmark
                mx, my = int((l[4].x + l[8].x) / 2 * w), int((l[4].y + l[8].y) / 2 * h)
                cv2.circle(alvo, (mx, my), max(2, int(self.tamanho / 2)), BRANCO, 2, cv2.LINE_AA)

        if neon:
            cv2.add(saida, alvo, dst=saida)
            pq = cv2.resize(alvo, (max(1, w // 4), max(1, h // 4)), interpolation=cv2.INTER_AREA)
            pq = cv2.GaussianBlur(pq, (0, 0), 3)
            luz = cv2.resize(pq, (w, h), interpolation=cv2.INTER_LINEAR)
            saida = cv2.add(saida, cv2.convertScaleAbs(luz, alpha=2.0))

        # 5) particulas e jogo
        self.part.desenhar(saida)
        self.jogo.desenhar(saida, agora, e)
        return saida

    # interface
    def desenhar_menu(self, saida, agora):
        g, e = self.g, self.e
        px0, py0, px1, py1 = g["painel"]
        rrect(saida, (px0, py0), (px1, py1), (28, 28, 28), int(14 * e), -1, 0.88)
        rrect(saida, (px0, py0), (px1, py1), (200, 200, 200), int(14 * e), 1)

        def prog(box, ident, dwell, raio):
            if self.hover_alvo == ident and not self.hover_ok:
                p = min(1.0, (agora - self.hover_inicio) / dwell)
                rrect(saida, (box[0], box[1]), (box[0] + int(p * (box[2] - box[0])), box[3]),
                      (0, 140, 0), raio, -1, 0.75)

        r10 = int(10 * e)
        for i, b in enumerate(g["abas"]):
            ativa = i == self.pagina
            rrect(saida, (b[0], b[1]), (b[2], b[3]), (95, 95, 95) if ativa else (50, 50, 50), r10, -1, 0.95)
            prog(b, "aba%d" % i, DWELL_ABA, r10)
            rrect(saida, (b[0], b[1]), (b[2], b[3]), BRANCO if ativa else (110, 110, 110), r10, 1)
            txt_centro(saida, ABAS[i], (b[0] + b[2]) / 2, (b[1] + b[3]) / 2, 0.55 * e,
                       BRANCO if ativa else CINZA, 1, borda=False)
        b = g["fechar"]
        rrect(saida, (b[0], b[1]), (b[2], b[3]), (40, 40, 140), r10, -1, 0.95)
        prog(b, "fechar", DWELL_ABA, r10)
        rrect(saida, (b[0], b[1]), (b[2], b[3]), (150, 150, 255), r10, 1)
        txt_centro(saida, "X", (b[0] + b[2]) / 2, (b[1] + b[3]) / 2, 0.7 * e, BRANCO, 2, borda=False)

        for i, (iid, rot, val, cv_) in enumerate(self.itens_pagina()):
            b = g["itens"][i]
            rrect(saida, (b[0], b[1]), (b[2], b[3]), (55, 55, 55), r10, -1, 0.9)
            prog(b, iid, DWELL_ITEM, r10)
            rrect(saida, (b[0], b[1]), (b[2], b[3]), (130, 130, 130), r10, 1)
            ty = int((b[1] + b[3]) / 2 + 6 * e)
            cv2.putText(saida, rot, (b[0] + int(14 * e), ty), FONTE, 0.58 * e, BRANCO, 1, cv2.LINE_AA)
            if val:
                tw, _ = tam_txt(val, 0.55 * e)
                cv2.putText(saida, val, (b[2] - tw - int(14 * e), ty), FONTE, 0.55 * e, cv_, 1, cv2.LINE_AA)

        d = g["dica"]
        dica = DICAS.get(self.hover_alvo or "", "Aponte o indicador em uma opcao e segure.")
        if self.hover_alvo and self.hover_alvo.startswith("aba"):
            dica = "Troca de pagina."
        cv2.putText(saida, dica, (d[0] + int(4 * e), int((d[1] + d[3]) / 2 + 5 * e)),
                    FONTE, 0.48 * e, (210, 210, 210), 1, cv2.LINE_AA)

    def interface(self, saida, agora):
        w, h, e = self.w, self.h, self.e
        c = self.cfg
        cor = self.cor_anim

        # textos
        if c["textos"]:
            sim = SIMETRIAS[self.sim_i][0]
            linha = "%s | %s | %dpx" % (ESTILOS[self.estilo], PINCEIS[self.pincel_i],
                                        int(round(self.tamanho)))
            if sim != "OFF":
                linha += " | SIM " + sim
            txt(saida, linha, (10, 24 * e), 0.55 * e, BRANCO, 1)
            txt(saida, "Pincel: %s   FPS %d" % (self.gesto, self.fps), (10, 46 * e), 0.5 * e, AMARELO, 1)
            txt(saida, "Cor: " + COR_OPCOES[self.cor_idx][0], (10, 68 * e), 0.5 * e, self.cor_traco, 1)
            txt(saida, "H ajuda  |  M menu", (w - 170 * e, h - 10 * e), 0.45 * e, CINZA, 1)
            for m, nome in ((self.mao_des, "PINCEL"), (self.mao_cor, "COR")):
                if m is not None:
                    wx, wy = int(m.landmark[0].x * w), int(m.landmark[0].y * h)
                    txt(saida, nome, (max(5, wx - 30), min(h - 8, wy + 28)), 0.5 * e, BRANCO, 1)

        # status da pintura
        if self.armada:
            if self.quadro.atual is not None:
                msg = "BORRACHA..." if self.apagando else "PINTANDO..."
            else:
                msg = "PINTURA LIGADA: levante so o indicador"
            txt(saida, msg, (10, (96 if c["textos"] else 30) * e), 0.6 * e, VERDE, 2)

        # gravando
        if self.grav.ativo:
            seg = int(agora - self.grav.t0)
            cv2.circle(saida, (int(w / 2 - 50 * e), int(20 * e)), int(7 * e), VERMELHO, -1, cv2.LINE_AA)
            txt(saida, "REC %02d:%02d" % (seg // 60, seg % 60), (w / 2 - 38 * e, 27 * e),
                0.6 * e, BRANCO, 2)

        # paleta (embaixo, a esquerda)
        if not self.menu_aberto:
            for i in range(len(COR_OPCOES)):
                cx, cy = int((28 + i * 44) * e), h - int(70 * e)
                cc = cor if COR_OPCOES[i][1] is None else COR_OPCOES[i][1]
                cv2.circle(saida, (cx, cy), int(12 * e), cc, -1, cv2.LINE_AA)
                if i == self.cor_idx:
                    cv2.circle(saida, (cx, cy), int(17 * e), BRANCO, 2, cv2.LINE_AA)
                txt(saida, SIGLAS[i], (cx - 12 * e, cy + 32 * e), 0.4 * e, CINZA, 1)

        # medidor de boca
        if c["boca"] and not self.menu_aberto:
            mt, mh = int(60 * e), int(150 * e)
            mx0, mx1 = w - int(40 * e), w - int(20 * e)
            nivel = int(min(self.boca / 0.6, 1.0) * mh)
            cv2.rectangle(saida, (mx0, mt), (mx1, mt + mh), (110, 110, 110), 1)
            cv2.rectangle(saida, (mx0, mt + mh - nivel), (mx1, mt + mh), cor, -1)
            txt(saida, "boca", (w - 55 * e, mt + mh + 20 * e), 0.5 * e, BRANCO, 1)
            if self.boca > 0.35:
                txt_centro(saida, "AAAAAH!", w / 2, h - 30 * e, 1.2 * e, cor, 3)

        # botao MENU
        b = self.g["btn"]
        r10 = int(10 * e)
        rrect(saida, (b[0], b[1]), (b[2], b[3]), (30, 30, 30), r10, -1, 0.85)
        if self.hover_alvo == "menu" and not self.hover_ok:
            p = min(1.0, (agora - self.hover_inicio) / DWELL_MENU)
            rrect(saida, (b[0], b[1]), (b[0] + int(p * (b[2] - b[0])), b[3]), (0, 200, 255), r10, -1, 0.9)
        rrect(saida, (b[0], b[1]), (b[2], b[3]), BRANCO, r10, 2)
        txt_centro(saida, "FECHAR" if self.menu_aberto else "MENU", (b[0] + b[2]) / 2,
                   (b[1] + b[3]) / 2, 0.6 * e, BRANCO, 2, borda=False)

        if self.menu_aberto:
            self.desenhar_menu(saida, agora)

        # cursor / pincel
        if self.armada and self.quadro.atual is not None and self.ponteiro is not None:
            raio = int((self.tamanho * 2.5 if self.apagando else self.tamanho) / 2) + 4
            cv2.circle(saida, (int(self.ponteiro[0]), int(self.ponteiro[1])), raio,
                       VERMELHO if self.apagando else BRANCO, 2, cv2.LINE_AA)
        elif self.cursor is not None:
            p = (int(self.cursor[0]), int(self.cursor[1]))
            cv2.circle(saida, p, int(9 * e), CIANO, 2, cv2.LINE_AA)
            cv2.circle(saida, p, 2, CIANO, -1, cv2.LINE_AA)

        # contagem da foto
        if self.foto_em is not None:
            n = int(math.ceil(self.foto_em - agora))
            txt_centro(saida, str(max(n, 1)), w / 2, h / 2, 6 * e, BRANCO, 10)

        # avisos
        self.avisos = [a for a in self.avisos if a[1] > agora]
        for k, (s, _, cc) in enumerate(reversed(self.avisos)):
            txt_centro(saida, s, w / 2, h - (26 + 28 * k) * e - (50 * e if self.boca > 0.35 else 0),
                       0.65 * e, cc, 2)

        # ajuda
        if agora < self.ajuda_ate:
            lh = int(24 * e)
            pw, ph = int(w * 0.84), lh * (len(AJUDA) + 2)
            x0, y0 = (w - pw) // 2, (h - ph) // 2
            rrect(saida, (x0, y0), (x0 + pw, y0 + ph), (20, 20, 20), int(14 * e), -1, 0.9)
            rrect(saida, (x0, y0), (x0 + pw, y0 + ph), BRANCO, int(14 * e), 1)
            for k, linha in enumerate(AJUDA):
                cv2.putText(saida, linha, (x0 + int(20 * e), y0 + lh * (k + 1) + int(8 * e)), FONTE,
                            0.62 * e if k == 0 else 0.46 * e, AMARELO if k == 0 or linha.isupper() else BRANCO,
                            1, cv2.LINE_AA)

    # teclado
    def tecla(self, k):
        if k in (ord("q"), ord("Q"), 27):
            return True
        if k in (ord("1"), ord("2"), ord("3")):
            self.estilo = int(chr(k))
        elif k in (ord("p"), ord("P")):
            if self.cfg["pintura"] and not self.menu_aberto and not self.jogo.ativo:
                self.armada, self.armada_desde, self.perdido = True, self.agora, None
        elif k in (ord("c"), ord("C")):
            self.acao("limpar")
        elif k in (ord("z"), ord("Z")):
            self.desfazer()
        elif k in (ord("y"), ord("Y")):
            self.refazer()
        elif k in (ord("s"), ord("S")):
            self.salvar_desenho()
        elif k in (ord("r"), ord("R")):
            self.alternar_gravacao()
        elif k in (ord("t"), ord("T")):
            self.acao("dominante")
        elif k in (ord("m"), ord("M")):
            self.menu_aberto = not self.menu_aberto
        elif k in (ord("h"), ord("H")):
            self.ajuda_ate = 0.0 if self.agora < self.ajuda_ate else self.agora + 30
        elif k == ord(" "):
            self.pedir_foto = True
        elif k in (ord("f"), ord("F")):
            self.tela_cheia = not self.tela_cheia
            cv2.setWindowProperty(JANELA, cv2.WND_PROP_FULLSCREEN,
                                  cv2.WINDOW_FULLSCREEN if self.tela_cheia else cv2.WINDOW_NORMAL)
        return False

    # loop
    def salvar_foto(self, img):
        os.makedirs(PASTA, exist_ok=True)
        nome = time.strftime("foto_%Y%m%d_%H%M%S.png")
        cv2.imwrite(os.path.join(PASTA, nome), img)
        self.flash = 6
        self.toast("Foto salva: " + nome, 2.5, VERDE)
        self.sons.tocar(1200, 90)

    def passo(self):
        frame = self.ler_frame()
        if frame is None:
            return None
        agora = time.time()
        dt = min(max(agora - self.agora, 1e-3), 0.1)
        self.agora = agora
        self.fps += (1.0 / dt - self.fps) * 0.1
        self.cor_anim = cor_arco_iris()

        self.detectar(frame)
        self.geometria()
        self.logica_rosto(agora)
        self.logica_maos(agora, dt)
        self.logica_jogo(agora, dt)
        self.part.atualizar(dt)

        saida = self.desenhar(frame, agora)

        if self.tirar_foto:
            self.salvar_foto(saida)
        if self.grav.ativo:
            self.grav.frame(saida, agora)
        if self.flash > 0:
            saida = cv2.addWeighted(saida, 1 - self.flash / 8, np.full_like(saida, 255),
                                    self.flash / 8, 0)
            self.flash -= 1

        self.interface(saida, agora)
        return saida

    def rodar(self):
        cv2.namedWindow(JANELA, cv2.WINDOW_NORMAL)
        self.toast("Segure o indicador em MENU (canto) | H = ajuda", 6)
        try:
            while True:
                saida = self.passo()
                if saida is None:
                    break
                cv2.imshow(JANELA, saida)
                k = cv2.waitKey(1) & 0xFF
                if self.tecla(k):
                    break
                try:
                    if cv2.getWindowProperty(JANELA, cv2.WND_PROP_VISIBLE) < 1:
                        break
                except cv2.error:
                    break
        finally:
            self.grav.parar()
            self.cap.release()
            cv2.destroyAllWindows()


# INICIO
def abrir_camera():
    candidatos = []
    for idx in dict.fromkeys([CAMERA_INDEX, 0, 1, 2]):
        candidatos.append((idx, None))
        if os.name == "nt":
            candidatos.append((idx, cv2.CAP_DSHOW))
    for idx, be in candidatos:
        cap = cv2.VideoCapture(idx) if be is None else cv2.VideoCapture(idx, be)
        if cap.isOpened():
            if RESOLUCAO:
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, RESOLUCAO[0])
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, RESOLUCAO[1])
            ok, _ = cap.read()
            if ok:
                return cap
        cap.release()
    return None


def main():
    if not hasattr(mp, "solutions"):
        print("Seu mediapipe e novo demais. Rode no terminal:")
        print("    python -m pip install mediapipe==0.10.14")
        return
    cap = abrir_camera()
    if cap is None:
        print("Nao consegui abrir a camera. Feche outros programas que usam a camera")
        print("(Zoom, Teams, navegador...) ou mude CAMERA_INDEX no topo do arquivo.")
        return
    m = mp.solutions
    with m.face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True,
                              min_detection_confidence=0.5,
                              min_tracking_confidence=0.5) as fm, \
         m.hands.Hands(max_num_hands=2, min_detection_confidence=0.6,
                       min_tracking_confidence=0.5) as hd:
        App(cap, fm, hd).rodar()


if __name__ == "__main__":
    main()