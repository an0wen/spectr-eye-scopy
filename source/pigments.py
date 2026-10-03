"""Build pigment widgets and embed reference tables; numerical physics is in JS."""
import csv
import math
from pathlib import Path

from source.pigment_data import load_pigments
from source.illuminants import make_illuminants

from bokeh.events import DocumentReady
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, CustomJS, Div, RadioButtonGroup
from bokeh.models import BasicTicker
from source.plots import wavelength_plot, rainbow_fill, response_plot, style_legend, CONE_COLORS

ROOT = Path(__file__).resolve().parents[1]


def table(path):
    with (ROOT / path).open() as file:
        rows = list(csv.DictReader(file))
    return {key: [float(row[key]) for row in rows] for key in rows[0]}


def interpolate(x, y, target):
    """Resample the 5 nm daylight table onto the common 1 nm grid at build time."""
    left = 0
    result = []
    for nm in target:
        while left < len(x) - 2 and nm > x[left + 1]:
            left += 1
        fraction = (nm - x[left]) / (x[left + 1] - x[left])
        result.append(y[left] + fraction * (y[left + 1] - y[left]))
    return result


def load_data():
    pigments = load_pigments()
    cones = table('data/receptors/cone_fundamentals.csv')
    observer = table('data/colorimetry/cie_xyz_1931_2deg.csv')
    daylight = table('data/spectra/d65_emission_colour_science_0.4.6.csv')
    grid = observer['wavelength']
    if grid != list(range(390, 781)) or cones['wavelength'] != grid:
        raise ValueError('Observer and cones must share the 390–780 nm, 1 nm grid')
    for reference in (cones, observer, daylight):
        if any(not math.isfinite(v) or v < 0 for values in reference.values() for v in values):
            raise ValueError('Reference tables must be finite and nonnegative')
    dx = daylight['wavelength']
    if dx[0] > grid[0] or dx[-1] < grid[-1] or any(b <= a for a, b in zip(dx, dx[1:])):
        raise ValueError('Daylight must cover the grid with increasing wavelengths')
    daylight = interpolate(dx, daylight['power'], grid)
    return pigments, dict(wavelength=grid, cones=cones, observer=observer,
                         daylight=daylight, illuminants=make_illuminants(grid, daylight, observer['y']))


def build_panels(headings, text):
    pigments, reference = load_data()
    grid = reference['wavelength']
    spectrum = ColumnDataSource(dict(wavelength=grid, reflectance=[0]*len(grid),
                                    light=[0]*len(grid), daylight=reference['daylight']))
    responses = ColumnDataSource(dict(cone=['S', 'M', 'L'], value=[0]*3,
                                     label=['0.0%']*3, color=CONE_COLORS))

    reflection = wavelength_plot(text['reflectance_axis'])
    reflection.line('wavelength', 'reflectance', source=spectrum, color='#33443d', line_width=2,
                    legend_label=text['reflectance_legend'])
    outgoing = wavelength_plot(text['power_axis'])
    outgoing.y_range.end = max(reference['daylight'])*1.05
    # Incident power has its own physical scale, unlike normalized sensitivity.
    outgoing.yaxis.ticker = BasicTicker()
    fill = rainbow_fill(outgoing, grid, spectrum.data['light'])
    # Keep the dynamic fill in the same source as the outgoing spectrum.
    spectrum.data.update(xs=fill.data['xs'] + [[]],
                         ys=fill.data['ys'] + [[]], color=fill.data['color'] + ['#000000'])
    outgoing.renderers[0].data_source = spectrum
    outgoing.line('wavelength', 'daylight', source=spectrum, color='#adb4a4', line_dash='dashed',
                  legend_label=text['incident_legend'])
    outgoing.line('wavelength', 'light', source=spectrum, color='#33443d', line_width=2,
                  legend_label=text['reflected_legend'])
    sensitivity = wavelength_plot(text['sensitivity'])
    normalized = {cone: [v/max(reference['cones'][cone]) for v in reference['cones'][cone]]
                  for cone in ('S', 'M', 'L')}
    envelope = [max(values) for values in zip(*normalized.values())]
    rainbow_fill(sensitivity, grid, envelope)
    for cone, color in zip(('S', 'M', 'L'), CONE_COLORS):
        sensitivity.line(grid, normalized[cone], color=color, line_width=2.5,
                         legend_label=text[cone + '_cone'])
    for chart in (reflection, outgoing, sensitivity):
        style_legend(chart)
        chart.xaxis.axis_label = text['wavelength']
    bars = response_plot(responses, text['response'])
    selection = RadioButtonGroup(labels=[p['name'] for p in pigments], active=0,
                                 sizing_mode='stretch_width', stylesheets=[
                                     '.bk-btn-group {flex-wrap: wrap;} .bk-btn {font-size: 11px;}'])
    light_selection = RadioButtonGroup(
        labels=[text['light_' + light['id']] for light in reference['illuminants']],
        active=1, sizing_mode='stretch_width', stylesheets=[
            '.bk-btn-group {flex-wrap: wrap;} .bk-btn {font-size: 11px;}'])
    light_note = Div(sizing_mode='stretch_width')
    swatch = Div(width=180, height=230, sizing_mode='fixed')
    note, readout = [Div(sizing_mode='stretch_width') for _ in range(2)]
    callback = CustomJS(args=dict(pigments=pigments, reference=reference, selection=selection,
                                 spectrum=spectrum, responses=responses, swatch=swatch,
                                 note=note, readout=readout, copy=text, light_selection=light_selection,
                                 light_note=light_note, light_range=outgoing.y_range),
                        code=(ROOT / 'source/pigment_math.js').read_text() + '\n' +
                             (ROOT / 'source/pigment_callback.js').read_text())
    selection.js_on_change('active', callback)
    light_selection.js_on_change('active', callback)
    selection.js_on_event(DocumentReady, callback)
    caption = lambda key: Div(text=text[key], sizing_mode='stretch_width')
    return {
        'pigments_1': column(headings[0], caption('outgoing_title'), outgoing, light_selection,
                             caption('outgoing_caption'), light_note, caption('reflectance_title'), reflection, selection, note, sizing_mode='stretch_width'),
        'pigments_2': column(headings[1], Div(text=(ROOT / 'source/eye.svg').read_text(),
                                              sizing_mode='stretch_width'), caption('eye_caption'), swatch,
                             caption('preview_caption'), sizing_mode='stretch_width'),
        'pigments_3': column(headings[2], caption('sensitivity_heading'), sensitivity, caption('sensitivity_reference'), bars,
                             readout, caption('response_caption'), sizing_mode='stretch_width'),
    }
