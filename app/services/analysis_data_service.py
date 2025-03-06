from autogen_agentchat.ui import Console
import asyncio

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat, SelectorGroupChat
from autogen_core.components.tools import FunctionTool
from autogen_ext.models import OpenAIChatCompletionClient
from autogen_agentchat.base import TaskResult

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import random
import datetime
import os 
import base64
from io import BytesIO
from PIL import Image

from app.services.storage.storage_service import load_document_blod
#from storage.storage_service import load_document_blod

class AnalysisService:

    general_model_client = OpenAIChatCompletionClient(model="gpt-4o-mini", 
                                                      api_key="sk-u4V8dGD5v1fSLgtYP-j7Jwz6wdBRu7XHG52EpWoNFxT3BlbkFJ0gkbtuVQpj5b_Pkh4pT80La_aofoLYCZvvvZQGWAEA")

    image_name = "plot_hours_worked.png"

    def generate_hours_worked(self, description: str) -> str:

        # Simulación de datos
        dias = pd.date_range(start="2025-02-06", periods=8, freq='D')  # 10 días de datos
        vehiculos = [f"Vehicle {i+1}" for i in range(7)]  # 7 vehículos

        # Generar datos de horas trabajadas de forma aleatoria
        np.random.seed(42)
        data = {vehiculo: np.random.randint(0, 16, size=len(dias)) for vehiculo in vehiculos}

        # Crear DataFrame
        df = pd.DataFrame(data, index=dias)

        # Configuración del gráfico
        sns.set_theme(style="darkgrid")
        plt.figure(figsize=(10, 6))

        # Graficar cada vehículo con una línea diferente
        for vehiculo in vehiculos:
            plt.plot(df.index, df[vehiculo], marker='o', label=vehiculo, linewidth=2.5)

        # Personalización del gráfico
        plt.title("Hours Worked by Vehicle in the Last Days", fontsize=14, fontweight='bold')
        plt.xlabel("Date", fontsize=12)
        plt.ylabel("Hours Worked", fontsize=12)
        plt.xticks(rotation=45)
        plt.legend(title="Vehicles", bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True, linestyle="--", alpha=0.7)

        self.image_name = "plot_hours_worked_" + str(random.randint(1, 10000)) + ".png"

        """
        # Save plot to file
        os.makedirs("graphic", exist_ok=True)
        plot_file_path = f"graphic/{self.image_name}"
        plt.savefig(plot_file_path)
        print(f"Plot saved as {plot_file_path}")
        """
        # Guardar el gráfico en un objeto BytesIO en lugar de escribirlo en disco
        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)

        #store blod
        load_document_blod(self.image_name, buf.getvalue())
        #https://storeblodassistent.blob.core.windows.net/documents/plot_hours_worked_6005.jpg
        ## Mostrar gráfico
        #plt.tight_layout()
        #plt.show()

        # Cerrar el objeto BytesIO y la figura de matplotlib
        buf.close()
        plt.close()

        #for col in df.columns:
        #    print(f"Vehicle {col} - Total Hours Worked: {df[col].sum()}")

        # Crear un nuevo DataFrame con el nombre de cada columna y el total de horas de cada columna
        vehicle_totals = pd.DataFrame({
            'Vehicle': df.columns,
            'Hours Worked': [df[col].sum() if df[col].dtype in ['int32', 'int64', 'float64'] else None for col in df.columns]
        })

        # Calcular el total de horas trabajadas por cada vehículo
        #total_hours = df.groupby('vehicle')['hours_worked'].sum().reset_index()

        # Convertir la tabla a formato Markdown
        markdown_table = vehicle_totals.to_markdown(index=False)
        #print(markdown_table)

        return markdown_table
      
    def generate_alerts(self, description: str) -> str:
        # Configure professional style
        sns.set_theme(style="darkgrid")

        # Sample data: Alert levels and corrective action status
        alerts_data = {
            "Alert Level": ["Critical 🔴", "Medium 🟠", "Low 🟢"],
            "Total Alerts": [39, 30, 32],       # Total alerts per level
            "🚧 Action Pending": [1, 5, 15],            # Alerts with no action taken
            "✅ Action Scheduled": [38, 25, 17]           # Alerts with scheduled actions
        }

        # Convert to DataFrame
        df_alerts = pd.DataFrame(alerts_data)

        # Define colors
        #colores = ["red", "orange", "green"]
        action_colors = ["orange", "green"]  # Pending (Red) and Scheduled (Green)

        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))

        # Stacked bar chart
        bars1 = ax.bar(df_alerts["Alert Level"], df_alerts["🚧 Action Pending"], color=action_colors[0], label="🚧 Action Pending")
        bars2 = ax.bar(df_alerts["Alert Level"], df_alerts["✅ Action Scheduled"], 
                    bottom=df_alerts["🚧 Action Pending"], color=action_colors[1], label="✅ Action Scheduled")

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
        ax.set_ylabel("Number of Alerts")
        ax.set_xlabel("Actions")
        ax.legend()

        # Ajustar diseño
        plt.tight_layout()

        self.image_name = "plot_alerts_" + str(random.randint(1, 10000)) + ".png"

        # Guardar el gráfico en un objeto BytesIO en lugar de escribirlo en disco
        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)

        #store blod
        load_document_blod(self.image_name, buf.getvalue())

        # Convertir la tabla a formato Markdown
        markdown_table_alerts = df_alerts.to_markdown(index=False)
        print(markdown_table_alerts)

        return markdown_table_alerts

    def generate_sensor_historical_data(self, num_days=12):

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

    def generate_sensor_plot(self):
        # Generate and display the data
        historical_df = self.generate_sensor_historical_data()
        #print(historical_df)

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
        #plt.show()

        self.image_name = "plot_sensor_" + str(random.randint(1, 10000)) + ".png"

        # Guardar el gráfico en un objeto BytesIO en lugar de escribirlo en disco
        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)

        #store blod
        load_document_blod(self.image_name, buf.getvalue())

        # Opcional: Guardar en un archivo CSV
        # df_historico.to_csv('datos_historicos_vehiculo.csv', index=False)

        # Convertir la tabla a formato Markdown
        markdown_sensor = historical_df.to_markdown(index=False)
        print(markdown_sensor)

        return markdown_sensor


    def generate_explanation(self):
        
        return """When the temperature continues to rise, 
                            base on the engine temperature plot.
                            it could cause overheating
                            This indicates a potential failure in the cooling system:
                                The system outlines the risks:
                                - If the temperature continues to rise, it could cause overheating
                                - Overheating may result in severe engine damage
                                - This could lead to prolonged and costly downtime
                                Recommended Action:
                                - To prevent major issues, Autosense recommends the following immediate actions:
                                    - Inspect the cooling system to detect possible leaks or radiator failures.
                                    - Replace the coolant to ensure stable temperature and optimal engine performance. 
               """
    

    async def execute_command(self, status: str, command: str):
        
        print("Starting the service")
        self.image_name = ""

        graphic_hours_worked = FunctionTool(
            self.generate_hours_worked, 
            name="graphic_hours_worked",
            description="Generate a plot with the hours worked by vehicle in the last days and return a summary of the total hours worked by each vehicle",
        )
        plot_worked_hours_agent = AssistantAgent(
            name         = "Plot_Hours_Worked_Agent",
            model_client = self.general_model_client,
            tools        = [graphic_hours_worked],
            description  = "Generate a plot with the hours worked by vehicle in the last days",
            system_message = """You are a helpful AI assistant. Solve tasks using your tools. 
                                you should execute the tool Plot_Hours_Worked_Agent to Generate a plot with the hours worked by vehicle in the last days
                                when the user asks for the status of the vehicle fleet."
                            """,
        )

        graphic_alerts = FunctionTool(
            self.generate_alerts, 
            name="graphic_alerts",
            description="Generate a chart with alerts and actions by alert type over the past few days and return a summary of the total alerts and actions",
        )
        plot_alerts_agent = AssistantAgent(
            name         = "Plot_Alerts_Agent",
            model_client = self.general_model_client,
            tools        = [graphic_alerts],
            description  = "Generate a chart with alerts and actions by alert type over the past few days and return a summary of the total alerts and actions",
            system_message = """You are a helpful AI assistant. Solve tasks using your tools. 
                                you should execute the tool Plot_Alerts_Agent to Generate a plot with alerts and actions by alert type over the past few days and return a summary of the total alerts and actions
                                when the user asks for the alerts of the vehicle fleet."
                            """,
        )

        graphic_sensor = FunctionTool(
            self.generate_sensor_plot, 
            name="graphic_sensor",
            description="""Generate a plot of engine temperature, which shows the engine temperature has been progressively increasing over the past week. 
                           """,
        )

        generate_explanation = FunctionTool(
            self.generate_explanation, 
            name="generate_explanation",
            description="""generate a explanation what is the action recomended when the temperature continues to rise, 
                            base on the engine temperature plot
                           """
        )

        system_message = ""
        tools = []
        match status:
            case "status":  
                system_message = """You are a helpful AI assistant. Generate a plot and Solve tasks using your tools.

                                    When the user asks for the status of the vehicle fleet,
                                    You should execute the tool graphic_hours_worked to Generate a plot with the hours worked by vehicle in the last days.
                                """;
                tools = [graphic_hours_worked] 
            case "alerts":  
                system_message = """You are a helpful AI assistant. Generate a plot and Solve tasks using your tools.

                                    When the user asks for the alerts of the vehicle fleet,
                                    You should execute the tool graphic_alerts to Generate a plot with alerts and actions by alert type over the past few days and return a summary of the total alerts and actions.
                                """;
                tools = [graphic_alerts] 
            case "critical":  
                system_message = """You are a helpful AI assistant. Generate a plot and Solve tasks using your tools.

                                    When the user asks for the root cause of critical alerts 
                                    You should execute the tool graphic_sensor to Generate a plot with engine temperature over the past few days and return a summary of engine temperature
                                """;
                tools = [graphic_sensor] 
            case "explain":  
                system_message = """You are a helpful AI assistant. Generate a plot and Solve tasks using your tools.

                                    When the user asks what actions should be taken to correct the critical alert 
                                    You should execute the tool generate_explanation to Generate an explanation to correct the critical alert
                                """;
            case "schedule":  
                system_message = """You are a helpful AI assistant. Generate a plot and Solve tasks using your tools.

                                    When the user asks you to schedule a maintenance appointment, 
                                    please return an appointment scheduled for next Monday at 9:00 AM at the shop to check the coolant system.
                                """;
                tools = [generate_explanation] 
            case _:
                system_message = """You are a helpful AI assistant. Generate a plot and Solve tasks using your tools.
                                    
                                    When the user asks for the status of the vehicle fleet,
                                    You should execute the tool graphic_hours_worked to Generate a plot with the hours worked by vehicle in the last days.

                                    When the user asks for the alerts of the vehicle fleet,
                                    You should execute the tool graphic_alerts to Generate a plot with alerts and actions by alert type over the past few days and return a summary of the total alerts and actions.

                                    When the user asks for the root cause of critical alerts 
                                    You should execute the tool graphic_sensor to Generate a plot with engine temperature over the past few days and return a summary of engine temperature

                                    When the user asks what actions should be taken to correct the critical alert 
                                    You should execute the tool generate_explanation to Generate an explanation to correct the critical alert

                                    When the user asks you to schedule a maintenance appointment, 
                                    please return an appointment scheduled for next Monday at 9:00 AM at the shop to check the coolant system.
                                """;
        print(system_message)


        plot_agent = AssistantAgent(
            name         = "Plot_Agent",
            model_client = self.general_model_client,
            tools        = [graphic_hours_worked, graphic_alerts, graphic_sensor, generate_explanation],
            description  = "You are a helpful AI assistant. Generate a plot and Solve tasks using your tools.",
            system_message = system_message,
        )


        report_agent = AssistantAgent(
            name = "Report_Agent",
            model_client   = self.general_model_client,
            description    = "Summarize the data provided by the other agents",
            system_message = """You are a helpful assistant who can generate a short summary of data provided by the other agents based on a given task,
                                only describe more relevant data in maximoun two sentences. 
                                When you are done with generating the report, reply with TERMINATE.
                              """,
        )
        #system_message = "You are a helpful assistant that can generate a comprehensive report on a given topic based on search and stock analysis.",
        #posible reponse


        termination = TextMentionTermination("TERMINATE")


        # Run the team and stream messages to the console
        agent_team = RoundRobinGroupChat([plot_agent, report_agent], 
                                         termination_condition=termination,
                                         max_turns=2)


        result = agent_team.run_stream(task=""" """ + command)
        #await Console(result)

        summary          = ""
        async for message in result:
            if isinstance(message, TaskResult):
                for message in message.messages:
                    #print('-' * 30)
                    #print("content: " + str(message.content))
                    #print("source: " + message.source)
                    #if message.source == "db_agent" or "content=\"[" in str(message.content):
                    #    database_summary = str(message.content)
                    if (message.source == "Report_Agent" or message.source == "Report_Agent" or "TERMINATE" in message.content) and message != "TERMINATE":
                        summary = str(message.content)
                        summary = summary.replace("TERMINATE", "")

        print(f"summary: {summary} ")
        print(f"image_name: {self.image_name} ")
        return (summary, self.image_name)


if __name__ == "__main__":
    """Could you show the vehicles status?
        Could you show the alerts report?
        Could you explain the root cause of the critical alert?
        Could you explain What actions I should take?
        Could you schedule a maintenance appointment?"""
    service = AnalysisService()
    #service.generate_hours_worked("Generate a plot about hours worked for every vehicle in the last days")
    #service.generate_alerts("Could you generate a plot about alerts in the last days?")
    #print(asyncio.run(service.execute_command("init", "Could you give me the status of the vehicle fleet?")))
    #print(asyncio.run(service.execute_command("init", "Could you generate a plot about alerts in the last days?")))
    print(asyncio.run(service.execute_command("init", "Could you explain me the root cause of 2 critial alerts?")))
