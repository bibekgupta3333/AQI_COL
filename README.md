## Setup

### Prerequisites

- Python 3.12 or higher
- Poetry for dependency management

### Installation

1. Clone the repository:

   ```sh
   git clone https://github.com/yourusername/AQI_COL.git
   cd AQI_COL
   ```

2. Install dependencies using Poetry:

   ```sh
   poetry install
   ```

3. Activate the virtual environment:

   ```sh
   poetry shell
   ```

### Running the Project

1. Navigate to the project directory:

   ```sh
   cd Air-Quality-Prediction/airprediction
   ```

2. Run the Django development server:

   ```sh
   python manage.py runserver
   ```

3. Open your web browser and go to `http://127.0.0.1:8000/` to view the application.

### Running the Machine Learning Models

The machine learning models are provided as Jupyter notebooks in the `Machine Learning Models` directory. To run the notebooks:

1. Start Jupyter Notebook:

   ```sh
   jupyter notebook
   ```

2. Open the desired notebook (e.g., `Regression_Linear.ipynb`) and run the cells to train and evaluate the model and link model to django views for prediction.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License.
