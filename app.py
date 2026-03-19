import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ── Page config ──
st.set_page_config(
    page_title="TravelTide — Customer Segmentation",
    page_icon="✈️",
    layout="wide"
)

# ── Color palette ──
PERK_COLORS = {
    'Exclusive Discounts' : '#F4A261',
    'Free Checked Bag'    : '#2A9D8F',
    'No Cancellation Fee' : '#E76F51',
    'Free Hotel Meal'     : '#457B9D',
    'Priority Boarding'   : '#8338EC'
}
PERK_ORDER = list(PERK_COLORS.keys())

PERK_ICONS = {
    'Exclusive Discounts' : '🏷️',
    'Free Checked Bag'    : '🧳',
    'No Cancellation Fee' : '❌',
    'Free Hotel Meal'     : '🍽️',
    'Priority Boarding'   : '🛫'
}

# ── Load data ──
@st.cache_data
def load_data():
    df = pd.read_csv('outputs/traveltide_final_segments.csv')
    df['age'] = pd.to_numeric(df['age'], errors='coerce').astype(int)
    df['total_flights_booked'] = pd.to_numeric(df['total_flights_booked'], errors='coerce')
    df['total_hotels_booked'] = pd.to_numeric(df['total_hotels_booked'], errors='coerce')
    df['total_cancellations'] = pd.to_numeric(df['total_cancellations'], errors='coerce')
    return df

df = load_data()

# ── Sidebar navigation ──
st.sidebar.image("https://img.icons8.com/color/96/airplane-mode-on.png", width=80)
st.sidebar.title("TravelTide")
st.sidebar.markdown("Customer Perk Segmentation")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate",
    ["📊 Overview", "🔍 Segment Explorer", "👤 Customer Lookup", "📖 Methodology"]
)

