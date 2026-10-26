from jinja2.filters import do_attr, do_xmlattr
from jinja2.nodes import EvalContext
from jinja2.sandbox import SandboxedEnvironment
from jinja2.utils import urlize

REPORT_TEMPLATE = '<div {{ attrs|xmlattr }}>{{ body|urlize }}</div>'


def build_environment():
    return SandboxedEnvironment(autoescape=True)


def render_report(body, attrs):
    environment = build_environment()
    return environment.from_string(REPORT_TEMPLATE).render(body=body, attrs=attrs)


def link_urls(text):
    return urlize(text, trim_url_limit=40, rel='nofollow')


def html_attributes(attrs):
    environment = build_environment()
    return do_xmlattr(EvalContext(environment), attrs)


def student_attribute(student, name):
    return do_attr(build_environment(), student, name)


def sandboxed_lookup(obj, attribute):
    return build_environment().getattr(obj, attribute)


def sandboxed_call(template_context, func, *args):
    return build_environment().call(template_context, func, *args)
