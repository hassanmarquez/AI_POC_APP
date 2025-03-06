import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import random
from io import BytesIO


# Configure professional style
sns.set_theme(style="darkgrid")

# Sample data: Alert levels and corrective action status
alerts_data = {
    "Alert Level": ["Critical 🔴", "Medium 🟠", "Low 🟢"],
    "Total Alerts": [40, 30, 32],       # Total alerts per level
    "🚧 Pending": [2, 5, 15],            # Alerts with no action taken
    "✅ Scheduled": [38, 25, 17]           # Alerts with scheduled actions
}

# Convert to DataFrame
df_alerts = pd.DataFrame(alerts_data)

# Define colors
#colores = ["red", "orange", "green"]
action_colors = ["orange", "green"]  # Pending (Red) and Scheduled (Green)

# Create figure
fig, ax = plt.subplots(figsize=(10, 6))

# Stacked bar chart
bars1 = ax.bar(df_alerts["Alert Level"], df_alerts["🚧 Pending"], color=action_colors[0], label="🚧 Pending")
bars2 = ax.bar(df_alerts["Alert Level"], df_alerts["✅ Scheduled"], 
            bottom=df_alerts["🚧 Pending"], color=action_colors[1], label="✅ Scheduled")

# Add data labels for each section
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        if height > 0:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_y() + height/2, 
                    f'{int(height)}', ha='center', va='center', fontsize=12, color='white', fontweight="bold")

# Add total labels above bars
for i, total in enumerate(df_alerts["Total Alerts"]):
    ax.text(i, total + 2, f'Total: {total}', ha='center', fontsize=12, fontweight="bold")

# Titles and labels
ax.set_title("📊 Alerts by Severity and Action Status", fontsize=14, fontweight="bold")
ax.set_xlabel("")
ax.set_ylabel("Number of Alerts")
ax.legend()

# Ajustar diseño
plt.tight_layout()

image_name = "plot_alerts_" + str(random.randint(1, 10000)) + ".png"

# Guardar el gráfico en un objeto BytesIO en lugar de escribirlo en disco
plt.savefig(image_name, format="png")


# Convertir la tabla a formato Markdown
markdown_table_alerts = df_alerts.to_markdown()
print(markdown_table_alerts)

# Adjust layout and show chart
#plt.tight_layout()
#plt.show()