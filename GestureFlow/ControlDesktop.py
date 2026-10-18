import sys
import time
import math
import ctypes
from collections import deque

import cv2
import numpy as np
import tkinter as tk
import mediapipe as mp
from pynput import mouse, keyboard

# CONFIGURACOES 
CAMERA_INDEX = 0
RESOLUCAO = (960, 540)
PREVIA_TAMANHO = (480, 270)     

MODO_MAO = "destro"   


AREA = (0.15, 0.10, 0.85, 0.70)

PINCA_ON = 0.28                   
PINCA_OFF = 0.40                     
CURSOR_PONTO = 5          
                               
LOOKBACK = 0.08                    
TEMPO_ARRASTE = 0.45          
TEMPO_PUNHO = 1.2                  
TEMPO_CLIQUE_DIREITO = 0.6  

ROLAR_ANGULO = 0.5                  
ROLAR_VEL_MIN = 3.0               
ROLAR_VEL_MAX = 15.0                 

ALFA_MIN = 0.12             
ALFA_MAX = 0.85
ZONA_MORTA = 3                      
VEL_REF = 120                        

REPETE_ATRASO = 0.6                  
REPETE_INTERVALO = 0.08

LINHAS = [
    (0.0, [(c, 1.0) for c in "1234567890"] + [("Apagar", 1.8)]),
    (0.5, [(c, 1.0) for c in "qwertyuiop"] + [("Tab", 1.3)]),
    (0.8, [(c, 1.0) for c in "asdfghjklç"] + [("Enter", 1.0)]),
    (0.0, [("Shift", 1.8)] + [(c, 1.0) for c in "zxcvbnm"] + [(",", 1.0), (".", 1.0), ("?", 1.0)]),
    (0.0, [("Esc", 1.6), ("Espaço", 5.4), ("←", 1.2), ("↑", 1.2), ("↓", 1.2), ("→", 1.2)]),
]
REPETIVEIS = ("Apagar", "←", "→", "↑", "↓")


# utilidades 
def ativar_dpi():
    """No Windows, evita que a escala da tela (125%, 150%) desalinhe o cursor."""
    if sys.platform != "win32":
        return
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


def dist(a, b):
    return float(math.hypot(a[0] - b[0], a[1] - b[1]))


def limitar(v, lo, hi):
    return max(lo, min(hi, v))


def para_tela(nx, ny, W, H):
    """Converte posicao normalizada da imagem em pixel da tela, via AREA."""
    x0, y0, x1, y1 = AREA
    u = limitar((nx - x0) / (x1 - x0), 0.0, 1.0)
    v = limitar((ny - y0) / (y1 - y0), 0.0, 1.0)
    return u * (W - 1), v * (H - 1)


class Suavizador:
    """Media exponencial: suave quando a mao esta devagar, rapida quando se move."""

    def __init__(self):
        self.p = None

    def atualizar(self, x, y):
        if self.p is None:
            self.p = (x, y)
            return self.p
        px, py = self.p
        d = math.hypot(x - px, y - py)
        if d < ZONA_MORTA:
            return self.p
        a = ALFA_MIN + (ALFA_MAX - ALFA_MIN) * min(d / VEL_REF, 1.0)
        self.p = (px + (x - px) * a, py + (y - py) * a)
        return self.p


def direcao_vertical(pts):
    """Para onde indicador+mindinho apontam na imagem: -1 = cima, +1 = baixo, 0 = de lado."""
    vx = (pts[8][0] - pts[5][0]) + (pts[20][0] - pts[17][0])
    vy = (pts[8][1] - pts[5][1]) + (pts[20][1] - pts[17][1])
    n = math.hypot(vx, vy)
    return vy / n if n > 1e-6 else 0.0


def analisar(pts):
    """pts: 21 pontos da mao em pixels. Retorna gesto e medidas da pinca."""
    palma = max(dist(pts[0], pts[9]), 1e-6)
    ext = [dist(pts[t], pts[0]) > dist(pts[j], pts[0]) * 1.15
           for t, j in zip((8, 12, 16, 20), (6, 10, 14, 18))]
    ind, med, ane, mim = ext
    n = sum(ext)
    if ind and not med and not ane and not mim:
        gesto = "APONTAR"
    elif ind and mim and not med and not ane:
        gesto = "ROLAR"
    elif n == 4:
        gesto = "PAUSA"
    elif n == 0:
        gesto = "PUNHO"
    else:
        gesto = "OUTRO"
    return {
        "gesto": gesto,
        "vy": direcao_vertical(pts) if gesto == "ROLAR" else 0.0,
        "r_ind": dist(pts[4], pts[8]) / palma,
        "r_med": dist(pts[4], pts[12]) / palma,
        "ind_ok": dist(pts[8], pts[0]) / palma > 1.3,
        "med_ok": dist(pts[12], pts[0]) / palma > 1.3,
    }


