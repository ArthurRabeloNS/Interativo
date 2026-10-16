import os
import time
import cv2
import numpy as np
import mediapipe as mp

mp_face = mp.solutions.face_mesh
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
mp_styles = mp.solutions.drawing_styles

PASTA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fotos")
os.makedirs(PASTA, exist_ok=True)

FONTE = cv2.FONT_HERSHEY_SIMPLEX
NOMES_MODOS = {1: "MALHA", 2: "NEON", 3: "PONTOS"}

# Dedos 
PONTAS = {"indicador": 8, "medio": 12, "anelar": 16, "mindinho": 20}
JUNTAS = {"indicador": 6, "medio": 10, "anelar": 14, "mindinho": 18}

# A MAO DA COR
DEDOS_ORDEM = ["polegar", "indicador", "medio", "anelar", "mindinho"]
PONTA_DEDO = {"polegar": 4, "indicador": 8, "medio": 12, "anelar": 16, "mindinho": 20}
SIGLAS = ["pol", "ind", "med", "ane", "min"]
COR_OPCOES = [                   # mesma ordem de DEDOS_ORDEM
    ("AMARELO", (0, 255, 255)),  # polegar
    ("VERMELHO", (0, 0, 255)),   # indicador
    ("VERDE", (0, 255, 0)),      # medio
    ("AZUL", (255, 120, 0)),     # anelar
    ("ARCO-IRIS", None),         # mindinho (None = cor animada RGB)
]
ESPESSURAS = [3, 6, 10, 16]

# Tempo (segundos) segurando o dedo em cima de um botao
DWELL_MENU = 2.0 
DWELL_ITEM = 1.3 
LINHAS = 6        


# ---------------------------------------------------------------- funcoes
def dist(a, b):
    return np.hypot(a.x - b.x, a.y - b.y)


def dedos_esticados(mao):
    """4 dedos (sem polegar): True se a ponta esta mais longe do pulso que a junta."""
    pulso = mao.landmark[0]
    return {
        d: dist(mao.landmark[PONTAS[d]], pulso) > dist(mao.landmark[JUNTAS[d]], pulso)
        for d in PONTAS
    }


def polegar_esticado(mao):
    """Polegar esticado: ponta mais longe da base do mindinho que a junta dele."""
    l = mao.landmark
    return dist(l[4], l[17]) > dist(l[3], l[17]) * 1.1


def dedo_unico(mao):
    """Se so UM dedo (polegar incluso) estiver esticado, devolve o nome dele."""
    d = dedos_esticados(mao)
    d["polegar"] = polegar_esticado(mao)
    ativos = [n for n, v in d.items() if v]
    return ativos[0] if len(ativos) == 1 else None


def mao_fechada(mao):
    return not any(dedos_esticados(mao).values())


def gesto_paz(mao):
    d = dedos_esticados(mao)
    return d["indicador"] and d["medio"] and not d["anelar"] and not d["mindinho"]


def um_dedo(mao):
    """So o indicador esticado (apontando); o polegar e ignorado."""
    d = dedos_esticados(mao)
    return d["indicador"] and not d["medio"] and not d["anelar"] and not d["mindinho"]


def abertura_boca(rosto):
    l = rosto.landmark
    return dist(l[13], l[14]) / dist(l[78], l[308])


def cor_arco_iris():
    h = int((time.time() * 60) % 180)
    bgr = cv2.cvtColor(np.uint8([[[h, 255, 255]]]), cv2.COLOR_HSV2BGR)[0][0]
    return tuple(int(c) for c in bgr)


def separar_maos(res):
    """Devolve (mao_direita, mao_esquerda) DO USUARIO. A imagem esta espelhada."""
    maos = res.multi_hand_landmarks
    if not maos:
        return None, None
    if len(maos) >= 2:
        # duas maos: a que esta mais a direita na tela e a direita do usuario
        esq, dir_ = sorted(maos[:2], key=lambda m: m.landmark[0].x)
        return dir_, esq
    # uma mao so: usa o rotulo do MediaPipe
    rotulo = res.multi_handedness[0].classification[0].label
    return (maos[0], None) if rotulo == "Right" else (None, maos[0])


