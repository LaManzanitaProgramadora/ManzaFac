import flet as ft
from login_page import LoginPage
from register_page import RegisterPage
from invoice_page import InvoicePage

def main(page: ft.Page):
    page.title = "ManzaFAC"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 700
    page.window_height = 500
    
    # Color scheme
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ft.colors.RED_700,
            secondary=ft.colors.RED_400,
            surface=ft.colors.WHITE,
        )
    )
    
    def route_change(route):
        page.views.clear()
        
        if page.route == "/":
            page.views.append(LoginPage(page))
        elif page.route == "/register":
            page.views.append(RegisterPage(page))
        elif page.route == "/invoice":
            page.views.append(InvoicePage(page))
            
        page.update()

    page.on_route_change = route_change
    page.go('/')

ft.app(target=main) 