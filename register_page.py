import flet as ft
import mysql.connector
from mysql.connector import Error

class RegisterPage(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.initialize_view()

    def initialize_view(self):
        self.route = "/register"
        self.bgcolor = ft.colors.WHITE
        
        # Configurar tamaño de ventana
        self.page.window_min_width = 800  # Ancho mínimo
        self.page.window_min_height = 600  # Alto mínimo
        self.page.window_width = 1000  # Ancho inicial
        self.page.window_height = 700  # Alto inicial
        self.page.window_resizable = True  # Permitir redimensionar

        def save_to_database(data):
            try:
                connection = mysql.connector.connect(
                    host='localhost',
                    database='manzafac',
                    user='root',
                    password='root'
                )

                if connection.is_connected():
                    cursor = connection.cursor()
                    
                    # Primero verificar si ya existe algún registro
                    cursor.execute("SELECT COUNT(*) FROM negocios")
                    count = cursor.fetchone()[0]
                    
                    if count > 0:
                        self.page.show_snack_bar(
                            ft.SnackBar(content=ft.Text("Ya existe un negocio registrado"))
                        )
                        return "EXISTS"
                    
                    # Si no existe ningún registro, procedemos con la inserción
                    sql = """INSERT INTO negocios 
                            (business_name, ruc, address, province) 
                            VALUES (%s, %s, %s, %s)"""
                    values = (
                        data["business_name"],
                        data["ruc"],
                        data["address"],
                        data["province"]
                    )
                    
                    cursor.execute(sql, values)
                    connection.commit()
                    
                    self.page.show_snack_bar(
                        ft.SnackBar(content=ft.Text("Registro guardado exitosamente"))
                    )
                    return True

            except Error as e:
                self.page.show_snack_bar(
                    ft.SnackBar(content=ft.Text(f"Error de conexión a MySQL: {str(e)}"))
                )
                return False
                
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()

        def register_clicked(e):
            if not self.test_connection():
                self.page.show_snack_bar(
                    ft.SnackBar(content=ft.Text("Error de conexión a la base de datos"))
                )
                return

            # Validar campos vacíos
            empty_fields = []
            if not self.business_name_field.value:
                empty_fields.append("Nombre del Local/Empresa")
            if not self.ruc_field.value:
                empty_fields.append("RUC")
            if not self.address_field.value:
                empty_fields.append("Dirección")
            if not self.province_dropdown.value:
                empty_fields.append("Provincia")

            if empty_fields:
                self.page.show_snack_bar(
                    ft.SnackBar(
                        content=ft.Text(f"Por favor complete los siguientes campos: {', '.join(empty_fields)}")
                    )
                )
                return

            # Validar RUC antes de continuar
            is_valid_ruc, ruc_message = self.validate_ruc(self.ruc_field.value)
            if not is_valid_ruc:
                self.page.show_snack_bar(
                    ft.SnackBar(content=ft.Text(ruc_message))
                )
                return

            # Si todas las validaciones pasan, proceder con el guardado
            data = {
                "business_name": self.business_name_field.value,
                "ruc": self.ruc_field.value,
                "address": self.address_field.value,
                "province": self.province_dropdown.value
            }
            
            result = save_to_database(data)
            
            if result == "EXISTS":
                # Mostrar diálogo de error
                self.page.dialog = ft.AlertDialog(
                    title=ft.Text("Registro no permitido"),
                    content=ft.Text(
                        "Ya existe un negocio registrado en el sistema. "
                        "Esta versión solo permite el registro de un único negocio."
                    ),
                    actions=[
                        ft.TextButton("Entendido", on_click=lambda _: self.page.go("/"))
                    ],
                )
                self.page.dialog.open = True
                self.page.update()
            elif result:
                # Verificar que los datos se guardaron correctamente
                if self.verify_saved_data(data["ruc"]):
                    self.page.show_snack_bar(
                        ft.SnackBar(content=ft.Text("Registro guardado y verificado"))
                    )
                    self.page.go("/")
                else:
                    self.page.show_snack_bar(
                        ft.SnackBar(content=ft.Text("Error al verificar los datos guardados"))
                    )
            else:
                self.page.show_snack_bar(
                    ft.SnackBar(content=ft.Text("Error al guardar los datos"))
                )

        # Lista de provincias de Ecuador
        PROVINCIAS_ECUADOR = [
            "Azuay", "Bolívar", "Cañar", "Carchi", "Chimborazo", "Cotopaxi",
            "El Oro", "Esmeraldas", "Galápagos", "Guayas", "Imbabura", "Loja",
            "Los Ríos", "Manabí", "Morona Santiago", "Napo", "Orellana", "Pastaza",
            "Pichincha", "Santa Elena", "Santo Domingo de los Tsáchilas", 
            "Sucumbíos", "Tungurahua", "Zamora Chinchipe"
        ]

        self.business_name_field = ft.TextField(
            label="Nombre del Local/Empresa",
            border_color=ft.colors.RED_400,
            width=400  # Aumentado de 300 a 400
        )
        
        self.ruc_field = ft.TextField(
            label="RUC",
            border_color=ft.colors.RED_400,
            width=400  # Aumentado de 300 a 400
        )

        self.address_field = ft.TextField(
            label="Dirección del Local",
            border_color=ft.colors.RED_400,
            width=400  # Aumentado de 300 a 400
        )

        self.province_dropdown = ft.Dropdown(
            label="Provincia",
            width=400,  # Aumentado de 300 a 400
            options=[ft.dropdown.Option(provincia) for provincia in PROVINCIAS_ECUADOR],
            border_color=ft.colors.RED_400,
        )

        self.controls = [
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text("Registro de Negocio", 
                               size=40,  # Aumentado de 32 a 40
                               color=ft.colors.RED_700),
                        self.business_name_field,
                        self.ruc_field,
                        self.address_field,
                        self.province_dropdown,
                        ft.Row(
                            controls=[
                                ft.ElevatedButton(
                                    "Guardar",
                                    on_click=register_clicked,
                                    bgcolor=ft.colors.RED_700,
                                    color=ft.colors.WHITE,
                                    width=150  # Añadido ancho al botón
                                ),
                                ft.TextButton(
                                    "Volver",
                                    on_click=lambda _: self.page.go("/"),
                                    width=150  # Añadido ancho al botón
                                )
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=30  # Aumentado el espacio entre botones
                        )
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=30  # Aumentado el espacio entre elementos
                ),
                padding=60,  # Aumentado el padding general
                alignment=ft.alignment.center
            )
        ] 

    def test_connection(self):
        try:
            connection = mysql.connector.connect(
                host='localhost',
                database='manzafac',
                user='root',
                password='root'
            )
            
            if connection.is_connected():
                db_info = connection.get_server_info()
                print(f"Conectado a MySQL Server versión {db_info}")
                
                cursor = connection.cursor()
                cursor.execute("select database();")
                db_name = cursor.fetchone()[0]
                print(f"Conectado a la base de datos: {db_name}")
                
                return True
                
        except Error as e:
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text(f"Error de conexión a MySQL: {str(e)}"))
            )
            return False
            
        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()

    def verify_saved_data(self, ruc):
        try:
            connection = mysql.connector.connect(
                host='localhost',
                database='manzafac',
                user='root',
                password='root'
            )
            
            if connection.is_connected():
                cursor = connection.cursor(dictionary=True)
                
                sql = "SELECT * FROM negocios WHERE ruc = %s"
                cursor.execute(sql, (ruc,))
                
                result = cursor.fetchone()
                if result:
                    print("Datos encontrados:")
                    print(f"Nombre: {result['business_name']}")
                    print(f"RUC: {result['ruc']}")
                    print(f"Dirección: {result['address']}")
                    print(f"Provincia: {result['province']}")
                    return True
                else:
                    self.page.show_snack_bar(
                        ft.SnackBar(content=ft.Text("No se encontraron datos para ese RUC"))
                    )
                    return False
                    
        except Error as e:
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text(f"Error al verificar datos: {str(e)}"))
            )
            return False
            
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def validate_ruc(self, ruc):
        """Valida que el RUC cumpla con las reglas básicas de Ecuador"""
        # Verificar que tenga 13 dígitos y sean solo números
        if not ruc.isdigit() or len(ruc) != 13:
            return False, "El RUC debe tener 13 dígitos numéricos"

        # Verificar que los dos primeros dígitos correspondan a una provincia válida (01-24)
        provincia = int(ruc[:2])
        if provincia < 1 or provincia > 24:
            return False, "Los dos primeros dígitos deben corresponder a una provincia válida (01-24)"

        # Verificar el tercer dígito (tipo de contribuyente)
        tercer_digito = int(ruc[2])
        if tercer_digito not in [6, 9] and tercer_digito < 0 or tercer_digito > 5:
            return False, "El tercer dígito no es válido para un RUC"

        # Validación del dígito verificador para RUC de sociedades (tercer dígito = 9)
        if tercer_digito == 9:
            coeficientes = [4, 3, 2, 7, 6, 5, 4, 3, 2]
            suma = 0
            for i in range(len(coeficientes)):
                suma += int(ruc[i]) * coeficientes[i]
            residuo = suma % 11
            digito_verificador = 11 - residuo if residuo != 0 else 0
            if digito_verificador != int(ruc[9]):
                return False, "El RUC no es válido (dígito verificador incorrecto)"

        return True, "RUC válido"