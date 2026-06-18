from proveedores.models import Proveedor

def run():
    proveedores_data = [
        {
            'nombre': 'Distribuidora Central', 'razon_social': 'Distribuidora Central S.A. de C.V.', 'rfc': 'DIC123456789',
            'contacto': 'Juan Pérez', 'telefono': '5551234567', 'email': 'contacto@distribuidoracentral.com',
            'direccion': 'Av. Reforma 123', 'ciudad': 'CDMX', 'estado': 'CDMX', 'pais': 'México', 'codigo_postal': '01000', 'tipo': 'Nacional', 'sitio_web': 'https://distribuidoracentral.com', 'activo': True
        },
        {
            'nombre': 'Proveedora del Norte', 'razon_social': 'Proveedora del Norte S.A.', 'rfc': 'PRN987654321',
            'contacto': 'Ana Gómez', 'telefono': '8187654321', 'email': 'ventas@proveedoranorte.com',
            'direccion': 'Calle Hidalgo 456', 'ciudad': 'Monterrey', 'estado': 'Nuevo León', 'pais': 'México', 'codigo_postal': '64000', 'tipo': 'Nacional', 'sitio_web': '', 'activo': True
        },
        {
            'nombre': 'Importaciones Globales', 'razon_social': 'Importaciones Globales Ltd.', 'rfc': 'IML112233445',
            'contacto': 'Carlos Ruiz', 'telefono': '3331122334', 'email': 'info@importglobal.com',
            'direccion': 'Av. Patria 789', 'ciudad': 'Guadalajara', 'estado': 'Jalisco', 'pais': 'México', 'codigo_postal': '44100', 'tipo': 'Extranjero', 'sitio_web': 'https://importglobal.com', 'activo': True
        },
        {
            'nombre': 'Suministros Industriales', 'razon_social': 'Suministros Industriales y Más S.A.', 'rfc': 'SUM556677889',
            'contacto': 'María López', 'telefono': '5559988776', 'email': 'ml@suministros.com',
            'direccion': 'Insurgentes Sur 321', 'ciudad': 'CDMX', 'estado': 'CDMX', 'pais': 'México', 'codigo_postal': '03100', 'tipo': 'Nacional', 'sitio_web': '', 'activo': True
        },
        {
            'nombre': 'Papelería Express', 'razon_social': 'Papelería Express S.A.', 'rfc': 'PAP223344556',
            'contacto': 'Luis Martínez', 'telefono': '5553344556', 'email': 'ventas@papeleriaexpress.com',
            'direccion': 'Av. Juárez 654', 'ciudad': 'Puebla', 'estado': 'Puebla', 'pais': 'México', 'codigo_postal': '72000', 'tipo': 'Nacional', 'sitio_web': '', 'activo': True
        },
        {
            'nombre': 'Químicos del Bajío', 'razon_social': 'Químicos del Bajío S.A.', 'rfc': 'QUI667788990',
            'contacto': 'Patricia Torres', 'telefono': '4771234567', 'email': 'contacto@quimicosbajio.com',
            'direccion': 'Blvd. Campestre 100', 'ciudad': 'León', 'estado': 'Guanajuato', 'pais': 'México', 'codigo_postal': '37150', 'tipo': 'Nacional', 'sitio_web': '', 'activo': True
        },
        {
            'nombre': 'Tecnología Avanzada', 'razon_social': 'Tecnología Avanzada S.A.', 'rfc': 'TEC998877665',
            'contacto': 'Ricardo Díaz', 'telefono': '5557766554', 'email': 'rdiaz@tecavanzada.com',
            'direccion': 'Av. Universidad 200', 'ciudad': 'CDMX', 'estado': 'CDMX', 'pais': 'México', 'codigo_postal': '04360', 'tipo': 'Nacional', 'sitio_web': 'https://tecavanzada.com', 'activo': True
        },
        {
            'nombre': 'Alimentos Selectos', 'razon_social': 'Alimentos Selectos S.A.', 'rfc': 'ALI334455667',
            'contacto': 'Gabriela Ramírez', 'telefono': '5552233445', 'email': 'ventas@alimentosselectos.com',
            'direccion': 'Calle 5 de Mayo 123', 'ciudad': 'Toluca', 'estado': 'Edo. de México', 'pais': 'México', 'codigo_postal': '50000', 'tipo': 'Nacional', 'sitio_web': '', 'activo': True
        },
        {
            'nombre': 'Servicios Médicos Integrales', 'razon_social': 'Servicios Médicos Integrales S.A.', 'rfc': 'SMI445566778',
            'contacto': 'Enrique Salas', 'telefono': '5556677889', 'email': 'contacto@serviciosmedicos.com',
            'direccion': 'Av. Morelos 321', 'ciudad': 'Cuernavaca', 'estado': 'Morelos', 'pais': 'México', 'codigo_postal': '62000', 'tipo': 'Nacional', 'sitio_web': '', 'activo': True
        },
        {
            'nombre': 'Ferretería Moderna', 'razon_social': 'Ferretería Moderna S.A.', 'rfc': 'FER556677889',
            'contacto': 'Sofía Herrera', 'telefono': '5558899776', 'email': 'ventas@ferreteriamoderna.com',
            'direccion': 'Av. Central 456', 'ciudad': 'Querétaro', 'estado': 'Querétaro', 'pais': 'México', 'codigo_postal': '76000', 'tipo': 'Nacional', 'sitio_web': '', 'activo': True
        },
    ]
    for data in proveedores_data:
        Proveedor.objects.create(**data)
    print('10 proveedores creados')
