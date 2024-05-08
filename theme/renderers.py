from rest_framework.renderers import StaticHTMLRenderer


class PandasXlsxRenderer(StaticHTMLRenderer):
    media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    format = "xlsx"
    charset = None
    render_style = "binary"