# teclado virtual
def montar_layout(W, H):
    """Calcula posicao do teclado na tela e o retangulo de cada tecla."""
    ow = int(W * 0.58)
    pad = 12
    u = (ow - 2 * pad) / 11.8
    kh = u * 0.8
    gap = max(4, int(u * 0.06))
    oh = int(2 * pad + 5 * kh)
    ox = (W - ow) // 2
    oy = H - oh - 70                     
    teclas = []
    for r, (off, keys) in enumerate(LINHAS):
        x = off
        for rot, w in keys:
            teclas.append({
                "rot": rot,
                "x0": pad + x * u + gap / 2, "y0": pad + r * kh + gap / 2,
                "x1": pad + (x + w) * u - gap / 2, "y1": pad + (r + 1) * kh - gap / 2,
            })
            x += w
    return ox, oy, ow, oh, int(kh), teclas


class Teclado:
    """Teclado desenhado por cima da area de trabalho (nao rouba o foco no Windows)."""

    def __init__(self, root, W, H):
        self.root = root
        self.visivel = False
        self.shift = False
        self.kb = keyboard.Controller()
        self.especiais = {
            "Apagar": keyboard.Key.backspace, "Tab": keyboard.Key.tab,
            "Enter": keyboard.Key.enter, "Esc": keyboard.Key.esc,
            "Espaço": keyboard.Key.space, "←": keyboard.Key.left,
            "→": keyboard.Key.right, "↑": keyboard.Key.up, "↓": keyboard.Key.down,
        }
        self.ox, self.oy, self.ow, self.oh, kh, self.teclas = montar_layout(W, H)
        self.hover_idx = None
        self.flash = {}

        root.overrideredirect(True)
        root.attributes("-topmost", True)
        try:
            root.attributes("-alpha", 0.9)
        except tk.TclError:
            pass
        root.geometry("%dx%d+%d+%d" % (self.ow, self.oh, self.ox, self.oy))
        self.canvas = tk.Canvas(root, width=self.ow, height=self.oh,
                                bg="#0d1017", highlightthickness=0)
        self.canvas.pack()
        fonte = ("Segoe UI" if sys.platform == "win32" else "Arial", max(10, int(kh * 0.28)), "bold")
        for t in self.teclas:
            t["ret"] = self.canvas.create_rectangle(t["x0"], t["y0"], t["x1"], t["y1"],
                                                    fill=self._cor_base(t), outline="")
            t["txt"] = self.canvas.create_text((t["x0"] + t["x1"]) / 2, (t["y0"] + t["y1"]) / 2,
                                               text=t["rot"], fill="white", font=fonte)
        self._sem_foco()
        root.withdraw()

    def _sem_foco(self):
        """Janela que nao ativa (nao tira o foco do app onde voce digita)."""
        if sys.platform != "win32":
            return
        try:
            self.root.update_idletasks()
            user32 = ctypes.windll.user32
            hwnd = user32.GetParent(self.root.winfo_id()) or self.root.winfo_id()
            estilo = user32.GetWindowLongW(hwnd, -20)
            # NOACTIVATE | TOOLWINDOW | TRANSPARENT (cliques reais atravessam)
            user32.SetWindowLongW(hwnd, -20, estilo | 0x08000000 | 0x00000080 | 0x00000020)
        except Exception:
            pass

    @staticmethod
    def _cor_base(t):
        return "#2a3045" if len(t["rot"]) > 1 else "#1b2030"

    def _cor(self, i):
        t = self.teclas[i]
        if self.flash.get(i, 0) > time.time():
            return "#27c28b"
        if i == self.hover_idx:
            return "#2f6fed"
        if t["rot"] == "Shift" and self.shift:
            return "#d4a017"
        return self._cor_base(t)

    def _pintar(self, i):
        self.canvas.itemconfig(self.teclas[i]["ret"], fill=self._cor(i))

    def alternar(self):
        self.visivel = not self.visivel
        if self.visivel:
            self.root.deiconify()
        else:
            self.root.withdraw()
            self.hover_idx = None

    def sobre(self, sx, sy):
        return (self.ox <= sx < self.ox + self.ow) and (self.oy <= sy < self.oy + self.oh)

    def tecla_em(self, sx, sy):
        rx, ry = sx - self.ox, sy - self.oy
        for i, t in enumerate(self.teclas):
            if t["x0"] <= rx <= t["x1"] and t["y0"] <= ry <= t["y1"]:
                return i
        return None

    def hover(self, pos):
        idx = self.tecla_em(*pos) if self.visivel else None
        if idx != self.hover_idx:
            antigo, self.hover_idx = self.hover_idx, idx
            if antigo is not None:
                self._pintar(antigo)
            if idx is not None:
                self._pintar(idx)

    def repete(self, idx):
        return self.teclas[idx]["rot"] in REPETIVEIS

    def _rotulos(self):
        for t in self.teclas:
            if len(t["rot"]) == 1:
                txt = t["rot"].upper() if self.shift else t["rot"]
                self.canvas.itemconfig(t["txt"], text=txt)

    def apertar(self, idx):
        rot = self.teclas[idx]["rot"]
        self.flash[idx] = time.time() + 0.15
        self._pintar(idx)
        if rot == "Shift":
            self.shift = not self.shift
            self._rotulos()
            for i, t in enumerate(self.teclas):
                if t["rot"] == "Shift":
                    self._pintar(i)
            return
        if rot in self.especiais:
            k = self.especiais[rot]
            self.kb.press(k)
            self.kb.release(k)
        else:
            self.kb.type(rot.upper() if self.shift else rot)
        if self.shift:                    
            self.shift = False
            self._rotulos()
            for i, t in enumerate(self.teclas):
                if t["rot"] == "Shift":
                    self._pintar(i)

    def refrescar(self):
        agora = time.time()
        for i in [i for i, ate in self.flash.items() if ate <= agora]:
            del self.flash[i]
            self._pintar(i)
        try:
            self.root.update()
        except tk.TclError:
            pass


