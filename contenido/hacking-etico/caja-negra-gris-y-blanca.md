# Caja negra, gris y blanca

Un mismo edificio se puede revisar desde la calle, con las llaves del propietario o con el plano y una copia de la llave. Cada opción responde a una pregunta distinta y cuesta distinto. En una auditoría de seguridad, la pregunta equivalente es cuánta información recibe el equipo antes de empezar.

## La pregunta de la caja

La metáfora viene de la ingeniería: una caja negra deja ver entradas y salidas, y una caja blanca deja ver el interior. Trasladada a la auditoría, la pregunta es cuánto sabe el auditor del objetivo. De esa respuesta dependen el método, el coste y el tipo de hallazgo que se espera.

Conviene deshacer un equívoco: en el desarrollo de software, «prueba de caja negra» y «de caja blanca» son categorías de las pruebas de calidad. Aquí designan el enfoque de un encargo completo sobre sistemas en producción o preproducción, no una técnica de pruebas unitarias.

## Caja negra

El auditor parte sin información o con la mínima, como un atacante externo sin relación con la organización: quizá solo un nombre y un dominio. Tiene que descubrir por su cuenta la superficie de ataque, las tecnologías y los puntos débiles, empezando por un reconocimiento serio.

Su ventaja es el realismo: refleja lo que conseguiría alguien desde fuera sin privilegios. Sus límites son el tiempo —buena parte del esfuerzo se va en descubrir lo que el cliente ya sabe— y la cobertura, porque lo que no se encuentra no se prueba. Un atacante real dispone de semanas; un encargo, de unos días. De ahí el riesgo de falsa tranquilidad cuando el informe concluye «no hemos podido entrar» y el motivo era el calendario.

## Caja gris

Es el término medio y el más frecuente en la práctica. El auditor recibe información parcial: una cuenta de usuario con un rol concreto, el esquema de la red sin credenciales de administración o un equipo ya dentro del dominio. Combina buena parte del realismo de la caja negra con la eficiencia de la blanca y permite una pregunta muy útil: si un empleado, un cliente o alguien que ya ha entrado quisiera abusar del sistema, ¿hasta dónde llegaría?

## Caja blanca

El auditor recibe información completa o casi completa: diagramas, inventario, documentación, cuentas de varios niveles y, si se audita una aplicación, el código fuente. La ventaja es profundidad y eficiencia: sin tiempo perdido en descubrir, todo el esfuerzo va a buscar fallos, incluidos los de lógica o diseño que desde fuera no se ven. El límite es que no simula a un atacante real y que exige que el cliente entregue material muy sensible, con lo que la confidencialidad y los controles del encargo pasan a primer plano.

## Los tres enfoques en paralelo

| | Caja negra | Caja gris | Caja blanca |
|---|---|---|---|
| Qué sabe el auditor | Solo el nombre o la dirección | Lo que un usuario legítimo | Todo, con acceso privilegiado |
| Aplicación web | La URL pública, sin cuentas | Cuentas de varios roles | Código, arquitectura y entorno de pruebas |
| Red | Descubre desde internet qué existe | Esquema de red y cuenta sin privilegios | Diagramas, inventario y cuentas altas |
| Pregunta que responde | ¿Qué logra un externo sin información? | ¿Qué logra un acceso legítimo limitado? | ¿Qué fallos existen, se encuentren o no desde fuera? |
| Ventaja | Realismo | Equilibrio | Profundidad y cobertura |
| Limitación | Coste en tiempo y cobertura incompleta | Depende de la información entregada | No simula a un atacante; exige confianza |
| Esfuerzo para la misma cobertura | Alto | Medio | Menor |

La caja negra no es la prueba «de verdad» ni la blanca una trampa: un test de intrusión busca encontrar el máximo de problemas con los recursos disponibles, y la información es una herramienta para lograrlo. Una caja blanca bien hecha suele producir más y mejores hallazgos por jornada. La elección depende de qué quiera saber el cliente.

## Dos decisiones que se combinan con el enfoque

**Desde dónde se prueba.** Una prueba externa evalúa lo alcanzable desde internet: servicios publicados, portales, correo y accesos remotos. Una interna parte de un punto dentro de la red, con la perspectiva de un empleado, un visitante con una toma de red o un atacante que ya controla un equipo. Muchas organizaciones tienen un perímetro razonable y un interior blando. El compromiso asumido ahorra tiempo al dar por hecho el acceso inicial y equivale, en la práctica, a una caja gris interna.

**Quién sabe que hay una prueba.** En una prueba anunciada el equipo defensivo está informado y se evalúan sobre todo las debilidades técnicas. En una no anunciada solo un grupo de control conoce el ejercicio y lo que se mide es la detección y la respuesta. Esta modalidad exige reglas claras para que una detección no desencadene una respuesta real desproporcionada.

## Servicios que se confunden

