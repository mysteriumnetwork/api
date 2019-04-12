from humanize import naturaltime
from dashboard.helpers import format_duration, get_natural_size


def initialize_filters(app):
    @app.template_filter('naturaltime')
    def naturaltime_filter(text):
        return naturaltime(text)

    @app.template_filter('format_duration')
    def format_duration_filter(text):
        return format_duration(text)

    @app.template_filter('get_natural_size')
    def get_natural_size_filter(text):
        return get_natural_size(text)

    @app.template_filter('shorten_node_key')
    def shorten_node_key(text):
        return shorten_node_key(text)
