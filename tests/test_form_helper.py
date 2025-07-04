import re

import django
import pytest
from crispy_forms.bootstrap import (
    AppendedText,
    FieldWithButtons,
    PrependedAppendedText,
    PrependedText,
    StrictButton,
)
from crispy_forms.helper import FormHelper, FormHelpersException
from crispy_forms.layout import Button, Hidden, Layout, Reset, Submit
from crispy_forms.templatetags.crispy_forms_tags import CrispyFormNode
from crispy_forms.utils import render_crispy_form
from django import forms
from django.forms.models import formset_factory
from django.middleware.csrf import _get_new_csrf_string
from django.template import Context, Template
from django.test import override_settings
from django.test.html import parse_html
from django.urls import reverse

from .forms import SampleForm, SampleForm7, SampleForm8, SampleFormWithMedia
from .utils import parse_expected, parse_form

CONVERTERS = {
    "textinput": "textinput textInput inputtext",
    "fileinput": "fileinput fileUpload",
    "passwordinput": "textinput textInput",
}


def test_inputs():
    form_helper = FormHelper()
    form_helper.add_input(Submit("my-submit", "Submit", css_class="button white"))
    form_helper.add_input(Reset("my-reset", "Reset"))
    form_helper.add_input(Hidden("my-hidden", "Hidden"))
    form_helper.add_input(Button("my-button", "Button"))

    template = Template(
        """
        {% load crispy_forms_tags %}
        {% crispy form form_helper %}
    """
    )
    c = Context({"form": SampleForm(), "form_helper": form_helper})
    html = template.render(c)

    assert "button white" in html
    assert 'id="submit-id-my-submit"' in html
    assert 'id="reset-id-my-reset"' in html
    assert 'name="my-hidden"' in html
    assert 'id="button-id-my-button"' in html
    assert 'class="btn"' in html
    assert "btn btn-primary" in html
    assert "btn btn-inverse" in html
    assert len(re.findall(r"<input[^>]+> <", html)) == 9


def test_invalid_form_method():
    form_helper = FormHelper()
    with pytest.raises(FormHelpersException):
        form_helper.form_method = "superPost"


def test_form_with_helper_without_layout():
    form_helper = FormHelper()
    form_helper.form_id = "this-form-rocks"
    form_helper.form_class = "forms-that-rock"
    form_helper.form_method = "GET"
    form_helper.form_action = "simpleAction"
    form_helper.form_error_title = "ERRORS"

    template = Template(
        """
        {% load crispy_forms_tags %}
        {% crispy testForm form_helper %}
    """
    )

    # now we render it, with errors
    form = SampleForm({"password1": "wargame", "password2": "god"})
    form.is_valid()
    c = Context({"testForm": form, "form_helper": form_helper})
    html = template.render(c)

    # Lets make sure everything loads right
    assert html.count("<form") == 1
    assert "forms-that-rock" in html
    assert 'method="get"' in html
    assert 'id="this-form-rocks"' in html
    assert 'action="%s"' % reverse("simpleAction") in html

    assert "ERRORS" in html
    assert "<li>Passwords dont match</li>" in html

    # now lets remove the form tag and render it again. All the True items above
    # should now be false because the form tag is removed.
    form_helper.form_tag = False
    html = template.render(c)
    assert "<form" not in html
    assert "forms-that-rock" not in html
    assert 'method="get"' not in html
    assert 'id="this-form-rocks"' not in html


