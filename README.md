# 📊 India Tech Skills Intelligence Dashboard

> **What do 23,000+ tech job listings reveal about India's 2026 hiring landscape?**  
> This project analyses skill demand, role trends, and city-level insights from Naukri.com job data.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://job-analysis-qsuxrhzgdjcil7jmh6sxtr.streamlit.app/)

---

## 🚀 Live Demo

🔗 **[https://job-analysis-qsuxrhzgdjcil7jmh6sxtr.streamlit.app/](https://job-analysis-qsuxrhzgdjcil7jmh6sxtr.streamlit.app/)**

---

## 🖼️ Dashboard Preview

![India Tech Skills Intelligence Dashboard]

> Sidebar filters (Role · City · Work Mode · Experience) apply across all 6 tabs simultaneously.

---

## 📌 Business Problem

In India's tech job market, job seekers struggle to answer:

- *Which skills should I learn to get hired faster?*
- *Which city has the most opportunities for my role?*
- *What skills appear together — what's my learning path?*
- *Am I eligible for fresher-friendly roles?*

This dashboard answers all of that using real job listing data from Naukri.com.

---

## 📂 Dataset

| Property | Detail |
|---|---|
| Source | Naukri.com (scraped) |
| Period | June 2025 |
| Total listings | 22,728 |
| Unique skills | 10,342 |
| Cities covered | 11 |
| Fresher-friendly listings | 4,072 |
| Remote opportunities | 2,147 |

**Key columns used:** `role_category`, `primary_city`, `experience_tier`, `skills_required`, `work_mode`, `skill_domain`, `company_size_bucket`, `is_fresher_friendly`

---

## 🔍 Analysis Phases (Jupyter Notebook)

### Phase 1 — Role-Based Skill Roadmap
- Top skills per role broken down by experience tier (Fresher → Lead)
- Identifies entry-level vs senior-level skills within each role
- Covers: Data Scientist, Data Analyst, ML Engineer, Data Engineer, Business Analyst, Python Developer

### Phase 2 — Skill Co-occurrence Network
- Builds skill pair counts across all 23K listings using `itertools.combinations`
- NetworkX graph: nodes = skills, edge weight = how often they appear together
- Answers: *"If I know Python, what should I learn next?"*

### Phase 3 — City × Skill Heatmap
- Cross-tabulates top 20 skills against top 10 cities
- Both raw count and % normalised views
- Reveals city-specific skill priorities (e.g. Chennai → Business Analysis, Bangalore → ML)

---

## 📊 Dashboard Features (6 Tabs)

| Tab | What It Shows |
|---|---|
| 🌐 Overview | Top N skills bar chart · skill domain donut · work mode split |
| 🎯 By Role | Top skills per role · radar chart for cross-role skill overlap |
| 🏙️ City Intelligence | City × role heatmap · job volume · fresher-friendly % per city |
| 🔗 Co-occurrence | Skill pair heatmap · top 10 skill pairs table |
| 📈 Experience | Experience funnel · work mode stacked bars · company size split |
| 🔍 Skill Finder | Pick any skill → demand by role, city, and experience tier |

---

## 🗂️ Project Structure

```
├── app.py                        # Streamlit entrypoint
├── streamkit.py                  # Dashboard logic and UI (6 tabs)
├── p1.ipynb                      # Jupyter notebook — EDA & analysis
├── indian_tech_jobs_2026.csv     # Dataset
├── requirements.txt              # Python dependencies
├── dashboard_preview.png         # App screenshot for README
└── README.md                     # This file
```

---

## ⚙️ Run Locally

**1. Clone the repo**
```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Add the dataset**

Place `indian_tech_jobs_2026.csv` in the root folder (same level as `app.py`).

**4. Launch the dashboard**
```bash
streamlit run app.py
```

Opens at `http://localhost:8501`

---

## 🧰 Tech Stack

| Tool | Purpose |
|---|---|
| Python 3.10+ | Core language |
| Pandas | Data loading, cleaning, pivot tables |
| Plotly | Interactive charts (bar, pie, heatmap, radar) |
| Streamlit | Dashboard framework & deployment |
| NetworkX | Skill co-occurrence network graph (notebook) |
| Seaborn / Matplotlib | EDA plots in notebook |
| itertools | Skill pair combination logic |

---

## 💡 Key Insights

- **Python** is the #1 demanded skill — appears in nearly 1 in 5 listings
- **Business Intelligence** is the largest skill domain at **47.9%** of all listings
- **AI/ML/DL** is the second largest domain at **28.4%**
- **80.6%** of jobs are on-site — remote is still rare in Indian tech (9.3%)
- **Mid-level (3–5 years)** roles dominate hiring at 43% of all listings
- **4,072 listings** are explicitly fresher-friendly — filter by city to find the best markets

---

