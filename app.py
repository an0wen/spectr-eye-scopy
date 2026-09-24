"""Build a standalone interactive page: python app.py."""
from pathlib import Path
from bokeh.embed import components
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, CustomJS, Slider, LabelSet, Range1d
from bokeh.plotting import figure
from bokeh.resources import INLINE
from jinja2 import Template
from color_model import RGB_TO_LMS, cone_activation
from spectral_model import PIXEL_BASIS, pixel_spectrum, cone_sensitivities

ROOT = Path(__file__).resolve().parent


def wavelength_plot(y_label):
    plot = figure(x_range=(390, 780), y_range=(0, 1.12), height=175,
                  sizing_mode='stretch_width', toolbar_location=None, tools='',
                  background_fill_color='#fbfaf6', border_fill_color='#fbfaf6',
                  outline_line_color=None, min_border_left=48, min_border_right=12)
    plot.xaxis.axis_label = 'Wavelength (nm)'
    plot.yaxis.axis_label = y_label
    plot.xaxis.ticker = [400, 500, 600, 700]
    plot.yaxis.ticker = [0, .5, 1]
    plot.grid.grid_line_color = '#e6e7df'
    plot.axis.axis_line_color = None
    plot.axis.major_tick_line_color = None
    plot.axis.minor_tick_line_color = None
    plot.axis.major_label_text_color = '#53635b'
    plot.axis.axis_label_text_font_size = '11px'
    return plot


def rainbow_fill(plot, wavelengths, values):
    """One trapezoid per wavelength interval, colored by wavelength.

    Colors are illustrative display colors, not calibrated monochromatic sRGB.
    """
    stops = [(390, (112, 55, 210)), (450, (65, 80, 240)),
             (490, (40, 195, 225)), (530, (65, 190, 80)),
             (575, (240, 215, 45)), (610, (245, 140, 40)),
             (650, (220, 65, 55)), (780, (160, 35, 65))]
    colors = []
    for wavelength in wavelengths[:-1]:
        for (left, a), (right, b) in zip(stops, stops[1:]):
            if left <= wavelength <= right:
                t = (wavelength - left) / (right - left)
                rgb = tuple(round(x + t * (y - x)) for x, y in zip(a, b))
                colors.append('#%02x%02x%02x' % rgb)
                break
    fill = ColumnDataSource(dict(
        xs=[[a, a, b, b] for a, b in zip(wavelengths, wavelengths[1:])],
        ys=[[0, a, b, 0] for a, b in zip(values, values[1:])],
        color=colors))
    plot.patches('xs', 'ys', source=fill, fill_color='color',
                 fill_alpha=.45, line_color=None)
    return fill


def build(output=None):
    sliders = [Slider(title=title, start=0, end=end, value=value, step=1,
                      sizing_mode='stretch_width', bar_color=color, name=name, margin=(0, 5))
               for title, end, value, color, name in [
                   ('Red', 255, 255, '#df735f', 'red'),
                   ('Green', 255, 160, '#7caa75', 'green'),
                   ('Blue', 255, 80, '#789fdb', 'blue'),
                   ('Luminosity (%)', 100, 100, '#b99456', 'luminosity')]]
    values = [v * 100 for v in cone_activation(255, 160, 80)]
    source = ColumnDataSource(dict(cone=['S', 'M', 'L'], value=values,
                                   label=[f'{v:.1f}%' for v in values],
                                   color=['#789fdb', '#7caa75', '#df735f']), name='cone_responses')
    plot = figure(x_range=['S', 'M', 'L'], y_range=Range1d(0, 106), height=310,
                  sizing_mode='stretch_width', toolbar_location=None,
                  tools='', background_fill_color='#fbfaf6', border_fill_color='#fbfaf6',
                  outline_line_color=None, min_border_left=48)
    plot.vbar(x='cone', top=100, width=.48, color='#eeede7', source=source)
    plot.vbar(x='cone', top='value', width=.48, color='color', source=source)
    plot.add_layout(LabelSet(x='cone', y='value', text='label', source=source,
                            y_offset=9, text_align='center', text_font_size='12px', text_color='#33443d'))
    plot.yaxis.ticker = [0, 25, 50, 75, 100]
    plot.yaxis.axis_label = 'Relative response (%)'
    plot.xgrid.grid_line_color = None
    plot.ygrid.grid_line_color = '#e6e7df'
    plot.axis.axis_line_color = None
    plot.axis.major_tick_line_color = None
    plot.axis.minor_tick_line_color = None
    plot.axis.major_label_text_color = '#53635b'
    plot.xaxis.major_label_text_font_size = '16px'
    spectrum_source = ColumnDataSource(pixel_spectrum(255, 160, 80), name='pixel_spectrum')
    spectrum = wavelength_plot('Relative emission')
    spectrum_fill = rainbow_fill(spectrum, spectrum_source.data['wavelength'],
                                 spectrum_source.data['total'])
    for channel, color in [('blue', '#789fdb'), ('green', '#7caa75'), ('red', '#df735f')]:
        spectrum.line('wavelength', channel, source=spectrum_source, color=color,
                      line_width=1.5)
    spectrum.line('wavelength', 'total', source=spectrum_source, color='#33443d',
                  line_width=2, legend_label='Combined')
    sensitivity_source = ColumnDataSource(cone_sensitivities())
    sensitivity = wavelength_plot('Relative sensitivity')
    envelope = [max(values) for values in zip(*(sensitivity_source.data[c] for c in ('S', 'M', 'L')))]
    rainbow_fill(sensitivity, sensitivity_source.data['wavelength'], envelope)
    for cone, color in [('S', '#789fdb'), ('M', '#7caa75'), ('L', '#df735f')]:
        sensitivity.line('wavelength', cone, source=sensitivity_source, color=color,
                         line_width=2.5, legend_label=cone)
    for panel in (spectrum, sensitivity):
        panel.legend.location = 'top_right'
        panel.legend.orientation = 'horizontal'
        panel.legend.label_text_font_size = '10px'
        panel.legend.background_fill_alpha = 0
        panel.legend.border_line_color = None
        panel.legend.padding = 0
        panel.legend.spacing = 5
    callback = CustomJS(args=dict(red=sliders[0], green=sliders[1], blue=sliders[2],
                                  luminosity=sliders[3], source=source, matrix=RGB_TO_LMS,
                                  spectrum_source=spectrum_source, spectrum_fill=spectrum_fill,
                                  pixel_basis=PIXEL_BASIS),
                        code=(ROOT / 'callbacks.js').read_text())
    for slider in sliders:
        slider.js_on_change('value', callback)
    controls = column(*sliders, sizing_mode='stretch_width', spacing=0)
    script, divs = components(dict(controls=controls, plot=plot,
                                  spectrum=spectrum, sensitivity=sensitivity))
    html = Template((ROOT / 'templates/index.html').read_text()).render(
        resources=INLINE.render(), script=script, **divs)
    target = Path(output) if output else ROOT / 'dist/index.html'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(html)
    return target


if __name__ == '__main__':
    print(build())