# logica de mouse/gestos
class Estado:
    def __init__(self):
        self.sair = False
        self.pausado = False
        self.alternar = False
        self.trocar = False
        self.canhoto = (MODO_MAO == "canhoto")


class Controle:
    def __init__(self, W, H, mouse_ctl, teclado, estado):
        self.W, self.H = W, H
        self.m = mouse_ctl
        self.tec = teclado
        self.estado = estado
        self.suav = Suavizador()
        self.hist = deque(maxlen=90)
        self.pos = tuple(self.m.position)
        self.status = ""
        self.prog_punho = 0.0
        self.t_visto = None
        self.t_dir = 0.0
        self.resetar()

    def resetar(self):
        self.pinca = False
        self.cont_on = 0
        self.cont_off = 0
        self.arrastando = False
        self.consumido = False
        self.tecla_rep = None
        self.t_rep = 0.0
        self.t_pinca = 0.0
        self.bloq = self.pos
        self.ref5 = (0, 0)
        self.med = False
        self.rolando = False
        self.t_rolar = 0.0
        self.acum = 0.0
        self.t_punho = None
        self.punho_usado = False
        self.prog_punho = 0.0

    def soltar_tudo(self):
        if self.arrastando:
            self.m.release(mouse.Button.left)
        self.resetar()
        self.suav.p = self.pos

    def perdeu(self, agora):
        """Chamado quando a camera nao ve a mao."""
        self.status = "SEM MAO"
        if self.t_visto is not None and agora - self.t_visto > 0.4:
            self.soltar_tudo()
            self.t_visto = None

    def _pos_antes(self, t_limite):
        achou = None
        for t, x, y in reversed(self.hist):
            achou = (x, y)
            if t <= t_limite:
                break
        return achou

    def _mover_cursor(self, x, y):
        x = limitar(x, 0, self.W - 1)
        y = limitar(y, 0, self.H - 1)
        self.pos = (x, y)
        self.m.position = (int(x), int(y))

    def _inicia_pinca(self, pc, agora):
        self.pinca = True
        self.t_pinca = agora
        self.arrastando = False
        self.consumido = False
        self.tecla_rep = None
        alvo = self._pos_antes(agora - LOOKBACK)
        if alvo:
            self._mover_cursor(*alvo)
        self.bloq = self.pos
        self.ref5 = para_tela(pc[0], pc[1], self.W, self.H)
        if self.tec.visivel and self.tec.sobre(*self.pos):
            self.consumido = True                  
            idx = self.tec.tecla_em(*self.pos)
            if idx is not None:
                self.tec.apertar(idx)
                self.tecla_rep = idx
                self.t_rep = agora + REPETE_ATRASO

    def _termina_pinca(self):
        if self.arrastando:
            self.m.release(mouse.Button.left)
        elif not self.consumido:
            self.m.click(mouse.Button.left, 1)
        self.pinca = False
        self.arrastando = False
        self.consumido = False
        self.tecla_rep = None
        self.suav.p = self.pos
        self.hist.clear()

    def _punho(self, gesto, agora):
        if gesto == "PUNHO" and not self.pinca:
            if self.t_punho is None:
                self.t_punho = agora
            self.prog_punho = limitar((agora - self.t_punho) / TEMPO_PUNHO, 0.0, 1.0)
            if self.prog_punho >= 1.0 and not self.punho_usado:
                self.punho_usado = True
                self.tec.alternar()
        else:
            self.t_punho = None
            self.prog_punho = 0.0
            self.punho_usado = False

    def atualizar(self, a, pc, agora):
        """a: analise da mao; pc: ponto estavel que guia o cursor (0 a 1)."""
        self.t_visto = agora
        if self.estado.pausado:
            self.soltar_tudo()
            self.status = "PAUSADO (F9)"
            return
        gesto = a["gesto"]
        self._punho(gesto, agora)

        # --- pinca do indicador (clique / arrastar / tecla) 
        limite = PINCA_OFF if self.pinca else PINCA_ON
        bruto = (a["ind_ok"] and a["r_ind"] < limite
                 and (self.pinca or gesto != "ROLAR"))  
        if bruto:
            self.cont_on += 1
            self.cont_off = 0
        else:
            self.cont_off += 1
            self.cont_on = 0
        if not self.pinca and self.cont_on >= 2:
            self._inicia_pinca(pc, agora)
        elif self.pinca and self.cont_off >= 2:
            self._termina_pinca()

        # --- clique direito (polegar + medio) ---
        lim_med = PINCA_OFF if self.med else PINCA_ON
        med_bruto = ((not self.pinca) and gesto != "ROLAR"
                     and a["med_ok"] and a["r_med"] < lim_med)
        if med_bruto and not self.med and agora - self.t_dir > TEMPO_CLIQUE_DIREITO:
            self.t_dir = agora
            if not (self.tec.visivel and self.tec.sobre(*self.pos)):
                self.m.click(mouse.Button.right, 1)
        self.med = med_bruto

        if self.pinca:
            if self.consumido:
                self.status = "TECLA"
                if (self.tecla_rep is not None and agora >= self.t_rep
                        and self.tec.repete(self.tecla_rep)):
                    self.tec.apertar(self.tecla_rep)
                    self.t_rep = agora + REPETE_INTERVALO
            else:
                if not self.arrastando and agora - self.t_pinca >= TEMPO_ARRASTE:
                    self.m.press(mouse.Button.left)
                    self.arrastando = True
                if self.arrastando:
                    r = para_tela(pc[0], pc[1], self.W, self.H)
                    self._mover_cursor(self.bloq[0] + r[0] - self.ref5[0],
                                       self.bloq[1] + r[1] - self.ref5[1])
                    self.status = "ARRASTANDO"
                else:
                    self.status = "PINCA (clique ao soltar)"
        else:
            congelar = self.cont_on > 0 or self.med
            if gesto == "APONTAR" and not congelar:
                sx, sy = self.suav.atualizar(*para_tela(pc[0], pc[1], self.W, self.H))
                self._mover_cursor(sx, sy)
                self.hist.append((agora, sx, sy))
                self.status = "MOVENDO"
            elif gesto == "APONTAR":
                self.status = "PRE-PINCA"
            elif gesto == "ROLAR":
                sinal = self._rolar(a["vy"], agora)
                self.status = {-1: "ROLANDO: CIMA", 1: "ROLANDO: BAIXO",
                               0: "ROLAR: incline os dedos p/ cima ou baixo"}[sinal]
            elif gesto == "PAUSA":
                self.status = "MAO ABERTA (pausa)"
            elif gesto == "PUNHO":
                self.status = "PUNHO: segure p/ teclado"
            else:
                self.status = "..."
        if gesto != "ROLAR" or self.pinca:
            self.rolando = False
            self.acum = 0.0
        if self.tec.visivel:
            self.tec.hover(self.pos)

    def _rolar(self, vy, agora):
        """vy: -1 (dedos p/ cima) a +1 (dedos p/ baixo). Rola continuamente enquanto durar o gesto.
        Retorna -1 (subindo), 1 (descendo) ou 0 (zona morta)."""
        dt = min(agora - self.t_rolar, 0.1) if self.rolando else 0.0
        self.t_rolar = agora
        self.rolando = True
        if abs(vy) < ROLAR_ANGULO:
            self.acum = 0.0
            return 0
        forca = (abs(vy) - ROLAR_ANGULO) / (1.0 - ROLAR_ANGULO)     
        vel = ROLAR_VEL_MIN + (ROLAR_VEL_MAX - ROLAR_VEL_MIN) * forca  
        sinal = -1 if vy < 0 else 1
        self.acum += -sinal * vel * dt                               
        passos = int(self.acum)
        if passos:
            self.acum -= passos
            self.m.scroll(0, limitar(passos, -6, 6))
        return sinal


