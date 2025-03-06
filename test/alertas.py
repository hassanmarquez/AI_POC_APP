import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os

# Configuración de estilo profesional
sns.set_theme(style="darkgrid")

# Datos de alertas y estado de acciones correctivas
alertas_data = {
    "Nivel de Alerta": ["Crítica 🔴", "Media 🟠", "Leve 🟢"],
    "Cantidad": [35, 50, 40]
}
acciones_data = {
    "Estado de Acción": ["🚧 Pendiente", "📅 Programada", "✅ Resuelta"],
    "Cantidad": [30, 45, 50]
}

# Calcular totales
total_alertas = sum(alertas_data["Cantidad"])
total_acciones = sum(acciones_data["Cantidad"])

# Convertir a DataFrame
df_alertas = pd.DataFrame(alertas_data)
df_acciones = pd.DataFrame(acciones_data)

# Crear figura y ejes
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Gráfico de Alertas por nivel de criticidad
sns.barplot(x="Nivel de Alerta", y="Cantidad", data=df_alertas, palette=["red", "orange", "green"], ax=axes[0])
axes[0].set_title(f"📊 Niveles de Alertas (Total: {total_alertas})", fontsize=14, fontweight="bold")
axes[0].set_xlabel("")
axes[0].set_ylabel("Cantidad")
axes[0].bar_label(axes[0].containers[0], fmt='%d', fontsize=12, label_type="edge")

# Gráfico de Estado de Acciones Correctivas (Acción Pendiente en rojo)
sns.barplot(x="Estado de Acción", y="Cantidad", data=df_acciones, palette=["red", "blue", "green"], ax=axes[1])
axes[1].set_title(f"🔧 Estado de Acciones Correctivas (Total: {total_acciones})", fontsize=14, fontweight="bold")
axes[1].set_xlabel("")
axes[1].set_ylabel("Cantidad")
axes[1].bar_label(axes[1].containers[0], fmt='%d', fontsize=12, label_type="edge")

# Ajustar diseño
plt.tight_layout()

# Save plot to file
os.makedirs("graphic", exist_ok=True)
plot_file_path = f"graphic/alertas_acciones2.png"
plt.savefig(plot_file_path)
print(f"Plot saved as {plot_file_path}")

# Mostrar gráfico
#plt.show()