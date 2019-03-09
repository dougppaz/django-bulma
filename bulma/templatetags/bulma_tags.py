from django import forms
from django import template
from django.forms import BoundField
from django.template.base import FilterExpression
from django.template.library import SimpleNode
from django.template.loader import get_template
from django.utils.safestring import mark_safe

register = template.Library()
BULMA_COLUMN_COUNT = 1


@register.simple_tag
def bulma_inline(element, **kwargs):
    kwargs['inline'] = True
    return bulma(element, **kwargs)


@register.simple_tag
def bulma(
        element,
        size=None,
        inline=False,
        wrap_with_field=True,
        icon_left=None,
        icon_left_size=None,
        icon_right=None,
        icon_right_size=None,
        css_class=None,
        control_css_class=None
):
    markup_classes = {
        'label': '',
        'field': css_class or '',
        'control': control_css_class or '',
        'input': size or '',
        'single_value': '',
        'icon_left': icon_left,
        'icon_left_size': 'is-' + (icon_left_size or 'small'),
        'icon_right': icon_right,
        'icon_right_size': 'is-' + (icon_right_size or 'small'),
    }
    if icon_left:
        markup_classes['control'] += ' has-icons-left'
    if icon_right:
        markup_classes['control'] += ' has-icons-right'
    if inline:
        markup_classes['label'] = 'sr-only'

    return render(
        element,
        markup_classes=markup_classes,
        wrap_with_field=wrap_with_field
    )


@register.simple_tag
def font_awesome():
    """
    The latest FontAwesome CDN link.
    """
    cdn_link = (
        '<link rel="stylesheet" '
        'href="https://use.fontawesome.com/releases/v5.7.2/css/all.css" '
        'integrity="sha384-fnmOCqbTlWIlj8LyTjo7mOUStjsKC4pOpQbqyi7RrhN7udi9RwhKkMHpvLbHG9Sr" '
        'crossorigin="anonymous">'
    )
    return mark_safe(cdn_link)


@register.filter(name="bulma")
def bulma_deprecated(element):
    markup_classes = {'label': '', 'control': '', 'single_value': ''}
    return render(element, markup_classes=markup_classes, wrap_with_field=True)


@register.filter(name="bulma_inline")
def bulma_inline_deprecated(element):
    markup_classes = {'label': 'sr-only', 'control': '', 'single_value': ''}
    return render(element, markup_classes=markup_classes, wrap_with_field=True)


@register.filter(name="bulma_horizontal")
def bulma_horizontal_deprecated(element, label_cols='is-2'):
    markup_classes = {'label': label_cols, 'control': '', 'single_value': ''}

    for cl in label_cols.split(' '):
        splitted_class = cl.split('-')

        try:
            value_nb_cols = int(splitted_class[-1])
        except ValueError:
            value_nb_cols = BULMA_COLUMN_COUNT

        if value_nb_cols >= BULMA_COLUMN_COUNT:
            splitted_class[-1] = str(BULMA_COLUMN_COUNT)
        else:
            offset_class = cl.split('-')
            offset_class[-1] = 'offset-' + str(value_nb_cols)
            splitted_class[-1] = str(BULMA_COLUMN_COUNT - value_nb_cols)
            markup_classes['single_value'] += ' ' + '-'.join(offset_class)
            markup_classes['single_value'] += ' ' + '-'.join(splitted_class)

        markup_classes['value'] += ' ' + '-'.join(splitted_class)

    return render(element, markup_classes=markup_classes, wrap_with_field=True)


@register.filter
def add_input_classes(field, size=None):
    field_classes = field.field.widget.attrs.get('class', '')
    if len(field.errors) > 0:
        field_classes += ' is-danger'
    if size:
        field_classes += " is-" + size
    field.field.widget.attrs['class'] = field_classes


def render(element, **kwargs):
    markup_classes = kwargs.pop('markup_classes', {})
    wrap_with_field = kwargs.pop('wrap_with_field', True)

    template_name = "bulma/forms/fields.html"
    if isinstance(element, BoundField):
        add_input_classes(element, markup_classes.get('input', ''))
        context = {
            'field': element,
            'classes': markup_classes,
            'form': element.form,
            'wrap_with_field': wrap_with_field
        }
    else:
        has_management = getattr(element, 'management_form', None)
        if has_management:
            for form in element.forms:
                for field in form.visible_fields():
                    add_input_classes(field)

            template_name = "bulma/forms/formset.html"
            context = {'formset': element, 'classes': markup_classes, 'wrap_with_field': wrap_with_field}
        else:
            for field in element.visible_fields():
                add_input_classes(field)

            template_name = "bulma/forms/form.html"
            context = {'form': element, 'classes': markup_classes, 'wrap_with_field': wrap_with_field}

    return get_template(template_name).render(context)


@register.filter
def widget_type(field):
    return field.field.widget


@register.filter
def is_select(field):
    return isinstance(field.field.widget, forms.Select)


@register.filter
def is_multiple_select(field):
    return isinstance(field.field.widget, forms.SelectMultiple)


@register.filter
def is_textarea(field):
    return isinstance(field.field.widget, forms.Textarea)


@register.filter
def is_input(field):
    return isinstance(field.field.widget, (
        forms.TextInput,
        forms.NumberInput,
        forms.EmailInput,
        forms.PasswordInput,
        forms.URLInput
    ))


@register.filter
def is_checkbox(field):
    return isinstance(field.field.widget, forms.CheckboxInput)


@register.filter
def is_multiple_checkbox(field):
    return isinstance(field.field.widget, forms.CheckboxSelectMultiple)


@register.filter
def is_radio(field):
    return isinstance(field.field.widget, forms.RadioSelect)


@register.filter
def is_file(field):
    return isinstance(field.field.widget, forms.FileInput)


@register.filter
def addclass(field, css_class):
    field.field.widget.attrs['class'] += ' ' + css_class
    return field


@register.filter
def bulma_message_tag(tag):
    return {
        'error': 'danger'
    }.get(tag, tag)


@register.tag
def bulma_addons(parser, token):
    return _bulma_group_addons(parser, token, 'endbulma_addons', 'has-addons')


@register.tag
def bulma_group(parser, token):
    return _bulma_group_addons(parser, token, 'endbulma_group', 'is-grouped')


def _bulma_group_addons(parser, token, end_token, main_css_class):
    tag_name, arg = token.contents.split(None, 1)
    group_kwargs = {arg_val.split("=")[0]: arg_val.split("=")[1].lstrip('"').rstrip('"') for arg_val in arg.split(" ")}
    group_kwargs['css_class'] = f"{main_css_class} {group_kwargs.get('css_class')}"

    nodelist = parser.parse((end_token,))
    parser.delete_first_token()

    for node in nodelist:
        if isinstance(node, SimpleNode) and node.func in [bulma, bulma_inline]:
            node.kwargs['wrap_with_field'] = FilterExpression('False', parser)
            node.kwargs['inline'] = FilterExpression('True', parser)

    return GroupNode(nodelist, group_kwargs)


class GroupNode(template.Node):
    def __init__(self, nodelist, group_kwargs):
        self.nodelist = nodelist
        self.group_kwargs = group_kwargs

    def render(self, context):
        output = self.nodelist.render(context)
        return f'<div class="field {self.group_kwargs.get("css_class")}">{output}</div>'
