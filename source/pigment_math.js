// Pure mathematics: no Bokeh, DOM, network, or Python server is needed.
const pigmentMath = (() => {
    // Area under sampled y(x): each pair of samples forms a trapezoid.
    function integrate(x, y) {
        let area = 0;
        for (let i = 1; i < x.length; i++) {
            area += (x[i] - x[i - 1]) * (y[i] + y[i - 1]) / 2;
        }
        return area;
    }

    // Linear interpolation: walk along the sorted source samples and join
    // neighboring points with straight lines. The build checks grid coverage.
    function interpolate(x, y, target) {
        let left = 0;
        return target.map(wavelength => {
            while (left < x.length - 2 && wavelength > x[left + 1]) left++;
            const fraction = (wavelength - x[left]) / (x[left + 1] - x[left]);
            return y[left] + fraction * (y[left + 1] - y[left]);
        });
    }

    function reflectance(pigment, wavelengths) {
        const samples = interpolate(pigment.wavelength, pigment.values, wavelengths);
        // One pass transmits T = 10^(-A). A white backing returns that light
        // through the layer again, so R = T*T = 10^(-2A).
        // Interpolate absorbance BEFORE applying this nonlinear conversion.
        return pigment.kind === 'absorbance'
            ? samples.map(absorbance => 10 ** (-2 * absorbance)) : samples;
    }

    function encodeSRGB(linear) {
        // Clip at the display boundary only; never brighten a dark pigment.
        const clipped = Math.max(0, Math.min(1, linear));
        const encoded = clipped <= 0.0031308
            ? 12.92 * clipped : 1.055 * clipped ** (1 / 2.4) - 0.055;
        return Math.round(255 * encoded);
    }

    function calculate(pigment, reference, incident = reference.daylight) {
        const {wavelength, cones, observer} = reference;
        const reflected = reflectance(pigment, wavelength);
        // E = selected incident light, R = reflectance; outgoing light is E*R.
        const light = incident.map((energy, i) => energy * reflected[i]);
        const weightedArea = (spectrum, sensitivity) => integrate(
            wavelength, spectrum.map((energy, i) => energy * sensitivity[i]));

        // Each cone has its OWN white reference under the SELECTED illuminant. A 50% gray reflector
        // gives 50% in every cone, regardless of the shape of its sensitivity.
        const responses = ['S', 'M', 'L'].map(cone =>
            100 * weightedArea(light, cones[cone]) / weightedArea(incident, cones[cone]));

        // Color takes a separate path through CIE XYZ; S/M/L are NOT RGB.
        // The single denominator makes perfect white have Y = 1.
        const whiteY = weightedArea(incident, observer.y);
        const xyz = ['x', 'y', 'z'].map(axis => weightedArea(light, observer[axis]) / whiteY);
        // XYZ -> D65-display linear sRGB. No chromatic adaptation is applied:
        // a white object under a warm lamp retains the lamp color cast.
        const matrix = [
            [3.2409699419, -1.5373831776, -0.4986107603],
            [-0.9692436363, 1.8759675015, 0.0415550574],
            [0.0556300797, -0.2039769589, 1.0569715142],
        ];
        const rgb = matrix.map(row => encodeSRGB(
            row.reduce((sum, coefficient, i) => sum + coefficient * xyz[i], 0)));
        return {reflected, light, responses, xyz, rgb};
    }
    return {integrate, interpolate, reflectance, encodeSRGB, calculate};
})();
if (typeof module !== 'undefined') module.exports = pigmentMath;
