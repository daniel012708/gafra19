from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from clientes.models import Cliente
from inventario.models import MateriaPrima, MovimientoMateriaPrima
from produccion.models import OrdenProduccion, ProduccionDiaria
from productos.models import Categoria, IngredienteReceta, Producto, ProductoMovimiento, Receta
from proveedores.models import Proveedor
from usuario.models import Usuario
from ventas.models import DetalleVenta, Venta


class Command(BaseCommand):
    help = 'Agrega 5 registros extra por modulo con datos reales para una distribuidora de productos de bebe.'

    @transaction.atomic
    def handle(self, *args, **options):
        summary = {
            'usuarios': 0,
            'clientes': 0,
            'proveedores': 0,
            'materias_primas': 0,
            'productos': 0,
            'ventas': 0,
            'ordenes_produccion': 0,
            'producciones_diarias': 0,
        }

        providers = self.create_providers(summary)
        materials = self.create_materials(providers, summary)
        products = self.create_products(materials, summary)
        users = self.create_users(summary)
        clients = self.create_clients(summary)
        self.create_sales(products, clients, users, summary)
        self.create_production(products, users, summary)

        self.stdout.write(self.style.SUCCESS('Registros extra para distribuidora de bebe creados correctamente.'))
        for key, value in summary.items():
            self.stdout.write(f'{key}: {value}')

    def create_users(self, summary):
        users_data = [
            {
                'username': 'admin_bebe_01',
                'email': 'gerencia@bebemovil.com',
                'password': 'BebeAdmin2026!01',
                'first_name': 'Veronica',
                'last_name': 'Paredes',
                'rol': 'admin',
                'telefono': '3105550101',
                'is_staff': True,
                'is_superuser': True,
            },
            {
                'username': 'cliente_bebe_01',
                'email': 'daniela.rojas@familianova.com',
                'password': 'BebeCliente2026!01',
                'first_name': 'Daniela',
                'last_name': 'Rojas',
                'rol': 'cliente',
                'telefono': '3205550102',
                'is_staff': False,
                'is_superuser': False,
            },
            {
                'username': 'cliente_bebe_02',
                'email': 'nicolas.mejia@hogarfeliz.com',
                'password': 'BebeCliente2026!02',
                'first_name': 'Nicolas',
                'last_name': 'Mejia',
                'rol': 'cliente',
                'telefono': '3205550103',
                'is_staff': False,
                'is_superuser': False,
            },
            {
                'username': 'logistica_bebe_01',
                'email': 'logistica.norte@bebemovil.com',
                'password': 'BebeLog2026!01',
                'first_name': 'Paula',
                'last_name': 'Mendoza',
                'rol': 'logistica',
                'telefono': '3155550104',
                'is_staff': True,
                'is_superuser': False,
            },
            {
                'username': 'logistica_bebe_02',
                'email': 'despachos@bebemovil.com',
                'password': 'BebeLog2026!02',
                'first_name': 'Javier',
                'last_name': 'Caro',
                'rol': 'logistica',
                'telefono': '3155550105',
                'is_staff': True,
                'is_superuser': False,
            },
        ]
        created_users = []
        for data in users_data:
            user, created = User.objects.get_or_create(username=data['username'], defaults={'email': data['email']})
            user.email = data['email']
            user.first_name = data['first_name']
            user.last_name = data['last_name']
            user.is_active = True
            user.is_staff = data['is_staff']
            user.is_superuser = data['is_superuser']
            user.set_password(data['password'])
            user.save()
            Usuario.objects.update_or_create(
                user=user,
                defaults={
                    'rol': data['rol'],
                    'telefono': data['telefono'],
                    'activo': True,
                },
            )
            created_users.append(user)
            if created:
                summary['usuarios'] += 1
        return created_users

    def create_clients(self, summary):
        clients_data = [
            ('Daniela Rojas', 'CC12004501', 'Cra 18 # 104-32, Bogota', '3205551101', 'daniela.rojas@familianova.com'),
            ('Nicolas Mejia', 'CC12004502', 'Calle 9 # 44-10, Medellin', '3205551102', 'nicolas.mejia@hogarfeliz.com'),
            ('Sara Villamil', 'CC12004503', 'Av. 6N # 28-90, Cali', '3205551103', 'sara.villamil@mamapractica.com'),
            ('Laura Benitez', 'CC12004504', 'Cra 52 # 76-18, Barranquilla', '3205551104', 'laura.benitez@casapequena.com'),
            ('Felipe Urrego', 'CC12004505', 'Calle 35 # 19-44, Bucaramanga', '3205551105', 'felipe.urrego@pequeshop.com'),
        ]
        clients = []
        for nombre, documento, direccion, telefono, email in clients_data:
            client, created = Cliente.objects.update_or_create(
                email=email,
                defaults={
                    'nombre': nombre,
                    'documento': documento,
                    'direccion': direccion,
                    'telefono': telefono,
                },
            )
            clients.append(client)
            if created:
                summary['clientes'] += 1
        return clients

    def create_providers(self, summary):
        providers_data = [
            {
                'nombre': 'BabyRide Components',
                'razon_social': 'BabyRide Components SAS',
                'rfc': 'BRC202600001',
                'contacto': 'Andrea Salas',
                'telefono': '6015552201',
                'email': 'andrea.salas@babyridecomponents.com',
                'direccion': 'Parque Industrial Norte Bodega 12',
                'ciudad': 'Bogota',
                'estado': 'Cundinamarca',
                'pais': 'Colombia',
                'codigo_postal': '111111',
                'tipo': 'Nacional',
                'sitio_web': 'https://babyridecomponents.com',
            },
            {
                'nombre': 'Colchones Infantiles Andinos',
                'razon_social': 'Colchones Infantiles Andinos LTDA',
                'rfc': 'CIA202600002',
                'contacto': 'Mauricio Prieto',
                'telefono': '6045552202',
                'email': 'mauricio.prieto@colchonesandinos.com',
                'direccion': 'Zona Franca Sur Local 8',
                'ciudad': 'Medellin',
                'estado': 'Antioquia',
                'pais': 'Colombia',
                'codigo_postal': '050021',
                'tipo': 'Nacional',
                'sitio_web': 'https://colchonesandinos.com',
            },
            {
                'nombre': 'Bosque Kids Woodworks',
                'razon_social': 'Bosque Kids Woodworks SAS',
                'rfc': 'BKW202600003',
                'contacto': 'Camilo Forero',
                'telefono': '6025552203',
                'email': 'camilo.forero@bosquekids.com',
                'direccion': 'Carrera 48 # 23-88',
                'ciudad': 'Cali',
                'estado': 'Valle del Cauca',
                'pais': 'Colombia',
                'codigo_postal': '760001',
                'tipo': 'Nacional',
                'sitio_web': 'https://bosquekids.com',
            },
            {
                'nombre': 'Textiles Sueno Bebe',
                'razon_social': 'Textiles Sueno Bebe SAS',
                'rfc': 'TSB202600004',
                'contacto': 'Martha Acevedo',
                'telefono': '6055552204',
                'email': 'martha.acevedo@textilessuenobebe.com',
                'direccion': 'Via 40 Parque Logistico 6',
                'ciudad': 'Barranquilla',
                'estado': 'Atlantico',
                'pais': 'Colombia',
                'codigo_postal': '080001',
                'tipo': 'Nacional',
                'sitio_web': 'https://textilessuenobebe.com',
            },
            {
                'nombre': 'Ruedas EVA Premium',
                'razon_social': 'Ruedas EVA Premium SAS',
                'rfc': 'REP202600005',
                'contacto': 'Sebastian Naranjo',
                'telefono': '6075552205',
                'email': 'sebastian.naranjo@ruedaseva.com',
                'direccion': 'Anillo Vial Km 3 Centro Empresarial',
                'ciudad': 'Bucaramanga',
                'estado': 'Santander',
                'pais': 'Colombia',
                'codigo_postal': '680001',
                'tipo': 'Nacional',
                'sitio_web': 'https://ruedaseva.com',
            },
        ]
        providers = []
        for data in providers_data:
            provider, created = Proveedor.objects.update_or_create(
                nombre=data['nombre'],
                defaults={
                    'razon_social': data['razon_social'],
                    'rfc': data['rfc'],
                    'contacto': data['contacto'],
                    'telefono': data['telefono'],
                    'email': data['email'],
                    'direccion': data['direccion'],
                    'ciudad': data['ciudad'],
                    'estado': data['estado'],
                    'pais': data['pais'],
                    'codigo_postal': data['codigo_postal'],
                    'tipo': data['tipo'],
                    'sitio_web': data['sitio_web'],
                    'activo': True,
                },
            )
            providers.append(provider)
            if created:
                summary['proveedores'] += 1
        return providers

    def create_materials(self, providers, summary):
        materials_data = [
            {
                'nombre': 'Tubo de aluminio anodizado 22mm',
                'descripcion': 'Estructura principal para coches y corrales plegables.',
                'marca': 'BabyRide Components',
                'proveedor': providers[0],
                'precio_unitario': Decimal('18500.00'),
                'unidad_medida': 'm',
                'stock_actual': Decimal('380.00'),
                'stock_minimo': Decimal('80.00'),
                'ubicacion': 'Rack A1',
            },
            {
                'nombre': 'Espuma HR 28 kg/m3',
                'descripcion': 'Espuma de alta resiliencia para colchonetas y reductores.',
                'marca': 'Colchones Infantiles Andinos',
                'proveedor': providers[1],
                'precio_unitario': Decimal('42000.00'),
                'unidad_medida': 'kg',
                'stock_actual': Decimal('240.00'),
                'stock_minimo': Decimal('50.00'),
                'ubicacion': 'Rack B3',
            },
            {
                'nombre': 'Madera pino inmunizada cepillada',
                'descripcion': 'Listones tratados para estructuras de cunas.',
                'marca': 'Bosque Kids',
                'proveedor': providers[2],
                'precio_unitario': Decimal('29500.00'),
                'unidad_medida': 'm',
                'stock_actual': Decimal('520.00'),
                'stock_minimo': Decimal('100.00'),
                'ubicacion': 'Patio Madera',
            },
            {
                'nombre': 'Tela pique hipoalergenica acolchada',
                'descripcion': 'Tela exterior para colchonetas, cunas y protectores.',
                'marca': 'Sueno Bebe Textil',
                'proveedor': providers[3],
                'precio_unitario': Decimal('23500.00'),
                'unidad_medida': 'm',
                'stock_actual': Decimal('460.00'),
                'stock_minimo': Decimal('90.00'),
                'ubicacion': 'Telares 2',
            },
            {
                'nombre': 'Juego de ruedas EVA 6 pulgadas',
                'descripcion': 'Kit de ruedas delanteras y traseras para coches de bebe.',
                'marca': 'Ruedas EVA Premium',
                'proveedor': providers[4],
                'precio_unitario': Decimal('56000.00'),
                'unidad_medida': 'caja',
                'stock_actual': Decimal('125.00'),
                'stock_minimo': Decimal('25.00'),
                'ubicacion': 'Rack C5',
            },
        ]
        materials = []
        for data in materials_data:
            materia, created = MateriaPrima.objects.update_or_create(
                nombre=data['nombre'],
                defaults={
                    'descripcion': data['descripcion'],
                    'marca': data['marca'],
                    'proveedor': data['proveedor'],
                    'precio_unitario': data['precio_unitario'],
                    'unidad_medida': data['unidad_medida'],
                    'stock_actual': data['stock_actual'],
                    'stock_minimo': data['stock_minimo'],
                    'ubicacion': data['ubicacion'],
                    'observaciones': 'Materia prima adicional para linea real de productos de bebe.',
                    'activo': True,
                },
            )
            MovimientoMateriaPrima.objects.get_or_create(
                materia_prima=materia,
                tipo='entrada',
                cantidad=Decimal('15.00'),
                motivo='Ingreso inicial linea bebe premium',
                defaults={'precio_unitario': materia.precio_unitario},
            )
            materials.append(materia)
            if created:
                summary['materias_primas'] += 1
        return materials

    def create_products(self, materials, summary):
        category, _ = Categoria.objects.get_or_create(
            nombre='Movilidad y descanso infantil',
            defaults={'descripcion': 'Coches, cunas, colchonetas y mobiliario premium para bebe.'},
        )

        products_data = [
            {
                'nombre': 'Coche Travel System Oslo',
                'descripcion': 'Coche de bebe plegable con portabebe y chasis de aluminio ultraligero.',
                'precio_costo': Decimal('415000.00'),
                'precio_venta': Decimal('589900.00'),
                'stock_actual': 12,
                'tiempo_produccion': 180,
                'ingredientes': [
                    (materials[0], Decimal('3.50')),
                    (materials[3], Decimal('1.80')),
                    (materials[4], Decimal('1.00')),
                ],
            },
            {
                'nombre': 'Cuna Evolutiva Nube',
                'descripcion': 'Cuna de pino inmunizado con tres niveles de altura y barandas seguras.',
                'precio_costo': Decimal('520000.00'),
                'precio_venta': Decimal('749900.00'),
                'stock_actual': 8,
                'tiempo_produccion': 240,
                'ingredientes': [
                    (materials[2], Decimal('8.50')),
                    (materials[3], Decimal('1.20')),
                ],
            },
            {
                'nombre': 'Colchoneta Antireflujo SoftDream',
                'descripcion': 'Colchoneta ergonomica antireflujo con espuma HR y funda desmontable.',
                'precio_costo': Decimal('98000.00'),
                'precio_venta': Decimal('159900.00'),
                'stock_actual': 24,
                'tiempo_produccion': 75,
                'ingredientes': [
                    (materials[1], Decimal('1.60')),
                    (materials[3], Decimal('1.40')),
                ],
            },
            {
                'nombre': 'Corral Plegable Brisa',
                'descripcion': 'Corral plegable con malla transpirable y estructura reforzada.',
                'precio_costo': Decimal('275000.00'),
                'precio_venta': Decimal('419900.00'),
                'stock_actual': 10,
                'tiempo_produccion': 140,
                'ingredientes': [
                    (materials[0], Decimal('2.80')),
                    (materials[3], Decimal('2.20')),
                ],
            },
            {
                'nombre': 'Mecedora de Lactancia Alba',
                'descripcion': 'Sillon mecedor tapizado para lactancia con soporte lumbar y brazos acolchados.',
                'precio_costo': Decimal('345000.00'),
                'precio_venta': Decimal('529900.00'),
                'stock_actual': 6,
                'tiempo_produccion': 210,
                'ingredientes': [
                    (materials[2], Decimal('4.80')),
                    (materials[1], Decimal('2.20')),
                    (materials[3], Decimal('2.60')),
                ],
            },
        ]

        products = []
        for data in products_data:
            producto, created = Producto.objects.update_or_create(
                nombre=data['nombre'],
                defaults={
                    'descripcion': data['descripcion'],
                    'categoria': category,
                    'precio_costo': data['precio_costo'],
                    'precio_venta': data['precio_venta'],
                    'stock_actual': data['stock_actual'],
                    'activo': True,
                },
            )
            receta, _ = Receta.objects.update_or_create(
                producto=producto,
                defaults={
                    'descripcion': f'Receta productiva de {producto.nombre}',
                    'tiempo_produccion': data['tiempo_produccion'],
                    'activo': True,
                },
            )
            for materia_prima, cantidad in data['ingredientes']:
                IngredienteReceta.objects.update_or_create(
                    receta=receta,
                    materia_prima=materia_prima,
                    defaults={'cantidad_requerida': cantidad},
                )
            ProductoMovimiento.objects.get_or_create(
                producto=producto,
                tipo='creacion',
                motivo='Alta de producto linea bebe premium',
                defaults={
                    'cantidad': Decimal(producto.stock_actual),
                    'usuario': 'add_baby_distributor_extras',
                },
            )
            products.append(producto)
            if created:
                summary['productos'] += 1
        return products

    def create_sales(self, products, clients, users, summary):
        seller = users[0]
        sales_data = [
            ('BEBE-REAL-0001', clients[0], products[0], 1, 'completada', 'Entrega en Chicó Norte'),
            ('BEBE-REAL-0002', clients[1], products[2], 2, 'completada', 'Pedido para gemelos con funda extra'),
            ('BEBE-REAL-0003', clients[2], products[1], 1, 'pendiente', 'Reservado para baby shower de fin de mes'),
            ('BEBE-REAL-0004', clients[3], products[3], 1, 'en_progreso', 'Despacho a Barranquilla en curso'),
            ('BEBE-REAL-0005', clients[4], products[4], 1, 'pendiente', 'Cliente solicita armado asistido'),
        ]
        for numero, cliente, producto, cantidad, estado, observacion in sales_data:
            venta, created = Venta.objects.update_or_create(
                numero_venta=numero,
                defaults={
                    'vendedor': seller,
                    'cliente': cliente,
                    'estado': estado,
                    'impuesto': Decimal('0.00'),
                    'descuento': Decimal('0.00'),
                    'total': Decimal('0.00'),
                    'observaciones': observacion,
                    'fecha_completado': timezone.now() if estado == 'completada' else None,
                },
            )
            venta.detalles.all().delete()
            DetalleVenta.objects.create(
                venta=venta,
                producto=producto,
                cantidad=cantidad,
                precio_unitario=producto.precio_venta,
                subtotal=producto.precio_venta * cantidad,
            )
            venta.recompute_total()
            if created:
                summary['ventas'] += 1

    def create_production(self, products, users, summary):
        responsible = users[3]
        production_data = [
            (products[0], 4, 'pendiente', 'Lote para vitrinas de Bogota'),
            (products[1], 3, 'en_progreso', 'Produccion para canal institucional'),
            (products[2], 12, 'completada', 'Reposicion de colchonetas de alta rotacion'),
            (products[3], 5, 'pendiente', 'Pedido mayorista de temporada'),
            (products[4], 2, 'completada', 'Mecedoras premium para sala de exhibicion'),
        ]
        for index, (producto, cantidad, estado, nota) in enumerate(production_data, start=1):
            orden, created = OrdenProduccion.objects.update_or_create(
                producto=producto,
                notas=nota,
                defaults={
                    'receta': producto.receta,
                    'cantidad_a_producir': cantidad,
                    'estado': estado,
                    'fecha_inicio': timezone.now() if estado in {'en_progreso', 'completada'} else None,
                    'fecha_fin': timezone.now() if estado == 'completada' else None,
                    'responsable': responsible,
                },
            )
            ProduccionDiaria.objects.update_or_create(
                orden_produccion=orden,
                fecha=timezone.now().date(),
                defaults={
                    'cantidad_producida': cantidad if estado == 'completada' else max(1, cantidad - 1),
                    'tiempo_trabajado': 120 + (index * 15),
                    'observaciones': f'Seguimiento real de produccion para {producto.nombre}',
                    'responsable': responsible,
                },
            )
            if created:
                summary['ordenes_produccion'] += 1
                summary['producciones_diarias'] += 1
