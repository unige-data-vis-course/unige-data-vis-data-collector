import logging

from unige_data_vis_data_collector.meteoswiss.forecast_loader import ForecastLoader

logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    loader = ForecastLoader()
    forecast_els = loader.load_all_forecast_elements(['rre150h0'])
    for e in forecast_els:
        print(e)
