import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page config
st.set_page_config(page_title="Sleep Health Analytics Dashboard", layout="wide", initial_sidebar_state="expanded")

@st.cache_data
def load_and_process_data():
    df = pd.read_excel('dataset.xlsx')
    df['Sleep Disorder'] = df['Sleep Disorder'].fillna('None')

    def assign_tier(row):
        sd = row['Sleep Duration']
        q = row['Quality of Sleep']
        stress = row['Stress Level']
        if sd < 6.0 or (sd < 6.5 and q <= 5):
            return 'Tier 1 (Severely Deprived)'
        elif sd < 7.0 and stress >= 6:
            return 'Tier 2 (Strained / Sub-Optimal)'
        else:
            return 'Tier 3 (Healthy / Rested)'

    df['Sleep_Health_Tier'] = df.apply(assign_tier, axis=1)
    return df

df = load_and_process_data()

# Sidebar
st.sidebar.title("🔬 Sleep Health Analytics")
st.sidebar.markdown("**NEEV Hackathon - Problem Statement 1**")
st.sidebar.markdown("---")
tier_filter = st.sidebar.multiselect(
    "Filter by Sleep Tier",
    options=df['Sleep_Health_Tier'].unique(),
    default=df['Sleep_Health_Tier'].unique()
)
occ_filter = st.sidebar.multiselect(
    "Filter by Occupation",
    options=sorted(df['Occupation'].unique()),
    default=sorted(df['Occupation'].unique())
)

# Apply filters
filtered_df = df[(df['Sleep_Health_Tier'].isin(tier_filter)) & (df['Occupation'].isin(occ_filter))]

# ===== HEADER =====
st.title("🌙 Sleep Health Analytics & Web Report Dashboard")
st.markdown("*Exploratory Data Analysis & Web Presentation - NEEV Hackathon*")
st.markdown("---")

# ===== KPI CARDS =====
col1, col2, col3, col4 = st.columns(4)

total_records = len(filtered_df)
tier_pct = filtered_df['Sleep_Health_Tier'].value_counts(normalize=True).mul(100).round(1)
tier1_avg_hr = filtered_df[filtered_df['Sleep_Health_Tier'] == 'Tier 1 (Severely Deprived)']['Heart Rate'].mean()

with col1:
    st.metric("📊 Total Records Analyzed", f"{total_records:,}")

with col2:
    st.metric("🔴 Tier 1 (Severely Deprived)", f"{tier_pct.get('Tier 1 (Severely Deprived)', 0):.1f}%")

with col3:
    st.metric("🟡 Tier 2 (Strained)", f"{tier_pct.get('Tier 2 (Strained / Sub-Optimal)', 0):.1f}%")

with col4:
    st.metric("🟢 Tier 3 (Healthy)", f"{tier_pct.get('Tier 3 (Healthy / Rested)', 0):.1f}%")

# Extra KPI row
col5, col6, col7 = st.columns(3)
with col5:
    st.metric("❤️ Avg Heart Rate (Tier 1)", f"{tier1_avg_hr:.0f} bpm" if not pd.isna(tier1_avg_hr) else "N/A")
with col6:
    st.metric("👟 Avg Daily Steps (All)", f"{filtered_df['Daily Steps'].mean():,.0f}")
with col7:
    st.metric("😴 Avg Sleep Duration", f"{filtered_df['Sleep Duration'].mean():.1f} hrs")

st.markdown("---")

# ===== VISUAL INSIGHTS =====
st.header("📈 Visual Insights")

# Row 1: Sleep Tier Breakdown by Profession + Scatter Plot
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("Sleep Tier Distribution by Profession")
    tier_occ = filtered_df.groupby(['Occupation', 'Sleep_Health_Tier']).size().reset_index(name='Count')
    fig_bar = px.bar(
        tier_occ, x='Occupation', y='Count', color='Sleep_Health_Tier',
        color_discrete_map={
            'Tier 1 (Severely Deprived)': '#e74c3c',
            'Tier 2 (Strained / Sub-Optimal)': '#f39c12',
            'Tier 3 (Healthy / Rested)': '#27ae60'
        },
        title="Sleep Health Tiers Across Occupations"
    )
    fig_bar.update_layout(xaxis_tickangle=-45, height=450, showlegend=True)
    st.plotly_chart(fig_bar, use_container_width=True)

