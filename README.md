# Pakistan Population & Demographic Analytics Dashboard
### *Interactive Data Analytics of Rural, Urban, Gender, Growth and Geographic Population Patterns*

---

## 📌 Project Overview
The **Pakistan Population & Demographic Analytics Dashboard** is an enterprise-grade, production-ready analytics web application engineered in Python, Streamlit, and Plotly. It transforms raw district and sub-divisional census data into actionable insights, interactive geospatial comparisons, demographic KPIs, and statistical diagnostics.

The dashboard uses the authentic official sub-division census dataset (covering 528 tehsils/sub-divisions across all administrative divisions and provinces of Pakistan), strictly adhering to the principle that **the actual dataset is the single source of truth** without synthetic or invented records.

---

## 🏗️ Architecture & Project Structure
```text
papolation/
│
├── app.py                     # Streamlit frontend & application coordinator
├── requirements.txt           # Python dependency specification
├── README.md                  # Comprehensive project documentation
│
├── data/
│   ├── dataset.csv                              # Primary census dataset
│   └── sub-division_population_of_pakistan.csv  # Original source file
│
├── modules/
│   ├── __init__.py            # Package initializer
│   ├── data_loader.py         # Dynamic file discovery, ingestion, & raw schema inspection
│   ├── preprocessing.py       # Non-destructive data cleaning, 30+ derived metrics, & quality audit
│   ├── analytics.py           # KPIs, descriptive stats, correlations, outlier detection, aggregations
│   ├── charts.py              # 24 Plotly interactive charts with unified visual styling
│   └── insights.py            # Dynamic, data-driven narrative insights generation
│
└── assets/
    └── style.css              # Custom responsive styling and theme variables
```

---

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.10+ (Python 3.11 recommended)
- Git (optional)

### 1. Clone or Open Project Directory
```powershell
cd "c:\Users\HP EliteBook\Desktop\papolation"
```

### 2. Install Required Dependencies
```powershell
pip install -r requirements.txt
```
*(Dependencies installed: `streamlit`, `pandas`, `numpy`, `plotly`, `scipy`, `openpyxl`)*

### 3. Launch the Application
```powershell
streamlit run 
```
Or directly with Python:
```powershell
python -m streamlit run app.py
```

The application will launch automatically in your default browser at `http://localhost:8501`.

---

## 📊 Summary of Implemented Analytics

1. **Hierarchical Population Analytics**: Complete spatial aggregation from Province down to Division, District, and Sub-Division (Tehsil).
2. **Rural-Urban Settlement Dynamics**: Split analysis, urbanization rate computation, rural dominance vs. urban dominance classification.
3. **Gender Balance & Demographics**: Male-female headcount, transgender representation, regional sex ratios, and net gender gap calculations.
4. **Historical Census Growth Analysis**: Inter-censal change between the 1998 census and current census (absolute headcount increase and percentage change).
5. **Spatial Concentration & Density**: Population density (persons per square kilometer) safely evaluated across land areas.
6. **Household Demographics**: Weighted average household sizes (persons per household) across rural and urban settlements.
7. **Descriptive Statistics**: Mean, median, standard deviation, interquartile range (IQR), 25th/75th percentiles, and skewness for key numeric variables.
8. **Correlation Modeling**: Pearson correlation matrix and interactive heatmap assessing relationships between population, land area, urbanization, and density.
9. **Outlier Detection**: Automated statistical outlier identification using both the Interquartile Range (IQR $\pm 1.5\times\text{IQR}$) and Z-Score methods.
10. **Dynamic Ranking Engine**: Flexible Top-N (Top 5, 10, 15, 20, 50, All) ranking across population, density, growth, and household indicators.

---

## 📈 Implemented Plotly Interactive Visualizations (24 Charts)

