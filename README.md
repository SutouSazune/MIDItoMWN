# Công cụ Chuyển Đổi MIDI sang Sơ Đồ Khối Nhạc Mini World

Một công cụ được thiết kế để giúp người chơi Mini World: Block Art dễ dàng chuyển đổi các file nhạc MIDI thành các bản thiết kế (blueprint) chi tiết để xây dựng trong game.

## Tính Năng Nổi Bật

-   **Nhập File MIDI:** Dễ dàng tải lên các file có định dạng `.mid` hoặc `.midi`.
-   **Map Nhạc Cụ Thông Minh:**
    -   Tự động quét và nhận diện các kênh nhạc cụ và trống có trong file MIDI.
    -   Giao diện trực quan để người dùng map từng kênh MIDI với các khối nhạc cụ trong Mini World (Tổng hợp, Điện tử, Trống).
    -   Tự động đề xuất map nhạc cụ dựa trên tên của nhạc cụ gốc (ví dụ: "piano" sẽ được map với "Piano" của Mini World).
-   **Hiển Thị Sơ Đồ Đa Dạng:**
    -   **Sơ đồ Dọc:** Dạng văn bản chi tiết, hiển thị rõ từng nốt nhạc cần đặt cho mỗi nhạc cụ trong một cụm.
    -   **Sơ đồ Ngang:** Dạng timeline đồ họa, cho phép cuộn và xem toàn bộ bản nhạc một cách trực quan.
    -   **Sơ đồ Đơn:** Hiển thị chi tiết thông tin của một cụm nốt nhạc được chọn.
-   **Nghe Thử & Điều Khiển Trực Quan:**
    -   **Chế độ nghe thử kép:**
        -   `🎵 Nhạc MIDI Gốc`: Phát lại bản nhạc gốc bằng bộ tổng hợp MIDI của hệ điều hành.
        -   `🎹 Mini World`: Mô phỏng âm thanh khi chơi bằng các khối nhạc trong game.
    -   **Bộ điều khiển phát nhạc đầy đủ:** Play/Pause, tua đến đầu, chuyển tới/lui từng cụm, thanh trượt thời gian.
    -   Điều chỉnh **tốc độ phát** (0.5x đến 1.5x).
    -   Điều chỉnh **cao độ** (tăng/giảm tông) của toàn bộ bản nhạc.
-   **Lọc và Tùy Chỉnh:**
    -   Cho phép ẩn/hiện các nhạc cụ không mong muốn khỏi sơ đồ cuối cùng.

## Hướng Dẫn Sử Dụng
** Để hiểu thêm về Khối nhạc của Miniworld, hãy ghé qua wiki của dự án**
1.  Chạy file `main.py` để khởi động ứng dụng.
2.  Tại màn hình chính, nhấn nút **"📁 Chọn File"** và chọn một file MIDI từ máy tính của bạn.
3.  Màn hình **"CẤU HÌNH NHẠC CỤ"** sẽ hiện ra. Tại đây:
    -   Kiểm tra và tùy chỉnh các nhạc cụ Mini World tương ứng với mỗi kênh MIDI.
    -   Bạn có thể chọn "Bỏ qua (Mute)" để không chuyển đổi một kênh nào đó.
    -   Nhấn **"⚡ Bắt Đầu Chuyển Đổi"** sau khi hoàn tất.
4.  Tại màn hình kết quả:
    -   Sử dụng các tab **"Sơ đồ Dọc"**, **"Sơ đồ Ngang"**, **"Sơ đồ Đơn"** để xem bản thiết kế.
    -   Sử dụng bảng điều khiển nhạc ở dưới cùng để nghe thử và điều hướng bản nhạc.
    -   Dùng các checkbox ở trên để lọc hiển thị các nhạc cụ.

## Yêu Cầu

Để chạy ứng dụng, bạn cần cài đặt các thư viện Python sau:

```bash
pip install customtkinter mido pygame numpy
```

---
*Được phát triển để hỗ trợ cộng đồng sáng tạo của Mini World.*