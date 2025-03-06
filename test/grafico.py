import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

# Simulación de datos
dias = pd.date_range(start="2024-01-01", periods=10, freq='D')  # 10 días de datos
vehiculos = [f"Vehículo {i+1}" for i in range(7)]  # 7 vehículos

# Generar datos de horas trabajadas de forma aleatoria
np.random.seed(42)
data = {vehiculo: np.random.randint(4, 12, size=len(dias)) for vehiculo in vehiculos}

# Crear DataFrame
df = pd.DataFrame(data, index=dias)

# Configuración del gráfico
sns.set_theme(style="darkgrid")
plt.figure(figsize=(10, 6))

# Graficar cada vehículo con una línea diferente
for vehiculo in vehiculos:
    plt.plot(df.index, df[vehiculo], marker='o', label=vehiculo, linewidth=2.5)

# Personalización del gráfico
plt.title("Horas Trabajadas por Vehículo en los Últimos Días", fontsize=14, fontweight='bold')
plt.xlabel("Fecha", fontsize=12)
plt.ylabel("Horas Trabajadas", fontsize=12)
plt.xticks(rotation=45)
plt.legend(title="Vehículos", bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(True, linestyle="--", alpha=0.7)

# Mostrar gráfico
plt.tight_layout()
plt.show()