from django.contrib.auth.forms import AuthenticationForm


class LoginForm(AuthenticationForm):
    """RF-19: formulario de inicio de sesión con el estilo de los mockups."""

    error_messages = {
        **AuthenticationForm.error_messages,
        "invalid_login": "Usuario o contraseña incorrectos. Vuelve a intentarlo.",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Usuario"
        self.fields["password"].label = "Contraseña"
        for campo in self.fields.values():
            campo.widget.attrs["class"] = "input"
