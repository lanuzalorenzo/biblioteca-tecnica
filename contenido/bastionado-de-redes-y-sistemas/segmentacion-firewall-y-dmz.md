# Segmentación, cortafuegos y DMZ

Un edificio de oficinas con una única entrada y sin tabiques interiores deja que cualquiera que pase el portal llegue a todas las plantas. Una red plana funciona igual: el visitante que conecta un portátil alcanza el servidor de nóminas. Segmentar es levantar tabiques y colocar puertas con llave; el cortafuegos decide quién pasa y la DMZ es el vestíbulo donde se atiende a quien viene de la calle.

La separación por VLAN y la autenticación de puerto están en [El acceso a la red](../seguridad-y-alta-disponibilidad/acceso-a-la-red.md), y la lógica de las ACL en [Enrutamiento avanzado, ACL y seguridad de la red](../redes/enrutamiento-acl-y-seguridad.md). Aquí se trata el modelo de filtrado: qué zonas se definen, qué reglas las separan y cómo se revisan.

## Qué se decide

Segmentar no es crear VLAN. Es decidir qué puede hablar con qué y dónde se aplica esa decisión. Cada zona necesita tres cosas:

- Un propósito: usuarios, servidores, invitados, gestión, DMZ, dispositivos industriales.
- Un límite: una subred o un conjunto de subredes con su puerta de enlace.
- Una política: qué flujos entran y salen, con origen, destino y puerto.

Sin la tercera, la zona solo cambia el dibujo. La comunicación sigue abierta si el router enruta sin filtro.

## Zonas mínimas

| Zona | Qué contiene | Si se mezcla |
|---|---|---|
| Gestión | Administración de switches, routers y cortafuegos | Un puesto comprometido puede reconfigurar la red |
| Servidores | Servicios internos y bases de datos | Un usuario alcanza datos que no le tocan |
| Usuarios | Puestos de trabajo | El malware de un equipo llega al resto |
| Invitados | Dispositivos de visitas y personales | Un invitado entra en la red corporativa |
| DMZ | Servicios publicados hacia Internet | Un fallo web abre la red interna |
| Industrial / IoT | Sensores, cámaras, maquinaria | Un dispositivo sin parches comparte red con oficinas |

El tamaño importa menos que la separación. Una zona pequeña con reglas claras protege más que una grande sin filtro.

## El modelo de reglas

Una política de filtrado se escribe con cuatro decisiones:

1. **Denegar por defecto.** Solo pasa lo que está permitido de forma explícita.
2. **Mínimo privilegio.** Cada permiso fija origen, destino, protocolo y puerto; «cualquier cosa desde dentro» no es una regla.
3. **Orden consciente.** La primera coincidencia decide; una regla amplia arriba anula las específicas de abajo.
4. **Registro y caducidad.** Los flujos relevantes se registran y las excepciones tienen fecha de revisión.

Una regla sin dueño ni motivo es deuda técnica. Se revisa, se justifica o se retira.

## DMZ: qué se publica

La DMZ existe para que un servicio expuesto no comparta red con lo que se protege. Publicar allí un servidor exige decidir:

- **Qué se publica.** Solo el servicio necesario, no el servidor entero.
- **Qué puede iniciar la DMZ hacia dentro.** Lo imprescindible; por defecto, nada.
- **Con qué credenciales.** Las del servicio publicado, nunca las de la red interna.
- **Quién administra.** El acceso de gestión va por una vía separada, no por la misma interfaz pública.
- **Qué se registra.** Intentos de acceso, errores y cambios de configuración.

Una DMZ que permite tráfico libre hacia la red interna es una red plana con otro nombre. Y publicar un servicio con credenciales internas traslada el problema en lugar de resolverlo.

## Auditoría de reglas

1. Inventaría las reglas y asígnalas a un dueño.
2. Busca reglas sombreadas: las que nunca se evalúan porque otra anterior las tapa.
3. Revisa los permisos «any-any» y los que abren más de lo necesario.
4. Detecta reglas sin tráfico durante un periodo suficiente.
5. Comprueba que las excepciones temporales tienen fecha y se retiran.
6. Verifica que el orden del conjunto sigue el criterio documentado.
7. Contrasta la política con el inventario de servicios y de zonas.

La auditoría no busca solo reglas mal escritas: busca reglas que ya no deberían existir.

## Cambios y excepciones

Toda excepción se pide, se justifica y se limita en el tiempo. Un cambio de regla sin registro convierte la política en un conjunto de decisiones invisibles.

El flujo mínimo: solicitud con origen, destino y motivo; aprobación de quien responde de la zona; aplicación; comprobación de que el flujo funciona y de que no se ha abierto más de la cuenta; fecha de revisión.

## Qué comprobar

- Cada zona tiene un propósito, una subred y una política.
- El paso entre zonas está permitido por regla explícita, no por defecto.
- La política empieza por denegar y cada permiso justifica origen, destino y puerto.
- La DMZ solo publica lo necesario y no inicia tráfico hacia dentro salvo lo imprescindible.
- Las reglas y las ACL tienen dueño, registro y revisión.
- Las excepciones temporales caducan y se retiran.

## Errores que se repiten

- Crear VLAN y creer que la seguridad está resuelta.
- Poner una regla de permiso total «para que funcione».
- Publicar en la misma red los servicios de Internet y los internos.
- Abrir un puerto para una prueba y olvidar cerrarlo.
- Acumular reglas durante años y no atreverse a borrar ninguna.

## Fuentes

- NIST SP 800-41 Rev. 1, *Guidelines on Firewalls and Firewall Policy*.
- IEEE 802.1Q (VLAN y etiquetado de tramas).
- NIST SP 800-125B, *Secure Virtual Network Configuration for Virtual Machine Protection*.