with col_right:
    st.subheader("Daily Steps vs Sleep Duration")
    fig_scatter = px.scatter(
        filtered_df, x='Daily Steps', y='Sleep Duration',
        color='Sleep_Health_Tier',
        color_discrete_map={
            'Tier 1 (Severely Deprived)': '#e74c3c',
            'Tier 2 (Strained / Sub-Optimal)': '#f39c12',
            'Tier 3 (Healthy / Rested)': '#27ae60'
        },
        hover_data=['Occupation', 'Stress Level', 'Quality of Sleep'],
        title="Daily Steps vs Sleep Duration by Tier"
    )
    fig_scatter.update_layout(height=450)
    st.plotly_chart(fig_scatter, use_container_width=True)

# Row 2: Comparative Chart - Stress Level and Heart Rate across Tiers
st.subheader("Stress Level & Heart Rate Comparison Across Tiers")

col_a, col_b = st.columns(2)

with col_a:
    fig_box_stress = px.box(
        filtered_df, x='Sleep_Health_Tier', y='Stress Level',
        color='Sleep_Health_Tier',
        color_discrete_map={
            'Tier 1 (Severely Deprived)': '#e74c3c',
            'Tier 2 (Strained / Sub-Optimal)': '#f39c12',
            'Tier 3 (Healthy / Rested)': '#27ae60'
        },
        title="Stress Level Distribution by Tier"
    )
    fig_box_stress.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig_box_stress, use_container_width=True)

with col_b:
    fig_box_hr = px.box(
        filtered_df, x='Sleep_Health_Tier', y='Heart Rate',
        color='Sleep_Health_Tier',
        color_discrete_map={
            'Tier 1 (Severely Deprived)': '#e74c3c',
            'Tier 2 (Strained / Sub-Optimal)': '#f39c12',
            'Tier 3 (Healthy / Rested)': '#27ae60'
        },
        title="Heart Rate Distribution by Tier"
    )
    fig_box_hr.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig_box_hr, use_container_width=True)

# Additional insight: Tier composition stacked bar
st.subheader("Tier Composition by Occupation (Stacked %)")
tier_occ_pct = filtered_df.groupby(['Occupation', 'Sleep_Health_Tier']).size().reset_index(name='Count')
tier_occ_total = tier_occ_pct.groupby('Occupation')['Count'].transform('sum')
tier_occ_pct['Percentage'] = (tier_occ_pct['Count'] / tier_occ_total * 100).round(1)

fig_stacked = px.bar(
    tier_occ_pct, x='Occupation', y='Percentage', color='Sleep_Health_Tier',
    color_discrete_map={
        'Tier 1 (Severely Deprived)': '#e74c3c',
        'Tier 2 (Strained / Sub-Optimal)': '#f39c12',
        'Tier 3 (Healthy / Rested)': '#27ae60'
    },
    title="Percentage Tier Composition by Occupation"
)
fig_stacked.update_layout(xaxis_tickangle=-45, height=450)
st.plotly_chart(fig_stacked, use_container_width=True)

st.markdown("---")

# ===== EXECUTIVE SUMMARY =====
st.header("📋 Executive Summary")

# Compute key insights
tier1_count = len(filtered_df[filtered_df['Sleep_Health_Tier'] == 'Tier 1 (Severely Deprived)'])
tier2_count = len(filtered_df[filtered_df['Sleep_Health_Tier'] == 'Tier 2 (Strained / Sub-Optimal)'])
tier3_count = len(filtered_df[filtered_df['Sleep_Health_Tier'] == 'Tier 3 (Healthy / Rested)'])

# Most vulnerable occupations
vulnerable = filtered_df[filtered_df['Sleep_Health_Tier'].isin(['Tier 1 (Severely Deprived)', 'Tier 2 (Strained / Sub-Optimal)'])]
if len(vulnerable) > 0:
    occ_vuln = vulnerable.groupby('Occupation').size().sort_values(ascending=False)
    top_vuln = occ_vuln.head(3).index.tolist()
else:
    top_vuln = []