def desenhar_mao(img, mao, modo, cor, w, h):
    if modo == 1:
        mp_draw.draw_landmarks(
            img, mao, mp_hands.HAND_CONNECTIONS,
            mp_styles.get_default_hand_landmarks_style(),
            mp_styles.get_default_hand_connections_style())
    elif modo == 2:
        mp_draw.draw_landmarks(
            img, mao, mp_hands.HAND_CONNECTIONS,
            mp_draw.DrawingSpec(color=cor, thickness=3, circle_radius=3),
            mp_draw.DrawingSpec(color=cor, thickness=3))
    elif modo == 3:
        for p in mao.landmark:
            cv2.circle(img, (int(p.x * w), int(p.y * h)), 3, (0, 255, 255), -1)


def lig(ligado):
    return ("LIGADO", (0, 255, 0)) if ligado else ("DESLIGADO", (0, 0, 255))


def montar_itens(modo, cor_idx, esp_idx, cfg, cor_traco, dominante):
    """Cada item: (id, texto, valor, cor_do_valor, repete_ao_segurar).
    Os 6 primeiros ficam na coluna da esquerda, os 6 ultimos na da direita."""
    branco = (255, 255, 255)
    return [
        ("dominante", "Voce e", dominante.upper(), branco, False),
        ("modo", "Modo visual", NOMES_MODOS[modo], branco, True),
        ("cor", "Cor do traco", COR_OPCOES[cor_idx][0], cor_traco, True),
        ("esp", "Espessura", str(ESPESSURAS[esp_idx]), branco, True),
        ("limpar", "Limpar desenho", "", branco, False),
        ("fechar", "Fechar menu", "", branco, False),
        ("foto", "Foto (punho)", *lig(cfg["foto"]), False),
        ("pintura", "Pintura (V)", *lig(cfg["pintura"]), False),
        ("rosto", "Mostrar rosto", *lig(cfg["rosto"]), False),
        ("mao", "Mostrar maos", *lig(cfg["mao"]), False),
        ("boca", "Medidor de boca", *lig(cfg["boca"]), False),
        ("textos", "Textos na tela", *lig(cfg["textos"]), False),
    ]


# ---------------------------------------------------------------- estado
cap = cv2.VideoCapture(0)  
modo = 1
mao_estava_aberta = False
ultima_foto = 0
ultima_troca = 0
flash = 0
aviso = ""

# Maos
dominante = "destro"     
cor_cand = None   
cor_cont = 0            

# Pintura
pintura_armada = False   
tracos = []
traco_atual = None
ponta_suave = None
cor_idx = 4              
esp_idx = 1

# Menu
cfg = {"foto": True, "pintura": True, "rosto": True,
       "mao": True, "boca": True, "textos": True}
menu_aberto = False
hover_alvo = None
hover_inicio = 0
hover_ok = False
ponteiro = None

