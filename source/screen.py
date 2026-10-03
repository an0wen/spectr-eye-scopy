"""RGB screen experiment restored from the legacy implementation."""
from pathlib import Path
from bokeh.events import DocumentReady
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, CustomJS, Slider, Div
from source.plots import wavelength_plot, rainbow_fill, response_plot, style_legend
from source.color_model import RGB_TO_LMS, cone_activation
from source.spectral_model import PIXEL_BASIS, pixel_spectrum, cone_sensitivities

ROOT = Path(__file__).resolve().parents[1]

def build_panels(headings, copy):
    sliders = [Slider(title=title, start=0, end=end, value=value, step=1,
                      sizing_mode='stretch_width', bar_color=color, name=name, margin=(0, 5))
               for title, end, value, color, name in [
                   (copy['red'], 255, 255, '#df735f', 'red'),
                   (copy['green'], 255, 160, '#7caa75', 'green'),
                   (copy['blue'], 255, 80, '#789fdb', 'blue'),
                   (copy['luminosity'], 100, 100, '#b99456', 'luminosity')]]
    values = [v * 100 for v in cone_activation(255, 160, 80)]
    source = ColumnDataSource(dict(cone=['S', 'M', 'L'], value=values,
                                   label=[f'{v:.1f}%' for v in values],
                                   color=['#789fdb', '#7caa75', '#df735f']), name='cone_responses')
    plot = response_plot(source, copy['response'])
    plot.yaxis[0].name = 'response_axis'
    spectrum_source = ColumnDataSource(pixel_spectrum(255, 160, 80), name='pixel_spectrum')
    spectrum = wavelength_plot(copy['emission'])
    spectrum.xaxis[0].name = 'spectrum_wavelength'
    spectrum.yaxis[0].name = 'emission_axis'
    spectrum_fill = rainbow_fill(spectrum, spectrum_source.data['wavelength'],
                                 spectrum_source.data['total'])
    for channel, color in [('red', '#df735f'), ('green', '#7caa75'), ('blue', '#789fdb')]:
        spectrum.line('wavelength', channel, source=spectrum_source, color=color, line_width=1.5,
                      legend_label=copy[channel + '_pixels'])
    spectrum.line('wavelength', 'total', source=spectrum_source, color='#33443d',
                  line_width=2, legend_label=copy['combined'])
    spectrum.legend[0].items[-1].name = 'combined_legend'
    sensitivity_source = ColumnDataSource(cone_sensitivities(), name='cone_sensitivities')
    spectrum_fill.name = 'spectrum_fill'
    sensitivity = wavelength_plot(copy['sensitivity'])
    sensitivity.xaxis[0].name = 'sensitivity_wavelength'
    sensitivity.yaxis[0].name = 'sensitivity_axis'
    for panel in (spectrum, sensitivity):
        panel.xaxis.axis_label = copy['wavelength']
    envelope = [max(values) for values in zip(*(sensitivity_source.data[c] for c in ('S', 'M', 'L')))]
    rainbow_fill(sensitivity, sensitivity_source.data['wavelength'], envelope)
    for cone, color in [('S', '#789fdb'), ('M', '#7caa75'), ('L', '#df735f')]:
        sensitivity.line('wavelength', cone, source=sensitivity_source, color=color,
                         line_width=2.5, legend_label=copy[cone + '_cone'])
    for panel in (spectrum, sensitivity):
        style_legend(panel)
    swatch = Div(width=180, height=230, sizing_mode='fixed')
    readout = Div(sizing_mode='stretch_width')
    callback = CustomJS(args=dict(red=sliders[0], green=sliders[1], blue=sliders[2],
                                  luminosity=sliders[3], source=source, matrix=RGB_TO_LMS,
                                  spectrum_source=spectrum_source, spectrum_fill=spectrum_fill,
                                  pixel_basis=PIXEL_BASIS, swatch=swatch, readout=readout),
                        code=(ROOT / 'source/screen_callback.js').read_text())
    for slider in sliders:
        slider.js_on_change('value', callback)
    controls = column(*sliders, sizing_mode='stretch_width', spacing=0)
    sliders[0].js_on_event(DocumentReady, callback)
    caption = lambda key: Div(text=copy[key], sizing_mode='stretch_width')
    return {
        'screen_1': column(headings[0], caption('spectrum_heading'), spectrum,
                           caption('spectrum_caption'), controls, sizing_mode='stretch_width'),
        'screen_2': column(headings[1], Div(text=(ROOT / 'source/eye.svg').read_text(),
                           sizing_mode='stretch_width'), caption('eye_caption'), swatch,
                           sizing_mode='stretch_width'),
        'screen_3': column(headings[2], caption('sensitivity_heading'), sensitivity,
                           caption('sensitivity_reference'), plot, readout,
                           sizing_mode='stretch_width'),
    }
