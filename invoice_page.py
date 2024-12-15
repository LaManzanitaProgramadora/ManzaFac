import flet as ft
import random
from datetime import datetime
from invoice_pdf_generator import generate_invoice_pdf
from login_page import LoginPage

# Movemos ProductRow fuera de la clase InvoicePage
class ProductRow(ft.Container):
    def __init__(self, invoice_page, can_delete=False):
        super().__init__()
        self.invoice_page = invoice_page
        self.quantity = ft.TextField(
            width=100,
            label="Cantidad",
            border_color=ft.colors.RED_400,
            on_change=self.validate_positive_number,
            hint_text="0",
            input_filter=ft.NumbersOnlyInputFilter()
        )
        self.description = ft.TextField(
            width=200,
            label="Descripción",
            border_color=ft.colors.RED_400
        )
        self.unit_price = ft.TextField(
            width=100,
            label="Precio",
            border_color=ft.colors.RED_400,
            on_change=self.validate_price,
            hint_text="0.00",
        )
        self.include_tax = ft.Checkbox(
            label="IVA 15%",
            value=False
        )
        self.total = ft.Text("0.00")
        
        controls_list = [
            self.quantity,
            self.description,
            self.unit_price,
            self.include_tax,
            self.total
        ]
        
        if can_delete:
            self.delete_button = ft.IconButton(
                icon=ft.icons.DELETE,
                icon_color=ft.colors.RED_400,
                on_click=self.delete_row
            )
            controls_list.append(self.delete_button)
        
        self.content = ft.Row(
            controls=controls_list,
            spacing=10
        )
    
    def delete_row(self, e):
        # Llamar al método de la página principal para eliminar esta fila
        self.invoice_page.delete_product_row(self)
    
    def validate_positive_number(self, e):
        """Validar que el valor ingresado sea un número positivo"""
        field = e.control
        try:
            # Permitir campo vacío
            if not field.value:
                field.border_color = ft.colors.RED_400
                return

            value = float(field.value)
            if value < 0:
                field.value = "0"
                field.border_color = ft.colors.RED_400
                self.invoice_page.page.show_snack_bar(
                    ft.SnackBar(content=ft.Text("No se permiten valores negativos"))
                )
            else:
                field.border_color = ft.colors.GREEN_400
        except ValueError:
            field.value = "0"
            field.border_color = ft.colors.RED_400
            self.invoice_page.page.show_snack_bar(
                ft.SnackBar(content=ft.Text("Por favor ingrese un número válido"))
            )
        finally:
            self.invoice_page.calculate_totals(None)
            self.invoice_page.update()

    def validate_price(self, e):
        """Validar que el precio tenga máximo dos decimales y sea positivo"""
        field = e.control
        try:
            # Permitir campo vacío
            if not field.value:
                field.border_color = ft.colors.RED_400
                return

            # Remover cualquier caracter que no sea número o punto
            value = ''.join(c for c in field.value if c.isdigit() or c == '.')
            
            # Asegurar que solo haya un punto decimal
            if value.count('.') > 1:
                value = value.replace('.', '', value.count('.') - 1)
            
            # Si hay punto decimal, limitar a dos decimales
            if '.' in value:
                integer_part, decimal_part = value.split('.')
                decimal_part = decimal_part[:2]  # Limitar a dos decimales
                value = f"{integer_part}.{decimal_part}"
            
            # Convertir a float para validar
            price = float(value)
            
            if price < 0:
                field.value = "0.00"
                field.border_color = ft.colors.RED_400
                self.invoice_page.page.show_snack_bar(
                    ft.SnackBar(content=ft.Text("No se permiten valores negativos"))
                )
            else:
                field.value = value  # Actualizar el campo con el valor formateado
                field.border_color = ft.colors.GREEN_400
        except ValueError:
            field.value = "0.00"
            field.border_color = ft.colors.RED_400
            self.invoice_page.page.show_snack_bar(
                ft.SnackBar(content=ft.Text("Por favor ingrese un número válido"))
            )
        finally:
            self.invoice_page.calculate_totals(None)
            self.invoice_page.update()

