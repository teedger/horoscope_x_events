# Монголын Сарны Календарийн "Муу Өдөр" ба Дэлхийн Гамшигт Үйл Явдлын Корреляц

## Төслийн Зорилго
Монголын сарны календарийн "муу өдрүүд" (modon_days, ters_days) болон дэлхийн бодит гамшигт үйл явдлуудын хооронд статистик хамаарал байгаа эсэхийг олж тогтоох, үр дүнг харуулах дүрслэл бүтээх.

## Хугацаа
1942-2005 он (одоо байгаа lunar calendar өгөгдлийн хязгаарлалт)

---

## 1. ӨГӨГДЛИЙН ЦУГЛУУЛГА (Data Collection)

### 1.1 Сарны Календарийн Өгөгдөл
**Файл:** `horoscope_list_20250112.json`
**Огтлолцоо:** 1942-2005

**Өгөгдлийн бүтэц:**
```json
{
  "year": "2025",
  "month": "1",
  "haircut_days": [...],    // Үс засах өдөр
  "baljin_days": [...],     // Сайн өдөр (баялаг)
  "dash_days": [...],       // Сайн өдөр (даш)
  "modon_days": [...],      // МУУ ӨДӨР (модон)
  "ters_days": [...]        // МУУ ӨДӨР (төрс)
}
```

**Даалгавар:**
- Сарны он сар + өдөр → Григорийн он сар өдөр хөрвүүлэлт хийх
- 1942-2005 оны бүх муу өдрүүдийн жагсаалт гаргах

### 1.2 Дэлхийн Үйл Явдлын Өгөгдөл

**Эх сурвалж стратеги:**
1. **Wikipedia** - Major historical events
   - List of wars (1900-2025)
   - Major terrorist attacks
   - Economic crises
   - Natural disasters
   - Political assassinations

2. **GDELT Project API** - Global Database of Events, Language, and Tone
   - Comprehensive event database
   - Machine-readable format

3. **Academic Datasets:**
   - UCDP/PRIO Armed Conflict Dataset
   - EM-DAT (Emergency Events Database)

**Цуглуулах үйл явдлын төрлүүд:**

| Төрөл | Жишээ | Хүндрэлийн Оноо |
|-------|-------|----------------|
| **Дайн** | World War I/II, Vietnam War | 10 |
| **Террорист халдлага** | 9/11, Pearl Harbor | 9 |
| **Алуурчилгаа** | JFK, MLK assassinations | 8 |
| **Эдийн засгийн хямрал** | Great Depression, 2008 Crisis | 7-9 |
| **Байгалийн гамшиг** | Earthquakes, tsunamis, hurricanes | 5-10 |
| **Геноцид** | Holocaust, Rwanda | 10 |
| **Техникийн гамшиг** | Chernobyl, plane crashes | 6-9 |

---

## 2. ТЕХНИКИЙН БҮТЭЦ (Technical Architecture)

### 2.1 Төслийн Бүтэц
```
horoscope_x_events/
│
├── data/
│   ├── raw/
│   │   ├── horoscope_list_20250112.json
│   │   └── world_events_raw.json
│   ├── processed/
│   │   ├── lunar_bad_days_gregorian.csv
│   │   ├── world_disasters.csv
│   │   └── matched_events.csv
│   └── checkpoints/
│       └── scraping_progress.json
│
├── src/
│   ├── 1_lunar_converter.py
│   ├── 2_event_scraper.py
│   ├── 3_data_matcher.py
│   ├── 4_statistical_analysis.py
│   ├── 5_visualization.py
│   └── utils/
│       ├── checkpoint_manager.py
│       ├── progress_tracker.py
│       └── date_converter.py
│
├── notebooks/
│   └── analysis_colab.ipynb
│
├── results/
│   ├── visualizations/
│   └── reports/
│
├── requirements.txt
└── README.md
```

### 2.2 Технологийн Stack
```python
# Core
python = "3.12"

# Data Collection
requests = "*"
beautifulsoup4 = "*"
selenium = "*"        # Dynamic content
lxml = "*"

# Date Conversion
ephem = "*"           # Astronomical calculations
convertdate = "*"     # Calendar conversions
lunarcalendar = "*"   # Chinese/Mongolian lunar calendar

# Data Processing
pandas = "*"
numpy = "*"

# Machine Learning
scikit-learn = "*"
scipy = "*"           # Statistical tests

# Visualization
matplotlib = "*"
seaborn = "*"
plotly = "*"          # Interactive charts

# Utilities
tqdm = "*"            # Progress bars
joblib = "*"          # Checkpointing
python-dotenv = "*"
```

