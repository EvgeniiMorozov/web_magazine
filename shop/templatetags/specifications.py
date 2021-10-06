from django import template
from django.utils.safestring import mark_safe

register = template.Library()

TABLE_HEAD = """
                <table class="table">
                    <tbody>
            """
TABLE_TAIL = """
                    </tbody>
                </table>
            """
TABLE_CONTENT = """
                <tr>
                    <td>{name}</td>
                    <td>{value}</td>
                </tr>
            """

PRODUCT_SPEC = {
    "notebook": {
        "Диагональ экрана": "diagonal",
        "Тип дисплея": "display",
        "Процессор": "cpu",
        "Оперативная память": "ram",
        "Видеокарта": "video",
    },
    "smartphone": {
        "Диагональ экрана": "diagonal",
        "Тип дисплея": "display",
        "Разрешение экрана": "resolution",
        "Емкость аккумулятора": "batt_capacity",
        "Оперативная память": "ram",
        "Встроенная память": "rom",
        "Разрешение основной камеры": "main_cam_mp",
    },
}


def get_product_spec(product, model_name):
    # table_content = ""
    # for name, value in PRODUCT_SPEC[model_name].items():
    #     table_content += TABLE_CONTENT.format(name=name, value=getattr(product, value))
    # return table_content
    return "".join(
        TABLE_CONTENT.format(name=name, value=getattr(product, value))
        for name, value in PRODUCT_SPEC[model_name].items()
    )


@register.filter
def product_spec(product):
    model_name = product.__class__._meta.model_name
    return mark_safe(TABLE_HEAD + get_product_spec(product, model_name) + TABLE_TAIL)
