from django import forms


def select_option(form):
    for field in form.fields:
        f = form.fields[field]
        if isinstance(f, forms.ChoiceField) and len(f.choices) and f.choices[0][0] == '':
            f.choices = [('', 'Select')] + f.choices[1:]