---

## 3. АЛГОРИТМ & САНАА (Algorithm Design)

### 3.1 Сарны → Григорийн Хөрвүүлэлт

**Асуудал:** Монголын сарны календарь нь Хятадын сарны календартай адил боловч timezone өөр.

**Шийдэл:**
```python
def lunar_to_gregorian(lunar_year, lunar_month, lunar_day):
    """
    Монголын сарны огноог Григорийн огноо руу хөрвүүлэх

    Parameters:
    - lunar_year: int (жишээ: 2000)
    - lunar_month: int (1-12)
    - lunar_day: int (1-30)

    Returns:
    - datetime object (Gregorian date)
    """
    # 1. Хятадын сарны календарь ашиглах
    # 2. Timezone offset (+8 UTC Улаанбаатар)
    # 3. Нэг өдрийн хязгаарыг тооцох
    pass
```

### 3.2 Үйл Явдлын Скрэйпинг (с Checkpoint)

```python
class EventScraper:
    def __init__(self, checkpoint_file='data/checkpoints/scraping.json'):
        self.checkpoint = self.load_checkpoint(checkpoint_file)
        self.events = []

    def scrape_with_resume(self, start_year=1942, end_year=2005):
        """Зогссон газраасаа үргэлжлүүлэх"""
        last_year = self.checkpoint.get('last_completed_year', start_year - 1)

        for year in tqdm(range(last_year + 1, end_year + 1)):
            try:
                events = self.scrape_year(year)
                self.events.extend(events)

                # Checkpoint хадгалах
                self.save_checkpoint(year)

                # Жил бүрийн дараа файл dump хийх
                self.dump_intermediate_results(year)

            except Exception as e:
                logger.error(f"Error at year {year}: {e}")
                # Зогс, checkpoint-оос үргэлжлүүлж болно
                break

        return self.events
```

### 3.3 Үйл Явдлын Ангилал (Event Severity Scoring)

**Хандлага:** Multi-factor scoring system

```python
def calculate_severity_score(event):
    """
    Үйл явдлын хүндрэлийн оноо тооцох

    Factors:
    - Нас барсан хүний тоо (death toll)
    - Эдийн засгийн хохирол (economic damage)
    - Нөлөөлсөн хүн ам (affected population)
    - Үргэлжилсэн хугацаа (duration)
    - Геополитик нөлөө (geopolitical impact)
    """
    score = 0

    # Death toll (0-40 points)
    if event.deaths > 1000000:
        score += 40
    elif event.deaths > 100000:
        score += 30
    elif event.deaths > 10000:
        score += 20
    # ... etc

    # Economic impact (0-30 points)
    # ...

    # Geopolitical impact (0-30 points)
    # ...

    return min(score, 100)  # Max 100
```

### 3.4 Огноо Таарах Алгоритм

**Асуудал:** Үйл явдал нь олон хоног үргэлжилдэг (дайн жишээ нь)

**Шийдэл:**
```python
def match_events_to_lunar_days(events_df, lunar_days_df):
    """
    Үйл явдлыг сарны муу өдөртэй тааруулах

    Strategy:
    1. Богино үйл явдал (1 өдөр) → шууд таарах
    2. Урт үйл явдал (>1 өдөр) → эхлэх өдрөөр нь
    3. Альтернатив: Хамгийн их хохирол болсон өдрөөр нь
    """
    matches = []

    for _, event in events_df.iterrows():
        event_date = event['date']

        # Муу өдөр мөн эсэхийг шалгах
        is_bad_day = check_if_bad_day(event_date, lunar_days_df)

        matches.append({
            'event': event['name'],
            'date': event_date,
            'is_bad_day': is_bad_day,
            'day_type': get_day_type(event_date, lunar_days_df),
            'severity': event['severity_score']
        })

    return pd.DataFrame(matches)
```

---

## 4. СТАТИСТИК ШИНЖИЛГЭЭ (Statistical Analysis)

### 4.1 Хэмжих Үзүүлэлтүүд

**Үндсэн асуулт:** Муу өдрүүдэд гамшигт үйл явдал их гардаг уу?

**Тест 1: Chi-Square Test**
```
H0: Муу өдөр ба гамшгийн үйл явдал хамааралгүй
H1: Хамааралтай

Contingency Table:
                  Bad Day    Not Bad Day
Disaster Event       A           B
No Disaster          C           D
```

