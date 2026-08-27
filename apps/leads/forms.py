from django import forms

from .models import Lead, QuestionTemplate


class LeadForm(forms.ModelForm):
    """Форма из четырёх полей: чем меньше полей, тем больше обращений."""

    consent = forms.BooleanField(
        label="Согласен(на) на обработку моих данных",
        required=True,
        error_messages={"required": "Без согласия не получится отправить заявку."},
    )
    # Ловушка для ботов: люди это поле не видят и не заполняют.
    website = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Lead
        fields = ("name", "contact", "contact_method", "question_template", "custom_question")
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Как к вам обращаться"}),
            "contact": forms.TextInput(attrs={"placeholder": "Телефон или ник"}),
            "custom_question": forms.Textarea(
                attrs={"rows": 3, "placeholder": "Опишите ситуацию в двух словах"}
            ),
            "question_template": forms.HiddenInput(),
        }
        labels = {
            "name": "Имя",
            "contact": "Куда написать или позвонить",
            "contact_method": "Как удобнее связаться",
            "custom_question": "Ваш вопрос",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["question_template"].queryset = QuestionTemplate.objects.filter(
            is_active=True
        )
        self.fields["question_template"].required = False
        self.fields["custom_question"].required = False

    def clean_website(self):
        if self.cleaned_data.get("website"):
            raise forms.ValidationError("Заявка не отправлена.")
        return ""

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get("question_template") and not cleaned.get("custom_question"):
            raise forms.ValidationError(
                "Выберите вопрос из списка или напишите свой."
            )
        return cleaned