@override_settings(CRISPY_CLASS_CONVERTERS=CONVERTERS)
def test_form_show_errors_non_field_errors(settings):
    form = SampleForm({"password1": "wargame", "password2": "god"})
    form.helper = FormHelper()
    form.helper.form_show_errors = True
    form.is_valid()

    template = Template(
        """
        {% load crispy_forms_tags %}
        {% crispy testForm %}
    """
    )

    # First we render with errors
    c = Context({"testForm": form})
    # Ensure those errors were rendered
    if django.VERSION < (5, 0):
        expected = parse_expected(
            "bootstrap4/test_form_helper/"
            "test_form_show_errors_non_field_errors_true_lt50.html"
        )
    elif django.VERSION < (5, 2):
        expected = parse_expected(
            "bootstrap4/test_form_helper/"
            "test_form_show_errors_non_field_errors_true_lt52.html"
        )
    else:
        expected = parse_expected(
            "bootstrap4/test_form_helper/"
            "test_form_show_errors_non_field_errors_true.html"
        )
    assert parse_html(template.render(c)) == expected

    # Now we render without errors
    form.helper.form_show_errors = False
    c = Context({"testForm": form})
    # Ensure errors were not rendered
    if django.VERSION < (5, 0):
        expected = parse_expected(
            "bootstrap4/test_form_helper/"
            "test_form_show_errors_non_field_errors_false_lt50.html"
        )
    elif django.VERSION < (5, 2):
        expected = parse_expected(
            "bootstrap4/test_form_helper/"
            "test_form_show_errors_non_field_errors_false_lt52.html"
        )
    else:
        expected = parse_expected(
            "bootstrap4/test_form_helper/"
            "test_form_show_errors_non_field_errors_false.html"
        )
    assert parse_html(template.render(c)) == expected


def test_media_is_included_by_default_with_bootstrap4():
    form = SampleFormWithMedia()
    form.helper = FormHelper()
    form.helper.template_pack = "bootstrap4"
    html = render_crispy_form(form)
    assert "test.css" in html
    assert "test.js" in html


def test_media_removed_when_include_media_is_false_with_bootstrap4():
    form = SampleFormWithMedia()
    form.helper = FormHelper()
    form.helper.template_pack = "bootstrap4"
    form.helper.include_media = False
    html = render_crispy_form(form)
    assert "test.css" not in html
    assert "test.js" not in html


def test_attrs():
    form = SampleForm()
    form.helper = FormHelper()
    form.helper.attrs = {"id": "TestIdForm", "autocomplete": "off"}
    html = render_crispy_form(form)

    assert 'autocomplete="off"' in html
    assert 'id="TestIdForm"' in html


def test_template_context():
    helper = FormHelper()
    helper.attrs = {
        "id": "test-form",
        "class": "test-forms",
        "action": "submit/test/form",
        "autocomplete": "off",
    }
    node = CrispyFormNode("form", "helper")
    context = node.get_response_dict(helper, {}, False)

    assert context["form_id"] == "test-form"
    assert context["form_attrs"]["id"] == "test-form"
    assert "test-forms" in context["form_class"]
    assert "test-forms" in context["form_attrs"]["class"]
    assert context["form_action"] == "submit/test/form"
    assert context["form_attrs"]["action"] == "submit/test/form"
    assert context["form_attrs"]["autocomplete"] == "off"


def test_template_context_using_form_attrs():
    helper = FormHelper()
    helper.form_id = "test-form"
    helper.form_class = "test-forms"
    helper.form_action = "submit/test/form"
    node = CrispyFormNode("form", "helper")
    context = node.get_response_dict(helper, {}, False)

    assert context["form_id"] == "test-form"
    assert context["form_attrs"]["id"] == "test-form"
    assert "test-forms" in context["form_class"]
    assert "test-forms" in context["form_attrs"]["class"]
    assert context["form_action"] == "submit/test/form"
    assert context["form_attrs"]["action"] == "submit/test/form"


def test_template_helper_access():
    helper = FormHelper()
    helper.form_id = "test-form"

    assert helper["form_id"] == "test-form"


def test_without_helper():
    template = Template(
        """
        {% load crispy_forms_tags %}
        {% crispy form %}
    """
    )
    c = Context({"form": SampleForm()})
    html = template.render(c)

    # Lets make sure everything loads right
    assert "<form" in html
    assert 'method="post"' in html
    assert "action" not in html


