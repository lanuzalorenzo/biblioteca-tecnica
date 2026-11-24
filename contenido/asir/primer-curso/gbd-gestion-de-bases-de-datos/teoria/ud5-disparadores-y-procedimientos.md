# UD5. Disparadores y procedimientos

Hay reglas que no dependen de quién escribe: un pedido servido no puede volver a abierto, un movimiento bancario tiene que dejar rastro en el saldo. Cuando esa regla vive fuera de la base de datos, cada programa la implementa a su manera y uno acaba olvidándola. Ponerla dentro es lo que garantiza que se cumpla siempre.

> **Módulo:** GBD. Gestión de bases de datos

## Qué es un disparador

Un **trigger** es código que el motor ejecuta solo cuando ocurre un evento sobre una tabla: antes o después de insertar, modificar o borrar.

- **BEFORE:** puede validar y modificar la fila antes de que se guarde. Si lanza un error, la operación no se realiza.
- **AFTER:** actúa cuando el cambio ya está hecho. Sirve para auditar, propagar o recalcular.
- **Por fila o por sentencia:** uno se ejecuta por cada fila afectada; el otro, una vez. La diferencia importa cuando una orden toca diez mil filas.

Un uso típico y legítimo:

```sql
CREATE TRIGGER tr_pedido_servido
BEFORE UPDATE ON pedidos
FOR EACH ROW
BEGIN
  IF OLD.estado = 'servido' AND NEW.estado = 'abierto' THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'un pedido servido no se reabre';
  END IF;
END;
```

## Qué se puede y qué no se debe

Los disparadores son potentes y se abusa de ellos por tres motivos:

- **No se ven.** Quien consulta la tabla no sabe que hay lógica detrás; el comportamiento «raro» se investiga durante horas.
- **Se encadenan.** Un disparador que escribe en otra tabla puede disparar el de esa tabla. Algunos motores limitan la profundidad; otros no, y el resultado es un efecto en cascada imposible de seguir.
- **No se prueban como el código.** No hay un repositorio que los revise ni un test que los cubra si no se escriben.

Un criterio práctico: el disparador para **garantizar un invariante** —algo que nunca puede ocurrir— y para **auditar**. Para lógica de negocio con varios pasos, mejor un procedimiento que alguien llama a propósito.

## Procedimientos y funciones

- **Procedimiento:** ejecuta acciones, puede recibir parámetros de entrada y salida, y no devuelve un valor por sí mismo. Se invoca con `CALL`.
- **Función:** devuelve un valor y se usa dentro de una consulta. No debería modificar datos.

En el material del módulo aparecen ejemplos de los dos: funciones que calculan cargos o ingresos, y procedimientos que registran movimientos bancarios. La lógica de un movimiento —comprobar saldo, insertar, actualizar— es exactamente un procedimiento con transacción, no un disparador.

```sql
CREATE PROCEDURE mover_saldo(IN p_cuenta INT, IN p_importe DECIMAL(12,2))
BEGIN
  START TRANSACTION;
    UPDATE cuentas SET saldo = saldo + p_importe WHERE id_cuenta = p_cuenta;
    INSERT INTO movimientos (id_cuenta, importe, fecha) VALUES (p_cuenta, p_importe, NOW());
  COMMIT;
END;
```

## Leer el resultado de un ejercicio

En los ejercicios resueltos del material se ve el patrón de trabajo: se identifica la tabla que cambia, se decide si la regla es un invariante o una acción, se elige `BEFORE` o `AFTER`, y se prueba con un caso que debe fallar. El caso que debe fallar es el que demuestra que el código sirve; el que funciona solo confirma que no estorba.

## Lo que se comprueba

Que el disparador impide el cambio indebido y no bloquea el legítimo; que no se dispara en cascada sin control; que los procedimientos abren y cierran transacción; que un error a mitad deja los datos como estaban; y que todo esto está en un guion versionado, no escrito a mano en el servidor.

## Errores que se repiten

- Un disparador `AFTER` que actualiza la misma tabla que lo lanzó.
- Procedimientos sin manejo de errores que dejan datos a medias.
- Reglas de negocio repartidas entre disparador, aplicación y base de datos.
- Validar en el disparador lo que ya impedía una restricción.

| Necesidad | Dónde va |
|---|---|
| Un valor obligatorio o un rango | Restricción (`NOT NULL`, `CHECK`) |
| Que un estado no pueda volver atrás | Disparador `BEFORE` |
| Dejar rastro de quién cambió qué | Disparador `AFTER` sobre tabla de auditoría |
| Una operación de varios pasos | Procedimiento con transacción |

## Fuentes

- ISO/IEC 9075 (SQL), parte de rutinas y disparadores.
- Documentación de MySQL/MariaDB y PostgreSQL sobre triggers y procedimientos.
