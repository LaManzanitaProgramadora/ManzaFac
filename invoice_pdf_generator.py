from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A6
from reportlab.lib import colors
from reportlab.lib.units import cm
import mysql.connector
import os

def get_business_data():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='manzafac',
            user='root',
            password='root'
        )
        
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM negocios ORDER BY id DESC LIMIT 1")
            business_data = cursor.fetchone()
            return business_data
            
    except Exception as e:
        print(f"Error al obtener datos del negocio: {e}")
        return None
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

def generate_invoice_pdf(client_data, invoice_data, products, totals):
    # Obtener datos del negocio
    business_data = get_business_data()
    if not business_data:
        business_data = {
            'business_name': 'ManzaFAC',
            'ruc': 'N/A',
            'address': 'N/A',
            'province': 'N/A'
        }

    # Crear directorio si no existe
    documents_path = os.path.join(os.path.expanduser("~"), "Documents", "ManzaFAC")
    if not os.path.exists(documents_path):
        os.makedirs(documents_path)

    # Generar nombre del archivo usando la identificación del cliente y el número de factura
    filename = os.path.join(
        documents_path, 
        f"Factura_{client_data['identificacion']}_{invoice_data['numero']}.pdf"
    )
    
    # Configurar página A6 con márgenes
    pagesize = A6
    margin = 0.5 * cm
    c = canvas.Canvas(filename, pagesize=pagesize)
    width, height = pagesize
    
    # Función auxiliar para dibujar recuadros
    def draw_box(x, y, w, h):
        c.rect(x, y, w, h)
    
    # Recuadro para información del negocio
    business_box_height = 50
    draw_box(margin, height - margin - business_box_height, width - 2*margin, business_box_height)
    
    # Datos del negocio dentro del recuadro
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margin + 5, height - margin - 12, business_data['business_name'])
    c.setFont("Helvetica", 8)
    c.drawString(margin + 5, height - margin - 22, f"RUC: {business_data['ruc']}")
    c.drawString(margin + 5, height - margin - 32, f"Dir: {business_data['address']}")
    c.drawString(margin + 5, height - margin - 42, f"Provincia: {business_data['province']}")
    
    # Espacio entre recuadros
    y_offset = height - margin - business_box_height - 15
    
    # Recuadro combinado para información de la factura y del cliente
    combined_box_height = 90  # Aumentado de 80 a 90 para dar más espacio
    draw_box(margin, y_offset - combined_box_height, width - 2*margin, combined_box_height)
    
    # Datos de la factura y del cliente dentro del recuadro combinado
    c.setFont("Helvetica", 8)
    c.drawString(margin + 5, y_offset - 12, f"Orden N°: {invoice_data['numero']}")
    c.drawString(margin + 5, y_offset - 22, f"Fecha: {invoice_data['fecha']}")
    c.drawString(margin + 5, y_offset - 32, f"Vendedor: {invoice_data['vendedor']}")
    c.drawString(margin + 5, y_offset - 42, f"Cliente: {client_data['cliente']}")
    c.drawString(margin + 5, y_offset - 52, f"ID: {client_data['identificacion']}")
    c.drawString(margin + 5, y_offset - 62, f"Dir: {client_data['direccion']}")
    c.drawString(margin + 5, y_offset - 72, f"Provincia: {client_data['provincia']}")
    c.drawString(margin + 5, y_offset - 82, f"Ciudad: {client_data['ciudad']}")
    
    # Actualizar offset para la tabla de productos
    y_offset -= (combined_box_height + 15)
    
    # Tabla de productos
    col_widths = [30, 120, 40, 40]  # Anchos de columnas
    row_height = 15
    table_width = sum(col_widths)
    
    # Encabezados de la tabla
    c.setFont("Helvetica-Bold", 8)
    x = margin
    headers = ["Cant.", "Descripción", "Precio", "Total"]
    for i, header in enumerate(headers):
        draw_box(x, y_offset - row_height, col_widths[i], row_height)
        c.drawString(x + 2, y_offset - row_height + 4, header)
        x += col_widths[i]
    
    # Productos
    c.setFont("Helvetica", 8)
    for product in products:
        y_offset -= row_height
        x = margin
        
        # Dibujar celdas y agregar datos
        draw_box(x, y_offset - row_height, col_widths[0], row_height)
        c.drawString(x + 2, y_offset - row_height + 4, str(product['cantidad']))
        x += col_widths[0]
        
        draw_box(x, y_offset - row_height, col_widths[1], row_height)
        descripcion = product['descripcion'][:20] + '...' if len(product['descripcion']) > 20 else product['descripcion']
        c.drawString(x + 2, y_offset - row_height + 4, descripcion)
        x += col_widths[1]
        
        draw_box(x, y_offset - row_height, col_widths[2], row_height)
        c.drawString(x + 2, y_offset - row_height + 4, f"${product['precio']}")
        x += col_widths[2]
        
        draw_box(x, y_offset - row_height, col_widths[3], row_height)
        c.drawString(x + 2, y_offset - row_height + 4, f"${product['total']}")
        
        if product['incluye_iva']:
            c.drawString(x + col_widths[3] - 15, y_offset - row_height + 4, "(I)")
    
    # Espacio para totales
    y_offset -= (row_height + 10)
    
    # Recuadro para totales (separado de la tabla de productos)
    totals_box_width = 100
    totals_x = width - margin - totals_box_width
    
    # Dibujar cada línea de totales en su propia casilla
    c.setFont("Helvetica-Bold", 8)
    items = [
        f"Subtotal: ${totals['subtotal']}",  # Aquí se está incluyendo algo extra
        f"IVA: ${totals['iva']}",
        f"Desc: {totals['descuento']}%",
        f"Total: ${totals['total']}"
    ]
    
    for item in items:
        draw_box(totals_x, y_offset - row_height, totals_box_width, row_height)
        c.drawString(totals_x + 5, y_offset - row_height + 4, item)
        y_offset -= row_height
    
    c.save()
    return filename 