import mido
from mido import Message, MidiFile, MidiTrack

def generate_stress_test():
    # 480 ticks = 500ms (tại tempo 120 BPM mặc định)
    # => 1 tick tương đương ~1.0416 ms
    mid = MidiFile(ticks_per_beat=480)
    track = MidiTrack()
    mid.tracks.append(track)

    # Đặt tempo 120 BPM
    track.append(mido.MetaMessage('set_tempo', tempo=500000, time=0))

    TOTAL_NOTES = 100000

    for i in range(TOTAL_NOTES):
        # Cao độ nhảy từ 0 đến 127 liên tục để test logic dịch quãng của GPU
        note_val = i % 127
        
        # Test ranh giới 30ms (CLUSTER_TIME_THRESHOLD)
        # 28 ticks ~= 29.1 ms (Dưới ngưỡng -> Cùng 1 cụm, Dây Sát nhau)
        # 30 ticks ~= 31.2 ms (Vượt ngưỡng -> Tách sang Cụm mới)
        delay_ticks = 28 if i % 2 == 0 else 30
        
        # Ghi nốt
        track.append(Message('note_on', note=note_val, velocity=100, time=delay_ticks))
        track.append(Message('note_off', note=note_val, velocity=0, time=0))

    filename = 'GPU_Stress_Test_100k.mid'
    mid.save(filename)
    print(f"🔥 Đã xuất lò file {filename} với {TOTAL_NOTES} nốt!")
    print("Ném ngay vào tool để xem GPU CuPy bẻ cụm có bị lệch nhịp nào không!")

if __name__ == "__main__":
    generate_stress_test()