with mp_face.FaceMesh(max_num_faces=1, refine_landmarks=True,
                      min_detection_confidence=0.5,
                      min_tracking_confidence=0.5) as face_mesh, \
     mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.6,
                    min_tracking_confidence=0.5) as hands:

    while cap.isOpened():
        ok, frame = cap.read()
        if not ok:
            break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res_rosto = face_mesh.process(rgb)
        res_mao = hands.process(rgb)
        h, w = frame.shape[:2]
        e = h / 480.0                      
        agora = time.time()
        cor = cor_arco_iris()

        # ---------- QUAL MAO É QUAL 
        mao_dir, mao_esq = separar_maos(res_mao)
        if dominante == "destro":
            mao_des, mao_cor = mao_dir, mao_esq   
        else:
            mao_des, mao_cor = mao_esq, mao_dir   

        # ---------- COR:
        dedo = dedo_unico(mao_cor) if mao_cor is not None else None
        if dedo is not None and dedo == cor_cand:
            cor_cont += 1
        else:
            cor_cand = dedo
            cor_cont = 1 if dedo is not None else 0
        if cor_cand is not None and cor_cont >= 5:   
            cor_idx = DEDOS_ORDEM.index(cor_cand)

        cor_traco = cor if COR_OPCOES[cor_idx][1] is None else COR_OPCOES[cor_idx][1]

        # ---------- GEOMETRIA DO MENU 
        bx0, by0 = w - int(120 * e), int(10 * e)       # botao MENU
        bx1, by1 = w - int(10 * e), int(48 * e)
        itens = montar_itens(modo, cor_idx, esp_idx, cfg, cor_traco, dominante)
        pw = int(w * 0.88)
        px0 = (w - pw) // 2
        px1 = px0 + pw
        tit = int(36 * e)
        ih = int(46 * e)
        ph = tit + LINHAS * ih + int(12 * e)
        py0 = (h - ph) // 2
        py1 = py0 + ph
        iy0 = py0 + tit
        colw = (pw - int(30 * e)) // 2
        cols_x = [px0 + int(10 * e), px0 + int(20 * e) + colw]
        alt = ih - int(6 * e)                          

        # ---------- ROSTO 
        boca = 0.0
        rosto = None
        if res_rosto.multi_face_landmarks:
            rosto = res_rosto.multi_face_landmarks[0]
            boca = abertura_boca(rosto)

        # ---------- LOGICA DA MAO DO PINCEL
        tirar_foto = False
        gesto = ""
        cursor_pos = None
        terminou_traco = False

        if mao_des is not None:
            fechada = mao_fechada(mao_des)
            paz = gesto_paz(mao_des)
            apontando = um_dedo(mao_des)

            # ponteiro suavizado = ponta do indicador
            p8 = mao_des.landmark[8]
            bruto = (p8.x * w, p8.y * h)
            if ponteiro is None:
                ponteiro = bruto
            else:
                ponteiro = (0.5 * ponteiro[0] + 0.5 * bruto[0],
                            0.5 * ponteiro[1] + 0.5 * bruto[1])

            # ---- MENU: segurar o indicador em cima de um botao
            alvo = None
            if apontando and not pintura_armada:
                cursor_pos = (int(ponteiro[0]), int(ponteiro[1]))
                mx, my = ponteiro
                if bx0 <= mx <= bx1 and by0 <= my <= by1:
                    alvo = "menu"
                elif menu_aberto:
                    for i, it in enumerate(itens):
                        col, lin = divmod(i, LINHAS)
                        xa, y = cols_x[col], iy0 + lin * ih
                        if xa <= mx <= xa + colw and y <= my <= y + alt:
                            alvo = it[0]
                            break

            if alvo != hover_alvo:       
                hover_alvo = alvo
                hover_inicio = agora
                hover_ok = False

            if alvo is not None and not hover_ok:
                limite = DWELL_MENU if alvo == "menu" else DWELL_ITEM
                if agora - hover_inicio >= limite:
                    if alvo == "menu":
                        menu_aberto = not menu_aberto
                    elif alvo == "dominante":
                        dominante = "canhoto" if dominante == "destro" else "destro"
                    elif alvo == "modo":
                        modo = modo % 3 + 1
                    elif alvo == "cor":
                        cor_idx = (cor_idx + 1) % len(COR_OPCOES)
                    elif alvo == "esp":
                        esp_idx = (esp_idx + 1) % len(ESPESSURAS)
                    elif alvo in cfg:
                        cfg[alvo] = not cfg[alvo]
                    elif alvo == "limpar":
                        tracos.clear()
                        traco_atual = None
                        ponta_suave = None
                    elif alvo == "fechar":
                        menu_aberto = False

                    if alvo in ("modo", "cor", "esp"):
                        hover_inicio = agora   
                    else:
                        hover_ok = True        

            # ---- PINTURA ----
            if pintura_armada and not menu_aberto and cfg["pintura"]:
                if apontando:
                    novo = (p8.x * w, p8.y * h)
                    if ponta_suave is None:
                        ponta_suave = novo
                    else:
                        ponta_suave = (0.6 * ponta_suave[0] + 0.4 * novo[0],
                                       0.6 * ponta_suave[1] + 0.4 * novo[1])
                    if traco_atual is None:
                        traco_atual = []
                        tracos.append(traco_atual)
                    traco_atual.append((int(ponta_suave[0]), int(ponta_suave[1]),
                                        cor_traco, ESPESSURAS[esp_idx]))
                elif traco_atual is not None:
                    # tirou o dedo: termina o traco e desliga a pintura
                    pintura_armada = False
                    traco_atual = None
                    ponta_suave = None
                    terminou_traco = True
                    ultima_troca = agora

            # Punho da mao do pincel
            if (cfg["foto"] and not menu_aberto and fechada and mao_estava_aberta
                    and not pintura_armada and not terminou_traco
                    and agora - ultima_foto > 2.0):
                tirar_foto = True
                ultima_foto = agora

            # V de paz: liga a pintura
            if (cfg["pintura"] and not menu_aberto and paz and not pintura_armada
                    and not terminou_traco and agora - ultima_troca > 0.8):
                pintura_armada = True

            mao_estava_aberta = not fechada and not terminou_traco
            if fechada:
                gesto = "PUNHO"
            elif paz:
                gesto = "PAZ"
            elif apontando:
                gesto = "APONTANDO"
            else:
                gesto = "ABERTA"
        else:
            mao_estava_aberta = False
            hover_alvo = None
            ponteiro = None
            if traco_atual is not None:  
                pintura_armada = False
                traco_atual = None
                ponta_suave = None

        # =============== DESENHO
        saida = np.zeros_like(frame) if modo == 2 else frame.copy()

        # 1) Tracos da pintura (ficam ATRAS de tudo)
        for traco in tracos:
            for i in range(1, len(traco)):
                x1, y1, c1, t1 = traco[i - 1]
                x2, y2, _, _ = traco[i]
                cv2.line(saida, (x1, y1), (x2, y2), c1, t1, cv2.LINE_AA)

        # 2) Rosto
        if rosto is not None and cfg["rosto"]:
            if modo == 1:
                mp_draw.draw_landmarks(
                    saida, rosto, mp_face.FACEMESH_TESSELATION, None,
                    mp_styles.get_default_face_mesh_tesselation_style())
                mp_draw.draw_landmarks(
                    saida, rosto, mp_face.FACEMESH_CONTOURS, None,
                    mp_styles.get_default_face_mesh_contours_style())
                mp_draw.draw_landmarks(
                    saida, rosto, mp_face.FACEMESH_IRISES, None,
                    mp_styles.get_default_face_mesh_iris_connections_style())
            elif modo == 2:
                spec = mp_draw.DrawingSpec(color=cor, thickness=2)
                mp_draw.draw_landmarks(saida, rosto, mp_face.FACEMESH_CONTOURS, None, spec)
                mp_draw.draw_landmarks(saida, rosto, mp_face.FACEMESH_IRISES, None, spec)
            elif modo == 3:
                for p in rosto.landmark:
                    cv2.circle(saida, (int(p.x * w), int(p.y * h)), 1, (0, 255, 0), -1)

        # 3) Esqueleto das maos
        if cfg["mao"]:
            for m in (mao_dir, mao_esq):
                if m is not None:
                    desenhar_mao(saida, m, modo, cor, w, h)

        # 4) Bolinhas de cor nas pontas dos dedos da mao da cor
        if mao_cor is not None:
            for i, nome in enumerate(DEDOS_ORDEM):
                c = cor if COR_OPCOES[i][1] is None else COR_OPCOES[i][1]
                lm = mao_cor.landmark[PONTA_DEDO[nome]]
                pt = (int(lm.x * w), int(lm.y * h))
                cv2.circle(saida, pt, int(10 * e), c, -1)
                if i == cor_idx:
                    cv2.circle(saida, pt, int(15 * e), (255, 255, 255), 2)

        # 5) Anel do pincel enquanto pinta
        if traco_atual is not None and ponta_suave is not None:
            cv2.circle(saida, (int(ponta_suave[0]), int(ponta_suave[1])),
                       10, (255, 255, 255), 2)

        # ---------- BRILHO NEON 
        if modo == 2:
            brilho = cv2.GaussianBlur(saida, (0, 0), 12)
            saida = cv2.addWeighted(saida, 1.0, brilho, 1.8, 0)

        # ---------- FOTOS
        if tirar_foto:
            nome = time.strftime("foto_%Y%m%d_%H%M%S.png")
            cv2.imwrite(os.path.join(PASTA, nome), saida)
            flash = 6
            aviso = f"Salvo: {nome}"
            print(aviso)

        if flash > 0:
            branco = np.full_like(saida, 255)
            saida = cv2.addWeighted(saida, 1 - flash / 8, branco, flash / 8, 0)
            flash -= 1

        # ---------- TEXTOS
        if cfg["textos"]:
            cv2.putText(saida, f"Modo: {NOMES_MODOS[modo]}", (10, 25),
                        FONTE, 0.7, (255, 255, 255), 2)
            cv2.putText(saida, "V pintar | 1/2/3 modo | C limpar | T mao | Punho foto | q",
                        (10, 50), FONTE, 0.45, (200, 200, 200), 1)
            if gesto:
                cv2.putText(saida, f"Pincel: {gesto}", (10, 78),
                            FONTE, 0.6, (0, 255, 255), 2)
            cv2.putText(saida, f"Cor: {COR_OPCOES[cor_idx][0]}", (10, 102),
                        FONTE, 0.6, cor_traco, 2)
            if aviso:
                cv2.putText(saida, aviso, (10, h - 10), FONTE, 0.5, (0, 255, 0), 1)
            # etiquetas nas maos
            for m, nome in ((mao_des, "PINCEL"), (mao_cor, "COR")):
                if m is not None:
                    wx, wy = int(m.landmark[0].x * w), int(m.landmark[0].y * h)
                    cv2.putText(saida, nome, (max(5, wx - 30), min(h - 8, wy + 28)),
                                FONTE, 0.5, (255, 255, 255), 1)

        # Status da pintura
        if pintura_armada:
            msg = ("PINTANDO..." if traco_atual is not None
                   else "PINTURA LIGADA: aponte so o indicador")
            cv2.putText(saida, msg, (10, 130 if cfg["textos"] else 30),
                        FONTE, 0.6, (0, 255, 0), 2)

        # ---------- PALETA
        if not menu_aberto:
            for i in range(len(COR_OPCOES)):
                cx, cy = int((28 + i * 44) * e), h - int(70 * e)
                c = cor if COR_OPCOES[i][1] is None else COR_OPCOES[i][1]
                cv2.circle(saida, (cx, cy), int(12 * e), c, -1)
                if i == cor_idx:
                    cv2.circle(saida, (cx, cy), int(17 * e), (255, 255, 255), 2)
                cv2.putText(saida, SIGLAS[i], (cx - int(12 * e), cy + int(32 * e)),
                            FONTE, 0.4 * e, (200, 200, 200), 1)

        # ---------- MEDIDOR DE BOCA
        if cfg["boca"] and not menu_aberto:
            mt, mh = int(60 * e), int(150 * e)
            mx0, mx1 = w - int(40 * e), w - int(20 * e)
            nivel = int(min(boca / 0.6, 1.0) * mh)
            cv2.rectangle(saida, (mx0, mt), (mx1, mt + mh), (80, 80, 80), 1)
            cv2.rectangle(saida, (mx0, mt + mh - nivel), (mx1, mt + mh), cor, -1)
            cv2.putText(saida, "boca", (w - int(55 * e), mt + mh + int(20 * e)),
                        FONTE, 0.5 * e, (255, 255, 255), 1)
            if boca > 0.35:
                cv2.putText(saida, "AAAAAH!", (w // 2 - 80, h - 30),
                            FONTE, 1.2, cor, 3)

        # ---------- BOTAO DO MENU
        cv2.rectangle(saida, (bx0, by0), (bx1, by1), (30, 30, 30), -1)
        if hover_alvo == "menu" and not hover_ok:
            prog = min((agora - hover_inicio) / DWELL_MENU, 1.0)
            cv2.rectangle(saida, (bx0, by0), (bx0 + int(prog * (bx1 - bx0)), by1),
                          (0, 200, 255), -1)
        cv2.rectangle(saida, (bx0, by0), (bx1, by1), (255, 255, 255), 2)
        rotulo = "FECHAR" if menu_aberto else "MENU"
        (tw, th), _ = cv2.getTextSize(rotulo, FONTE, 0.6 * e, 2)
        cv2.putText(saida, rotulo,
                    (bx0 + (bx1 - bx0 - tw) // 2, by0 + (by1 - by0 + th) // 2),
                    FONTE, 0.6 * e, (255, 255, 255), 2)

        # ---------- PAINEL DO MENU 
        if menu_aberto:
            regiao = saida[py0:py1, px0:px1]
            saida[py0:py1, px0:px1] = (regiao * 0.25).astype(np.uint8)
            cv2.rectangle(saida, (px0, py0), (px1, py1), (255, 255, 255), 1)
            cv2.putText(saida, "MENU - aponte o indicador e segure",
                        (px0 + int(12 * e), py0 + int(24 * e)),
                        FONTE, 0.55 * e, (255, 255, 255), 1)

            fs = 0.5 * e
            for i, (iid, texto, valor, cor_valor, _) in enumerate(itens):
                col, lin = divmod(i, LINHAS)
                xa, y = cols_x[col], iy0 + lin * ih
                xb = xa + colw
                if hover_alvo == iid and not hover_ok:
                    prog = min((agora - hover_inicio) / DWELL_ITEM, 1.0)
                    cv2.rectangle(saida, (xa, y), (xa + int(prog * colw), y + alt),
                                  (0, 120, 0), -1)
                cv2.rectangle(saida, (xa, y), (xb, y + alt), (120, 120, 120), 1)
                ty = y + int(alt * 0.65)
                cv2.putText(saida, texto, (xa + 8, ty), FONTE, fs, (255, 255, 255), 1)
                if valor:
                    (vw, _), _ = cv2.getTextSize(valor, FONTE, fs, 1)
                    cv2.putText(saida, valor, (xb - vw - 8, ty), FONTE, fs, cor_valor, 1)

        # ---------- CURSOR 
        if cursor_pos is not None:
            cv2.circle(saida, cursor_pos, int(9 * e), (255, 255, 0), 2)
            cv2.circle(saida, cursor_pos, 2, (255, 255, 0), -1)

        cv2.imshow("Camera", saida)

        tecla = cv2.waitKey(1) & 0xFF
        if tecla == ord("q"):
            break
        elif tecla in (ord("1"), ord("2"), ord("3")):
            modo = int(chr(tecla))
        elif tecla in (ord("p"), ord("P")):
            if cfg["pintura"] and not menu_aberto:
                pintura_armada = True
        elif tecla in (ord("c"), ord("C")):
            tracos.clear()
            traco_atual = None
            ponta_suave = None
        elif tecla in (ord("t"), ord("T")):   # troca destro/canhoto no teclado
            dominante = "canhoto" if dominante == "destro" else "destro"

cap.release()
cv2.destroyAllWindows()