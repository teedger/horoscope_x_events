# 🚀 Quick Start Guide

## Хурдан эхлэх - 5 минутад

### Урьдчилсан шаардлага

```bash
# Python 3.12+ шаардлагатай
python --version  # Python 3.12 эсвэл түүнээс дээш байх ёстой
```

### 1. Repository clone хийх

```bash
git clone https://github.com/yourusername/horoscope_x_events.git
cd horoscope_x_events
```

### 2. Virtual environment үүсгэх

```bash
# Mac/Linux
python3.12 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Dependencies суулгах

```bash
pip install -r requirements.txt
```

### 4. Өгөгдөл бэлдэх

**ЧУХАЛ:** `horoscope_list_20250112.json` файлаа `data/raw/` хавтаст хуулна уу.

```bash
# Жишээ:
cp /path/to/horoscope_list_20250112.json data/raw/
```

### 5. Шинжилгээ ажиллуулах

```bash
# Нэг удаа бүгдийг ажиллуулах
python src/main_analysis.py
```

Энэ нь автоматаар:
1. ✅ Сарны огноо хөрвүүлэх
2. ✅ Дэлхийн гамшигт үйл явдал цуглуулах
3. ✅ Өгөгдөл таарах
4. ✅ Статистик шинжилгээ хийх
5. ✅ Visualization үүсгэх

### 6. Үр дүн үзэх

```bash
# Mac/Linux
open results/visualizations/comprehensive_analysis.png

# Windows
start results/visualizations/comprehensive_analysis.png
```

---

## 📁 Үр дүнгүүд

Амжилттай дууссаны дараа дараах файлууд үүсгэгдэнэ:

```
horoscope_x_events/
├── data/
│   └── processed/
│       ├── lunar_bad_days_gregorian.csv      # Хөрвүүлсэн сарны өдрүүд
│       ├── world_disasters.csv                # Дэлхийн гамшигт үйл явдлууд
│       └── matched_events.csv                 # Таарсан өгөгдөл
│
└── results/
    ├── reports/
    │   └── statistical_results.json           # Статистик үр дүн
    └── visualizations/
        ├── comprehensive_analysis.png         # Нэгтгэсэн график
        ├── timeline.png                       # Timeline chart
        ├── heatmap.png                        # Heatmap
        ├── box_comparison.png                 # Box plot
        ├── event_distribution.png             # Event distribution
        └── statistical_summary.png            # Statistical summary
```

---

## 🔧 Алхам алхмаар ажиллуулах

Хэрэв нэг бүрчлэн шалгах гэж байвал:

```bash
# 1. Сарны огноо хөрвүүлэх
python src/1_lunar_converter.py

# 2. Үйл явдал цуглуулах
python src/2_event_scraper.py

# 3. Өгөгдөл таарах
python src/3_data_matcher.py

# 4. Статистик шинжилгээ
python src/4_statistical_analysis.py

# 5. Visualization
python src/5_visualization.py
```

---

## 🌐 Google Colab дээр ажиллуулах

1. `notebooks/analysis_colab.ipynb` файлыг Google Colab-д нээх
2. **Runtime > Run all** хийх
3. `horoscope_list_20250112.json` файлаа upload хийх
4. Үр дүнг харах!

**Colab Link:** [Open in Colab](https://colab.research.google.com/github/yourusername/horoscope_x_events/blob/main/notebooks/analysis_colab.ipynb)

---

## ❓ Түгээмэл асуултууд

### Q: "FileNotFoundError: horoscope_list_20250112.json"

**A:** Horoscope JSON файлаа `data/raw/` хавтаст хуулна уу.

```bash
cp /your/path/horoscope_list_20250112.json data/raw/
```

### Q: Өөр нэртэй файл ашиглах гэж байвал?

**A:** `--data-file` параметр ашиглана уу:

```bash
python src/main_analysis.py --data-file /path/to/your_file.json
```

### Q: Checkpoint-уудыг хэрхэн цэвэрлэх вэ?

**A:** `data/checkpoints/` хавтсыг устгана уу:

```bash
rm -rf data/checkpoints/
```

### Q: Бүгдийг дахин ажиллуулах (checkpoint-уудыг алгасахгүй)

**A:** `--no-skip` flag ашиглана уу:

```bash
python src/main_analysis.py --no-skip
```

---

## 🆘 Тусламж авах

```bash
python src/main_analysis.py --help
```

Эсвэл GitHub issues: https://github.com/yourusername/horoscope_x_events/issues

---

## 📊 Үр дүнгийн жишээ

Дууссаны дараа та дараах мэдээллийг харна:

```
╔══════════════════════════════════════════════════════════════╗
║         STATISTICAL ANALYSIS SUMMARY                          ║
╠══════════════════════════════════════════════════════════════╣
║  Total Events: 35                                             ║
║  Events on Bad Days: 8 (22.9%)                                ║
║  Overall Severity Mean: 45.67                                 ║
║                                                               ║
║  Bad Days Mean: 48.23                                         ║
║  Not Bad Days Mean: 44.82                                     ║
║  P-value: 0.2345                                              ║
║  Significant: NO                                              ║
╚══════════════════════════════════════════════════════════════╝
```

*(Жишээ үр дүн - бодит үр дүн өөр байж болно)*

---

## 💻 Системийн шаардлага

- **Python:** 3.12 эсвэл түүнээс дээш
- **RAM:** 2GB+
- **Диск:** 500MB+ чөлөөтэй зай
- **OS:** Mac, Linux, Windows

---

Асуулт байвал Issues хэсэгт бичнэ үү!
