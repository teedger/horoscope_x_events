# 🌙 Mongolian Lunar Calendar vs World Disasters Analysis

**Монголын сарны календарийн "муу өдөр" ба дэлхийн гамшигт үйл явдлын хоорондын корреляц**

## 📊 Төслийн тойм

Энэ төсөл нь Монголын сарны календарийн "муу өдрүүд" (modon_days, ters_days) болон дэлхийн бодит гамшигт үйл явдлуудын хооронд статистик хамаарал байгаа эсэхийг шинжлэх ухааны аргаар судалдаг.

### Судлах асуултууд:
- ❓ Муу өдрүүдэд гамшигт үйл явдал илүү их гардаг уу?
- ❓ Ямар төрлийн үйл явдлууд хамгийн их таардаг вэ?
- ❓ Статистик хувьд ямар нотолгоо байгаа вэ?

## 📅 Өгөгдлийн хамрах хүрээ

- **Хугацаа:** 1942-2005 (63 жил)
- **Сарны календар:** Монголын сарны календарийн өдөр тутмын мэдээлэл
- **Дэлхийн үйл явдал:** Дайн, терроризм, эдийн засгийн хямрал, байгалийн гамшиг г.м

## 🚀 Хурдан эхлэл

### 1. Суулгалт

```bash
# Clone repository
git clone https://github.com/yourusername/horoscope_x_events.git
cd horoscope_x_events

# Виртуал орчин үүсгэх (Python 3.12+)
python3.12 -m venv venv
source venv/bin/activate  # Mac/Linux
# эсвэл
venv\Scripts\activate  # Windows

# Dependencies суулгах
pip install -r requirements.txt
```

### 2. Өгөгдөл бэлдэх

```bash
# Сарны календарийн файлыг data/raw/ folder-т хуулах
cp /path/to/horoscope_list_20250112.json data/raw/
```

### 3. Бүх шинжилгээг ажиллуулах

```bash
# Бүгдийг нэг дороо
python src/main_analysis.py

# Эсвэл алхам алхмаар:
python src/1_lunar_converter.py
python src/2_event_scraper.py
python src/3_data_matcher.py
python src/4_statistical_analysis.py
python src/5_visualization.py
```

### 4. Үр дүн үзэх

```bash
# Visualizations
open results/visualizations/comprehensive_analysis.png

# HTML тайлан
open results/reports/final_report.html
```

## 📁 Төслийн бүтэц

```
horoscope_x_events/
│
├── data/
│   ├── raw/                          # Анхны өгөгдөл
│   │   ├── horoscope_list_20250112.json
│   │   └── world_events_raw.json
│   ├── processed/                    # Боловсруулсан өгөгдөл
│   │   ├── lunar_bad_days_gregorian.csv
│   │   ├── world_disasters.csv
│   │   └── matched_events.csv
│   └── checkpoints/                  # Checkpoint файлууд
│       └── scraping_progress.json
│
├── src/                              # Үндсэн код
│   ├── 1_lunar_converter.py          # Сарны → Григорийн хөрвүүлэлт
│   ├── 2_event_scraper.py            # Үйл явдал цуглуулах
│   ├── 3_data_matcher.py             # Өгөгдөл таарах
│   ├── 4_statistical_analysis.py     # Статистик шинжилгээ
│   ├── 5_visualization.py            # Визуализаци
│   ├── main_analysis.py              # Бүгдийг нэгтгэсэн script
│   └── utils/                        # Туслах функцууд
│       ├── checkpoint_manager.py
│       ├── progress_tracker.py
│       └── date_converter.py
│
├── notebooks/
│   └── analysis_colab.ipynb          # Google Colab notebook
│
├── results/
│   ├── visualizations/               # Зургууд
│   └── reports/                      # Тайлангууд
│
├── requirements.txt                  # Dependencies
├── README.md                         # Энэ файл
└── PROJECT_PLAN.md                   # Дэлгэрэнгүй төлөвлөгөө
```

