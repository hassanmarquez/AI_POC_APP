import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
import seaborn as sns

def generate_sensor_historical_data(num_days=12):

    dates = [datetime.date.today() - pd.DateOffset(days=i) for i in range(num_days)]
    dates.reverse()  # Order the dates chronologically

    # Initialize lists to store the data
    engine_temperature = []
    oil_pressure = []
    o2_sensor = []
    tire_pressure = []

    # Generate data with trends
    for i in range(num_days):
        # Temperature: Gradually increases with some noise
        temp = 80 + (i * 2) + np.random.normal(0, 1)
        engine_temperature.append(temp)

        # Oil Pressure: Gradually decreases with some noise
        pressure = 45 - (i * 0.5) + np.random.normal(0, 0.5)
        oil_pressure.append(pressure)

        # O2 Sensor: Gradually increases (simulating inefficiency)
        o2 = 0.8 + (i * 0.1) + np.random.normal(0, 0.05)
        o2_sensor.append(o2)

        # Tire Pressure: Random variation around a base value
        tires = 32 + np.random.normal(0, 1)
        tire_pressure.append(tires)


    # Create the DataFrame
    data = {
        'Date': dates,
        'Engine_Temperature_°C': engine_temperature,
        'Oil_Pressure_psi': oil_pressure,
        'O2_Sensor_%': o2_sensor,
        'Tire_Pressure_psi': tire_pressure
    }

    df = pd.DataFrame(data)
    return df


if __name__ == "__main__":
    # Generate and display the data
    historical_df = generate_sensor_historical_data()
    print(historical_df)

    # Create graphs with Matplotlib and Seaborn
    plt.figure(figsize=(12, 6))  # Adjust the figure size

    # Subplot 1: Engine Temperature
    #plt.subplot(2, 1, 1)  # 2 rows, 1 column, first graph
    sns.lineplot(x='Date', y='Engine_Temperature_°C', data=historical_df)
    plt.title('Engine Temperature over Time')
    plt.xlabel('Date')
    plt.ylabel('Temperature (°C)')

    """
    # Subplot 2: Oil Pressure
    plt.subplot(2, 1, 2)  # 2 rows, 1 column, second graph
    sns.lineplot(x='Date', y='Oil_Pressure_psi', data=historical_df)
    plt.title('Oil Pressure over Time')
    plt.xlabel('Date')
    plt.ylabel('Pressure (psi)')
    """

    plt.tight_layout()  # Adjust spacing between subplots
    plt.show()

    # Opcional: Guardar en un archivo CSV
    # df_historico.to_csv('datos_historicos_vehiculo.csv', index=False)

    # Opcional: Guardar en un archivo CSV
    # df_historico.to_csv('datos_historicos_vehiculo.csv', index=False)
