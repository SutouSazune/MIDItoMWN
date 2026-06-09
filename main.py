import customtkinter as ctk
from tkinter import filedialog, messagebox
import mido
import threading
import pygame
import time
import os
import math
import pygame.midi
import numpy as np 
import json
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use('TkAgg')

# =========================================================
# THÔNG SỐ CỐT LÕI & DATA NHẠC CỤ
# HẰNG SỐ VÀ CẤU HÌNH
# =========================================================
HE_SO_TOC_DO = 1.0
CONFIG_FILE = "app_config.json"
APP_TITLE = "MIDI to Mini World Noteblock"

# Ngưỡng xử lý
CLUSTER_TIME_THRESHOLD = 30  # ms, các nốt trong khoảng này được gộp thành 1 cụm
MUC0_START_W_MS = 825      # ms, ngưỡng bắt đầu tính là Mức 0

# Màu sắc
COLOR_BG_MAIN = "#2B2B2B"
COLOR_BG_FRAME = "#242424"
COLOR_BG_SECTION = "#2a2d2e"
COLOR_ACCENT_1 = "#00e5ff"  # Cyan
COLOR_ACCENT_2 = "#ffc107"  # Vàng
COLOR_SYNTH = "#17a2b8"
COLOR_DRUM = "#e83e8c"
COLOR_SUCCESS = "#28a745"
COLOR_SUCCESS_HOVER = "#218838"
COLOR_DANGER = "#ff6b6b"
COLOR_INFO = "#17a2b8"
COLOR_INFO_HOVER = "#138496"
COLOR_SECONDARY = "#6c757d"
COLOR_SECONDARY_HOVER = "#5a6268"

# =========================================================
# DATA NHẠC CỤ
# =========================================================
MW_SYNTH = {
    "Piano": 0, "Guitar": 1, "Harp": 2, "Violin": 3, "Trumpet": 4,
    "Recorder": 5, "Oud": 6, "Guitar Mộc": 7
}

MW_ELECTRONIC = {
    "Guitar Bass Điện": 0, "Pluck Synth": 1, "Stylophone": 3,
    "Chuông Điện Tử": 5, "Harpsichord": 7
}

MW_DRUMS = {
    "Bass": 0, "Floor tom": 1, "Tom-tom": 2, "Lẫy": 3,
    "Hi-hat (đóng)": 4, "Chũm choẹ trung": 5, "Chũm choẹ to": 6, "Jam-block": 7
}

GM_INSTRUMENTS = [
    "Acoustic Grand Piano", "Bright Acoustic Piano", "Electric Grand Piano", "Honky-tonk Piano", "Electric Piano 1", "Electric Piano 2", "Harpsichord", "Clavinet",
    "Celesta", "Glockenspiel", "Music Box", "Vibraphone", "Marimba", "Xylophone", "Tubular Bells", "Dulcimer",
    "Drawbar Organ", "Percussive Organ", "Rock Organ", "Church Organ", "Reed Organ", "Accordion", "Harmonica", "Tango Accordion",
    "Acoustic Guitar (nylon)", "Acoustic Guitar (steel)", "Electric Guitar (jazz)", "Electric Guitar (clean)", "Electric Guitar (muted)", "Overdriven Guitar", "Distortion Guitar", "Guitar Harmonics",
    "Acoustic Bass", "Electric Bass (finger)", "Electric Bass (pick)", "Fretless Bass", "Slap Bass 1", "Slap Bass 2", "Synth Bass 1", "Synth Bass 2",
    "Violin", "Viola", "Cello", "Contrabass", "Tremolo Strings", "Pizzicato Strings", "Orchestral Harp", "Timpani",
    "String Ensemble 1", "String Ensemble 2", "Synth Strings 1", "Synth Strings 2", "Choir Aahs", "Voice Oohs", "Synth Voice", "Orchestra Hit",
    "Trumpet", "Trombone", "Tuba", "Muted Trumpet", "French Horn", "Brass Section", "Synth Brass 1", "Synth Brass 2",
    "Soprano Sax", "Alto Sax", "Tenor Sax", "Baritone Sax", "Oboe", "English Horn", "Bassoon", "Clarinet",
    "Piccolo", "Flute", "Recorder", "Pan Flute", "Blown Bottle", "Shakuhachi", "Whistle", "Ocarina",
    "Lead 1 (square)", "Lead 2 (sawtooth)", "Lead 3 (calliope)", "Lead 4 (chiff)", "Lead 5 (charang)", "Lead 6 (voice)", "Lead 7 (fifths)", "Lead 8 (bass + lead)",
    "Pad 1 (new age)", "Pad 2 (warm)", "Pad 3 (polysynth)", "Pad 4 (choir)", "Pad 5 (bowed)", "Pad 6 (metallic)", "Pad 7 (halo)", "Pad 8 (sweep)",
    "FX 1 (rain)", "FX 2 (soundtrack)", "FX 3 (crystal)", "FX 4 (atmosphere)", "FX 5 (brightness)", "FX 6 (goblins)", "FX 7 (echoes)", "FX 8 (sci-fi)",
    "Sitar", "Banjo", "Shamisen", "Koto", "Kalimba", "Bagpipe", "Fiddle", "Shanai",
    "Tinkle Bell", "Agogo", "Steel Drums", "Woodblock", "Taiko Drum", "Melodic Tom", "Synth Drum", "Reverse Cymbal",
    "Guitar Fret Noise", "Breath Noise", "Seashore", "Bird Tweet", "Telephone Ring", "Helicopter", "Applause", "Gunshot"
]

GM_DRUM_MAP = {
    35: "Acoustic Bass Drum", 36: "Bass Drum 1", 37: "Side Stick", 38: "Acoustic Snare",
    39: "Hand Clap", 40: "Electric Snare", 41: "Low Floor Tom", 42: "Closed Hi Hat",
    43: "High Floor Tom", 44: "Pedal Hi-Hat", 45: "Low Tom", 46: "Open Hi-Hat",
    47: "Low-Mid Tom", 48: "Hi-Mid Tom", 49: "Crash Cymbal 1", 50: "High Tom",
    51: "Ride Cymbal 1", 52: "Chinese Cymbal", 53: "Ride Bell", 54: "Tambourine",
    55: "Splash Cymbal", 56: "Cowbell", 57: "Crash Cymbal 2", 58: "Vibraslap", 
    59: "Ride Cymbal 2", 60: "Hi Bongo", 61: "Low Bongo", 62: "Mute Hi Conga",
    63: "Open Hi Conga", 64: "Low Conga", 65: "High Timbale", 66: "Low Timbale"
}

HELP_TEXT = """# Hướng Dẫn Sử Dụng Công Cụ

## 1. Dây Nối (Wire)
Dây nối xác định khoảng thời gian chờ giữa hai cụm nốt nhạc.

- **Sát nhau:** Các nốt ở cụm tiếp theo được gõ gần như ngay lập tức.
- **1 PL (Pulse):** Khoảng trễ rất ngắn, tương đương 1 lần gõ của khối hẹn giờ.
- **Mức 5 -> Mức 1:** Các khoảng trễ tăng dần. Mức 5 là nhanh nhất, Mức 1 là chậm nhất trong thang này.
- **Mức 0:** Một khoảng trễ dài. Các khoảng trễ rất dài sẽ được biểu diễn bằng bội số của Mức 0 (ví dụ: "2 Mức 0 + 1 Mức 3").

## 2. Chế Độ Nghe Thử
- **🎵 Nhạc MIDI Gốc:** Phát lại bản nhạc gốc với các nhạc cụ được map. Yêu cầu có bộ tổng hợp MIDI của hệ điều hành (thường có sẵn trên Windows).
- **🎹 Mini World:** Mô phỏng âm thanh của các khối nhạc trong game.

## 3. Các Tính Năng Khác
- **Lưu/Tải Cấu Hình:** Lưu lại cách bạn map nhạc cụ để tái sử dụng sau này.
- **Tăng/Giảm Pitch:** Thay đổi cao độ của toàn bộ bản nhạc (không áp dụng cho trống).
- **Xuất Sơ Đồ:** Lưu sơ đồ dọc chi tiết ra file .txt.
- **Quản lý bộ trống:** Tùy chỉnh cách map các nốt trống MIDI sang trống Mini World.
- **Đơn giản hóa:** Loại bỏ các nốt nhạc quá nhanh hoặc quá nhẹ để bản thiết kế dễ xây dựng hơn.

---
Công cụ được phát triển bởi LKL."""

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# =========================================================
# DATA PROCESSING CLASSES
# =========================================================

class MidiProcessor:
    """Xử lý việc đọc và trích xuất dữ liệu thô từ file MIDI."""
    def scan_channels(self, file_path):
        mid = mido.MidiFile(file_path)
        used_channels = set()
        used_drum_notes = set()
        channel_programs = {i: 0 for i in range(16)}
        
        for msg in mido.merge_tracks(mid.tracks):
            if msg.type == 'program_change':
                channel_programs[msg.channel] = msg.program
            elif msg.type == 'note_on' and msg.velocity > 0:
                if msg.channel == 9: used_drum_notes.add(msg.note)
                else: used_channels.add(msg.channel)
        return sorted(list(used_channels)), sorted(list(used_drum_notes)), channel_programs

    def build_note_list(self, file_path, channel_map, simplification_options):
        mid = mido.MidiFile(file_path)
        absolute_time = 0
        tempo = 500000
        original_notes = []
        full_midi_events = []
        current_programs = {i: 0 for i in range(16)}

        midi_metadata = {
            'ticks_per_beat': mid.ticks_per_beat, 'length': mid.length,
            'initial_tempo': 500000, 'initial_time_signature': '4/4'
        }
        found_tempo, found_ts = False, False
        
        for msg in mido.merge_tracks(mid.tracks):
            if not found_tempo and msg.type == 'set_tempo':
                midi_metadata['initial_tempo'] = msg.tempo
                found_tempo = True
            if not found_ts and msg.type == 'time_signature':
                midi_metadata['initial_time_signature'] = f"{msg.numerator}/{msg.denominator}"
                found_ts = True

            absolute_time += mido.tick2second(msg.time, mid.ticks_per_beat, tempo) * 1000
            
            if not msg.is_meta:
                full_midi_events.append({'time': absolute_time, 'msg': msg})
            if msg.type == 'set_tempo':
                tempo = msg.tempo
            elif msg.type == 'program_change':
                current_programs[msg.channel] = msg.program
            elif msg.type == 'note_on' and msg.velocity > 0:
                map_key = f"9_{msg.note}" if msg.channel == 9 else f"{msg.channel}_ALL"
                if map_key in channel_map:
                    original_notes.append({
                        'time': absolute_time, 'note': msg.note, 'velocity': msg.velocity,
                        'channel': msg.channel, 'map_key': map_key,
                        'program': current_programs.get(msg.channel, 0)
                    })
        
        if simplification_options['enabled']:
            filtered_notes = []
            time_threshold = simplification_options['time_ms']
            velo_threshold = simplification_options['velocity']
            
            if original_notes:
                last_note_time = -1
                for note in original_notes:
                    if note['velocity'] < velo_threshold: continue
                    if (note['time'] - last_note_time) < time_threshold and last_note_time != -1: continue
                    
                    filtered_notes.append(note)
                    last_note_time = note['time']
            original_notes = filtered_notes

        return original_notes, full_midi_events, midi_metadata

