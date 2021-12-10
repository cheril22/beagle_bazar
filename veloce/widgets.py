from django import forms
from django.utils.safestring import mark_safe


class CustomRadio(forms.widgets.RadioSelect):

    def __init__(self, label, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label = label

    def render(self, name, attrs=None, **kwargs):
        attrs = ' '.join([f'{k}="{attrs[k]}"' for k in attrs])
        attrs += ' '.join([f'{k}="{self.attrs[k]}"' for k in self.attrs])

        return mark_safe(f"""           
            <div class="form-check form-check-inline">
              <input class="form-check-input" type="radio" name="inlineRadioOptions" id="inlineRadio1">
              <label class="form-check-label" for="inlineRadio1">1</label>
            </div>
        """)
