import threading
import queue
import tkinter as tk

from morse_core import (
    state_lock, gui_queue, current_text, current_letter,
    LETTER_GAP, WORD_GAP, PHRASE_GAP, DOT_THRESHOLD, play_audio,
    MORSE_CODE_DICT,
)


class GapBar(tk.Canvas):
    def __init__(self, parent, width=400, height=14, **kwargs):
        super().__init__(parent, width=width, height=height, **kwargs)
        self.bar_w = width
        self.bar_h = height
        self._value = 0.0

    def set(self, fraction):
        self._value = max(0.0, min(1.0, fraction))
        self.draw()

    def draw(self):
        self.delete('all')
        self.create_rectangle(0, 0, self.bar_w, self.bar_h,
                              fill='#2a2a4e', outline='#3a3a5e', width=1)

        if self._value > 0:
            fw = self._value * self.bar_w
            if self._value < 0.5:
                r = int(self._value * 2 * 255)
                g = 255
                b = int(100 - self._value * 2 * 100)
            else:
                r = 255
                g = int(255 - (self._value - 0.5) * 2 * 255)
                b = 0
            color = f'#{r:02x}{g:02x}{b:02x}'
            self.create_rectangle(1, 1, fw - 1, self.bar_h - 1,
                                  fill=color, outline='')

        self.create_rectangle(0, 0, self.bar_w, self.bar_h,
                              outline='#3a3a5e', width=1)


class MorseGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Traductor Morse a Voz")
        self.root.configure(bg='#1a1a2e')
        self.root.minsize(720, 620)
        self.root.resizable(True, True)

        self.bg = '#1a1a2e'
        self.card = '#16213e'
        self.accent = '#00ff88'
        self.cyan = '#00d2ff'
        self.fg = '#ffffff'
        self.gray = '#888888'

        self.morse_symbols = []

        self._build_ui()
        self.root.after(50, self.poll_queue)

    def _build_ui(self):
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(2, weight=1)

        header = tk.Frame(self.root, bg=self.bg)
        header.grid(row=0, column=0, sticky='ew', padx=20, pady=(12, 4))
        header.columnconfigure(0, weight=1)

        tk.Label(header, text='TRADUCTOR MORSE A VOZ',
                 font=('Segoe UI', 16, 'bold'),
                 bg=self.bg, fg=self.accent).pack(side=tk.LEFT)

        self.status_lbl = tk.Label(header, text='Listo \u2014 presiona ESPACIO',
                                   font=('Segoe UI', 9), bg=self.bg, fg=self.gray)
        self.status_lbl.pack(side=tk.RIGHT)

        body = tk.Frame(self.root, bg=self.bg)
        body.grid(row=1, column=0, sticky='nsew', padx=20, pady=4)
        body.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        # -- Morse code live display --
        morse_card = self._card(body)
        morse_card.grid(row=0, column=0, sticky='ew', pady=(0, 8))
        tk.Label(morse_card, text='C\u00d3DIGO MORSE EN VIVO',
                 font=('Segoe UI', 8, 'bold'),
                 bg=self.card, fg=self.gray).pack(anchor='w', padx=14, pady=(8, 0))

        self.morse_canvas = tk.Canvas(morse_card, height=56, bg=self.card,
                                      highlightthickness=0)
        self.morse_canvas.pack(fill='x', padx=14, pady=(2, 10))

        # -- Letter & Word side by side --
        mid = tk.Frame(body, bg=self.bg)
        mid.grid(row=1, column=0, sticky='ew', pady=4)
        mid.columnconfigure(0, weight=1)
        mid.columnconfigure(1, weight=1)

        let_card = self._card(mid)
        let_card.grid(row=0, column=0, sticky='nsew', padx=(0, 4))
        tk.Label(let_card, text='LETRA ACTUAL',
                 font=('Segoe UI', 8, 'bold'),
                 bg=self.card, fg=self.gray).pack(anchor='w', padx=14, pady=(8, 0))
        self.letter_var = tk.StringVar()
        tk.Label(let_card, textvariable=self.letter_var,
                 font=('Segoe UI', 30, 'bold'),
                 bg=self.card, fg=self.accent, anchor='w'
                 ).pack(fill='x', padx=14, pady=(0, 6))

        word_card = self._card(mid)
        word_card.grid(row=0, column=1, sticky='nsew', padx=(4, 0))
        tk.Label(word_card, text='PALABRA ACTUAL',
                 font=('Segoe UI', 8, 'bold'),
                 bg=self.card, fg=self.gray).pack(anchor='w', padx=14, pady=(8, 0))
        self.word_var = tk.StringVar()
        tk.Label(word_card, textvariable=self.word_var,
                 font=('Segoe UI', 22, 'bold'),
                 bg=self.card, fg=self.cyan, anchor='w'
                 ).pack(fill='x', padx=14, pady=(0, 6))

        # -- Full phrase --
        phr_card = self._card(body)
        phr_card.grid(row=2, column=0, sticky='ew', pady=4)
        tk.Label(phr_card, text='FRASE COMPLETA',
                 font=('Segoe UI', 8, 'bold'),
                 bg=self.card, fg=self.gray).pack(anchor='w', padx=14, pady=(8, 0))
        self.phrase_var = tk.StringVar()
        tk.Label(phr_card, textvariable=self.phrase_var,
                 font=('Segoe UI', 13), bg=self.card, fg=self.fg,
                 wraplength=660, justify='left', anchor='w'
                 ).pack(fill='x', padx=14, pady=(2, 10))

        # -- Progress bars --
        tim_card = self._card(body)
        tim_card.grid(row=3, column=0, sticky='ew', pady=4)
        tk.Label(tim_card, text='PROGRESO DE PAUSA',
                 font=('Segoe UI', 8, 'bold'),
                 bg=self.card, fg=self.gray).pack(anchor='w', padx=14, pady=(8, 0))

        bars_frame = tk.Frame(tim_card, bg=self.card)
        bars_frame.pack(fill='x', padx=14, pady=(4, 8))
        bars_frame.columnconfigure(1, weight=1)

        labels = ['Letra', 'Palabra', 'Frase']
        thresholds = [LETTER_GAP, WORD_GAP, PHRASE_GAP]
        self.bars = []
        for i, (lbl, thr) in enumerate(zip(labels, thresholds)):
            tk.Label(bars_frame, text=lbl, font=('Segoe UI', 8),
                     bg=self.card, fg='#aaaaaa', width=8, anchor='w'
                     ).grid(row=i, column=0, sticky='w', pady=2)
            bar = GapBar(bars_frame, width=420, height=14,
                         bg=self.card, highlightthickness=0)
            bar.grid(row=i, column=1, sticky='ew', padx=(8, 0), pady=2)
            tk.Label(bars_frame, text=f'{thr:.1f}s',
                     font=('Segoe UI', 7), bg=self.card, fg='#666666', width=5
                     ).grid(row=i, column=2, padx=(4, 0), pady=2)
            self.bars.append(bar)

        # -- Instructions --
        instr_card = tk.Frame(body, bg='#0f3460', bd=0,
                              highlightthickness=1, highlightbackground='#1a4a7a')
        instr_card.grid(row=4, column=0, sticky='ew', pady=(4, 0))
        tk.Label(instr_card, text='C\u00d3MO FUNCIONA',
                 font=('Segoe UI', 9, 'bold'),
                 bg='#0f3460', fg='#4fc3f7').pack(anchor='w', padx=14, pady=(8, 2))
        lines = (
            'ESPA\u00d1OL: pulso corto (<0.3s) = \u2022 punto  |  '
            'pulso largo (\u22650.3s) = \u2500\u2500 raya',
            'Pausa 0.5s \u2192 decodifica letra  |  '
            'Pausa 1.5s \u2192 separa palabra',
            'Pausa 3.0s \u2192 reproduce frase  |  '
            'Q \u2192 sale y reproduce frase final',
        )
        for line in lines:
            tk.Label(instr_card, text=line, font=('Segoe UI', 9),
                     bg='#0f3460', fg='#cccccc', anchor='w'
                     ).pack(fill='x', padx=14, pady=1)
        tk.Label(instr_card, text='', bg='#0f3460').pack(pady=(0, 8))

        # -- Buttons row --
        btn_f = tk.Frame(body, bg=self.bg)
        btn_f.grid(row=5, column=0, sticky='ew', pady=(8, 4))
        tk.Button(btn_f, text='DICCIONARIO', font=('Segoe UI', 10, 'bold'),
                  bg='#0f3460', fg='#4fc3f7', activebackground='#1a4a7a',
                  activeforeground='white', bd=0, padx=20, pady=6,
                  cursor='hand2', command=self.open_dict
                  ).pack(side='left')
        tk.Button(btn_f, text='SALIR (Q)', font=('Segoe UI', 10, 'bold'),
                  bg='#e94560', fg='white', activebackground='#c23152',
                  activeforeground='white', bd=0, padx=24, pady=6,
                  cursor='hand2', command=self.quit_app
                  ).pack(side='right')

    def _card(self, parent):
        return tk.Frame(parent, bg=self.card, bd=0,
                        highlightthickness=1, highlightbackground='#2a2a4e')

    def open_dict(self):
        rev = {v: k for k, v in MORSE_CODE_DICT.items()}
        letters = sorted(rev.items(), key=lambda x: (
            0 if x[0].isalpha() else 1 if x[0].isdigit() else 2, x[0]))

        win = tk.Toplevel(self.root)
        win.title('Diccionario Morse')
        win.configure(bg='#1a1a2e')
        win.resizable(False, False)

        tk.Label(win, text='DICCIONARIO MORSE', font=('Segoe UI', 14, 'bold'),
                 bg='#1a1a2e', fg='#00ff88').pack(pady=(10, 4))

        cols = 4
        rows = (len(letters) + cols - 1) // cols
        groups = [letters[i * rows:(i + 1) * rows] for i in range(cols)]

        outer = tk.Frame(win, bg='#16213e')
        outer.pack(padx=10, pady=(0, 10))

        for ci, group in enumerate(groups):
            sub = tk.Frame(outer, bg='#16213e')
            sub.grid(row=0, column=ci, padx=6)

            tk.Label(sub, text='Char', font=('Segoe UI', 8, 'bold'),
                     bg='#0f3460', fg='#4fc3f7', padx=6, pady=2
                     ).grid(row=0, column=0, sticky='ew')
            tk.Label(sub, text='Morse', font=('Segoe UI', 8, 'bold'),
                     bg='#0f3460', fg='#4fc3f7', padx=6, pady=2
                     ).grid(row=0, column=1, sticky='ew')

            for ri, (ch, morse) in enumerate(group, start=1):
                bg = '#1a1a2e' if ri % 2 == 0 else '#16213e'
                tk.Label(sub, text=ch, font=('Segoe UI', 10, 'bold'),
                         bg=bg, fg='#00ff88', padx=6, pady=1
                         ).grid(row=ri, column=0, sticky='ew')
                tk.Label(sub, text=morse, font=('Segoe UI', 10),
                         bg=bg, fg='#cccccc', padx=6, pady=1
                         ).grid(row=ri, column=1, sticky='ew')

    def poll_queue(self):
        try:
            while True:
                ev = gui_queue.get_nowait()
                self.handle(ev)
        except queue.Empty:
            pass
        self.root.after(50, self.poll_queue)

    def handle(self, ev):
        t = ev[0]

        if t == 'morse_add':
            self.morse_symbols.append(ev[1])
            self.draw_morse()
            self.status_lbl.config(text='Escribiendo...', fg=self.accent)

        elif t == 'press_end':
            dur = ev[1]
            lbl = 'punto' if dur < DOT_THRESHOLD else 'raya'
            self.status_lbl.config(text=f'{lbl} ({dur:.2f}s)', fg=self.accent)

        elif t == 'char':
            self.letter_var.set(self.letter_var.get() + ev[1])
            self.morse_symbols.clear()
            self.draw_morse()

        elif t == 'word':
            w = ev[1]
            self.word_var.set(w)
            self.phrase_var.set(self.phrase_var.get() + w + ' ')
            self.letter_var.set('')
            self.morse_symbols.clear()
            self.draw_morse()
            self.status_lbl.config(text=f'Palabra: {w}', fg=self.cyan)

        elif t == 'phrase':
            self.phrase_var.set(ev[1])
            self.letter_var.set('')
            self.word_var.set('')
            self.morse_symbols.clear()
            self.draw_morse()
            self.status_lbl.config(text='Frase reproducida', fg='#ffd700')

        elif t == 'final':
            self.phrase_var.set(ev[1])

        elif t == 'reset_morse':
            self.morse_symbols.clear()
            self.draw_morse()

        elif t == 'reset_all':
            self.letter_var.set('')
            self.word_var.set('')
            self.phrase_var.set('')
            self.morse_symbols.clear()
            self.draw_morse()

        elif t == 'gap':
            g = ev[1]
            if g <= 0:
                for b in self.bars:
                    b.set(0)
                return
            bar_vals = [g / LETTER_GAP, g / WORD_GAP, g / PHRASE_GAP]
            for b, v in zip(self.bars, bar_vals):
                b.set(min(1.0, v))
            if g > PHRASE_GAP * 0.8:
                self.status_lbl.config(
                    text=f'Pausa: {g:.1f}s \u2014 reproduciendo...', fg='#ff4444')
            elif g > WORD_GAP * 0.8:
                self.status_lbl.config(
                    text=f'Pausa: {g:.1f}s \u2014 separando palabra...', fg='#ffd700')
            elif g > LETTER_GAP * 0.8:
                self.status_lbl.config(
                    text=f'Pausa: {g:.1f}s \u2014 decodificando letra...', fg='#00d2ff')
            else:
                self.status_lbl.config(text=f'Pausa: {g:.1f}s', fg=self.gray)

        elif t == 'quit':
            self.root.after(200, self.root.destroy)

    def draw_morse(self):
        self.morse_canvas.delete('all')
        cw = self.morse_canvas.winfo_width() or 660
        x, y = 20, 28
        dot_r, dash_w = 7, 32

        for s in self.morse_symbols:
            if x > cw - 50:
                x = 20
                y += 22
            if s == '.':
                self.morse_canvas.create_oval(
                    x - dot_r, y - dot_r, x + dot_r, y + dot_r,
                    fill=self.accent, outline='')
                x += dot_r * 2 + 10
            else:
                self.morse_canvas.create_rectangle(
                    x, y - dot_r, x + dash_w, y + dot_r,
                    fill=self.accent, outline='')
                x += dash_w + 10

    def quit_app(self):
        with state_lock:
            frase = (current_text + current_letter).strip()
        if frase:
            self.phrase_var.set(frase)
            threading.Thread(target=play_audio, args=(frase,), daemon=True).start()
        self.root.after(300, self.root.destroy)
