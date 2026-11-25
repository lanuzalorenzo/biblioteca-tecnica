# Copias de seguridad y recuperación del motor

Un motor de base de datos no se copia como una carpeta de ficheros: mientras está en marcha, sus ficheros cambian por dentro y una copia directa puede parecer válida y no serlo. Lo que se copia es un estado coherente, y hay dos maneras de conseguirlo.


## Copia lógica y copia física

- **Lógica:** el motor exporta datos y estructura en un fichero de texto o binario —`pg_dump`, `mysqldump`, `BACKUP DATABASE`—. Es portable entre versiones y sirve para migrar; restaurar una base grande tarda mucho y no permite recuperar hasta un instante concreto sin encadenar copias.
- **Física:** se copian los ficheros de datos de forma coherente, con la herramienta del motor —`pg_basebackup`, copia con instantánea del volumen—. Es rápida y es la base de la recuperación a un punto en el tiempo.

Para un servidor en producción se usan las dos: física para recuperar rápido, lógica para migrar o para recuperar una tabla suelta.

## Recuperar hasta un instante

Los motores anotan cada cambio en un diario antes de aplicarlo: **WAL** en PostgreSQL, *binary log* en MySQL, *transaction log* en SQL Server. Archivar ese diario permite restaurar una copia base y **reproducir** los cambios hasta el segundo anterior al incidente.

Esa es la diferencia entre «recupero la copia de anoche y pierdo el día» y «recupero hasta las 11:47, justo antes del borrado». Requiere tres cosas configuradas de antemano: archivo del diario activo, copia base periódica y una prueba de que la cadena se puede reproducir.

## Lo que hay que decidir y dejar escrito

- **Qué se copia:** las bases, los roles y la configuración del motor. Copiar solo los datos deja un servidor que no arranca igual.
- **Cada cuánto:** según lo que se pueda perder. El RPO se negocia con el negocio, no se elige por comodidad.
- **Cuánto se conserva:** diarias, semanales, mensuales. La copia de ayer no sirve si el error se descubrió hace un mes.
- **Dónde:** fuera del servidor, en un medio que la cuenta comprometida no pueda borrar.
- **Quién restaura y cuánto tarda:** medido, no supuesto.

## La restauración se prueba

Una copia no está validada hasta que se restaura. Y no vale restaurar en el mismo servidor con el mismo administrador: se restaura en otro equipo, con la documentación que hay escrita y preferiblemente con otra persona.

Comprobaciones mínimas después de restaurar: el motor arranca, las cuentas existen, las claves ajenas están íntegras, el número de filas de las tablas grandes cuadra y la aplicación conecta.

```bash
pg_dump -Fc -f respaldo.dump basedatos          # copia lógica comprimida
createdb baseprueba && pg_restore -d baseprueba respaldo.dump
psql -d baseprueba -c "SELECT count(*) FROM pedidos;"
```

## Registro de la propia copia

Una copia sin registro no se puede auditar. Como mínimo, cada ejecución anota: cuándo, qué, tamaño, resultado y quién la revisó. Las herramientas lo escriben; el fallo silencioso —el trabajo que termina «bien» sin copiar nada— es el que hay que detectar con una comprobación de tamaño y fecha.

## Lo que se comprueba

Que la copia de anoche existe y tiene el tamaño esperado; que se restaura en un equipo distinto; que la aplicación funciona sobre la copia restaurada; que la cadena de diario permite recuperar un instante; y que el tiempo de restauración está medido y cabe en el RTO.

## Errores que se repiten

- Copiar los ficheros del motor con el servicio en marcha y sin mecanismo coherente.
- Guardar las copias en el mismo servidor o en el mismo volumen.
- Cifrar la copia y guardar la clave junto a ella.
- No copiar los roles: se recuperan los datos y nadie puede entrar.
- Descubrir el día del incidente que la copia llevaba un mes fallando.

## Órdenes de copia y vuelta atrás

```bash
pg_dump -Fc -f respaldo.dump basedatos            # lógica, comprimida
pg_restore -l respaldo.dump | head                # inventario del contenido
mysqldump --single-transaction --databases bd > bd.sql
mysql --binary-mode < binlog.000042               # reproducir el diario
```

`--single-transaction` toma la copia dentro de una transacción coherente sin bloquear las escrituras en InnoDB; sin esa opción, la copia puede mezclar estados.

Una réplica no es una copia. Replica los cambios, incluido el borrado accidental, y llega con el mismo retraso que el original. Sirve para repartir lecturas y para conmutar en un fallo del servidor, no para volver a un estado anterior. Confundir las dos cosas es cómo se descubre, la misma tarde, que no había copia.

La frecuencia se decide por lo que se puede perder, y la retención por cuánto tarda en descubrirse un error. Un borrado accidental detectado en minutos se arregla con una copia reciente; uno detectado a los dos meses exige conservar mensuales. Las dos cifras se escriben antes del primer incidente.

## Fuentes

- Documentación oficial de `pg_dump`, `pg_basebackup`, `mysqldump` y del registro de transacciones.
- ISO/IEC 27001:2022, control de copias de seguridad (A.8.13).
- NIST SP 800-34, guía de contingencias.
- Restaurar en producción para «probar rápido» y sobrescribir el estado actual.