class InvoicePage(ft.View):
    def __init__(self, page):
        super().__init__()
        self.page = page
        
        # Mapeo de provincias a ciudades
        self.province_to_cities = {
            "Pichincha": ["Quito", "Cayambe", "Rumiñahui", "Mejía", "Pedro Vicente Maldonado", "San Miguel de los Bancos", "Puerto Quito"],
"Azuay": ["Cuenca", "Girón", "Paute", "Azogues", "Biblián", "Chordeleg", "El Pan", "La Troncal", "San Fernando", "Santa Isabel"],
"Bolívar": ["Guaranda", "Chillanes", "Echeandía", "Las Naves", "San Miguel", "Santiago de los Andes"],
"Carchi": ["Tulcán", "Bolívar", "Espejo", "Montúfar", "Mataje", "El Chical", "San Gabriel"],
"Cañar": ["Azogues", "Biblián", "La Troncal", "Cañar", "La Paz", "El Tambo", "Deleg", "Chanchán"],
"Chimborazo": ["Riobamba", "Alausí", "Chanchán", "Guano", "Colta", "Penipe", "Ficoa"],
"Cotopaxi": ["Latacunga", "Salcedo", "La Maná", "Pangua", "Pujilí", "Sigchos", "Rumiñahui"],
"El oro": ["Machala", "Pasaje", "Zaruma", "Arenillas", "Balsas", "Chilla", "El Guabo", "Piñas", "Santa Rosa"],
"Esmeraldas": ["Esmeraldas", "Atacames", "Muisne", "Río Verde", "Tonchigüe", "Santiago", "La Tola", "Mompiche"],
"Guayas": ["Guayaquil", "Samborondón", "Durán", "Balao", "Balzar", "Naranjal", "Playas", "General Villamil", "Daule", "Yaguachi"],
"Imbabura": ["Ibarra", "Otavalo", "Cotacachi", "Antonio Ante", "Urcuquí", "San Gabriel", "La Esperanza", "Mira"],
"Loja": ["Loja", "Catamayo", "Cariamanga", "Zamora", "Pindal", "Chinchipe", "Cañas", "Macar", "Saraguro"],
"Los ríos": ["Babahoyo", "Quevedo", "Vinces", "Montalvo", "Ventanas", "Valencia", "Urdaneta", "Palestina"],
"Manabí": ["Portoviejo", "Manta", "Chone", "Jama", "Jipijapa", "El Carmen", "Pedernales", "Puerto López", "Montecristi", "Bahía de Caráquez"],
"Morona-santiago": ["Macas", "Sucúa", "Gualaquiza", "Tiwintza", "Huaquillas", "San Juan Bosco", "Puyo", "Río Blanco"],
"Napo": ["Tena", "Archidona", "El Chaco", "Baeza", "Quijos", "Carlos Julio Arosemena Tola", "Santa Clara"],
"Oriente": ["Shushufindi", "Coca", "La Joya de los Sachas", "Sucumbíos", "Nueva Loja", "Canton Lago Agrio"],
"Pastaza": ["Puyo", "Mera", "Arajuno", "Tena", "Santa Clara", "Puyo"],
"Tungurahua": ["Ambato", "Baños", "Patate", "Cevallos", "Mocha", "Totorillas", "Pelileo", "Quero", "Pillaro"],
"Zamora-chinchipe": ["Zamora", "Loja", "Yantzaza", "Centinela del Cóndor", "Chinchipe", "El Pangui", "Pindal", "Cariamanga"],
"Morona-santiago": ["Macas", "Sucúa", "Gualaquiza", "Tiwintza", "San Juan Bosco", "Puyo", "Río Blanco"],
"Carchi": ["Tulcán", "Bolívar", "Espejo", "Montúfar", "Mataje", "El Chical", "San Gabriel"],
"Galápagos": ["Puerto Ayora", "Puerto Baquerizo Moreno", "Isabela", "San Cristóbal", "Floreana"],
"Cotopaxi": ["Latacunga", "Salcedo", "La Maná", "Pangua", "Pujilí", "Sigchos", "Rumiñahui"]
            # Agrega más provincias y ciudades según sea necesario
        }

        # Inicializar el campo de provincia
        self.province_dropdown = ft.Dropdown(
            label="Provincia",
            width=300,
            options=[ft.dropdown.Option(text=prov) for prov in self.province_to_cities.keys()],
            on_change=self.province_selected
        )

        # Inicializar el campo de ciudad (inicialmente oculto)
        self.city_dropdown = ft.Dropdown(
            label="Ciudad",
            width=300,
            options=[],
            visible=False  # Oculto inicialmente
        )
        
        # Configurar ventana inicial
        self.page.window_min_width = 1000
        self.page.window_min_height = 650
        self.page.window_width = 1200
        self.page.window_height = 750
        self.page.window_resizable = True
        self.page.auto_scroll = True  # Habilitar scroll automático
        
        # Inicializar DatePicker
        self.date_picker = ft.DatePicker(
            on_change=self.change_date,
            first_date=datetime(2020, 1, 1),
            last_date=datetime(2030, 12, 31)
        )
        self.page.overlay.append(self.date_picker)
        
        # Inicializar el campo de fecha
        self.date_field = ft.TextField(
            label="Fecha",
            width=200,
            border_color=ft.colors.RED_400,
            read_only=True
        )
        
        # Inicializar el menú como atributo de clase
        self.menu = ft.PopupMenuButton(
            items=[
                ft.PopupMenuItem(text="Nueva factura", on_click=self.new_invoice),
                ft.PopupMenuItem(text="Generar PDF", on_click=self.generate_pdf),
                ft.PopupMenuItem(text="Cerrar programa", on_click=self.close_app),
            ]
        )
        
        # Inicializar products_list antes de cualquier otra cosa
        self.products_list = ft.Column(spacing=10)
        
        self.initialize_view()

    def change_date(self, e):
        """Actualizar el campo de fecha cuando se seleccione una nueva fecha"""
        if hasattr(e, 'control') and e.control == self.date_picker:
            selected_date = e.control.value
            if selected_date:
                self.date_field.value = selected_date.strftime("%Y-%m-%d")
                self.update()

    def initialize_view(self):
        self.route = "/invoice"
        self.bgcolor = ft.colors.WHITE
        
        # Generar código único de factura (8 dígitos)
        invoice_code = str(random.randint(10000000, 99999999))
        
        # Establecer la fecha actual en el campo de fecha
        self.date_field.value = datetime.now().strftime("%Y-%m-%d")
        
        # Header section
        self.header = ft.Container(
            content=ft.Column([
                ft.Row([
                    self.menu,
                    ft.Text("ManzaFAC - Facturación", 
                           size=32,
                           color=ft.colors.RED_700)
                ]),
                
                # Información del cliente - lado izquierdo
                ft.Row([
                    # Columna izquierda - datos del cliente
                    ft.Column([
                        ft.TextField(
                            label="Cliente",
                            width=300,
                            border_color=ft.colors.RED_400
                        ),
                        ft.TextField(
                            label="Identificación (Cédula/RUC)",
                            width=300,
                            border_color=ft.colors.RED_400,
                            on_blur=self.validate_identification_field
                        ),
                        ft.TextField(
                            label="Dirección",
                            width=300,
                            border_color=ft.colors.RED_400
                        ),
                        self.province_dropdown,  # Campo de provincia
                        self.city_dropdown,      # Campo de ciudad
                    ]),
                    
                    # Espaciador
                    ft.Container(width=40),
                    
                    # Columna derecha - datos de la factura
                    ft.Column([
                        ft.TextField(
                            label="N° Factura",
                            value=invoice_code,
                            width=200,
                            read_only=True,
                            border_color=ft.colors.RED_400
                        ),
                        ft.Row([
                            self.date_field,
                            ft.IconButton(
                                icon=ft.icons.CALENDAR_TODAY,
                                on_click=lambda _: self.date_picker.pick_date()
                            )
                        ]),
                        ft.TextField(
                            label="Vendedor",
                            width=200,
                            border_color=ft.colors.RED_400
                        ),
                    ]),
                ], alignment=ft.MainAxisAlignment.START),
            ])
        )

        # Products section
        self.add_product_row()

        # Totals section
        self.subtotal = ft.Text("Subtotal: $0.00")
        self.tax = ft.Text("IVA (15%): $0.00")
        self.total = ft.Text("Total: $0.00")

        # Sección de descuento
        self.discount = ft.TextField(
            label="Descuento %",
            width=100,
            value="0",
            hint_text="0-100",
            on_change=self.validate_discount,
            input_filter=ft.NumbersOnlyInputFilter()
        )
        
        # Reorganización de botones y totales
        buttons_column = ft.Column([
            ft.ElevatedButton(
                "Agregar Producto",
                on_click=lambda _: self.add_product_row(),
                bgcolor=ft.colors.RED_700,
                color=ft.colors.WHITE
            ),
            ft.ElevatedButton(
                "Calcular",
                on_click=self.calculate_totals,
                bgcolor=ft.colors.RED_700,
                color=ft.colors.WHITE
            ),
        ])
        
        totals_column = ft.Column([
            self.subtotal,
            self.tax,
            self.total
        ], alignment=ft.MainAxisAlignment.END)
        
        footer_row = ft.Row([
            buttons_column,
            ft.Column([
                ft.Text("Descuento:"),
                self.discount
            ]),
            totals_column
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        # Modificar la sección de productos para tener una altura máxima
        products_container = ft.Container(
            content=ft.Column(
                controls=[self.products_list],
                scroll=ft.ScrollMode.AUTO,  # El scroll va en el Column, no en el Container
                spacing=10,
            ),
            height=240,  # Altura para 4 productos (60px cada uno)
            border=ft.border.all(1, ft.colors.BLACK12),
            border_radius=10
        )

        # Modificar la estructura del contenedor principal
        self.controls = [
            ft.Container(
                content=ft.Column([
                    self.header,
                    ft.Divider(),
                    products_container,  # Usar el nuevo contenedor de productos
                    footer_row
                ]),
                padding=40
            )
        ]

    def add_product_row(self):
        """Método para añadir una nueva fila de producto"""
        # Verificar si ya hay 8 productos
        if len(self.products_list.controls) >= 8:
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text("No se pueden agregar más de 8 productos"))
            )
            return
        
        can_delete = len(self.products_list.controls) > 0
        new_row = ProductRow(self, can_delete=can_delete)
        self.products_list.controls.append(new_row)
        self.adjust_window_size()
        self.update()

    def new_invoice(self, e):
        # Limpiar productos
        self.products_list.controls = []
        self.add_product_row()
        
        # Limpiar campos del cliente
        client_fields = self.header.content.controls[1].controls[0].controls
        for field in client_fields:
            field.value = ""
        
        # Limpiar campo del vendedor
        self.header.content.controls[1].controls[2].controls[2].value = ""
        
        # Generar nuevo número de factura
        new_invoice_code = str(random.randint(10000000, 99999999))
        self.header.content.controls[1].controls[2].controls[0].value = new_invoice_code
        
        # Establecer la fecha actual en lugar de dejarla en blanco
        self.date_field.value = datetime.now().strftime("%Y-%m-%d")
        
        # Limpiar totales y descuento
        self.discount.value = "0"
        self.calculate_totals(None)
        
        # Resetear altura de la ventana
        self.page.window_height = 800
        
        self.update()

    def close_app(self, e):
        self.page.window_close()

    def generate_pdf(self, e):
        """Genera un PDF de la factura actual"""
        # Recopilar datos del cliente
        client_data = {
            "cliente": self.header.content.controls[1].controls[0].controls[0].value,
            "identificacion": self.header.content.controls[1].controls[0].controls[1].value,
            "direccion": self.header.content.controls[1].controls[0].controls[2].value,
            "provincia": self.province_dropdown.value,  # Acceder al valor del Dropdown
            "ciudad": self.city_dropdown.value if self.city_dropdown.visible else ""  # Incluir la ciudad si está visible
        }
        
        # Recopilar datos de la factura
        invoice_data = {
            "numero": self.header.content.controls[1].controls[2].controls[0].value,
            "fecha": self.date_field.value,
            "vendedor": self.header.content.controls[1].controls[2].controls[2].value,
        }
        
        # Recopilar productos
        products = []
        for product_row in self.products_list.controls:
            products.append({
                "cantidad": product_row.quantity.value,
                "descripcion": product_row.description.value,
                "precio": product_row.unit_price.value,
                "incluye_iva": product_row.include_tax.value,
                "total": product_row.total.value.replace("$", "")
            })
        
        # Recopilar totales
        totals = {
            "subtotal": self.subtotal.value.split("$")[1],
            "iva": self.tax.value.split("$")[1],
            "descuento": self.discount.value,
            "total": self.total.value.split("$")[1]
        }
        
        try:
            # Llamar al generador de PDF
            generate_invoice_pdf(
                client_data=client_data,
                invoice_data=invoice_data,
                products=products,
                totals=totals
            )
            # Mostrar mensaje de éxito
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text("PDF generado exitosamente"))
            )
        except Exception as e:
            # Mostrar mensaje de error
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text(f"Error al generar PDF: {str(e)}"))
            )
        
        self.update()

    def calculate_totals(self, e):
        """Calcular totales en el orden correcto:
        1. Aplicar descuento a cada producto
        2. Calcular IVA sobre productos marcados (después del descuento)
        3. Mostrar subtotal (suma de productos con descuento)
        4. Mostrar total (subtotal + IVA)
        """
        subtotal = 0
        total_iva = 0
        
        try:
            discount_percent = float(self.discount.value or 0)
            discount_percent = max(0, min(100, discount_percent))  # Limitar entre 0 y 100
        except ValueError:
            discount_percent = 0

        # Calcular para cada producto
        for product in self.products_list.controls:
            try:
                if not product.quantity.value or not product.unit_price.value:
                    continue

                quantity = float(product.quantity.value)
                price = float(product.unit_price.value)

                if quantity < 0 or price < 0:
                    continue

                # 1. Calcular precio base de la línea
                line_total = quantity * price

                # 2. Aplicar descuento si existe
                if discount_percent > 0:
                    discount_amount = line_total * (discount_percent / 100)
                    line_total_with_discount = line_total - discount_amount
                else:
                    line_total_with_discount = line_total

                # 3. Calcular IVA si el producto está marcado (sobre el monto con descuento)
                if product.include_tax.value:
                    iva_producto = line_total_with_discount * 0.15
                    total_iva += iva_producto
                
                # Actualizar el total mostrado en la línea del producto
                product.total.value = f"${line_total_with_discount:.2f}"
                
                # Agregar al subtotal
                subtotal += line_total_with_discount

            except ValueError:
                continue

        # Calcular total final (subtotal + IVA)
        total = subtotal + total_iva

        # Actualizar los valores mostrados
        self.subtotal.value = f"Subtotal: ${subtotal:.2f}"
        self.tax.value = f"IVA (15%): ${total_iva:.2f}"
        self.total.value = f"Total: ${total:.2f}"

        self.update()

    def delete_product_row(self, row):
        """Método para eliminar una fila de producto"""
        if row in self.products_list.controls:
            self.products_list.controls.remove(row)
            self.calculate_totals(None)
            self.adjust_window_size()
            self.update()

    def adjust_window_size(self):
        # Mantener una altura fija para la ventana
        self.page.window_height = 900
        self.page.update()

    def validate_identification(self, identification):
        """Valida cédula o RUC ecuatoriano"""
        if not identification.isdigit():
            return False, "La identificación debe contener solo números"
            
        length = len(identification)
        if length not in [10, 13]:
            return False, "La identificación debe tener 10 dígitos (cédula) o 13 dígitos (RUC)"
            
        # Validar provincia (primeros 2 dígitos)
        provincia = int(identification[:2])
        if provincia < 1 or provincia > 24:
            return False, "Los dos primeros dígitos deben corresponder a una provincia válida (01-24)"

        # Validar tercer dígito
        tercer_digito = int(identification[2])
        
        if length == 10:  # Cédula
            if tercer_digito > 5:
                return False, "El tercer dígito de la cédula debe ser menor a 6"
                
            # Algoritmo validación cédula
            coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
            suma = 0
            for i in range(9):
                valor = int(identification[i]) * coeficientes[i]
                suma += valor if valor < 10 else valor - 9
                
            verificador = 0 if (suma % 10 == 0) else 10 - (suma % 10)
            if verificador != int(identification[9]):
                return False, "Número de cédula no válido (dígito verificador incorrecto)"
                
            return True, "Cédula válida"
            
        else:  # RUC (13 dígitos)
            if tercer_digito == 6:  # RUC Público
                coeficientes = [3, 2, 7, 6, 5, 4, 3, 2]
                suma = 0
                for i in range(8):
                    suma += int(identification[i]) * coeficientes[i]
                residuo = suma % 11
                verificador = 11 - residuo if residuo != 0 else 0
                if verificador != int(identification[8]):
                    return False, "RUC público no válido"
                    
            elif tercer_digito == 9:  # RUC Jurídico
                coeficientes = [4, 3, 2, 7, 6, 5, 4, 3, 2]
                suma = 0
                for i in range(9):
                    suma += int(identification[i]) * coeficientes[i]
                residuo = suma % 11
                verificador = 11 - residuo if residuo != 0 else 0
                if verificador != int(identification[9]):
                    return False, "RUC jurídico no válido"
                    
            elif tercer_digito < 6:  # RUC Natural
                # Validar primero como cédula (primeros 10 dígitos)
                is_valid_cedula, mensaje = self.validate_identification(identification[:10])
                if not is_valid_cedula:
                    return False, "RUC persona natural no válido"
            else:
                return False, "Tipo de RUC no válido"
                
            # Validar que los últimos dígitos del RUC sean 001
            if identification[-3:] != "001":
                return False, "Los últimos 3 dígitos del RUC deben ser 001"
                
            return True, "RUC válido"

    def validate_identification_field(self, e):
        """Validar el campo de identificación cuando pierde el foco"""
        # Obtener el campo de identificación directamente del evento
        identification_field = e.control
        
        if identification_field.value:
            is_valid, message = self.validate_identification(identification_field.value)
            if not is_valid:
                identification_field.border_color = ft.colors.RED_400
                self.page.show_snack_bar(
                    ft.SnackBar(content=ft.Text(message))
                )
            else:
                identification_field.border_color = ft.colors.GREEN_400
            self.update()

    def province_selected(self, e):
        """Mostrar el campo de ciudad con las opciones correspondientes a la provincia seleccionada"""
        selected_province = self.province_dropdown.value
        if selected_province in self.province_to_cities:
            cities = self.province_to_cities[selected_province]
            self.city_dropdown.options = [ft.dropdown.Option(text=city) for city in cities]
            self.city_dropdown.visible = True
        else:
            self.city_dropdown.visible = False

        self.update()

    def validate_discount(self, e):
        """Validar que el descuento sea un número entre 0 y 100"""
        try:
            # Permitir campo vacío
            if not self.discount.value:
                self.discount.value = "0"
                self.discount.border_color = ft.colors.RED_400
                return

            value = float(self.discount.value)
            if value < 0:
                self.discount.value = "0"
                self.discount.border_color = ft.colors.RED_400
                self.page.show_snack_bar(
                    ft.SnackBar(content=ft.Text("El descuento no puede ser negativo"))
                )
            elif value > 100:
                self.discount.value = "100"
                self.discount.border_color = ft.colors.RED_400
                self.page.show_snack_bar(
                    ft.SnackBar(content=ft.Text("El descuento no puede ser mayor a 100%"))
                )
            else:
                self.discount.border_color = ft.colors.GREEN_400
        except ValueError:
            self.discount.value = "0"
            self.discount.border_color = ft.colors.RED_400
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text("Por favor ingrese un número válido"))
            )
        finally:
            self.calculate_totals(None)
            self.update()