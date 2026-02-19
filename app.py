import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# 1. Define the prioridad_colors dictionary
prioridad_colors = {
    'ALTA': 'red',
    'MEDIA': 'orange',
    'BAJA': 'green'
}

# 2. Load the unified_gantt_data.csv into a pandas DataFrame
csv_file_path = 'unified_gantt_data.csv'
try:
    df = pd.read_csv(csv_file_path)
    # Ensure datetime columns are correctly parsed
    df['start_time'] = pd.to_datetime(df['start_time'])
    df['end_time'] = pd.to_datetime(df['end_time'])
    print("Unified DataFrame loaded successfully.")
except FileNotFoundError:
    print(f"Error: The file '{csv_file_path}' was not found. Please ensure it's in the same directory as app.py.")
    # Exit or handle error appropriately if file is crucial
    df = pd.DataFrame() # Create an empty DataFrame to avoid errors later


# 3. Initialize the Dash application
app = dash.Dash(__name__)

# Get unique equipment names for the dropdown
unique_equipos = df['EQUIPO'].dropna().unique()

# 4. Define the application layout
app.layout = html.Div([
    html.H1("Gantt Chart de Mantenimiento por Equipo", style={'textAlign': 'center'}),

    html.Div([
        html.Label("Seleccionar Equipo:", style={'marginRight': '10px'}),
        dcc.Dropdown(
            id='equipment-dropdown',
            options=[
                {'label': equipo, 'value': equipo}
                for equipo in unique_equipos
            ],
            value=unique_equipos[0] if len(unique_equipos) > 0 else None, # Default value
            placeholder="Seleccione un equipo",
            style={'width': '50%', 'display': 'inline-block'}
        ),
    ], style={'textAlign': 'center', 'marginBottom': '20px'}),

    dcc.Graph(id='gantt-chart')
])

# 5. Implement a Dash callback function
@app.callback(
    Output('gantt-chart', 'figure'),
    Input('equipment-dropdown', 'value')
)
def update_gantt_chart(selected_equipment):
    if not selected_equipment:
        return px.timeline(pd.DataFrame(columns=['Start', 'Finish', 'Resource', 'Task', 'Prioridad'])) # Return empty plot

    filtered_df = df[df['EQUIPO'] == selected_equipment].copy()

    # Prepare the filtered_df for Plotly
    filtered_df = filtered_df.rename(columns={
        'ACTIVIDAD A EJECUTAR': 'Task',
        'start_time': 'Start',
        'end_time': 'Finish',
        'PERSONA ASIGNADA A LA ACTIVIDAD': 'Resource'
    })

    # Sort activities by resource and then by start_time for better visualization
    filtered_df = filtered_df.sort_values(by=['Resource', 'Start']).reset_index(drop=True)

    # Create a Plotly timeline (Gantt chart)
    fig = px.timeline(filtered_df,
                      x_start="Start",
                      x_end="Finish",
                      y="Resource",
                      color="Prioridad",
                      color_discrete_map=prioridad_colors,
                      text="Task",
                      title=f"Gantt Chart para {selected_equipment} (por Persona)")

    # Customize the fig properties
    fig.update_yaxes(categoryorder="total ascending") # Order resources by their appearance or total tasks
    fig.update_traces(textposition='inside') # Position text inside the bars

    # Customize hover information to show detailed activity info
    fig.update_traces(hovertemplate='<b>Task:</b> %{text}<br><b>Person:</b> %{y}<br><b>Start:</b> %{x|%Y-%m-%d %H:%M}<br><b>Finish:</b> %{customdata[0]|%Y-%m-%d %H:%M}<br><b>Priority:</b> %{customdata[1]}<extra></extra>',
                      customdata=filtered_df[['Finish', 'Prioridad']])
    
    fig.update_layout(
        hovermode="closest",
        xaxis_title="Tiempo",
        yaxis_title="Persona Asignada",
        legend_title="Prioridad",
        margin=dict(l=0, r=0, t=50, b=0) # Adjust margins
    )

    return fig

# 6. Add the if __name__ == '__main__': block to run the Dash application
if __name__ == '__main__':
    app.run(debug=True, jupyter_mode='inline')