class BlueprintGenerator:
    """Tạo sơ đồ chi tiết (blueprint) từ danh sách nốt nhạc đã xử lý."""
    def create_blueprint(self, original_notes, channel_map, selected_instruments, transpose_semitones, mw_drum_to_gm_note):
        target_notes = [n for n in original_notes if channel_map[n['map_key']]["display_name"] in selected_instruments]
        blueprint = []
        
        if not target_notes: return blueprint

        groups, current_group = [], [0]
        for i in range(1, len(target_notes)):
            if target_notes[i]['time'] - target_notes[current_group[-1]]['time'] < CLUSTER_TIME_THRESHOLD:
                current_group.append(i)
            else:
                groups.append(current_group); current_group = [i]
        groups.append(current_group)

        for gi, grp in enumerate(groups):
            time_sync = target_notes[grp[0]]['time']
            inst_data = {}
            
            for idx in grp:
                n = target_notes[idx]
                map_info = channel_map[n['map_key']]
                inst_name = map_info["display_name"]
                
                if inst_name not in inst_data:
                    inst_data[inst_name] = {"notes_raw": [], "notes": [], "type": map_info["type"], "name": map_info["name"]}
                
                if map_info["type"] == "Drum":
                    inst_data[inst_name]["notes_raw"].append(f"[Trống] Gõ {map_info['tap']}")
                    # For drum preview, we use a fixed note from the MW_DRUM mapping
                    gm_note_for_preview = mw_drum_to_gm_note.get(map_info['name'], 60) # Default to Hi Bongo
                    inst_data[inst_name]["notes"].append({'midi': gm_note_for_preview, 'channel': 9})
                else: # Synth
                    final_note = n['note'] + transpose_semitones
                    mw_note_val = final_note
                    while mw_note_val < 48: mw_note_val += 12
                    while mw_note_val > 83: mw_note_val -= 12
                    
                    tap = mw_note_val % 12
                    b = "Trầm" if mw_note_val <= 59 else "Trung" if mw_note_val <= 71 else "Cao"
                    inst_data[inst_name]["notes_raw"].append(f"Khối {b}: {tap}")
                    inst_data[inst_name]["notes"].append({'midi': final_note, 'channel': n['channel']})

            for name in inst_data:
                inst_data[name]["notes_raw"] = list(dict.fromkeys(inst_data[name]["notes_raw"]))
                inst_data[name]["notes"] = list({(d['midi'], d['channel']): d for d in inst_data[name]["notes"]}.values())
            
            wire_str = "[HẾT BÀI]"
            if gi < len(groups) - 1:
                d_ms = target_notes[groups[gi+1][0]]['time'] - time_sync
                w_ms = max(0, (d_ms * HE_SO_TOC_DO) - 50)

                if w_ms < 30: wire_str = "Sát nhau"
                elif w_ms < 100: wire_str = "1 PL"
                elif w_ms < MUC0_START_W_MS:
                    ticks = int(round(w_ms / 150.0))
                    wire_str = f"Mức {5 - (ticks - 1)}"
                else:
                    num_muc0 = int(w_ms // MUC0_START_W_MS)
                    rem_w_ms = w_ms % MUC0_START_W_MS
                    parts = [f"{num_muc0} Mức 0"] if num_muc0 > 0 else []
                    if rem_w_ms >= 100:
                        rem_ticks = int(round(rem_w_ms / 150.0))
                        parts.append(f"1 Mức {5 - (rem_ticks - 1)}")
                    elif rem_w_ms >= 30:
                        parts.append("1 PL")
                    wire_str = " + ".join(parts) if parts else "Mức 0"

            blueprint.append({
                "id": f"{gi+1:03d}", "sync_time": time_sync,
                "instruments": inst_data, "wire": wire_str
            })
        return blueprint

class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.transient(master)
        self.title("Cài Đặt")
        self.geometry("400x300")
        self.app = master

        ctk.CTkLabel(self, text="Chủ đề màu sắc:", font=ctk.CTkFont(weight="bold")).pack(pady=(20, 5))
        theme_combo = ctk.CTkComboBox(self, values=["Mặc định (Cyan)", "Vàng Gold", "Hồng Ruby"], command=self.app._apply_theme)
        theme_combo.set(self.app.current_theme_name)
        theme_combo.pack(pady=5)

        ctk.CTkLabel(self, text="Nâng cao:", font=ctk.CTkFont(weight="bold")).pack(pady=(30, 5))
        ctk.CTkButton(self, text="Trình Quản Lý Bộ Trống", command=self.open_drum_kit_manager).pack(pady=10)

    def open_drum_kit_manager(self):
        if not hasattr(self, 'drum_kit_window') or not self.drum_kit_window.winfo_exists():
            self.drum_kit_window = DrumKitManager(self.app)
        self.drum_kit_window.focus()

class DrumKitManager(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.transient(master)
        self.app = master
        self.title("Trình Quản Lý Bộ Trống")
        self.geometry("700x600")

        self.drum_map_combos = {}

        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkButton(top_frame, text="Tải Bộ Trống", command=self.load_kit).pack(side="left", padx=5)
        ctk.CTkButton(top_frame, text="Lưu Bộ Trống", command=self.save_kit).pack(side="left", padx=5)
        ctk.CTkButton(top_frame, text="Áp Dụng cho Lần Chuyển Đổi Này", command=self.apply_kit, fg_color=COLOR_SUCCESS).pack(side="right", padx=5)

        scroll_frame = ctk.CTkScrollableFrame(self)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=5)

        options_drum = [f"🥁 Trống: {k} (Gõ {v})" for k, v in MW_DRUMS.items()]

        for note_val, note_name in sorted(GM_DRUM_MAP.items()):
            row = ctk.CTkFrame(scroll_frame)
            row.pack(fill="x", pady=2, padx=5)
            ctk.CTkLabel(row, text=f"Nốt {note_val}: {note_name}", width=250, anchor="w").pack(side="left", padx=10)
            
            combo = ctk.CTkComboBox(row, values=options_drum, width=250)
            
            # Set default value from current mapping
            current_mw_drum = self.app.active_drum_map.get(note_val)
            if current_mw_drum:
                for option in options_drum:
                    if current_mw_drum in option:
                        combo.set(option)
                        break
            
            combo.pack(side="right", padx=10, pady=5)
            self.drum_map_combos[note_val] = combo

    def save_kit(self):
        kit_data = {note: combo.get() for note, combo in self.drum_map_combos.items()}
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("Drum Kit JSON", "*.json")], title="Lưu Bộ Trống")
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(kit_data, f, indent=4)
                messagebox.showinfo("Thành công", "Đã lưu bộ trống.", parent=self)
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể lưu file: {e}", parent=self)

    def load_kit(self):
        file_path = filedialog.askopenfilename(filetypes=[("Drum Kit JSON", "*.json")], title="Tải Bộ Trống")
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    kit_data = json.load(f)
                for note_val_str, mw_drum_str in kit_data.items():
                    note_val = int(note_val_str)
                    if note_val in self.drum_map_combos:
                        self.drum_map_combos[note_val].set(mw_drum_str)
                messagebox.showinfo("Thành công", "Đã tải bộ trống.", parent=self)
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể tải file: {e}", parent=self)

    def apply_kit(self):
        new_map = {}
        for note_val, combo in self.drum_map_combos.items():
            val = combo.get()
            name = val.split(":")[1].split("(")[0].strip()
            full_name_part = val.split(":")[1].strip()
            last_paren_index = full_name_part.rfind('(')
            name = full_name_part[:last_paren_index].strip()
            new_map[note_val] = name
        
        self.app.active_drum_map = new_map
        messagebox.showinfo("Hoàn tất", "Đã áp dụng bộ trống tùy chỉnh cho lần chuyển đổi này.", parent=self)
        self.destroy()

