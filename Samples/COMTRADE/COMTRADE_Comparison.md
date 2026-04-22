# Comparison of IEEE COMTRADE Standards (1991, 1999, 2013)

This document provides a technical comparison of the three major revisions of the IEEE C37.111 standard for Common Format for Transient Data Exchange (COMTRADE).

## 1. Version Identification in .CFG File
The first line of the configuration (.CFG) file indicates the standard version.

| Feature | 1991 Standard | 1999 Standard | 2013 Standard |
| :--- | :--- | :--- | :--- |
| **Line 1 Structure** | `station_name, rec_dev_id` | `station_name, rec_dev_id, rev_year` | `station_name, rec_dev_id, rev_year` |
| **Typical Value** | (2 fields) | `..., 1999` | `..., 2013` |

## 2. Channel Configuration (Analog)
| Standard | Attributes per Analog Channel |
| :--- | :--- |
| **1991** | `index, ch_id, ph, cc, uu, a, b, skew, min, max` |
| **1999 / 2013** | `index, ch_id, ph, ccbm, uu, a, b, skew, min, max, primary, secondary, PS` |

### Detailed Attribute Definition (Analog)
| Atribut | Nama Lengkap | Penjelasan |
| :--- | :--- | :--- |
| **`index`** | Channel Index | Nomor urut channel (1, 2, 3, ...). |
| **`ch_id`** | Channel Identifier | Nama unik channel (e.g., `V_Line_1`). |
| **`ph`** | Phase | Identifikasi fasa (A, B, C, N). |
| **`ccbm`** | Circuit Component | Nama peralatan/sirkuit yang dipantau. |
| **`uu`** | Units | Satuan fisik (e.g., `kV`, `V`, `A`). |
| **`a`** | Multiplier (Gain) | Faktor pengali untuk konversi data ke nilai aktual. |
| **`b`** | Offset | Faktor penambahan (pergeseran titik nol). |
| **`skew`** | Time Skew | Pergeseran waktu (μs) antar channel. |
| **`min`** | Minimum Value | Nilai digital minimum data. |
| **`max`** | Maximum Value | Nilai digital maksimum data. |
| **`primary`** | Primary Ratio | Nilai nominal sisi primer trafo (CT/PT). |
| **`secondary`** | Secondary Ratio | Nilai nominal sisi sekunder trafo (CT/PT). |
| **`PS`** | P/S Identifier | **P**: Hasil adalah nilai Primer. **S**: Nilai Sekunder. |

## 3. Global Configuration Lines (Footer)
| Komponen | Nama Standar | Penjelasan |
| :--- | :--- | :--- |
| **Nominal Freq** | `lf` | Frekuensi sistem tenaga (e.g., `50` atau `60` Hz). |
| **Num Rates** | `nrates` | Jumlah perubahan kecepatan sampling dalam satu file. |
| **Sample Rate** | `samp, endsamp` | Kecepatan sampling (Hz) dan nomor sampel terakhir. |
| **Start Time** | `date, time` | Waktu sampel pertama (`dd/mm/yyyy,hh:mm:ss.ssssss`). |
| **Trigger Time** | `date, time` | Waktu saat gangguan/pemicu terjadi. |
| **File Type** | `ft` | Format file data: `ASCII` atau `BINARY`. |
| **Timemult** | `timemult` | (1999+) Faktor pengali kolom waktu (biasanya `1.0`). |
| **Time Code** | `time_code` | (2013+) Offset waktu dari UTC (e.g., `+07h00`). |
| **Local Code** | `local_code` | (2013+) Offset waktu lokal ke UTC. |
| **TMQ Code** | `tmq_code` | (2013+) Indikator kualitas waktu (0-F). |
| **Leapsec** | `leapsec` | (2013+) Status detik kabisat. |

---

## 7. Literal CFG Examples

### IEEE C37.111-1991 (Example from `SEL.CFG`)
```cfg
FID=SEL-351A-R101-V0,CID=C88C
11,11A,0D
1,IA,A,XFMR1,A,0.000436,-240,0,0,9999
...
60
1
480, 2
09/08/1991,10:25:32.000000
09/08/1991,10:25:32.000000
BINARY
```

### IEEE C37.111-1999 (Example from `RECORD1.CFG`)
```cfg
STATION_A, DEVICE_B, 1999
4, 2A, 2D
1,V_PH_A,A,BUS1,V,0.0165,0,0,-32767,32767,150,0.1,P
2,I_PH_A,A,BUS1,A,0.0055,0,0,-32767,32767,2000,5,S
1,TRIP,A,BUS1,0
2,CLOSE,A,BUS1,0
50
1
4000, 1000
05/11/1999,11:03:07.414000
05/11/1999,11:03:07.514000
BINARY
1.0
```

### IEEE C37.111-2013 (Representative Example)
```cfg
SUBSTATION_CENTRAL, IED_MODERN, 2013
4, 4A, 0D
1,V A,A,LINE1,V,1.0,0,0,-2147483648,2147483647,150,0.1,P
2,V B,B,LINE1,V,1.0,0,0,-2147483648,2147483647,150,0.1,P
3,V C,C,LINE1,V,1.0,0,0,-2147483648,2147483647,150,0.1,P
4,I A,A,LINE1,A,1.0,0,0,-2147483648,2147483647,2000,5,P
50
1
8000, 2000
15/05/2013,10:00:00.000000
15/05/2013,10:00:00.100000
FLOAT32
1.0
+07h00, 0
0,0
```

---
*Created for Pak Roni's PSPlot Research Workflow - April 2026*
