<img src="../assets/iconos/hacking-etico.svg" width="64" alt="Hacking ético">

# Hacking ético

Una prueba de intrusión es un simulacro: se provoca un fuego controlado para comprobar cómo responde el edificio. La técnica ofensiva es real y el resultado importa, pero el ejercicio solo tiene sentido si hay permiso, un perímetro definido y alguien que corrija lo que se descubra. Sin esas tres piezas, el mismo trabajo deja de ser una auditoría y pasa a ser un delito.

Estas notas explican cómo se organiza una evaluación ofensiva profesional: qué distingue una prueba legítima, cómo se acuerda el alcance, qué fases tiene una intrusión, cómo se mide y se documenta un hallazgo, qué herramientas existen y dónde están los límites del auditor.

## Contenido

| Nota | Qué trata |
|---|---|
| [Fundamentos del hacking ético](fundamentos-de-hacking-etico.md) | Autorización, tríada CIA, vulnerabilidad, amenaza, riesgo e impacto |
| [Hacking, pentest y hacktivismo](hacking-pentest-y-hacktivismo.md) | Conceptos, principios éticos, marco legal y límites del anonimato |
| [Autorización y alcance](autorizacion-y-alcance.md) | Objetivos, exclusiones, reglas de actuación y documentos |
| [Fases de un ataque](fases-de-un-ataque.md) | Reconocimiento, acceso, consolidación, modelos y metodologías |
| [Severidad con CVSS](severidad-con-cvss.md) | Métricas, vector, escala y diferencia entre severidad y riesgo |
| [Caja negra, gris y blanca](caja-negra-gris-y-blanca.md) | Enfoques, prueba externa e interna, servicios y equipos de colores |
| [Documentar un hallazgo](documentar-un-hallazgo.md) | Anatomía del hallazgo, CVE, CWE, EPSS, informe y divulgación |
| [Clasificar herramientas](clasificar-herramientas.md) | Criterios, monitorización y elección según la organización |
| [Capas de internet](capas-de-internet.md) | ClearNet, Deep Web, darknets, Tor y límites legales |
| [Comunicación inalámbrica](comunicacion-inalambrica.md) | Medio compartido, bandas, tramas 802.11 y secuencia de asociación |
| [Protocolos de seguridad Wi-Fi](protocolos-de-seguridad-wifi.md) | WEP, TKIP, handshake de WPA2, PMKID y ataques conocidos |

## Límites de autorización y alcance

Este módulo describe técnicas ofensivas con fines formativos. Nada de lo que aparece aquí autoriza a probar un sistema ajeno.

- **Sin autorización escrita no hay prueba.** La concede el titular del sistema o quien tenga delegación expresa. Un técnico, un responsable de área o una conversación telefónica no bastan.
- **El alcance es la frontera.** Lo que no figura en el documento queda fuera, incluidos los sistemas de proveedores, el alojamiento compartido, la nube y los equipos personales. Salirse del alcance, aunque sea por curiosidad, convierte el acceso en no autorizado.
- **La autorización no cubre a terceros, datos personales ni derechos de las personas.** El secreto de las comunicaciones está protegido y la empresa no puede autorizar un delito.
- **El laboratorio debe estar aislado.** Las máquinas vulnerables no se conectan a la red de la organización, a la red doméstica ni a internet mediante un adaptador mal configurado.
- **Las referencias legales se contrastan** con el BOE y EUR-Lex antes de citarlas o aplicarlas. Las de este módulo son orientativas.
- **La técnica no clasifica la actividad.** Lo hacen la autorización, el alcance, la finalidad y el daño. Una buena intención no convierte un acceso no autorizado en una prueba ética.

## Cómo se leen

Las notas van de lo general a lo concreto: primero el marco ético y legal, después el encargo, la ejecución y la entrega. Cada una se apoya en las anteriores y enlaza a las que amplían el tema. Los ejemplos con dominios `.example` y rangos reservados son ficticios; ninguna cifra, captura ni hallazgo de estas páginas procede de un sistema real.