**Тест 2: T-Test**
```
Compare:
- Average severity score on bad days
- Average severity score on normal days
```

**Тест 3: Correlation Analysis**
```python
# Сар бүрийн:
- Муу өдрийн тоо
- Гамшгийн үйл явдлын тоо
- Нийт severity score

Pearson correlation coefficient
```

### 4.2 Machine Learning Approach

**Binary Classification:**
```
Features:
- is_bad_day (0/1)
- is_good_day (0/1)
- lunar_month (1-12)
- lunar_day (1-30)

Target:
- disaster_occurred (0/1)

Model: Logistic Regression, Random Forest
Metric: AUC-ROC, Precision, Recall
```

---

## 5. ВИЗУАЛИЗАЦИ (Visualization)

### 5.1 График Төрлүүд

**1. Timeline Visualization**
```
X-axis: Он (1942-2005)
Y-axis: Үйл явдлын severity score
Color:
- Улаан = Муу өдөр
- Ногоон = Сайн өдөр
- Саарал = Энгийн өдөр
```

**2. Heatmap**
```
X-axis: Сарны өдөр (1-30)
Y-axis: Он (1942-2005)
Color intensity: Үйл явдлын тоо эсвэл severity
Overlay: Муу өдрүүдийг тэмдэглэх
```

**3. Statistical Comparison**
```
Box plot:
- Bad days vs Normal days
- Y-axis: Severity scores
- Show mean, median, outliers
```

**4. Correlation Matrix**
```
Variables:
- Bad day count per month
- Disaster count per month
- Total severity per month
- Economic indicators (optional)
```

**5. Interactive Dashboard**
```
Plotly Dash:
- Filter by year range
- Filter by event type
- Toggle bad day overlay
- Drill down to specific events
```

### 5.2 Код Загвар

```python
def create_comprehensive_visualization(matched_data):
    """
    Бүх визуализацийг нэг дор үүсгэх
    """
    fig, axes = plt.subplots(2, 3, figsize=(20, 12))

    # 1. Timeline
    plot_timeline(matched_data, axes[0, 0])

    # 2. Heatmap
    plot_heatmap(matched_data, axes[0, 1])

    # 3. Box plot comparison
    plot_severity_comparison(matched_data, axes[0, 2])

    # 4. Correlation matrix
    plot_correlation_matrix(matched_data, axes[1, 0])

    # 5. Event type distribution
    plot_event_distribution(matched_data, axes[1, 1])

    # 6. Statistical summary
    plot_statistical_summary(matched_data, axes[1, 2])

    plt.tight_layout()
    plt.savefig('results/comprehensive_analysis.png', dpi=300)
    plt.show()
```

---

## 6. ERROR HANDLING & CHECKPOINTING

### 6.1 Checkpoint Manager

```python
class CheckpointManager:
    """
    Үйл явцыг хадгалж, зогссон газраас үргэлжлүүлэх
    """

    def __init__(self, checkpoint_dir='data/checkpoints'):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(exist_ok=True)

    def save(self, name, data, metadata=None):
        """Checkpoint хадгалах"""
        checkpoint_file = self.checkpoint_dir / f"{name}.pkl"
        metadata_file = self.checkpoint_dir / f"{name}_meta.json"

        # Data хадгалах
        joblib.dump(data, checkpoint_file)

        # Metadata хадгалах
        if metadata is None:
            metadata = {}
        metadata['timestamp'] = datetime.now().isoformat()
        metadata['size'] = len(data) if hasattr(data, '__len__') else 'N/A'

        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)

    def load(self, name):
        """Checkpoint унших"""
        checkpoint_file = self.checkpoint_dir / f"{name}.pkl"

        if not checkpoint_file.exists():
            return None

        return joblib.load(checkpoint_file)

    def exists(self, name):
        """Checkpoint байгаа эсэхийг шалгах"""
        checkpoint_file = self.checkpoint_dir / f"{name}.pkl"
        return checkpoint_file.exists()
```

### 6.2 Progress Tracker with tqdm

```python
def scrape_with_progress(years, scraper):
    """
    Татах явцыг харуулах
    """
    events = []

    with tqdm(total=len(years), desc="Scraping events") as pbar:
        for year in years:
            try:
                year_events = scraper.scrape_year(year)
                events.extend(year_events)

                # Progress update
                pbar.set_postfix({
                    'Year': year,
                    'Events': len(year_events),
                    'Total': len(events)
                })
                pbar.update(1)

            except Exception as e:
                tqdm.write(f"ERROR at {year}: {str(e)}")
                continue

    return events
```