1. **Population by Province** *(Horizontal bar chart with blues gradient)*
2. **Population by Division** *(Ranked horizontal bar chart with top-N filtering)*
3. **Population by District** *(Horizontal bar chart with top-N selector)*
4. **Population by Sub Division** *(Tehsil-level ranking bar chart with top-N selector)*
5. **Rural vs. Urban Population Comparison** *(Grouped bar chart across administrative units)*
6. **Rural vs. Urban Population Share** *(Interactive donut/pie chart)*
7. **Male vs. Female Population Comparison** *(Dual grouped bar chart)*
8. **Gender Composition by Region** *(100% stacked bar chart showing male/female proportion)*
9. **Transgender Population Comparison** *(Ranked bar chart highlighting recorded counts)*
10. **Population Density by Region** *(Bar chart of persons per sq.km)*
11. **Annual Growth Rate by Region** *(Comparative regional growth chart)*
12. **Rural vs. Urban Annual Growth Rates** *(Side-by-side grouped bar chart)*
13. **1998 Population vs. Current Population** *(Historical comparison grouped bar chart)*
14. **Absolute Population Growth** *(Net headcount change since 1998)*
15. **Population vs. Geographic Area** *(Bubble scatter plot with regional color coding)*
16. **Population Density vs. Growth Rate** *(Scatter correlation plot)*
17. **Average Household Size by Region** *(Horizontal comparative bar chart)*
18. **Sex Ratio Comparison (Rural vs. Urban)** *(Grouped bar chart with gender parity benchmark)*
19. **Top 10 Most Populated Regions** *(Dynamic top-N ranking chart)*
20. **Bottom 10 Least Populated Regions** *(Dynamic lowest-N ranking chart)*
21. **Top 10 Highest Growth Regions** *(Dynamic rapid growth ranking chart)*
22. **Top 10 Slowest Growth Regions** *(Dynamic low/negative growth ranking chart)*
23. **Top 10 Highest Density Regions** *(High-density urban core ranking chart)*
24. **Settlement Dominance Breakdown** *(Rural Dominant vs. Urban Dominant categorical chart)*

*Additional analytical visualizations:*
- **Demographic Pearson Correlation Heatmap**
- **Household Size & Indicator Distribution Histograms with Marginal Boxplots**

---

## 🧮 Mathematical Formulations & Derived Metrics

| Metric | Mathematical Formula | Handling of Edge Cases |
| :--- | :--- | :--- |
| **Combined Population** | $\text{Pop}_{\text{rural}} + \text{Pop}_{\text{urban}}$ | Default to $0$ if missing |
| **Total Male Population** | $\text{Male}_{\text{rural}} + \text{Male}_{\text{urban}}$ | Default to $0$ if missing |
| **Total Female Population** | $\text{Female}_{\text{rural}} + \text{Female}_{\text{urban}}$ | Default to $0$ if missing |
| **Total Transgender** | $\text{Trans}_{\text{rural}} + \text{Trans}_{\text{urban}}$ | Default to $0$ if missing |
| **Urbanization Rate (%)** | $\frac{\text{Pop}_{\text{urban}}}{\text{Pop}_{\text{combined}}} \times 100$ | $0.0\%$ if $\text{Pop}_{\text{combined}} = 0$ |
| **Rural Share (%)** | $\frac{\text{Pop}_{\text{rural}}}{\text{Pop}_{\text{combined}}} \times 100$ | $0.0\%$ if $\text{Pop}_{\text{combined}} = 0$ |
| **Population Density** | $\frac{\text{Pop}_{\text{combined}}}{\text{Area (sq.km)}}$ | Returns `NaN` if $\text{Area} \le 0$ to prevent $\frac{x}{0}$ errors |
| **1998 Combined Pop** | $\text{Pop98}_{\text{rural}} + \text{Pop98}_{\text{urban}}$ | Default to $0$ if missing |
| **Population Change** | $\text{Pop}_{\text{combined}} - \text{Pop98}_{\text{combined}}$ | Signed numeric integer |
| **Growth % (1998-Current)**| $\frac{\text{Pop}_{\text{change}}}{\text{Pop98}_{\text{combined}}} \times 100$ | $0.0\%$ if $\text{Pop98} = 0$ |
| **Overall Sex Ratio** | $\frac{\text{Male}_{\text{total}}}{\text{Female}_{\text{total}}} \times 100$ | Returns $0$ if $\text{Female}_{\text{total}} = 0$ |
| **Weighted Household Size**| $\frac{(\text{Pop}_{\text{r}} \times \text{HH}_{\text{r}}) + (\text{Pop}_{\text{u}} \times \text{HH}_{\text{u}})}{\text{Pop}_{\text{combined}}}$ | Evaluated only where valid census values exist |
| **Net Gender Gap** | $\text{Male}_{\text{total}} - \text{Female}_{\text{total}}$ | Signed headcount integer |

