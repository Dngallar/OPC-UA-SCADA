import numpy as np
from bokeh.models import ColumnDataSource, PreText
from bokeh.layouts import layout, column, row
from bokeh.plotting import curdoc, figure, show, gridplot
from bokeh.io import output_file, show
from bokeh.models.widgets import RadioButtonGroup, Slider
from bokeh.client import push_session
import PID #Controlador PID

''' Funcion que actualiza la opciones de interfaz segun modo de operacio '''
def update_layout(attr, old, new):
    curdoc().remove_root(layout_0)
    if mode_group.active == 0:
        layout_1.children[0].children[0] = layout_manual
    elif mode_group.active == 1:
        layout_1.children[0].children[0] = layout_auto

''' Funcion que actualiza los graficos'''
t_modo_manual = 0
def update_modo_manual(): # Funcion principal que se llama cada cierto tiempo para mostrar la informacion
    global t_modo_manual, sin, cos
    update = dict(time=[t_modo_manual], sin=[sin[t_modo_manual]], cos=[cos[t_modo_manual]])
    DataSource.stream(new_data=update, rollover=100) # Se ven los ultimos 100 datos
    SinText.text = 'Valor del Seno: {}'.format(round(sin[t_modo_manual],2))
    CosText.text = 'Valor del Coseno: {}'.format(round(cos[t_modo_manual],2))
    t_modo_manual += 1

#Botones de manual/automático
mode_group = RadioButtonGroup(labels=["Manual", "Automático"])
widgets_mode = [mode_group]

#Interfaz modo manual:
slider_v1 = Slider(start=-1, end=1, value=0, step=.01, title="Voltaje 1")
slider_v2 = Slider(start=-1, end=1, value=0, step=.01, title="Voltaje 2")
slider_gamma1 = Slider(start=0, end=1, value=0, step=.01, title="Razón de flujo 1")
slider_gamma2 = Slider(start=0, end=1, value=0, step=.01, title="Razón de flujo 2")

#Interfaz modo automático:
slider_ref_1 = Slider(start=0, end=50, value=20, step=.01, title="Referencia Estanque 1")
slider_kp_1 = Slider(start=0, end=100, value=0, step=.01, title="Ganancia proporcional tanque 1")
slider_kd_1 = Slider(start=0, end=100, value=0, step=.01, title="Ganancia derivativa tanque 1")
slider_ki_1 = Slider(start=0, end=100, value=0, step=.01, title="Ganancia integral tanque 1")
slider_nsamples_1 = Slider(start=0, end=20, value=2, step=1, title="Número de muestras para filtro derivativo tanque 1")
slider_ref_2 = Slider(start=0, end=50, value=20, step=.01, title="Referencia Estanque 2")
slider_kp_2 = Slider(start=0, end=100, value=0, step=.01, title="Ganancia proporcional tanque 2")
slider_kd_2 = Slider(start=0, end=100, value=0, step=.01, title="Ganancia derivativa tanque 2")
slider_ki_2 = Slider(start=0, end=100, value=0, step=.01, title="Ganancia integral tanque 2")
slider_nsamples_2 = Slider(start=0, end=20, value=2, step=1, title="Número de muestras para filtro derivativo tanque 2")

#Layout de opciones segun modo de operacion
widgets_manual = [slider_v1, slider_v2, slider_gamma1, slider_gamma2]
widgets_auto = [slider_ref_1, slider_kp_1, slider_kd_1, slider_ki_1, slider_nsamples_1,
                slider_ref_2, slider_kp_2, slider_kd_2, slider_ki_2, slider_nsamples_2]
u1 = -5
'''Detalle de los graficos'''
T = np.linspace(0,500,10001)
sin = u1*np.sin(T)
cos = np.cos(T)
# Se crea el DataSource
DataSource = ColumnDataSource(dict(time=[], sin=[], cos=[]))

# Figuras para cada grafico
fig_tanque1 = figure(title='Tanque 1', plot_width=600, plot_height=250)
fig_tanque2 = figure(title='Tanque 2', plot_width=600, plot_height=250)
fig_tanque3 = figure(title='Tanque 3', plot_width=600, plot_height=250)
fig_tanque4 = figure(title='Tanque 4', plot_width=600, plot_height=250)
fig_valvula1 = figure(title='Válvula 1', plot_width=600, plot_height=250)
fig_valvula2 = figure(title='Válvula 2', plot_width=600, plot_height=250)

#
fig_tanque1.line(x='time', y='sin', alpha=0.8, line_width=3, color='blue', source=DataSource, legend='Seno')
fig_tanque1.line(x='time', y='cos', alpha=0.8, line_width=3, color='red', source=DataSource, legend='Coseno')
fig_tanque1.xaxis.axis_label = 'Tiempo (S)'
fig_tanque1.yaxis.axis_label = 'Valores'

# Se crea un par de Widgets
estilo  = {'color':'white', 'font': '15px bold arial, sans-serif', 'background-color': 'green', 'text-align': 'center','border-radius': '7px'}
SinText = PreText(text='Valor del Seno: 0.00 ', width=300, style=estilo)
CosText = PreText(text='Valor del Coseno: 0.00', width=300, style=estilo)

'''Inicializacion de layouts'''
layout_manual = column(widgets_mode + widgets_manual)
layout_auto = column(widgets_mode + widgets_auto)
plot_grid = gridplot([[fig_tanque1,fig_tanque2],[fig_tanque3,fig_tanque4],[fig_valvula1,fig_valvula2]])
layout_1 = layout([[layout_manual,plot_grid]])
layout_0 = column(widgets_mode)
curdoc().add_root(layout_1)

# Metodo que detecta cambio en el modo de operacion
mode_group.on_change('active', update_layout)
# Metodo que llama cada Ts a la funcion que actualiza los graficos
Ts = 100 #ms
curdoc().add_periodic_callback(update_modo_manual, Ts)
curdoc().title = "Experiencia Control de Procesos"