# interface 
def atalhos_globais(estado):
    def ao_apertar(tecla):
        try:
            if tecla == keyboard.Key.f12:
                estado.sair = True
            elif tecla == keyboard.Key.f9:
                estado.pausado = not estado.pausado
            elif tecla == keyboard.Key.f8:
                estado.trocar = True
            elif tecla == keyboard.Key.f10:
                estado.alternar = True
        except Exception:
            pass

    ouvinte = keyboard.Listener(on_press=ao_apertar)
    ouvinte.daemon = True
    ouvinte.start()
    return ouvinte


def escolher_mao(res, canhoto):
    """Separa a mao do modo escolhido das demais. Retorna (mao_alvo ou None, lista_de_outras).
    A imagem ja chega espelhada (cv2.flip), entao o rotulo do MediaPipe bate com a mao real da pessoa."""
    if not res.multi_hand_landmarks:
        return None, []
    alvo = "Left" if canhoto else "Right"
    escolhida, outras = None, []
    for lm, h in zip(res.multi_hand_landmarks, res.multi_handedness):
        c = h.classification[0]
        if c.label == alvo and (escolhida is None or c.score > escolhida[1]):
            if escolhida is not None:
                outras.append(escolhida[0])
            escolhida = (lm, c.score)
        else:
            outras.append(lm)
    return (escolhida[0] if escolhida else None), outras