---

## 🔍 Data Quality Audit & Dataset Observations

During the automated ingestion and audit of `data/sub-division_population_of_pakistan.csv` (528 administrative rows, 21 initial columns), the following verifiable findings were identified:

1. **Zero-Area Tehsils ($4$ Records)**:
   - In **Killa Saifullah District** (Balochistan), four sub-divisions (`BADINI SUB-TEHSIL`, `KAN MEHTARZAI SUB-TEHSIL`, `LOIBAND TEHSIL`, `MUSLIM BAGH TEHSIL`) have an area listed as `0` sq.km.
   - *System Handling*: The preprocessing engine assigns `NaN` for density to prevent division by zero, flagging them in the Data Quality tab.
2. **Census Growth Rate Coding Placeholder ($5$ Records)**:
   - In **Lahore District** (Punjab), five tehsils (`LAHORE CANTT`, `LAHORE CITY`, `MODEL TOWN`, `RAIWIND`, `SHALIMAR`) show an `ANNUAL GROWTH RATE (RURAL)` of exactly `100.0`. In these areas, the rural population shifted to $0$ due to complete municipal reclassification. The census bureau used `100.0` as an administrative code.
   - *System Handling*: The analytics engine identifies this artifact, displays an explanatory callout, and excludes extreme placeholders when calculating average regional growth rates to avoid skewing summary statistics.
3. **100% Urban Sub-Divisions ($34$ Records)**:
   - Highly urbanized cores (Karachi tehsils, Lahore urban divisions, Quetta City, Sukkur City) have $0$ rural population. Rural sex ratios and household sizes are naturally $0$.
4. **100% Rural Sub-Divisions ($155$ Records)**:
   - Sub-divisions across rural Balochistan, interior Sindh, and Khyber Pakhtunkhwa / FATA have $0$ urban population. Urban metrics are naturally $0$.

---

## 🚀 Key Features

- **Cascading Hierarchy Filters**: Selecting a Province dynamically filters available Divisions; selecting a Division narrows Districts; selecting a District narrows Sub-Divisions.
- **Stateful Reset**: Single-click "Reset All Filters" button clears all selections and returns the user to the national perspective.
- **Adaptive Aggregations**: Summary tables and bar charts automatically adapt their grouping dimension (`Province` $\rightarrow$ `Division` $\rightarrow$ `District` $\rightarrow$ `Sub Division`) depending on the depth of user filter selection.
- **Dynamic Narrative Insights**: The "Data Insights" tab automatically generates narrative findings from the active slice of data (identifying population champions, highest density hotspots, sex ratio imbalances, and rapid growth zones).
- **Export Center**: Download filtered datasets, full 51-column cleaned datasets, statistical summaries, and KPI summaries in standard CSV format without external API dependencies.

---

## 🔮 Future Enhancements
- Integration of GeoJSON boundary polygons for choropleth mapping across Pakistani districts.
- Predictive demographic forecasting using time-series population projection models.
- Literacy and employment rate integrations as supplementary census tables become digitally available.
