# El CPD y la seguridad pasiva

Un centro de proceso de datos es la caja fuerte del edificio: no impide que alguien lo intente, pero hace que el intento no llegue a los datos y que un corte de luz no se convierta en una pérdida. La seguridad pasiva no detiene el ataque; consigue que el servicio sobreviva a él.


## Dónde se ubica

El local se elige antes de comprar nada y condiciona todo lo demás:

- **Riesgo del entorno:** lejos de zonas inundables, de cauces, de costas, de aeropuertos y de industrias con riesgo de explosión o incendio.
- **Altura:** plantas intermedias. La baja está expuesta a sabotaje y a entrada de agua; la subterránea, a inundación; las superiores, a incendio y a daño estructural.
- **Accesos:** dos, por calles distintas, para que el cierre de una no deje el local sin entrada ni sin suministro.
- **Discreción:** sin señalizar. El cartel «CPD» en la puerta ahorra trabajo a quien busca qué sabotear.
- **Obra:** suelos y techos registrables para el cableado, pintura lavable que no retenga polvo, materiales ignífugos y cerramiento resistente a la intrusión.

La norma de referencia para instalaciones de centro de datos es la serie **UNE-EN 50600**, que clasifica el diseño por clases de disponibilidad y cubre distribución de potencia, climatización, cableado y control. La alternativa estadounidense es ANSI/TIA-942.

## Climatización

Los equipos convierten casi toda la electricidad en calor, y el calor acorta su vida. El diseño actual separa el aire en dos circuitos:

- **Pasillo frío:** recibe el aire de las unidades de climatización y alimenta la toma de los servidores.
- **Pasillo caliente:** recibe el aire que expulsan y lo devuelve al equipo.
- **Contención:** cerrar uno de los dos pasillos con puertas y paneles evita que el aire frío y el caliente se mezclen, que es la causa más común de ineficacia.

Los rangos recomendados por ASHRAE para equipos de clase A1 están entre **18 y 27 °C** de entrada, con el punto de rocío acotado para no condensar. La humedad alta corroe y provoca descargas; la baja genera electricidad estática.

Conviene medir la eficiencia con el **PUE** —energía total dividida entre la que llega a los equipos—: un valor de 1,2 es bueno; por encima de 2 hay margen de mejora.

## Suministro eléctrico

- **Doble acometida**, preferiblemente de empresas distintas y por recorridos distintos.
- **Grupo electrógeno** para cortes largos y **SAI** para el hueco entre el corte y el arranque del grupo.
- **Cuadros separados** para el CPD y para el resto del edificio, de modo que un fallo en oficinas no arrastre a los servidores.

El SAI se elige por tipo:

| Tipo | Cómo funciona | Cuándo se usa |
|---|---|---|
| De espera (*offline*) | La carga va a la red; el SAI entra al caer | Puesto de trabajo |
| Interactivo (*line-interactive*) | Regula tensión con la red presente | Pequeño armario de comunicaciones |
| En línea (*online*, doble conversión) | La carga va siempre por el inversor | Servidores y CPD |

Un SAI no es una fuente infinita: da minutos. Lo que hace útil ese tiempo es la **parada ordenada** —apagar servicios, sincronizar discos, cerrar bases de datos— y el aviso. Las baterías se degradan: hay que probar la autonomía periódicamente y sustituirlas cuando no aguantan la carga. Las configuraciones modulares de baterías pequeñas escalan mejor que una grande.

## Detección y extinción

Antes del fuego hay humo, y antes del humo hay partículas. Los sistemas de aspiración detectan concentraciones mínimas y avisan cuando aún se puede intervenir con un conato.

Para apagar no se usa agua sobre equipos energizados ni polvo, que arruina lo que no quemó. Se emplean **gases inertes** (IG-541, IG-100) o **agentes limpios**, diseñados para desplazar el oxígeno sin dejar residuo. Los hidrofluorocarbonos como el FM-200 siguen instalados, pero están en retirada por la normativa europea de gases fluorados: al ampliar o renovar, se elige alternativa.

## Control de acceso físico

- **Esclusa** (*man-trap*): dos puertas que no se abren a la vez, para que nadie entre detrás de otro.
- **Doble factor físico:** tarjeta más biometría o PIN, con registro de cada apertura.
- **Videovigilancia y sensores** de presencia, inundación y apertura de puertas.
- **Registro** de visitas y de quién retira un disco o un servidor.

## Centro de respaldo y continuidad

El centro de respaldo replica los servicios en un lugar físicamente separado —otra ciudad, otro riesgo sísmico y eléctrico— y se activa si el principal cae. Tres decisiones lo definen:

- **RTO:** cuánto tiempo puede estar el servicio caído.
- **RPO:** cuántos datos se puede permitir perder, en minutos u horas.
- **Tipo de sitio:** caliente (listo y sincronizado), templado (equipado, sin datos al día) o frío (solo espacio y suministro).

El error clásico es tener el centro de respaldo documentado y nunca probado. Un plan que no se ensaya una vez al año es un supuesto, no un plan. La continuidad del negocio se estandariza en **ISO 22301**; las medidas físicas, en el anexo de controles físicos de ISO/IEC 27001.

## Seguridad física del puesto de trabajo

En un equipo de escritorio o portátil, lo pasivo se reduce a cuatro cosas: evitar que se lo lleven, evitar que lo abran, evitar que arranquen con otro medio y que, si se lo llevan, no puedan leer el disco.

Anclaje o candado Kensington para el robo, caja cerrada con detección de apertura para el interior, contraseña de UEFI y orden de arranque fijado en el disco interno para el LiveCD, y cifrado del disco —BitLocker o LUKS— para el último caso. La contraseña de firmas de UEFI y el arranque seguro se desarrollan en [el apunte de sistema operativo y aplicaciones](sistema-operativo-y-aplicaciones.md).

## Lo que ha cambiado

Hasta hace unos años el CPD era único, centralizado y con temperatura fija de 22 °C. Hoy el modelo habitual mezcla sala propia, colocation y nube; la temperatura se deja subir dentro del rango recomendado porque cada grado ahorra energía; y el respaldo ya no es solo otro edificio, sino réplica entre zonas. Los principios —doble suministro, pasillos separados, parada ordenada, esclusa, plan probado— no han cambiado.

## Fuentes

- UNE-EN 50600, serie de instalaciones e infraestructuras de centros de datos.
- ASHRAE, *Thermal Guidelines for Data Processing Environments*.
- ISO/IEC 27001:2022, controles físicos (anexo A, tema físico).
- ISO 22301, sistemas de gestión de la continuidad del negocio.
- Reglamento (UE) 2024/573, gases fluorados.
