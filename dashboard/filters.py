from humanize import naturaltime
from dashboard import helpers


def initialize_filters(app):
    @app.template_filter()
    def format_time(text):
        return naturaltime(text)

    @app.template_filter()
    def format_duration(text):
        return helpers.format_duration(text)

    @app.template_filter()
    def format_bytes_count(text):
        return helpers.format_bytes_count(text)

    @app.template_filter()
    def shorten_node_key(text):
        return helpers.shorten_node_key(text)
