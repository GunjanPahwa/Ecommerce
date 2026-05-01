📦 Olist Delivery Performance Audit

An interactive data analytics app that quantifies how shipping delays impact business health and customer satisfaction for Brazil's largest e-commerce marketplace.

Live Demo: https://ecommercedashboard12.streamlit.app/

Overview

This project audits delivery performance across 100,000+ orders from the Olist Brazilian E-Commerce dataset (2017–2018). It surfaces which sellers, states, and time periods are driving late deliveries — and quantifies the revenue and review score impact.

📈 Business Impact & Decision Support:

-This project moves beyond descriptive statistics to provide actionable insights for marketplace stakeholders:

-Revenue Recovery: Quantified that orders delayed by 7+ days result in a 25% drop in customer retention, identifying a specific "Revenue at Risk" segment for targeted marketing intervention.

-Operational Efficiency: Pinpointed three specific Brazilian states where late rates exceed 15%, providing a data-backed case for logistics partner renegotiation or local warehousing expansion.

-Customer Trust: Established a direct correlation between delivery speed and review scores, proving that reducing average shipping time by just 2 days could potentially increase the platform's average rating from 4.1 to 4.4 stars.

-Risk Mitigation: Developed a "Critical Seller" quadrant that allows the Olist operations team to automate warnings for sellers with high GMV but failing delivery SLAs.


Tech Stack:

Python — data processing and app logic

SQL — data extraction and aggregation

Pandas / NumPy — data wrangling

Plotly — interactive charts

Streamlit — web app framework

Power BI — business intelligence dashboard

Groq API (Llama 3.3 70B) — AI data assistant


📊 Key Dashboard Features

1. Executive Performance Layer
   
-KPI Tracking: Real-time visibility into Total Orders, Average Late Rate (8.77%), and Estimated Revenue at Risk.

-Monthly Trends: Visualizes performance fluctuations to identify seasonal logistics strain.

2. Geographic Risk Mapping
   
-State-Level Heatmap: Highlighting high-delay regions across Brazil to pinpoint infrastructure failures.

-Freight Analysis: Correlates shipping costs with delivery speed to find "low-efficiency" zones.

3. Seller Intelligence & Root Cause
   
-Decomposition Tree: Drills down from Product Categories to specific states to find the root cause of delays.

-Performance Quadrants: Categorizes sellers into "Star," "At Risk," or "Critical" based on their late rates and customer review scores.

4. PowerBI DashBoard Integration

5. "Ask the Data" (AI Integration)
   
An integrated LLM-powered assistant (via Groq) that allows stakeholders to query the audit data using natural language for instant insights.




