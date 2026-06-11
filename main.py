import customtkinter as ctk, mido, threading, pygame, pygame.midi, time, os, math, json, numpy as np
from tkinter import filedialog, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib; matplotlib.use('TkAgg')

# ==============================================================================================
# [ CẤU HÌNH CỐT LÕI & GIAO DIỆN ]
# ==============================================================================================
APP_TITLE              = "MIDI to Mini World Noteblock"
CONFIG_FILE            = "app_config.json"
HE_SO_TOC_DO           = 1.0
CLUSTER_TIME_THRESHOLD = 30       
MUC0_START_W_MS        = 825      

COLOR_BG_MAIN          = ("#FAFAFA", "#2B2B2B")
COLOR_BG_FRAME         = ("#E0E0E0", "#242424")
COLOR_BG_SECTION       = ("#F0F0F0", "#2a2d2e")
COLOR_ACCENT_1         = ("#008C99", "#00e5ff")  # Default Cyan
COLOR_ACCENT_2         = ("#B38600", "#ffc107")  # Default Gold-ish for warnings
COLOR_SYNTH            = ("#107A8B", "#17a2b8")
COLOR_DRUM             = ("#B8326F", "#e83e8c")
COLOR_SUCCESS          = ("#1D7732", "#28a745")
COLOR_SUCCESS_HOVER    = ("#175C27", "#218838")
COLOR_DANGER           = ("#CC3333", "#ff6b6b")
COLOR_INFO             = ("#107A8B", "#17a2b8")
COLOR_INFO_HOVER       = ("#0D6A7A", "#138496")
COLOR_SECONDARY        = ("#5A6268", "#6c757d")
COLOR_SECONDARY_HOVER  = ("#4A5054", "#5a6268")

# ==============================================================================================
# [ TỪ ĐIỂN TRA CỨU TỐC ĐỘ CAO O(1) ]
# ==============================================================================================
MW_NOTE_STRINGS = {}
for b_id, b_name in [(0, "Trầm"), (1, "Trung"), (2, "Cao")]:
    for n_id in range(12):
        MW_NOTE_STRINGS[(b_id, n_id)] = f"Khối {b_name}: {n_id}"

# ==============================================================================================
# [ DỮ LIỆU NHẠC CỤ & MAPPING ]
# ==============================================================================================
MW_SYNTH      = {"Piano": 0, "Guitar": 1, "Harp": 2, "Violin": 3, "Trumpet": 4, "Recorder": 5, "Oud": 6, "Guitar Mộc": 7}
MW_ELECTRONIC = {"Guitar Bass Điện": 0, "Pluck Synth": 1, "Stylophone": 3, "Chuông Điện Tử": 5, "Harpsichord": 7}
MW_DRUMS      = {"Bass": 0, "Floor tom": 1, "Tom-tom": 2, "Lẫy": 3, "Hi-hat (đóng)": 4, "Chũm choẹ trung": 6, "Chũm choẹ to": 5, "Jam-block": 7}

GM_DRUM_MAP = {
    35: "Acoustic Bass Drum", 36: "Bass Drum 1",  37: "Side Stick",     38: "Acoustic Snare",
    39: "Hand Clap",          40: "Electric Snare", 41: "Low Floor Tom",  42: "Closed Hi Hat",
    43: "High Floor Tom",     44: "Pedal Hi-Hat",   45: "Low Tom",        46: "Open Hi-Hat",
    47: "Low-Mid Tom",        48: "Hi-Mid Tom",     49: "Crash Cymbal 1", 50: "High Tom",
    51: "Ride Cymbal 1",      52: "Chinese Cymbal", 53: "Ride Bell",      54: "Tambourine",
    55: "Splash Cymbal",      56: "Cowbell",        57: "Crash Cymbal 2", 58: "Vibraslap", 
    59: "Ride Cymbal 2",      60: "Hi Bongo",       61: "Low Bongo",      62: "Mute Hi Conga",
    63: "Open Hi Conga",      64: "Low Conga",      65: "High Timbale",   66: "Low Timbale"
}

GM_INSTRUMENTS = [
    "Acoustic Grand Piano", "Bright Acoustic Piano", "Electric Grand Piano", "Honky-tonk Piano", "Electric Piano 1", "Electric Piano 2", "Harpsichord", "Clavinet", "Celesta", "Glockenspiel", "Music Box", "Vibraphone", "Marimba", "Xylophone", "Tubular Bells", "Dulcimer", "Drawbar Organ", "Percussive Organ", "Rock Organ", "Church Organ", "Reed Organ", "Accordion", "Harmonica", "Tango Accordion", "Acoustic Guitar (nylon)", "Acoustic Guitar (steel)", "Electric Guitar (jazz)", "Electric Guitar (clean)", "Electric Guitar (muted)", "Overdriven Guitar", "Distortion Guitar", "Guitar Harmonics", "Acoustic Bass", "Electric Bass (finger)", "Electric Bass (pick)", "Fretless Bass", "Slap Bass 1", "Slap Bass 2", "Synth Bass 1", "Synth Bass 2", "Violin", "Viola", "Cello", "Contrabass", "Tremolo Strings", "Pizzicato Strings", "Orchestral Harp", "Timpani", "String Ensemble 1", "String Ensemble 2", "Synth Strings 1", "Synth Strings 2", "Choir Aahs", "Voice Oohs", "Synth Voice", "Orchestra Hit", "Trumpet", "Trombone", "Tuba", "Muted Trumpet", "French Horn", "Brass Section", "Synth Brass 1", "Synth Brass 2", "Soprano Sax", "Alto Sax", "Tenor Sax", "Baritone Sax", "Oboe", "English Horn", "Bassoon", "Clarinet", "Piccolo", "Flute", "Recorder", "Pan Flute", "Blown Bottle", "Shakuhachi", "Whistle", "Ocarina", "Lead 1 (square)", "Lead 2 (sawtooth)", "Lead 3 (calliope)", "Lead 4 (chiff)", "Lead 5 (charang)", "Lead 6 (voice)", "Lead 7 (fifths)", "Lead 8 (bass + lead)", "Pad 1 (new age)", "Pad 2 (warm)", "Pad 3 (polysynth)", "Pad 4 (choir)", "Pad 5 (bowed)", "Pad 6 (metallic)", "Pad 7 (halo)", "Pad 8 (sweep)", "FX 1 (rain)", "FX 2 (soundtrack)", "FX 3 (crystal)", "FX 4 (atmosphere)", "FX 5 (brightness)", "FX 6 (goblins)", "FX 7 (echoes)", "FX 8 (sci-fi)", "Sitar", "Banjo", "Shamisen", "Koto", "Kalimba", "Bagpipe", "Fiddle", "Shanai", "Tinkle Bell", "Agogo", "Steel Drums", "Woodblock", "Taiko Drum", "Melodic Tom", "Synth Drum", "Reverse Cymbal", "Guitar Fret Noise", "Breath Noise", "Seashore", "Bird Tweet", "Telephone Ring", "Helicopter", "Applause", "Gunshot"
]

HELP_TEXT = """# Hướng Dẫn Sử Dụng Công Cụ

## 1. Dây Nối (Wire)
Dây nối xác định khoảng thời gian chờ giữa hai cụm nốt nhạc.
- **Sát nhau:** Gõ gần như ngay lập tức.
- **1 PL (Pulse):** Tương đương 1 lần gõ của khối hẹn giờ.
- **Mức 5 -> Mức 1:** Khoảng trễ tăng dần. Mức 5 là nhanh nhất.
- **Mức 0:** Khoảng trễ dài. Dài hơn sẽ là bội số của Mức 0.

## 2. Chế Độ Nghe Thử
- **🎵 Nhạc MIDI Gốc:** Phát lại bản nhạc gốc. Yêu cầu có bộ tổng hợp MIDI HĐH.
- **🎹 Mini World:** Mô phỏng âm thanh khối nhạc trong game.

## 3. Các Tính Năng Khác
- **Lưu/Tải Cấu Hình:** Lưu lại cách map nhạc cụ.
- **Tăng/Giảm Pitch:** Thay đổi cao độ.
- **Xuất Sơ Đồ:** Lưu file .txt.
- **Đơn giản hóa:** Loại bỏ nốt quá nhanh/nhẹ.
"""

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# ==============================================================================================
# [ LÕI XỬ LÝ THUẬT TOÁN ]
# ==============================================================================================
class MidiProcessor:
    def scan_channels(self, file_path):
        
        mid = mido.MidiFile(file_path)
        used_ch, used_dr, ch_prog = set(), set(), {i: 0 for i in range(16)}
        
        for track in mid.tracks:
            for m in track:
                if m.type == 'program_change': ch_prog[m.channel] = m.program
                elif m.type == 'note_on' and m.velocity > 0: 
                    used_dr.add(m.note) if m.channel == 9 else used_ch.add(m.channel)
                    
        return sorted(list(used_ch)), sorted(list(used_dr)), ch_prog

    def build_note_list(self, file_path, channel_map, simp_opts):
        mid = mido.MidiFile(file_path); abs_t, tempo, og_notes, evts, progs = 0, 500000, [], [], {i: 0 for i in range(16)}
        meta = {'ticks_per_beat': mid.ticks_per_beat, 'length': mid.length, 'initial_tempo': 500000, 'initial_time_signature': '4/4'}
        f_tmp, f_ts = False, False
        for m in mido.merge_tracks(mid.tracks):
            if not f_tmp and m.type == 'set_tempo': meta['initial_tempo'] = m.tempo; f_tmp = True
            if not f_ts and m.type == 'time_signature': meta['initial_time_signature'] = f"{m.numerator}/{m.denominator}"; f_ts = True
            abs_t += mido.tick2second(m.time, mid.ticks_per_beat, tempo) * 1000
            
            if not m.is_meta and m.type in ('note_on', 'note_off', 'program_change', 'control_change', 'pitchwheel'):
                evts.append((abs_t, m))
                
            if m.type == 'set_tempo': tempo = m.tempo
            elif m.type == 'program_change': progs[m.channel] = m.program
            elif m.type == 'note_on' and m.velocity > 0:
                k = f"9_{m.note}" if m.channel == 9 else f"{m.channel}_ALL"
                if k in channel_map: og_notes.append({'time': abs_t, 'note': m.note, 'velocity': m.velocity, 'channel': m.channel, 'map_key': k, 'program': progs.get(m.channel, 0)})
        if simp_opts['enabled']:
            f_notes, lst_t = [], -1
            for n in og_notes:
                if n['velocity'] < simp_opts['velocity'] or ((n['time'] - lst_t) < simp_opts['time_ms'] and lst_t != -1): continue
                f_notes.append(n); lst_t = n['time']
            og_notes = f_notes
        return og_notes, evts, meta

