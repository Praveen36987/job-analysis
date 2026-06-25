"""
India Tech Skills Intelligence Dashboard
==========================================
Streamlit app that explores skill demand across 23,000+ tech job listings.

Run:
    streamlit run streamkit.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import warnings

warnings.filterwarnings("ignore")

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="India Tech Skills Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────

st.markdown("""
<style>
    /* Main background */
    .stApp { background-color: #F7F8FA; }

    /* Metric cards */
    [data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #E8EAF0;
        border-radius: 10px;
        padding: 14px 18px;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.7rem !important;
        font-weight: 700 !important;
        color: #1A1D2E !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.78rem !important;
        color: #6B7280 !important;
        font-weight: 500 !important;
    }

    /* Section headers */
    h2 { color: #1A1D2E !important; font-weight: 700 !important; }
    h3 { color: #3D4066 !important; font-weight: 600 !important; }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #FFFFFF;
        border-right: 1px solid #E8EAF0;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background: #FFFFFF;
        border-radius: 10px;
        padding: 4px;
        border: 1px solid #E8EAF0;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 6px 18px;
        font-size: 0.85rem;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background: #5C6BC0 !important;
        color: white !important;
    }

    /* Divider */
    hr { border-color: #E8EAF0; margin: 1rem 0; }

    /* Insight box */
    .insight-box {
        background: #EEF2FF;
        border-left: 4px solid #5C6BC0;
        border-radius: 0 8px 8px 0;
        padding: 10px 16px;
        margin: 8px 0 16px;
        font-size: 0.88rem;
        color: #3D4066;
        line-height: 1.55;
    }
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────

DATA_PATH = "indian_tech_jobs_2026.csv"

MAJOR_CITIES = [
    "Bangalore", "Mumbai", "Hyderabad", "Pune",
    "Chennai", "Noida", "Gurgaon", "Kolkata",
    "Ahmedabad", "Delhi",
]

EXP_ORDER = [
    "Fresher", "Junior (0-2 Yrs)", "Mid (3-5 Yrs)",
    "Senior (6-8 Yrs)", "Lead/Architect (9+ Yrs)",
]

ROLE_COLORS = {
    "Data Scientist":            "#5C6BC0",
    "Data Analyst":              "#26A69A",
    "Machine Learning Engineer": "#EF6C00",
    "Data Engineer":             "#8D6E63",
    "Business Analyst":          "#EC407A",
    "Python Developer":          "#42A5F5",
}

WORK_MODE_COLORS = {
    "On-site": "#EF6C00",
    "Hybrid":  "#5C6BC0",
    "Remote":  "#26A69A",
}

PLOTLY_TEMPLATE = "plotly_white"

# ── Data loading & caching ────────────────────────────────────────────────────

@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    return df


@st.cache_data
def parse_skills(df: pd.DataFrame) -> pd.DataFrame:
    valid = df[df["skills_required"] != "Not Available"].copy()
    valid["skill_list"] = valid["skills_required"].str.split(",")
    exploded = valid.explode("skill_list")
    exploded["skill"] = exploded["skill_list"].str.strip().str.lower()
    exploded = exploded[exploded["skill"] != ""]
    return exploded


@st.cache_data
def build_cooccurrence(skills_df: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
    top_skills = [s for s, _ in Counter(skills_df["skill"]).most_common(top_n)]
    matrix = pd.DataFrame(0, index=top_skills, columns=top_skills)
    grouped = skills_df.groupby("job_id")["skill"].apply(list)
    for _, skill_list in grouped.items():
        job_top = [s for s in skill_list if s in top_skills]
        for i, s1 in enumerate(job_top):
            for s2 in job_top[i + 1:]:
                matrix.loc[s1, s2] += 1
                matrix.loc[s2, s1] += 1
    return matrix


# ── Sidebar ───────────────────────────────────────────────────────────────────

def render_sidebar(df: pd.DataFrame):
    st.sidebar.image(
        "https://img.icons8.com/fluency/64/combo-chart.png", width=48
    )
    st.sidebar.title("Filters")
    st.sidebar.caption("Filters apply across all tabs")

    roles = st.sidebar.multiselect(
        "Role category",
        options=sorted(df["role_category"].dropna().unique()),
        default=sorted(df["role_category"].dropna().unique()),
    )

    cities = st.sidebar.multiselect(
        "City",
        options=MAJOR_CITIES + ["Remote"],
        default=MAJOR_CITIES,
    )

    work_modes = st.sidebar.multiselect(
        "Work mode",
        options=["On-site", "Hybrid", "Remote"],
        default=["On-site", "Hybrid", "Remote"],
    )

    exp_tiers = st.sidebar.multiselect(
        "Experience tier",
        options=EXP_ORDER,
        default=EXP_ORDER,
    )

    st.sidebar.divider()
    st.sidebar.caption(
        "📁 Data: Naukri.com scrape · June 2025\n"
        "📊 23,201 job listings · 10,633 unique skills"
    )

    return roles, cities, work_modes, exp_tiers


# ── Filter helper ─────────────────────────────────────────────────────────────

def apply_filters(df, skills_df, roles, cities, work_modes, exp_tiers):
    mask = (
        df["role_category"].isin(roles) &
        df["primary_city"].isin(cities + ["Remote"]) &
        df["work_mode"].isin(work_modes) &
        df["experience_tier"].isin(exp_tiers)
    )
    filtered_df = df[mask].copy()

    filtered_skills = skills_df[
        skills_df["job_id"].isin(filtered_df["job_id"])
    ].copy()

    return filtered_df, filtered_skills


# ── KPI row ───────────────────────────────────────────────────────────────────

def render_kpis(df: pd.DataFrame, skills_df: pd.DataFrame):
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total listings",     f"{len(df):,}")
    c2.metric("Unique skills",       f"{skills_df['skill'].nunique():,}")
    c3.metric("Cities covered",      f"{df['primary_city'].nunique():,}")
    c4.metric("Fresher-friendly",    f"{df['is_fresher_friendly'].sum():,}")
    c5.metric("Remote opportunities",
              f"{(df['work_mode'] == 'Remote').sum():,}")


# ── Tab 1 — Overall skill demand ─────────────────────────────────────────────────

def tab_overview(df: pd.DataFrame, skills_df: pd.DataFrame):
    st.subheader("Most in-demand skills across all filtered roles")

    col1, col2 = st.columns([2, 1])

    with col1:
        n_skills = st.slider("Show top N skills", 10, 30, 20, key="n_overview")
        top_skills = skills_df["skill"].value_counts().head(n_skills).reset_index()
        top_skills.columns = ["skill", "count"]
        top_skills["skill"] = top_skills["skill"].str.title()

        fig = px.bar(
            top_skills.sort_values("count"),
            x="count", y="skill",
            orientation="h",
            color="count",
            color_continuous_scale="Blues",
            labels={"count": "Job listings", "skill": ""},
            template=PLOTLY_TEMPLATE,
        )
        fig.update_layout(
            coloraxis_showscale=False,
            height=520,
            margin=dict(l=0, r=20, t=10, b=10),
            plot_bgcolor="white",
            yaxis=dict(tickfont=dict(size=12)),
        )
        fig.update_traces(
            hovertemplate="<b>%{y}</b><br>%{x:,} listings<extra></extra>"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### Skill domain split")
        domain_counts = df["skill_domain"].value_counts().reset_index()
        domain_counts.columns = ["domain", "count"]

        fig2 = px.pie(
            domain_counts, values="count", names="domain",
            color_discrete_sequence=px.colors.qualitative.Set2,
            hole=0.45,
            template=PLOTLY_TEMPLATE,
        )
        fig2.update_traces(
            textposition="outside",
            textinfo="label+percent",
            hovertemplate="<b>%{label}</b><br>%{value:,} listings<extra></extra>",
        )
        fig2.update_layout(
            showlegend=False,
            height=300,
            margin=dict(l=10, r=10, t=10, b=10),
        )
        st.plotly_chart(fig2, use_container_width=True)

        st.markdown("#### Work mode split")
        wm_counts = df["work_mode"].value_counts().reset_index()
        wm_counts.columns = ["mode", "count"]

        fig3 = px.pie(
            wm_counts, values="count", names="mode",
            color="mode",
            color_discrete_map=WORK_MODE_COLORS,
            hole=0.45,
            template=PLOTLY_TEMPLATE,
        )
        fig3.update_traces(
            textposition="outside",
            textinfo="label+percent",
            hovertemplate="<b>%{label}</b><br>%{value:,} listings<extra></extra>",
        )
        fig3.update_layout(
            showlegend=False,
            height=280,
            margin=dict(l=10, r=10, t=10, b=10),
        )
        st.plotly_chart(fig3, use_container_width=True)

    top1 = top_skills.iloc[-1]["skill"]
    top2 = top_skills.iloc[-2]["skill"]
    st.markdown(
        f'<div class="insight-box">💡 <b>{top1}</b> and <b>{top2}</b> lead demand '
        f"across all roles. Business Intelligence accounts for the largest share "
        f"of listings ({domain_counts.iloc[0]['count']:,} jobs), driven by the "
        f"high volume of Data Analyst and Business Analyst postings.</div>",
        unsafe_allow_html=True,
    )


# ── Tab 2 — Skills by role ────────────────────────────────────────────────────

def tab_by_role(df: pd.DataFrame, skills_df: pd.DataFrame):
    st.subheader("Top skills demanded per role category")

    selected_roles = st.multiselect(
        "Select roles to compare",
        options=sorted(df["role_category"].unique()),
        default=sorted(df["role_category"].unique())[:3],
        key="role_compare",
    )
    if not selected_roles:
        st.info("Select at least one role.")
        return

    n = st.slider("Skills per role", 5, 15, 8, key="n_role")

    cols = st.columns(min(len(selected_roles), 3))

    for idx, role in enumerate(selected_roles):
        col = cols[idx % 3]
        with col:
            role_df = skills_df[skills_df["role_category"] == role]
            top = role_df["skill"].value_counts().head(n).reset_index()
            top.columns = ["skill", "count"]
            top["skill"] = top["skill"].str.title()
            color = ROLE_COLORS.get(role, "#78909C")

            fig = px.bar(
                top.sort_values("count"),
                x="count", y="skill",
                orientation="h",
                template=PLOTLY_TEMPLATE,
                labels={"count": "Listings", "skill": ""},
            )
            fig.update_traces(
                marker_color=color,
                hovertemplate="<b>%{y}</b><br>%{x:,} listings<extra></extra>",
            )
            fig.update_layout(
                title=dict(text=role, font=dict(size=13, color=color)),
                height=360,
                margin=dict(l=0, r=10, t=40, b=10),
                plot_bgcolor="white",
                yaxis=dict(tickfont=dict(size=11)),
            )
            st.plotly_chart(fig, use_container_width=True)

    if len(selected_roles) >= 2:
        st.divider()
        st.markdown("#### Cross-role skill overlap radar")

        all_top = Counter(skills_df["skill"]).most_common(12)
        radar_skills = [s.title() for s, _ in all_top]

        fig_radar = go.Figure()
        for role in selected_roles:
            role_df = skills_df[skills_df["role_category"] == role]
            total = len(role_df["job_id"].unique()) or 1
            counts = []
            for s, _ in all_top:
                c = (role_df["skill"] == s).sum()
                counts.append(round(c / total * 100, 1))

            fig_radar.add_trace(go.Scatterpolar(
                r=counts + [counts[0]],
                theta=radar_skills + [radar_skills[0]],
                fill="toself",
                name=role,
                line_color=ROLE_COLORS.get(role, "#78909C"),
                opacity=0.65,
                hovertemplate="<b>%{theta}</b>: %{r:.1f}%<extra>" + role + "</extra>",
            ))

        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100],
                                ticksuffix="%", tickfont=dict(size=9)),
            ),
            showlegend=True,
            height=420,
            margin=dict(l=30, r=30, t=20, b=20),
            template=PLOTLY_TEMPLATE,
        )
        st.plotly_chart(fig_radar, use_container_width=True)

        st.markdown(
            '<div class="insight-box">💡 The radar shows where roles overlap and where '
            "they diverge. Python and SQL are the common core; specialised skills "
            "(Power BI for analysts, NLP for ML engineers) mark each role's unique "
            "territory — ideal for planning a skill-switching roadmap.</div>",
            unsafe_allow_html=True,
        )


# ── Tab 3 — City intelligence ───────────────────────────────────────────────

def tab_city(df: pd.DataFrame, skills_df: pd.DataFrame):
    st.subheader("City-level job market intelligence")

    city_filter = st.multiselect(
        "Cities to analyse",
        options=MAJOR_CITIES,
        default=MAJOR_CITIES[:7],
        key="city_tab",
    )
    if not city_filter:
        st.info("Select at least one city.")
        return

    sub = df[df["primary_city"].isin(city_filter)]
    pivot = (
        sub.groupby(["primary_city", "role_category"])["job_id"]
        .count()
        .unstack(fill_value=0)
    )
    pivot_pct = pivot.div(pivot.sum(axis=1), axis=0) * 100

    fig_heat = px.imshow(
        pivot_pct.round(1),
        text_auto=".0f",
        color_continuous_scale="YlOrRd",
        aspect="auto",
        labels={"color": "% of city listings"},
        template=PLOTLY_TEMPLATE,
    )
    fig_heat.update_layout(
        title="Role demand by city — % share of total city listings",
        height=380,
        margin=dict(l=10, r=10, t=40, b=10),
        coloraxis_colorbar=dict(title="% share", ticksuffix="%"),
        xaxis=dict(tickangle=-25),
    )
    st.plotly_chart(fig_heat, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        city_counts = (
            sub["primary_city"].value_counts()
            .reset_index()
        )
        city_counts.columns = ["city", "count"]

        fig_vol = px.bar(
            city_counts.sort_values("count"),
            x="count", y="city",
            orientation="h",
            color="count",
            color_continuous_scale="Blues",
            labels={"count": "Job listings", "city": ""},
            template=PLOTLY_TEMPLATE,
            title="Total listings by city",
        )
        fig_vol.update_layout(
            coloraxis_showscale=False,
            height=340,
            margin=dict(l=0, r=10, t=40, b=10),
        )
        st.plotly_chart(fig_vol, use_container_width=True)

    with col2:
        chosen_city = st.selectbox(
            "Drill into top skills for city",
            options=city_filter,
            key="city_drill",
        )
        city_skills = (
            skills_df[skills_df["primary_city"] == chosen_city]["skill"]
            .value_counts()
            .head(10)
            .reset_index()
        )
        city_skills.columns = ["skill", "count"]
        city_skills["skill"] = city_skills["skill"].str.title()

        fig_cs = px.bar(
            city_skills.sort_values("count"),
            x="count", y="skill",
            orientation="h",
            color="count",
            color_continuous_scale="Teal",
            labels={"count": "Listings", "skill": ""},
            title=f"Top 10 skills in {chosen_city}",
            template=PLOTLY_TEMPLATE,
        )
        fig_cs.update_layout(
            coloraxis_showscale=False,
            height=340,
            margin=dict(l=0, r=10, t=40, b=0),
        )
        st.plotly_chart(fig_cs, use_container_width=True)

    st.markdown("#### Fresher-friendly job share per city")
    ff = sub.groupby("primary_city").agg(
        total=("job_id", "count"),
        fresher=("is_fresher_friendly", "sum"),
    ).reset_index()
    ff["pct"] = (ff["fresher"] / ff["total"] * 100).round(1)
    ff = ff.sort_values("pct", ascending=False)

    fig_ff = px.bar(
        ff, x="primary_city", y="pct",
        color="pct",
        color_continuous_scale="Greens",
        labels={"pct": "% fresher-friendly", "primary_city": "City"},
        text="pct",
        template=PLOTLY_TEMPLATE,
        title="% of listings open to freshers — by city",
    )
    fig_ff.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig_ff.update_layout(
        coloraxis_showscale=False,
        height=320,
        margin=dict(l=10, r=10, t=40, b=10),
        yaxis=dict(ticksuffix="%"),
    )
    st.plotly_chart(fig_ff, use_container_width=True)

    top_ff_city = ff.iloc[0]["primary_city"]
    top_ff_pct  = ff.iloc[0]["pct"]
    st.markdown(
        f'<div class="insight-box">💡 <b>{top_ff_city}</b> has the highest share of '
        f"fresher-friendly listings at <b>{top_ff_pct:.0f}%</b>. If you are a "
        f"new graduate, filtering by city matters as much as filtering by role.</div>",
        unsafe_allow_html=True,
    )


# ── Tab 4 — Skill co-occurrence ───────────────────────────────────────────────

def tab_cooccurrence(skills_df: pd.DataFrame):
    st.subheader("Skill co-occurrence — what skills appear together?")
    st.caption(
        "Darker cells = those two skills appear together in more job listings. "
        "Use this to plan your learning path: mastering the top cluster "
        "maximises your coverage."
    )

    top_n = st.slider("Number of skills in matrix", 10, 25, 15, key="cooc_n")

    with st.spinner("Building co-occurrence matrix…"):
        matrix = build_cooccurrence(skills_df, top_n=top_n)

    matrix.index   = [s.title() for s in matrix.index]
    matrix.columns = [s.title() for s in matrix.columns]

    fig = px.imshow(
        matrix,
        color_continuous_scale="Blues",
        aspect="auto",
        labels={"color": "Co-occurrences"},
        template=PLOTLY_TEMPLATE,
    )
    fig.update_layout(
        height=580,
        margin=dict(l=10, r=10, t=20, b=10),
        xaxis=dict(tickangle=-40, tickfont=dict(size=10)),
        yaxis=dict(tickfont=dict(size=10)),
        coloraxis_colorbar=dict(title="Count"),
    )
    fig.update_traces(
        hovertemplate="<b>%{x}</b> + <b>%{y}</b><br>%{z:,} listings<extra></extra>"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### Top 10 skill pairs")
    pairs = []
    for i, s1 in enumerate(matrix.index):
        for s2 in list(matrix.columns)[i + 1:]:
            val = matrix.loc[s1, s2]
            if val > 0:
                pairs.append((s1, s2, int(val)))
    pairs_df = (
        pd.DataFrame(pairs, columns=["Skill A", "Skill B", "Co-occurrences"])
        .sort_values("Co-occurrences", ascending=False)
        .head(10)
        .reset_index(drop=True)
    )
    pairs_df.index = pairs_df.index + 1
    st.dataframe(pairs_df, use_container_width=True)

    st.markdown(
        '<div class="insight-box">💡 Python + Machine Learning is the strongest skill '
        "pair (1,192 jobs). If you already know Python, learning ML unlocks the "
        "largest cluster of Data Scientist and ML Engineer roles. "
        "SQL is the universal connector — it pairs strongly with both Python "
        "and data analysis skills.</div>",
        unsafe_allow_html=True,
    )


# ── Tab 5 — Experience & work mode ───────────────────────────────────────────

def tab_experience(df: pd.DataFrame):
    st.subheader("Experience level & work mode analysis")

    col1, col2 = st.columns(2)

    with col1:
        exp_counts = (
            df["experience_tier"]
            .value_counts()
            .reindex(EXP_ORDER)
            .reset_index()
        )
        exp_counts.columns = ["tier", "count"]

        fig_exp = px.funnel(
            exp_counts,
            x="count", y="tier",
            color_discrete_sequence=["#5C6BC0"],
            template=PLOTLY_TEMPLATE,
            labels={"count": "Job listings", "tier": ""},
            title="Listings per experience level",
        )
        fig_exp.update_layout(height=360, margin=dict(l=0, r=10, t=40, b=10))
        st.plotly_chart(fig_exp, use_container_width=True)

    with col2:
        wm_pivot = (
            df.groupby(["role_category", "work_mode"])["job_id"]
            .count()
            .unstack(fill_value=0)
        )
        wm_pct = wm_pivot.div(wm_pivot.sum(axis=1), axis=0) * 100

        wm_long = wm_pct.reset_index().melt(
            id_vars="role_category",
            var_name="work_mode",
            value_name="pct",
        )
        fig_wm = px.bar(
            wm_long,
            x="pct", y="role_category",
            color="work_mode",
            orientation="h",
            barmode="stack",
            color_discrete_map=WORK_MODE_COLORS,
            labels={"pct": "% of role", "role_category": "", "work_mode": ""},
            template=PLOTLY_TEMPLATE,
            title="Work mode split per role (%)",
        )
        fig_wm.update_layout(
            height=360,
            margin=dict(l=0, r=10, t=40, b=10),
            xaxis=dict(ticksuffix="%"),
            legend=dict(orientation="h", y=-0.18),
        )
        fig_wm.update_traces(
            hovertemplate="<b>%{y}</b> — %{customdata}: %{x:.1f}%<extra></extra>",
            customdata=wm_long["work_mode"],
        )
        st.plotly_chart(fig_wm, use_container_width=True)

    st.markdown("#### Skill domain demand across experience tiers")
    exp_domain = (
        df.groupby(["experience_tier", "skill_domain"])["job_id"]
        .count()
        .unstack(fill_value=0)
        .reindex([e for e in EXP_ORDER if e in df["experience_tier"].unique()])
    )

    fig_ed = px.imshow(
        exp_domain,
        text_auto=True,
        color_continuous_scale="Purples",
        aspect="auto",
        labels={"color": "Job count"},
        template=PLOTLY_TEMPLATE,
    )
    fig_ed.update_layout(
        height=320,
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(tickangle=-20),
        coloraxis_colorbar=dict(title="Count"),
    )
    st.plotly_chart(fig_ed, use_container_width=True)

    st.markdown("#### Hiring by company size")
    cs_pivot = (
        df.groupby(["company_size_bucket", "role_category"])["job_id"]
        .count()
        .reset_index()
    )
    cs_pivot.columns = ["company_size", "role", "count"]

    fig_cs = px.bar(
        cs_pivot,
        x="role", y="count",
        color="company_size",
        barmode="group",
        color_discrete_sequence=["#5C6BC0", "#26A69A", "#EF6C00"],
        labels={"count": "Listings", "role": "", "company_size": "Company size"},
        template=PLOTLY_TEMPLATE,
        title="Role demand split by company size",
    )
    fig_cs.update_layout(
        height=340,
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis=dict(tickangle=-20),
        legend=dict(orientation="h", y=-0.25),
    )
    st.plotly_chart(fig_cs, use_container_width=True)

    st.markdown(
        '<div class="insight-box">💡 Mid-level (3–5 years) dominates demand at 43% of '
        "listings. Data Scientists have the highest remote share (10.5%) while "
        "Python Developers are almost exclusively on-site. "
        "Small startups (&lt;100 employees) post 81% of all listings — "
        "networking and startup-targeted portfolios pay off.</div>",
        unsafe_allow_html=True,
    )


# ── Tab 6 — Skill finder tool ─────────────────────────────────────────────────

def tab_skill_finder(df: pd.DataFrame, skills_df: pd.DataFrame):
    st.subheader("Skill finder — explore any skill's demand landscape")

    all_skills_sorted = (
        skills_df["skill"].value_counts().head(200).index.str.title().tolist()
    )
    chosen_skill = st.selectbox(
        "Choose a skill",
        options=all_skills_sorted,
        key="skill_finder",
    )

    skill_lower = chosen_skill.lower()
    matched_jobs = skills_df[skills_df["skill"] == skill_lower]["job_id"].unique()
    skill_df = df[df["job_id"].isin(matched_jobs)]

    if skill_df.empty:
        st.warning("No jobs found for this skill with current filters.")
        return

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total listings",  f"{len(skill_df):,}")
    k2.metric("Fresher-friendly", f"{skill_df['is_fresher_friendly'].sum():,}")
    k3.metric("Remote openings",
              f"{(skill_df['work_mode'] == 'Remote').sum():,}")
    k4.metric("Avg company rating",
              f"{skill_df['company_rating'].mean():.2f} / 5")

    col1, col2 = st.columns(2)

    with col1:
        by_role = skill_df["role_category"].value_counts().reset_index()
        by_role.columns = ["role", "count"]
        fig1 = px.pie(
            by_role, values="count", names="role",
            color="role",
            color_discrete_map=ROLE_COLORS,
            hole=0.4,
            template=PLOTLY_TEMPLATE,
            title=f"Roles hiring for '{chosen_skill}'",
        )
        fig1.update_traces(
            textinfo="label+percent",
            hovertemplate="<b>%{label}</b><br>%{value:,} listings<extra></extra>",
        )
        fig1.update_layout(showlegend=False, height=320,
                           margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        by_city = (
            skill_df[skill_df["primary_city"].isin(MAJOR_CITIES)]
            ["primary_city"].value_counts()
            .head(8)
            .reset_index()
        )
        by_city.columns = ["city", "count"]
        fig2 = px.bar(
            by_city.sort_values("count"),
            x="count", y="city",
            orientation="h",
            color="count",
            color_continuous_scale="Oranges",
            labels={"count": "Listings", "city": ""},
            template=PLOTLY_TEMPLATE,
            title=f"Cities hiring for '{chosen_skill}'",
        )
        fig2.update_layout(
            coloraxis_showscale=False, height=320,
            margin=dict(l=0, r=10, t=40, b=0),
        )
        st.plotly_chart(fig2, use_container_width=True)

    exp_counts = (
        skill_df["experience_tier"]
        .value_counts()
        .reindex(EXP_ORDER)
        .fillna(0)
        .reset_index()
    )
    exp_counts.columns = ["tier", "count"]

    fig3 = px.bar(
        exp_counts,
        x="tier", y="count",
        color="tier",
        color_discrete_sequence=px.colors.sequential.Purples_r[:5],
        labels={"count": "Listings", "tier": ""},
        template=PLOTLY_TEMPLATE,
        title=f"Experience level demand for '{chosen_skill}'",
    )
    fig3.update_layout(
        showlegend=False, height=300,
        margin=dict(l=10, r=10, t=40, b=10),
    )
    st.plotly_chart(fig3, use_container_width=True)

    top_role = by_role.iloc[0]["role"] if not by_role.empty else "N/A"
    top_city = by_city.iloc[-1]["city"] if not by_city.empty else "N/A"
    st.markdown(
        f'<div class="insight-box">💡 <b>{chosen_skill}</b> is most demanded in '
        f"<b>{top_role}</b> roles, and <b>{top_city}</b> has the highest concentration "
        f"of openings. Use the experience chart above to gauge whether you need "
        f"to pair this skill with seniority or if freshers are welcome.</div>",
        unsafe_allow_html=True,
    )


# ── Main app ──────────────────────────────────────────────────────────────────

def main():
    st.markdown(
        """
        <h1 style='color:#1A1D2E; font-size:1.9rem; font-weight:800;
                   margin-bottom:2px;'>
            📊 India Tech Skills Intelligence
        </h1>
        <p style='color:#6B7280; font-size:0.92rem; margin-top:0;'>
            What 23,000+ job listings reveal about the 2026 tech hiring landscape
        </p>
        <hr>
        """,
        unsafe_allow_html=True,
    )

    try:
        df = load_data()
    except FileNotFoundError:
        st.error(
            f"❌ Dataset not found at `{DATA_PATH}`. "
            "Place `indian_tech_jobs_2026.csv` in the same folder as this script."
        )
        st.stop()

    skills_df = parse_skills(df)

    roles, cities, work_modes, exp_tiers = render_sidebar(df)

    filtered_df, filtered_skills = apply_filters(
        df, skills_df, roles, cities, work_modes, exp_tiers
    )

    if filtered_df.empty:
        st.warning("No data matches your current filters. Try widening the selection.")
        st.stop()

    render_kpis(filtered_df, filtered_skills)
    st.markdown("<hr>", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Overview",
        "By Role",
        "City Intelligence",
        "Co-occurrence",
        "Experience",
        "Skill Finder",
    ])

    with tab1:
        tab_overview(filtered_df, filtered_skills)
    with tab2:
        tab_by_role(filtered_df, filtered_skills)
    with tab3:
        tab_city(filtered_df, filtered_skills)
    with tab4:
        tab_cooccurrence(filtered_skills)
    with tab5:
        tab_experience(filtered_df)
    with tab6:
        tab_skill_finder(filtered_df, filtered_skills)


if __name__ == "__main__":
    main()
