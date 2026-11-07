# SupplyChainIQ
### Autonomous Supply Chain Decision Agent

## 1. Project Overview

SupplyChainIQ is a Python-based supply chain management system that analyses inventory levels, historical sales data and supplier information to generate intelligent procurement recommendations.

It helps identify stockout risks, calculate reorder quantities, compare suppliers and support better purchasing decisions.

## 2. Project Objectives

- Monitor current inventory levels.
- Analyse historical sales and average daily demand.
- Identify potential stockout risks.
- Compare suppliers based on price and delivery time.
- Calculate recommended reorder quantities.
- Generate intelligent supplier recommendations.
- Produce downloadable procurement reports.

## 3. Technologies Used

- Python 3.8
- Streamlit
- Pandas
- Matplotlib
- CSV datasets

## 4. Main Features

1. Inventory Overview
2. Inventory Details
3. Demand Analysis
4. Stockout Risk Analysis
5. Supplier Comparison
6. What-if Analysis
7. Intelligent Supplier Recommendation
8. Reorder Recommendations
9. Procurement Report Generation

## 5. Project Structure

```text
SupplyChain/
│
├── app.py
├── inventory.csv
├── sales.csv
├── suppliers.csv
│
├── modules/
│   ├── inventory.py
│   ├── demand.py
│   ├── stockout.py
│   ├── supplier.py
│   ├── reorder.py
│   └── report.py
│
└── reports/
    └── procurement_report.csv
```

## 6. Installation

Install the required libraries:

```bash
pip install streamlit==1.38.0 pandas==1.3.5 matplotlib==3.5.3
```

## 7. How to Run

Open the project directory in VS Code and execute:

```bash
python -m streamlit run app.py
```

Open the local URL displayed in the terminal.

## 8. Working Principle

The system uses historical sales data to calculate average daily demand.

Expected Demand = Average Daily Demand × Supplier Delivery Days

Reorder Quantity = Expected Demand + Safety Stock − Current Stock

If the calculated reorder quantity is negative, the system recommends zero additional units.

The system classifies stockout risk into three categories:

- HIGH: Current stock is below expected demand.
- MEDIUM: Current stock is sufficient for expected demand but does not exceed expected demand plus safety stock.
- LOW: Current stock exceeds expected demand plus safety stock.

Supplier recommendations consider inventory risk, delivery time and unit price.

## 9. Expected Output

The application provides:

- Inventory monitoring dashboard.
- Demand analysis chart.
- Stockout risk report.
- Supplier comparison table.
- Interactive inventory simulation.
- Recommended supplier.
- Reorder quantity report.
- Downloadable procurement report.

## 10. Conclusion

SupplyChainIQ demonstrates how data analysis and rule-based decision-making can improve inventory monitoring and procurement planning.

It provides an interactive platform for identifying inventory risks and generating practical purchasing recommendations.