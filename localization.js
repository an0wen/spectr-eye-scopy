(() => {
  const storageKey = 'spectr-eye-scopy.language';
  let language = 'en';
  try {
    const saved = localStorage.getItem(storageKey);
    if (Object.hasOwn(translations, saved)) language = saved;
  } catch (_) { /* Local files and private browsers may disable storage. */ }
  const t = key => translations[language][key] ?? translations.en[key];
  const percent = value => new Intl.NumberFormat(language, {
    style: 'percent', minimumFractionDigits: 1, maximumFractionDigits: 1,
  }).format(value / 100);
  function updateReadouts(doc) {
    const source = doc.get_model_by_name('cone_responses');
    const values = source.data.value;
    source.data.label = Array.from(values, percent);
    source.change.emit();
    document.getElementById('response-readout').textContent = t('response_readout')
      .replace('{s}', percent(values[0])).replace('{m}', percent(values[1])).replace('{l}', percent(values[2]));
    const readout = document.getElementById('rgb-readout');
    readout.textContent = readout.textContent.replace(/^\S+/, t('rgb_label'));
  }
  function apply(doc) {
    document.documentElement.lang = language;
    document.getElementById('language').value = language;
    document.querySelectorAll('[data-i18n]').forEach(el => { el.textContent = t(el.dataset.i18n); });
    document.querySelectorAll('[data-i18n-aria]').forEach(el => { el.setAttribute('aria-label', t(el.dataset.i18nAria)); });
    if (!doc) return;
    ['red', 'green', 'blue', 'luminosity'].forEach(key => { doc.get_model_by_name(key).title = t(key); });
    ['spectrum_wavelength', 'sensitivity_wavelength'].forEach(name => { doc.get_model_by_name(name).axis_label = t('wavelength'); });
    ['emission', 'sensitivity', 'response'].forEach(key => { doc.get_model_by_name(key + '_axis').axis_label = t(key); });
    doc.get_model_by_name('combined_legend').label = {value: t('combined')};
    updateReadouts(doc);
  }
  window.spectrI18n = {apply, updateReadouts};
  apply();
  document.getElementById('language').addEventListener('change', event => {
    language = event.target.value;
    try { localStorage.setItem(storageKey, language); } catch (_) { /* Selection still works. */ }
    apply(window.Bokeh?.documents[0]);
  });
})();