# =========================================================
# MAIN APPLICATION
# =========================================================
class MiniWorldConverterApp(ctk.CTk):
    """
    Ứng dụng chuyển đổi file MIDI thành sơ đồ khối nhạc cho Mini World.

    Bao gồm các tính năng map nhạc cụ, hiển thị sơ đồ đa dạng,
    và trình phát nhạc với hai chế độ để nghe thử bản gốc và bản chuyển đổi.
    """
    def __init__(self):
        super().__init__()
        
        self.last_directory = "."
        self.load_app_config()
        self.title(APP_TITLE)
        self.geometry(self.window_geometry)
        
        pygame.mixer.pre_init(44100, -16, 2, 1024)
        pygame.init()
        if not pygame.mixer.get_init():
            pygame.mixer.init(44100, -16, 2, 1024)

        self.midi_out = None
        self.has_midi_output = False
        try:
            pygame.midi.init()
            if pygame.midi.get_count() > 0:
                default_id = pygame.midi.get_default_output_id()
                if default_id != -1:
                    self.midi_out = pygame.midi.Output(default_id)
                    self.has_midi_output = True
                    print(f"MIDI output device '{pygame.midi.get_device_info(default_id)[1].decode()}' initialized.")
            if not self.has_midi_output:
                print("No default MIDI output device found or available. 'MIDI Gốc' playback will be silent.")
        except Exception as e:
            print(f"Could not initialize pygame.midi: {e}")

        self.processor = MidiProcessor()
        self.generator = BlueprintGenerator()

        pygame.mixer.set_num_channels(64) 
        self.synth_channel = pygame.mixer.Channel(0)
        self.synth_channel.set_volume(1)
        
        self.file_path = ""
        self.original_notes = [] 
        
        self.available_instruments = []
        self.selected_instruments = set()
        self.checkbox_vars = {}
        self.active_blueprint = [] 
        
        self.cached_sounds = {}
        self.mw_instrument_to_gm = {
            "Piano": 0, "Guitar": 27, "Harp": 46, "Violin": 45, "Trumpet": 56,
            "Recorder": 74, "Oud": 24, "Guitar Mộc": 24,
            "Guitar Bass Điện": 33, "Pluck Synth": 84, "Stylophone": 80,
            "Chuông Điện Tử": 10, "Harpsichord": 6,
        }
        self.mw_channel_programs = {}
        self.mw_drum_to_gm_note = {
            "Bass": 36, "Floor tom": 41, "Tom-tom": 45, "Lẫy": 38,
            "Hi-hat (đóng)": 42, "Chũm choẹ trung": 51, "Chũm choẹ to": 49, "Jam-block": 76
        }
        self._sound_gen_thread = None
        self.midi_metadata = {}
        self.transpose_semitones = 0
        
        self.is_playing = False
        self.is_paused = False
        self.playback_speed = 1.0 
        self.current_step_index = 0
        self.playback_offset = 0  
        self.current_preview_mode = "🎵 Nhạc MIDI Gốc"
        
        self.start_perf = 0
        self.start_offset = 0
        self.next_orig_idx = 0
        self.next_mw_idx = 0
        self.full_midi_events = []
        self.next_midi_event_idx = 0
        
        self.canvas_rects = [] 
        self.txt_vert_line_map = [] 
        self._last_highlight_idx = None
        self.card_width = 320  
        
        self.setup_input_screen()
        
        # --- Cài đặt màu sắc và theme ---
        self.current_theme_name = "Mặc định (Cyan)"
        self._apply_theme(self.current_theme_name, first_load=True)

        # --- Cài đặt bộ trống ---
        self.default_drum_map = {note: name for note, name in MW_DRUMS.items()} # Simplified
        self.active_drum_map = self._create_default_drum_map()

        # --- Setup UI ---
        self.setup_mapping_screen()
        self.setup_output_screen()
        
        self.frame_mapping.pack_forget()
        self.frame_output.pack_forget()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def load_app_config(self):
        self.window_geometry = "1400x950"
        self.last_directory = "."
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    self.window_geometry = config.get("window_geometry", "1400x950")
                    self.last_directory = config.get("last_directory", ".")
                    if not os.path.isdir(self.last_directory): self.last_directory = "."
        except Exception as e:
            print(f"Could not load config: {e}")

    def save_app_config(self):
        try:
            config = {
                "window_geometry": self.geometry(),
                "last_directory": self.last_directory
            }
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Could not save config: {e}")

    def on_closing(self):
        self.is_playing = False
        self.save_app_config()
        if self.midi_out:
            try:
                for chan in range(16):
                    self.midi_out.write_short(0b10110000 | chan, 123, 0)
                self.midi_out.close()
            except Exception as e:
                print(f"Error closing MIDI out: {e}")
        try:
            if pygame.midi.get_init(): pygame.midi.quit()
        except Exception as e:
            print(f"Error quitting pygame.midi: {e}")
        self.destroy()

    def setup_input_screen(self):
        self.frame_input = ctk.CTkFrame(self)
        self.frame_input.pack(fill="both", expand=True, padx=20, pady=20)
        self.lbl_title = ctk.CTkLabel(self.frame_input, text="Chọn file MIDI", font=ctk.CTkFont(size=32, weight="bold"))
        self.lbl_title.pack(pady=(250, 10))
        self.lbl_file = ctk.CTkLabel(self.frame_input, text="Chưa chọn file nào", text_color="gray", font=ctk.CTkFont(size=18))
        self.lbl_file.pack(pady=(0, 20))
        self.btn_select = ctk.CTkButton(self.frame_input, text="📁 Chọn File", width=250, height=50, font=ctk.CTkFont(size=18), command=self.select_file)
        self.btn_select.pack(pady=10)

        self.lbl_signature = ctk.CTkLabel(self.frame_input, text="ft.LKL", font=ctk.CTkFont(size=12, slant="italic"), text_color="gray50")
        self.lbl_signature.pack(side="bottom", pady=10)

    def setup_mapping_screen(self):
        self.frame_mapping = ctk.CTkFrame(self)
        self.lbl_map_title = ctk.CTkLabel(self.frame_mapping, text="CẤU HÌNH NHẠC CỤ", font=ctk.CTkFont(size=28, weight="bold"))
        self.lbl_map_title.pack(pady=(30, 20))
        self.map_scroll = ctk.CTkScrollableFrame(self.frame_mapping, width=600, height=400)

        search_frame = ctk.CTkFrame(self.frame_mapping, fg_color="transparent")
        search_frame.pack(fill="x", padx=10, pady=(0, 5))
        self.map_search_entry = ctk.CTkEntry(search_frame, placeholder_text="🔍 Tìm kiếm nhạc cụ...")
        self.map_search_entry.pack(fill="x", padx=10, pady=5)
        self.map_search_entry.bind("<KeyRelease>", self._filter_mapping_list)
        self.map_scroll.pack(pady=10, padx=10, fill="y", expand=True)

        map_actions_frame = ctk.CTkFrame(self.frame_mapping, fg_color="transparent")
        map_actions_frame.pack(pady=(10, 10))
        
        self.btn_load_map = ctk.CTkButton(map_actions_frame, text="Tải Cấu Hình", command=self.load_mapping_config, fg_color=COLOR_SECONDARY, hover_color=COLOR_SECONDARY_HOVER)
        self.btn_load_map.pack(side="left", padx=10)
        
        self.btn_save_map = ctk.CTkButton(map_actions_frame, text="Lưu Cấu Hình", command=self.save_mapping_config, fg_color=COLOR_INFO, hover_color=COLOR_INFO_HOVER)
        self.btn_save_map.pack(side="left", padx=10)

        simplify_frame = ctk.CTkFrame(self.frame_mapping, fg_color="transparent")
        simplify_frame.pack(pady=(10, 0), padx=10, fill='x')
        s_frame_inner = ctk.CTkFrame(simplify_frame)
        s_frame_inner.pack()
        self.simplify_enabled_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(s_frame_inner, text="Đơn giản hóa:", variable=self.simplify_enabled_var).pack(side='left', padx=10, pady=10)
        ctk.CTkLabel(s_frame_inner, text="Bỏ nốt nhanh hơn (ms):").pack(side='left', padx=(10,0))
        self.simplify_time_var = ctk.StringVar(value="50")
        ctk.CTkEntry(s_frame_inner, textvariable=self.simplify_time_var, width=50).pack(side='left', padx=(5,10))
        ctk.CTkLabel(s_frame_inner, text="Bỏ nốt có velocity <").pack(side='left', padx=(10,0))
        self.simplify_velocity_var = ctk.StringVar(value="20")
        ctk.CTkEntry(s_frame_inner, textvariable=self.simplify_velocity_var, width=50).pack(side='left', padx=5, pady=10)

        self.btn_start_convert = ctk.CTkButton(self.frame_mapping, text="⚡ Bắt Đầu Chuyển Đổi", width=250, height=50, font=ctk.CTkFont(size=18, weight="bold"), command=self.process_mapping_and_convert, fg_color=COLOR_SUCCESS, hover_color=COLOR_SUCCESS_HOVER)
        self.btn_start_convert.pack(pady=(10, 30))
        self.mapping_comboboxes = []




    def setup_output_screen(self):
        self.frame_output = ctk.CTkFrame(self)
        self.top_bar = ctk.CTkFrame(self.frame_output, fg_color="transparent")
        self.top_bar.pack(fill="x", padx=10, pady=5)
        self.btn_back = ctk.CTkButton(self.top_bar, text="← Tệp", width=100, corner_radius=8, fg_color=COLOR_BG_MAIN, hover_color="#3a3a3a", cursor="hand2", command=self.back_to_input)
        self.btn_back.pack(side="left")
        self.btn_export_txt = ctk.CTkButton(self.top_bar, text="Xuất Sơ đồ Dọc (.txt)", width=200, command=self.export_vertical_to_txt)
        self.btn_export_txt.pack(side="left", padx=(10, 0))
        self.lbl_now_playing = ctk.CTkLabel(self.top_bar, text="", font=ctk.CTkFont(weight="bold", size=20))
        self.btn_settings = ctk.CTkButton(self.top_bar, text="⚙️", width=30, command=self.open_settings)
        self.btn_settings.pack(side="right", padx=(0, 5))
        self.lbl_now_playing.pack(side="left", fill="x", expand=True)
        self.btn_help = ctk.CTkButton(self.top_bar, text="?", width=30, command=self.show_help)
        self.btn_help.pack(side="right", padx=(0, 10))

        self.sheet_panel = ctk.CTkFrame(self.frame_output, height=60)
        self.sheet_panel.pack(fill="x", padx=10, pady=5)
        self.lbl_sheet = ctk.CTkLabel(self.sheet_panel, text="Hiển thị Bản vẽ:", font=ctk.CTkFont(weight="bold", size=15))
        self.lbl_sheet.pack(side="left", padx=15, pady=10)
        self.btn_select_all = ctk.CTkButton(self.sheet_panel, text="Chọn Tất Cả", width=100, fg_color=COLOR_INFO, hover_color=COLOR_INFO_HOVER, command=self.select_all_sheets)
        self.btn_select_all.pack(side="left", padx=5)
        self.btn_clear_all = ctk.CTkButton(self.sheet_panel, text="Bỏ Chọn", width=90, fg_color=COLOR_SECONDARY, hover_color=COLOR_SECONDARY_HOVER, command=self.clear_all_sheets)
        self.btn_clear_all.pack(side="left", padx=5)
        self.sheet_checkboxes_frame = ctk.CTkScrollableFrame(self.sheet_panel, orientation="horizontal", height=45, fg_color="transparent")
        self.sheet_checkboxes_frame.pack(side="left", fill="x", expand=True, padx=10)

        self.tabview = ctk.CTkTabview(self.frame_output, command=self.on_tab_change)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=5)
        self.tab_vert = self.tabview.add("Sơ đồ Dọc")
        self.tab_horz = self.tabview.add("Sơ đồ Ngang")
        self.tab_step = self.tabview.add("Sơ đồ Đơn")
        self.tab_stats = self.tabview.add("📊 Thống kê")
        
        self.txt_vert = ctk.CTkTextbox(self.tab_vert, font=ctk.CTkFont(family="Consolas", size=16), wrap="none", cursor="hand2")
        self.txt_vert.pack(fill="both", expand=True, padx=5, pady=5)
        self.txt_vert.tag_config("active_line", background="#12505a", foreground="white")
        self.txt_vert.bind("<Button-1>", self.on_txt_vert_click)
        self.txt_vert.bind("<Double-Button-1>", self.on_txt_vert_double_click)
        
        self.canvas_frame = ctk.CTkFrame(self.tab_horz)
        self.canvas_frame.pack(fill="both", expand=True)
        self.canvas = ctk.CTkCanvas(self.canvas_frame, bg="#121212", highlightthickness=0)
        self.minimap_canvas = ctk.CTkCanvas(self.canvas_frame, height=50, bg="#0c0c0c", highlightthickness=0)
        self.minimap_viewport = self.minimap_canvas.create_rectangle(0,0,0,0, outline="red") # Placeholder
        self.scrollbar_x = ctk.CTkScrollbar(self.canvas_frame, orientation="horizontal")
        
        self.canvas.pack(side="top", fill="both", expand=True)
        self.minimap_canvas.pack(side="bottom", fill="x")
        self.scrollbar_x.pack(side="bottom", fill="x")

        self.canvas.bind("<MouseWheel>", lambda e: self.canvas.xview_scroll(int(-1 * (e.delta / 120)), "units"))
        
        self.frame_step = ctk.CTkFrame(self.tab_step, corner_radius=10)
        self.frame_step.pack(fill="both", expand=True, padx=20, pady=20)
        self.frame_step_header = ctk.CTkFrame(self.frame_step, fg_color="transparent")
        self.frame_step_header.pack(fill="x", pady=(20, 10))
        self.lbl_step_num = ctk.CTkLabel(self.frame_step_header, text="[ CỤM 000 ]", font=ctk.CTkFont(size=36, weight="bold"), text_color=COLOR_ACCENT_1)
        self.lbl_step_num.pack()
        self.frame_step_instruments = ctk.CTkFrame(self.frame_step, fg_color="transparent")
        self.frame_step_instruments.pack(expand=True, fill="both", padx=20)
        self.lbl_step_wire = ctk.CTkLabel(self.frame_step, text="➔ Dây: ...", font=ctk.CTkFont(size=30, weight="bold"), text_color=COLOR_ACCENT_2)
        self.lbl_step_wire.pack(pady=(10, 30))

        # Khung cho tab Thống kê
        self.stats_scroll_frame = ctk.CTkScrollableFrame(self.tab_stats, label_text="Phân Tích Chi Tiết Bản Nhạc")
        self.stats_scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.music_panel = ctk.CTkFrame(self.frame_output, height=90)
        self.music_panel.pack(fill="x", padx=10, pady=(0, 10))
        
        self.btn_reset = ctk.CTkButton(self.music_panel, text="⏮", width=50, corner_radius=10, command=self.jump_to_start)
        self.btn_reset.pack(side="left", padx=(20, 5), pady=20)
        self.btn_prev = ctk.CTkButton(self.music_panel, text="◀◀", width=50, corner_radius=10, command=lambda: self.manual_change_step(-1))
        self.btn_prev.pack(side="left", padx=5, pady=20)
        self.btn_play = ctk.CTkButton(self.music_panel, text="▶ Phát", width=140, corner_radius=12, fg_color=COLOR_SUCCESS, hover_color=COLOR_SUCCESS_HOVER, font=ctk.CTkFont(weight="bold", size=18), command=self.toggle_play)
        self.btn_play.pack(side="left", padx=5, pady=20)
        self.btn_next = ctk.CTkButton(self.music_panel, text="▶▶", width=50, corner_radius=10, command=lambda: self.manual_change_step(1))
        self.btn_next.pack(side="left", padx=5, pady=20)
        self.mode_switch = ctk.CTkSegmentedButton(self.music_panel, values=["🎵 Nhạc MIDI Gốc", "🎹 Mini World"], command=self.change_preview_mode)
        self.mode_switch.set("🎵 Nhạc MIDI Gốc")
        self.mode_switch.pack(side="left", padx=20, pady=20)
        self.combo_speed = ctk.CTkComboBox(self.music_panel, values=["0.5x", "0.75x", "1.0x", "1.25x", "1.5x"], width=90, command=self.change_speed)
        self.combo_speed.set("1.0x")
        self.combo_speed.pack(side="left", padx=5, pady=20)
        self.btn_decrease = ctk.CTkButton(self.music_panel, text="⇩", width=40, corner_radius=10, fg_color=COLOR_DANGER, command=self.decrease_pitch)
        self.btn_decrease.pack(side="left", padx=(10, 0), pady=20)
        self.lbl_pitch = ctk.CTkLabel(self.music_panel, text="Pitch: 0", width=70, font=ctk.CTkFont(size=14, family="Consolas"))
        self.lbl_pitch.pack(side="left", padx=5, pady=20)
        self.btn_increase = ctk.CTkButton(self.music_panel, text="⇧", width=40, corner_radius=10, fg_color=COLOR_INFO, command=self.increase_pitch)
        self.btn_increase.pack(side="left", padx=(0, 15), pady=20)
        
        self.lbl_time = ctk.CTkLabel(self.music_panel, text="00:00.00 / 00:00.00", width=150, font=ctk.CTkFont(family="Consolas", size=14))
        self.lbl_time.pack(side="right", padx=(0, 20), pady=20)
        self.slider_time = ctk.CTkSlider(self.music_panel, from_=0, to=100, command=self.on_slider_seek)
        self.slider_time.set(0)
        self.slider_time.pack(side="left", fill="x", expand=True, padx=(10, 0), pady=20)

    # =========================================================
    # QUÉT FILE & MAPPING NHẠC CỤ
    # =========================================================
    def select_file(self):
        """Mở hộp thoại chọn file MIDI và bắt đầu quá trình quét."""
        path = filedialog.askopenfilename(filetypes=[("MIDI", "*.mid *.midi")], initialdir=self.last_directory)
        if path:
            self.file_path = path
            self.last_directory = os.path.dirname(path)
            self.lbl_file.configure(text=os.path.basename(path))
            self.scan_midi_channels()

    def _filter_mapping_list(self, event=None):
        search_term = self.map_search_entry.get().lower()
        for item in self.mapping_comboboxes:
            row_frame = item['frame']
            label_widget = row_frame.winfo_children()[0]
            label_text = label_widget.cget("text").lower()
            
            if search_term in label_text:
                if not row_frame.winfo_ismapped():
                    row_frame.pack(fill="x", pady=item['pady'], padx=item['padx'])
            else:
                if row_frame.winfo_ismapped():
                    row_frame.pack_forget()


    def scan_midi_channels(self):
        try:
            used_channels, used_drum_notes, channel_programs = self.processor.scan_channels(self.file_path)
            
            for widget in self.map_scroll.winfo_children(): widget.destroy()
            self.mapping_comboboxes.clear()
            
            options_synth = ["Bỏ qua (Mute)"] + [f"🎹 Tổng hợp: {k} (Gõ {v})" for k, v in MW_SYNTH.items()]
            options_electronic = [f"⚡ Điện tử: {k} (Gõ {v})" for k, v in MW_ELECTRONIC.items()]
            options_drum = ["Bỏ qua (Mute)"] + [f"🥁 Trống: {k} (Gõ {v})" for k, v in MW_DRUMS.items()]
            all_synth_options = options_synth + options_electronic
            
            for ch in used_channels:
                frame_row = ctk.CTkFrame(self.map_scroll)
                frame_row.pack(fill="x", pady=5, padx=10) # Default pack options
                
                prog = channel_programs[ch]
                display_name = f"🎹 {GM_INSTRUMENTS[prog]}" if 0 <= prog < len(GM_INSTRUMENTS) else f"🎹 Nhạc cụ (Prog {prog})"
                lbl_name = ctk.CTkLabel(frame_row, text=f"Ch {ch+1}: {display_name}", width=250, anchor="w", font=ctk.CTkFont(weight="bold"))
                lbl_name.pack(side="left", padx=10, pady=10)
                
                combo = ctk.CTkComboBox(frame_row, values=all_synth_options, width=300)
                p_name = display_name.lower()
                if "bass" in p_name and "drum" not in p_name:
                    combo.set("⚡ Điện tử: Guitar Bass Điện (Gõ 0)")
                elif "harpsichord" in p_name or "clav" in p_name:
                    combo.set("⚡ Điện tử: Harpsichord (Gõ 7)")
                elif any(x in p_name for x in ["bell", "glockenspiel", "celesta", "music box", "vibraphone", "xylophone", "tubular"]):
                    combo.set("⚡ Điện tử: Chuông Điện Tử (Gõ 5)")
                elif "square" in p_name or "calliope" in p_name:
                    combo.set("⚡ Điện tử: Stylophone (Gõ 3)")
                elif any(x in p_name for x in ["synth", "pad", "lead", "charang"]):
                    combo.set("⚡ Điện tử: Pluck Synth (Gõ 1)")
                elif "guitar" in p_name:
                    if "nylon" in p_name or "steel" in p_name or "acoustic" in p_name:
                        combo.set("🎹 Tổng hợp: Guitar Mộc (Gõ 7)")
                    else:
                        combo.set("🎹 Tổng hợp: Guitar (Gõ 1)")
                elif "violin" in p_name or "string" in p_name:
                    combo.set("🎹 Tổng hợp: Violin (Gõ 3)")
                elif "harp" in p_name:
                    combo.set("🎹 Tổng hợp: Harp (Gõ 2)")
                elif "trumpet" in p_name or "brass" in p_name:
                    combo.set("🎹 Tổng hợp: Trumpet (Gõ 4)")
                elif "flute" in p_name or "recorder" in p_name:
                    combo.set("🎹 Tổng hợp: Recorder (Gõ 5)")
                else:
                    combo.set("🎹 Tổng hợp: Piano (Gõ 0)")
                combo.pack(side="right", padx=10, pady=10)
                self.mapping_comboboxes.append({'channel': ch, 'is_drum': False, 'drum_note': None, 'combo': combo, 'frame': frame_row, 'pady': 5, 'padx': 10})

            if used_drum_notes:
                lbl_drum_title = ctk.CTkLabel(self.map_scroll, text="--- CHI TIẾT BỘ TRỐNG (Kênh 10) ---", text_color=COLOR_ACCENT_2, font=ctk.CTkFont(weight="bold"))
                lbl_drum_title.pack(pady=(15, 5))
                for note in used_drum_notes:
                    frame_row = ctk.CTkFrame(self.map_scroll)
                    frame_row.pack(fill="x", pady=2, padx=10)
                    
                    drum_name = GM_DRUM_MAP.get(note, f"Unknown Drum ({note})")
                    lbl_name = ctk.CTkLabel(frame_row, text=f"🥁 Nốt {note}: {drum_name}", width=250, anchor="w", font=ctk.CTkFont(weight="bold"))
                    lbl_name.pack(side="left", padx=10, pady=10)
                    combo = ctk.CTkComboBox(frame_row, values=options_drum, width=300)
                    
                    mw_drum_name = self.active_drum_map.get(note)
                    if mw_drum_name:
                        for option in options_drum:
                            if mw_drum_name in option:
                                combo.set(option); break

                    combo.pack(side="right", padx=10, pady=10)
                    self.mapping_comboboxes.append({'channel': 9, 'is_drum': True, 'drum_note': note, 'combo': combo, 'frame': frame_row, 'pady': 2, 'padx': 10})
                
            self.frame_input.pack_forget()
            self.frame_mapping.pack(fill="both", expand=True, padx=20, pady=20)
        except Exception as e:
            messagebox.showerror("Lỗi Quét MIDI", f"Đã xảy ra lỗi khi quét file MIDI:\n\n{e}")

    def save_mapping_config(self):
        if not self.mapping_comboboxes:
            messagebox.showwarning("Chưa có cấu hình", "Không có thông tin map nhạc cụ để lưu.")
            return
        
        config_data = []
        for item in self.mapping_comboboxes:
            identifier = f"drum_{item['drum_note']}" if item['is_drum'] else f"ch_{item['channel']}"
            config_data.append({
                'id': identifier,
                'value': item['combo'].get()
            })

        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Config", "*.json")],
            title="Lưu Cấu Hình Mapping",
            initialfile="my_mapping_config.json",
            initialdir=self.last_directory
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(config_data, f, indent=4)
                messagebox.showinfo("Thành công", f"Đã lưu cấu hình vào:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể lưu file cấu hình:\n{e}")

    def load_mapping_config(self):
        if not self.mapping_comboboxes:
            messagebox.showwarning("Chưa có nhạc cụ", "Vui lòng chọn file MIDI trước khi tải cấu hình.")
            return

        file_path = filedialog.askopenfilename(filetypes=[("JSON Config", "*.json")], title="Tải Cấu Hình Mapping", initialdir=self.last_directory)
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                config_map = {item['id']: item['value'] for item in config_data}
                loaded_count = 0
                for item in self.mapping_comboboxes:
                    identifier = f"drum_{item['drum_note']}" if item['is_drum'] else f"ch_{item['channel']}"
                    if identifier in config_map and config_map[identifier] in item['combo'].cget('values'):
                        item['combo'].set(config_map[identifier])
                        loaded_count += 1
                messagebox.showinfo("Hoàn tất", f"Đã tải và áp dụng thành công {loaded_count} mục cấu hình.")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể đọc hoặc áp dụng file cấu hình:\n{e}")

    def process_mapping_and_convert(self):
        self.transpose_semitones = 0
        if hasattr(self, 'lbl_pitch') and self.lbl_pitch:
            self.lbl_pitch.configure(text="Pitch: 0")

        self.mw_channel_programs.clear()
        self.channel_map = {}
        for item in self.mapping_comboboxes:
            val = item['combo'].get()
            if "Bỏ qua" in val: continue
            
            map_key = f"9_{item['drum_note']}" if item['is_drum'] else f"{item['channel']}_ALL"
            
            # Phân tích chuỗi để lấy tên và số lần gõ, xử lý được các tên có dấu ngoặc đơn
            full_name_part = val.split(":")[1].strip()
            last_paren_index = full_name_part.rfind('(')
            name = full_name_part[:last_paren_index].strip()
            tap_part = full_name_part[last_paren_index:]
            tap = int(tap_part.split("Gõ")[1].replace(")", "").strip())

            if item['is_drum']:
                name = val.split(":")[1].split("(")[0].strip()
                tap = int(val.split("Gõ")[1].replace(")", "").strip())
                display_name = f"🥁 {name} ({tap})"
                inst_type = "Drum"
            else: # Synth hoặc Electronic
                is_synth = "Tổng hợp" in val or "🎹" in val
                name = val.split(":")[1].split("(")[0].strip()
                tap = int(val.split("Gõ")[1].replace(")", "").strip())
                emoji = "🎹" if is_synth else "⚡"
                display_name = f"{emoji} {name} ({tap})"
                inst_type = "Synth"

            self.channel_map[map_key] = {
                "type": inst_type,
                "name": name, "tap": tap,
                "display_name": display_name
            }
        
        simplification_options = {
            'enabled': self.simplify_enabled_var.get(),
            'time_ms': int(self.simplify_time_var.get() or 0),
            'velocity': int(self.simplify_velocity_var.get() or 0)
        }

        self.frame_mapping.pack_forget()
        self.lbl_now_playing.configure(text="Đang xử lý...")
        threading.Thread(target=self._build_initial_data_thread, args=(simplification_options,), daemon=True).start()

    def _build_initial_data_thread(self, simplification_options):
        try:
            self.original_notes, self.full_midi_events, self.midi_metadata = self.processor.build_note_list(self.file_path, self.channel_map, simplification_options)
            if not self.original_notes:
                self.after(0, lambda: messagebox.showerror("Lỗi", "Không tìm thấy nốt nhạc nào có thể map trong file MIDI này."))
                return
            self.after(0, self.render_gui_initial)
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Lỗi Xử Lý File", f"Không thể xử lý file MIDI:\n\n{e}"))

    def update_active_blueprint(self):
        was_playing = self.is_playing
        if was_playing:
            self.playback_offset = self.start_offset + (time.perf_counter() - self.start_perf) * 1000.0 * self.playback_speed
            self.is_playing = False
            
        self.active_blueprint = self.generator.create_blueprint(
            self.original_notes, self.channel_map, self.selected_instruments, self.transpose_semitones, self.mw_drum_to_gm_note
        )

        self.render_active_sheet()
        self.update_stats_tab()
        self.sync_playback_indices()
        self._last_highlight_idx = None
        self.apply_sync_visuals()
        
        if was_playing:
            self.start_offset = self.playback_offset
            self.start_perf = time.perf_counter()
            self.is_playing = True
            threading.Thread(target=self._audio_playback_thread, daemon=True).start()

    def render_gui_initial(self):
        self.lbl_now_playing.configure(text=os.path.basename(self.file_path))
        self.frame_output.pack(fill="both", expand=True, padx=10, pady=10)
        
        for w in self.sheet_checkboxes_frame.winfo_children(): w.destroy()
        self.checkbox_vars.clear()
        
        unique_targets = list(set(v["display_name"] for v in self.channel_map.values()))
        self.available_instruments = sorted(unique_targets)
        self.selected_instruments = set(self.available_instruments)
        
        for inst in self.available_instruments:
            var = ctk.BooleanVar(value=True)
            self.checkbox_vars[inst] = var
            chk = ctk.CTkCheckBox(self.sheet_checkboxes_frame, text=inst, variable=var, font=ctk.CTkFont(weight="bold"), command=lambda n=inst: self.on_checkbox_change(n))
            chk.pack(side="left", padx=10, pady=5)
            
        max_time = self.original_notes[-1]['time'] if self.original_notes else 0
        self.slider_time.configure(to=max_time + 1000)
        self.update_active_blueprint()
        self.jump_to_start()

        # Configure minimap after everything is drawn
        self.canvas.configure(xscrollcommand=self._on_canvas_scrolled)
        self.scrollbar_x.configure(command=self._on_horizontal_scroll)

    def on_tab_change(self):
        if self.tabview.get() == "Sơ đồ Ngang":
            self._draw_minimap()
            self._update_minimap_viewport()

    def on_checkbox_change(self, inst_name):
        if self.checkbox_vars[inst_name].get(): self.selected_instruments.add(inst_name)
        else: self.selected_instruments.discard(inst_name)
        self.update_active_blueprint()
        
    def select_all_sheets(self):
        for name, var in self.checkbox_vars.items():
            var.set(True)
            self.selected_instruments.add(name)
        self.update_active_blueprint()
        
    def clear_all_sheets(self):
        for name, var in self.checkbox_vars.items(): var.set(False)
        self.selected_instruments.clear()
        self.update_active_blueprint()

    def render_active_sheet(self):
        bp = self.active_blueprint
        
        self.txt_vert.configure(state="normal")
        self.txt_vert.delete("1.0", "end")
        self.txt_vert_line_map.clear()
        
        vert_lines = []
        current_line = 1
        col_w = 26
        
        for item in bp:
            insts = list(item['instruments'].keys())
            if not insts: continue
            
            vert_lines.append(f"[ CỤM {item['id']} ]\n")
            
            headers = []
            for inst in insts:
                clean_inst = inst.replace("🎹 ", "").replace("🥁 ", "").replace("⚡ ", "")
                headers.append(f"{clean_inst:^{col_w}}")
            vert_lines.append(f"|{'|'.join(headers)}|\n")
            
            max_r = max(len(d['notes_raw']) for d in item['instruments'].values())
            for r in range(max_r):
                r_strs = []
                for inst in insts:
                    note = item['instruments'][inst]['notes_raw'][r] if r < len(item['instruments'][inst]['notes_raw']) else ""
                    r_strs.append(f"{note:^{col_w}}")
                vert_lines.append(f"|{'|'.join(r_strs)}|\n")
            
            vert_lines.append("-" * (len(insts) * (col_w + 1) + 1) + "\n")
            vert_lines.append(f"➔ Dây tiếp: {item['wire']}\n")
            vert_lines.append("\n") 
            
            lines_added = max_r + 5
            self.txt_vert_line_map.append((current_line, current_line + max_r + 3))
            current_line += lines_added

        self.txt_vert.insert("1.0", "".join(vert_lines))
        self.txt_vert.configure(state="disabled")

        self.canvas.delete("all")
        self.canvas_rects.clear()
        if not bp: return
        
        try: self.canvas_frame.update_idletasks(); frame_h = max(200, self.canvas_frame.winfo_height())
        except: frame_h = 700

        box_heights = []
        for item in bp:
            h = 50
            for inst, data in item['instruments'].items():
                h += 30 + math.ceil(len(", ".join(data['notes_raw'])) / 35) * 22
            box_heights.append(max(120, h + 10))

        line_y = frame_h // 2
        card_center_y = line_y - (max(box_heights) // 2) - 20
        self.canvas.create_line(0, line_y, len(bp) * (self.card_width + 80), line_y, fill="#333333", width=8)

        def bind_click(item_id, idx):
            self.canvas.tag_bind(item_id, "<Button-1>", lambda e, i=idx: self.on_item_click(idx=i))
            
        def bind_hover(rect_id, idx):
            self.canvas.tag_bind(rect_id, "<Enter>", lambda e: self.canvas.itemconfig(rect_id, outline="#00e5ff", width=4) if idx != getattr(self, '_last_highlight_idx', -1) else None)
            self.canvas.tag_bind(rect_id, "<Leave>", lambda e: self.canvas.itemconfig(rect_id, outline="#555555", width=2) if idx != getattr(self, '_last_highlight_idx', -1) else None)

        x_offset = 40
        for i, item in enumerate(bp):
            box_h = box_heights[i]
            box_y = int(card_center_y - (box_h // 2))

            rect_id = self.canvas.create_rectangle(x_offset, box_y, x_offset + self.card_width, box_y + box_h, fill="#242424", outline="#555555", width=2)
            self.canvas_rects.append({'bg': rect_id})
            
            title_id = self.canvas.create_text(x_offset + self.card_width//2, box_y + 20, text=f"CỤM {item['id']}", fill="white", font=("Arial", 16, "bold"))
            
            bind_click(rect_id, i)
            bind_click(title_id, i)
            self.canvas.tag_bind(rect_id, "<Double-Button-1>", lambda e, idx=i: self.jump_to_step(idx, auto_play_note=True))
            bind_hover(rect_id, i)

            y_text = box_y + 45
            for inst, data in item['instruments'].items():
                is_synth = "🎹" in inst
                inst_color = "#17a2b8" if is_synth else "#e83e8c"
                
                inst_id = self.canvas.create_text(x_offset + 15, y_text, text=inst, fill=inst_color, font=("Arial", 13, "bold"), anchor="w")
                bind_click(inst_id, i)
                y_text += 20
                
                notes_str = ", ".join(data['notes_raw'])
                notes_id = self.canvas.create_text(x_offset + 25, y_text, text=notes_str, fill="#cccccc", font=("Arial", 11), anchor="nw", width=self.card_width-40)
                bind_click(notes_id, i)
                
                y_text += math.ceil(len(notes_str) / 35) * 20 + 10

            if i < len(bp) - 1:
                self.canvas.create_line(x_offset + self.card_width, line_y, x_offset + self.card_width + 80, line_y, fill="#ffc107", width=6, arrow="last", arrowshape=(16, 20, 6))
                label_y = box_y - 16 if (box_y - 16) > 8 else line_y - 25
                self.canvas.create_text(x_offset + self.card_width + 40, label_y, text=item['wire'], fill="#ffc107", font=("Arial", 16, "bold"))
            x_offset += self.card_width + 80

        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        self._draw_minimap()
        self._update_minimap_viewport()

    def _draw_minimap(self):
        self.minimap_canvas.delete("all")
        bp = self.active_blueprint
        if not bp: return

        self.minimap_canvas.update_idletasks()
        canvas_w = self.minimap_canvas.winfo_width()
        total_w = len(bp) * (self.card_width + 80)
        if total_w == 0 or canvas_w <= 1: return
        
        scale = canvas_w / total_w
        
        for i, item in enumerate(bp):
            x0 = i * (self.card_width + 80) * scale
            x1 = x0 + self.card_width * scale
            self.minimap_canvas.create_rectangle(x0, 5, x1, 45, fill="#242424", outline="#555555", tags="minimap_item")

        self.minimap_viewport = self.minimap_canvas.create_rectangle(0, 2, 0, 48, outline=self.COLOR_ACCENT_1, width=2)
        self.minimap_canvas.bind("<Button-1>", self._on_minimap_click_drag)
        self.minimap_canvas.bind("<B1-Motion>", self._on_minimap_click_drag)

    def _update_minimap_viewport(self):
        start_frac, end_frac = self.canvas.xview()
        minimap_w = self.minimap_canvas.winfo_width()
        x0, x1 = start_frac * minimap_w, end_frac * minimap_w
        self.minimap_canvas.coords(self.minimap_viewport, x0, 2, x1, 48)

    def update_stats_tab(self):
        """Tính toán và hiển thị các thông số chi tiết của bản nhạc trong tab Thống kê."""
        # Helper to create an expandable list for top stats
        def _add_expandable_stat_list(parent, title, items, unit_label):
            if not items:
                return

            stat_frame = ctk.CTkFrame(parent, fg_color="transparent")
            stat_frame.pack(fill="x", pady=2, padx=20)

            header_frame = ctk.CTkFrame(stat_frame, fg_color="transparent")
            header_frame.pack(fill="x")

            ctk.CTkLabel(header_frame, text=title, anchor="w").pack(side="left")

            details_frame = ctk.CTkFrame(stat_frame, fg_color="#343638")
            details_frame.pack(fill="x", pady=(5, 0), padx=(20, 0))
            details_frame.pack_forget()

            for i, (count, cluster_id) in enumerate(items[1:10], start=2):
                rank_frame = ctk.CTkFrame(details_frame, fg_color="transparent")
                rank_frame.pack(fill="x", padx=10, pady=1)
                ctk.CTkLabel(rank_frame, text=f"#{i}:", anchor="w", width=40, font=ctk.CTkFont(slant="italic")).pack(side="left")
                ctk.CTkLabel(rank_frame, text=f"{count} {unit_label} (tại Cụm {cluster_id})", anchor="e", font=ctk.CTkFont(weight="normal")).pack(side="right", fill="x", expand=True)

            def toggle_details():
                if details_frame.winfo_viewable(): details_frame.pack_forget(); expand_btn.configure(text="Mở rộng")
                else: details_frame.pack(fill="x", pady=(5, 0), padx=(20, 0)); expand_btn.configure(text="Thu gọn")

            expand_btn = ctk.CTkButton(header_frame, text="Mở rộng", width=80, height=24, command=toggle_details, fg_color="transparent", border_width=1, text_color=("gray70", "gray30"))
            expand_btn.pack(side="right", padx=(5, 0))
            if len(items) <= 1: expand_btn.pack_forget()

            top_count, top_cluster_id = items[0]
            ctk.CTkLabel(header_frame, text=f"{top_count} {unit_label} (tại Cụm {top_cluster_id})", anchor="e", font=ctk.CTkFont(weight="bold")).pack(side="right", fill="x", expand=True)

        # Helper to create a section
        def _add_section(parent, title):
            frame = ctk.CTkFrame(parent, fg_color=COLOR_BG_SECTION)
            frame.pack(fill="x", pady=(10, 5), padx=5) # This color is static, no need to update
            label = ctk.CTkLabel(frame, text=title, font=ctk.CTkFont(size=18, weight="bold"), text_color=COLOR_ACCENT_1)
            label.pack(pady=5, padx=10, anchor="w")
            return frame

        # Helper to add a stat entry
        def _add_entry(parent, label_text, value_text):
            frame = ctk.CTkFrame(parent, fg_color="transparent")
            frame.pack(fill="x", pady=2, padx=20)
            ctk.CTkLabel(frame, text=label_text, anchor="w").pack(side="left")
            ctk.CTkLabel(frame, text=str(value_text), anchor="e", font=ctk.CTkFont(weight="bold")).pack(side="right")

        # Clear previous stats
        for widget in self.stats_scroll_frame.winfo_children():
            widget.destroy()

        bp = self.active_blueprint
        if not bp:
            ctk.CTkLabel(self.stats_scroll_frame, text="Không có dữ liệu để hiển thị.\nHãy chọn các nhạc cụ và chuyển đổi.", font=ctk.CTkFont(size=16)).pack(pady=20)
            return

        # --- CALCULATIONS ---

        # 1. General Stats
        total_clusters = len(bp)
        total_instruments_used = len(self.selected_instruments)
        total_time_ms = bp[-1]['sync_time'] if bp else 0
        minutes, seconds = divmod(total_time_ms / 1000, 60)
        total_time_str = f"{int(minutes):02d}:{seconds:05.2f}"
        initial_bpm = 60_000_000 / self.midi_metadata.get('initial_tempo', 500000)

        # 2. Note and Cluster Stats
        total_notes = 0
        instrument_note_counts = {name: 0 for name in self.selected_instruments}
        cluster_note_counts = []
        cluster_instrument_counts = []

        for item in bp:
            current_cluster_notes = 0
            num_instruments = len(item['instruments'])
            cluster_instrument_counts.append((num_instruments, item['id']))

            for inst_name, data in item['instruments'].items():
                num_notes = len(data['notes'])
                current_cluster_notes += num_notes
                if inst_name in instrument_note_counts:
                    instrument_note_counts[inst_name] += num_notes

            total_notes += current_cluster_notes
            cluster_note_counts.append((current_cluster_notes, item['id']))

        avg_notes_per_cluster = total_notes / total_clusters if total_clusters > 0 else 0

        # Sort the lists to find top clusters
        cluster_note_counts.sort(key=lambda x: x[0], reverse=True)
        cluster_instrument_counts.sort(key=lambda x: x[0], reverse=True)

        # 3. Wire Stats
        wire_counts = {"Mức 0": 0, "Mức 1": 0, "Mức 2": 0, "Mức 3": 0, "Mức 4": 0, "Mức 5": 0, "PL": 0, "Sát nhau": 0}
        for item in bp:
            if item['wire'] == '[HẾT BÀI]': continue
            wire_str = item.get('wire', '')
            parts = [p.strip() for p in wire_str.split('+')]
            for part in parts:
                if "Sát nhau" in part: wire_counts["Sát nhau"] += 1
                elif "PL" in part: wire_counts["PL"] += 1
                elif "Mức" in part:
                    try:
                        tokens = part.split(' ')
                        if tokens[0] == 'Mức': # Format "Mức 5"
                            level = f"Mức {tokens[1]}"
                            if level in wire_counts: wire_counts[level] += 1
                        else: # Format "N Mức X"
                            count = int(tokens[0])
                            level = f"Mức {tokens[2]}"
                            if level in wire_counts: wire_counts[level] += count
                    except (IndexError, ValueError): pass

        # --- RENDER UI ---
        sec_overview = _add_section(self.stats_scroll_frame, "📈 Tổng Quan")
        _add_entry(sec_overview, "Tổng số cụm:", f"{total_clusters} cụm")
        _add_entry(sec_overview, "Tổng số nốt nhạc:", f"{total_notes} nốt")
        _add_entry(sec_overview, "Tổng số nhạc cụ sử dụng:", f"{total_instruments_used} loại")
        _add_entry(sec_overview, "Tổng thời gian:", total_time_str)
        _add_entry(sec_overview, "Tempo ban đầu (ước tính):", f"~{initial_bpm:.1f} BPM")
        _add_entry(sec_overview, "Nhịp ban đầu:", self.midi_metadata.get('initial_time_signature', 'N/A'))

        sec_cluster = _add_section(self.stats_scroll_frame, "🔬 Phân Tích Cụm")
        _add_entry(sec_cluster, "Số nốt trung bình / cụm:", f"{avg_notes_per_cluster:.2f}")
        _add_expandable_stat_list(sec_cluster, "Nhiều nốt nhất trong 1 cụm:", cluster_note_counts, "nốt")
        _add_expandable_stat_list(sec_cluster, "Nhiều nhạc cụ nhất trong 1 cụm:", cluster_instrument_counts, "nhạc cụ")

        sec_wire = _add_section(self.stats_scroll_frame, "🔌 Thống Kê Dây Nối")
        for level in range(5, -1, -1):
            _add_entry(sec_wire, f"Tổng số Mức {level}:", f"{wire_counts[f'Mức {level}']} dây")
        _add_entry(sec_wire, "Tổng số dây 1 PL:", f"{wire_counts['PL']} dây")
        _add_entry(sec_wire, "Tổng số dây 'Sát nhau':", f"{wire_counts['Sát nhau']} dây")

        pie_chart_frame = ctk.CTkFrame(sec_wire, fg_color="transparent", height=300)
        pie_chart_frame.pack(fill="x", expand=True, pady=10, padx=5)
        self.generate_wire_pie_chart(pie_chart_frame, wire_counts)

        sec_instruments = _add_section(self.stats_scroll_frame, "🎼 Thống Kê Nhạc Cụ")
        
        instrument_chart_frame = ctk.CTkFrame(sec_instruments, fg_color="transparent", height=300)
        instrument_chart_frame.pack(fill="x", expand=True, pady=10, padx=5)
        self.generate_instrument_bar_chart(instrument_chart_frame, instrument_note_counts)

        sorted_instruments = sorted(instrument_note_counts.items(), key=lambda item: item[1], reverse=True)
        for inst_name, count in sorted_instruments:
            if count > 0: _add_entry(sec_instruments, f"{inst_name}:", f"{count} nốt")


    def generate_wire_pie_chart(self, parent, wire_counts):
        for widget in parent.winfo_children():
            widget.destroy()

        labels, sizes = [], []
        for key, value in wire_counts.items():
            if value > 0:
                labels.append(key)
                sizes.append(value)

        if not sizes:
            ctk.CTkLabel(parent, text="Không có dữ liệu dây nối để vẽ biểu đồ.").pack(pady=20)
            return

        try:
            fig = Figure(figsize=(5, 4), dpi=100)
            fig.patch.set_facecolor(self.COLOR_BG_MAIN)
            ax = fig.add_subplot(111)

            explode = [0] * len(sizes)
            if sizes:
                max_index = sizes.index(max(sizes))
                explode[max_index] = 0.1

            wedges, _, autotexts = ax.pie(sizes, explode=explode, labels=None, autopct='%1.1f%%',
                                          shadow=False, startangle=140, pctdistance=0.85,
                                          wedgeprops={'edgecolor': 'white'})

            for text in autotexts:
                text.set_color('white')
                text.set_fontsize(10)
                text.set_fontweight('bold')

            ax.axis('equal')
            
            ax.legend(wedges, labels, title="Loại Dây Nối", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1),
                      facecolor="#343638", labelcolor='white', edgecolor='gray')
            
            fig.suptitle('Tỷ Lệ Các Loại Dây Nối', color='white', fontsize=16, fontweight='bold')
            fig.tight_layout(rect=[0, 0, 0.75, 1])

            canvas = FigureCanvasTkAgg(fig, master=parent)
            canvas.draw()
            canvas.get_tk_widget().pack(side="top", fill="both", expand=True, padx=5, pady=5)
        except Exception as e:
            ctk.CTkLabel(parent, text=f"Lỗi vẽ biểu đồ:\n{e}").pack(pady=20)

    def generate_instrument_bar_chart(self, parent, inst_counts):
        for widget in parent.winfo_children():
            widget.destroy()

        sorted_counts = sorted(inst_counts.items(), key=lambda item: item[1], reverse=False)
        labels = [item[0].replace("🎹 ", "").replace("🥁 ", "").replace("⚡ ", "") for item in sorted_counts if item[1] > 0]
        sizes = [item[1] for item in sorted_counts if item[1] > 0]

        if not sizes: return

        try:
            fig = Figure(figsize=(5, max(4, len(labels) * 0.4)), dpi=100)
            fig.patch.set_facecolor(self.COLOR_BG_MAIN)
            ax = fig.add_subplot(111)
            ax.set_facecolor(self.COLOR_BG_SECTION)

            y_pos = np.arange(len(labels))
            bars = ax.barh(y_pos, sizes, align='center', color=self.COLOR_SYNTH)
            ax.set_yticks(y_pos, labels=labels)
            ax.invert_yaxis()
            ax.set_xlabel('Số Lượng Nốt', color='white')
            ax.set_title('Phân Bố Nốt Nhạc Theo Nhạc Cụ', color='white', fontweight='bold')
            ax.tick_params(axis='x', colors='white')
            ax.tick_params(axis='y', colors='white')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_color('gray')
            ax.spines['left'].set_color('gray')
            fig.tight_layout()

            canvas = FigureCanvasTkAgg(fig, master=parent)
            canvas.draw()
            canvas.get_tk_widget().pack(side="top", fill="both", expand=True, padx=5, pady=5)
        except Exception as e:
            ctk.CTkLabel(parent, text=f"Lỗi vẽ biểu đồ:\n{e}").pack(pady=20)

    def _update_time_display(self, current_ms):
        if not hasattr(self, 'lbl_time') or self.lbl_time is None:
            return

        def format_ms(ms):
            if ms < 0: ms = 0
            minutes, seconds = divmod(ms / 1000, 60)
            return f"{int(minutes):02d}:{seconds:05.2f}"

        total_ms = self.slider_time.cget("to")
        if total_ms <= 0: total_ms = self.original_notes[-1]['time'] if self.original_notes else 0
        
        self.lbl_time.configure(text=f"{format_ms(current_ms)} / {format_ms(total_ms)}")

    def export_vertical_to_txt(self):
        """Lưu nội dung của Sơ đồ Dọc vào một file .txt."""
        if not self.active_blueprint:
            messagebox.showwarning("Không có dữ liệu", "Không có dữ liệu sơ đồ để xuất.")
            return

        initial_filename = f"Sơ đồ - {os.path.basename(self.file_path or 'Untitled')}.txt"
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            title="Lưu Sơ Đồ Dọc",
            initialfile=initial_filename,
            initialdir=self.last_directory
        )
        
        if file_path:
            try:
                content = self.txt_vert.get("1.0", "end")
                with open(file_path, "w", encoding="utf-8") as f: f.write(content)
                messagebox.showinfo("Thành công", f"Đã xuất sơ đồ ra file:\n{file_path}")
            except Exception as e: messagebox.showerror("Lỗi", f"Không thể xuất file:\n{e}")
    # =========================================================
    # AUDIO VÀ TIMBRE: KHỞI TẠO ÂM THANH CHO TỪNG NHẠC CỤ
    # =========================================================

    def play_mixed_instruments(self, inst_dict):
        """Phát âm thanh mô phỏng Mini World bằng bộ synth MIDI của hệ điều hành."""
        if not self.has_midi_output or not inst_dict: return

        DRUM_PREVIEW_CHANNEL = 15 # Sử dụng một kênh riêng cho preview trống
        DRUM_PREVIEW_PROGRAM = 117 # GM Melodic Tom, một âm thanh gõ có cao độ

        if self.mw_channel_programs.get(DRUM_PREVIEW_CHANNEL) != DRUM_PREVIEW_PROGRAM:
            self.midi_out.set_instrument(DRUM_PREVIEW_PROGRAM, DRUM_PREVIEW_CHANNEL)
            self.mw_channel_programs[DRUM_PREVIEW_CHANNEL] = DRUM_PREVIEW_PROGRAM

        def turn_off_notes(notes_to_turn_off):
            time.sleep(0.15)  # Thời gian ngân để tạo cảm giác gõ block
            for note, channel in notes_to_turn_off:
                self.midi_out.note_off(note, 0, channel)

        notes_to_turn_off = []
        for inst_name, data in inst_dict.items():
            inst_type = data.get("type", "Synth")
            for note_info in data['notes']:
                note = note_info['midi']
                channel = note_info['channel']
                base_name = data.get('name')
                if not base_name: continue
                
                if inst_type == "Drum":
                    # Use the pre-calculated GM note for preview
                    velocity = 127 if base_name == "Jam-block" else 100
                    self.midi_out.note_on(note, velocity, 9) # Kênh 9 cho trống
                    notes_to_turn_off.append((note, 9))
                else:
                    gm_program = self.mw_instrument_to_gm.get(base_name, 0)
                    
                    if self.mw_channel_programs.get(channel) != gm_program:
                        self.midi_out.set_instrument(gm_program, channel)
                        self.mw_channel_programs[channel] = gm_program
                        
                    self.midi_out.note_on(note, 100, channel)
                    notes_to_turn_off.append((note, channel))

        if notes_to_turn_off:
            threading.Thread(target=turn_off_notes, args=(notes_to_turn_off,), daemon=True).start()

    # =========================================================
    # BỘ ĐIỀU KHIỂN VÀ SỰ KIỆN UI
    # =========================================================
    def on_item_click(self, event=None, idx=None):
        """Xử lý sự kiện click vào một cụm trong sơ đồ."""
        bp = self.active_blueprint
        if idx is not None and 0 <= idx < len(bp):
            self.current_step_index = idx
            try: self.slider_time.set(bp[idx]['sync_time'])
            except: pass
            self.apply_sync_visuals()
            self.play_mixed_instruments(bp[idx]['instruments'])

    def on_txt_vert_click(self, event):
        """Xử lý sự kiện click trên sơ đồ dọc."""
        idx_click = int(self.txt_vert.index(f"@{event.x},{event.y}").split('.')[0])
        for i, (start_l, end_l) in enumerate(self.txt_vert_line_map):
            if start_l <= idx_click <= end_l:
                self.on_item_click(idx=i); break

    def on_txt_vert_double_click(self, event):
        idx_click = int(self.txt_vert.index(f"@{event.x},{event.y}").split('.')[0])
        """Xử lý sự kiện double-click trên sơ đồ dọc để nhảy tới cụm."""
        for i, (start_l, end_l) in enumerate(self.txt_vert_line_map):
            if start_l <= idx_click <= end_l:
                self.jump_to_step(i, auto_play_note=True); break

    def jump_to_step(self, idx, auto_play_note=False):
        """Nhảy tới một cụm (step) cụ thể trong bản nhạc."""
        bp = self.active_blueprint
        if idx < 0 or idx >= len(bp): return
        
        was_playing = self.is_playing; self.is_playing = False 
        self.current_step_index = idx
        self.playback_offset = bp[idx]['sync_time']
        self._update_time_display(self.playback_offset)
        self.slider_time.set(self.playback_offset)
        
        self._resync_midi_output()
        self.apply_sync_visuals()
                
        if auto_play_note:
            self.play_mixed_instruments(bp[idx]['instruments'])

        if was_playing:
            # If it was playing, resume it
            self.start_offset = self.playback_offset
            self.start_perf = time.perf_counter()
            self.is_playing = True
            threading.Thread(target=self._audio_playback_thread, daemon=True).start()
        else: self.is_paused = False 

    def manual_change_step(self, direction): self.jump_to_step(self.current_step_index + direction, auto_play_note=True)
    def jump_to_start(self): self.jump_to_step(0)

    def toggle_play(self):
        """Bật/tắt phát nhạc."""
        if self.is_playing:
            self.is_playing = False; self.is_paused = True
            self.btn_play.configure(text="▶ Phát")
            # Dừng toàn bộ nốt nhạc để tránh bị treo âm
            if self.has_midi_output:
                for chan in range(16):
                    self.midi_out.write_short(0b10110000 | chan, 123, 0) # All notes off
            self.synth_channel.stop()
            self.playback_offset = self.start_offset + (time.perf_counter() - self.start_perf) * 1000.0 * self.playback_speed
        else:
            self.start_offset = self.playback_offset; self.start_perf = time.perf_counter()
            self.is_playing = True; self.is_paused = False
            self.btn_play.configure(text="⏸ Tạm Dừng")
            threading.Thread(target=self._audio_playback_thread, daemon=True).start()
            self._ui_update_loop()

    def on_slider_seek(self, value):
        """Xử lý sự kiện khi người dùng kéo thanh trượt thời gian."""
        was_playing = self.is_playing; self.is_playing = False
        self.playback_offset = float(value)
        self._update_time_display(self.playback_offset)
        
        self._resync_midi_output()

        closest_idx = 0
        for i, item in enumerate(self.active_blueprint):
            if item['sync_time'] > self.playback_offset:
                closest_idx = max(0, i - 1); break
        
        self.current_step_index = closest_idx
        self.apply_sync_visuals()
        
        if was_playing:
            self.start_offset = self.playback_offset; self.start_perf = time.perf_counter()
            self.is_playing = True
            threading.Thread(target=self._audio_playback_thread, daemon=True).start()
        else: self.is_paused = False

    def _resync_midi_output(self):
        if self.has_midi_output:
            # 1. Dừng tất cả các nốt đang phát
            for chan in range(16):
                self.midi_out.write_short(0b10110000 | chan, 123, 0) # All notes off

            # 2. Xây dựng lại trạng thái kênh (program, control change) cho đến điểm seek
            for event in self.full_midi_events:
                if event['time'] >= self.playback_offset:
                    break
                msg = event['msg']
                if msg.type in ['program_change', 'control_change', 'pitchwheel']:
                    map_key = f"{msg.channel}_ALL"
                    if map_key in self.channel_map:
                        try:
                            b = msg.bytes()
                            self.midi_out.write_short(b[0], b[1] if len(b) > 1 else 0, b[2] if len(b) > 2 else 0)
                        except: pass
        
        self.sync_playback_indices()

    def sync_playback_indices(self):
        self.next_midi_event_idx = len(self.full_midi_events)
        for i, event in enumerate(self.full_midi_events):
            if event['time'] >= self.playback_offset: self.next_midi_event_idx = i; break

        self.next_mw_idx = len(self.active_blueprint)
        for i, item in enumerate(self.active_blueprint):
            if item['sync_time'] >= self.playback_offset: self.next_mw_idx = i; break

    def _audio_playback_thread(self):
        bp = self.active_blueprint
        while self.is_playing:
            current_ms = self.start_offset + (time.perf_counter() - self.start_perf) * 1000.0 * self.playback_speed
            
            while self.next_mw_idx < len(bp) and bp[self.next_mw_idx]['sync_time'] <= current_ms:
                if self.current_preview_mode == "🎹 Mini World":
                    self.play_mixed_instruments(bp[self.next_mw_idx]['instruments'])
                self.current_step_index = self.next_mw_idx
                self.next_mw_idx += 1
            
            while self.next_midi_event_idx < len(self.full_midi_events) and self.full_midi_events[self.next_midi_event_idx]['time'] <= current_ms:
                if self.current_preview_mode == "🎵 Nhạc MIDI Gốc" and self.has_midi_output:
                    event = self.full_midi_events[self.next_midi_event_idx]
                    original_msg = event['msg']
                    
                    map_key = f"9_{original_msg.note}" if original_msg.channel == 9 and original_msg.type.startswith('note') else f"{original_msg.channel}_ALL"
                    if map_key in self.channel_map:
                        try:
                            msg_to_send = original_msg
                            # Áp dụng transpose cho các nốt không phải trống
                            if original_msg.channel != 9 and original_msg.type in ('note_on', 'note_off'):
                                transposed_note = original_msg.note + self.transpose_semitones
                                if 0 <= transposed_note <= 127:
                                    msg_to_send = original_msg.copy(note=transposed_note)
                                else:
                                    continue # Bỏ qua nốt ngoài khoảng MIDI

                            b = msg_to_send.bytes()
                            if msg_to_send.type == 'note_on' and msg_to_send.velocity > 0:
                                balanced_velocity = 100
                                self.midi_out.write_short(b[0], b[1], balanced_velocity)
                            else:
                                self.midi_out.write_short(b[0], b[1] if len(b) > 1 else 0, b[2] if len(b) > 2 else 0)
                        except Exception: pass

                self.next_midi_event_idx += 1

            is_mw_end = self.next_mw_idx >= len(bp)
            is_midi_end = self.next_midi_event_idx >= len(self.full_midi_events)

            if is_mw_end and is_midi_end:
                # Đặt lại trạng thái MIDI khi hết bài
                if self.has_midi_output: self._resync_midi_output()
                self.is_playing = False
                self.after(0, lambda: self.btn_play.configure(text="▶ Phát"))
                break
            time.sleep(0.002)

    def _ui_update_loop(self):
        if self.is_playing:
            current_ms = self.start_offset + (time.perf_counter() - self.start_perf) * 1000.0 * self.playback_speed
            try: self.slider_time.set(current_ms)
            except: pass # Can fail if window is closing
            self._update_time_display(current_ms)
            self.apply_sync_visuals()
            self.after(33, self._ui_update_loop)

    def apply_sync_visuals(self):
        bp = self.active_blueprint
        idx = self.current_step_index
        if idx < 0 or idx >= len(bp): return
        
        if getattr(self, '_last_highlight_idx', None) == idx: return
        self._last_highlight_idx = idx
        data = bp[idx]
        
        self.lbl_step_num.configure(text=f"[ CỤM {data['id']} ]")
        self.lbl_step_wire.configure(text=f"➔ Dây tiếp: {data['wire']}")
        for w in self.frame_step_instruments.winfo_children(): w.destroy()
        
        for inst, inst_data in data['instruments'].items():
            is_synth = "🎹" in inst
            col_frame = ctk.CTkFrame(self.frame_step_instruments, fg_color="transparent")
            col_frame.pack(side="left", expand=True, fill="both", padx=10)
            
            lbl_title = ctk.CTkLabel(col_frame, text=inst, font=ctk.CTkFont(size=22, weight="bold"), text_color=COLOR_SYNTH if is_synth else COLOR_DRUM)
            lbl_title.pack(pady=10)
            
            for note in inst_data['notes_raw']:
                ctk.CTkLabel(col_frame, text=note, font=ctk.CTkFont(size=18, weight="bold")).pack(pady=3)
        
        if idx < len(self.txt_vert_line_map):
            start_l, end_l = self.txt_vert_line_map[idx]
            self.txt_vert.tag_remove("active_line", "1.0", "end")
            self.txt_vert.tag_add("active_line", f"{start_l}.0", f"{end_l}.end")
            self.txt_vert.see(f"{end_l}.end")
            self.txt_vert.see(f"{start_l}.0")
        
        for i, card_info in enumerate(self.canvas_rects):
            self.canvas.itemconfig(card_info['bg'], fill="#12505a" if i == idx else "#242424", outline="#00e5ff" if i == idx else "#555555", width=4 if i == idx else 2)
            
        if len(self.canvas_rects) > 0:
            total_width = len(self.canvas_rects) * (self.card_width + 80)
            if total_width == 0: return
            
            # Center the active card
            card_center_x = (idx * (self.card_width + 80)) + (self.card_width / 2)
            canvas_width = self.canvas.winfo_width()
            
            moveto_fraction = (card_center_x - (canvas_width / 2)) / total_width
            
            try: self.canvas.xview_moveto(max(0, min(1, moveto_fraction)))
            except: pass

    def change_preview_mode(self, mode):
        # This method is called by the segmented button
        self.current_preview_mode = mode
        # Xóa cache chương trình của chế độ Mini World để buộc đặt lại nhạc cụ
        self.mw_channel_programs.clear()
        # Đồng bộ lại sẽ reset tất cả controller và đặt lại đúng chương trình nhạc cụ
        self._resync_midi_output()

    def change_speed(self, choice, force_load=False):
        new_speed = float(choice.replace("x", ""))
        if new_speed == self.playback_speed and not force_load: return
        was_playing = self.is_playing
        if was_playing:
            self.playback_offset = self.start_offset + (time.perf_counter() - self.start_perf) * 1000.0 * self.playback_speed
            self.is_playing = False
        self.playback_speed = new_speed
        if was_playing:
            self.start_offset = self.playback_offset; self.start_perf = time.perf_counter()
            self.is_playing = True
            threading.Thread(target=self._audio_playback_thread, daemon=True).start()
            self._ui_update_loop()

    def back_to_input(self):
        self.is_playing = False; self.is_paused = False
        if self.midi_out:
            # Reset các kênh để tránh treo nốt
            for chan in range(16):
                self.midi_out.write_short(0b10110000 | chan, 123, 0) # All notes off
        self.frame_output.pack_forget(); self.frame_mapping.pack_forget()
        self.frame_input.pack(fill="both", expand=True, padx=20, pady=20)

    def increase_pitch(self): self.apply_transpose(1)
    def decrease_pitch(self): self.apply_transpose(-1)

    def apply_transpose(self, semitones):
        if not self.original_notes: return
        self.transpose_semitones += semitones
        if hasattr(self, 'lbl_pitch') and self.lbl_pitch:
            self.lbl_pitch.configure(text=f"Pitch: {self.transpose_semitones:+d}")
        self.update_active_blueprint()

    def open_settings(self):
        if not hasattr(self, 'settings_window') or not self.settings_window.winfo_exists():
            self.settings_window = SettingsWindow(self)
        self.settings_window.focus()

    def _create_default_drum_map(self):
        # Creates the default mapping from GM note to MW drum name
        mapping = {}
        for note in range(35, 82): # Standard GM drum notes
            if note in [35, 36]: mapping[note] = "Bass"
            elif note in [38, 40]: mapping[note] = "Lẫy"
            elif note in [42, 44, 46]: mapping[note] = "Hi-hat (đóng)"
            elif note in [41, 43, 45, 47, 48, 50]: mapping[note] = "Tom-tom"
            elif note in [49, 52, 55, 57]: mapping[note] = "Chũm choẹ to"
            elif note in [51, 53, 59]: mapping[note] = "Chũm choẹ trung"
            else: mapping[note] = "Jam-block"
        return mapping

    def _apply_theme(self, theme_name, first_load=False):
        self.current_theme_name = theme_name
        if theme_name == "Vàng Gold":
            self.COLOR_ACCENT_1 = "#ffc107"
            self.COLOR_SYNTH = "#ffb300"
            self.COLOR_DRUM = "#f06292"
            self.COLOR_INFO = "#ffb300"
            self.COLOR_INFO_HOVER = "#e6a100"
        elif theme_name == "Hồng Ruby":
            self.COLOR_ACCENT_1 = "#e91e63"
            self.COLOR_SYNTH = "#ec407a"
            self.COLOR_DRUM = "#ab47bc"
            self.COLOR_INFO = "#ec407a"
            self.COLOR_INFO_HOVER = "#d43a6f"
        else: # Default
            self.COLOR_ACCENT_1 = "#00e5ff"
            self.COLOR_SYNTH = "#17a2b8"
            self.COLOR_DRUM = "#e83e8c"
            self.COLOR_INFO = "#17a2b8"
            self.COLOR_INFO_HOVER = "#138496"
        
        if not first_load:
            self._reconfigure_colors()
    
    def _reconfigure_colors(self):
        # Re-configure all relevant widgets
        self.lbl_step_num.configure(text_color=self.COLOR_ACCENT_1)
        self.btn_select_all.configure(fg_color=self.COLOR_INFO, hover_color=self.COLOR_INFO_HOVER)
        self.btn_increase.configure(fg_color=self.COLOR_INFO)
        
        # Redraw elements that depend on colors
        if self.active_blueprint:
            self.update_stats_tab()
            self.render_active_sheet()
            self.apply_sync_visuals()

    def _on_canvas_scrolled(self, *args):
        """Called when the main canvas is scrolled."""
        self.scrollbar_x.set(*args)
        self._update_minimap_viewport()

    def _on_horizontal_scroll(self, *args):
        """Called when the scrollbar is moved."""
        self.canvas.xview(*args)
        self._update_minimap_viewport()

    def _on_minimap_click_drag(self, event):
        """Called when the minimap is clicked or dragged."""
        self.minimap_canvas.update_idletasks()
        frac = event.x / self.minimap_canvas.winfo_width()
        self.canvas.xview_moveto(frac)
        self._update_minimap_viewport()

    def show_help(self):
        if hasattr(self, 'help_window') and self.help_window.winfo_exists():
            self.help_window.focus()
            return

        self.help_window = ctk.CTkToplevel(self)
        self.help_window.title("Trợ Giúp & Giới Thiệu")
        self.help_window.geometry("700x600")
        self.help_window.transient(self)

        textbox = ctk.CTkTextbox(self.help_window, wrap="word", font=("Arial", 14))
        textbox.pack(fill="both", expand=True, padx=10, pady=10)

        textbox.insert("1.0", HELP_TEXT)
        textbox.configure(state="disabled")

if __name__ == "__main__":
    try: app = MiniWorldConverterApp(); app.mainloop()
    except Exception as e: print("Ứng dụng dừng với lỗi:", e)