class BlueprintGenerator:
    def create_blueprint(self, og_notes, ch_map, sel_inst, trans_semi, mw_dr_gm, algorithm_mode="CPU (Ổn định)", cp_module=None, cluster_threshold=30, he_so_toc_do=1.0, muc0_ms=825, polyphony=0):
        tg_notes = [n for n in og_notes if ch_map.get(n['map_key']) and ch_map[n['map_key']]["display_name"] in sel_inst]
        if not tg_notes: return []

        gps = []
        gpu_precalculated = False

        if algorithm_mode == "GPU (Thử nghiệm)" and cp_module is not None and len(tg_notes) > 1:
            try:
                times_cpu = np.array([n['time'] for n in tg_notes], dtype=np.float64)
                notes_cpu = np.array([n['note'] for n in tg_notes], dtype=np.int32)
                is_drum_cpu = np.array([1 if ch_map[n['map_key']]["type"] == "Drum" else 0 for n in tg_notes], dtype=np.int32)

                times_gpu = cp_module.asarray(times_cpu)
                notes_gpu = cp_module.asarray(notes_cpu)
                is_drum_gpu = cp_module.asarray(is_drum_cpu)

                diffs = cp_module.diff(times_gpu)
                new_group_flags = cp_module.zeros(len(tg_notes), dtype=cp_module.int32)
                new_group_flags[1:] = (diffs >= cluster_threshold).astype(cp_module.int32)

                pitch_kernel = cp_module.ElementwiseKernel(
                    'int32 notes, int32 trans_semi, int32 is_drum',
                    'int32 block_type, int32 note_mod',
                    '''
                    if (is_drum == 0) {
                        int fn = notes + trans_semi;
                        int mwn = fn;
                        while (mwn < 48) { mwn += 12; }
                        while (mwn > 83) { mwn -= 12; }
                        
                        if (mwn <= 59) { block_type = 0; }
                        else if (mwn <= 71) { block_type = 1; }
                        else { block_type = 2; }
                        
                        note_mod = mwn % 12;
                    } else {
                        block_type = 3; // 3 is id
                        note_mod = 0;   // Will be updated by the Tap number below
                    }
                    ''',
                    'mw_pitch_processor'
                )

                block_type_gpu, note_mod_gpu = pitch_kernel(notes_gpu, trans_semi, is_drum_gpu)

                fn_cpu = block_type_gpu.get() 
                block_type_cpu = block_type_gpu.get()
                note_mod_cpu = note_mod_gpu.get()
                split_flags_cpu = new_group_flags.get()

                split_indices = np.where(split_flags_cpu == 1)[0]
                gps = [g.tolist() for g in np.split(np.arange(len(tg_notes)), split_indices)]
                gpu_precalculated = True

            except Exception as e:
                print(f"Lỗi tăng tốc GPU, quay về CPU. Chi tiết: {e}")
                algorithm_mode = "CPU (Ổn định)"

        if algorithm_mode == "CPU (Ổn định)" or not gps:
            if len(tg_notes) > 1:
                times_cpu = np.array([n['time'] for n in tg_notes], dtype=np.float64)
                diffs = np.diff(times_cpu)
                split_indices = np.where(diffs >= cluster_threshold)[0] + 1
                gps = [g.tolist() for g in np.split(np.arange(len(tg_notes)), split_indices)]
            elif tg_notes:
                gps = [[0]]

        bp = []
        for gi, grp_indices in enumerate(gps):
            if not grp_indices: continue
            t_sync = tg_notes[grp_indices[0]]['time']
            inst_d = {}

            for idx in grp_indices:
                n = tg_notes[idx]
                minfo = ch_map[n['map_key']]
                inm = minfo["display_name"]

                if inm not in inst_d: 
                    inst_d[inm] = {"notes_raw_data": [], "notes": [], "type": minfo["type"], "name": minfo["name"]}

                if minfo["type"] == "Drum":
                    inst_d[inm]["notes_raw_data"].append((3, minfo['tap']))
                    inst_d[inm]["notes"].append({'midi': mw_dr_gm.get(minfo['name'], 60), 'channel': 9, 'og_midi': n['note'], 'program': n.get('program', 0), 'velocity': n.get('velocity', 100)})
                else:
                    fn = n['note'] + trans_semi
                    if gpu_precalculated:
                        b_id = int(block_type_cpu[idx])
                        n_mod = int(note_mod_cpu[idx])
                    else:
                        mwn = fn
                        while mwn < 48: mwn += 12
                        while mwn > 83: mwn -= 12
                        b_id = 0 if mwn <= 59 else 1 if mwn <= 71 else 2
                        n_mod = mwn % 12
                    
                    inst_d[inm]["notes_raw_data"].append((b_id, n_mod))
                    inst_d[inm]["notes"].append({'midi': fn, 'channel': n['channel'], 'og_midi': fn, 'program': n.get('program', 0), 'velocity': n.get('velocity', 100)})

            for nm in inst_d:
                inst_d[nm]["notes_raw_data"] = list(dict.fromkeys(inst_d[nm]["notes_raw_data"]))
                inst_d[nm]["notes"] = list({(d['og_midi'], d['channel']): d for d in inst_d[nm]["notes"]}.values())
                if polyphony > 0:
                    inst_d[nm]["notes_raw_data"] = inst_d[nm]["notes_raw_data"][:polyphony]
                    inst_d[nm]["notes"] = inst_d[nm]["notes"][:polyphony]

            wstr = "[HẾT BÀI]"
            if gi < len(gps) - 1:
                next_grp_indices = gps[gi+1]
                if next_grp_indices:
                    w_ms = max(0, ((tg_notes[next_grp_indices[0]]['time'] - t_sync) * he_so_toc_do) - 50)
                    if w_ms < 30: wstr = "Sát nhau"
                    elif w_ms < 100: wstr = "1 PL"
                    elif w_ms < muc0_ms: wstr = f"Mức {5 - (int(round(w_ms / 150.0)) - 1)}"
                    else:
                        pts = [f"{int(w_ms // muc0_ms)} Mức 0"] if int(w_ms // muc0_ms) > 0 else []
                        rem = w_ms % muc0_ms
                        if rem >= 100: pts.append(f"1 Mức {5 - (int(round(rem / 150.0)) - 1)}")
                        elif rem >= 30: pts.append("1 PL")
                        wstr = " + ".join(pts) if pts else "Mức 0"
            
            bp.append({"id": f"{gi+1:03d}", "sync_time": t_sync, "instruments": inst_d, "wire": wstr})
        return bp

# ==============================================================================================
# [ GIAO DIỆN & CỬA SỔ PHỤ ]
# ==============================================================================================
class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master); self.app = master
        self.title("Trạm Điều Khiển Trung Tâm (Studio Mode)"); self.geometry("900x800")
        self.attributes('-topmost', self.app.always_on_top.get())
        self.protocol("WM_DELETE_WINDOW", self.hide_window)

        self.tabs_loaded = {"ui": False, "audio": False, "algo": False, "advanced": False}
        self.tabs = ctk.CTkTabview(self, command=self.on_tab_change)
        self.tabs.pack(fill="both", expand=True, padx=15, pady=10)
        
        self.tab_ui = self.tabs.add("🖥 Giao diện")
        self.tab_au = self.tabs.add("🎵 Âm thanh")
        self.tab_al = self.tabs.add("⚡ Thuật toán")
        self.tab_ad = self.tabs.add("🛠 Nâng cao")

        self.build_ui_tab()

    def on_tab_change(self):
        t = self.tabs.get()
        if t == "🎵 Âm thanh" and not self.tabs_loaded["audio"]: self.build_audio_tab()
        elif t == "⚡ Thuật toán" and not self.tabs_loaded["algo"]: self.build_algo_tab()
        elif t == "🛠 Nâng cao" and not self.tabs_loaded["advanced"]: self.build_advanced_tab()

    def add_row_switch(self, parent, title, variable, default_val, desc="", command=None):
        frm = ctk.CTkFrame(parent, fg_color="transparent"); frm.pack(fill="x", pady=8, padx=10, anchor="w")
        lbl_frm = ctk.CTkFrame(frm, fg_color="transparent"); lbl_frm.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(lbl_frm, text=title, font=ctk.CTkFont(weight="bold", size=14), anchor="w").pack(fill="x")
        if desc: ctk.CTkLabel(lbl_frm, text=desc, font=ctk.CTkFont(size=12, slant="italic"), text_color="gray", anchor="w").pack(fill="x")
        def reset_action(): 
            variable.set(default_val)
            if command: command()
        ctk.CTkButton(frm, text="↺", width=30, height=30, fg_color="transparent", hover_color=self.app.get_current_color(COLOR_BG_SECTION), text_color="gray", command=reset_action).pack(side="right", padx=(5, 0))
        ctk.CTkSwitch(frm, text="", variable=variable, command=command, width=50).pack(side="right", padx=(5, 0))

    def add_row_dropdown(self, parent, title, variable, default_val, options, desc="", command=None):
        frm = ctk.CTkFrame(parent, fg_color="transparent"); frm.pack(fill="x", pady=8, padx=10, anchor="w")
        lbl_frm = ctk.CTkFrame(frm, fg_color="transparent"); lbl_frm.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(lbl_frm, text=title, font=ctk.CTkFont(weight="bold", size=14), anchor="w").pack(fill="x")
        if desc: ctk.CTkLabel(lbl_frm, text=desc, font=ctk.CTkFont(size=12, slant="italic"), text_color="gray", anchor="w").pack(fill="x")
        def reset_action(): 
            variable.set(default_val)
            if command: command(default_val)
        ctk.CTkButton(frm, text="↺", width=30, height=30, fg_color="transparent", hover_color=self.app.get_current_color(COLOR_BG_SECTION), text_color="gray", command=reset_action).pack(side="right", padx=(5, 0))
        ctk.CTkOptionMenu(frm, values=options, variable=variable, command=command, width=160).pack(side="right", padx=(5, 0))

    def add_row_slider(self, parent, title, variable, default_val, min_val, max_val, formatter=lambda x: str(int(x)), desc="", extra_cmd=None):
        frm = ctk.CTkFrame(parent, fg_color="transparent"); frm.pack(fill="x", pady=10, padx=10, anchor="w")
        lbl_frm = ctk.CTkFrame(frm, fg_color="transparent"); lbl_frm.pack(fill="x")
        ctk.CTkLabel(lbl_frm, text=title, font=ctk.CTkFont(weight="bold", size=14), anchor="w").pack(side="left")
        val_lbl = ctk.CTkLabel(lbl_frm, text=formatter(variable.get()), font=ctk.CTkFont(weight="bold"), text_color=self.app.get_current_color(COLOR_ACCENT_1))
        val_lbl.pack(side="right", padx=40)
        if desc: ctk.CTkLabel(frm, text=desc, font=ctk.CTkFont(size=12, slant="italic"), text_color="gray", anchor="w").pack(fill="x", pady=(0, 5))
        sl_frm = ctk.CTkFrame(frm, fg_color="transparent"); sl_frm.pack(fill="x")
        def update_lbl(v): 
            val_lbl.configure(text=formatter(float(v)))
            if extra_cmd: extra_cmd()
        def reset_action(): 
            variable.set(default_val); update_lbl(default_val)
        ctk.CTkButton(sl_frm, text="↺", width=30, height=30, fg_color="transparent", hover_color=self.app.get_current_color(COLOR_BG_SECTION), text_color="gray", command=reset_action).pack(side="right", padx=(5, 0))
        sl = ctk.CTkSlider(sl_frm, from_=min_val, to=max_val, variable=variable, command=update_lbl)
        sl.pack(side="left", fill="x", expand=True, padx=(0, 5))

    def build_ui_tab(self):
        s_ui = ctk.CTkScrollableFrame(self.tab_ui, fg_color="transparent"); s_ui.pack(fill="both", expand=True)
        self.add_row_switch(s_ui, "Luôn hiển thị trên cùng", self.app.always_on_top, False, command=self.app.toggle_always_on_top)
        self.add_row_dropdown(s_ui, "Chế độ nền", self.app.appearance_mode_str, "Dark", ["System", "Dark", "Light"], command=self.change_appearance_mode)
        self.add_row_dropdown(s_ui, "Tỉ lệ giao diện", self.app.ui_scaling_str, "100%", ["80%", "90%", "100%", "110%", "120%", "150%"], command=self.change_scaling)
        self.add_row_switch(s_ui, "Hiển thị Minimap (Sơ đồ ngang)", self.app.show_minimap, True, "Tắt tính năng này sẽ tăng đang kể FPS khi cuộn màn hình.", self.toggle_minimap)
        self.add_row_switch(s_ui, "Tự động cuộn Sơ đồ Dọc", self.app.auto_scroll_text, True, "Văn bản sẽ tự chạy theo nhạc. Tắt đi nếu muốn tự đọc.")
        self.add_row_dropdown(s_ui, "Font chữ Sơ đồ Dọc", getattr(self.app, 'font_vertical', ctk.StringVar(value="Consolas")), "Consolas", ["Consolas", "Courier New", "Arial"], "Chọn font Monospace để kẻ bảng không bị lệch.")
        self.add_row_switch(s_ui, "Hiển thị tên nốt (C4, D4)", getattr(self.app, 'show_note_names', ctk.BooleanVar(value=False)), False, "Sơ đồ ngang sẽ hiện C4, D4 thay vì 'Khối Trung: 1'.", command=self.mark_recalc)
        self.add_row_switch(s_ui, "Hiện nhãn trên Dây Nối ngang", self.app.show_wire_label, True, command=self.mark_recalc)
        self.add_row_slider(s_ui, "Tốc độ quét đồ họa (FPS)", self.app.canvas_fps, 33, 10, 60, lambda x: f"{int(x)} ms", "Thấp (10ms): Mượt nhưng nóng máy | Cao (60ms): Nhẹ máy.")
        self.add_row_slider(s_ui, "Độ rộng thẻ Sơ đồ Ngang", getattr(self.app, 'ui_card_width', ctk.IntVar(value=320)), 320, 200, 600, lambda x: f"{int(x)} px", extra_cmd=self.change_card_width)
        self.tabs_loaded["ui"] = True

    def build_audio_tab(self):
        s_au = ctk.CTkScrollableFrame(self.tab_au, fg_color="transparent"); s_au.pack(fill="both", expand=True)
        self.add_row_switch(s_au, "Phát nhạc khi bấm Cụm", self.app.auto_play_cluster_audio, True, "Nghe trước toàn bộ nốt trong Cụm khi bấm chuột.")
        self.add_row_switch(s_au, "Cưỡng chế gửi lệnh Tắt Nốt", getattr(self.app, 'enable_note_off', ctk.BooleanVar(value=True)), True, "Chống kẹt âm kéo dài cho các nhạc cụ hệ hơi (Sáo, Violin).")
        self.add_row_switch(s_au, "Chặn hiệu ứng Vang (Reverb/Chorus)", getattr(self.app, 'ignore_reverb', ctk.BooleanVar(value=False)), False, "Lọc bỏ các lệnh gây tiếng vang vọng không cần thiết.")
        self.add_row_switch(s_au, "Chuẩn hóa lực gõ (Normalize Velocity)", getattr(self.app, 'auto_normalize_velocity', ctk.BooleanVar(value=False)), False, "Ép tất cả nốt nhạc kêu to bằng nhau (Bỏ qua sắc thái tác giả).")
        self.add_row_slider(s_au, "Sàn âm lượng cứu hộ", self.app.volume_floor, 50, 0, 100, lambda x: f"Mức {int(x)}", "Cứu các bản nhạc bị tác giả cố tình Fade-out quá nhỏ.")
        self.add_row_slider(s_au, "Khuếch đại tổng (Nhạc cụ)", self.app.volume_boost, 1.5, 0.5, 3.0, lambda x: f"{x:.2f}x", "Nhân âm lượng toàn bài. MiniWorld khuyên dùng 1.5x.")
        self.add_row_slider(s_au, "Khuếch đại riêng cho Trống", getattr(self.app, 'drum_boost_factor', ctk.DoubleVar(value=1.5)), 1.5, 0.5, 3.0, lambda x: f"{x:.2f}x")
        self.tabs_loaded["audio"] = True

    def build_algo_tab(self):
        s_al = ctk.CTkScrollableFrame(self.tab_al, fg_color="transparent"); s_al.pack(fill="both", expand=True)
        f_gpu = ctk.CTkFrame(s_al, fg_color="transparent"); f_gpu.pack(fill="x", pady=8, padx=10, anchor="w")
        ctk.CTkLabel(f_gpu, text="Lõi xử lý (Engine)", font=ctk.CTkFont(weight="bold", size=14)).pack(side="left")
        algo_seg = ctk.CTkSegmentedButton(f_gpu, values=["CPU (Ổn định)", "GPU (Thử nghiệm)"], variable=self.app.algorithm_mode, command=self.mark_recalc)
        if not self.app.has_gpu: algo_seg.configure(state="disabled")
        algo_seg.pack(side="right", padx=(5, 0))
        self.add_row_switch(s_al, "Chế độ Performance (Cày cuốc)", self.app.performance_mode, False, "Tắt mọi hiệu ứng làm đẹp. Dành riêng cho máy yếu.", self.toggle_performance_mode)
        self.add_row_slider(s_al, "Ngưỡng gộp cụm (Cluster Time)", self.app.cluster_time_threshold, 30, 10, 100, lambda x: f"{int(x)} ms", "Nốt cách nhau dưới mức này sẽ bị gộp chung vào 1 thẻ.", extra_cmd=self.mark_recalc)
        self.add_row_slider(s_al, "Độ giãn của dây Mức 0", self.app.wire_level_0_ms, 825, 500, 2000, lambda x: f"{int(x)} ms", "Quy định 1 khối Mức 0 (Chậm nhất) tương đương bao nhiêu mili-giây.", extra_cmd=self.mark_recalc)
        self.add_row_slider(s_al, "Hệ số co giãn nhịp tổng", getattr(self.app, 'he_so_toc_do', ctk.DoubleVar(value=1.0)), 1.0, 0.5, 2.0, lambda x: f"{x:.2f}x", "Làm thưa hoặc nén nhịp toàn bộ bản nhạc.", extra_cmd=self.mark_recalc)
        self.add_row_slider(s_al, "Lọc nốt siêu ngắn (Staccato Filter)", getattr(self.app, 'staccato_cutoff', ctk.IntVar(value=0)), 0, 0, 200, lambda x: "Tắt" if int(x)==0 else f"Bỏ nốt < {int(x)} ms", "Xóa các nốt rác cực ngắn làm đục âm thanh.", extra_cmd=self.mark_recalc)
        self.add_row_slider(s_al, "Giới hạn đa âm (Polyphony Limit)", self.app.polyphony_limit, 0, 0, 30, lambda x: "Vô hạn" if int(x)==0 else f"Tối đa {int(x)} nốt", "Chống Crash game MiniWorld khi có quá nhiều khối gõ cùng lúc.", extra_cmd=self.mark_recalc)
        self.tabs_loaded["algo"] = True

    def build_advanced_tab(self):
        s_ad = ctk.CTkScrollableFrame(self.tab_ad, fg_color="transparent"); s_ad.pack(fill="both", expand=True)
        ctk.CTkButton(s_ad, text="🥁 Mở Trình Quản Lý Trống", height=45, font=ctk.CTkFont(size=14, weight="bold"), command=self.open_drum_kit_manager).pack(fill="x", padx=10, pady=(10, 20))
        
        frm_ram = ctk.CTkFrame(s_ad, fg_color="transparent"); frm_ram.pack(fill="x", padx=10)
        ctk.CTkLabel(frm_ram, text="Công cụ hệ thống", font=ctk.CTkFont(weight="bold", size=14)).pack(anchor="w", pady=(0, 5))
        ctk.CTkLabel(frm_ram, text="Bấm nút này nếu RAM máy tính đang bị đầy do load file Black MIDI quá nặng.", text_color="gray", justify="left").pack(anchor="w", pady=(0, 10))
        ctk.CTkButton(frm_ram, text="🧹 Xả Bộ Nhớ Đệm Khẩn Cấp (Flush RAM)", fg_color=self.app.get_current_color(COLOR_DANGER), hover_color="#8b0000", command=self.force_clear_ram).pack(anchor="w")
        self.tabs_loaded["advanced"] = True

    def mark_recalc(self, *args):
        self._needs_recalc = True

    def hide_window(self):
        if hasattr(self.app, 'ui_card_width'): self.app.card_width = self.app.ui_card_width.get()
        self.app.save_app_config()
        self.withdraw() 
        if hasattr(self, '_needs_recalc') and self._needs_recalc:
            if self.app.original_notes:
                with self.app.cache_lock: self.app.blueprint_cache.clear()
                self.app.update_active_blueprint()
            self._needs_recalc = False

    def change_appearance_mode(self, mode):
        ctk.set_appearance_mode(mode)
        if hasattr(self.app, 'active_blueprint') and self.app.active_blueprint:
            self.app.render_active_sheet(); self.app.apply_sync_visuals()
        if hasattr(self.app, '_is_stats_loaded'): self.app._is_stats_loaded = False
        if hasattr(self.app, 'tabview') and self.app.tabview.get() == "Thống kê": self.app._load_stats_now()
        
    def change_scaling(self, scale_str): ctk.set_widget_scaling(float(scale_str.replace("%", "")) / 100.0)
    def toggle_minimap(self):
        if self.app.show_minimap.get():
            self.app.minimap_canvas.pack(side="bottom", fill="x", before=self.app.scrollbar_x)
            self.app._draw_minimap(); self.app._update_minimap_viewport()
        else: self.app.minimap_canvas.pack_forget()

    def toggle_performance_mode(self): self.app.apply_sync_visuals(); self.app.render_active_sheet()
    def open_drum_kit_manager(self):
        if not hasattr(self.app, 'drum_kit_window') or not self.app.drum_kit_window.winfo_exists(): 
            self.app.drum_kit_window = DrumKitManager(self.app)
        self.app.drum_kit_window.deiconify(); self.app.drum_kit_window.focus()
        
    def force_clear_ram(self):
        import gc; gc.collect()
        if self.app.has_gpu and self.app.cupy:
            try:
                self.app.cupy.get_default_memory_pool().free_all_blocks()
                self.app.cupy.get_default_pinned_memory_pool().free_all_blocks()
            except: pass
        self.app.show_dialog(messagebox.showinfo, "Dọn dẹp", "Đã dọn dẹp sạch sẽ bộ nhớ hệ thống!", parent=self)
    def change_card_width(self):
        self.app.card_width = self.app.ui_card_width.get()
        if hasattr(self.app, 'active_blueprint') and self.app.active_blueprint:
            self.app.render_active_sheet()
            self.app.apply_sync_visuals()

