# 🗺️ Paris Unmapped: Is the 15-Minute City a Luxury?

![Python](https://img.shields.io/badge/Python-3.11-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B.svg)
![Plotly](https://img.shields.io/badge/Plotly-Interactive_Charts-3f4f75.svg)

**A Data Visualization Dashboard exploring the intersection of urban accessibility and housing affordability in Paris.**

This project is the final deliverable for the **Data Visualization** course as part of the **Master's in Data Science & Business Analytics**.

---

## 📖 About the Project

The **"15-Minute City"** is a popular urban planning concept aiming to provide all residents with access to essential services (food, healthcare, culture, etc.) within a short walk or bike ride. While conceptually designed to improve the quality of life and reduce carbon emissions, critics argue it may lead to "green gentrification"—where highly accessible neighborhoods become exclusive enclaves for the wealthy.

**Our Research Question:** *Does high accessibility to essential services correlate with a premium price tag in Paris, effectively pricing out lower-income groups like students?*

This interactive dashboard acts as an exploratory tool to test this hypothesis. It allows students and prospective renters to input their real-world constraints (budget and apartment size) to find "Sweet Spots": neighborhoods that offer excellent amenity density without the premium price tag.

## ✨ Key Features

* **Real-World Budget Filtering:** Users input their target apartment size (m²) and monthly budget (€), dynamically calculating the viable neighborhoods rather than relying purely on price-per-square-meter.
* **Persistent Context Mapping:** A dual-layer spatial view (built with Plotly) keeps all 80 Parisian *Quartiers* visible. Neighborhoods that do not match the user's criteria are grayed out, preserving the geographic context and allowing for easy comparison.
* **Analytical "Sweet Spot" Finder:** A linked scatter plot visualizes the statistical trade-off between Rent and Essential Shops, helping users identify high-value areas in the bottom-right quadrant.
* **Customizable Visual Encodings:** Users can dynamically change what the color mapping represents (Average Rent, Shop Count, or Value Score) to view the data from different analytical perspectives.

## 🗄️ Data Sources

The dashboard combines and aggregates spatial, economic, and commercial data at the level of the 80 Parisian *Quartiers*:

1. **Rental Prices (Affordability):** Average reference rent (€/m²) per Quartier derived from the official Paris Rent Control dataset (2025). Maintained by the *Direction Régionale et Interdépartementale de l'Hébergement et du Logement (DRIHL)*.
2. **Amenities (Accessibility):** Count of essential shops per Quartier (bakeries, supermarkets, bookstores, etc.) derived from the Permanent Equipment Database. Maintained by *INSEE (Base Permanente des Équipements - BPE)*.
3. **Geography:** Official boundaries and coordinates of the 80 *Quartiers Administratifs* provided by *IGN*.

## 🔬 Methodology & Metrics

* **The Amenity Score (`Shop_Count`):** The total aggregated count of essential commercial establishments within a given Quartier.
* **Average Rent (`Avg_Rent_m2`):** The mean reference rent per square meter for the area.
* **The Value Score (`Value_Score`):** Calculated as `Shop_Count / Avg_Rent_m2`. This represents *"shops per euro"*—indicating how many amenities you get per euro of rent. A higher score signifies better value.

## 🚀 How to Run Locally

This project includes a `.devcontainer` setup for instant deployment in GitHub Codespaces or VS Code Dev Containers.

To run it manually on your local machine:

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/your-username/paris-unmapped.git](https://github.com/your-username/paris-unmapped.git)
   cd paris-unmapped
   
2. **Install the required dependencies:**
(Ensure you have Python 3.8+ installed)
   ```bash
    pip install -r requirements.txt

3. **Run the Streamlit app:**
   ```bash
    streamlit run app.py

4. **View the dashboard:**
   Open your browser and navigate to http://localhost:8501.

👥 Team: - Quentin Rebut
    - Haidar Bouaquiche

*Master in Data Science & Business Analytics*