def texto(img, s, org, cor=(255, 255, 255), esc=0.5):
    cv2.putText(img, s, org, cv2.FONT_HERSHEY_SIMPLEX, esc, (0, 0, 0), 3, cv2.LINE_AA)
    cv2.putText(img, s, org, cv2.FONT_HERSHEY_SIMPLEX, esc, cor, 1, cv2.LINE_AA)


def desenhar(frame, hand, outras, pts, a, ctrl, estado, tec, fps, mp_draw, mp_hands):
    h, w = frame.shape[:2]
    x0, y0, x1, y1 = AREA
    cv2.rectangle(frame, (int(x0 * w), int(y0 * h)), (int(x1 * w), int(y1 * h)), (255, 200, 0), 1)
    texto(frame, "area de controle", (int(x0 * w) + 4, int(y0 * h) - 6), (255, 200, 0), 0.4)
    cor_st = (80, 80, 255) if estado.pausado else (80, 220, 80)
    for o in outras:                            
        mp_draw.draw_landmarks(
            frame, o, mp_hands.HAND_CONNECTIONS,
            mp_draw.DrawingSpec(color=(70, 70, 70), thickness=1, circle_radius=1),
            mp_draw.DrawingSpec(color=(50, 50, 50), thickness=1))
    if hand is not None:
        mp_draw.draw_landmarks(
            frame, hand, mp_hands.HAND_CONNECTIONS,
            mp_draw.DrawingSpec(color=(255, 255, 255), thickness=1, circle_radius=1),
            mp_draw.DrawingSpec(color=(170, 170, 170), thickness=1))
        pi = (int(pts[8][0]), int(pts[8][1]))
        pt = (int(pts[4][0]), int(pts[4][1]))
        cor = (0, 255, 255) if ctrl.pinca else (0, 220, 0)
        if ctrl.arrastando:
            cor = (0, 0, 255)
        cv2.line(frame, pt, pi, cor, 2)
        pc = (int(pts[CURSOR_PONTO][0]), int(pts[CURSOR_PONTO][1]))
        cv2.circle(frame, pi, 4, cor, -1)
        cv2.circle(frame, pc, 9, cor, -1)          
        if ctrl.prog_punho > 0:
            c = (int(pts[9][0]), int(pts[9][1]))
            cv2.ellipse(frame, c, (45, 45), 0, -90, -90 + 360 * ctrl.prog_punho, (255, 0, 255), 4)
    texto(frame, ctrl.status, (10, 24), cor_st, 0.6)
    texto(frame, "Teclado: %s | FPS %d" % ("ON" if tec.visivel else "OFF", fps), (10, 48), (255, 255, 255), 0.45)
    texto(frame, "Modo: %s (so mao %s)" % (("CANHOTO", "ESQUERDA") if estado.canhoto else ("DESTRO", "DIREITA")),
          (10, 70), (0, 200, 255), 0.45)
    texto(frame, "F8 troca mao  F9 pausa  F10 teclado  F12 sair", (10, h - 10), (200, 200, 200), 0.45)


