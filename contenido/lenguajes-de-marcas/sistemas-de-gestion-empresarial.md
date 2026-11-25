# Sistemas de gestión empresarial

Una empresa pequeña puede llevar clientes en una hoja de cálculo, facturas en otra y el almacén en la cabeza. Funciona hasta que dos personas venden la última unidad del mismo producto o el gestor pide un listado que nadie sabe construir. Un sistema de gestión empresarial pone esos datos en un solo sitio y hace que las áreas hablen el mismo idioma.


## Qué es un ERP y qué es un CRM

El **ERP** (*enterprise resource planning*) integra los procesos internos: compras, ventas, almacén, fabricación, contabilidad y recursos humanos. El **CRM** (*customer relationship management*) gestiona la relación con el cliente: contactos, oportunidades, presupuestos y seguimiento. Muchos ERP incluyen CRM, y muchos CRM se conectan al ERP.

La diferencia con una aplicación suelta no es el número de pantallas: es que comparten los datos maestros. Un cliente es el mismo para ventas, facturación y envíos; un artículo tiene un código único y un stock que se actualiza al vender.

## Datos maestros y datos de movimiento

El sistema distingue dos capas:

- **Maestros:** clientes, proveedores, artículos, tarifas, almacenes, cuentas contables. Cambian poco y deben ser únicos.
- **Movimientos:** pedidos, albaranes, facturas, cobros, entradas y salidas de almacén. Cambian mucho y se apoyan en los maestros.

La calidad del sistema se mide en los maestros: un cliente duplicado, un artículo sin unidad de medida o una cuenta contable mal asignada contaminan todos los movimientos. Antes de implantar, se limpia y se normaliza; después, se impide crear duplicados con reglas y validaciones.

## Módulos que se conectan

Un ERP típico de pyme cubre:

| Área | Qué resuelve |
|---|---|
| Compras | Pedido, recepción, factura de proveedor |
| Ventas | Presupuesto, pedido, albarán, factura, cobro |
| Almacén | Existencias, entradas, salidas, inventario |
| Contabilidad | Asientos, impuestos, cuentas anuales |
| Personas | Nóminas, altas, bajas, formación |
| CRM | Contactos, oportunidades, seguimiento |

La integración evita volver a teclear: una factura de venta genera el asiento contable y descuenta stock. Cuando un módulo no está integrado, aparece la doble grabación y con ella la discrepancia.

## Cómo se intercambian los datos

Los sistemas hablan por tres vías:

- **API:** el estándar actual. REST con JSON para operaciones y consultas; el sistema expone recursos y el otro los consume con autenticación.
- **Ficheros:** CSV para volúmenes simples, XML cuando hay que validar estructura y significado.
- **Mensajería:** colas o eventos para integrar sin acoplar los sistemas; un pedido publicado lo consumen almacén y facturación.

En España, la factura electrónica tiene formatos normalizados: **Facturae** y **UBL** son los habituales, y la norma europea **EN 16931** fija el modelo semántico. Un esquema XSD permite validar que el documento cumple antes de importarlo; sin validación, el error aparece en contabilidad.

## Elegir e implantar

La elección no se hace por la lista de funciones, sino por los procesos que hay que resolver. Preguntas útiles:

- ¿Qué procesos duelen hoy y cuáles no?
- ¿Cuántos usuarios y con qué permisos?
- ¿Se necesita nube, servidor propio o mixto?
- ¿Qué integraciones exige —banco, gestoría, tienda online—?
- ¿Cuánto cuesta la implantación, la formación y el soporte, no solo la licencia?
- ¿Cómo se sale si el proveedor desaparece o sube el precio?

La **implantación** se hace por fases: maestros, compras y ventas, almacén, contabilidad. Personalizar en exceso ata el sistema a una versión y encarece cada actualización. La formación y el responsable interno pesan más que el número de módulos.

## Riesgos que se repiten

- **Datos sucios:** se importa todo y el sistema nace con duplicados.
- **Alcance que crece:** cada área pide su módulo y el proyecto no termina.
- **Doble sistema:** conviven el viejo y el nuevo y nadie sabe cuál manda.
- **Dependencia del proveedor:** datos en un formato que no se puede exportar.
- **Falta de formación:** el sistema hace más de lo que el equipo usa.

## Lo que se comprueba

Que los datos maestros están limpios y tienen reglas de unicidad; que los procesos de compra, venta y contabilidad comparten la información; que la integración valida el documento antes de aceptarlo; que el coste total incluye implantación y soporte; y que existe un plan de salida con los datos exportables.

## Fuentes

- Facturae 3.2.2 y su esquema XSD; UBL 2.1.
- UNE-EN 16931, modelo semántico de la factura electrónica.
- Documentación de referencia de ERP y CRM de uso extendido en pymes.
- Orden EDU/392/2010, de 20 de enero (BOE-A-2010-3028).