class DrumKitManager(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master); self.transient(master); self.app = master
        self.title("Trình Quản Lý Bộ Trống"); self.geometry("700x600"); self.drum_map_combos = {}
        
        top_frm = ctk.CTkFrame(self, fg_color="transparent"); top_frm.pack(fill="x", padx=10, pady=10)
        ctk.CTkButton(top_frm, text="Tải Bộ Trống", command=self.load_kit).pack(side="left", padx=5)
        ctk.CTkButton(top_frm, text="Lưu Bộ Trống", command=self.save_kit).pack(side="left", padx=5)
        ctk.CTkButton(top_frm, text="Áp Dụng", command=self.apply_kit, fg_color=self.app.get_current_color(COLOR_SUCCESS)).pack(side="right", padx=5)

        scr_frm = ctk.CTkScrollableFrame(self); scr_frm.pack(fill="both", expand=True, padx=10, pady=5)
        opt_drum = [f"🥁 Trống: {k} (Gõ {v})" for k, v in MW_DRUMS.items()]

        for n_val, n_name in sorted(GM_DRUM_MAP.items()):
            row = ctk.CTkFrame(scr_frm); row.pack(fill="x", pady=2, padx=5)
            ctk.CTkLabel(row, text=f"Nốt {n_val}: {n_name}", width=250, anchor="w").pack(side="left", padx=10)
            cb = ctk.CTkComboBox(row, values=opt_drum, width=250)
            cur = self.app.active_drum_map.get(n_val)
            if cur:
                for o in opt_drum:
                    if cur in o: cb.set(o); break
            cb.pack(side="right", padx=10, pady=5); self.drum_map_combos[n_val] = cb

    def save_kit(self):
        path = self.app.show_dialog(filedialog.asksaveasfilename, defaultextension=".json", filetypes=[("Drum Kit JSON", "*.json")], title="Lưu Bộ Trống", parent=self)
        if path:
            try:
                with open(path, 'w', encoding='utf-8') as f: json.dump({n: c.get() for n, c in self.drum_map_combos.items()}, f, indent=4)
                self.app.show_dialog(messagebox.showinfo, "Thành công", "Đã lưu bộ trống.", parent=self)
            except Exception as e: self.app.show_dialog(messagebox.showerror, "Lỗi", f"Không thể lưu file: {e}", parent=self)

    def load_kit(self):
        path = self.app.show_dialog(filedialog.askopenfilename, filetypes=[("Drum Kit JSON", "*.json")], title="Tải Bộ Trống", parent=self)
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f: d = json.load(f)
                for k, v in d.items():
                    if int(k) in self.drum_map_combos: self.drum_map_combos[int(k)].set(v)
                self.app.show_dialog(messagebox.showinfo, "Thành công", "Đã tải bộ trống.", parent=self)
            except Exception as e: self.app.show_dialog(messagebox.showerror, "Lỗi", f"Không thể tải file: {e}", parent=self)

    def apply_kit(self):
        self.app.active_drum_map = {n: c.get().split(":")[1].split("(")[0].strip() for n, c in self.drum_map_combos.items()}
        self.app.show_dialog(messagebox.showinfo, "Hoàn tất", "Đã áp dụng.", parent=self); self.destroy()

