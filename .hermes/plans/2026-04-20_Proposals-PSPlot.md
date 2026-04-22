# PSPlot Improvement Roadmap - April 2026

Berdasarkan arsitektur saat ini dan kebutuhan riset HVDC, berikut adalah rekomendasi pengembangan fitur untuk PSPlot guna meningkatkan fungsionalitas dan efisiensi kerja Pak Roni:

## 1. Analisis Sinyal (Power System focus)
- **FFT Analysis Window**: Menambahkan mode tampilan FFT untuk melihat konten harmonisa dari sinyal yang sedang di-zoom. Berguna untuk analisis kontrol konverter HVDC.
- **Filtering Modules**: Implementasi On-the-fly filtering (Moving Average, Low-Pass Butterworth) untuk membersihkan sinyal yang noise tanpa mengubah data asli.
- **THD Calculation**: Perhitungan otomatis *Total Harmonic Distortion* pada kursor pengukuran.

## 2. Peningkatan Interaksi Data
- **Hover/Data Inquiry Tool**: Fitur untuk melihat nilai koordinat (x, y) secara akurat saat mouse diletakkan di atas garis sinyal (tooltip), tanpa harus menarik kursor permanen.
- **Search & Filter di Signal Explorer**: Jika file `.inf` berisi ratusan signal, fitur pencarian di dialog Explorer akan sangat membantu mempercepat pemilihan.
- **Multi-File Comparison (Overlay Mode)**: Fitur untuk membandingkan dua file simulasi yang berbeda (misalnya: 'Scenario_A.out' vs 'Scenario_B.out') dalam satu plot secara otomatis untuk melihat dampak perubahan parameter.

## 3. UI & Layout Flexibility
- **Adjustable Subplot Heights**: Slider untuk mengubah ukuran tinggi subplot secara dinamis (saat ini statis dibagi rata).
- **Drag-and-Drop Reordering**: Kemampuan untuk memindah atau menukar signal antar subplot hanya dengan menarik label di legend atau item di manager.

## 4. Efisiensi Alur Kerja (Workflow)
- **Session Templating (.psp/.json)**: Kemampuan untuk menyimpan seluruh layout (jumlah subplot, signal yang dipilih, zoom, warna) ke dalam sebuah file template. Ini memungkinkan Pak Roni membuka data simulasi baru namun langsung menggunakan layout yang sudah rapi dari simulasi sebelumnya.
- **Batch Export to PDF**: Tombol untuk memproses seluruh folder hasil simulasi PSCAD menjadi satu file laporan PDF dengan format seragam.
- **LaTeX Integration**: Link otomatis untuk me-generate perintah `\includegraphics` atau kode TikZ/PGFPlots bagi Bapak yang menulis paper di Overleaf.

## 5. Performance Improvements
- **Background Loading**: Memindahkan proses `pandas.read_csv` ke *worker thread* agar UI PSPlot tidak "freeze" sesaat saat membaca file `.out` yang ukurannya sangat besar (>500MB).

---
*Status: Ini adalah dokumen rencana pengembangan. Pilih fitur yang paling prioritas untuk kita prioritaskan implementasinya.*