def test_formset_with_helper_without_layout():
    template = Template(
        """
        {% load crispy_forms_tags %}
        {% crispy testFormSet formset_helper %}
    """
    )

    form_helper = FormHelper()
    form_helper.form_id = "thisFormsetRocks"
    form_helper.form_class = "formsets-that-rock"
    form_helper.form_method = "POST"
    form_helper.form_action = "simpleAction"

    SampleFormSet = formset_factory(SampleForm, extra=3)
    testFormSet = SampleFormSet()

    c = Context(
        {
            "testFormSet": testFormSet,
            "formset_helper": form_helper,
            "csrf_token": _get_new_csrf_string(),
        }
    )
    html = template.render(c)

    assert html.count("<form") == 1
    assert html.count("csrfmiddlewaretoken") == 1

    # Check formset management form
    assert "form-TOTAL_FORMS" in html
    assert "form-INITIAL_FORMS" in html
    assert "form-MAX_NUM_FORMS" in html

    assert "formsets-that-rock" in html
    assert 'method="post"' in html
    assert 'id="thisFormsetRocks"' in html
    assert 'action="%s"' % reverse("simpleAction") in html


def test_CSRF_token_POST_form():
    form_helper = FormHelper()
    template = Template(
        """
        {% load crispy_forms_tags %}
        {% crispy form form_helper %}
    """
    )

    # The middleware only initializes the CSRF token when processing a real request
    # So using RequestContext or csrf(request) here does not work.
    # Instead I set the key `csrf_token` to a CSRF token manually, which `csrf_token`
    # tag uses
    c = Context(
        {
            "form": SampleForm(),
            "form_helper": form_helper,
            "csrf_token": _get_new_csrf_string(),
        }
    )
    html = template.render(c)

    assert "csrfmiddlewaretoken" in html


def test_CSRF_token_GET_form():
    form_helper = FormHelper()
    form_helper.form_method = "GET"
    template = Template(
        """
        {% load crispy_forms_tags %}
        {% crispy form form_helper %}
    """
    )

    c = Context(
        {
            "form": SampleForm(),
            "form_helper": form_helper,
            "csrf_token": _get_new_csrf_string(),
        }
    )
    html = template.render(c)

    assert "csrfmiddlewaretoken" not in html


def test_disable_csrf():
    form = SampleForm()
    helper = FormHelper()
    helper.disable_csrf = True
    html = render_crispy_form(form, helper, {"csrf_token": _get_new_csrf_string()})
    assert "csrf" not in html


def test_render_unmentioned_fields():
    test_form = SampleForm()
    test_form.helper = FormHelper()
    test_form.helper.layout = Layout("email")
    test_form.helper.render_unmentioned_fields = True

    html = render_crispy_form(test_form)
    assert html.count("<input") == 8


def test_render_unmentioned_fields_order():
    test_form = SampleForm7()
    test_form.helper = FormHelper()
    test_form.helper.layout = Layout("email")
    test_form.helper.render_unmentioned_fields = True

    html = render_crispy_form(test_form)
    assert html.count("<input") == 4
    assert (
        # From layout
        html.index('id="div_id_email"')
        # From form.Meta.fields
        < html.index('id="div_id_password"')
        < html.index('id="div_id_password2"')
        # From fields
        < html.index('id="div_id_is_company"')
    )

    test_form = SampleForm8()
    test_form.helper = FormHelper()
    test_form.helper.layout = Layout("email")
    test_form.helper.render_unmentioned_fields = True

    html = render_crispy_form(test_form)
    assert html.count("<input") == 4
    assert (
        # From layout
        html.index('id="div_id_email"')
        # From form.Meta.fields
        < html.index('id="div_id_password2"')
        < html.index('id="div_id_password"')
        # From fields
        < html.index('id="div_id_is_company"')
    )


def test_render_hidden_fields():
    from .utils import contains_partial

    test_form = SampleForm()
    test_form.helper = FormHelper()
    test_form.helper.layout = Layout("email")
    test_form.helper.render_hidden_fields = True

    html = render_crispy_form(test_form)
    assert html.count("<input") == 1

    # Now hide a couple of fields
    for field in ("password1", "password2"):
        test_form.fields[field].widget = forms.HiddenInput()

    html = render_crispy_form(test_form)
    assert html.count("<input") == 3
    assert html.count("hidden") == 2

    assert contains_partial(html, '<input name="password1" type="hidden"/>')
    assert contains_partial(html, '<input name="password2" type="hidden"/>')


def test_render_required_fields():
    test_form = SampleForm()
    test_form.helper = FormHelper()
    test_form.helper.layout = Layout("email")
    test_form.helper.render_required_fields = True

    html = render_crispy_form(test_form)
    assert html.count("<input") == 7