---

## 7. DELIVERABLES (Гаралт)

### 7.1 Код Скриптүүд

**Бүгдийг нэг run script:**
```python
# main_analysis.py
"""
Нэг удаа ажиллуулахад бүх зүйлийг хийнэ:
1. Сарны өдрүүдийг хөрвүүлэх
2. Үйл явдал цуглуулах (эсвэл cache-аас авах)
3. Таарах
4. Шинжлэх
5. Визуализаци үүсгэх
6. Тайлан бичих
"""

def main():
    print("🌙 Mongolian Lunar Calendar vs World Disasters Analysis")
    print("=" * 60)

    # Step 1: Convert lunar calendar
    if not checkpoint_exists('lunar_converted'):
        print("\n[1/5] Converting lunar calendar to Gregorian...")
        lunar_df = convert_lunar_calendar('data/raw/horoscope_list_20250112.json')
        save_checkpoint('lunar_converted', lunar_df)
    else:
        print("\n[1/5] Loading lunar calendar from checkpoint...")
        lunar_df = load_checkpoint('lunar_converted')

    # Step 2: Scrape/load world events
    if not checkpoint_exists('events_scraped'):
        print("\n[2/5] Scraping world disaster events...")
        events_df = scrape_world_events(1942, 2005)
        save_checkpoint('events_scraped', events_df)
    else:
        print("\n[2/5] Loading events from checkpoint...")
        events_df = load_checkpoint('events_scraped')

    # Step 3: Match events to lunar days
    print("\n[3/5] Matching events to lunar calendar...")
    matched_df = match_events_to_lunar_days(events_df, lunar_df)
    save_checkpoint('matched', matched_df)

    # Step 4: Statistical analysis
    print("\n[4/5] Performing statistical analysis...")
    stats_results = perform_statistical_analysis(matched_df)

    # Step 5: Visualizations
    print("\n[5/5] Creating visualizations...")
    create_all_visualizations(matched_df, stats_results)

    # Generate report
    print("\n✅ Analysis complete!")
    print(f"Results saved to: results/")
    print(f"- Visualizations: results/visualizations/")
    print(f"- Report: results/reports/final_report.html")

    return matched_df, stats_results

if __name__ == "__main__":
    main()
```

### 7.2 Google Colab Notebook

```python
# analysis_colab.ipynb

# Cell 1: Setup
!pip install -q lunarcalendar convertdate ephem pandas matplotlib seaborn plotly tqdm

# Cell 2: Upload data
from google.colab import files
uploaded = files.upload()  # Upload horoscope_list_20250112.json

# Cell 3: Run analysis
!wget https://github.com/yourusername/horoscope_x_events/raw/main/src/main_analysis.py
%run main_analysis.py

# Cell 4: Display results
from IPython.display import Image, display
display(Image('results/comprehensive_analysis.png'))
```

### 7.3 Final Report Structure

**HTML Report:**
```
1. Executive Summary
   - Correlation coefficient: r = X.XX
   - P-value: p = X.XX
   - Conclusion: Significant/Not significant

2. Data Overview
   - Total bad days analyzed: X
   - Total disaster events: X
   - Date range: 1942-2005

3. Key Findings
   - Bad days disaster rate: X%
   - Normal days disaster rate: X%
   - Severity comparison

4. Visualizations
   - [All 6 charts embedded]

5. Statistical Tests
   - Chi-square results
   - T-test results
   - Correlation analysis

6. Limitations
   - Data coverage gaps
   - Date conversion accuracy
   - Event categorization subjectivity

7. Conclusions & Future Work
```

---

## 8. ХУГАЦААНЫ ТӨЛӨВЛӨГӨӨ (Timeline)

