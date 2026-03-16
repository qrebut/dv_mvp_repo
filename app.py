import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(page_title="Paris Unmapped | MVP", layout="wide", page_icon="🥐")

st.markdown("""
    <style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    </style>
""", unsafe_allow_html=True)

st.title("🗺️ Paris Unmapped: Is the 15-Minute City a Luxury?")

st.markdown("""
Welcome to our beta exploratory dashboard. The **15-Minute City** is an urban planning concept where all essential daily needs are reachable within a short walk. 
Our research asks an important question: **Does high accessibility come with a premium price tag, pricing out students?**
""")
@st.cache_data
def load_data():
    final_df = pd.read_csv("paris_80_quartiers_final.csv")
    
    final_df = final_df.rename(columns={'quartier': 'Arrondissement'})
    
    final_df['Arrondissement'] = final_df['Arrondissement'].astype(str)
    
    if 'Lat' not in final_df.columns:
        np.random.seed(42)
        # Generate 80 random points roughly within the Paris bounding box
        final_df['Lat'] = np.random.uniform(48.82, 48.89, len(final_df))
        final_df['Lon'] = np.random.uniform(2.27, 2.40, len(final_df))
        
    return final_df

final_df = load_data()


with st.sidebar:
    st.header("🎛️ Dashboard Controls")
    
    max_rent = st.slider("Budget: Max Rent (€/m²)", 
                         min_value=float(final_df['avg_rent'].min()), 
                         max_value=float(final_df['avg_rent'].max()), 
                         value=float(final_df['avg_rent'].mean()), step=0.5)

    min_shops = st.slider("Need: Min Shop Count", 
                          min_value=int(final_df['shop_count'].min()), 
                          max_value=int(final_df['shop_count'].max()), 
                          value=int(final_df['shop_count'].median()), step=10)
    
    st.divider()
    
    st.markdown("### 📖 How to read this tool")
    st.markdown("""
    1. **Set your budget** and desired amenity level above.
    2. **Check the Map** to see *where* these neighborhoods are located.
    3. **Check the Scatter Plot** to see the statistical trade-off. 
    4. **Look for the Sweet Spot:** The ideal neighborhood is in the bottom-right of the scatter plot (High Amenities, Low Rent).
    """)

filtered_df = final_df[(final_df['avg_rent'] <= max_rent) & (final_df['shop_count'] >= min_shops)]

st.divider()
if not filtered_df.empty:
    best_value_arr = filtered_df.loc[filtered_df['value_score'].idxmax()]
    
    colA, colB, colC = st.columns(3)
    colA.metric("Neighborhoods Matching Criteria", len(filtered_df), "Out of 80") 
    colB.metric("Avg Rent of Selection", f"{filtered_df['avg_rent'].mean():.1f} €/m²")
    colC.metric("Top 'Sweet Spot' Quartier", f"ID: {best_value_arr['Arrondissement']}", f"Value Score: {best_value_arr['value_score']}")
else:
    st.warning("No neighborhoods match your current filters. Try increasing your budget or lowering your shop requirements.")

st.divider()

col1, col2 = st.columns(2, gap="large")

with col1:
    st.subheader("📍 The Spatial View")
    st.markdown("*Size = Shop Density | Color = Rent Price (Green is cheaper)*")
    
    fig_map = px.scatter_mapbox(
        filtered_df, lat="Lat", lon="Lon", 
        hover_name="Arrondissement", 
        hover_data={"Lat": False, "Lon": False, "avg_rent": True, "shop_count": True, "value_score": True},
        color="avg_rent", size="shop_count",
        color_continuous_scale="RdYlGn_r", size_max=25, zoom=10.5, height=500,
        mapbox_style="carto-positron"
    )
    fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, coloraxis_showscale=False)
    st.plotly_chart(fig_map, use_container_width=True)

with col2:
    st.subheader("📈 The Analytical View")
    st.markdown("*Finding the Sweet Spot: Look for the bottom-right corner.*")
    
    fig_scatter = px.scatter(
        filtered_df, x="shop_count", y="avg_rent", 
        text="Arrondissement", color="avg_rent",
        color_continuous_scale="RdYlGn_r",
        labels={"shop_count": "Essential Shop Count", "avg_rent": "Avg Rent (€/m²)"},
        height=500
    )
    fig_scatter.update_traces(textposition='top center', marker=dict(size=14, line=dict(width=1, color='white')))
    fig_scatter.update_layout(
        coloraxis_colorbar=dict(title="Rent €/m²"),
        plot_bgcolor="rgba(240, 240, 240, 0.5)",
        xaxis=dict(showgrid=True, gridcolor='white'),
        yaxis=dict(showgrid=True, gridcolor='white')
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("---")

col3, col4 = st.columns(2)

with col3:
    with st.expander("🔬 Methodology & Metrics"):
        st.markdown("""
        **1. The Amenity Score (`shop_count`)**
        This score is computed by aggregating the total count of "essential" commercial establishments (bakeries, pharmacies, supermarkets, etc.) within each arrondissement.
        
        **2. Average Rent (`avg_rent`)**
        The official reference rent fixed by the Paris prefecture, aggregated by neighborhood.
        
        **3. The Value Score (`value_score`)**
        `final_df['value_score'] = (final_df['shop_count'] / final_df['avg_rent']).round(2)`
        
        **What This Means:** It's *shops per euro*, how many essential shops you get for each euro of rent per m². A higher score means better value for your money."
        """)
        
    with st.expander("📊 About the Data"):
        st.markdown("""
        * **🏘️ Rental Prices:** Average reference rent (€/m²) per arrondissement from the Paris Rent Control dataset (2025). *(Source: Paris Open Data / DRIHL)*
        * **🏪 Amenities:** Count of essential shops per arrondissement (bakeries, supermarkets, bookstores, etc.) from the Permanent Equipment Database. *(Source: INSEE BPE)*
        * **🗺️ Geography:** Official arrondissement boundaries. *(Source: IGN)*
        """)

with col4:
    with st.expander("🚧 MVP Limitations & Next Steps"):
        st.markdown("""
        *This MVP has several limitations that we want to address in the final project:*
        
        * **Granularity:** Data is currently aggregated at the *Arrondissement* level (20 zones). We would want our final version to be broken down at the *Quartier* level (80 zones) in order to expose price differences within a single district.
        * **Isochrone Accuracy:** We are currently using raw shop counts within administrative boundaries. Although difficult, we could map actual 15-minute walking radii using network graphs (OSMnx).
        * **Shop Weighting:** Currently, a large supermarket and a small bakery carry the same weight (1 shop). Future iterations should categorize and weigh amenities by utility.
        * **Data Completeness (Pharmacies):** The dataset used for amenity computations did not include pharmacies. Since healthcare access is a core pillar of the 15-minute city framework, we must source and include this data in future iterations.
        """)

st.subheader("🗄️ Filtered Data Overview")
st.dataframe(
    filtered_df[['Arrondissement', 'avg_rent', 'shop_count', 'value_score']]
    .sort_values('value_score', ascending=False)
    .style.format({
        'avg_rent': "{:.2f} €",
        'value_score': "{:.2f}"
    }), 
    use_container_width=True,
    hide_index=True
)
