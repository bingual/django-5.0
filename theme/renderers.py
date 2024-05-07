from rest_framework.renderers import StaticHTMLRenderer

from theme.utils import create_excel_file


class PandasXlsxRenderer(StaticHTMLRenderer):
    media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    format = "xlsx"
    charset = None
    render_style = "binary"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        filename = renderer_context.get("filename", "default_filename.xlsx")
        excel_file = create_excel_file(data, filename)
        return excel_file