# ════════════════════════════════════════════════════════
# PAGE 1 — OVERVIEW
# ════════════════════════════════════════════════════════
if page == "📊 Overview":

    st.title("✈️ TravelTide — Customer Perk Segmentation")
    st.markdown("Behavioral segmentation of **24,724 active customers** into 5 personalized reward perks.")
    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Customers", f"{len(df):,}")
    col2.metric("Perks", "5")
    col3.metric("Largest Segment", df['assigned_perk'].value_counts().index[0])
    col4.metric("Smallest Segment", df['assigned_perk'].value_counts().index[-1])

    st.markdown("---")

    seg_counts = df['assigned_perk'].value_counts().reindex(PERK_ORDER)

    col_left, col_right = st.columns(2)

    with col_left:
        fig_bar = go.Figure(go.Bar(
            x=seg_counts.values.tolist(),
            y=seg_counts.index.tolist(),
            orientation='h',
            marker_color=[PERK_COLORS[p] for p in seg_counts.index],
            text=[f'{v:,} ({v/len(df)*100:.1f}%)' for v in seg_counts.values],
            textposition='outside'
        ))
        fig_bar.update_layout(
            title='Segment Sizes',
            xaxis_title='Number of Customers',
            showlegend=False,
            xaxis=dict(range=[0, max(seg_counts.values) * 1.35])
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_right:
        fig_pie = go.Figure(data=[go.Pie(
            labels=seg_counts.index.tolist(),
            values=seg_counts.values.tolist(),
            marker_colors=[PERK_COLORS[p] for p in seg_counts.index],
            textinfo='percent+label',
            pull=[0.03] * 5
        )])
        fig_pie.update_layout(title='Segment Distribution', showlegend=True)
        st.plotly_chart(fig_pie, use_container_width=True)

# ════════════════════════════════════════════════════════
# PAGE 2 — SEGMENT EXPLORER
# ════════════════════════════════════════════════════════
elif page == "🔍 Segment Explorer":

    st.title("🔍 Segment Explorer")
    st.markdown("Select a perk to explore who is in that segment.")
    st.markdown("---")

    selected_perk = st.selectbox(
        "Select a Perk Segment",
        PERK_ORDER,
        format_func=lambda x: f"{PERK_ICONS[x]} {x}"
    )

    seg_df = df[df['assigned_perk'] == selected_perk].copy()
    color  = PERK_COLORS[selected_perk]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Customers",      f"{len(seg_df):,}")
    col2.metric("Avg Age",        f"{seg_df['age'].mean():.0f}")
    col3.metric("% Married",      f"{seg_df['married'].mean()*100:.1f}%")
    col4.metric("% Has Children", f"{seg_df['has_children'].mean()*100:.1f}%")

    st.markdown("---")

    col_left, col_right = st.columns(2)

    with col_left:
        age_values = seg_df['age'].dropna().astype(int).tolist()
        fig_age = go.Figure(go.Histogram(
            x=age_values,
            nbinsx=20,
            marker_color=color,
            marker_line_color='white',
            marker_line_width=1
        ))
        fig_age.update_layout(
            title=f'Age Distribution — {selected_perk}',
            xaxis_title='Age',
            yaxis_title='Number of Customers',
            bargap=0.1
        )
        st.plotly_chart(fig_age, use_container_width=True)

    with col_right:
        gender_counts = seg_df['gender'].value_counts()
        fig_gender = go.Figure(data=[go.Pie(
            labels=gender_counts.index.tolist(),
            values=gender_counts.values.tolist(),
            marker_colors=['#457B9D', '#E76F51', '#2A9D8F'],
            textinfo='percent+label',
            hole=0.4
        )])
        fig_gender.update_layout(title=f'Gender — {selected_perk}')
        st.plotly_chart(fig_gender, use_container_width=True)

    col_left2, col_right2 = st.columns(2)

    with col_left2:
        top_countries = seg_df['home_country'].value_counts().head(10)
        fig_country = go.Figure(go.Bar(
            x=top_countries.values.tolist(),
            y=top_countries.index.tolist(),
            orientation='h',
            marker_color=color,
            marker_line_color='white',
            marker_line_width=1
        ))
        fig_country.update_layout(
            title='Top 10 Home Countries',
            xaxis_title='Number of Customers',
            yaxis_title='',
            showlegend=False
        )
        st.plotly_chart(fig_country, use_container_width=True)

    with col_right2:
        metrics   = ['Avg Flights', 'Avg Hotels', 'Avg Cancellations']
        values    = [
            round(float(seg_df['total_flights_booked'].mean()), 2),
            round(float(seg_df['total_hotels_booked'].mean()), 2),
            round(float(seg_df['total_cancellations'].mean()), 2)
        ]
        fig_beh = go.Figure(go.Bar(
            x=metrics,
            y=values,
            marker_color=color,
            marker_line_color='white',
            marker_line_width=1,
            text=[str(v) for v in values],
            textposition='outside'
        ))
        fig_beh.update_layout(
            title='Avg Booking Behavior',
            yaxis_title='Average Count',
            yaxis=dict(range=[0, max(values) * 1.3])
        )
        st.plotly_chart(fig_beh, use_container_width=True)

# ════════════════════════════════════════════════════════
# PAGE 3 — CUSTOMER LOOKUP
# ════════════════════════════════════════════════════════
elif page == "👤 Customer Lookup":

    st.title("👤 Customer Lookup")
    st.markdown("Enter a customer ID to see their assigned perk and behavioral scores.")
    st.markdown("---")

    user_id = st.number_input("Enter User ID", min_value=int(df['user_id'].min()),
                               max_value=int(df['user_id'].max()), step=1)

    if st.button("Look Up Customer"):
        customer = df[df['user_id'] == user_id]

        if len(customer) == 0:
            st.error(f"No customer found with ID {user_id}")
        else:
            row = customer.iloc[0]
            perk = row['assigned_perk']

            st.success(f"{PERK_ICONS[perk]} This customer is assigned to: **{perk}**")

            st.markdown("---")
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Age",          f"{row['age']}")
            col2.metric("Gender",       f"{row['gender']}")
            col3.metric("Married",      "Yes" if row['married'] else "No")
            col4.metric("Has Children", "Yes" if row['has_children'] else "No")
            col5.metric("Country",      f"{row['home_country'].title()}")

            st.markdown("---")
            st.subheader("Perk Affinity Scores")

            scores = {
                'Exclusive Discounts' : round(float(row['idx_discount']), 4),
                'Free Checked Bag'    : round(float(row['idx_bag']), 4),
                'No Cancellation Fee' : round(float(row['idx_cancellation']), 4),
                'Free Hotel Meal'     : round(float(row['idx_hotel']), 4),
                'Priority Boarding'   : round(float(row['idx_priority']), 4)
            }

            fig_scores = go.Figure(go.Bar(
                x=list(scores.keys()),
                y=list(scores.values()),
                marker_color=[PERK_COLORS[p] for p in scores.keys()],
                marker_line_color='white',
                marker_line_width=1,
                text=[str(v) for v in scores.values()],
                textposition='outside'
            ))
            fig_scores.update_layout(
                xaxis_title='Perk',
                yaxis_title='Affinity Score',
                showlegend=False,
                yaxis=dict(range=[0, max(scores.values()) * 1.4 if max(scores.values()) > 0 else 0.1])
            )
            st.plotly_chart(fig_scores, use_container_width=True)

# ════════════════════════════════════════════════════════
# PAGE 4 — METHODOLOGY
# ════════════════════════════════════════════════════════
elif page == "📖 Methodology":

    st.title("📖 Methodology")
    st.markdown("---")

    st.markdown("""
    ## How the Segmentation Works

    ### 1. Data Extraction (SQL)
    A cohort of **24,724 active users** was extracted from the TravelTide
    PostgreSQL database — users with at least 7 sessions after January 4, 2023.
    Behavioral metrics were computed by joining the `sessions`, `flights`,
    `hotels`, and `users` tables.

    ### 2. Feature Engineering (Python)
    - **Null filling:** Missing values filled with 0 — absence of behavior = zero affinity
    - **Outlier capping:** All metrics capped at the 99th percentile
    - **MinMax scaling:** All metrics scaled to 0–1 for fair distance calculations

    ### 3. Perk Affinity Indexes
    For each perk, its scaled metrics are multiplied together to form a
    single composite index score:

    | Perk | Index Formula |
    |------|--------------|
    | 🏷️ Exclusive Discounts | discount_proportion × avg_discount × ads |
    | 🧳 Free Checked Bag | avg_bags × total_bags |
    | ❌ No Cancellation Fee | cancellation_rate |
    | 🍽️ Free Hotel Meal | avg_hotel_cost × avg_nights × total_spend |
    | 🛫 Priority Boarding | avg_fare × avg_seats × total_spend |

    ### 4. Fuzzy Segmentation
    Each customer is ranked for all 5 perks. They are assigned to the perk
    where their rank is lowest — meaning their highest relative affinity.
    Every customer is assigned to exactly **one perk** (mutually exclusive).

    ### 5. K-Means Validation
    K-Means clustering (K=5) was run as a second method and compared to
    rule-based segmentation. Rule-based was recommended because:
    - Perks are pre-defined business categories
    - K-Means misses rare but important behaviors like cancellations
    - Rule-based results are fully interpretable by stakeholders

    ---
    **Author:** Akakinad | ML Engineer | Berlin

    **GitHub:** [traveltide-customer-segmentation](https://github.com/Akakinad/traveltide-customer-segmentation)
    """)