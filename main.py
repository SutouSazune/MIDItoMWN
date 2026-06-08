import customtkinter as ctk
from tkinter import filedialog
import mido
import threading
import pygame
import time
import os
import io
import wave
import math
import pygame.midi
import numpy as np 

# =========================================================
# THÔNG SỐ CỐT LÕI & DATA NHẠC CỤ
# =========================================================
HE_SO_TOC_DO = 1.0

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

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class MiniWorldConverterApp(ctk.CTk):
    """
    Ứng dụng chuyển đổi file MIDI thành sơ đồ khối nhạc cho Mini World.

    Bao gồm các tính năng map nhạc cụ, hiển thị sơ đồ đa dạng,
    và trình phát nhạc với hai chế độ để nghe thử bản gốc và bản chuyển đổi.
    """
    def __init__(self):
        super().__init__()
        self.title("MIDI to Mini World Noteblock")
        self.geometry("1400x950")
        
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
        self.setup_mapping_screen()
        self.setup_output_screen()
        
        self.frame_mapping.pack_forget()
        self.frame_output.pack_forget()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        if self.midi_out:
            self.midi_out.close()
        if pygame.midi.get_init():
            pygame.midi.quit()
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
        self.map_scroll.pack(pady=10, fill="y", expand=True)
        self.btn_start_convert = ctk.CTkButton(self.frame_mapping, text="⚡ Bắt Đầu Chuyển Đổi", width=250, height=50, font=ctk.CTkFont(size=18, weight="bold"), command=self.process_mapping_and_convert, fg_color="#28a745", hover_color="#218838")
        self.btn_start_convert.pack(pady=30)
        self.mapping_comboboxes = []

    def setup_output_screen(self):
        self.frame_output = ctk.CTkFrame(self)
        self.top_bar = ctk.CTkFrame(self.frame_output, fg_color="transparent")
        self.top_bar.pack(fill="x", padx=10, pady=5)
        self.btn_back = ctk.CTkButton(self.top_bar, text="← Tệp", width=100, corner_radius=8, fg_color="#2b2b2b", hover_color="#3a3a3a", cursor="hand2", command=self.back_to_input)
        self.btn_back.pack(side="left")
        self.lbl_now_playing = ctk.CTkLabel(self.top_bar, text="", font=ctk.CTkFont(weight="bold", size=20))
        self.lbl_now_playing.pack(side="left", fill="x", expand=True)

        self.sheet_panel = ctk.CTkFrame(self.frame_output, height=60)
        self.sheet_panel.pack(fill="x", padx=10, pady=5)
        self.lbl_sheet = ctk.CTkLabel(self.sheet_panel, text="Hiển thị Bản vẽ:", font=ctk.CTkFont(weight="bold", size=15))
        self.lbl_sheet.pack(side="left", padx=15, pady=10)
        self.btn_select_all = ctk.CTkButton(self.sheet_panel, text="Chọn Tất Cả", width=100, fg_color="#17a2b8", hover_color="#138496", command=self.select_all_sheets)
        self.btn_select_all.pack(side="left", padx=5)
        self.btn_clear_all = ctk.CTkButton(self.sheet_panel, text="Bỏ Chọn", width=90, fg_color="#6c757d", hover_color="#5a6268", command=self.clear_all_sheets)
        self.btn_clear_all.pack(side="left", padx=5)
        self.sheet_checkboxes_frame = ctk.CTkScrollableFrame(self.sheet_panel, orientation="horizontal", height=45, fg_color="transparent")
        self.sheet_checkboxes_frame.pack(side="left", fill="x", expand=True, padx=10)

        self.tabview = ctk.CTkTabview(self.frame_output)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=5)
        self.tab_vert = self.tabview.add("Sơ đồ Dọc")
        self.tab_horz = self.tabview.add("Sơ đồ Ngang")
        self.tab_step = self.tabview.add("Sơ đồ Đơn")
        
        self.txt_vert = ctk.CTkTextbox(self.tab_vert, font=ctk.CTkFont(family="Consolas", size=16), wrap="none", cursor="hand2")
        self.txt_vert.pack(fill="both", expand=True, padx=5, pady=5)
        self.txt_vert.tag_config("active_line", background="#12505a", foreground="white")
        self.txt_vert.bind("<Button-1>", self.on_txt_vert_click)
        self.txt_vert.bind("<Double-Button-1>", self.on_txt_vert_double_click)
        
        self.canvas_frame = ctk.CTkFrame(self.tab_horz)
        self.canvas_frame.pack(fill="both", expand=True)
        self.canvas = ctk.CTkCanvas(self.canvas_frame, bg="#121212", highlightthickness=0)
        self.scrollbar_x = ctk.CTkScrollbar(self.canvas_frame, orientation="horizontal", command=self.canvas.xview)
        self.canvas.configure(xscrollcommand=self.scrollbar_x.set)
        self.canvas.pack(side="top", fill="both", expand=True)
        self.scrollbar_x.pack(side="bottom", fill="x")
        self.canvas.bind("<MouseWheel>", lambda e: self.canvas.xview_scroll(int(-1 * (e.delta / 120)), "units"))
        
        self.frame_step = ctk.CTkFrame(self.tab_step, corner_radius=10)
        self.frame_step.pack(fill="both", expand=True, padx=20, pady=20)
        self.frame_step_header = ctk.CTkFrame(self.frame_step, fg_color="transparent")
        self.frame_step_header.pack(fill="x", pady=(20, 10))
        self.lbl_step_num = ctk.CTkLabel(self.frame_step_header, text="[ CỤM 000 ]", font=ctk.CTkFont(size=36, weight="bold"), text_color="#00e5ff")
        self.lbl_step_num.pack()
        self.frame_step_instruments = ctk.CTkFrame(self.frame_step, fg_color="transparent")
        self.frame_step_instruments.pack(expand=True, fill="both", padx=20)
        self.lbl_step_wire = ctk.CTkLabel(self.frame_step, text="➔ Dây: ...", font=ctk.CTkFont(size=30, weight="bold"), text_color="#ffc107")
        self.lbl_step_wire.pack(pady=(10, 30))

        self.music_panel = ctk.CTkFrame(self.frame_output, height=90)
        self.music_panel.pack(fill="x", padx=10, pady=(0, 10))
        
        self.btn_reset = ctk.CTkButton(self.music_panel, text="⏮", width=50, corner_radius=10, command=self.jump_to_start)
        self.btn_reset.pack(side="left", padx=(20, 5), pady=20)
        self.btn_prev = ctk.CTkButton(self.music_panel, text="◀◀", width=50, corner_radius=10, command=lambda: self.manual_change_step(-1))
        self.btn_prev.pack(side="left", padx=5, pady=20)
        self.btn_play = ctk.CTkButton(self.music_panel, text="▶ Phát", width=140, corner_radius=12, fg_color="#28a745", hover_color="#218838", font=ctk.CTkFont(weight="bold", size=18), command=self.toggle_play)
        self.btn_play.pack(side="left", padx=5, pady=20)
        self.btn_next = ctk.CTkButton(self.music_panel, text="▶▶", width=50, corner_radius=10, command=lambda: self.manual_change_step(1))
        self.btn_next.pack(side="left", padx=5, pady=20)
        self.mode_switch = ctk.CTkSegmentedButton(self.music_panel, values=["🎵 Nhạc MIDI Gốc", "🎹 Mini World"], command=self.change_preview_mode)
        self.mode_switch.set("🎵 Nhạc MIDI Gốc")
        self.mode_switch.pack(side="left", padx=20, pady=20)
        self.combo_speed = ctk.CTkComboBox(self.music_panel, values=["0.5x", "0.75x", "1.0x", "1.25x", "1.5x"], width=90, command=self.change_speed)
        self.combo_speed.set("1.0x")
        self.combo_speed.pack(side="left", padx=5, pady=20)
        self.btn_decrease = ctk.CTkButton(self.music_panel, text="⇩", width=50, corner_radius=10, fg_color="#ff6b6b", command=self.decrease_pitch)
        self.btn_decrease.pack(side="left", padx=5, pady=20)
        self.btn_increase = ctk.CTkButton(self.music_panel, text="⇧", width=50, corner_radius=10, fg_color="#6c8cff", command=self.increase_pitch)
        self.btn_increase.pack(side="left", padx=5, pady=20)
        self.slider_time = ctk.CTkSlider(self.music_panel, from_=0, to=100, command=self.on_slider_seek)
        self.slider_time.set(0)
        self.slider_time.pack(side="left", fill="x", expand=True, padx=20, pady=20)

    # =========================================================
    # QUÉT FILE & MAPPING NHẠC CỤ
    # =========================================================
    def select_file(self):
        """Mở hộp thoại chọn file MIDI và bắt đầu quá trình quét."""
        path = filedialog.askopenfilename(filetypes=[("MIDI", "*.mid *.midi")])
        if path:
            self.file_path = path
            self.lbl_file.configure(text=os.path.basename(path))
            self.scan_midi_channels()

    def scan_midi_channels(self):
        try:
            mid = mido.MidiFile(self.file_path)
            used_channels = set()
            used_drum_notes = set()
            channel_programs = {i: 0 for i in range(16)}
            
            for msg in mido.merge_tracks(mid.tracks):
                if msg.type == 'program_change':
                    channel_programs[msg.channel] = msg.program
                elif msg.type == 'note_on' and msg.velocity > 0:
                    if msg.channel == 9: used_drum_notes.add(msg.note)
                    else: used_channels.add(msg.channel)
            
            for widget in self.map_scroll.winfo_children(): widget.destroy()
            self.mapping_comboboxes.clear()
            
            options_synth = ["Bỏ qua (Mute)"] + [f"🎹 Tổng hợp: {k} (Gõ {v})" for k, v in MW_SYNTH.items()]
            options_electronic = [f"⚡ Điện tử: {k} (Gõ {v})" for k, v in MW_ELECTRONIC.items()]
            options_drum = ["Bỏ qua (Mute)"] + [f"🥁 Trống: {k} (Gõ {v})" for k, v in MW_DRUMS.items()]
            all_synth_options = options_synth + options_electronic
            
            for ch in sorted(list(used_channels)):
                frame_row = ctk.CTkFrame(self.map_scroll)
                frame_row.pack(fill="x", pady=5, padx=10)
                
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
                self.mapping_comboboxes.append({'channel': ch, 'is_drum': False, 'drum_note': None, 'combo': combo})

            if used_drum_notes:
                lbl_drum_title = ctk.CTkLabel(self.map_scroll, text="--- CHI TIẾT BỘ TRỐNG (Kênh 10) ---", text_color="#ffc107", font=ctk.CTkFont(weight="bold"))
                lbl_drum_title.pack(pady=(15, 5))
                for note in sorted(list(used_drum_notes)):
                    frame_row = ctk.CTkFrame(self.map_scroll)
                    frame_row.pack(fill="x", pady=2, padx=10)
                    drum_name = GM_DRUM_MAP.get(note, f"Unknown Drum ({note})")
                    lbl_name = ctk.CTkLabel(frame_row, text=f"🥁 Nốt {note}: {drum_name}", width=250, anchor="w", font=ctk.CTkFont(weight="bold"))
                    lbl_name.pack(side="left", padx=10, pady=10)
                    combo = ctk.CTkComboBox(frame_row, values=options_drum, width=300)
                    if note in [35, 36]: combo.set("🥁 Trống: Bass (Gõ 0)")
                    elif note in [38, 40]: combo.set("🥁 Trống: Lẫy (Gõ 3)")
                    elif note in [42, 44, 46]: combo.set("🥁 Trống: Hi-hat (đóng) (Gõ 4)")
                    elif note in [41, 43, 45, 47, 48, 50]: combo.set("🥁 Trống: Tom-tom (Gõ 2)")
                    elif note in [49, 52, 55, 57]: combo.set("🥁 Trống: Chũm choẹ to (Gõ 6)")
                    elif note in [51, 53, 59]: combo.set("🥁 Trống: Chũm choẹ trung (Gõ 5)")
                    else: combo.set("🥁 Trống: Jam-block (Gõ 7)")
                    combo.pack(side="right", padx=10, pady=10)
                    self.mapping_comboboxes.append({'channel': 9, 'is_drum': True, 'drum_note': note, 'combo': combo})
                
            self.frame_input.pack_forget()
            self.frame_mapping.pack(fill="both", expand=True, padx=20, pady=20)
        except Exception as e: print("Lỗi quét MIDI:", e)

    def process_mapping_and_convert(self):
        self.mw_channel_programs.clear()
        self.channel_map = {}
        for item in self.mapping_comboboxes:
            val = item['combo'].get()
            if "Bỏ qua" in val: continue
            
            is_synth = "Tổng hợp" in val or "🎹" in val
            is_electronic = "Điện tử" in val or "⚡" in val
            name = val.split(":")[1].split("(")[0].strip()
            tap = int(val.split("Gõ")[1].replace(")", "").strip())
            map_key = f"9_{item['drum_note']}" if item['is_drum'] else f"{item['channel']}_ALL"
            
            inst_type = "Drum"
            emoji = "🥁"
            if is_synth or is_electronic:
                inst_type = "Synth"
            
            if is_synth: emoji = "🎹"
            elif is_electronic: emoji = "⚡"

            self.channel_map[map_key] = {
                "type": inst_type,
                "name": name, "tap": tap,
                "display_name": f"{emoji} {name} ({tap})"
            }
        
        self.frame_mapping.pack_forget()
        threading.Thread(target=self.build_initial_data, daemon=True).start()

    def build_initial_data(self):
        try:
            mid = mido.MidiFile(self.file_path)
            absolute_time = 0
            tempo = 500000
            self.original_notes.clear()
            self.full_midi_events.clear()
            current_programs = {i: 0 for i in range(16)}
            
            for msg in mido.merge_tracks(mid.tracks):
                absolute_time += mido.tick2second(msg.time, mid.ticks_per_beat, tempo) * 1000
                
                if not msg.is_meta:
                    self.full_midi_events.append({'time': absolute_time, 'msg': msg})
                if msg.type == 'set_tempo':
                    tempo = msg.tempo
                elif msg.type == 'program_change':
                    current_programs[msg.channel] = msg.program
                elif msg.type == 'note_on' and msg.velocity > 0:
                    map_key = f"9_{msg.note}" if msg.channel == 9 else f"{msg.channel}_ALL"
                    if map_key in self.channel_map:
                        self.original_notes.append({
                            'time': absolute_time, 'note': msg.note, 'velocity': msg.velocity,
                            'channel': msg.channel, 'map_key': map_key,
                            'program': current_programs.get(msg.channel, 0)
                        })
            
            if not self.original_notes: return
            self.after(0, self.render_gui_initial)
        except Exception as e: print(f"Lỗi tạo data: {e}")

    def update_active_blueprint(self):
        was_playing = self.is_playing
        if was_playing:
            self.playback_offset = self.start_offset + (time.perf_counter() - self.start_perf) * 1000.0 * self.playback_speed
            self.is_playing = False
            
        target_notes = [n for n in self.original_notes if self.channel_map[n['map_key']]["display_name"] in self.selected_instruments]
        self.active_blueprint.clear()
        
        if target_notes:
            groups, current_group = [], [0]
            for i in range(1, len(target_notes)):
                if target_notes[i]['time'] - target_notes[current_group[-1]]['time'] < 30:
                    current_group.append(i)
                else:
                    groups.append(current_group); current_group = [i]
            groups.append(current_group)

            for gi, grp in enumerate(groups):
                time_sync = target_notes[grp[0]]['time']
                inst_data = {}
                
                for idx in grp:
                    n = target_notes[idx]
                    map_info = self.channel_map[n['map_key']]
                    inst_name = map_info["display_name"]
                    
                    if inst_name not in inst_data:
                        inst_data[inst_name] = {
                            "notes_raw": [],
                            "notes": [],
                            "type": map_info["type"]
                        }
                        
                    if map_info["type"] == "Synth":
                        note_val = n['note']
                        while note_val < 48: note_val += 12 # Transpose up to C3
                        while note_val > 83: note_val -= 12 # Transpose down to B5
                        tap = note_val % 12
                        b = "Trầm" if note_val <= 59 else "Trung" if note_val <= 71 else "Cao"
                        inst_data[inst_name]["notes_raw"].append(f"Khối {b}: {tap}")
                        inst_data[inst_name]["notes"].append({'midi': note_val, 'channel': n['channel']})
                    else:
                        inst_data[inst_name]["notes_raw"].append(f"[Trống] Gõ {map_info['tap']}")
                        inst_data[inst_name]["notes"].append({'midi': n['note'], 'channel': 9})
                
                for name in inst_data:
                    inst_data[name]["notes_raw"] = list(dict.fromkeys(inst_data[name]["notes_raw"]))
                    inst_data[name]["notes"] = list({(d['midi'], d['channel']): d for d in inst_data[name]["notes"]}.values())
                
                wire_str = "[HẾT BÀI]"
                if gi < len(groups) - 1:
                    d_ms = target_notes[groups[gi+1][0]]['time'] - time_sync
                    w_ms = max(0, (d_ms * HE_SO_TOC_DO) - 50)

                    # Ngưỡng w_ms mà tại đó Mức 0 bắt đầu
                    MUC0_START_W_MS = 825 

                    if w_ms < 30:
                        wire_str = "Sát nhau"
                    elif w_ms < 100:
                        wire_str = "1 PL"
                    elif w_ms < MUC0_START_W_MS: # Logic cũ cho Mức 5 -> 1
                        ticks = int(round(w_ms / 150.0))
                        level = 5 - (ticks - 1)
                        wire_str = f"Mức {level}"
                    else: # Logic mới để phân rã các khoảng trễ rất dài (>= Mức 0)
                        MUC0_UNIT_VALUE = MUC0_START_W_MS
                        
                        num_muc0 = int(w_ms // MUC0_UNIT_VALUE)
                        rem_w_ms = w_ms % MUC0_UNIT_VALUE
                        
                        parts = [f"{num_muc0} Mức 0"] if num_muc0 > 0 else []
                        
                        # Phân loại phần dư (rem_w_ms sẽ luôn < 825)
                        if rem_w_ms >= 100: # Phần dư là một Mức (5 -> 1)
                            rem_ticks = int(round(rem_w_ms / 150.0))
                            parts.append(f"1 Mức {5 - (rem_ticks - 1)}")
                        elif rem_w_ms >= 30: # Phần dư là 1 PL
                            parts.append("1 PL")
                            
                        wire_str = " + ".join(parts) if parts else "Mức 0"

                self.active_blueprint.append({
                    "id": f"{gi+1:03d}", "sync_time": time_sync,
                    "instruments": inst_data, "wire": wire_str
                })

        self.render_active_sheet()
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

    # =========================================================
    # AUDIO VÀ TIMBRE: KHỞI TẠO ÂM THANH CHO TỪNG NHẠC CỤ
    # =========================================================

    def play_mixed_instruments(self, inst_dict):
        """Phát âm thanh mô phỏng Mini World bằng bộ synth MIDI của hệ điều hành."""
        if not self.has_midi_output or not inst_dict: return

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
                
                if inst_type == "Drum":
                    base_name = inst_name.split('(')[0].strip().replace('🥁 ', '')
                    velocity = 127 if base_name == "Jam-block" else 100
                    playback_note = self.mw_drum_to_gm_note.get(base_name, note)
                    self.midi_out.note_on(playback_note, velocity, 9) # Kênh 9 cho trống
                    notes_to_turn_off.append((playback_note, 9))
                else:
                    base_name = inst_name.split('(')[0].strip().replace('🎹 ', '').replace('⚡ ', '')
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
        self.slider_time.set(self.playback_offset)
        
        self._resync_midi_output()
        self.apply_sync_visuals()
                
        if auto_play_note:
            self.play_mixed_instruments(bp[idx]['instruments'])

        if was_playing:
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
                    msg = event['msg']
                    
                    map_key = f"9_{msg.note}" if msg.channel == 9 and msg.type.startswith('note') else f"{msg.channel}_ALL"
                    if map_key in self.channel_map:
                        try:
                            b = msg.bytes()
                            if msg.type == 'note_on' and msg.velocity > 0:
                                # Cân bằng âm lượng: đặt một vận tốc (velocity) cố định
                                balanced_velocity = 100
                                self.midi_out.write_short(b[0], b[1], balanced_velocity)
                            else:
                                self.midi_out.write_short(b[0], b[1] if len(b) > 1 else 0, b[2] if len(b) > 2 else 0)
                        except Exception: pass # Bỏ qua các message MIDI không hợp lệ

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
            try: self.slider_time.set(self.start_offset + (time.perf_counter() - self.start_perf) * 1000.0 * self.playback_speed)
            except: pass
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
            
            lbl_title = ctk.CTkLabel(col_frame, text=inst, font=ctk.CTkFont(size=22, weight="bold"), text_color="#17a2b8" if is_synth else "#e83e8c")
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
            try: self.canvas.xview_moveto(max(0, (idx * (self.card_width + 80)) / (len(self.canvas_rects) * (self.card_width + 80))))
            except: pass

    def change_preview_mode(self, mode):
        self.current_preview_mode = mode
        if self.has_midi_output:
            # Reset toàn bộ nốt và controller để chuẩn bị cho chế độ mới
            for chan in range(16):
                self.midi_out.write_short(0b10110000 | chan, 123, 0) # All notes off
                self.midi_out.write_short(0b10110000 | chan, 121, 0) # Reset all controllers
            self.mw_channel_programs.clear()

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
        for n in self.original_notes:
            if n['channel'] != 9: n['note'] = int(n.get('note', 0) + semitones)
        self.update_active_blueprint()

if __name__ == "__main__":
    try: app = MiniWorldConverterApp(); app.mainloop()
    except Exception as e: print("Ứng dụng dừng với lỗi:", e)