import flet as ft

class LoginPage(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.route = "/login"
        self.bgcolor = ft.colors.WHITE
        
        def login_clicked(e):
            if (self.username_field.value == "manza" and 
                self.password_field.value == "fac"):
                self.page.go("/invoice")
            else:
                self.page.show_snack_bar(
                    ft.SnackBar(content=ft.Text("Usuario Inválido"))
                )

        self.username_field = ft.TextField(
            label="Usuario",
            border_color=ft.colors.RED_400,
            width=300
        )
        
        self.password_field = ft.TextField(
            label="Contraseña",
            password=True,
            border_color=ft.colors.RED_400,
            width=300
        )

        self.controls = [
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text("Bienvenido a ManzaFAC", 
                               size=32, 
                               color=ft.colors.RED_700),
                        self.username_field,
                        self.password_field,
                        ft.ElevatedButton(
                            "Ingresar",
                            on_click=login_clicked,
                            bgcolor=ft.colors.RED_700,
                            color=ft.colors.WHITE
                        ),
                        ft.TextButton(
                            "Registrar negocio",
                            on_click=lambda _: self.page.go("/register")
                        )
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20
                ),
                padding=40,
                alignment=ft.alignment.center
            )
        ] 