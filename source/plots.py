"""Shared chart styling keeps both experiments visually consistent."""
from bokeh.models import ColumnDataSource, LabelSet, Range1d
from bokeh.plotting import figure

CONE_COLORS = ['#789fdb', '#7caa75', '#df735f']

def wavelength_plot(y_label):
    plot = figure(x_range=(390, 780), y_range=(0, 1.12), height=210,
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


def response_plot(source, y_label):
    plot = figure(x_range=['S', 'M', 'L'], y_range=Range1d(0, 106), height=190,
                  sizing_mode='stretch_width', toolbar_location=None,
                  tools='', background_fill_color='#fbfaf6', border_fill_color='#fbfaf6',
                  outline_line_color=None, min_border_left=48)
    plot.vbar(x='cone', top=100, width=.48, color='#eeede7', source=source)
    plot.vbar(x='cone', top='value', width=.48, color='color', source=source)
    plot.add_layout(LabelSet(x='cone', y='value', text='label', source=source,
                            y_offset=9, text_align='center', text_font_size='12px', text_color='#33443d'))
    plot.yaxis.ticker = [0, 25, 50, 75, 100]
    plot.yaxis.axis_label = y_label
    plot.xgrid.grid_line_color = None
    plot.ygrid.grid_line_color = '#e6e7df'
    plot.axis.axis_line_color = None
    plot.axis.major_tick_line_color = None
    plot.axis.minor_tick_line_color = None
    plot.axis.major_label_text_color = '#53635b'
    plot.xaxis.major_label_text_font_size = '16px'
    return plot


def style_legend(panel):
    panel.legend.location = 'top_right'
    panel.legend.orientation = 'horizontal'
    panel.legend.label_text_font_size = '10px'
    panel.legend.background_fill_alpha = 0
    panel.legend.border_line_color = None
    panel.legend.padding = 0
    panel.legend.spacing = 5
