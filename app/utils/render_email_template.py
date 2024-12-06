from jinja2 import Environment, FileSystemLoader
import os


def render_email_template(template_name: str, context: dict) -> str:
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    env = Environment(loader=FileSystemLoader(template_dir))

    template = env.get_template(template_name)

    return template.render(context)