# Tier 1 specific occupations
tier1_occ = filtered_df[filtered_df['Sleep_Health_Tier'] == 'Tier 1 (Severely Deprived)']['Occupation'].value_counts().head(3).index.tolist()

# Average metrics by tier
avg_stress_t1 = filtered_df[filtered_df['Sleep_Health_Tier'] == 'Tier 1 (Severely Deprived)']['Stress Level'].mean()
avg_stress_t2 = filtered_df[filtered_df['Sleep_Health_Tier'] == 'Tier 2 (Strained / Sub-Optimal)']['Stress Level'].mean()
avg_stress_t3 = filtered_df[filtered_df['Sleep_Health_Tier'] == 'Tier 3 (Healthy / Rested)']['Stress Level'].mean()

avg_steps_t1 = filtered_df[filtered_df['Sleep_Health_Tier'] == 'Tier 1 (Severely Deprived)']['Daily Steps'].mean()
avg_steps_t3 = filtered_df[filtered_df['Sleep_Health_Tier'] == 'Tier 3 (Healthy / Rested)']['Daily Steps'].mean()

summary_text = f"""
### Key Findings

**Population Distribution:** Of the **{total_records} individuals** analyzed:
- **Tier 1 (Severely Deprived):** {tier1_count} people ({tier_pct.get('Tier 1 (Severely Deprived)', 0):.1f}%) — critically low sleep (<6 hrs or <6.5 hrs with poor quality)
- **Tier 2 (Strained/Sub-Optimal):** {tier2_count} people ({tier_pct.get('Tier 2 (Strained / Sub-Optimal)', 0):.1f}%) — moderate sleep deficit with high stress (≥6)
- **Tier 3 (Healthy/Rested):** {tier3_count} people ({tier_pct.get('Tier 3 (Healthy / Rested)', 0):.1f}%) — adequate sleep and manageable stress

**Most Vulnerable Occupational Groups:**
"""

if tier1_occ:
    summary_text += f"- **Critically sleep-deprived (Tier 1):** {', '.join(tier1_occ)} show the most severe sleep deficits\n"

if top_vuln:
    summary_text += f"- **High-risk for strain (Tier 1+2 combined):** {', '.join(top_vuln)} have the highest concentration of poor sleep health\n"

summary_text += f"""

**Physiological Markers:**
- **Stress Levels:** Tier 1 averages **{avg_stress_t1:.1f}/10**, Tier 2 averages **{avg_stress_t2:.1f}/10**, Tier 3 averages **{avg_stress_t3:.1f}/10**
- **Heart Rate:** Severely deprived group averages **{tier1_avg_hr:.0f} bpm** (elevated vs normal 60-100)
- **Physical Activity:** Tier 1 averages **{avg_steps_t1:,.0f} steps/day** vs Tier 3's **{avg_steps_t3:,.0f} steps/day**

---

### 🎯 Actionable Lifestyle Takeaways

| Priority | Recommendation | Target Group |
|----------|----------------|--------------|
| **Critical** | Enforce minimum 7-hour sleep schedule; consider workload redistribution | Tier 1 occupations: {', '.join(tier1_occ) if tier1_occ else 'N/A'} |
| **High** | Implement stress management programs (mindfulness, counseling access) | Tier 1 & 2 — all high-stress roles |
| **High** | Promote daily movement: target 7,000+ steps; correlate with sleep quality | Sedentary roles (Software Engineer, Accountant, Scientist) |
| **Medium** | Screen for sleep disorders (apnea, insomnia) — {filtered_df[filtered_df['Sleep Disorder'] != 'None'].shape[0]} cases detected | All tiers, especially Tier 1 |
| **Medium** | Optimize sleep environment: temperature, light, noise control | Universal |
| **Ongoing** | Monthly sleep health check-ins; track tier migration over time | Organization-wide |

---

### 📊 Data Quality Notes
- **Sleep Disorder:** {df['Sleep Disorder'].isna().sum()} missing values imputed as "None" before analysis
- **Tier Logic:** Deterministic rules based on sleep duration, quality, and stress — no ML model used
- **Sample Size:** 374 records across 11 occupations; results indicative, not nationally representative
"""

st.markdown(summary_text)

st.markdown("---")
st.caption("Built for NEEV Hackathon • Problem Statement 1 • Sleep Health Analytics Dashboard")