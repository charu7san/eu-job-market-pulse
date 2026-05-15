# 🌍 EU Job Market Pulse

An automated ETL pipeline and interactive dashboard visualizing the technology job market across Europe. Built with real-time data from the Adzuna API, this project tracks hiring trends, salary benchmarks, and skill demand in key EUR-zone markets.


## 🚀 Overview

This project serves as a comprehensive Data Engineering and Frontend showcase. It solves the challenge of tracking fragmented job markets by centralizing data from multiple countries into a single, premium dashboard.

### 🛠️ Tech Stack
- **Data Engineering:** Python (Requests, JSON, ETL logic)
- **Frontend:** React + Vite, Tailwind CSS v4
- **Visualization:** Recharts, Lucide Icons
- **Automation:** GitHub Actions (Cron Job)
- **Deployment:** GitHub Pages

## ⚙️ How It Works (The ETL Pipeline)

The system is designed to be fully self-sustaining with a **$0 budget** using GitHub Actions:

1.  **Extract:** A Python script wakes up every 24 hours (via GitHub Actions Cron). It fetches data for **7 countries** (AT, BE, DE, ES, FR, IT, NL) from the Adzuna API.
2.  **Transform:** The script calculates mean salaries, identifies top tech cities, aggregates skill demand for 15+ keywords (React, Python, Snowflake, etc.), and computes remote-work ratios.
3.  **Load:** The transformed data is saved as a single `market_data.json` file.
4.  **Sync:** GitHub Actions commits the new data back to the repository, which triggers an automatic update of the live dashboard.

## 📊 Key Features

- **Daily Automated Sync:** No manual updates required; data is refreshed every midnight.
- **Skill Demand Analysis:** Real-time tracking of what tools employers are actually looking for.
- **Salary Benchmarking:** Transparent average salary data across different European borders.
- **Remote Ratio Tracking:** Insights into which countries are leading the "Work from Anywhere" trend.
- **Premium UI:** A light, modern aesthetic designed for clarity and visual impact.

## 🛠️ Local Setup

### 1. Prerequisites
- Node.js (v18+)
- Python 3.9+
- Adzuna API Keys ([Get them here](https://developer.adzuna.com/))

### 2. Environment Configuration
Create a `.env` file in the root directory:
```env
ADZUNA_APP_ID=your_app_id
ADZUNA_APP_KEY=your_app_key
```

### 3. Running the Pipeline
```bash
# Install Python dependencies
pip install -r requirements.txt

# Run the ETL script
python script.py
```

### 4. Running the Dashboard
```bash
# Install JS dependencies
npm install

# Start the development server
npm run dev
```

## 📈 Portfolio Note

This project demonstrates proficiency in **Full-Stack Development** and **Data Engineering**, specifically:
- Building automated **ETL (Extract, Transform, Load)** pipelines.
- Managing **API Rate Limiting** and error handling in production scripts.
- Implementing secure **Secret Management** using GitHub Actions.
- Crafting high-performance, responsive UIs with modern CSS frameworks.

---
*Built with ❤️ for the European tech community.*