def abrir_camera():
    cap = None
    if sys.platform == "win32":
        cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)
    if cap is None or not cap.isOpened():
        cap = cv2.VideoCapture(CAMERA_INDEX)
    if RESOLUCAO:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, RESOLUCAO[0])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, RESOLUCAO[1])
    return cap


def main():
    if not hasattr(mp, "solutions"):
        print("Seu mediapipe e novo demais. Rode: python -m pip install mediapipe==0.10.14")
        return
    ativar_dpi()
    root = tk.Tk()
    root.withdraw()
    W, H = root.winfo_screenwidth(), root.winfo_screenheight()

    cap = abrir_camera()
    if not cap.isOpened():
        print("Nao consegui abrir a camera. Feche outros programas que usam a camera.")
        root.destroy()
        return

    estado = Estado()
    tec = Teclado(root, W, H)
    ctrl = Controle(W, H, mouse.Controller(), tec, estado)
    atalhos_globais(estado)

    mp_hands = mp.solutions.hands
    mp_draw = mp.solutions.drawing_utils
    hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, model_complexity=0,
                           min_detection_confidence=0.6, min_tracking_confidence=0.6)

    janela = "Controle Desktop"
    cv2.namedWindow(janela, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(janela, *PREVIA_TAMANHO)
    cv2.moveWindow(janela, max(0, W - PREVIA_TAMANHO[0] - 20), 20)
    try:
        cv2.setWindowProperty(janela, cv2.WND_PROP_TOPMOST, 1)
    except Exception:
        pass

    print("Controle Desktop ligado. F8 = trocar mao | F9 = pausa | F10 = teclado | F12 ou Q/Esc = sair")
    fps, t_ant = 0.0, time.time()
    try:
        while not estado.sair:
            ok, frame = cap.read()
            if not ok:
                break
            frame = cv2.flip(frame, 1)
            h, w = frame.shape[:2]
            res = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            agora = time.time()
            fps = 0.9 * fps + 0.1 / max(agora - t_ant, 1e-6)
            t_ant = agora

            if estado.alternar:
                estado.alternar = False
                tec.alternar()
            if estado.trocar:
                estado.trocar = False
                estado.canhoto = not estado.canhoto
                ctrl.soltar_tudo()                   

            pts, a = None, None
            hand, outras = escolher_mao(res, estado.canhoto)
            if hand is not None:
                lm = hand.landmark
                pts = [(p.x * w, p.y * h) for p in lm]
                a = analisar(pts)
                ctrl.atualizar(a, (lm[CURSOR_PONTO].x, lm[CURSOR_PONTO].y), agora)
            else:
                ctrl.perdeu(agora)
                ctrl.status = "SEM MAO %s" % ("ESQUERDA" if estado.canhoto else "DIREITA")

            desenhar(frame, hand, outras, pts, a, ctrl, estado, tec, fps, mp_draw, mp_hands)
            cv2.imshow(janela, frame)
            tec.refrescar()
            tecla = cv2.waitKey(1) & 0xFF
            if tecla in (ord("m"), ord("M")):
                estado.trocar = True
            elif tecla in (27, ord("q"), ord("Q")):
                break
    finally:
        ctrl.soltar_tudo()
        hands.close()
        cap.release()
        cv2.destroyAllWindows()
        try:
            root.destroy()
        except Exception:
            pass


if __name__ == "__main__":
    main()