| Алхам | Хугацаа | Тайлбар |
|-------|---------|---------|
| **Phase 1: Бэлтгэл** | 1 өдөр | Төслийн бүтэц, requirements |
| 1.1 Төслийн бүтэц үүсгэх | 1 цаг | Folder structure |
| 1.2 Dependencies суулгах | 1 цаг | requirements.txt |
| 1.3 Сарны өгөгдөл шалгах | 1 цаг | JSON файл уншиж үзэх |
| **Phase 2: Date Conversion** | 1 өдөр | Lunar → Gregorian |
| 2.1 Conversion library судлах | 2 цаг | lunarcalendar, convertdate |
| 2.2 Converter бичих | 3 цаг | lunar_converter.py |
| 2.3 1942-2005 хөрвүүлэх | 1 цаг | Бүх өдрүүдийг хөрвүүлэх |
| **Phase 3: Event Collection** | 2-3 өдөр | Web scraping |
| 3.1 Эх сурвалж судлах | 3 цаг | Wikipedia, GDELT, etc. |
| 3.2 Scraper бичих | 4 цаг | event_scraper.py |
| 3.3 Өгөгдөл татах | 4-8 цаг | Checkpoint-тэй |
| 3.4 Categorization | 3 цаг | Severity scoring |
| **Phase 4: Analysis** | 1 өдөр | Statistical analysis |
| 4.1 Data matching | 2 цаг | Events ↔ lunar days |
| 4.2 Statistical tests | 3 цаг | Chi-square, t-test, etc. |
| 4.3 ML model (optional) | 2 цаг | Classification |
| **Phase 5: Visualization** | 1 өдөр | Charts & graphs |
| 5.1 Basic charts | 3 цаг | Timeline, heatmap |
| 5.2 Statistical charts | 2 цаг | Box plots, correlation |
| 5.3 Interactive dashboard | 2 цаг | Plotly |
| **Phase 6: Packaging** | 0.5 өдөр | Finalization |
| 6.1 Colab notebook | 1 цаг | Google Colab бэлдэх |
| 6.2 Documentation | 1 цаг | README, comments |
| 6.3 Final report | 1 цаг | HTML тайлан |
| **НИЙТ** | **6-7 өдөр** | |

---

## 9. АНХААРАХ ЗҮЙЛС

### 9.1 Техникийн Сорилтууд

1. **Date Conversion Accuracy**
   - Монгол vs Хятадын сарны календар ялгаа
   - Timezone handling
   - Leap months
   - **Шийдэл:** Manual verification sample, use multiple libraries

2. **Data Availability**
   - 1942 өмнөх үйл явдлын мэдээлэл хомс
   - Severity scoring subjective
   - **Шийдэл:** Multiple data sources, transparent methodology

3. **Statistical Significance**
   - Small sample size (63 years)
   - Rare events (major disasters)
   - **Шийдэл:** Use appropriate statistical tests, acknowledge limitations

### 9.2 Bias Control

1. **Selection Bias:** Зөвхөн томоохон үйл явдлуудыг сонгоогүй байх
2. **Confirmation Bias:** Correlation олохыг хүсэх хандлага
3. **Temporal Bias:** Сүүлийн үеийн үйл явдлын мэдээлэл илүү дэлгэрэнгүй

**Шийдэл:**
- Objective criteria for event inclusion
- Pre-registered hypothesis
- Sensitivity analysis

---

## 10. ХҮЛЭЭГДЭЖ БУЙ ҮР ДҮН

### 10.1 Хамгийн Магадлалтай Scenarios

**Scenario A: Correlation Found (p < 0.05)**
```
Finding: Bad days have 15-20% higher disaster rate
Interpretation: Possible correlation exists
Next steps:
- Expand date range
- Control for confounding variables
- Publish findings
```

**Scenario B: No Correlation (p > 0.05)**
```
Finding: No statistically significant difference
Interpretation: Lunar calendar bad days don't predict disasters
Next steps:
- Check for specific disaster types
- Regional analysis (Mongolia vs global)
- Alternative hypotheses
```

**Scenario C: Reverse Correlation**
```
Finding: Bad days have fewer disasters
Interpretation: ???
Next steps: Data quality check
```

### 10.2 Visualization Examples

Би энэ төслийг дуусаахдаа дараах зургуудыг гаргах болно:

1. **Comprehensive Dashboard** (1920x1080 PNG)
2. **Timeline Animation** (GIF or video)
3. **Interactive HTML** (Plotly)
4. **Statistical Summary** (Publication-ready)

---

## ДҮГНЭЛТ

Энэ төсөл нь:
✅ **Өгөгдлийн шинжлэл ухаан** - Data collection, processing, analysis
✅ **Статистик** - Hypothesis testing, correlation
✅ **Визуализаци** - Beautiful, informative charts
✅ **Соёл судлал** - Mongolian tradition meets modern science

**Хамгийн чухал:** Үр дүн ямар ч гарсан, бид шинжлэх ухааны аргаар, объектив байдлаар хандсан байх ёстой. Correlation олдсон ч гэсэн, энэ нь causation гэсэн үг биш!

---

**Эхлүүлэх бэлэн үү?** 🚀

Дараагийн алхам: `requirements.txt` болон төслийн бүтцийг үүсгэе!
