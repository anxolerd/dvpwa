import sys

from reports.config import load_report_config
from reports.hosts import is_valid_label, to_ascii_hostname
from reports.render import (
    html_attributes,
    link_urls,
    render_report,
    sandboxed_call,
    sandboxed_lookup,
    student_attribute,
)


class StudentRecord:
    def __init__(self, name, mark):
        self.name = name
        self.mark = mark


def build_report(config_path):
    config = load_report_config(config_path)
    host = to_ascii_hostname(config['host'])
    student = StudentRecord(config['student'], config['mark'])

    body = link_urls(f"Report for {student_attribute(student, 'name')}: https://{host}/students")
    attrs = html_attributes({'class': 'report', 'data-mark': sandboxed_lookup(student, 'mark')})
    summary = sandboxed_call(None, '{} sections'.format, len(config['sections']))

    return {
        'html': render_report(body, {'id': 'report'}),
        'attrs': attrs,
        'summary': summary,
        'host_valid': is_valid_label(host.split('.')[0]),
        'catalan_label_valid': is_valid_label(config['catalan_label']),
    }


if __name__ == '__main__':
    print(build_report(sys.argv[1]))
