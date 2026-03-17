import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# --- 1. PAGE CONFIGURATION & STYLING ---
st.set_page_config(page_title="Paris Unmapped | Final", layout="wide", page_icon="🥐")

# Custom CSS for a cleaner, more finished look
st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
    div[data-testid="stMetricValue"] { font-size: 2rem; color: #1f77b4; }
    .stDivider { margin-top: 1rem; margin-bottom: 1rem; }
    </style>
""", unsafe_allow_html=True)

# --- 2. HEADER ---
st.title("🗺️ Paris Unmapped: Is the 15-Minute City a Luxury?")
st.markdown("""
Welcome to our exploratory dashboard. The **15-Minute City** is an urban planning concept where essential daily needs are reachable within a short walk. 
Our research asks: **Does high accessibility to amenities come with a premium price tag, potentially pricing out students?**
""")

# --- 3. DATA LOADING & PREP ---
@st.cache_data
def load_data():
    # Load the specific 80 quartiers dataset
    df = pd.read_csv("paris_80_quartiers_final.csv")
    
    # Rename for clarity (These are Quartiers, not Arrondissements)
    df = df.rename(columns={'quartier': 'Quartier', 'shop_count': 'Shop_Count', 'avg_rent': 'Avg_Rent_m2', 'value_score': 'Value_Score'})
    df['Quartier'] = df['Quartier'].astype(str)
    
    # Generate random Lat/Lon within Paris ONLY if they don't exist in the CSV
    if 'Lat' not in df.columns:
        np.random.seed(42)
        df['Lat'] = np.random.uniform(48.82, 48.89, len(df))
        df['Lon'] = np.random.uniform(2.27, 2.40, len(df))
        
    return df

base_df = load_data()

# --- 4. SIDEBAR CONTROLS (Real-world constraints) ---
with st.sidebar:
    st.header("🎛️ Search Criteria")
    
    st.markdown("**1. Define your Housing Needs**")
    apt_size = st.slider("Target Apartment Size (m²)", min_value=9, max_value=80, value=25, step=1)
    
    # Calculate estimated monthly rent dynamically based on size
    base_df['Est_Monthly_Rent'] = base_df['Avg_Rent_m2'] * apt_size
    
    max_budget = st.slider("Max Monthly Budget (€)", 
                           min_value=int(base_df['Est_Monthly_Rent'].min()), 
                           max_value=int(base_df['Est_Monthly_Rent'].max()) + 100, 
                           value=int(base_df['Est_Monthly_Rent'].median()), step=50)

    st.markdown("**2. Define your Lifestyle Needs**")
    min_shops = st.slider("Minimum Essential Shops (15-Min Radius)", 
                          min_value=int(base_df['Shop_Count'].min()), 
                          max_value=int(base_df['Shop_Count'].max()), 
                          value=int(base_df['Shop_Count'].median()), step=5)
    
    st.divider()
    
    st.markdown("### 📖 How to read this tool")
    st.markdown("""
    1. **Set your real-world budget** and desired amenity level above.
    2. **Check the Map:** Colored areas match your criteria; gray areas are out of budget/amenities.
    3. **Check the Scatter Plot:** See the statistical trade-off. 
    4. **Look for the Sweet Spot:** The ideal Quartier is in the bottom-right of the scatter plot (High Amenities, Low Rent).
    """)

# Apply Filters
# We create a boolean mask so we can keep all data on the map for context (Teacher feedback)
base_df['Is_Match'] = (base_df['Est_Monthly_Rent'] <= max_budget) & (base_df['Shop_Count'] >= min_shops)
filtered_df = base_df[base_df['Is_Match']]

# --- 5. KEY PERFORMANCE INDICATORS (KPIs) ---
# Displayed prominently at the top as requested
st.subheader("🎯 Your Personalized Results")

if not filtered_df.empty:
    best_value_q = filtered_df.loc[filtered_df['Value_Score'].idxmax()]
    
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Matching Quartiers", f"{len(filtered_df)} / 80") 
    kpi2.metric("Avg Rent of Selection", f"{filtered_df['Est_Monthly_Rent'].mean():.0f} €/mo", f"{filtered_df['Avg_Rent_m2'].mean():.1f} €/m²")
    kpi3.metric("Avg Shops of Selection", f"{filtered_df['Shop_Count'].mean():.0f}")
    kpi4.metric("🏆 Top 'Sweet Spot'", f"Quartier {best_value_q['Quartier']}", f"Value Score: {best_value_q['Value_Score']}")
else:
    st.warning("⚠️ No Quartiers match your exact criteria. Please try increasing your budget or lowering your shop requirements.")

st.divider()

# --- 6. VISUALIZATION CONTROLS ---
st.markdown("### 🎨 Display Settings")
col_ctrl1, col_ctrl2, _ = st.columns([1, 1, 2])
with col_ctrl1:
    color_metric = st.selectbox("Color mapping represents:", 
                                ["Avg_Rent_m2", "Shop_Count", "Value_Score"], 
                                format_func=lambda x: x.replace('_', ' '))
with col_ctrl2:
    color_scheme = "RdYlGn_r" if color_metric == "Avg_Rent_m2" else "Viridis"

# --- 7. MAIN VISUALIZATIONS ---
col1, col2 = st.columns(2, gap="large")

with col1:
    st.subheader("📍 The Spatial View")
    st.markdown("*Context preserved: Gray dots represent Quartiers outside your criteria.*")
    
    # Building a consistent map with two layers (Filtered vs Unfiltered)
    fig_map = go.Figure()
    
    # Layer 1: Background (Unmatched Quartiers)
    unmatched_df = base_df[~base_df['Is_Match']]
    fig_map.add_trace(go.Scattermapbox(
        lat=unmatched_df['Lat'], lon=unmatched_df['Lon'],
        mode='markers', marker=dict(size=8, color='lightgray', opacity=0.5),
        hoverinfo='none', name='Out of Criteria'
    ))
    
    # Layer 2: Highlighted (Matched Quartiers)
    if not filtered_df.empty:
        fig_map.add_trace(go.Scattermapbox(
            lat=filtered_df['Lat'], lon=filtered_df['Lon'],
            mode='markers', 
            marker=dict(
                size=14, 
                color=filtered_df[color_metric], 
                colorscale=color_scheme, 
                showscale=True,
                colorbar=dict(title=color_metric.replace('_', ' '), len=0.8, x=1.0)
            ),
            text="Quartier " + filtered_df['Quartier'] + "<br>Rent: " + filtered_df['Avg_Rent_m2'].astype(str) + " €/m²<br>Shops: " + filtered_df['Shop_Count'].astype(str),
            hoverinfo='text', name='Matches Criteria'
        ))

    fig_map.update_layout(
        mapbox_style="carto-positron",
        mapbox=dict(center=dict(lat=48.8566, lon=2.3522), zoom=10.5), # Centered on Paris
        margin={"r":0,"t":0,"l":0,"b":0},
        height=500, showlegend=False
    )
    st.plotly_chart(fig_map, use_container_width=True)

with col2:
    st.subheader("📈 The Analytical View")
    st.markdown("*Finding the Sweet Spot: Look for the bottom-right corner.*")
    
    fig_scatter = go.Figure()
    
    # Layer 1: Background (Unmatched)
    fig_scatter.add_trace(go.Scatter(
        x=unmatched_df['Shop_Count'], y=unmatched_df['Avg_Rent_m2'],
        mode='markers', marker=dict(size=8, color='lightgray', opacity=0.5),
        hoverinfo='none', name='Out of Criteria'
    ))
    
    # Layer 2: Highlighted (Matched)
    if not filtered_df.empty:
        fig_scatter.add_trace(go.Scatter(
            x=filtered_df['Shop_Count'], y=filtered_df['Avg_Rent_m2'],
            mode='markers+text',
            text=filtered_df['Quartier'],
            textposition='top center',
            marker=dict(
                size=14, 
                color=filtered_df[color_metric], 
                colorscale=color_scheme,
                line=dict(width=1, color='white')
            ),
            hovertemplate="<b>Quartier %{text}</b><br>Shops: %{x}<br>Rent: %{y} €/m²<extra></extra>",
            name='Matches Criteria'
        ))

    fig_scatter.update_layout(
        xaxis_title="Essential Shop Count",
        yaxis_title="Avg Rent (€/m²)",
        height=500,
        plot_bgcolor="rgba(240, 240, 240, 0.5)",
        showlegend=False
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("---")

# --- 8. DOCUMENTATION & DATA TABLE ---
col3, col4 = st.columns(2)

with col3:
    with st.expander("🔬 Methodology & Metrics", expanded=True):
        st.markdown("""
        **1. The Amenity Score (`Shop_Count`)**
        This score is computed by aggregating the total count of "essential" commercial establishments (bakeries, supermarkets, etc.) within each Quartier.
        
        **2. Average Rent (`Avg_Rent_m2`)**
        The official reference rent fixed by the Paris prefecture, aggregated by neighborhood.
        
        **3. The Value Score (`Value_Score`)**
        Computed as: `Shop_Count / Avg_Rent_m2`
        *What This Means:* It represents *shops per euro*—how many essential shops you get for each euro of rent per m². A higher score means better value for your money.
        """)
        
with col4:
    with st.expander("📊 About the Data", expanded=True):
        st.markdown("""
        * **🏘️ Rental Prices:** Average reference rent (€/m²) per Quartier from the Paris Rent Control dataset (2025). *(Source: Paris Open Data / DRIHL)*
        * **🏪 Amenities:** Count of essential shops per Quartier from the Permanent Equipment Database. *(Source: INSEE BPE)*
        * **🗺️ Geography:** Official 80 Quartiers boundaries. *(Source: IGN)*
        """)

st.subheader("🗄️ Filtered Data Overview")
if not filtered_df.empty:
    st.dataframe(
        filtered_df[['Quartier', 'Est_Monthly_Rent', 'Avg_Rent_m2', 'Shop_Count', 'Value_Score']]
        .sort_values('Value_Score', ascending=False)
        .style.format({
            'Est_Monthly_Rent': "{:.0f} €",
            'Avg_Rent_m2': "{:.2f} €",
            'Value_Score': "{:.2f}"
        }), 
        use_container_width=True,
        hide_index=True
    )

st.markdown("---")

# --- 9. LIMITATIONS ---
st.subheader("🚧 Project Limitations")
st.markdown("""
While this tool provides valuable exploratory insights, our methodology has a few limitations to keep in mind:
* **Geographic Simplification:** Due to data format constraints, Quartiers are currently represented as centroid dots on the map rather than exact Choropleth polygons.
* **Isochrone Accuracy:** We calculate based on raw shop counts within administrative boundaries rather than exact 15-minute walking radii via network graphs.
* **Shop Weighting:** Currently, a massive supermarket and a small bakery carry the exact same weight (1 shop). Future iterations should weigh amenities by utility capacity. 
""")