def test_helper_custom_template():
    form = SampleForm()
    form.helper = FormHelper()
    form.helper.template = "custom_form_template.html"

    html = render_crispy_form(form)
    assert "<h1>Special custom form</h1>" in html


def test_helper_custom_field_template():
    form = SampleForm()
    form.helper = FormHelper()
    form.helper.layout = Layout("password1", "password2")
    form.helper.field_template = "custom_field_template.html"

    html = render_crispy_form(form)
    assert html.count("<h1>Special custom field</h1>") == 2


def test_helper_custom_field_template_no_layout():
    form = SampleForm()
    form.helper = FormHelper()
    form.helper.field_template = "custom_field_template.html"

    html = render_crispy_form(form)
    for field in form.fields:
        assert html.count('id="div_id_%s"' % field) == 1
    assert html.count("<h1>Special custom field</h1>") == len(form.fields)


def test_helper_std_field_template_no_layout():
    form = SampleForm()
    form.helper = FormHelper()

    html = render_crispy_form(form)
    for field in form.fields:
        assert html.count('id="div_id_%s"' % field) == 1


@override_settings(CRISPY_CLASS_CONVERTERS=CONVERTERS)
def test_bootstrap_form_show_errors_bs4():
    form = SampleForm(
        {
            "email": "invalidemail",
            "first_name": "first_name_too_long",
            "last_name": "last_name_too_long",
            "password1": "yes",
            "password2": "yes",
        }
    )
    form.helper = FormHelper()
    form.helper.layout = Layout(
        AppendedText("email", "whatever"),
        PrependedText("first_name", "blabla"),
        PrependedAppendedText("last_name", "foo", "bar"),
        AppendedText("password1", "whatever"),
        PrependedText("password2", "blabla"),
    )
    form.is_valid()
    form.helper.form_show_errors = True
    if django.VERSION < (5, 0):
        expected = (
            "bootstrap4/test_form_helper/bootstrap_form_show_errors_bs4_true_lt50.html"
        )
    elif django.VERSION < (5, 2):
        expected = (
            "bootstrap4/test_form_helper/bootstrap_form_show_errors_bs4_true_lt52.html"
        )
    else:
        expected = (
            "bootstrap4/test_form_helper/bootstrap_form_show_errors_bs4_true.html"
        )
    assert parse_form(form) == parse_expected(expected)
    form.helper.form_show_errors = False
    if django.VERSION < (5, 0):
        expected = (
            "bootstrap4/test_form_helper/bootstrap_form_show_errors_bs4_false_lt50.html"
        )
    elif django.VERSION < (5, 2):
        expected = (
            "bootstrap4/test_form_helper/bootstrap_form_show_errors_bs4_false_lt52.html"
        )
    else:
        expected = (
            "bootstrap4/test_form_helper/bootstrap_form_show_errors_bs4_false.html"
        )
    assert parse_form(form) == parse_expected(expected)


def test_error_text_inline(settings):
    form = SampleForm({"email": "invalidemail"})
    form.helper = FormHelper()
    layout = Layout(
        AppendedText("first_name", "wat"),
        PrependedText("email", "@"),
        PrependedAppendedText("last_name", "@", "wat"),
    )
    form.helper.layout = layout
    form.is_valid()
    html = render_crispy_form(form)

    matches = re.findall(r'<span id="error_\d_\w*"', html, re.MULTILINE)
    assert len(matches) == 3

    form = SampleForm({"email": "invalidemail"})
    form.helper = FormHelper()
    form.helper.layout = layout
    form.helper.error_text_inline = False
    html = render_crispy_form(form)

    help_tag_name = "p"

    matches = re.findall(
        r'<{} id="error_\d_\w*"'.format(help_tag_name),
        html,
        re.MULTILINE,
    )
    assert len(matches) == 3


