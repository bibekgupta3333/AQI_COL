# AQI_COL - Air Quality Index Prediction for Kathmandu

A comprehensive air quality prediction system for Kathmandu, Nepal, that combines real-time air quality monitoring, historical data analysis, and machine learning models to predict and visualize air pollution levels.

## 🌟 Project Overview

This project develops a web-based air quality prediction system specifically focused on Kathmandu, Nepal. It integrates multiple data sources including real-time API feeds and historical air quality measurements to provide accurate AQI (Air Quality Index) predictions and visualizations.

### Key Features

- **Real-time Air Quality Monitoring**: Live AQI data from multiple APIs including AirNow and Air Quality API
- **Historical Data Analysis**: Comprehensive dataset spanning 2018-2023 with daily and hourly measurements
- **Machine Learning Predictions**: Multiple ML models for AQI forecasting
- **Web Interface**: Django-based web application with user authentication and data visualization
- **Data Processing Pipeline**: Automated scripts for data cleaning, aggregation, and feature engineering
- **Multi-parameter Analysis**: Tracks PM2.5, PM10, O3, NO2, CO, SO2, temperature, humidity, wind speed, and more

### Data Sources

- **US Embassy Kathmandu PM2.5 Data** (2021-2023)
- **Real-time APIs**: AirNow API and Air Quality Ninjas API
- **Weather Data**: Temperature, humidity, wind speed, visibility, and atmospheric pressure
- **Historical AQI Data**: Scraped and processed data from 2018-2021

## 🛠️ Technology Stack

- **Backend**: Django 4.0.5, Python 3.10+
- **Machine Learning**: Scikit-learn, XGBoost, Pandas, NumPy
- **Data Visualization**: Matplotlib, Seaborn
- **Web Scraping**: BeautifulSoup4
- **Frontend**: HTML/CSS/JavaScript (Django Templates)
- **Dependency Management**: Poetry

## 📊 Machine Learning Models

The project includes five different regression models for AQI prediction:

1. **Linear Regression** (`Regression_Linear.ipynb`)
2. **Decision Tree Regression** (`Regression_Decision_Tree.ipynb`)
3. **Random Forest Regression** (`Regression_Random_Forest.ipynb`)
4. **Ridge and Lasso Regression** (`Regression_Ridge_Lasso.ipynb`)
5. **XGBoost Regression** (`Regression_Xgboost.ipynb`)

Each model is trained on historical data with features including:

- Temperature (T, TM, Tm)
- Humidity (H)
- Wind Speed (V) and Wind Gust (VM)
- Visibility (VV)
- Sea Level Pressure (SLP)
- Previous day AQI values

## 🗂️ Project Structure

```
AQI_COL/
├── Air-Quality-Prediction/airprediction/
│   ├── airprediction/          # Django project settings
│   ├── main/                   # Main Django app
│   │   ├── templates/          # HTML templates
│   │   ├── static/            # CSS, JS, images
│   │   ├── models.py          # Database models
│   │   └── views.py           # Web application logic
│   ├── Data/
│   │   ├── AQI/               # Historical AQI CSV files (2018-2021)
│   │   ├── NewData/           # Recent data and processing scripts
│   │   ├── Html_Data/         # Scraped HTML data
│   │   └── Real-Data/         # Processed real data
│   ├── Machine Learning Models/ # Jupyter notebooks for ML models
│   ├── manage.py              # Django management script
│   └── requirements.txt       # Project dependencies
├── pyproject.toml             # Poetry configuration
└── README.md                  # This file
```

## 🚀 Setup and Installation

### Prerequisites

- Python 3.10 or higher
- Poetry for dependency management
- Git

### Installation Steps

1. **Clone the repository**:

   ```bash
   git clone https://github.com/yourusername/AQI_COL.git
   cd AQI_COL
   ```

2. **Install dependencies using Poetry**:

   ```bash
   poetry install
   ```

3. **Activate the virtual environment**:

   ```bash
   poetry shell
   ```

