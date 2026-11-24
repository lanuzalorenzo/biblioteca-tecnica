# Servicios orientados a eventos

Un servicio orientado a eventos reacciona a hechos en lugar de preguntar por el estado: algo ocurre, se publica un evento y cada servicio interesado actúa. El emisor no sabe quién escucha ni espera respuesta, y quien escucha decide qué hacer con el aviso.

## Evento, comando y mensaje

Un comando es una orden dirigida a alguien concreto y espera un efecto; un evento es un hecho ocurrido, en pasado y sin destinatario. Un mensaje es la unidad que viaja por una cola o un bus y puede llevar cualquiera de los dos. Confundirlos lleva a diseñar servicios que esperan respuesta donde no la hay.

## Event Grid

Event Grid distribuye eventos discretos: una notificación pequeña, entregada a los servicios suscritos con reintentos. Un tema es el punto de publicación y una suscripción dice a dónde va cada evento, con filtros por tipo o por asunto. Habla CloudEvents 1.0, un formato estándar que evita reescribir el emisor al cambiar de proveedor.

## Event Hubs

Event Hubs ingiere flujos: muchos eventos por segundo, en orden dentro de cada partición, disponibles para que uno o varios consumidores los lean por su cuenta. Los grupos de consumidores permiten leer el mismo flujo desde dos sitios sin quitarse nada, y Capture guarda el histórico en bruto sin escribir código.

## Cuándo cada uno

Event Grid para reaccionar a hechos puntuales y enrutar por tipo; Event Hubs para procesar un torrente continuo y releerlo. En los dos casos la entrega es de al menos una vez y el consumidor tiene que ser idempotente.