| Servicio | Pregunta que responde | Sigilo | Resultado típico |
|---|---|---|---|
| Evaluación de vulnerabilidades | ¿Qué debilidades conocidas tenemos y cuáles pesan más? | Ninguno | Lista priorizada, normalmente sin explotar |
| Test de intrusión | ¿Se pueden explotar y con qué impacto? | Bajo o nulo | Informe con pruebas y recomendaciones |
| Ejercicio de equipo rojo | ¿Un adversario realista alcanza el objetivo sin ser detectado? | Alto | Narrativa del ataque y tiempos de detección |
| Ejercicio de equipo púrpura | ¿Cómo mejoramos juntos la detección de estas técnicas? | Ninguno | Reglas de detección nuevas |
| Auditoría de cumplimiento | ¿Cumplimos la norma? | Ninguno | Conformidades y no conformidades |
| Programa de recompensas | ¿Qué encuentran investigadores externos de forma continua? | Ninguno | Informes individuales con recompensa |

No son sustitutivos: se complementan y corresponden a momentos distintos de madurez.

## Equipo rojo, azul, púrpura y blanco

El equipo rojo ataca y simula a un adversario. El azul defiende: monitoriza, detecta, responde y refuerza. El púrpura no suele ser un grupo aparte, sino una forma de trabajar en la que rojo y azul comparten en tiempo real lo que hacen y lo que ven para convertir cada técnica ofensiva en una mejora de detección. El blanco es el grupo reducido que controla el ejercicio, conoce ambos lados y puede detenerlo.

En sectores regulados, algunos ejercicios de equipo rojo son obligatorios. En el ámbito financiero europeo se habla de pruebas de penetración dirigidas por amenazas, articuladas en marcos como TIBER-EU; conviene comprobar el texto vigente antes de citarlos como requisito.

## Cómo elegir

No hay una respuesta universal, pero sí criterios que ordenan la decisión: el objetivo, la madurez de la organización, el tiempo y el presupuesto, el riesgo tolerado sobre producción, los requisitos regulatorios o contractuales y la naturaleza del activo. No se audita igual un perímetro externo, que conviene ver desde fuera, que una aplicación nueva, donde el código y las cuentas de prueba multiplican la eficacia.

La madurez merece un apartado propio porque es el error de planteamiento más caro. Las evaluaciones forman una escalera: primero la higiene básica y la evaluación de vulnerabilidades periódica; después los tests de intrusión de caja gris, externos e internos; más arriba los ejercicios menos anunciados; y en la cima los ejercicios de rojo y púrpura continuos. Un equipo rojo contra una organización sin parches ni registros centralizados es un desperdicio: entrará con técnicas elementales y el azul no verá nada porque no tiene con qué verlo.

## Un caso para razonar

El gerente de una empresa mediana plantea tres preocupaciones: va a abrir un módulo del portal donde los clientes subirán facturas; le preocupa qué pasaría si un empleado de administración cae en un correo fraudulento; y un cliente importante le ha preguntado si detectarían un ataque. La empresa tiene un administrador, un proveedor de mantenimiento y ningún centro de operaciones; los registros no están centralizados.

- **Módulo nuevo**: test de intrusión de caja gris o blanca sobre preproducción, con cuentas de varios roles y revisión de código si es posible. La caja negra tras el lanzamiento queda como verificación externa posterior.
- **Empleado que cae en un correo**: prueba interna con compromiso asumido, entregando un equipo y una cuenta estándar. Un *phishing* simulado exige autorización específica y coordinación con personas y asesoría jurídica.
- **«¿Detectaríamos un ataque?»**: todavía no es el momento de un equipo rojo. Primero registros centralizados y detección básica, además de una evaluación externa periódica; después, un ejercicio púrpura pequeño.

La tercera respuesta es la que más enseña: una recomendación profesional no siempre es vender el servicio más vistoso, sino decir qué hace falta antes de lo que el cliente cree necesitar.

## Errores frecuentes

- Creer que la caja negra es la única prueba seria y que la blanca es hacer trampa.
- Confundir estos enfoques con las pruebas de caja negra y blanca del control de calidad.
- Dar un escaneo automático por un test de intrusión.
- Contratar un equipo rojo sin capacidad de detección.
- No fijar el enfoque en el documento de alcance, o fijarlo de forma ambigua.
- Elegir el servicio que impresiona en lugar del que responde a la pregunta del cliente.

## Glosario

| Término | Definición |
|---|---|
| Compromiso asumido | Prueba que parte de un acceso inicial ya conseguido. |
| Equipo blanco | Grupo de control que conoce el ejercicio y puede detenerlo. |
| TIBER-EU | Marco europeo de pruebas de penetración dirigidas por amenazas. |
| Prueba no anunciada | Ejercicio que el equipo defensivo desconoce. |

## Fuentes

- NIST. *SP 800-115, Technical Guide to Information Security Testing and Assessment*.
- PTES: *Penetration Testing Execution Standard*.
- Banco Central Europeo. *TIBER-EU Framework*.