def test_error_and_help_inline():
    form = SampleForm({"email": "invalidemail"})
    form.helper = FormHelper()
    form.helper.error_text_inline = False
    form.helper.help_text_inline = True
    form.helper.layout = Layout("email")
    form.is_valid()
    html = render_crispy_form(form)

    # Check that help goes before error, otherwise CSS won't work
    help_position = html.find('<span id="id_email_helptext" class="help-inline">')
    error_position = html.find('<p id="error_1_id_email">')
    assert help_position < error_position

    # Viceversa
    form = SampleForm({"email": "invalidemail"})
    form.helper = FormHelper()
    form.helper.error_text_inline = True
    form.helper.help_text_inline = False
    form.helper.layout = Layout("email")
    form.is_valid()
    html = render_crispy_form(form)

    # Check that error goes before help, otherwise CSS won't work
    error_position = html.find('<span id="error_1_id_email" class="help-inline">')
    help_position = html.find(
        '<small id="id_email_helptext" class="form-text text-muted">'
    )
    assert error_position < help_position


def test_form_show_labels():
    form = SampleForm()
    form.helper = FormHelper()
    form.helper.layout = Layout(
        "password1",
        FieldWithButtons("password2", StrictButton("Confirm")),
        PrependedText("first_name", "Mr."),
        AppendedText("last_name", "@"),
        PrependedAppendedText("datetime_field", "on", "secs"),
    )
    form.helper.form_show_labels = False

    html = render_crispy_form(form)
    assert html.count("<label") == 0


def test_label_class_and_field_class_bs4():
    form = SampleForm()
    form.helper = FormHelper()
    form.helper.label_class = "col-lg-2"
    form.helper.field_class = "col-lg-8"
    html = render_crispy_form(form)

    assert '<div class="form-group">' in html
    assert '<div class="col-lg-8">' in html
    assert html.count("col-lg-8") == 7
    assert "offset" not in html

    form.helper.label_class = "col-sm-3 col-md-4"
    form.helper.field_class = "col-sm-8 col-md-6"
    html = render_crispy_form(form)

    assert '<div class="form-group">' in html
    assert '<div class="col-sm-8 col-md-6">' in html
    assert html.count("col-sm-8") == 7
    assert "offset" not in html


def test_label_class_and_field_class_bs4_offset_when_horizontal():
    # Test col-XX-YY pattern
    form = SampleForm()
    form.helper = FormHelper()
    form.helper.label_class = "col-lg-2"
    form.helper.field_class = "col-lg-8"
    form.helper.form_class = "form-horizontal"
    html = render_crispy_form(form)

    assert '<div class="form-group row">' in html
    assert '<div class="offset-lg-2 col-lg-8">' in html
    assert html.count("col-lg-8") == 7

    # Test multi col-XX-YY pattern and col-X pattern

    form.helper.label_class = "col-sm-3 col-md-4 col-5 col-lg-4"
    form.helper.field_class = "col-sm-8 col-md-6 col-7 col-lg-8"
    html = render_crispy_form(form)

    assert '<div class="form-group row">' in html
    assert (
        '<div class="offset-sm-3 offset-md-4 offset-5 offset-lg-4 col-sm-8 '
        'col-md-6 col-7 col-lg-8">' in html
    )
    assert html.count("col-sm-8") == 7
    assert html.count("col-md-6") == 7
    assert html.count("col-7") == 7
    assert html.count("col-lg-8") == 7


def test_form_group_with_form_inline_bs4():
    form = SampleForm()
    form.helper = FormHelper()
    html = render_crispy_form(form)
    assert '<div class="form-group">' in html

    # .row class shouldn't be together with .form-group in inline forms
    form = SampleForm()
    form.helper = FormHelper()
    form.helper.form_class = "form-inline"
    form.helper.field_template = "bootstrap4/layout/inline_field.html"
    html = render_crispy_form(form)
    assert '<div class="form-group row">' not in html


def test_passthrough_context():
    """
    Test to ensure that context is passed through implicitly from outside of
    the crispy form into the crispy form templates.
    """
    form = SampleForm()
    form.helper = FormHelper()
    form.helper.template = "custom_form_template_with_context.html"

    c = {"prefix": "foo", "suffix": "bar"}

    html = render_crispy_form(form, helper=form.helper, context=c)
    assert "Got prefix: foo" in html
    assert "Got suffix: bar" in html