4. **Navigate to the Django project**:

   ```bash
   cd Air-Quality-Prediction/airprediction
   ```

5. **Set up the database**:

   ```bash
   python manage.py migrate
   ```

6. **Create a superuser (optional)**:

   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**:

   ```bash
   python manage.py runserver
   ```

8. **Access the application**:
   Open your web browser and navigate to `http://127.0.0.1:8000/`

## 📈 Usage

### Web Application Features

- **Homepage**: Real-time AQI display with color-coded health categories
- **Prediction**: ML-powered AQI forecasting based on weather parameters
- **Historical Data**: Browse and analyze past air quality data (2018-2023)
- **User Authentication**: Sign up/login functionality for personalized features
- **Data Download**: Export processed datasets for research purposes

### Running Machine Learning Models

1. **Start Jupyter Notebook**:

   ```bash
   cd "Machine Learning Models"
   jupyter notebook
   ```

2. **Open desired notebook**:

   - `Regression_Linear.ipynb` - Linear regression analysis
   - `Regression_Random_Forest.ipynb` - Random Forest implementation
   - `Regression_Xgboost.ipynb` - XGBoost model training
   - And others...

3. **Run cells sequentially** to train models and evaluate performance

### Data Processing

The project includes several data processing scripts in the `Data/NewData/` directory:

- `dailyScriptWithCombinedData.py` - Daily data aggregation and cleaning
- `hourlyScriptWithCombinedData.py` - Hourly data processing
- `dailyWithhumidity.py` - Humidity calculation and adjustment
- `proc.py` - General data preprocessing utilities

## 🔧 Configuration

### API Keys

The application uses external APIs for real-time data. Update the following in `main/views.py`:

- **AirNow API**: Replace `API_KEY` with your AirNow API key
- **Air Quality Ninjas**: Replace `X-Api-Key` with your API Ninjas key

### Database

The project uses SQLite by default. For production, consider configuring PostgreSQL or MySQL in `settings.py`.

## 📊 Data Processing Pipeline

### Daily Data Processing

1. **Data Collection**: Aggregate hourly measurements into daily averages
2. **Missing Value Handling**: Use previous day data or historical averages
3. **Feature Engineering**: Calculate relative humidity, adjust wind speeds
4. **Quality Control**: Validate data ranges and remove outliers
5. **Output Generation**: Create clean CSV files for model training

### Real-time Data Integration

- Fetches current AQI from multiple APIs
- Compares and validates data sources
- Provides real-time health recommendations
- Updates database with latest measurements

## 🎯 Health Categories

The system provides AQI-based health recommendations:

- **Good (0-50)**: Air quality is satisfactory
- **Moderate (51-100)**: Acceptable, but sensitive individuals may experience minor issues
- **Unhealthy for Sensitive Groups (101-150)**: Sensitive individuals may experience health effects
- **Unhealthy (151-200)**: Everyone may experience health effects
- **Very Unhealthy (201-300)**: Health alert for everyone
- **Hazardous (301+)**: Emergency conditions

## 🤝 Contributing

We welcome contributions to improve the air quality prediction system!

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and add tests
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

### Areas for Contribution

- Additional machine learning models
- Improved data visualization
- Mobile app development
- API endpoints for external integration
- Documentation improvements
- Bug fixes and performance optimizations

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Contact

- **Author**: Bibek Gupta
- **Email**: bibekgupta3333@gmail.com
- **GitHub**: [@bibekg](https://github.com/bibekg)

## 🙏 Acknowledgments

- US Embassy Kathmandu for PM2.5 data
- AirNow API for real-time air quality data
- Air Quality API Ninjas for additional data sources
- Django and Scikit-learn communities for excellent frameworks

## 📚 Research and References

This project contributes to air quality research in South Asian urban environments, particularly focusing on:

- Seasonal air pollution patterns in Kathmandu valley
- Machine learning applications in environmental monitoring
- Real-time air quality prediction systems
- Public health impact assessment tools

---

**Note**: This project is for educational and research purposes. For critical health decisions, please consult official air quality monitoring agencies.