## 🔬 Methodology

### 1. Date Conversion
Монголын сарны календарийн огноог Григорийн огноо руу хөрвүүлэхдээ `lunarcalendar` болон `convertdate` library ашигладаг.

### 2. Event Collection
Дэлхийн үйл явдлыг дараах эх сурвалжаас цуглуулдаг:
- Wikipedia (List of wars, terrorist attacks, disasters)
- GDELT Project API
- EM-DAT (Emergency Events Database)

### 3. Severity Scoring
Үйл явдал бүрийг дараах criteria-аар үнэлдэг:
- Нас барсан хүний тоо (40 оноо)
- Эдийн засгийн хохирол (30 оноо)
- Геополитик нөлөө (30 оноо)
- **Max:** 100 оноо

### 4. Statistical Tests
- **Chi-Square Test**: Independence тест
- **T-Test**: Severity score харьцуулалт
- **Pearson Correlation**: Хамаарлын коэффициент

## 📊 Үр дүн (Үлгэр загвар)

```
┌─────────────────────────────────────────────────┐
│ CORRELATION ANALYSIS RESULTS                    │
├─────────────────────────────────────────────────┤
│ Total Bad Days Analyzed:        X,XXX           │
│ Total Disaster Events:          XXX             │
│ Date Range:                     1942-2005       │
│                                                 │
│ Bad Days Disaster Rate:         XX.X%           │
│ Normal Days Disaster Rate:      XX.X%           │
│                                                 │
│ Pearson Correlation:            r = 0.XXX       │
│ P-value:                        p = 0.XXX       │
│ Result:                         [SIG/NOT SIG]   │
└─────────────────────────────────────────────────┘
```

## 🎨 Visualizations

Төсөл дараах visualization-уудыг үүсгэдэг:

1. **Timeline Chart** - Цаг хугацааны дагуу гамшгийн үйл явдал
2. **Heatmap** - Он ба сарны өдрөөр гамшгийн тархалт
3. **Box Plot** - Муу өдөр vs энгийн өдрийн severity харьцуулалт
4. **Correlation Matrix** - Хувьсагчдын хоорондын хамаарал
5. **Event Distribution** - Үйл явдлын төрөл бүрийн тоо хэмжээ
6. **Interactive Dashboard** - Plotly дашборд

## 🛠️ Technologies

- **Python 3.12**
- **Data Processing:** pandas, numpy
- **Date Conversion:** lunarcalendar, convertdate, ephem
- **Web Scraping:** requests, beautifulsoup4, selenium
- **Statistics:** scipy, scikit-learn, statsmodels
- **Visualization:** matplotlib, seaborn, plotly
- **Utilities:** tqdm, joblib

## ⚠️ Анхаарах зүйлс

1. **Date Conversion Accuracy:** Монгол vs Хятадын сарны календар багавтар ялгаатай байж болзошгүй
2. **Data Availability:** 1942 өмнөх үйл явдлын мэдээлэл хомс
3. **Severity Scoring:** Субъектив үнэлгээ орсон
4. **Sample Size:** 63 жилийн өгөгдөл статистик хувьд хязгаарлалттай

## 📝 License

MIT License

## 👥 Contributing

Contributions welcome! Please read CONTRIBUTING.md first.

## 📧 Contact

- Issues: [GitHub Issues](https://github.com/yourusername/horoscope_x_events/issues)
- Email: your.email@example.com

## 🙏 Acknowledgments

- Mongolian lunar calendar data providers
- GDELT Project
- Wikipedia contributors

---

**Disclaimer:** Энэ төсөл бол эрдэм шинжилгээний судалгаа бөгөөд сарны календарь гамшгийг урьдчилан таамаглах чадвартай гэсэн мэдэгдэл биш юм. Үр дүнг шинжлэх ухааны арга зүйгээр, критик сэтгэлгээгээр хүлээн авна уу.
