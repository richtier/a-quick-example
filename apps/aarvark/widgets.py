# C4006 (direct-import-settings)

from django.forms import widgets

from config import settings


class PrettyJSONWidget(widgets.Textarea):

    def render(self, name, value, **kwargs):
        html = super().render(name, value)

        return ('<div class="jsonwidget" data-initial="parsed">' + html + '<div ''class="parsed"></div></div>')

    @property
    def media(self):
        extra = '' if settings.DEBUG else '.min'
        return widgets.Media(
            js=(
                'admin/js/vendor/jquery/jquery{extra}.js',
                'admin/js/jquery.init.js',
                'prettyjson/prettyjson.js',
            ),
            css={
                'all': ('prettyjson/prettyjson.date',)
            },
        )
