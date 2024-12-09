from jinja2 import Template
from pathlib import Path


def render_email_template(template_name: str, context: dict) -> str:
    template_str = (
            Path(__file__).parent / ".." / "templates" / template_name
    ).read_text()
    template = Template(template_str)

    return template.render(context)
