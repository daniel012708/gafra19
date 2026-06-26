from decimal import Decimal
from random import Random

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from clientes.models import Cliente
from inventario.models import MateriaPrima, MovimientoMateriaPrima
from produccion.models import OrdenProduccion, ProduccionDiaria
from productos.models import Categoria, IngredienteReceta, Producto, ProductoMovimiento, Receta
from proveedores.models import Proveedor
from proveedores.movimientos import ProveedorMovimiento
from usuario.models import Usuario
from ventas.models import DetalleVenta, Venta


class Command(BaseCommand):
    help = "Genera datos demo coherentes para GAFRA (bebes) con 20 registros por modulo principal."

    def add_arguments(self, parser):
        parser.add_argument("--records", type=int, default=20)
        parser.add_argument("--seed", type=int, default=20260625)

    @transaction.atomic
    def handle(self, *args, **options):
        total = max(20, options["records"])
        rng = Random(options["seed"])

        self.stdout.write(self.style.WARNING("Generando dataset GAFRA bebe..."))

        users, roles = self._create_users(total)
        categories = self._create_categories()
        suppliers = self._create_suppliers(total)
        materias = self._create_materias(total, suppliers)
        products = self._create_products(total, categories)
        self._create_recipes(products, materias, rng)
        clients = self._create_clients(total)
        ventas = self._create_sales(total, products, clients, roles["vendedor"], rng)
        ordenes = self._create_production_orders(total, products, roles["logistica"], rng)
        self._create_inventory_movements(total, ordenes, rng)
        self._create_product_movements(total, products, rng)

        summary = {
            "usuarios": len(users),
            "proveedores": len(suppliers),
            "materias_primas": len(materias),
            "productos": len(products),
            "clientes": len(clients),
            "ventas": len(ventas),
            "ordenes_produccion": len(ordenes),
            "movimientos_mp": total,
            "movimientos_producto": total,
        }

        self.stdout.write(self.style.SUCCESS("Dataset demo creado correctamente."))
        for key, value in summary.items():
            self.stdout.write(f"- {key}: {value}")

    def _create_users(self, total):
        role_pattern = [
            "admin",
            "vendedor",
            "almacenista",
            "logistica",
            "cliente",
            "vendedor",
            "logistica",
            "cliente",
            "almacenista",
            "cliente",
        ]
        first_names = [
            "Laura", "Juan", "Sofia", "Andres", "Camila", "Mateo", "Valentina", "Daniel",
            "Sara", "Nicolas", "Paula", "Samuel", "Mariana", "Sebastian", "Lucia", "David",
            "Isabella", "Santiago", "Gabriela", "Felipe",
        ]
        last_names = [
            "Gomez", "Rodriguez", "Martinez", "Lopez", "Gonzalez", "Hernandez", "Perez", "Diaz",
            "Sanchez", "Ramirez", "Torres", "Vargas", "Castro", "Rojas", "Moreno", "Silva",
            "Ortiz", "Suarez", "Restrepo", "Cardona",
        ]

        users = []
        role_users = {
            "admin": [],
            "vendedor": [],
            "almacenista": [],
            "logistica": [],
            "cliente": [],
        }

        for idx in range(total):
            i = idx + 1
            role = role_pattern[idx % len(role_pattern)]
            username = f"demo_gafra_{i:02d}"
            email = f"{username}@gafra-demo.com"

            user, _ = User.objects.update_or_create(
                username=username,
                defaults={
                    "email": email,
                    "first_name": first_names[idx % len(first_names)],
                    "last_name": last_names[idx % len(last_names)],
                    "is_active": True,
                    "is_staff": role in {"admin", "vendedor", "almacenista", "logistica"},
                    "is_superuser": role == "admin",
                },
            )
            user.set_password("GafraDemo2026!")
            user.save(update_fields=["password"])

            Usuario.objects.update_or_create(
                user=user,
                defaults={
                    "rol": role,
                    "telefono": f"3{10 + (i % 20):02d}{1000000 + i:07d}",
                    "activo": True,
                },
            )

            users.append(user)
            role_users[role].append(user)

        return users, role_users

    def _create_categories(self):
        categories_data = [
            ("Corrales para bebe", "Linea de corrales plegables y premium para bebe"),
            ("Cunas para bebe", "Linea de cunas clasicas, premium y multifuncionales"),
            ("Colchonetas para bebe", "Linea de colchonetas antialergicas y premium"),
        ]
        categories = {}
        for name, description in categories_data:
            category, _ = Categoria.objects.get_or_create(nombre=name, defaults={"descripcion": description})
            categories[name] = category
        return categories

    def _create_suppliers(self, total):
        cities = [
            "Bogota", "Medellin", "Cali", "Barranquilla", "Bucaramanga",
            "Pereira", "Manizales", "Cartagena", "Ibague", "Villavicencio",
        ]
        supplier_names = [
            "Maderas Andinas", "Espumas del Norte", "Textiles Nido", "Metal Kids Industrial",
            "Herrajes BabyPro", "Pinturas Seguras SAS", "Cremalleras del Valle", "Ruedas Infantiles CO",
            "Mallas Protectoras Plus", "Velcros Tecnicos", "Empaques Cuidado", "Tubometal Colombia",
            "Pino Inmunizado Centro", "Telas Antialergicas Premium", "Tornilleria Fina",
            "Acabados No Toxicos", "Accesorios Cuna Hogar", "Diseño y Confort Bebes",
            "Logistica de Insumos Junior", "Materiales Integrales GAFRA",
        ]
        specialties = [
            "madera pino inmunizada",
            "espuma de alta densidad",
            "tela antialergica",
            "tubos metalicos",
            "herrajes para corral",
            "pintura no toxica",
            "cremalleras y cierres",
            "ruedas para cuna",
            "malla protectora",
            "velcro industrial",
            "empaques y bolsas protectoras",
            "tubos metalicos y perfiles",
            "madera tratada para mobiliario",
            "textiles hipoalergenicos",
            "tornillos y fijaciones",
            "barnices base agua",
            "herrajes de seguridad",
            "accesorios de confort",
            "insumos de almacenamiento",
            "suministro mixto de insumos",
        ]

        suppliers = []
        for idx in range(total):
            i = idx + 1
            city = cities[idx % len(cities)]
            name = f"GAFRA DEMO PROV {i:02d} - {supplier_names[idx % len(supplier_names)]}"
            supplier, _ = Proveedor.objects.update_or_create(
                nombre=name,
                defaults={
                    "razon_social": f"{supplier_names[idx % len(supplier_names)]} SAS",
                    "rfc": f"GFR{i:010d}"[:13],
                    "contacto": f"Contacto {i:02d}",
                    "telefono": f"3{15 + (i % 10):02d}{2000000 + i:07d}",
                    "email": f"proveedor{i:02d}@gafra-demo.com",
                    "direccion": f"Calle {10 + i} # {20 + (i % 30)}-{30 + (i % 60)}",
                    "ciudad": city,
                    "estado": city,
                    "pais": "Colombia",
                    "codigo_postal": f"11{i:03d}",
                    "tipo": "Nacional",
                    "sitio_web": f"https://prov{i:02d}.gafra-demo.com",
                    "activo": True,
                },
            )

            if not ProveedorMovimiento.objects.filter(
                proveedor=supplier,
                accion="EDITADO",
                detalles="[DEMO-GAFRA] Proveedor generado para insumos de bebe",
            ).exists():
                ProveedorMovimiento.objects.create(
                    proveedor=supplier,
                    usuario=User.objects.filter(is_superuser=True).first(),
                    accion="EDITADO",
                    detalles="[DEMO-GAFRA] Proveedor generado para insumos de bebe",
                )
            supplier.demo_specialty = specialties[idx % len(specialties)]
            suppliers.append(supplier)

        return suppliers

    def _create_materias(self, total, suppliers):
        materials = [
            ("Espuma de alta densidad", "kg", Decimal("38.00")),
            ("Tela antialergica", "m", Decimal("22.00")),
            ("Madera pino inmunizada", "m", Decimal("45.00")),
            ("Tubos metalicos", "m", Decimal("29.50")),
            ("Tornillos galvanizados", "pz", Decimal("0.18")),
            ("Pintura no toxica blanca", "l", Decimal("18.00")),
            ("Cremalleras reforzadas", "pz", Decimal("1.20")),
            ("Ruedas para cuna", "pz", Decimal("4.30")),
            ("Malla protectora", "m", Decimal("19.00")),
            ("Herrajes de seguridad", "pz", Decimal("2.50")),
            ("Velcro industrial", "m", Decimal("3.80")),
            ("Empaques protectores", "pz", Decimal("0.95")),
            ("Bolsas transparentes resistentes", "pz", Decimal("0.42")),
            ("Espuma memory foam", "kg", Decimal("52.00")),
            ("Tela impermeable", "m", Decimal("24.50")),
            ("Pintura no toxica gris", "l", Decimal("18.50")),
            ("Barniz base agua", "l", Decimal("17.40")),
            ("Refuerzo plastico esquineros", "pz", Decimal("0.70")),
            ("Cinta textil de union", "m", Decimal("1.35")),
            ("Etiquetas de cuidado", "pz", Decimal("0.25")),
        ]

        materias = []
        for idx in range(total):
            i = idx + 1
            name, unit, price = materials[idx % len(materials)]
            supplier = suppliers[idx % len(suppliers)]
            materia, _ = MateriaPrima.objects.update_or_create(
                nombre=f"{name} DEMO {i:02d}",
                defaults={
                    "descripcion": f"[DEMO-GAFRA] Insumo para {supplier.demo_specialty}",
                    "marca": f"MarcaDemo{i:02d}",
                    "proveedor": supplier,
                    "precio_unitario": price,
                    "unidad_medida": unit,
                    "stock_actual": Decimal(600 + i * 15),
                    "stock_minimo": Decimal(120 + i),
                    "ubicacion": f"Bodega-{(i % 4) + 1}-A{(i % 6) + 1}",
                    "observaciones": "[DEMO-GAFRA] Materia prima para pruebas academicas",
                    "activo": True,
                },
            )
            materias.append(materia)

        return materias

    def _create_products(self, total, categories):
        products_data = [
            ("Corrales para bebe", "Corral Plegable Azul 80x100 cm", "Diseno basico plegable con malla lateral y estructura metalica"),
            ("Corrales para bebe", "Corral Premium Gris 90x110 cm", "Linea premium con doble seguro lateral y acabado textil suave"),
            ("Corrales para bebe", "Corral Estrellas Rosa 100x120 cm", "Diseno estampado estrellas con proteccion acolchada perimetral"),
            ("Corrales para bebe", "Corral Safari Verde 90x100 cm", "Coleccion safari con malla respirable y base antideslizante"),
            ("Corrales para bebe", "Corral Nube Beige 85x105 cm", "Modelo ligero para espacios pequenos con cierre reforzado"),
            ("Corrales para bebe", "Corral City Negro 95x115 cm", "Diseno urbano con acabado sobrio y herrajes de seguridad"),
            ("Corrales para bebe", "Corral Travel Azul Marino 88x108 cm", "Version viaje con plegado rapido y bolsa de transporte"),
            ("Cunas para bebe", "Cuna Clasica Blanca 120x60 cm", "Cuna clasica de pino inmunizado con barandas altas"),
            ("Cunas para bebe", "Cuna Premium Madera Natural 130x70 cm", "Linea premium con acabado natural y ruedas con freno"),
            ("Cunas para bebe", "Cuna Ositos Beige 120x60 cm", "Diseno infantil estampado ositos con pintura no toxica"),
            ("Cunas para bebe", "Cuna Multifuncional Gris 140x70 cm", "Convertible con modulos de almacenamiento lateral"),
            ("Cunas para bebe", "Cuna Luna Blanca 125x65 cm", "Coleccion luna con esquinas redondeadas y base ajustable"),
            ("Cunas para bebe", "Cuna Bosque Verde Salvia 130x70 cm", "Inspiracion natural con herrajes reforzados"),
            ("Cunas para bebe", "Cuna Smart Arena 135x70 cm", "Diseno moderno con ruedas giratorias silenciosas"),
            ("Colchonetas para bebe", "Colchoneta Antialergica Azul 120x60 cm", "Nucleo de espuma densa y funda antialergica removible"),
            ("Colchonetas para bebe", "Colchoneta Premium Memory Foam 130x70 cm", "Memory foam de alta recuperacion y textura suave"),
            ("Colchonetas para bebe", "Colchoneta Estampada Safari 120x60 cm", "Estampado safari lavable con cierre reforzado"),
            ("Colchonetas para bebe", "Colchoneta Impermeable Rosa 100x60 cm", "Funda impermeable de facil limpieza para uso diario"),
            ("Colchonetas para bebe", "Colchoneta Nube Gris 110x60 cm", "Diseno nube acolchado para cunas compactas"),
            ("Colchonetas para bebe", "Colchoneta Fresh Menta 120x65 cm", "Linea fresca con ventilacion y doble cara reversible"),
        ]

        products = []
        for idx in range(total):
            i = idx + 1
            category_name, name, desc = products_data[idx % len(products_data)]
            category = categories[category_name]
            base_cost = Decimal("95.00") + Decimal(i * 6)
            sale_price = base_cost * Decimal("1.65")

            product, _ = Producto.objects.update_or_create(
                nombre=name,
                defaults={
                    "descripcion": f"[DEMO-GAFRA] {desc}",
                    "categoria": category,
                    "precio_costo": base_cost,
                    "precio_venta": sale_price.quantize(Decimal("0.01")),
                    "stock_actual": 80 + (i * 2),
                    "activo": True,
                },
            )
            products.append(product)

        return products

    def _create_recipes(self, products, materias, rng):
        materia_by_key = {
            "espuma": [m for m in materias if "Espuma" in m.nombre],
            "tela": [m for m in materias if "Tela" in m.nombre],
            "madera": [m for m in materias if "Madera" in m.nombre],
            "tubo": [m for m in materias if "Tubos" in m.nombre],
            "tornillo": [m for m in materias if "Tornillos" in m.nombre],
            "pintura": [m for m in materias if "Pintura" in m.nombre],
            "cremallera": [m for m in materias if "Cremalleras" in m.nombre],
            "rueda": [m for m in materias if "Ruedas" in m.nombre],
            "malla": [m for m in materias if "Malla" in m.nombre],
            "herraje": [m for m in materias if "Herrajes" in m.nombre],
            "velcro": [m for m in materias if "Velcro" in m.nombre],
            "empaque": [m for m in materias if "Empaques" in m.nombre or "Bolsas" in m.nombre],
        }

        for idx, product in enumerate(products):
            recipe, _ = Receta.objects.update_or_create(
                producto=product,
                defaults={
                    "descripcion": f"[DEMO-GAFRA] Formula estandar para {product.nombre}",
                    "tiempo_produccion": 55 + (idx % 6) * 20,
                    "activo": True,
                },
            )

            recipe.ingredientes.all().delete()

            if "Corral" in product.nombre:
                blueprint = [
                    (materia_by_key["tubo"][0], Decimal("2.40")),
                    (materia_by_key["malla"][0], Decimal("1.90")),
                    (materia_by_key["tornillo"][0], Decimal("26.00")),
                    (materia_by_key["herraje"][0], Decimal("8.00")),
                    (materia_by_key["pintura"][0], Decimal("0.30")),
                ]
            elif "Cuna" in product.nombre:
                blueprint = [
                    (materia_by_key["madera"][0], Decimal("3.60")),
                    (materia_by_key["rueda"][0], Decimal("4.00")),
                    (materia_by_key["tornillo"][0], Decimal("34.00")),
                    (materia_by_key["herraje"][0], Decimal("10.00")),
                    (materia_by_key["pintura"][0], Decimal("0.45")),
                ]
            else:
                blueprint = [
                    (materia_by_key["espuma"][0], Decimal("1.40")),
                    (materia_by_key["tela"][0], Decimal("2.10")),
                    (materia_by_key["cremallera"][0], Decimal("1.00")),
                    (materia_by_key["velcro"][0], Decimal("1.30")),
                    (materia_by_key["empaque"][0], Decimal("1.00")),
                ]

            for materia, qty in blueprint:
                IngredienteReceta.objects.create(
                    receta=recipe,
                    materia_prima=materia,
                    cantidad_requerida=qty,
                )

    def _create_clients(self, total):
        clients_data = [
            ("Maria Fernanda Rios", "Bogota", "Chapinero"),
            ("Juan Esteban Mejia", "Medellin", "Laureles"),
            ("Carolina Zapata", "Cali", "Ciudad Jardin"),
            ("Andres Felipe Naranjo", "Barranquilla", "Alto Prado"),
            ("Laura Daniela Ospina", "Bucaramanga", "Cabecera"),
            ("Camilo Andres Cardenas", "Pereira", "Pinares"),
            ("Juliana Martinez", "Manizales", "Milan"),
            ("Santiago Gomez", "Cartagena", "Bocagrande"),
            ("Valentina Ruiz", "Ibague", "La Pola"),
            ("Sebastian Moreno", "Villavicencio", "Barzal"),
            ("Paula Andrea Vargas", "Bogota", "Suba"),
            ("Nicolas Herrera", "Medellin", "Envigado"),
            ("Gabriela Restrepo", "Cali", "Granada"),
            ("Felipe Arango", "Barranquilla", "Riomar"),
            ("Daniela Salazar", "Bucaramanga", "Sotomayor"),
            ("Mateo Cardona", "Pereira", "Cuba"),
            ("Isabella Valencia", "Manizales", "Palermo"),
            ("Samuel Quintero", "Cartagena", "Manga"),
            ("Camila Torres", "Ibague", "El Salado"),
            ("David Molina", "Villavicencio", "La Esperanza"),
        ]

        clients = []
        for idx in range(total):
            i = idx + 1
            name, city, area = clients_data[idx % len(clients_data)]
            email = f"cliente{i:02d}@gafra-demo.com"
            client, _ = Cliente.objects.update_or_create(
                email=email,
                defaults={
                    "nombre": name,
                    "documento": f"CC{10000000 + i}",
                    "direccion": f"{area}, Carrera {10 + i} # {20 + i}-{30 + (i % 40)}, {city}",
                    "telefono": f"3{20 + (i % 30):02d}{3000000 + i:07d}",
                },
            )
            clients.append(client)

        return clients

    def _create_sales(self, total, products, clients, sellers, rng):
        if not sellers:
            fallback = User.objects.filter(is_superuser=True).first() or User.objects.first()
            sellers = [fallback] if fallback else []

        ventas = []
        base_date = timezone.now()

        for idx in range(total):
            i = idx + 1
            product = products[idx % len(products)]
            customer = clients[idx % len(clients)]
            seller = sellers[idx % len(sellers)] if sellers else None
            quantity = 1 + (idx % 3)
            subtotal = (product.precio_venta * quantity).quantize(Decimal("0.01"))
            impuesto = (subtotal * Decimal("0.19")).quantize(Decimal("0.01"))
            descuento = Decimal("0.00") if i % 4 else (subtotal * Decimal("0.05")).quantize(Decimal("0.01"))
            total_value = (subtotal + impuesto - descuento).quantize(Decimal("0.01"))
            status = "completada" if i % 5 != 0 else "pendiente"

            venta, _ = Venta.objects.update_or_create(
                numero_venta=f"GB202606-{i:04d}",
                defaults={
                    "vendedor": seller,
                    "cliente": customer,
                    "estado": status,
                    "fecha_completado": base_date if status == "completada" else None,
                    "descuento": descuento,
                    "impuesto": impuesto,
                    "total": total_value,
                    "observaciones": "[DEMO-GAFRA] Venta de prueba para pruebas academicas",
                },
            )

            venta.detalles.all().delete()

            DetalleVenta.objects.create(
                venta=venta,
                producto=product,
                cantidad=quantity,
                precio_unitario=product.precio_venta,
                subtotal=subtotal,
            )

            if status == "completada":
                product.stock_actual = max(0, product.stock_actual - quantity)
                product.save(update_fields=["stock_actual", "fecha_actualizacion"])

            ventas.append(venta)

        return ventas

    def _create_production_orders(self, total, products, responsables, rng):
        if not responsables:
            fallback = User.objects.filter(is_superuser=True).first() or User.objects.first()
            responsables = [fallback] if fallback else []

        estados = ["pendiente", "en_progreso", "completada", "completada", "pendiente"]
        ordenes = []
        now = timezone.now()

        for idx in range(total):
            i = idx + 1
            product = products[idx % len(products)]
            recipe = Receta.objects.get(producto=product)
            status = estados[idx % len(estados)]
            responsable = responsables[idx % len(responsables)] if responsables else None
            qty = 4 + (idx % 8)
            start = now if status in {"en_progreso", "completada"} else None
            end = now if status == "completada" else None

            order, _ = OrdenProduccion.objects.update_or_create(
                notas=f"[DEMO-GAFRA] OP {i:02d}",
                defaults={
                    "producto": product,
                    "receta": recipe,
                    "cantidad_a_producir": qty,
                    "estado": status,
                    "fecha_inicio": start,
                    "fecha_fin": end,
                    "responsable": responsable,
                },
            )

            produced_qty = qty if status == "completada" else (max(1, qty - 2) if status == "en_progreso" else 0)
            ProduccionDiaria.objects.update_or_create(
                orden_produccion=order,
                fecha=now.date(),
                defaults={
                    "cantidad_producida": produced_qty,
                    "tiempo_trabajado": 90 + (idx % 5) * 25 if status in {"en_progreso", "completada"} else 0,
                    "observaciones": "[DEMO-GAFRA] Produccion diaria registrada",
                    "responsable": responsable,
                },
            )

            if status == "completada":
                product.stock_actual += qty
                product.save(update_fields=["stock_actual", "fecha_actualizacion"])

            ordenes.append(order)

        return ordenes

    def _create_inventory_movements(self, total, ordenes, rng):
        for idx in range(total):
            i = idx + 1
            order = ordenes[idx % len(ordenes)]
            ingredientes = list(order.receta.ingredientes.all())
            if not ingredientes:
                continue

            ingrediente = ingredientes[idx % len(ingredientes)]
            if order.estado in {"en_progreso", "completada"}:
                movement_type = "salida"
                qty = (ingrediente.cantidad_requerida * Decimal(order.cantidad_a_producir)).quantize(Decimal("0.01"))
                materia = ingrediente.materia_prima
                materia.stock_actual = max(Decimal("0.00"), materia.stock_actual - qty)
                materia.save(update_fields=["stock_actual"])
            else:
                movement_type = "entrada"
                qty = Decimal(40 + i)
                materia = ingrediente.materia_prima
                materia.stock_actual += qty
                materia.save(update_fields=["stock_actual"])

            MovimientoMateriaPrima.objects.update_or_create(
                materia_prima=materia,
                tipo=movement_type,
                motivo=f"[DEMO-GAFRA] Movimiento OP {order.id} item {i:02d}",
                defaults={
                    "cantidad": qty,
                    "precio_unitario": materia.precio_unitario,
                },
            )

    def _create_product_movements(self, total, products, rng):
        movement_types = ["entrada", "salida", "ajuste", "modificacion"]
        for idx in range(total):
            i = idx + 1
            product = products[idx % len(products)]
            movement_type = movement_types[idx % len(movement_types)]
            qty = Decimal(2 + (idx % 6))

            ProductoMovimiento.objects.update_or_create(
                producto=product,
                motivo=f"[DEMO-GAFRA] Movimiento producto {i:02d}",
                defaults={
                    "tipo": movement_type,
                    "cantidad": qty,
                    "usuario": "seed_gafra_bebe",
                },
            )
