// Hash links work on GitHub Pages, offline, and with browser Back/Forward.
const pageLinks = document.querySelectorAll('.page-nav a');
const pages = document.querySelectorAll('.page');

function showPage() {
    const selected = window.location.hash === '#pigments' ? 'pigments' : 'screen';

    for (const page of pages) {
        page.hidden = page.id !== selected;
    }
    for (const link of pageLinks) {
        if (link.hash === `#${selected}`) {
            link.setAttribute('aria-current', 'page');
        } else {
            link.removeAttribute('aria-current');
        }
    }
}

window.addEventListener('hashchange', showPage);
showPage();