# ==============================================================================================
# [ MAIN APPLICATION ]
# ==============================================================================================
class MiniWorldConverterApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.last_directory        = "."
        self.window_geometry       = "1400x950"
        self.always_on_top         = ctk.BooleanVar(value=False)
        self.appearance_mode_str   = ctk.StringVar(value="Dark")
        self.ui_scaling_str        = ctk.StringVar(value="100%")
        self.cluster_time_threshold = ctk.IntVar(value=30)
        self.auto_play_cluster_audio = ctk.BooleanVar(value=True)
        self.default_playback_speed = ctk.StringVar(value="1.0x")
        self.current_midi_device_str = ctk.StringVar(value="Default")
        self.show_minimap          = ctk.BooleanVar(value=True)
        self.performance_mode      = ctk.BooleanVar(value=False)
        self.highlight_active_notes = ctk.BooleanVar(value=True)
        self.default_theme_str     = ctk.StringVar(value="Mặc định (Cyan)")
        self.canvas_fps = ctk.IntVar(value=33)          
        self.volume_floor = ctk.IntVar(value=50)        
        self.volume_boost = ctk.DoubleVar(value=1.5)    
        self.auto_scroll_text = ctk.BooleanVar(value=True) 
        self.wire_level_0_ms = ctk.IntVar(value=825)    
        self.polyphony_limit = ctk.IntVar(value=0)      
        self.auto_transpose = ctk.BooleanVar(value=False) 
        self.remove_ghost_notes = ctk.BooleanVar(value=False) 
        self.he_so_toc_do = ctk.DoubleVar(value=1.0)     
        self.ui_card_width = ctk.IntVar(value=320)       
        self.show_wire_label = ctk.BooleanVar(value=True) 
        self.drum_boost_factor = ctk.DoubleVar(value=1.5) 
        self.enable_note_off = ctk.BooleanVar(value=True) 
        self.auto_normalize_velocity = ctk.BooleanVar(value=False) 
        self.ignore_reverb = ctk.BooleanVar(value=False)           
        self.show_note_names = ctk.BooleanVar(value=False)         
        self.font_vertical = ctk.StringVar(value="Consolas")       
        self.staccato_cutoff = ctk.IntVar(value=0)                 
        self.has_gpu = False
        self.cupy = None
        try:
            import cupy
            if cupy.is_available():
                self.cupy = cupy
                self.has_gpu = True
                print("CuPy GPU acceleration is available.")
        except (ImportError, ModuleNotFoundError):
            print("CuPy not found. GPU acceleration will be disabled.")
        self.algorithm_mode = ctk.StringVar(value="CPU (Ổn định)")
        self.load_app_config()
        self.title(APP_TITLE)
        self.geometry(self.window_geometry)
        self.attributes('-topmost', self.always_on_top.get())
        ctk.set_appearance_mode(self.appearance_mode_str.get())
        try: ctk.set_widget_scaling(float(self.ui_scaling_str.get().replace("%", "")) / 100.0)
        except: pass
        
        pygame.init()
        if not pygame.mixer.get_init(): pygame.mixer.init(44100, -16, 2, 1024)
        self.midi_out, self.has_midi_output = None, False
        try:
            pygame.midi.init()
            if pygame.midi.get_count() > 0 and pygame.midi.get_default_output_id() != -1:
                out_id = pygame.midi.get_default_output_id()
                dev_str = self.current_midi_device_str.get()
                if dev_str != "Default":
                    try: out_id = int(dev_str.split(":")[0])
                    except: pass
                if out_id != -1:
                    try:
                        self.midi_out = pygame.midi.Output(out_id)
                        self.has_midi_output = True
                    except Exception as e: print(f"Không thể mở thiết bị MIDI {out_id}: {e}")
        except: pass

        self.processor             = MidiProcessor()
        self.generator             = BlueprintGenerator()
        self.file_path             = ""
        self.original_notes        = [] 
        self.available_instruments = []
        self.selected_instruments  = set()
        self.checkbox_vars         = {}
        self.active_blueprint      = [] 
        self.blueprint_synctimes   = np.array([])
        self.mw_channel_programs   = {}
        self.midi_metadata         = {}
        self.transpose_semitones   = 0
        
        self.blueprint_cache       = {}
        self.cache_lock            = threading.Lock()
        
        self.mw_instrument_to_gm = {"Piano": 0, "Guitar": 27, "Harp": 46, "Violin": 45, "Trumpet": 56, "Recorder": 74, "Oud": 24, "Guitar Mộc": 24, "Guitar Bass Điện": 33, "Pluck Synth": 84, "Stylophone": 80, "Chuông Điện Tử": 10, "Harpsichord": 6}
        self.mw_drum_to_gm_note  = {"Bass": 36, "Floor tom": 41, "Tom-tom": 45, "Lẫy": 38, "Hi-hat (đóng)": 42, "Chũm choẹ trung": 51, "Chũm choẹ to": 49, "Jam-block": 76}
        self.default_drum_map    = {n: name for n, name in MW_DRUMS.items()}
        self.active_drum_map     = self._create_default_drum_map()
        
        self.is_playing           = False
        self.is_paused            = False
        self.playback_speed       = float(self.default_playback_speed.get().replace("x", "")) 
        self.current_step_index   = 0
        self.playback_offset      = 0  
        self.current_preview_mode = "🎵 Nhạc MIDI Gốc"
        self.start_perf, self.start_offset, self.next_orig_idx, self.next_mw_idx = 0, 0, 0, 0
        self.preview_note_off_timer = None
        self.preview_notes_on     = []
        self.preview_lock         = threading.Lock()
        self.top_10_notes_expanded = ctk.BooleanVar(value=False)
        self.top_10_inst_expanded = ctk.BooleanVar(value=False)
        self.btn_toggle_notes = None
        self.btn_toggle_inst = None
        self.full_midi_events, self.next_midi_event_idx = [], 0
        
        self.canvas_rects         = [] 
        self.txt_vert_line_map    = [] 
        self._last_highlight_idx  = None
        self.card_width           = 320  
        
        self.current_theme_name   = self.default_theme_str.get()
        self._apply_theme(self.current_theme_name, first_load=True)

        self.setup_input_screen()
        self.setup_mapping_screen()
        self.setup_output_screen()
        
        self.frame_mapping.pack_forget()
        self.frame_output.pack_forget()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def show_dialog(self, dialog_func, *args, **kwargs):
        was_top = self.always_on_top.get()
        if was_top:
            self.attributes('-topmost', False)
            self.update_idletasks()
        if 'parent' not in kwargs: kwargs['parent'] = self
        res = dialog_func(*args, **kwargs)
        if was_top:
            self.attributes('-topmost', True)
            self.toggle_always_on_top()
        return res

    def get_current_color(self, color_tuple):
        mode = ctk.get_appearance_mode()
        if mode == "Light": return color_tuple[0]
        else: return color_tuple[1]

    def _decode_note_str(self, b_id, n_mod):
        if b_id == 3: return f"[Trống] Gõ {n_mod}"
        return MW_NOTE_STRINGS.get((b_id, n_mod), f"Lỗi nốt: {n_mod}")

    def load_app_config(self):
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    cfg = json.load(f)
                    self.window_geometry = cfg.get("window_geometry", "1400x950")
                    self.last_directory = cfg.get("last_directory", ".") if os.path.isdir(cfg.get("last_directory", ".")) else "."
                    self.always_on_top.set(cfg.get("always_on_top", False))
                    if self.has_gpu: self.algorithm_mode.set(cfg.get("algorithm_mode", "CPU (Ổn định)"))
                    self.appearance_mode_str.set(cfg.get("appearance_mode", "Dark"))
                    self.ui_scaling_str.set(cfg.get("ui_scaling", "100%"))
                    self.cluster_time_threshold.set(cfg.get("cluster_threshold", 30))
                    self.auto_play_cluster_audio.set(cfg.get("auto_play_cluster", True))
                    self.current_midi_device_str.set(cfg.get("midi_out_device", "Default"))
                    self.default_playback_speed.set(cfg.get("default_playback_speed", "1.0x"))
                    self.show_minimap.set(cfg.get("show_minimap", True))
                    self.performance_mode.set(cfg.get("performance_mode", False))
                    self.highlight_active_notes.set(cfg.get("highlight_active_notes", True))
                    self.default_theme_str.set(cfg.get("default_theme", "Mặc định (Cyan)"))
                    self.canvas_fps.set(cfg.get("canvas_fps", 33))
                    self.volume_floor.set(cfg.get("volume_floor", 50))
                    self.volume_boost.set(cfg.get("volume_boost", 1.5))
                    self.auto_scroll_text.set(cfg.get("auto_scroll_text", True))
                    self.wire_level_0_ms.set(cfg.get("wire_level_0_ms", 825))
                    self.polyphony_limit.set(cfg.get("polyphony_limit", 0))
                    self.auto_transpose.set(cfg.get("auto_transpose", False))
                    self.remove_ghost_notes.set(cfg.get("remove_ghost_notes", False))
                    self.he_so_toc_do.set(cfg.get("he_so_toc_do", 1.0))
                    self.ui_card_width.set(cfg.get("ui_card_width", 320))
                    self.show_wire_label.set(cfg.get("show_wire_label", True))
                    self.drum_boost_factor.set(cfg.get("drum_boost_factor", 1.5))
                    self.enable_note_off.set(cfg.get("enable_note_off", True))
                    self.card_width = self.ui_card_width.get() 
        except: pass

    def save_app_config(self):
        try:
            config_data = {
                "window_geometry": self.geometry(), "last_directory": self.last_directory, "always_on_top": self.always_on_top.get(),
                "algorithm_mode": self.algorithm_mode.get(), "appearance_mode": self.appearance_mode_str.get(), "ui_scaling": self.ui_scaling_str.get(),
                "cluster_threshold": self.cluster_time_threshold.get(), "auto_play_cluster": self.auto_play_cluster_audio.get(),
                "midi_out_device": self.current_midi_device_str.get(), "default_playback_speed": self.default_playback_speed.get(),
                "show_minimap": self.show_minimap.get(), "performance_mode": self.performance_mode.get(), "highlight_active_notes": self.highlight_active_notes.get(),
                "default_theme": self.default_theme_str.get(), "canvas_fps": self.canvas_fps.get(), "volume_floor": self.volume_floor.get(),
                "volume_boost": self.volume_boost.get(), "auto_scroll_text": self.auto_scroll_text.get(), "wire_level_0_ms": self.wire_level_0_ms.get(),
                "polyphony_limit": self.polyphony_limit.get(), "auto_transpose": self.auto_transpose.get(), "remove_ghost_notes": self.remove_ghost_notes.get(),
                "he_so_toc_do": self.he_so_toc_do.get(), "ui_card_width": self.ui_card_width.get(), "show_wire_label": self.show_wire_label.get(),
                "drum_boost_factor": self.drum_boost_factor.get(), "enable_note_off": self.enable_note_off.get()
            }
            with open(CONFIG_FILE, 'w') as f: json.dump(config_data, f, indent=4)
        except: pass

    def on_closing(self):
        self.is_playing = False; self.save_app_config()
        if self.midi_out:
            try:
                for chan in range(16): self.midi_out.write_short(0b10110000 | chan, 123, 0)
                self.midi_out.close()
            except: pass
        try:
            if pygame.midi.get_init(): pygame.midi.quit()
        except: pass
        self.destroy()

    def setup_input_screen(self):
        self.frame_input   = ctk.CTkFrame(self)
        self.lbl_title     = ctk.CTkLabel(self.frame_input, text="Chọn file MIDI", font=ctk.CTkFont(size=32, weight="bold"))
        self.lbl_file      = ctk.CTkLabel(self.frame_input, text="Chưa chọn file nào", text_color="gray", font=ctk.CTkFont(size=18))
        self.btn_select    = ctk.CTkButton(self.frame_input, text="📁 Chọn File", width=250, height=50, font=ctk.CTkFont(size=18), command=self.select_file)
        self.lbl_signature = ctk.CTkLabel(self.frame_input, text="ft.LKL", font=ctk.CTkFont(size=12, slant="italic"), text_color="gray50")
        
        self.frame_input.pack(fill="both", expand=True, padx=20, pady=20)
        self.lbl_title.pack(pady=(250, 10))
        self.lbl_file.pack(pady=(0, 20))
        self.btn_select.pack(pady=10)
        self.lbl_signature.pack(side="bottom", pady=10)

    def setup_mapping_screen(self):
        self.frame_mapping = ctk.CTkFrame(self)
        self.lbl_map_title = ctk.CTkLabel(self.frame_mapping, text="CẤU HÌNH NHẠC CỤ", font=ctk.CTkFont(size=28, weight="bold"))
        
        search_frame       = ctk.CTkFrame(self.frame_mapping, fg_color="transparent")
        self.map_search_entry = ctk.CTkEntry(search_frame, placeholder_text="🔍 Tìm kiếm nhạc cụ...")
        self.map_search_entry.bind("<KeyRelease>", self._filter_mapping_list)
        
        self.map_scroll    = ctk.CTkScrollableFrame(self.frame_mapping, width=600, height=400)
        map_actions_frame  = ctk.CTkFrame(self.frame_mapping, fg_color="transparent")
        
        self.btn_load_map  = ctk.CTkButton(map_actions_frame, text="Tải Cấu Hình", command=self.load_mapping_config, fg_color=COLOR_SECONDARY, hover_color=COLOR_SECONDARY_HOVER)
        self.btn_save_map  = ctk.CTkButton(map_actions_frame, text="Lưu Cấu Hình", command=self.save_mapping_config, fg_color=COLOR_INFO, hover_color=COLOR_INFO_HOVER)

        simplify_frame     = ctk.CTkFrame(self.frame_mapping, fg_color="transparent")
        s_frame_inner      = ctk.CTkFrame(simplify_frame)
        self.simplify_enabled_var  = ctk.BooleanVar(value=False)
        self.simplify_time_var     = ctk.StringVar(value="50")
        self.simplify_velocity_var = ctk.StringVar(value="20")
        
        self.btn_start_convert = ctk.CTkButton(self.frame_mapping, text="⚡ Bắt Đầu Chuyển Đổi", width=250, height=50, font=ctk.CTkFont(size=18, weight="bold"), command=self.process_mapping_and_convert, fg_color=COLOR_SUCCESS, hover_color=COLOR_SUCCESS_HOVER)
        self.mapping_comboboxes = []

        self.lbl_map_title.pack(pady=(30, 20))
        search_frame.pack(fill="x", padx=10, pady=(0, 5))
        self.map_search_entry.pack(fill="x", padx=10, pady=5)
        self.map_scroll.pack(pady=10, padx=10, fill="y", expand=True)
        
        map_actions_frame.pack(pady=(10, 10))
        self.btn_load_map.pack(side="left", padx=10)
        self.btn_save_map.pack(side="left", padx=10)
        
        simplify_frame.pack(pady=(10, 0), padx=10, fill='x')
        s_frame_inner.pack()
        ctk.CTkCheckBox(s_frame_inner, text="Đơn giản hóa:", variable=self.simplify_enabled_var).pack(side='left', padx=10, pady=10)
        ctk.CTkLabel(s_frame_inner, text="Bỏ nốt nhanh hơn (ms):").pack(side='left', padx=(10,0))
        ctk.CTkEntry(s_frame_inner, textvariable=self.simplify_time_var, width=50).pack(side='left', padx=(5,10))
        ctk.CTkLabel(s_frame_inner, text="Bỏ nốt có velocity <").pack(side='left', padx=(10,0))
        ctk.CTkEntry(s_frame_inner, textvariable=self.simplify_velocity_var, width=50).pack(side='left', padx=5, pady=10)
        
        self.btn_start_convert.pack(pady=(10, 30))

    def setup_output_screen(self):
        self.frame_output = ctk.CTkFrame(self)
        
        self.top_bar        = ctk.CTkFrame(self.frame_output, fg_color="transparent")
        self.btn_back       = ctk.CTkButton(self.top_bar, text="← Tệp", width=100, corner_radius=8, fg_color=COLOR_BG_MAIN, hover_color="#3a3a3a", cursor="hand2", command=self.back_to_input)
        self.btn_export_txt = ctk.CTkButton(self.top_bar, text="Xuất Sơ đồ Dọc (.txt)", width=200, command=self.export_vertical_to_txt)
        
        self.lbl_now_playing= ctk.CTkLabel(self.top_bar, text="", font=ctk.CTkFont(weight="bold", size=20), text_color=self.get_current_color(COLOR_ACCENT_1))
        self.btn_settings   = ctk.CTkButton(self.top_bar, text="⚙️", width=30, command=self.open_settings)
        self.btn_help       = ctk.CTkButton(self.top_bar, text="?", width=30, command=self.show_help)
        
        self.top_bar.pack(fill="x", padx=10, pady=5)
        self.btn_back.configure(fg_color=self.get_current_color(COLOR_BG_MAIN), hover_color=self.get_current_color(COLOR_BG_FRAME)); self.btn_back.pack(side="left")
        self.btn_export_txt.pack(side="left", padx=(10, 0))
        self.lbl_now_playing.pack(side="left", fill="x", expand=True)
        self.btn_help.pack(side="right", padx=(0, 10))
        self.btn_settings.pack(side="right", padx=(0, 5))

        self.sheet_panel    = ctk.CTkFrame(self.frame_output, height=60)
        self.lbl_sheet      = ctk.CTkLabel(self.sheet_panel, text="Hiển thị Bản vẽ:", font=ctk.CTkFont(weight="bold", size=15), text_color=self.get_current_color(COLOR_ACCENT_1))
        self.btn_select_all = ctk.CTkButton(self.sheet_panel, text="Chọn Tất Cả", width=100, fg_color=self.get_current_color(COLOR_INFO), hover_color=self.get_current_color(COLOR_INFO_HOVER), command=self.select_all_sheets)
        self.btn_clear_all  = ctk.CTkButton(self.sheet_panel, text="Bỏ Chọn", width=90, fg_color=self.get_current_color(COLOR_SECONDARY), hover_color=self.get_current_color(COLOR_SECONDARY_HOVER), command=self.clear_all_sheets)
        self.sheet_checkboxes_frame = ctk.CTkScrollableFrame(self.sheet_panel, orientation="horizontal", height=45, fg_color="transparent")
        
        self.sheet_panel.pack(fill="x", padx=10, pady=5)
        self.lbl_sheet.pack(side="left", padx=15, pady=10)
        self.btn_select_all.pack(side="left", padx=5)
        self.btn_clear_all.pack(side="left", padx=5)
        self.sheet_checkboxes_frame.pack(side="left", fill="x", expand=True, padx=10)

        self.tabview    = ctk.CTkTabview(self.frame_output, command=self.on_tab_change)
        self.tab_vert   = self.tabview.add("Sơ đồ Dọc")
        self.tab_horz   = self.tabview.add("Sơ đồ Ngang")
        self.tab_step   = self.tabview.add("Sơ đồ Đơn")
        self.tab_stats  = self.tabview.add("Thống kê")
        self.tabview.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.txt_vert = ctk.CTkTextbox(self.tab_vert, font=ctk.CTkFont(family="Consolas", size=16), wrap="none", cursor="hand2")
        self.txt_vert.pack(fill="both", expand=True, padx=5, pady=5)
        self.txt_vert.tag_config("active_line", background="#12505a", foreground="white")
        self.txt_vert.bind("<Button-1>", self.on_txt_vert_click)
        self.txt_vert.bind("<Double-Button-1>", self.on_txt_vert_double_click)
        
        self.canvas_frame     = ctk.CTkFrame(self.tab_horz)
        self.canvas           = ctk.CTkCanvas(self.canvas_frame, bg=self.get_current_color(COLOR_BG_FRAME), highlightthickness=0)
        self.minimap_canvas   = ctk.CTkCanvas(self.canvas_frame, height=50, bg=self.get_current_color(COLOR_BG_SECTION), highlightthickness=0)
        self.minimap_viewport = self.minimap_canvas.create_rectangle(0,0,0,0, outline="red")
        self.scrollbar_x      = ctk.CTkScrollbar(self.canvas_frame, orientation="horizontal")
        
        self.canvas_frame.pack(fill="both", expand=True)
        self.canvas.pack(side="top", fill="both", expand=True)
        self.scrollbar_x.pack(side="bottom", fill="x")
        if self.show_minimap.get(): 
            self.minimap_canvas.pack(side="bottom", fill="x", before=self.scrollbar_x)
        self.canvas.bind("<MouseWheel>", lambda e: self.canvas.xview_scroll(int(-1 * (e.delta / 120)), "units"))
        
        self.frame_step             = ctk.CTkFrame(self.tab_step, corner_radius=10)
        self.frame_step_header      = ctk.CTkFrame(self.frame_step, fg_color="transparent")
        self.lbl_step_num           = ctk.CTkLabel(self.frame_step_header, text="[ CỤM 000 ]", font=ctk.CTkFont(size=36, weight="bold"), text_color=COLOR_ACCENT_1)
        self.frame_step_instruments = ctk.CTkFrame(self.frame_step, fg_color="transparent")
        self.lbl_step_wire          = ctk.CTkLabel(self.frame_step, text="➔ Dây: ...", font=ctk.CTkFont(size=30, weight="bold"), text_color=self.get_current_color(COLOR_ACCENT_2))
        
        self.frame_step.pack(fill="both", expand=True, padx=20, pady=20)
        self.frame_step_header.pack(fill="x", pady=(20, 10))
        self.lbl_step_num.pack()
        self.frame_step_instruments.pack(expand=True, fill="both", padx=20)
        self.lbl_step_wire.pack(pady=(10, 30))

        self.pool_frames = []
        for _ in range(20):
            cf = ctk.CTkFrame(self.frame_step_instruments, fg_color="transparent")
            lbl_title = ctk.CTkLabel(cf, font=ctk.CTkFont(size=22, weight="bold"))
            note_lbls = [ctk.CTkLabel(cf, font=ctk.CTkFont(size=18, weight="bold")) for _ in range(20)]
            self.pool_frames.append((cf, lbl_title, note_lbls))

        self.stats_scroll_frame = ctk.CTkScrollableFrame(self.tab_stats, label_text="Phân Tích Chi Tiết Bản Nhạc")
        self.stats_scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.music_panel  = ctk.CTkFrame(self.frame_output, height=90)
        self.btn_reset    = ctk.CTkButton(self.music_panel, text="⏮", width=50, corner_radius=10, fg_color=self.get_current_color(COLOR_SECONDARY), hover_color=self.get_current_color(COLOR_SECONDARY_HOVER), command=self.jump_to_start)
        self.btn_prev     = ctk.CTkButton(self.music_panel, text="◀◀", width=50, corner_radius=10, command=lambda: self.manual_change_step(-1))
        self.btn_play     = ctk.CTkButton(self.music_panel, text="▶ Phát", width=140, corner_radius=12, fg_color=self.get_current_color(COLOR_SUCCESS), hover_color=self.get_current_color(COLOR_SUCCESS_HOVER), font=ctk.CTkFont(weight="bold", size=18), command=self.toggle_play)
        self.btn_next     = ctk.CTkButton(self.music_panel, text="▶▶", width=50, corner_radius=10, command=lambda: self.manual_change_step(1))
        self.mode_switch  = ctk.CTkSegmentedButton(self.music_panel, values=["🎵 Nhạc MIDI Gốc", "🎹 Mini World"], command=self.change_preview_mode)
        self.combo_speed  = ctk.CTkComboBox(self.music_panel, values=["0.5x", "0.75x", "1.0x", "1.25x", "1.5x"], width=90, command=self.change_speed)
        self.btn_decrease = ctk.CTkButton(self.music_panel, text="⇩", width=40, corner_radius=10, fg_color=COLOR_DANGER, command=self.decrease_pitch)
        self.lbl_pitch    = ctk.CTkLabel(self.music_panel, text="Pitch: 0", width=70, font=ctk.CTkFont(size=14, family="Consolas"))
        self.btn_increase = ctk.CTkButton(self.music_panel, text="⇧", width=40, corner_radius=10, fg_color=COLOR_INFO, command=self.increase_pitch)
        self.lbl_time     = ctk.CTkLabel(self.music_panel, text="00:00.00 / 00:00.00", width=150, font=ctk.CTkFont(family="Consolas", size=14))
        self.slider_time  = ctk.CTkSlider(self.music_panel, from_=0, to=100, command=self.on_slider_seek)
        
        self.music_panel.pack(fill="x", padx=10, pady=(0, 10))
        self.btn_reset.pack(side="left", padx=(20, 5), pady=20)
        self.btn_prev.pack(side="left", padx=5, pady=20)
        self.btn_play.pack(side="left", padx=5, pady=20)
        self.btn_next.pack(side="left", padx=5, pady=20)
        self.mode_switch.set("🎵 Nhạc MIDI Gốc"); self.mode_switch.pack(side="left", padx=20, pady=20)
        self.combo_speed.set(self.default_playback_speed.get()); self.combo_speed.pack(side="left", padx=5, pady=20)
        self.btn_decrease.pack(side="left", padx=(10, 0), pady=20)
        self.lbl_pitch.pack(side="left", padx=5, pady=20)
        self.btn_increase.pack(side="left", padx=(0, 15), pady=20)
        self.lbl_time.pack(side="right", padx=(0, 20), pady=20)
        self.slider_time.set(0); self.slider_time.pack(side="left", fill="x", expand=True, padx=(10, 0), pady=20)

    def select_file(self):
        p = self.show_dialog(filedialog.askopenfilename, filetypes=[("MIDI", "*.mid *.midi")], initialdir=self.last_directory)
        if p: self.file_path = p; self.last_directory = os.path.dirname(p); self.lbl_file.configure(text=os.path.basename(p)); self.scan_midi_channels()

    def _filter_mapping_list(self, e=None):
        t = self.map_search_entry.get().lower()
        for i in self.mapping_comboboxes:
            rf = i['frame']
            if t in rf.winfo_children()[0].cget("text").lower():
                if not rf.winfo_ismapped(): rf.pack(fill="x", pady=i['pady'], padx=i['padx'])
            elif rf.winfo_ismapped(): rf.pack_forget()

    def scan_midi_channels(self):
        try:
            uc, ud, cp = self.processor.scan_channels(self.file_path)
            for w in self.map_scroll.winfo_children(): w.destroy()
            self.mapping_comboboxes.clear()
            osyn = ["Bỏ qua (Mute)"] + [f"🎹 Tổng hợp: {k} (Gõ {v})" for k, v in MW_SYNTH.items()]
            oelc = [f"⚡ Điện tử: {k} (Gõ {v})" for k, v in MW_ELECTRONIC.items()]
            odrm = ["Bỏ qua (Mute)"] + [f"🥁 Trống: {k} (Gõ {v})" for k, v in MW_DRUMS.items()]
            for ch in uc:
                f = ctk.CTkFrame(self.map_scroll); f.pack(fill="x", pady=5, padx=10)
                pr = cp[ch]
                dn = f"🎹 {GM_INSTRUMENTS[pr]}" if 0 <= pr < len(GM_INSTRUMENTS) else f"🎹 Nhạc cụ (Prog {pr})"
                ctk.CTkLabel(f, text=f"Ch {ch+1}: {dn}", width=250, anchor="w", font=ctk.CTkFont(weight="bold"), text_color=self.get_current_color(COLOR_ACCENT_1)).pack(side="left", padx=10, pady=10)
                cb = ctk.CTkComboBox(f, values=osyn + oelc, width=300)
                pn = dn.lower()
                if "bass" in pn and "drum" not in pn: cb.set("⚡ Điện tử: Guitar Bass Điện (Gõ 0)")
                elif "harpsichord" in pn or "clav" in pn: cb.set("⚡ Điện tử: Harpsichord (Gõ 7)")
                elif any(x in pn for x in ["bell","glockenspiel","celesta","music box","vibraphone","xylophone","tubular"]): cb.set("⚡ Điện tử: Chuông Điện Tử (Gõ 5)")
                elif "square" in pn or "calliope" in pn: cb.set("⚡ Điện tử: Stylophone (Gõ 3)")
                elif any(x in pn for x in ["synth","pad","lead","charang"]): cb.set("⚡ Điện tử: Pluck Synth (Gõ 1)")
                elif "guitar" in pn: cb.set("🎹 Tổng hợp: Guitar Mộc (Gõ 7)" if "nylon" in pn or "steel" in pn or "acoustic" in pn else "🎹 Tổng hợp: Guitar (Gõ 1)")
                elif "violin" in pn or "string" in pn: cb.set("🎹 Tổng hợp: Violin (Gõ 3)")
                elif "harp" in pn: cb.set("🎹 Tổng hợp: Harp (Gõ 2)")
                elif "trumpet" in pn or "brass" in pn: cb.set("🎹 Tổng hợp: Trumpet (Gõ 4)")
                elif "flute" in pn or "recorder" in pn: cb.set("🎹 Tổng hợp: Recorder (Gõ 5)")
                else: cb.set("🎹 Tổng hợp: Piano (Gõ 0)")
                cb.pack(side="right", padx=10, pady=10); self.mapping_comboboxes.append({'channel': ch, 'is_drum': False, 'drum_note': None, 'combo': cb, 'frame': f, 'pady': 5, 'padx': 10})
            if ud:
                ctk.CTkLabel(self.map_scroll, text="--- CHI TIẾT BỘ TRỐNG (Kênh 10) ---", text_color=self.get_current_color(COLOR_ACCENT_2), font=ctk.CTkFont(weight="bold")).pack(pady=(15, 5))
                for nt in ud:
                    f = ctk.CTkFrame(self.map_scroll); f.pack(fill="x", pady=2, padx=10) 
                    ctk.CTkLabel(f, text=f"🥁 Nốt {nt}: {GM_DRUM_MAP.get(nt, 'Unknown')}", width=250, anchor="w", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10, pady=10)
                    cb = ctk.CTkComboBox(f, values=odrm, width=300)
                    if self.active_drum_map.get(nt):
                        for o in odrm:
                            if self.active_drum_map.get(nt) in o: cb.set(o); break
                    cb.pack(side="right", padx=10, pady=10); self.mapping_comboboxes.append({'channel': 9, 'is_drum': True, 'drum_note': nt, 'combo': cb, 'frame': f, 'pady': 2, 'padx': 10})
            self.frame_input.pack_forget(); self.frame_mapping.pack(fill="both", expand=True, padx=20, pady=20)
        except Exception as e: self.show_dialog(messagebox.showerror, "Lỗi", f"Lỗi quét MIDI:\n{e}")

    def save_mapping_config(self):
        if not self.mapping_comboboxes: return self.show_dialog(messagebox.showwarning, "Cảnh báo", "Không có cấu hình để lưu.")
        d = [{'id': f"drum_{i['drum_note']}" if i['is_drum'] else f"ch_{i['channel']}", 'value': i['combo'].get()} for i in self.mapping_comboboxes]
        p = self.show_dialog(filedialog.asksaveasfilename, defaultextension=".json", filetypes=[("JSON", "*.json")], title="Lưu", initialfile="my_mapping_config.json")
        if p:
            with open(p, 'w', encoding='utf-8') as f: json.dump(d, f, indent=4)
            self.show_dialog(messagebox.showinfo, "Thành công", f"Đã lưu: {p}")

    def load_mapping_config(self):
        if not self.mapping_comboboxes: return self.show_dialog(messagebox.showwarning, "Cảnh báo", "Vui lòng quét MIDI trước.")
        p = self.show_dialog(filedialog.askopenfilename, filetypes=[("JSON", "*.json")], title="Tải", initialdir=self.last_directory)
        if p:
            with open(p, 'r', encoding='utf-8') as f: cm = {i['id']: i['value'] for i in json.load(f)}
            for i in self.mapping_comboboxes:
                kid = f"drum_{i['drum_note']}" if i['is_drum'] else f"ch_{i['channel']}"
                if kid in cm and cm[kid] in i['combo'].cget('values'): i['combo'].set(cm[kid])

    def process_mapping_and_convert(self):
        self.transpose_semitones = 0; self.lbl_pitch.configure(text="Pitch: 0")
        self.mw_channel_programs.clear(); self.channel_map = {}
        for i in self.mapping_comboboxes:
            v = i['combo'].get()
            if "Bỏ qua" in v: continue
            k = f"9_{i['drum_note']}" if i['is_drum'] else f"{i['channel']}_ALL"
            n_full = v.split(":")[1].strip(); lst_p = n_full.rfind('('); nm = n_full[:lst_p].strip(); tap = int(n_full[lst_p:].split("Gõ")[1].replace(")", "").strip())
            dnm = f"🥁 {nm} ({tap})" if i['is_drum'] else f"{'🎹' if 'Tổng hợp' in v else '⚡'} {nm} ({tap})"
            self.channel_map[k] = {"type": "Drum" if i['is_drum'] else "Synth", "name": nm, "tap": tap, "display_name": dnm}
        opts = {'enabled': self.simplify_enabled_var.get(), 'time_ms': int(self.simplify_time_var.get() or 0), 'velocity': int(self.simplify_velocity_var.get() or 0)}
        self.frame_mapping.pack_forget(); self.lbl_now_playing.configure(text="Đang xử lý...")
        threading.Thread(target=self._build_initial_data_thread, args=(opts,), daemon=True).start()

    def _build_initial_data_thread(self, opts):
        try:
            self.original_notes, self.full_midi_events, self.midi_metadata = self.processor.build_note_list(self.file_path, self.channel_map, opts)
            self.midi_event_times = np.array([e[0] for e in self.full_midi_events], dtype=np.float64)
            if not self.original_notes: return self.after(0, lambda: self.show_dialog(messagebox.showerror, "Lỗi", "Không tìm thấy nốt."))
            self.after(0, self.render_gui_initial)
        except Exception as e: self.after(0, lambda: self.show_dialog(messagebox.showerror, "Lỗi", f"Không xử lý được:\n{e}"))

    def update_active_blueprint(self):
        was_p = self.is_playing
        if was_p: self.playback_offset = self.start_offset + (time.perf_counter() - self.start_perf) * 1000.0 * self.playback_speed; self.is_playing = False
        
        cache_key = (frozenset(self.selected_instruments), self.transpose_semitones)
        with self.cache_lock:
            cached_bp = self.blueprint_cache.get(cache_key)

        if cached_bp is not None:
            self.active_blueprint = cached_bp
        else:
            self.active_blueprint = self.generator.create_blueprint(
                self.original_notes, self.channel_map, self.selected_instruments, 
                self.transpose_semitones, self.mw_drum_to_gm_note, 
                self.algorithm_mode.get(), self.cupy, self.cluster_time_threshold.get(),
                self.he_so_toc_do.get(), self.wire_level_0_ms.get(), self.polyphony_limit.get()
            )
            with self.cache_lock:
                self.blueprint_cache[cache_key] = self.active_blueprint
                if len(self.blueprint_cache) > 5:
                    oldest_key = next(iter(self.blueprint_cache))
                    del self.blueprint_cache[oldest_key]

        self.blueprint_synctimes = np.array([m['sync_time'] for m in self.active_blueprint])
        self.render_active_sheet()
        self.sync_playback_indices()
        self._last_highlight_idx = None
        self.apply_sync_visuals()

        self._is_stats_loaded = False
        if hasattr(self, 'tabview') and self.tabview.get() == "Thống kê":
            self._load_stats_now()
        if was_p: self.start_offset = self.playback_offset; self.start_perf = time.perf_counter(); self.is_playing = True; threading.Thread(target=self._audio_playback_thread, daemon=True).start()

    def render_gui_initial(self):
        self.lbl_now_playing.configure(text=os.path.basename(self.file_path)); self.frame_output.pack(fill="both", expand=True, padx=10, pady=10)
        for w in self.sheet_checkboxes_frame.winfo_children(): w.destroy()
        self.checkbox_vars.clear(); self.available_instruments = sorted(list(set(v["display_name"] for v in self.channel_map.values()))); self.selected_instruments = set(self.available_instruments)
        for i in self.available_instruments:
            v = ctk.BooleanVar(value=True); self.checkbox_vars[i] = v
            c = ctk.CTkCheckBox(self.sheet_checkboxes_frame, text=i, variable=v, font=ctk.CTkFont(weight="bold"), command=lambda n=i: self.on_checkbox_change(n))
            c.pack(side="left", padx=10, pady=5)
        self.slider_time.configure(to=(self.original_notes[-1]['time'] if self.original_notes else 0) + 1000)
        self.update_active_blueprint(); self.jump_to_start(); self.canvas.configure(xscrollcommand=self._on_canvas_scrolled); self.scrollbar_x.configure(command=self._on_horizontal_scroll)
        self.start_precaching_thread()

    def start_precaching_thread(self):
        threading.Thread(target=self._precache_blueprints, daemon=True).start()

    def _precache_blueprints(self):
        time.sleep(1) 
        current_pitch = self.transpose_semitones
        all_instruments = frozenset(self.available_instruments)
        if not all_instruments: return

        for pitch in (current_pitch - 1, current_pitch + 1):
            cache_key = (all_instruments, pitch)
            with self.cache_lock:
                if cache_key in self.blueprint_cache: continue
            
            blueprint = self.generator.create_blueprint(
                self.original_notes, self.channel_map, self.selected_instruments, 
                self.transpose_semitones, self.mw_drum_to_gm_note, 
                self.algorithm_mode.get(), self.cupy, self.cluster_time_threshold.get(),
                self.he_so_toc_do.get(), self.wire_level_0_ms.get(), self.polyphony_limit.get()
            )
            with self.cache_lock: 
                self.blueprint_cache[cache_key] = blueprint
                if len(self.blueprint_cache) > 5:
                    oldest_key = next(iter(self.blueprint_cache))
                    del self.blueprint_cache[oldest_key]
            time.sleep(0.5)

    def on_tab_change(self):
        t = self.tabview.get()
        if t == "Sơ đồ Ngang": 
            self._draw_minimap(); self._update_minimap_viewport()
        elif t == "Sơ đồ Dọc":
            self._load_vert_text_now()
        elif t == "Thống kê":
            self._load_stats_now()

    def _load_stats_now(self):
        if not getattr(self, '_is_stats_loaded', False):
            old_text = self.lbl_now_playing.cget("text")
            self.lbl_now_playing.configure(text="Đang vẽ biểu đồ thống kê...")
            self.update_idletasks() 
            self.update_stats_tab() 
            self._is_stats_loaded = True
            self.lbl_now_playing.configure(text=old_text)

    def _load_vert_text_now(self):
        if not getattr(self, '_is_vert_text_loaded', False) and getattr(self, 'active_blueprint', None):
            old_text = self.lbl_now_playing.cget("text")
            self.lbl_now_playing.configure(text="Đang kết xuất Sơ đồ Dọc...")
            self.update_idletasks() 
            
            bp = self.active_blueprint
            vl, cl = [], 1
            self.txt_vert_line_map.clear()
            
            for m in bp:
                i_s = list(m['instruments'].keys())
                if not i_s: continue
                vl.append(f"[ CỤM {m['id']} ]\n")

                header_parts = []
                col_widths = []
                display_headers = {}
                
                for h_original in i_s:
                    h_new = h_original
                    if '🎹 ' in h_new: h_new = h_new.replace('🎹 ', '[Tổng hợp] ')
                    elif '⚡ ' in h_new: h_new = h_new.replace('⚡ ', '[Điện tử] ')
                    elif '🥁 ' in h_new: h_new = h_new.replace('🥁 ', '[Trống] ')
                    
                    display_headers[h_original] = h_new
                    col_widths.append(max(len(h_new) + 2, 18))
                
                for idx, h_original in enumerate(i_s):
                    header_parts.append(f'{display_headers[h_original]:^{col_widths[idx]}}')
                
                vl.append(f"|{'|'.join(header_parts)}|\n")
                
                mr = max(len(d['notes_raw_data']) for d in m['instruments'].values())
                for r in range(mr): 
                    row_parts = []
                    for idx, i in enumerate(i_s):
                        if r < len(m["instruments"][i]["notes_raw_data"]):
                            b_id, n_mod = m["instruments"][i]["notes_raw_data"][r]
                            txt = self._decode_note_str(b_id, n_mod)
                        else:
                            txt = "" 
                        row_parts.append(f'{txt:^{col_widths[idx]}}')
                    vl.append(f"|{'|'.join(row_parts)}|\n")
                
                total_w = sum(col_widths) + len(i_s) + 1
                vl.append("-" * total_w + "\n")
                vl.append(f"➔ Dây tiếp: {m['wire']}\n\n")
                
                self.txt_vert_line_map.append((cl, cl + mr + 3)); cl += mr + 5
                
            self._cached_vert_text = "".join(vl)
            
            self.txt_vert.configure(state="normal")
            self.txt_vert.insert("1.0", self._cached_vert_text)
            self.txt_vert.configure(state="disabled")
            self._is_vert_text_loaded = True
            
            idx = getattr(self, 'current_step_index', 0)
            if idx < len(self.txt_vert_line_map):
                sl, el = self.txt_vert_line_map[idx]
                self.txt_vert.tag_remove("active_line", "1.0", "end")
                self.txt_vert.tag_add("active_line", f"{sl}.0", f"{el}.end")
                self.txt_vert.see(f"{el}.end"); self.txt_vert.see(f"{sl}.0")
                
            self.lbl_now_playing.configure(text=old_text)

    def on_checkbox_change(self, i): self.selected_instruments.add(i) if self.checkbox_vars[i].get() else self.selected_instruments.discard(i); self.update_active_blueprint()
    def select_all_sheets(self): [v.set(True) for v in self.checkbox_vars.values()]; self.selected_instruments = set(self.checkbox_vars.keys()); self.update_active_blueprint()
    def clear_all_sheets(self): [v.set(False) for v in self.checkbox_vars.values()]; self.selected_instruments.clear(); self.update_active_blueprint()

    def render_active_sheet(self):
        bp = self.active_blueprint
        
        self._is_vert_text_loaded = False
        self._cached_vert_text = ""
        self.txt_vert_line_map = []
        self.txt_vert.configure(state="normal")
        self.txt_vert.delete("1.0", "end")
        self.txt_vert.configure(state="disabled")

        if getattr(self, 'tabview', None) and self.tabview.get() == "Sơ đồ Dọc":
            self._load_vert_text_now()

        self.canvas.delete("all")
        if not hasattr(self, 'drawn_clusters'): self.drawn_clusters = {}
        self.drawn_clusters.clear()
        
        if not bp: return
        self._last_drawn_start = -1
        self._last_drawn_end = -1
        try: fh = max(200, self.canvas_frame.winfo_height())
        except: fh = 700
        
        self.cluster_heights = [
            max(120, 65 + sum(30 + math.ceil(len(d['notes_raw_data']) * 0.4) * 22 for d in m['instruments'].values()) + 10) 
            for m in bp
        ]

        total_width = len(bp) * (self.card_width + 80)
        self.canvas.configure(scrollregion=(0, 0, total_width, fh))
        ly = fh // 2
        self.canvas.create_line(0, ly, total_width, ly, fill="#333333", width=8)
        
        self._update_virtual_canvas()
        self._draw_minimap()
        self._update_minimap_viewport()

    def _update_virtual_canvas(self):
        if not self.active_blueprint: return
        try: fh = max(200, self.canvas.winfo_height())
        except: fh = 700
        ly, card_step = fh // 2, self.card_width + 80

        x0 = self.canvas.canvasx(0)
        x1 = self.canvas.canvasx(self.canvas.winfo_width())

        start_idx = max(0, int(x0 // card_step) - 1)
        end_idx = min(len(self.active_blueprint), int(x1 // card_step) + 2)

        if getattr(self, '_last_drawn_start', -1) == start_idx and getattr(self, '_last_drawn_end', -1) == end_idx:
            return 
            
        self._last_drawn_start = start_idx
        self._last_drawn_end = end_idx

        for idx in list(self.drawn_clusters.keys()):
            if idx < start_idx or idx >= end_idx:
                for item_id in self.drawn_clusters[idx]['items']: self.canvas.delete(item_id)
                del self.drawn_clusters[idx]

        def bd(id_c, idx): self.canvas.tag_bind(id_c, "<Button-1>", lambda e, i=idx: self.on_item_click(idx=i))
        def bh(rid, idx):
            self.canvas.tag_bind(rid, "<Enter>", lambda e: self.canvas.itemconfig(rid, outline="#00e5ff") if idx != getattr(self, '_last_highlight_idx', -1) else None)
            self.canvas.tag_bind(rid, "<Leave>", lambda e: self.canvas.itemconfig(rid, outline="#555555") if idx != getattr(self, '_last_highlight_idx', -1) else None)

        for i in range(start_idx, end_idx):
            if i in self.drawn_clusters: continue 

            m, ch = self.active_blueprint[i], self.cluster_heights[i]
            xo, by = i * card_step + 40, int(ly - (ch // 2) - 20)
            items = []
            text_color = "white" if ctk.get_appearance_mode() == "Dark" else "black"
            rid = self.canvas.create_rectangle(xo, by, xo + self.card_width, by + ch, fill=self.get_current_color(COLOR_BG_FRAME), outline=self.get_current_color(COLOR_SECONDARY), width=2)
            tid = self.canvas.create_text(xo + self.card_width//2, by + 20, text=f"CỤM {m['id']}", fill=text_color, font=("Arial", 16, "bold"))
            items.extend([rid, tid]); bd(rid, i); bd(tid, i)
            self.canvas.tag_bind(rid, "<Double-Button-1>", lambda e, idx=i: self.jump_to_step(idx, auto_play_note=True)); bh(rid, i)

            yt = by + 45
            for ins, d in m['instruments'].items():
                iid = self.canvas.create_text(xo + 15, yt, text=ins, fill=self.get_current_color(self.color_synth) if "🎹" in ins else self.get_current_color(self.color_drum), font=("Arial", 13, "bold"), anchor="w")
                items.append(iid); bd(iid, i); yt += 20
                n_str = ", ".join([self._decode_note_str(b, n) for b, n in d['notes_raw_data']])
                nid = self.canvas.create_text(xo + 25, yt, text=n_str, fill=self.get_current_color(COLOR_SECONDARY), font=("Arial", 11), anchor="nw", width=self.card_width-40)
                items.append(nid); bd(nid, i); yt += math.ceil(len(n_str) / 35) * 20 + 10

            if i < len(self.active_blueprint) - 1:
                lid = self.canvas.create_line(xo + self.card_width, ly, xo + self.card_width + 80, ly, fill="#ffc107", width=6, arrow="last", arrowshape=(16, 20, 6))
                wid = self.canvas.create_text(xo + self.card_width + 40, ly - 20, text=m['wire'], fill="#ffc107", font=("Arial", 15, "bold"))
                items.extend([lid, wid])

            if i == getattr(self, 'current_step_index', -1) and i == getattr(self, '_last_highlight_idx', -1) and not self.performance_mode.get() and self.highlight_active_notes.get(): 
                self.canvas.itemconfig(rid, fill="#12505a", outline="#00e5ff", width=4)

            self.drawn_clusters[i] = {'bg': rid, 'items': items}

    def _draw_minimap(self):
        self.minimap_canvas.delete("all")
        if not self.active_blueprint: return
        
        self.minimap_canvas.update_idletasks()
        cw = self.minimap_canvas.winfo_width()
        tw = len(self.active_blueprint) * (self.card_width + 80)
        
        if tw == 0 or cw <= 1: return
        sc = cw / tw
        
        pixel_map = set()
        for i in range(len(self.active_blueprint)):
            px = int(i * (self.card_width + 80) * sc)
            pixel_map.add(px) 
            
        for px in pixel_map:
            self.minimap_canvas.create_line(px, 5, px, 45, fill=self.get_current_color(COLOR_SECONDARY))
            
        self.minimap_viewport = self.minimap_canvas.create_rectangle(0, 2, 0, 48, outline=self.get_current_color(self.color_accent_1), width=2)
        
        self.minimap_canvas.bind("<Button-1>", self._on_minimap_click_drag)
        self.minimap_canvas.bind("<B1-Motion>", self._on_minimap_click_drag)

    def _update_minimap_viewport(self):
        sf, ef = self.canvas.xview(); mw = self.minimap_canvas.winfo_width()
        self.minimap_canvas.coords(self.minimap_viewport, sf * mw, 2, ef * mw, 48)

    def _execute_note_off(self):
        with self.preview_lock:
            if self.has_midi_output:
                for note, channel in self.preview_notes_on:
                    try: self.midi_out.note_off(note, 0, channel)
                    except: pass
            self.preview_notes_on.clear()
            self.preview_note_off_timer = None

    def play_mixed_instruments(self, inst_dict):
        with self.preview_lock:
            if self.preview_note_off_timer:
                self.preview_note_off_timer.cancel()
                self.preview_note_off_timer = None

            if self.has_midi_output:
                for note, channel in self.preview_notes_on:
                    try: self.midi_out.note_off(note, 0, channel)
                    except: pass
            self.preview_notes_on.clear()

            if not self.has_midi_output or not inst_dict: return

            is_mw_mode = (self.current_preview_mode == "🎹 Mini World")
            for i_nm, d in inst_dict.items():
                for n_info in d['notes']:
                    n = n_info.get('og_midi', n_info['midi']); ch = n_info['channel']; prog = n_info.get('program', 0); vel = n_info.get('velocity', 100)
                    boost_factor = 1.3 if is_mw_mode else 1.15; vel = min(127, int(vel * boost_factor))
                    bn = d.get('name')
                    if not bn: continue
                    if is_mw_mode:
                        self.midi_out.write_short(0b10110000 | ch, 91, 127) 
                        self.midi_out.write_short(0b10110000 | ch, 7, 127)  
                    if d.get("type", "Synth") == "Drum" or ch == 9:
                        play_note = n_info['midi'] if is_mw_mode else n_info['og_midi']
                        self.midi_out.note_on(play_note, vel, 9); self.preview_notes_on.append((play_note, 9))
                    else:
                        target_prog = self.mw_instrument_to_gm.get(bn, 0) if is_mw_mode else prog
                        if self.mw_channel_programs.get(ch) != target_prog: 
                            self.midi_out.set_instrument(target_prog, ch); self.mw_channel_programs[ch] = target_prog
                        play_note = n
                        if is_mw_mode:
                            while play_note < 48: play_note += 12
                            while play_note > 83: play_note -= 12
                        self.midi_out.note_on(play_note, vel, ch); self.preview_notes_on.append((play_note, ch))
            if self.preview_notes_on:
                self.preview_note_off_timer = threading.Timer(0.2, self._execute_note_off)
                self.preview_note_off_timer.daemon = True
                self.preview_note_off_timer.start()

    def on_item_click(self, e=None, idx=None):
        if idx is not None:
            self.jump_to_step(idx, auto_play_note=self.auto_play_cluster_audio.get())

    def on_txt_vert_click(self, e):
        ic = int(self.txt_vert.index(f"@{e.x},{e.y}").split('.')[0])
        for i, (sl, el) in enumerate(self.txt_vert_line_map):
            if sl <= ic <= el: self.on_item_click(idx=i); break

    def on_txt_vert_double_click(self, e):
        ic = int(self.txt_vert.index(f"@{e.x},{e.y}").split('.')[0])
        for i, (sl, el) in enumerate(self.txt_vert_line_map):
            if sl <= ic <= el: self.jump_to_step(i, auto_play_note=True); break

    def jump_to_step(self, idx, auto_play_note=False):
        bp = self.active_blueprint
        if idx < 0 or idx >= len(bp): return
        was_p = self.is_playing; self.is_playing = False; self.current_step_index = idx; self.playback_offset = bp[idx]['sync_time']
        self._update_time_display(self.playback_offset); self.slider_time.set(self.playback_offset)
        self.sync_playback_indices(); self._resync_midi_output(); self.apply_sync_visuals()
        if auto_play_note: self.play_mixed_instruments(bp[idx]['instruments'])
        if was_p: self.start_offset = self.playback_offset; self.start_perf = time.perf_counter(); self.is_playing = True; threading.Thread(target=self._audio_playback_thread, daemon=True).start()
        else: self.is_paused = False 

    def manual_change_step(self, dir): self.jump_to_step(self.current_step_index + dir, auto_play_note=True)
    def jump_to_start(self): self.jump_to_step(0)

    def toggle_play(self):
        if self.is_playing:
            self.playback_offset = self.start_offset + (time.perf_counter() - self.start_perf) * 1000.0 * self.playback_speed
            
            self.is_playing = False; self.is_paused = True; self.btn_play.configure(text="▶ Phát")
            if self.has_midi_output: [self.midi_out.write_short(0b10110000 | c, 123, 0) for c in range(16)]
        else:
            self.start_offset = self.playback_offset; self.start_perf = time.perf_counter(); self.is_playing = True; self.is_paused = False
            self.btn_play.configure(text="⏸ Tạm Dừng"); threading.Thread(target=self._audio_playback_thread, daemon=True).start(); self._ui_update_loop()

    def on_slider_seek(self, val):
        was_p = self.is_playing; self.is_playing = False; self.playback_offset = float(val); self._update_time_display(self.playback_offset); self.sync_playback_indices(); self._resync_midi_output()
        c_idx = 0
        if self.blueprint_synctimes.size > 0:
            idx = np.searchsorted(self.blueprint_synctimes, self.playback_offset)
            if idx == 0: c_idx = 0
            elif idx >= len(self.blueprint_synctimes): c_idx = len(self.blueprint_synctimes) - 1
            else:
                before = self.blueprint_synctimes[idx - 1]
                after = self.blueprint_synctimes[idx]
                c_idx = idx - 1 if (self.playback_offset - before) < (after - self.playback_offset) else idx

        self.current_step_index = c_idx; self.apply_sync_visuals()
        if was_p: self.start_offset = self.playback_offset; self.start_perf = time.perf_counter(); self.is_playing = True; threading.Thread(target=self._audio_playback_thread, daemon=True).start()
        else: self.is_paused = False

    def _resync_midi_output(self):
        if not self.has_midi_output: return
        [self.midi_out.write_short(0b10110000 | c, 123, 0) for c in range(16)]
        is_mw_mode = self.current_preview_mode == "🎹 Mini World"

        ch_state = {c: {'prog': 0, 'vol': 100, 'expr': 127, 'rev': 40} for c in range(16)}
        stop_idx = self.next_midi_event_idx
        for i in range(stop_idx):
            e = self.full_midi_events[i]; om = e[1]
            if om.type == 'program_change': ch_state[om.channel]['prog'] = om.program
            elif om.type == 'control_change':
                if om.control == 7: ch_state[om.channel]['vol'] = om.value
                elif om.control == 11: ch_state[om.channel]['expr'] = om.value
                elif om.control == 91: ch_state[om.channel]['rev'] = om.value

        vf, vb = self.volume_floor.get(), self.volume_boost.get()
        ign_rev = getattr(self, 'ignore_reverb', ctk.BooleanVar(value=False)).get()

        for ch in range(16):
            if is_mw_mode:
                vol = max(vf + 30, min(127, int(ch_state[ch]['vol'] * vb))) if ch_state[ch]['vol'] > 0 else 0
                expr = max(vf + 30, min(127, int(ch_state[ch]['expr'] * vb))) if ch_state[ch]['expr'] > 0 else 0
                self.midi_out.write_short(0b10110000 | ch, 7, vol)
                self.midi_out.write_short(0b10110000 | ch, 11, expr)
                self.midi_out.write_short(0b10110000 | ch, 91, 0 if ign_rev else 127)
            else:
                self.midi_out.write_short(0b11000000 | ch, ch_state[ch]['prog'], 0)
                vol = max(vf, min(127, int(ch_state[ch]['vol'] * (vb - 0.2)))) if ch_state[ch]['vol'] > 0 else 0
                expr = max(vf, min(127, int(ch_state[ch]['expr'] * (vb - 0.2)))) if ch_state[ch]['expr'] > 0 else 0
                self.midi_out.write_short(0b10110000 | ch, 7, vol)
                self.midi_out.write_short(0b10110000 | ch, 11, expr)
                self.midi_out.write_short(0b10110000 | ch, 91, 0 if ign_rev else ch_state[ch]['rev'])
            
            self.midi_out.write_short(0b11100000 | ch, 0, 64)

    def sync_playback_indices(self):
        if hasattr(self, 'midi_event_times') and self.midi_event_times.size > 0:
            self.next_midi_event_idx = np.searchsorted(self.midi_event_times, self.playback_offset)
        else:
            self.next_midi_event_idx = 0
            
        if self.blueprint_synctimes.size > 0:
            self.next_mw_idx = np.searchsorted(self.blueprint_synctimes, self.playback_offset)
        else:
            self.next_mw_idx = 0

    def _audio_playback_thread(self):
        bp = self.active_blueprint
        while self.is_playing:
            c_ms = self.start_offset + (time.perf_counter() - self.start_perf) * 1000.0 * self.playback_speed
            
            while self.next_mw_idx < len(bp) and bp[self.next_mw_idx]['sync_time'] <= c_ms:
                self.current_step_index = self.next_mw_idx; self.next_mw_idx += 1
                
            while self.next_midi_event_idx < len(self.full_midi_events) and self.full_midi_events[self.next_midi_event_idx][0] <= c_ms:
                if self.has_midi_output:
                    e = self.full_midi_events[self.next_midi_event_idx]; om = e[1]; is_mw_mode = (self.current_preview_mode == "🎹 Mini World")
                    if om.type in ('note_on', 'note_off'):
                        map_key = f"9_{om.note}" if om.channel == 9 else f"{om.channel}_ALL"
                        if map_key in self.channel_map:
                            minfo = self.channel_map[map_key]
                            if minfo["display_name"] in self.selected_instruments:
                                try:
                                    vel = om.velocity if om.type == 'note_on' else 0
                                    
                                    if vel == 0 and not getattr(self, 'enable_note_off', ctk.BooleanVar(value=True)).get():
                                        raise Exception("SkipNoteOff") 
                                        
                                    if getattr(self, 'auto_normalize_velocity', ctk.BooleanVar(value=False)).get() and vel > 0: 
                                        vel = 100
                                        
                                    if is_mw_mode:
                                        if om.channel == 9:
                                            play_note = self.mw_drum_to_gm_note.get(minfo['name'], 60)
                                            if vel > 0: 
                                                boost = getattr(self, 'drum_boost_factor', self.volume_boost).get()
                                                vel = max(self.volume_floor.get(), min(127, int(vel * boost)))
                                            self.midi_out.write_short(om.bytes()[0], play_note, vel)
                                            
                                        else:
                                            nt = om.note + self.transpose_semitones
                                            while nt < 48: nt += 12
                                            while nt > 83: nt -= 12
                                            
                                            if vel > 0:
                                                mw_prog = self.mw_instrument_to_gm.get(minfo['name'], 0)
                                                if self.mw_channel_programs.get(om.channel) != mw_prog:
                                                    self.midi_out.set_instrument(mw_prog, om.channel)
                                                    self.mw_channel_programs[om.channel] = mw_prog
                                                    self.midi_out.write_short(0b10110000 | om.channel, 91, 127)
                                                    self.midi_out.write_short(0b10110000 | om.channel, 7, 127)
                                                vel = max(self.volume_floor.get(), min(127, int(vel * self.volume_boost.get())))
                                            
                                            self.midi_out.write_short(om.bytes()[0], nt, vel)
                                            
                                    else: 
                                        if vel > 0: 
                                            vel = max(self.volume_floor.get() - 20, min(127, int(vel * (self.volume_boost.get() - 0.2))))
                                        nt = om.note + self.transpose_semitones if om.channel != 9 else om.note
                                        if 0 <= nt <= 127: self.midi_out.write_short(om.bytes()[0], nt, vel)
                                except Exception: pass 
                    elif om.type in ['program_change', 'control_change', 'pitchwheel']:
                        try:
                            if is_mw_mode and om.type == 'program_change': raise Exception("Skip")
                            b = om.bytes()
                            if om.type == 'control_change':
                                if b[1] in (7, 11): 
                                    val = b[2]
                                    if val > 0:
                                        if is_mw_mode: val = max(self.volume_floor.get() + 30, min(127, int(val * self.volume_boost.get()))) 
                                        else: val = max(self.volume_floor.get(), min(127, int(val * (self.volume_boost.get() - 0.2))))
                                    b = (b[0], b[1], val)
                                elif b[1] == 91:
                                    if getattr(self, 'ignore_reverb', ctk.BooleanVar(value=False)).get(): raise Exception("Skip")
                                    b = (b[0], b[1], max(100, b[2])) 
                            self.midi_out.write_short(b[0], b[1] if len(b)>1 else 0, b[2] if len(b)>2 else 0)
                        except: pass
                self.next_midi_event_idx += 1
                
            if self.next_mw_idx >= len(bp) and self.next_midi_event_idx >= len(self.full_midi_events):
                if self.has_midi_output: self._resync_midi_output()
                self.is_playing = False; self.after(0, lambda: self.btn_play.configure(text="▶ Phát")); break
            time.sleep(0.002)

    def _ui_update_loop(self):
        if self.is_playing:
            cms = self.start_offset + (time.perf_counter() - self.start_perf) * 1000.0 * self.playback_speed
            try: self.slider_time.set(cms)
            except: pass
            self._update_time_display(cms); self.apply_sync_visuals(); self.after(self.canvas_fps.get(), self._ui_update_loop)

    def apply_sync_visuals(self):
        bp, idx = self.active_blueprint, self.current_step_index
        if idx < 0 or idx >= len(bp) or getattr(self, '_last_highlight_idx', None) == idx: return
        self._last_highlight_idx = idx; d = bp[idx]
        
        self.lbl_step_num.configure(text=f"[ CỤM {d['id']} ]")
        self.lbl_step_wire.configure(text=f"➔ Dây tiếp: {d['wire']}")
        
        for cf, _, _ in self.pool_frames: cf.pack_forget()
        
        for i, (ins, ind) in enumerate(d['instruments'].items()):
            if i >= len(self.pool_frames): break
            cf, lbl_title, note_lbls = self.pool_frames[i]
            cf.pack(side="left", expand=True, fill="both", padx=10) 
            
            lbl_title.configure(text=ins, text_color=self.color_synth if "🎹" in ins else self.color_drum)
            lbl_title.pack(pady=(5, 10))
            
            for nl in note_lbls: nl.pack_forget()
            
            for j, (b_id, n_mod) in enumerate(ind['notes_raw_data']):
                if j < len(note_lbls):
                    note_lbls[j].configure(text=self._decode_note_str(b_id, n_mod))
                    note_lbls[j].pack(pady=3)

        if getattr(self, '_is_vert_text_loaded', False) and idx < len(self.txt_vert_line_map):
                try:
                    sl, el = self.txt_vert_line_map[idx]
                    self.txt_vert.tag_remove("active_line", "1.0", "end")
                    self.txt_vert.tag_add("active_line", f"{sl}.0", f"{el}.end")
                    if self.auto_scroll_text.get(): 
                        self.txt_vert.see(f"{el}.end"); self.txt_vert.see(f"{sl}.0")
                except: pass
        
        if hasattr(self, 'drawn_clusters') and not self.performance_mode.get() and self.highlight_active_notes.get():
            for idx_drawn, ci in self.drawn_clusters.items(): 
                is_active = (idx_drawn == idx)
                self.canvas.itemconfig(ci['bg'], fill="#12505a" if is_active else "#242424", outline="#00e5ff" if is_active else "#555555")

        if len(bp) > 0:
            target_x = (idx * (self.card_width + 80)) + (self.card_width / 2) - (self.canvas.winfo_width() / 2)
            max_x = len(bp) * (self.card_width + 80)
            try: 
                self.canvas.xview_moveto(max(0, min(1, target_x / max_x)))
                if hasattr(self, '_update_virtual_canvas'): self._update_virtual_canvas() 
            except: pass

    def update_stats_tab(self):
        bp = self.active_blueprint
        for w in self.stats_scroll_frame.winfo_children(): w.destroy()
        if not bp: return ctk.CTkLabel(self.stats_scroll_frame, text="Không có dữ liệu.", font=ctk.CTkFont(size=16), text_color=self.get_current_color(COLOR_SECONDARY)).pack(pady=20)
        def ae(p, l, v): f=ctk.CTkFrame(p, fg_color="transparent"); f.pack(fill="x", pady=2, padx=20); ctk.CTkLabel(f, text=l, anchor="w").pack(side="left"); ctk.CTkLabel(f, text=str(v), anchor="e", font=ctk.CTkFont(weight="bold")).pack(side="right")
        def a_s(p, t): f=ctk.CTkFrame(p, fg_color=COLOR_BG_SECTION); f.pack(fill="x", pady=(10, 5), padx=5); ctk.CTkLabel(f, text=t, font=ctk.CTkFont(size=18, weight="bold"), text_color=COLOR_ACCENT_1).pack(pady=5, padx=10, anchor="w"); return f
        tot_c, tm = len(bp), bp[-1]['sync_time'] if bp else 0
        min, sec = divmod(tm / 1000, 60); b_ts = f"{int(min):02d}:{sec:05.2f}"
        t_n, i_n_c, w_c = 0, {n: 0 for n in self.selected_instruments}, {"Mức 0":0,"Mức 1":0,"Mức 2":0,"Mức 3":0,"Mức 4":0,"Mức 5":0,"PL":0,"Sát nhau":0}
        
        cluster_stats = []
        max_inst_count, max_inst_cluster_id = 0, ""

        for m in bp:
            c_notes = 0
            for n, d in m['instruments'].items(): 
                t_n += len(d['notes'])
                i_n_c[n] = i_n_c.get(n, 0) + len(d['notes'])
                c_notes += len(d['notes']) 
            
            inst_count = len(m['instruments'])
            if inst_count > max_inst_count:
                max_inst_count = inst_count
                max_inst_cluster_id = m['id']
                
            cluster_stats.append({'id': m['id'], 'note_count': c_notes, 'inst_count': inst_count})
            
            if m['wire'] != '[HẾT BÀI]':
                for pt in [p.strip() for p in m.get('wire', '').split('+')]:
                    if "Sát nhau" in pt: w_c["Sát nhau"] += 1
                    elif "PL" in pt: w_c["PL"] += 1
                    elif "Mức" in pt:
                        tk = pt.split(' ')
                        if len(tk) >= 2 and tk[0] == 'Mức': w_c[f"Mức {tk[1]}"] += 1
                        elif len(tk) >= 3: w_c[f"Mức {tk[2]}"] = w_c.get(f"Mức {tk[2]}", 0) + int(tk[0])

        cluster_stats.sort(key=lambda x: x['note_count'], reverse=True)
        top_10_note_clusters = cluster_stats[:10]
        max_notes = top_10_note_clusters[0]['note_count'] if top_10_note_clusters else 0
        max_notes_cluster_id = top_10_note_clusters[0]['id'] if top_10_note_clusters else "N/A"

        cluster_stats.sort(key=lambda x: x['inst_count'], reverse=True) 
        top_10_inst_clusters = cluster_stats[:10]

        s_ov = a_s(self.stats_scroll_frame, "📈 Tổng Quan") 
        ae(s_ov, "Tổng số cụm:", f"{tot_c} cụm")
        ae(s_ov, "Tổng số nốt nhạc:", f"{t_n} nốt")
        ae(s_ov, "Tổng thời gian:", b_ts)
        
        note_container = ctk.CTkFrame(s_ov, fg_color="transparent")
        note_container.pack(fill="x", pady=0, padx=0)
        note_stats_frame = ctk.CTkFrame(note_container, fg_color="transparent") 
        note_stats_frame.pack(fill="x", pady=2, padx=20)
        ctk.CTkLabel(note_stats_frame, text="Số nốt cao nhất / 1 cụm:", anchor="w").pack(side="left")

        ctk.CTkLabel(note_stats_frame, text=f"{max_notes} nốt (Cụm {max_notes_cluster_id})", anchor="e", font=ctk.CTkFont(weight="bold")).pack(side="right")
        self.btn_toggle_notes = ctk.CTkButton(note_stats_frame, text="▶", width=28, height=24, command=self._toggle_top_10_notes_list, fg_color="transparent", hover_color=self.get_current_color(COLOR_BG_FRAME), text_color=self.get_current_color(self.color_accent_1))
        self.btn_toggle_notes.pack(side="right", padx=(0, 5))
        self.top_10_notes_list_frame = ctk.CTkFrame(note_container, fg_color="transparent")
        self._render_top_10_list(self.top_10_notes_list_frame, top_10_note_clusters, "note_count", "nốt")

        inst_container = ctk.CTkFrame(s_ov, fg_color="transparent")
        inst_container.pack(fill="x", pady=0, padx=0)
        inst_stats_frame = ctk.CTkFrame(inst_container, fg_color="transparent") 
        inst_stats_frame.pack(fill="x", pady=2, padx=20)
        ctk.CTkLabel(inst_stats_frame, text="Nhiều loại nhạc cụ nhất:", anchor="w").pack(side="left")

        ctk.CTkLabel(inst_stats_frame, text=f"{max_inst_count} loại (Cụm {max_inst_cluster_id})", anchor="e", font=ctk.CTkFont(weight="bold")).pack(side="right") 
        self.btn_toggle_inst = ctk.CTkButton(inst_stats_frame, text="▶", width=28, height=24, command=self._toggle_top_10_inst_list, fg_color="transparent", hover_color=self.get_current_color(COLOR_BG_FRAME), text_color=self.get_current_color(self.color_accent_1))
        self.btn_toggle_inst.pack(side="right", padx=(0, 5))
        self.top_10_inst_list_frame = ctk.CTkFrame(inst_container, fg_color="transparent")
        self._render_top_10_list(self.top_10_inst_list_frame, top_10_inst_clusters, "inst_count", "loại")

        s_w  = a_s(self.stats_scroll_frame, "🔌 Thống Kê Dây Nối") 
        for lvl in range(5, -1, -1): ae(s_w, f"Tổng số Mức {lvl}:", f"{w_c.get(f'Mức {lvl}', 0)} dây")
        ae(s_w, "Tổng số dây 1 PL:", f"{w_c['PL']} dây"); ae(s_w, "Tổng số dây 'Sát nhau':", f"{w_c['Sát nhau']} dây")
        pf = ctk.CTkFrame(s_w, fg_color="transparent", height=300); pf.pack(fill="x", expand=True, pady=10, padx=5); self.generate_wire_pie_chart(pf, w_c)
        s_ins = a_s(self.stats_scroll_frame, "🎼 Thống Kê Nhạc Cụ") 
        inst_f = ctk.CTkFrame(s_ins, fg_color="transparent", height=300); inst_f.pack(fill="x", expand=True, pady=10, padx=5); self.generate_instrument_bar_chart(inst_f, i_n_c)
        
        for inm, c in sorted(i_n_c.items(), key=lambda x: x[1], reverse=True): 
            if c > 0: ae(s_ins, f"{inm}:", f"{c} nốt")
    
    def _render_top_10_list(self, parent_frame, data, metric_key, metric_unit):
        for w in parent_frame.winfo_children(): w.destroy() 
        if not data:
            ctk.CTkLabel(parent_frame, text="Không có dữ liệu.", text_color=self.get_current_color(COLOR_SECONDARY)).pack(pady=5)
            return
        for i, c in enumerate(data):
            f = ctk.CTkFrame(parent_frame, fg_color="transparent")
            f.pack(fill="x", padx=5, pady=2)
            ctk.CTkLabel(f, text=f"#{i+1} - Cụm {c['id']}", font=ctk.CTkFont(weight="bold")).pack(side="left")
            ctk.CTkLabel(f, text=f"{c[metric_key]} {metric_unit}", font=ctk.CTkFont(weight="bold")).pack(side="right")
            btn_jump = ctk.CTkButton(f, text="Đến", width=50, height=24, command=lambda idx=int(c['id'])-1: self.jump_to_step(idx, auto_play_note=True))
            btn_jump.pack(side="right", padx=(10, 0))

    def _toggle_top_10_notes_list(self):
        if self.top_10_notes_expanded.get():
            self.top_10_notes_list_frame.pack_forget()
            if self.btn_toggle_notes: self.btn_toggle_notes.configure(text="▶", text_color=self.get_current_color(self.color_accent_1))
        else:
            self.top_10_notes_list_frame.pack(fill="x", padx=20, pady=(0, 10))
            if self.btn_toggle_notes: self.btn_toggle_notes.configure(text="▼", text_color=self.get_current_color(self.color_accent_1))
        self.top_10_notes_expanded.set(not self.top_10_notes_expanded.get())

    def _toggle_top_10_inst_list(self):
        if self.top_10_inst_expanded.get():
            self.top_10_inst_list_frame.pack_forget()
            if self.btn_toggle_inst: self.btn_toggle_inst.configure(text="▶", text_color=self.get_current_color(self.color_accent_1))
        else:
            self.top_10_inst_list_frame.pack(fill="x", padx=20, pady=(0, 10))
            if self.btn_toggle_inst: self.btn_toggle_inst.configure(text="▼", text_color=self.get_current_color(self.color_accent_1))
        self.top_10_inst_expanded.set(not self.top_10_inst_expanded.get())

    def _update_time_display(self, c_ms):
        if not hasattr(self, 'lbl_time') or not self.lbl_time: return
        t_ms = self.slider_time.cget("to")
        if t_ms <= 0: t_ms = self.original_notes[-1]['time'] if self.original_notes else 0
        def fms(m): min, sec = divmod(max(0, m) / 1000, 60); return f"{int(min):02d}:{sec:05.2f}"
        self.lbl_time.configure(text=f"{fms(c_ms)} / {fms(t_ms)}")

    def export_vertical_to_txt(self):
        if not self.active_blueprint: return self.show_dialog(messagebox.showwarning, "Cảnh báo", "Không có sơ đồ để xuất.")
        p = self.show_dialog(filedialog.asksaveasfilename, defaultextension=".txt", filetypes=[("Text", "*.txt")], title="Lưu Sơ Đồ Dọc", initialfile=f"Sơ đồ - {os.path.basename(self.file_path or 'Untitled')}.txt")
        if p:
            try:
                with open(p, "w", encoding="utf-8") as f: f.write(self.txt_vert.get("1.0", "end"))
                self.show_dialog(messagebox.showinfo, "Thành công", f"Đã xuất: {p}")
            except Exception as e: self.show_dialog(messagebox.showerror, "Lỗi", str(e))

    def change_preview_mode(self, m): self.current_preview_mode = m; self.mw_channel_programs.clear(); self._resync_midi_output()
    def change_speed(self, c, fl=False):
        ns = float(c.replace("x", ""))
        if ns == self.playback_speed and not fl: return
        was_p = self.is_playing
        if was_p: self.playback_offset = self.start_offset + (time.perf_counter() - self.start_perf) * 1000.0 * self.playback_speed; self.is_playing = False
        self.playback_speed = ns
        if was_p: self.start_offset = self.playback_offset; self.start_perf = time.perf_counter(); self.is_playing = True; threading.Thread(target=self._audio_playback_thread, daemon=True).start(); self._ui_update_loop()
    
    def back_to_input(self):
        self.is_playing = False; self.is_paused = False
        if self.midi_out: [self.midi_out.write_short(0b10110000 | c, 123, 0) for c in range(16)]
        
        import gc
        with self.cache_lock:
            self.blueprint_cache.clear()
        self.active_blueprint = []
        self.original_notes = []
        self.full_midi_events = []
        
        if hasattr(self, 'midi_event_times'): self.midi_event_times = np.array([])
        if hasattr(self, 'drawn_clusters'): self.drawn_clusters.clear()
        self._last_drawn_start = -1
        self.canvas.delete("all")
        
        gc.collect() 
        
        if self.has_gpu and self.cupy:
            try:
                self.cupy.get_default_memory_pool().free_all_blocks()
                self.cupy.get_default_pinned_memory_pool().free_all_blocks()
            except: pass

        self.frame_output.pack_forget(); self.frame_mapping.pack_forget(); self.frame_input.pack(fill="both", expand=True, padx=20, pady=20)
    
    def increase_pitch(self): self.apply_transpose(1)
    def decrease_pitch(self): self.apply_transpose(-1)
    def apply_transpose(self, s):
        if not self.original_notes: return
        self.transpose_semitones += s
        if hasattr(self, 'lbl_pitch'): self.lbl_pitch.configure(text=f"Pitch: {self.transpose_semitones:+d}")
        self.update_active_blueprint()
    
    def open_settings(self):
        if not hasattr(self, 'settings_window') or not self.settings_window.winfo_exists(): 
            self.settings_window = SettingsWindow(self)
        else:
            self.settings_window.deiconify()
        self.settings_window.focus()

    def toggle_always_on_top(self):
        self.attributes('-topmost', self.always_on_top.get())
        if hasattr(self, 'settings_window') and self.settings_window.winfo_exists():
            self.settings_window.attributes('-topmost', self.always_on_top.get())
        if hasattr(self, 'drum_kit_window') and self.drum_kit_window.winfo_exists():
            self.drum_kit_window.attributes('-topmost', self.always_on_top.get())

    def _create_default_drum_map(self):
        m = {}
        for nt in range(35, 82):
            if nt in [35, 36]: m[nt] = "Bass"
            elif nt in [37, 38, 39, 40]: m[nt] = "Lẫy"
            elif nt in [41, 43]: m[nt] = "Floor tom"
            elif nt in [45, 47, 48, 50, 65, 66]: m[nt] = "Tom-tom"
            elif nt in [42, 44, 46]: m[nt] = "Hi-hat (đóng)"
            elif nt in [49, 52, 55, 57]: m[nt] = "Chũm choẹ to"
            elif nt in [51, 53, 59]: m[nt] = "Chũm choẹ trung"
            else: m[nt] = "Jam-block"
        return m

    def _apply_theme(self, t, first_load=False):
        self.current_theme_name = t
        if t == "Vàng Gold":
            self.color_accent_1 = ("#B38600", "#ffc107") 
            self.color_synth = ("#B37A00", "#ffb300") 
            self.color_drum = ("#C7507A", "#f06292") 
            self.color_info = ("#B38600", "#ffb300") 
            self.color_info_hover = ("#A17900", "#e6a100") 
        elif t == "Hồng Ruby":
            self.color_accent_1 = ("#A31545", "#e91e63") 
            self.color_synth = ("#D33A6D", "#ec407a") 
            self.color_drum = ("#8C3A99", "#ab47bc") 
            self.color_info = ("#D33A6D", "#ec407a") 
            self.color_info_hover = ("#BF3463", "#d43a6f") 
        else: 
            self.color_accent_1 = ("#008C99", "#00e5ff") 
            self.color_synth = ("#107A8B", "#17a2b8") 
            self.color_drum = ("#B8326F", "#e83e8c") 
            self.color_info = ("#107A8B", "#17a2b8") 
            self.color_info_hover = ("#0D6A7A", "#138496") 
        if not first_load:
            self.lbl_step_num.configure(text_color=self.get_current_color(self.color_accent_1))
            self.btn_select_all.configure(fg_color=self.get_current_color(self.color_info), hover_color=self.get_current_color(self.color_info_hover))
            self.btn_increase.configure(fg_color=self.get_current_color(self.color_info))
            if self.active_blueprint:
                self._is_stats_loaded = False
                self.render_active_sheet()
                self.apply_sync_visuals()
                if self.tabview.get() == "Thống kê":
                    self._load_stats_now()
        self.default_theme_str.set(t)

    def generate_wire_pie_chart(self, p, wc):
        for w in p.winfo_children(): w.destroy()
        lbls, szs = [], []
        for k, v in wc.items():
            if v > 0: lbls.append(k); szs.append(v)
        if not szs: return ctk.CTkLabel(p, text="Không có dữ liệu.", text_color=self.get_current_color(COLOR_SECONDARY)).pack(pady=20)
        try:
            mode = ctk.get_appearance_mode()
            bg_color = self.get_current_color(COLOR_BG_MAIN)
            text_color = "white" if mode == "Dark" else "black"
            legend_bg = "#343638" if ctk.get_appearance_mode() == "Dark" else "#E5E5E5"
            fg = Figure(figsize=(5, 4), dpi=100); fg.patch.set_facecolor(bg_color); ax = fg.add_subplot(111)
            ex = [0.1 if i == szs.index(max(szs)) else 0 for i in range(len(szs))]
            ws, _, at = ax.pie(szs, explode=ex, labels=None, autopct='%1.1f%%', shadow=False, startangle=140, pctdistance=0.85, wedgeprops={'edgecolor': 'white'})
            for t in at: t.set_color(text_color); t.set_fontsize(10); t.set_fontweight('bold') 
            ax.axis('equal'); ax.legend(ws, lbls, title="Loại Dây", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1), facecolor=legend_bg, labelcolor=text_color, edgecolor='gray')
            fg.suptitle('Tỷ Lệ Các Loại Dây Nối', color=text_color, fontsize=16, fontweight='bold'); fg.tight_layout(rect=[0, 0, 0.75, 1])
            c = FigureCanvasTkAgg(fg, master=p); c.draw(); c.get_tk_widget().pack(side="top", fill="both", expand=True, padx=5, pady=5)
        except Exception as e: ctk.CTkLabel(p, text=f"Lỗi: {e}").pack(pady=20)

    def generate_instrument_bar_chart(self, p, ic):
        for w in p.winfo_children(): w.destroy()
        sc = sorted(ic.items(), key=lambda x: x[1], reverse=False)
        lbls = [x[0].replace("🎹 ", "").replace("🥁 ", "").replace("⚡ ", "") for x in sc if x[1] > 0]
        szs = [x[1] for x in sc if x[1] > 0]
        if not szs: return ctk.CTkLabel(p, text="Không có dữ liệu.", text_color=self.get_current_color(COLOR_SECONDARY)).pack(pady=20)
        try:
            mode = ctk.get_appearance_mode()
            bg_color = self.get_current_color(COLOR_BG_MAIN)
            text_color = "white" if mode == "Dark" else "black"
            bar_color = self.color_synth[0] if mode == "Light" else self.color_synth[1]
            ax_bg_color = self.get_current_color(COLOR_BG_SECTION)
            fg = Figure(figsize=(5, max(4, len(lbls) * 0.4)), dpi=100); fg.patch.set_facecolor(bg_color); ax = fg.add_subplot(111); ax.set_facecolor(ax_bg_color)
            yp = np.arange(len(lbls)); ax.barh(yp, szs, align='center', color=bar_color); ax.set_yticks(yp, labels=lbls); ax.invert_yaxis()
            ax.set_xlabel('Số Lượng Nốt', color=text_color); ax.set_title('Phân Bố Nốt Nhạc', color=text_color, fontweight='bold')
            ax.tick_params(axis='x', colors=text_color); ax.tick_params(axis='y', colors=text_color)
            ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False); ax.spines['bottom'].set_color('gray'); ax.spines['left'].set_color('gray'); fg.tight_layout()
            c = FigureCanvasTkAgg(fg, master=p); c.draw(); c.get_tk_widget().pack(side="top", fill="both", expand=True, padx=5, pady=5)
        except Exception as e: ctk.CTkLabel(p, text=f"Lỗi: {e}").pack(pady=20)

    def _on_canvas_scrolled(self, *args): 
        self.scrollbar_x.set(*args); self._update_minimap_viewport()
        if hasattr(self, '_update_virtual_canvas'): self._update_virtual_canvas()

    def _on_horizontal_scroll(self, *args): 
        self.canvas.xview(*args); self._update_minimap_viewport()
        if hasattr(self, '_update_virtual_canvas'): self._update_virtual_canvas()

    def _on_minimap_click_drag(self, e): 
        self.minimap_canvas.update_idletasks()
        if self.minimap_canvas.winfo_width() > 0: self.canvas.xview_moveto(e.x / self.minimap_canvas.winfo_width())
        self._update_minimap_viewport()
        if hasattr(self, '_update_virtual_canvas'): self._update_virtual_canvas()

    def show_help(self):
        if hasattr(self, 'help_window') and self.help_window.winfo_exists(): return self.help_window.focus()
        hw = ctk.CTkToplevel(self); hw.title("Trợ Giúp"); hw.geometry("700x600"); hw.transient(self); self.help_window = hw
        tb = ctk.CTkTextbox(hw, wrap="word", font=("Arial", 14)); tb.pack(fill="both", expand=True, padx=10, pady=10); tb.insert("1.0", HELP_TEXT); tb.configure(state="disabled")

if __name__ == "__main__":
    try: app = MiniWorldConverterApp(); app.mainloop()
    except Exception as e: print("Ứng dụng dừng với lỗi:", e)