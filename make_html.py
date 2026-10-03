"""Build the standalone website. Run: python make_html.py."""

import json
from html import escape
from pathlib import Path

from bokeh.embed import components
from bokeh.models import Div
from bokeh.resources import INLINE
from jinja2 import Environment, FileSystemLoader, select_autoescape
from source.pigments import build_panels
from source.screen import build_panels as build_screen_panels


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "source"


def main():
    with (ROOT / "translations" / "en.json").open(encoding="utf-8") as file:
        text = json.load(file)

    # Shared headings for both experiments.
    panels = {}
    for page in ("screen", "pigments"):
        labels = (text[f"{page}_step"], text["eye_step"], text["response_step"])
        for number, label in enumerate(labels, start=1):
            panels[f"{page}_{number}"] = Div(
                text=f'<b class="number">{number:02}</b> {escape(label)}',
                sizing_mode="stretch_width",
                margin=0,
                styles={"color": "#657466", "font-size": "12px"},
                stylesheets=["""
                    .number {
                        display: inline-grid;
                        place-items: center;
                        width: 24px;
                        height: 24px;
                        margin-right: 8px;
                        border: 1px solid #d0d8ca;
                        border-radius: 50%;
                        font-size: 10px;
                    }
                """],
            )
    # build_panels discovers every CSV under data/pigments, including subfolders.
    panels.update(build_panels([panels[f"pigments_{i}"] for i in range(1, 4)], text))
    panels.update(build_screen_panels([panels[f"screen_{i}"] for i in range(1, 4)], text))
    script, panel_html = components(panels)

    templates = Environment(
        loader=FileSystemLoader(SOURCE), autoescape=select_autoescape(["html"])
    )
    html = templates.get_template("interface.html").render(
        text=text,
        panels=panel_html,
        bokeh_script=script,
        resources=INLINE.render(),
        css=(SOURCE / "interface.css").read_text(encoding="utf-8"),
        navigation=(SOURCE / "navigation.js").read_text(encoding="utf-8"),
    )
    output = ROOT / "index.html"
    output.write_text(html, encoding="utf-8")
    print(f"Built {output}")


if __name__ == "__main__":
    main()
