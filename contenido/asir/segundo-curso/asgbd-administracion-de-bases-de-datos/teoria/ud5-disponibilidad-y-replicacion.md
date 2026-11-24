# UD5. Disponibilidad y replicación

Una copia de seguridad devuelve el sistema a un estado anterior; una réplica mantiene otro servidor al día para que el servicio no se caiga cuando el principal falla. Son dos seguros distintos: confundirlos es descubrir, en el peor momento, que se tenía el que no era.

> **Módulo:** ASGBD. Administración de sistemas gestores de bases de datos

## Dos objetivos, dos números

Antes de elegir tecnología hay que fijar dos objetivos:

- **RPO** (*recovery point objective*): cuántos datos se puede permitir perder. Una copia diaria da un RPO de hasta 24 horas; una réplica casi sincrónica, de segundos.
- **RTO** (*recovery time objective*): cuánto tiempo puede estar el servicio caído. Restaurar una copia puede tardar horas; conmutar a una réplica caliente, minutos.

Sin esos números, «alta disponibilidad» es una intención. Con ellos, se puede decidir si basta con copias, si hace falta réplica o si se necesita conmutación automática.

## Replicación: qué se copia y cómo

La réplica recibe los cambios del servidor principal y los aplica en el mismo orden. Dos formas de hacerlo:

- **Física:** se envían los bloques o el registro de transacciones —WAL en PostgreSQL, redo en otros motores—. La réplica es una copia binaria del principal.
- **Lógica:** se envían las operaciones o los cambios de fila —el *binlog* de MySQL, la replicación lógica de PostgreSQL—. Permite replicar solo una parte o entre versiones distintas, a cambio de más complejidad.

Según cuándo se confirma:

- **Asíncrona:** el principal confirma la transacción sin esperar a la réplica. Es rápida, pero si el principal cae puede perder los últimos cambios.
- **Sincrónica:** espera a que la réplica confirme. Reduce la pérdida, pero añade latencia y depende de que la réplica esté viva.

La mayoría de las instalaciones empiezan con asíncrona y añaden sincronía para lo crítico. La decisión se toma por datos, no por moda.

## Topologías

- **Principal–réplica:** una escribe, las demás leen. Es la más común; sirve para repartir lecturas y para conmutar.
- **Principal–réplica en cadena:** una réplica alimenta a otra; reduce la carga del principal, pero alarga el retraso.
- **Multiprincipal:** varios nodos aceptan escritura. Resuelve la disponibilidad a cambio de conflictos y de reglas de consenso.
- **Réplica retrasada:** se aplica con retraso deliberado para recuperar un borrado accidental. No sustituye a la copia, pero compra tiempo.

Repartir lecturas tiene trampa: una lectura inmediatamente después de una escritura puede llegar a una réplica que aún no la tiene. Se resuelve enviando esa lectura al principal o esperando la posición de replicación.

## Conmutación y cerebro partido

La **conmutación** (*failover*) promociona una réplica cuando el principal falla. Puede ser manual —más lenta, más controlada— o automática, con un orquestador que comprueba el estado y decide.

El riesgo es el **split-brain**: dos nodos se creen principales y aceptan escrituras divergentes. Se evita con cuórum: una mayoría de nodos debe coincidir en quién manda. Patroni, con su almacén de consenso, e InnoDB Cluster, con Group Replication, deciden quién manda; repmgr y otras herramientas asisten la promoción y la reconfiguración. No basta con un script que levante la réplica.

El **retraso de replicación** (*lag*) se vigila en segundos, no en impresiones. Si crece, la conmutación pierde más datos y las lecturas de la réplica devuelven información vieja.

## Copias y réplicas no se sustituyen

Una réplica recibe también el `DELETE` accidental, el `DROP TABLE` y el cifrado por *ransomware*: reproduce el error en segundos. La copia permite volver a un estado anterior; la réplica permite seguir funcionando. Una estrategia completa tiene:

- Copias periódicas con retención y prueba de restauración.
- Registro de transacciones archivado para recuperar un punto concreto.
- Réplica para disponibilidad y lecturas.
- Un procedimiento escrito de conmutación y vuelta atrás.

## Probarlo

Una alta disponibilidad que no se prueba es una hipótesis. Se ensaya la caída del principal, la promoción, la reconexión del antiguo principal como réplica y la vuelta al estado normal. Se mide cuánto tarda y cuántos datos se pierden. Si el ensayo no se hace en un entorno parecido al real, el día del incidente se estrena el procedimiento.

## Lo que se comprueba

Que RPO y RTO están escritos; que la replicación va al día; que la conmutación tiene un responsable y un procedimiento; que el cuórum evita el split-brain; que la copia se restaura sin depender de la réplica; y que el ensayo de caída se ha hecho con un resultado medido.

## Fuentes

- Documentación de PostgreSQL: write-ahead log, streaming replication y recuperación a un punto en el tiempo.
- Documentación de MySQL: binlog, replicación asíncrona y Group Replication; InnoDB Cluster.
- Documentación de Patroni y repmgr para conmutación y promoción.
- Orden EDU/392/2010, de 20 de enero, currículo del ciclo de ASIR (BOE-A-2010-3028), módulo 0377.
