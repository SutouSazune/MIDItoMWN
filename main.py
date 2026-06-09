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

COLOR_BG_MAIN          = "#2B2B2B"
COLOR_BG_FRAME         = "#242424"
COLOR_BG_SECTION       = "#2a2d2e"
COLOR_ACCENT_1         = "#00e5ff"  
COLOR_ACCENT_2         = "#ffc107"  
COLOR_SYNTH            = "#17a2b8"
COLOR_DRUM             = "#e83e8c"
COLOR_SUCCESS          = "#28a745"
COLOR_SUCCESS_HOVER    = "#218838"
COLOR_DANGER           = "#ff6b6b"
COLOR_INFO             = "#17a2b8"
COLOR_INFO_HOVER       = "#138496"
COLOR_SECONDARY        = "#6c757d"
COLOR_SECONDARY_HOVER  = "#5a6268"

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
        mid = mido.MidiFile(file_path); used_ch, used_dr, ch_prog = set(), set(), {i: 0 for i in range(16)}
        for m in mido.merge_tracks(mid.tracks):
            if m.type == 'program_change': ch_prog[m.channel] = m.program
            elif m.type == 'note_on' and m.velocity > 0: used_dr.add(m.note) if m.channel == 9 else used_ch.add(m.channel)
        return sorted(list(used_ch)), sorted(list(used_dr)), ch_prog

    def build_note_list(self, file_path, channel_map, simp_opts):
        mid = mido.MidiFile(file_path); abs_t, tempo, og_notes, evts, progs = 0, 500000, [], [], {i: 0 for i in range(16)}
        meta = {'ticks_per_beat': mid.ticks_per_beat, 'length': mid.length, 'initial_tempo': 500000, 'initial_time_signature': '4/4'}
        f_tmp, f_ts = False, False
        for m in mido.merge_tracks(mid.tracks):
            if not f_tmp and m.type == 'set_tempo': meta['initial_tempo'] = m.tempo; f_tmp = True
            if not f_ts and m.type == 'time_signature': meta['initial_time_signature'] = f"{m.numerator}/{m.denominator}"; f_ts = True
            abs_t += mido.tick2second(m.time, mid.ticks_per_beat, tempo) * 1000
            if not m.is_meta: evts.append({'time': abs_t, 'msg': m})
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
    def create_blueprint(self, og_notes, ch_map, sel_inst, trans_semi, mw_dr_gm):
        tg_notes = [n for n in og_notes if ch_map[n['map_key']]["display_name"] in sel_inst]
        if not tg_notes: return []
        gps, cur_g, bp = [], [0], []
        for i in range(1, len(tg_notes)):
            if tg_notes[i]['time'] - tg_notes[cur_g[-1]]['time'] < CLUSTER_TIME_THRESHOLD: cur_g.append(i)
            else: gps.append(cur_g); cur_g = [i]
        gps.append(cur_g)
        for gi, grp in enumerate(gps):
            t_sync, inst_d = tg_notes[grp[0]]['time'], {}
            for idx in grp:
                n, minfo = tg_notes[idx], ch_map[tg_notes[idx]['map_key']]
                inm = minfo["display_name"]
                if inm not in inst_d: inst_d[inm] = {"notes_raw": [], "notes": [], "type": minfo["type"], "name": minfo["name"]}
                if minfo["type"] == "Drum":
                    inst_d[inm]["notes_raw"].append(f"[Trống] Gõ {minfo['tap']}")
                    inst_d[inm]["notes"].append({'midi': mw_dr_gm.get(minfo['name'], 60), 'channel': 9, 'og_midi': n['note'], 'program': n.get('program', 0), 'velocity': n.get('velocity', 100)})
                else:
                    fn = n['note'] + trans_semi
                    mwn = fn
                    while mwn < 48: mwn += 12
                    while mwn > 83: mwn -= 12
                    b = "Trầm" if mwn <= 59 else "Trung" if mwn <= 71 else "Cao"
                    inst_d[inm]["notes_raw"].append(f"Khối {b}: {mwn % 12}")
                    inst_d[inm]["notes"].append({'midi': fn, 'channel': n['channel'], 'og_midi': fn, 'program': n.get('program', 0), 'velocity': n.get('velocity', 100)})
            for nm in inst_d:
                inst_d[nm]["notes_raw"] = list(dict.fromkeys(inst_d[nm]["notes_raw"]))
                inst_d[nm]["notes"] = list({(d['og_midi'], d['channel']): d for d in inst_d[nm]["notes"]}.values())
            wstr = "[HẾT BÀI]"
            if gi < len(gps) - 1:
                w_ms = max(0, ((tg_notes[gps[gi+1][0]]['time'] - t_sync) * HE_SO_TOC_DO) - 50)
                if w_ms < 30: wstr = "Sát nhau"
                elif w_ms < 100: wstr = "1 PL"
                elif w_ms < MUC0_START_W_MS: wstr = f"Mức {5 - (int(round(w_ms / 150.0)) - 1)}"
                else:
                    pts = [f"{int(w_ms // MUC0_START_W_MS)} Mức 0"] if int(w_ms // MUC0_START_W_MS) > 0 else []
                    rem = w_ms % MUC0_START_W_MS
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
        super().__init__(master); self.transient(master); self.app = master
        self.title("Cài Đặt"); self.geometry("400x300")
        
        ctk.CTkLabel(self, text="Chủ đề màu sắc:", font=ctk.CTkFont(weight="bold")).pack(pady=(20, 5))
        cb_theme = ctk.CTkComboBox(self, values=["Mặc định (Cyan)", "Vàng Gold", "Hồng Ruby"], command=self.app._apply_theme)
        cb_theme.set(self.app.current_theme_name); cb_theme.pack(pady=5)
        
        ctk.CTkLabel(self, text="Nâng cao:", font=ctk.CTkFont(weight="bold")).pack(pady=(30, 5))
        ctk.CTkButton(self, text="Trình Quản Lý Bộ Trống", command=self.open_drum_kit_manager).pack(pady=10)

    def open_drum_kit_manager(self):
        if not hasattr(self, 'drum_kit_window') or not self.drum_kit_window.winfo_exists(): self.drum_kit_window = DrumKitManager(self.app)
        self.drum_kit_window.focus()

class DrumKitManager(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master); self.transient(master); self.app = master
        self.title("Trình Quản Lý Bộ Trống"); self.geometry("700x600"); self.drum_map_combos = {}
        
        top_frm = ctk.CTkFrame(self, fg_color="transparent"); top_frm.pack(fill="x", padx=10, pady=10)
        ctk.CTkButton(top_frm, text="Tải Bộ Trống", command=self.load_kit).pack(side="left", padx=5)
        ctk.CTkButton(top_frm, text="Lưu Bộ Trống", command=self.save_kit).pack(side="left", padx=5)
        ctk.CTkButton(top_frm, text="Áp Dụng", command=self.apply_kit, fg_color=COLOR_SUCCESS).pack(side="right", padx=5)

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
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("Drum Kit JSON", "*.json")], title="Lưu Bộ Trống")
        if path:
            try:
                with open(path, 'w', encoding='utf-8') as f: json.dump({n: c.get() for n, c in self.drum_map_combos.items()}, f, indent=4)
                messagebox.showinfo("Thành công", "Đã lưu bộ trống.", parent=self)
            except Exception as e: messagebox.showerror("Lỗi", f"Không thể lưu file: {e}", parent=self)

    def load_kit(self):
        path = filedialog.askopenfilename(filetypes=[("Drum Kit JSON", "*.json")], title="Tải Bộ Trống")
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f: d = json.load(f)
                for k, v in d.items():
                    if int(k) in self.drum_map_combos: self.drum_map_combos[int(k)].set(v)
                messagebox.showinfo("Thành công", "Đã tải bộ trống.", parent=self)
            except Exception as e: messagebox.showerror("Lỗi", f"Không thể tải file: {e}", parent=self)

    def apply_kit(self):
        self.app.active_drum_map = {n: c.get().split(":")[1].split("(")[0].strip() for n, c in self.drum_map_combos.items()}
        messagebox.showinfo("Hoàn tất", "Đã áp dụng.", parent=self); self.destroy()

# ==============================================================================================
# [ MAIN APPLICATION ]
# ==============================================================================================
class MiniWorldConverterApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.last_directory        = "."
        self.window_geometry       = "1400x950"
        self.load_app_config()
        self.title(APP_TITLE)
        self.geometry(self.window_geometry)
        
        pygame.mixer.pre_init(44100, -16, 2, 1024)
        pygame.init()
        if not pygame.mixer.get_init(): pygame.mixer.init(44100, -16, 2, 1024)
        self.midi_out, self.has_midi_output = None, False
        try:
            pygame.midi.init()
            if pygame.midi.get_count() > 0 and pygame.midi.get_default_output_id() != -1:
                self.midi_out = pygame.midi.Output(pygame.midi.get_default_output_id())
                self.has_midi_output = True
        except: pass
        pygame.mixer.set_num_channels(64)
        self.synth_channel = pygame.mixer.Channel(0)
        self.synth_channel.set_volume(1)

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
        self.playback_speed       = 1.0 
        self.current_step_index   = 0
        self.playback_offset      = 0  
        self.current_preview_mode = "🎵 Nhạc MIDI Gốc"
        self.start_perf, self.start_offset, self.next_orig_idx, self.next_mw_idx = 0, 0, 0, 0
        self.top_10_notes_expanded = ctk.BooleanVar(value=False)
        self.top_10_inst_expanded = ctk.BooleanVar(value=False)
        self.btn_toggle_notes = None
        self.btn_toggle_inst = None
        self.full_midi_events, self.next_midi_event_idx = [], 0
        
        self.canvas_rects         = [] 
        self.txt_vert_line_map    = [] 
        self._last_highlight_idx  = None
        self.card_width           = 320  
        
        self.current_theme_name   = "Mặc định (Cyan)"
        self._apply_theme(self.current_theme_name, first_load=True)

        self.setup_input_screen()
        self.setup_mapping_screen()
        self.setup_output_screen()
        
        self.frame_mapping.pack_forget()
        self.frame_output.pack_forget()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def load_app_config(self):
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    cfg = json.load(f)
                    self.window_geometry = cfg.get("window_geometry", "1400x950")
                    self.last_directory = cfg.get("last_directory", ".") if os.path.isdir(cfg.get("last_directory", ".")) else "."
        except: pass

    def save_app_config(self):
        try:
            with open(CONFIG_FILE, 'w') as f: json.dump({"window_geometry": self.geometry(), "last_directory": self.last_directory}, f, indent=4)
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
        self.lbl_now_playing= ctk.CTkLabel(self.top_bar, text="", font=ctk.CTkFont(weight="bold", size=20))
        self.btn_settings   = ctk.CTkButton(self.top_bar, text="⚙️", width=30, command=self.open_settings)
        self.btn_help       = ctk.CTkButton(self.top_bar, text="?", width=30, command=self.show_help)
        
        self.top_bar.pack(fill="x", padx=10, pady=5)
        self.btn_back.pack(side="left")
        self.btn_export_txt.pack(side="left", padx=(10, 0))
        self.lbl_now_playing.pack(side="left", fill="x", expand=True)
        self.btn_help.pack(side="right", padx=(0, 10))
        self.btn_settings.pack(side="right", padx=(0, 5))

        self.sheet_panel    = ctk.CTkFrame(self.frame_output, height=60)
        self.lbl_sheet      = ctk.CTkLabel(self.sheet_panel, text="Hiển thị Bản vẽ:", font=ctk.CTkFont(weight="bold", size=15))
        self.btn_select_all = ctk.CTkButton(self.sheet_panel, text="Chọn Tất Cả", width=100, fg_color=COLOR_INFO, hover_color=COLOR_INFO_HOVER, command=self.select_all_sheets)
        self.btn_clear_all  = ctk.CTkButton(self.sheet_panel, text="Bỏ Chọn", width=90, fg_color=COLOR_SECONDARY, hover_color=COLOR_SECONDARY_HOVER, command=self.clear_all_sheets)
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
        self.canvas           = ctk.CTkCanvas(self.canvas_frame, bg="#121212", highlightthickness=0)
        self.minimap_canvas   = ctk.CTkCanvas(self.canvas_frame, height=50, bg="#0c0c0c", highlightthickness=0)
        self.minimap_viewport = self.minimap_canvas.create_rectangle(0,0,0,0, outline="red")
        self.scrollbar_x      = ctk.CTkScrollbar(self.canvas_frame, orientation="horizontal")
        
        self.canvas_frame.pack(fill="both", expand=True)
        self.canvas.pack(side="top", fill="both", expand=True)
        self.minimap_canvas.pack(side="bottom", fill="x")
        self.scrollbar_x.pack(side="bottom", fill="x")
        self.canvas.bind("<MouseWheel>", lambda e: self.canvas.xview_scroll(int(-1 * (e.delta / 120)), "units"))
        
        self.frame_step             = ctk.CTkFrame(self.tab_step, corner_radius=10)
        self.frame_step_header      = ctk.CTkFrame(self.frame_step, fg_color="transparent")
        self.lbl_step_num           = ctk.CTkLabel(self.frame_step_header, text="[ CỤM 000 ]", font=ctk.CTkFont(size=36, weight="bold"), text_color=COLOR_ACCENT_1)
        self.frame_step_instruments = ctk.CTkFrame(self.frame_step, fg_color="transparent")
        self.lbl_step_wire          = ctk.CTkLabel(self.frame_step, text="➔ Dây: ...", font=ctk.CTkFont(size=30, weight="bold"), text_color=COLOR_ACCENT_2)
        
        self.frame_step.pack(fill="both", expand=True, padx=20, pady=20)
        self.frame_step_header.pack(fill="x", pady=(20, 10))
        self.lbl_step_num.pack()
        self.frame_step_instruments.pack(expand=True, fill="both", padx=20)
        self.lbl_step_wire.pack(pady=(10, 30))

        # =========================================================================
        # LÕI TỐI ƯU OBJECT POOLING: Khởi tạo sẵn toàn bộ RAM cần dùng ngay từ đầu
        # Không tạo mới, không phá hủy. Giữ app mượt tuyệt đối.
        # =========================================================================
        self.pool_frames = []
        for _ in range(20):
            cf = ctk.CTkFrame(self.frame_step_instruments, fg_color="transparent")
            lbl_title = ctk.CTkLabel(cf, font=ctk.CTkFont(size=22, weight="bold"))
            note_lbls = [ctk.CTkLabel(cf, font=ctk.CTkFont(size=18, weight="bold")) for _ in range(20)]
            self.pool_frames.append((cf, lbl_title, note_lbls))
        # =========================================================================

        self.stats_scroll_frame = ctk.CTkScrollableFrame(self.tab_stats, label_text="Phân Tích Chi Tiết Bản Nhạc")
        self.stats_scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.music_panel  = ctk.CTkFrame(self.frame_output, height=90)
        self.btn_reset    = ctk.CTkButton(self.music_panel, text="⏮", width=50, corner_radius=10, command=self.jump_to_start)
        self.btn_prev     = ctk.CTkButton(self.music_panel, text="◀◀", width=50, corner_radius=10, command=lambda: self.manual_change_step(-1))
        self.btn_play     = ctk.CTkButton(self.music_panel, text="▶ Phát", width=140, corner_radius=12, fg_color=COLOR_SUCCESS, hover_color=COLOR_SUCCESS_HOVER, font=ctk.CTkFont(weight="bold", size=18), command=self.toggle_play)
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
        self.combo_speed.set("1.0x"); self.combo_speed.pack(side="left", padx=5, pady=20)
        self.btn_decrease.pack(side="left", padx=(10, 0), pady=20)
        self.lbl_pitch.pack(side="left", padx=5, pady=20)
        self.btn_increase.pack(side="left", padx=(0, 15), pady=20)
        self.lbl_time.pack(side="right", padx=(0, 20), pady=20)
        self.slider_time.set(0); self.slider_time.pack(side="left", fill="x", expand=True, padx=(10, 0), pady=20)

    def select_file(self):
        p = filedialog.askopenfilename(filetypes=[("MIDI", "*.mid *.midi")], initialdir=self.last_directory)
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
                ctk.CTkLabel(f, text=f"Ch {ch+1}: {dn}", width=250, anchor="w", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10, pady=10)
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
                ctk.CTkLabel(self.map_scroll, text="--- CHI TIẾT BỘ TRỐNG (Kênh 10) ---", text_color=COLOR_ACCENT_2, font=ctk.CTkFont(weight="bold")).pack(pady=(15, 5))
                for nt in ud:
                    f = ctk.CTkFrame(self.map_scroll); f.pack(fill="x", pady=2, padx=10)
                    ctk.CTkLabel(f, text=f"🥁 Nốt {nt}: {GM_DRUM_MAP.get(nt, 'Unknown')}", width=250, anchor="w", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10, pady=10)
                    cb = ctk.CTkComboBox(f, values=odrm, width=300)
                    if self.active_drum_map.get(nt):
                        for o in odrm:
                            if self.active_drum_map.get(nt) in o: cb.set(o); break
                    cb.pack(side="right", padx=10, pady=10); self.mapping_comboboxes.append({'channel': 9, 'is_drum': True, 'drum_note': nt, 'combo': cb, 'frame': f, 'pady': 2, 'padx': 10})
            self.frame_input.pack_forget(); self.frame_mapping.pack(fill="both", expand=True, padx=20, pady=20)
        except Exception as e: messagebox.showerror("Lỗi", f"Lỗi quét MIDI:\n{e}")

    def save_mapping_config(self):
        if not self.mapping_comboboxes: return messagebox.showwarning("Cảnh báo", "Không có cấu hình để lưu.")
        d = [{'id': f"drum_{i['drum_note']}" if i['is_drum'] else f"ch_{i['channel']}", 'value': i['combo'].get()} for i in self.mapping_comboboxes]
        p = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")], title="Lưu", initialfile="my_mapping_config.json")
        if p:
            with open(p, 'w', encoding='utf-8') as f: json.dump(d, f, indent=4)
            messagebox.showinfo("Thành công", f"Đã lưu: {p}")

    def load_mapping_config(self):
        if not self.mapping_comboboxes: return messagebox.showwarning("Cảnh báo", "Vui lòng quét MIDI trước.")
        p = filedialog.askopenfilename(filetypes=[("JSON", "*.json")], title="Tải", initialdir=self.last_directory)
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
            if not self.original_notes: return self.after(0, lambda: messagebox.showerror("Lỗi", "Không tìm thấy nốt."))
            self.after(0, self.render_gui_initial)
        except Exception as e: self.after(0, lambda: messagebox.showerror("Lỗi", f"Không xử lý được:\n{e}"))

    def update_active_blueprint(self):
        was_p = self.is_playing
        if was_p: self.playback_offset = self.start_offset + (time.perf_counter() - self.start_perf) * 1000.0 * self.playback_speed; self.is_playing = False
        
        cache_key = (frozenset(self.selected_instruments), self.transpose_semitones)
        with self.cache_lock:
            cached_bp = self.blueprint_cache.get(cache_key)

        if cached_bp is not None:
            self.active_blueprint = cached_bp
        else:
            self.active_blueprint = self.generator.create_blueprint(self.original_notes, self.channel_map, self.selected_instruments, self.transpose_semitones, self.mw_drum_to_gm_note)
            with self.cache_lock:
                self.blueprint_cache[cache_key] = self.active_blueprint

        self.blueprint_synctimes = np.array([m['sync_time'] for m in self.active_blueprint])
        self.render_active_sheet(); self.update_stats_tab(); self.sync_playback_indices(); self._last_highlight_idx = None; self.apply_sync_visuals()
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

        for pitch in range(current_pitch - 3, current_pitch + 4):
            if pitch == current_pitch: continue
            cache_key = (all_instruments, pitch)
            with self.cache_lock:
                if cache_key in self.blueprint_cache: continue
            
            blueprint = self.generator.create_blueprint(self.original_notes, self.channel_map, all_instruments, pitch, self.mw_drum_to_gm_note)
            with self.cache_lock: self.blueprint_cache.setdefault(cache_key, blueprint)
            time.sleep(0.2)

        if len(all_instruments) > 1 and len(all_instruments) < 25:
            for instrument_to_remove in all_instruments:
                subset_instruments = all_instruments - {instrument_to_remove}
                cache_key = (subset_instruments, current_pitch)
                
                with self.cache_lock:
                    if cache_key in self.blueprint_cache: continue

                blueprint = self.generator.create_blueprint(self.original_notes, self.channel_map, subset_instruments, current_pitch, self.mw_drum_to_gm_note)
                with self.cache_lock: self.blueprint_cache.setdefault(cache_key, blueprint)
                time.sleep(0.2)

    def on_tab_change(self):
        if self.tabview.get() == "Sơ đồ Ngang": self._draw_minimap(); self._update_minimap_viewport()

    def on_checkbox_change(self, i): self.selected_instruments.add(i) if self.checkbox_vars[i].get() else self.selected_instruments.discard(i); self.update_active_blueprint()
    def select_all_sheets(self): [v.set(True) for v in self.checkbox_vars.values()]; self.selected_instruments = set(self.checkbox_vars.keys()); self.update_active_blueprint()
    def clear_all_sheets(self): [v.set(False) for v in self.checkbox_vars.values()]; self.selected_instruments.clear(); self.update_active_blueprint()

    def render_active_sheet(self):
        bp = self.active_blueprint; self.txt_vert.configure(state="normal"); self.txt_vert.delete("1.0", "end"); self.txt_vert_line_map.clear(); vl, cl, cw = [], 1, 26
        for m in bp:
            i_s = list(m['instruments'].keys())
            if not i_s: continue
            vl.append(f"[ CỤM {m['id']} ]\n"); vl.append(f"|{'|'.join([f'{i.replace("🎹 ", "").replace("🥁 ", "").replace("⚡ ", ""):^{cw}}' for i in i_s])}|\n")
            mr = max(len(d['notes_raw']) for d in m['instruments'].values())
            for r in range(mr): vl.append(f"|{'|'.join([f'{m["instruments"][i]["notes_raw"][r] if r < len(m["instruments"][i]["notes_raw"]) else "":^{cw}}' for i in i_s])}|\n")
            vl.append("-" * (len(i_s) * (cw + 1) + 1) + "\n"); vl.append(f"➔ Dây tiếp: {m['wire']}\n\n")
            self.txt_vert_line_map.append((cl, cl + mr + 3)); cl += mr + 5
        self.txt_vert.insert("1.0", "".join(vl)); self.txt_vert.configure(state="disabled")
        
        self.canvas.delete("all"); self.canvas_rects.clear()
        if not bp: return
        try: self.canvas_frame.update_idletasks(); fh = max(200, self.canvas_frame.winfo_height())
        except: fh = 700
        b_h = [max(120, 50 + sum(30 + math.ceil(len(", ".join(d['notes_raw'])) / 35) * 22 for d in m['instruments'].values()) + 10) for m in bp]
        ly, cy, xo = fh // 2, (fh // 2) - (max(b_h) // 2) - 20, 40
        self.canvas.create_line(0, ly, len(bp) * (self.card_width + 80), ly, fill="#333333", width=8)
        
        def bd(id_c, idx): self.canvas.tag_bind(id_c, "<Button-1>", lambda e, i=idx: self.on_item_click(idx=i))
        def bh(rid, idx):
            self.canvas.tag_bind(rid, "<Enter>", lambda e: self.canvas.itemconfig(rid, outline="#00e5ff", width=4) if idx != getattr(self, '_last_highlight_idx', -1) else None)
            self.canvas.tag_bind(rid, "<Leave>", lambda e: self.canvas.itemconfig(rid, outline="#555555", width=2) if idx != getattr(self, '_last_highlight_idx', -1) else None)

        for i, m in enumerate(bp):
            by = int(cy - (b_h[i] // 2)); rid = self.canvas.create_rectangle(xo, by, xo + self.card_width, by + b_h[i], fill="#242424", outline="#555555", width=2)
            self.canvas_rects.append({'bg': rid}); tid = self.canvas.create_text(xo + self.card_width//2, by + 20, text=f"CỤM {m['id']}", fill="white", font=("Arial", 16, "bold"))
            bd(rid, i); bd(tid, i); self.canvas.tag_bind(rid, "<Double-Button-1>", lambda e, idx=i: self.jump_to_step(idx, auto_play_note=True)); bh(rid, i); yt = by + 45
            for ins, d in m['instruments'].items():
                ic = "#17a2b8" if "🎹" in ins else "#e83e8c"; iid = self.canvas.create_text(xo + 15, yt, text=ins, fill=ic, font=("Arial", 13, "bold"), anchor="w"); bd(iid, i); yt += 20
                n_str = ", ".join(d['notes_raw']); nid = self.canvas.create_text(xo + 25, yt, text=n_str, fill="#cccccc", font=("Arial", 11), anchor="nw", width=self.card_width-40); bd(nid, i); yt += math.ceil(len(n_str) / 35) * 20 + 10
            if i < len(bp) - 1:
                self.canvas.create_line(xo + self.card_width, ly, xo + self.card_width + 80, ly, fill="#ffc107", width=6, arrow="last", arrowshape=(16, 20, 6))
                self.canvas.create_text(xo + self.card_width + 40, by - 16 if (by - 16) > 8 else ly - 25, text=m['wire'], fill="#ffc107", font=("Arial", 16, "bold"))
            xo += self.card_width + 80
        self.canvas.configure(scrollregion=self.canvas.bbox("all")); self._draw_minimap(); self._update_minimap_viewport()

    def _draw_minimap(self):
        self.minimap_canvas.delete("all")
        if not self.active_blueprint: return
        self.minimap_canvas.update_idletasks(); cw, tw = self.minimap_canvas.winfo_width(), len(self.active_blueprint) * (self.card_width + 80)
        if tw == 0 or cw <= 1: return
        sc = cw / tw
        for i, m in enumerate(self.active_blueprint): self.minimap_canvas.create_rectangle(i*(self.card_width+80)*sc, 5, (i*(self.card_width+80)+self.card_width)*sc, 45, fill="#242424", outline="#555555")
        self.minimap_viewport = self.minimap_canvas.create_rectangle(0, 2, 0, 48, outline=self.COLOR_ACCENT_1, width=2)
        self.minimap_canvas.bind("<Button-1>", self._on_minimap_click_drag); self.minimap_canvas.bind("<B1-Motion>", self._on_minimap_click_drag)

    def _update_minimap_viewport(self):
        sf, ef = self.canvas.xview(); mw = self.minimap_canvas.winfo_width()
        self.minimap_canvas.coords(self.minimap_viewport, sf * mw, 2, ef * mw, 48)

    def play_mixed_instruments(self, inst_dict):
        if not self.has_midi_output or not inst_dict: return
        is_mw_mode = (self.current_preview_mode == "🎹 Mini World")
        n_off = []
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
                    self.midi_out.note_on(play_note, vel, 9); n_off.append((play_note, 9))
                else:
                    target_prog = self.mw_instrument_to_gm.get(bn, 0) if is_mw_mode else prog
                    if self.mw_channel_programs.get(ch) != target_prog: 
                        self.midi_out.set_instrument(target_prog, ch); self.mw_channel_programs[ch] = target_prog
                    play_note = n
                    if is_mw_mode:
                        while play_note < 48: play_note += 12
                        while play_note > 83: play_note -= 12
                    self.midi_out.note_on(play_note, vel, ch); n_off.append((play_note, ch))
        if n_off:
            def t_off(): time.sleep(0.15); [self.midi_out.note_off(nt, 0, c) for nt, c in n_off]
            threading.Thread(target=t_off, daemon=True).start()

    def on_item_click(self, e=None, idx=None):
        if idx is not None and 0 <= idx < len(self.active_blueprint):
            self.current_step_index = idx; self.apply_sync_visuals(); self.play_mixed_instruments(self.active_blueprint[idx]['instruments'])
            try: self.slider_time.set(self.active_blueprint[idx]['sync_time'])
            except: pass

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
        self._resync_midi_output(); self.apply_sync_visuals()
        if auto_play_note: self.play_mixed_instruments(bp[idx]['instruments'])
        if was_p: self.start_offset = self.playback_offset; self.start_perf = time.perf_counter(); self.is_playing = True; threading.Thread(target=self._audio_playback_thread, daemon=True).start()
        else: self.is_paused = False 

    def manual_change_step(self, dir): self.jump_to_step(self.current_step_index + dir, auto_play_note=True)
    def jump_to_start(self): self.jump_to_step(0)

    def toggle_play(self):
        if self.is_playing:
            self.is_playing = False; self.is_paused = True; self.btn_play.configure(text="▶ Phát")
            if self.has_midi_output: [self.midi_out.write_short(0b10110000 | c, 123, 0) for c in range(16)]
            self.synth_channel.stop(); self.playback_offset = self.start_offset + (time.perf_counter() - self.start_perf) * 1000.0 * self.playback_speed
        else:
            self.start_offset = self.playback_offset; self.start_perf = time.perf_counter(); self.is_playing = True; self.is_paused = False
            self.btn_play.configure(text="⏸ Tạm Dừng"); threading.Thread(target=self._audio_playback_thread, daemon=True).start(); self._ui_update_loop()

    def on_slider_seek(self, val):
        was_p = self.is_playing; self.is_playing = False; self.playback_offset = float(val); self._update_time_display(self.playback_offset); self._resync_midi_output()
        c_idx = 0
        if self.blueprint_synctimes.size > 0:
            # Find the index of the cluster with the sync_time closest to the current playback offset.
            # This is more robust against floating point inaccuracies.
            c_idx = np.argmin(np.abs(self.blueprint_synctimes - self.playback_offset))

        self.current_step_index = c_idx; self.apply_sync_visuals()
        if was_p: self.start_offset = self.playback_offset; self.start_perf = time.perf_counter(); self.is_playing = True; threading.Thread(target=self._audio_playback_thread, daemon=True).start()
        else: self.is_paused = False

    def _resync_midi_output(self):
        if self.has_midi_output:
            [self.midi_out.write_short(0b10110000 | c, 123, 0) for c in range(16)]
            is_mw_mode = self.current_preview_mode == "🎹 Mini World"
            if is_mw_mode:
                used_channels = set(int(k.split('_')[0]) for k in self.channel_map.keys())
                for ch in used_channels:
                    self.midi_out.write_short(0b10110000 | ch, 7, 127)
                    self.midi_out.write_short(0b10110000 | ch, 91, 127)

            for e in self.full_midi_events:
                if e['time'] >= self.playback_offset: break
                om = e['msg']
                if om.type in ['program_change', 'control_change', 'pitchwheel']:
                    try:
                        if om.type == 'program_change' and is_mw_mode: continue 
                        b = om.bytes()
                        if om.type == 'control_change':
                            boost_factor = 1.3 if is_mw_mode else 1.15
                            if b[1] == 7: b = (b[0], b[1], min(127, int(b[2] * boost_factor)))
                            elif b[1] == 91: b = (b[0], b[1], max(100, b[2])) 
                        self.midi_out.write_short(b[0], b[1] if len(b) > 1 else 0, b[2] if len(b) > 2 else 0)
                    except: pass
        self.sync_playback_indices()

    def sync_playback_indices(self):
        self.next_midi_event_idx = len(self.full_midi_events)
        for i, e in enumerate(self.full_midi_events):
            if e['time'] >= self.playback_offset: self.next_midi_event_idx = i; break
        self.next_mw_idx = len(self.active_blueprint)
        for i, m in enumerate(self.active_blueprint):
            if m['sync_time'] >= self.playback_offset: self.next_mw_idx = i; break

    def _audio_playback_thread(self):
        bp = self.active_blueprint
        while self.is_playing:
            c_ms = self.start_offset + (time.perf_counter() - self.start_perf) * 1000.0 * self.playback_speed
            
            while self.next_mw_idx < len(bp) and bp[self.next_mw_idx]['sync_time'] <= c_ms:
                self.current_step_index = self.next_mw_idx; self.next_mw_idx += 1
                
            while self.next_midi_event_idx < len(self.full_midi_events) and self.full_midi_events[self.next_midi_event_idx]['time'] <= c_ms:
                if self.has_midi_output:
                    e = self.full_midi_events[self.next_midi_event_idx]; om = e['msg']; is_mw_mode = (self.current_preview_mode == "🎹 Mini World")
                    if om.type in ('note_on', 'note_off'):
                        map_key = f"9_{om.note}" if om.channel == 9 else f"{om.channel}_ALL"
                        if map_key in self.channel_map:
                            minfo = self.channel_map[map_key]
                            if minfo["display_name"] in self.selected_instruments:
                                try:
                                    vel = om.velocity if om.type == 'note_on' else 0
                                    if vel > 0: vel = min(127, int(vel * (1.3 if is_mw_mode else 1.15)))
                                    if om.channel == 9:
                                        play_note = self.mw_drum_to_gm_note.get(minfo['name'], 60) if is_mw_mode else om.note
                                        self.midi_out.write_short(om.bytes()[0], play_note, vel)
                                    else:
                                        if is_mw_mode:
                                            mw_prog = self.mw_instrument_to_gm.get(minfo['name'], 0)
                                            if self.mw_channel_programs.get(om.channel) != mw_prog:
                                                self.midi_out.set_instrument(mw_prog, om.channel); self.mw_channel_programs[om.channel] = mw_prog
                                                self.midi_out.write_short(0b10110000 | om.channel, 91, 127); self.midi_out.write_short(0b10110000 | om.channel, 7, 127)
                                        nt = om.note + self.transpose_semitones
                                        if is_mw_mode:
                                            while nt < 48: nt += 12
                                            while nt > 83: nt -= 12
                                        if 0 <= nt <= 127: self.midi_out.write_short(om.bytes()[0], nt, vel)
                                except: pass
                    elif om.type in ['program_change', 'control_change', 'pitchwheel']:
                        try:
                            if is_mw_mode and om.type == 'program_change': continue 
                            b = om.bytes()
                            if om.type == 'control_change':
                                boost_factor = 1.3 if is_mw_mode else 1.15
                                if b[1] == 7: b = (b[0], b[1], min(127, int(b[2] * boost_factor)))
                                elif b[1] == 91: b = (b[0], b[1], max(100, b[2])) 
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
            self._update_time_display(cms); self.apply_sync_visuals(); self.after(33, self._ui_update_loop)

    # =========================================================================
    # LÕI TỐI ƯU OBJECT POOLING: Thay đổi thông số, TUYỆT ĐỐI KHÔNG DESTROY
    # Tốc độ phản hồi: Ngay lập tức (Instant/O(1))
    # =========================================================================
    def apply_sync_visuals(self):
        bp, idx = self.active_blueprint, self.current_step_index
        if idx < 0 or idx >= len(bp) or getattr(self, '_last_highlight_idx', None) == idx: return
        self._last_highlight_idx = idx; d = bp[idx]
        
        self.lbl_step_num.configure(text=f"[ CỤM {d['id']} ]")
        self.lbl_step_wire.configure(text=f"➔ Dây tiếp: {d['wire']}")
        
        # 1. Thu hồi toàn bộ nhãn hiện tại cất vào kho
        for cf, _, _ in self.pool_frames: cf.pack_forget()
        
        # 2. Bốc số lượng nhãn vừa đủ ra để hiển thị và điền text mới
        for i, (ins, ind) in enumerate(d['instruments'].items()):
            if i >= len(self.pool_frames): break
            cf, lbl_title, note_lbls = self.pool_frames[i]
            cf.pack(side="left", expand=True, fill="both", padx=10)
            
            lbl_title.configure(text=ins, text_color=COLOR_SYNTH if "🎹" in ins else COLOR_DRUM)
            
            # Ẩn hết nốt cũ
            for nl in note_lbls: nl.pack_forget()
            
            # Hiện nốt mới
            for j, n in enumerate(ind['notes_raw']):
                if j < len(note_lbls):
                    note_lbls[j].configure(text=n)
                    note_lbls[j].pack(pady=3)
        
        if idx < len(self.txt_vert_line_map):
            sl, el = self.txt_vert_line_map[idx]
            self.txt_vert.tag_remove("active_line", "1.0", "end")
            self.txt_vert.tag_add("active_line", f"{sl}.0", f"{el}.end")
            self.txt_vert.see(f"{el}.end"); self.txt_vert.see(f"{sl}.0")
        
        for i, ci in enumerate(self.canvas_rects): self.canvas.itemconfig(ci['bg'], fill="#12505a" if i == idx else "#242424", outline="#00e5ff" if i == idx else "#555555", width=4 if i == idx else 2)
        if len(self.canvas_rects) > 0 and len(self.canvas_rects) * (self.card_width + 80) != 0:
            try: self.canvas.xview_moveto(max(0, min(1, ((idx * (self.card_width + 80)) + (self.card_width / 2) - (self.canvas.winfo_width() / 2)) / (len(self.canvas_rects) * (self.card_width + 80)))))
            except: pass
    # =========================================================================

    def update_stats_tab(self):
        bp = self.active_blueprint
        for w in self.stats_scroll_frame.winfo_children(): w.destroy()
        if not bp: return ctk.CTkLabel(self.stats_scroll_frame, text="Không có dữ liệu.", font=ctk.CTkFont(size=16)).pack(pady=20)
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
        self.btn_toggle_notes = ctk.CTkButton(note_stats_frame, text="▶", width=28, height=24, command=self._toggle_top_10_notes_list, fg_color="transparent", hover_color="#444444", text_color=self.COLOR_ACCENT_1)
        self.btn_toggle_notes.pack(side="right", padx=(0, 5))
        self.top_10_notes_list_frame = ctk.CTkFrame(note_container, fg_color="transparent")
        self._render_top_10_list(self.top_10_notes_list_frame, top_10_note_clusters, "note_count", "nốt")

        inst_container = ctk.CTkFrame(s_ov, fg_color="transparent")
        inst_container.pack(fill="x", pady=0, padx=0)
        inst_stats_frame = ctk.CTkFrame(inst_container, fg_color="transparent")
        inst_stats_frame.pack(fill="x", pady=2, padx=20)
        ctk.CTkLabel(inst_stats_frame, text="Nhiều loại nhạc cụ nhất:", anchor="w").pack(side="left")

        ctk.CTkLabel(inst_stats_frame, text=f"{max_inst_count} loại (Cụm {max_inst_cluster_id})", anchor="e", font=ctk.CTkFont(weight="bold")).pack(side="right")
        self.btn_toggle_inst = ctk.CTkButton(inst_stats_frame, text="▶", width=28, height=24, command=self._toggle_top_10_inst_list, fg_color="transparent", hover_color="#444444", text_color=self.COLOR_ACCENT_1)
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
            ctk.CTkLabel(parent_frame, text="Không có dữ liệu.").pack(pady=5)
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
            if self.btn_toggle_notes: self.btn_toggle_notes.configure(text="▶")
        else:
            self.top_10_notes_list_frame.pack(fill="x", padx=20, pady=(0, 10))
            if self.btn_toggle_notes: self.btn_toggle_notes.configure(text="▼")
        self.top_10_notes_expanded.set(not self.top_10_notes_expanded.get())

    def _toggle_top_10_inst_list(self):
        if self.top_10_inst_expanded.get():
            self.top_10_inst_list_frame.pack_forget()
            if self.btn_toggle_inst: self.btn_toggle_inst.configure(text="▶")
        else:
            self.top_10_inst_list_frame.pack(fill="x", padx=20, pady=(0, 10))
            if self.btn_toggle_inst: self.btn_toggle_inst.configure(text="▼")
        self.top_10_inst_expanded.set(not self.top_10_inst_expanded.get())

    def _update_time_display(self, c_ms):
        if not hasattr(self, 'lbl_time') or not self.lbl_time: return
        t_ms = self.slider_time.cget("to")
        if t_ms <= 0: t_ms = self.original_notes[-1]['time'] if self.original_notes else 0
        def fms(m): min, sec = divmod(max(0, m) / 1000, 60); return f"{int(min):02d}:{sec:05.2f}"
        self.lbl_time.configure(text=f"{fms(c_ms)} / {fms(t_ms)}")

    def export_vertical_to_txt(self):
        if not self.active_blueprint: return messagebox.showwarning("Cảnh báo", "Không có sơ đồ để xuất.")
        p = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text", "*.txt")], title="Lưu Sơ Đồ Dọc", initialfile=f"Sơ đồ - {os.path.basename(self.file_path or 'Untitled')}.txt")
        if p:
            try:
                with open(p, "w", encoding="utf-8") as f: f.write(self.txt_vert.get("1.0", "end"))
                messagebox.showinfo("Thành công", f"Đã xuất: {p}")
            except Exception as e: messagebox.showerror("Lỗi", str(e))

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
        self.frame_output.pack_forget(); self.frame_mapping.pack_forget(); self.frame_input.pack(fill="both", expand=True, padx=20, pady=20)
    
    def increase_pitch(self): self.apply_transpose(1)
    def decrease_pitch(self): self.apply_transpose(-1)
    def apply_transpose(self, s):
        if not self.original_notes: return
        self.transpose_semitones += s
        if hasattr(self, 'lbl_pitch'): self.lbl_pitch.configure(text=f"Pitch: {self.transpose_semitones:+d}")
        self.update_active_blueprint()
    
    def open_settings(self):
        if not hasattr(self, 'settings_window') or not self.settings_window.winfo_exists(): self.settings_window = SettingsWindow(self)
        self.settings_window.focus()

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
        if t == "Vàng Gold": self.COLOR_ACCENT_1, self.COLOR_SYNTH, self.COLOR_DRUM, self.COLOR_INFO, self.COLOR_INFO_HOVER = "#ffc107", "#ffb300", "#f06292", "#ffb300", "#e6a100"
        elif t == "Hồng Ruby": self.COLOR_ACCENT_1, self.COLOR_SYNTH, self.COLOR_DRUM, self.COLOR_INFO, self.COLOR_INFO_HOVER = "#e91e63", "#ec407a", "#ab47bc", "#ec407a", "#d43a6f"
        else: self.COLOR_ACCENT_1, self.COLOR_SYNTH, self.COLOR_DRUM, self.COLOR_INFO, self.COLOR_INFO_HOVER = "#00e5ff", "#17a2b8", "#e83e8c", "#17a2b8", "#138496"
        if not first_load:
            self.lbl_step_num.configure(text_color=self.COLOR_ACCENT_1); self.btn_select_all.configure(fg_color=self.COLOR_INFO, hover_color=self.COLOR_INFO_HOVER); self.btn_increase.configure(fg_color=self.COLOR_INFO)
            if self.active_blueprint: self.update_stats_tab(); self.render_active_sheet(); self.apply_sync_visuals()

    def generate_wire_pie_chart(self, p, wc):
        for w in p.winfo_children(): w.destroy()
        lbls, szs = [], []
        for k, v in wc.items():
            if v > 0: lbls.append(k); szs.append(v)
        if not szs: return ctk.CTkLabel(p, text="Không có dữ liệu.").pack(pady=20)
        try:
            fg = Figure(figsize=(5, 4), dpi=100); fg.patch.set_facecolor(COLOR_BG_MAIN); ax = fg.add_subplot(111)
            ex = [0.1 if i == szs.index(max(szs)) else 0 for i in range(len(szs))]
            ws, _, at = ax.pie(szs, explode=ex, labels=None, autopct='%1.1f%%', shadow=False, startangle=140, pctdistance=0.85, wedgeprops={'edgecolor': 'white'})
            for t in at: t.set_color('white'); t.set_fontsize(10); t.set_fontweight('bold')
            ax.axis('equal'); ax.legend(ws, lbls, title="Loại Dây", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1), facecolor="#343638", labelcolor='white', edgecolor='gray')
            fg.suptitle('Tỷ Lệ Các Loại Dây Nối', color='white', fontsize=16, fontweight='bold'); fg.tight_layout(rect=[0, 0, 0.75, 1])
            c = FigureCanvasTkAgg(fg, master=p); c.draw(); c.get_tk_widget().pack(side="top", fill="both", expand=True, padx=5, pady=5)
        except Exception as e: ctk.CTkLabel(p, text=f"Lỗi: {e}").pack(pady=20)

    def generate_instrument_bar_chart(self, p, ic):
        for w in p.winfo_children(): w.destroy()
        sc = sorted(ic.items(), key=lambda x: x[1], reverse=False)
        lbls = [x[0].replace("🎹 ", "").replace("🥁 ", "").replace("⚡ ", "") for x in sc if x[1] > 0]
        szs = [x[1] for x in sc if x[1] > 0]
        if not szs: return
        try:
            fg = Figure(figsize=(5, max(4, len(lbls) * 0.4)), dpi=100); fg.patch.set_facecolor(COLOR_BG_MAIN); ax = fg.add_subplot(111); ax.set_facecolor(COLOR_BG_SECTION)
            yp = np.arange(len(lbls)); ax.barh(yp, szs, align='center', color=self.COLOR_SYNTH); ax.set_yticks(yp, labels=lbls); ax.invert_yaxis()
            ax.set_xlabel('Số Lượng Nốt', color='white'); ax.set_title('Phân Bố Nốt Nhạc', color='white', fontweight='bold')
            ax.tick_params(axis='x', colors='white'); ax.tick_params(axis='y', colors='white')
            ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False); ax.spines['bottom'].set_color('gray'); ax.spines['left'].set_color('gray'); fg.tight_layout()
            c = FigureCanvasTkAgg(fg, master=p); c.draw(); c.get_tk_widget().pack(side="top", fill="both", expand=True, padx=5, pady=5)
        except Exception as e: ctk.CTkLabel(p, text=f"Lỗi: {e}").pack(pady=20)

    def _on_canvas_scrolled(self, *args): self.scrollbar_x.set(*args); self._update_minimap_viewport()
    def _on_horizontal_scroll(self, *args): self.canvas.xview(*args); self._update_minimap_viewport()
    def _on_minimap_click_drag(self, e): self.minimap_canvas.update_idletasks(); self.canvas.xview_moveto(e.x / self.minimap_canvas.winfo_width()); self._update_minimap_viewport()

    def show_help(self):
        if hasattr(self, 'help_window') and self.help_window.winfo_exists(): return self.help_window.focus()
        hw = ctk.CTkToplevel(self); hw.title("Trợ Giúp"); hw.geometry("700x600"); hw.transient(self); self.help_window = hw
        tb = ctk.CTkTextbox(hw, wrap="word", font=("Arial", 14)); tb.pack(fill="both", expand=True, padx=10, pady=10); tb.insert("1.0", HELP_TEXT); tb.configure(state="disabled")

if __name__ == "__main__":
    try: app = MiniWorldConverterApp(); app.mainloop()
    except Exception as e: print("Ứng dụng dừng với lỗi:", e)