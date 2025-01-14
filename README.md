# 3D Game Project

Este proyecto es un juego en 3D que permite explorar una habitación cargada desde un archivo OBJ. A continuación se detallan los componentes del proyecto y cómo ejecutarlo.

## Estructura del Proyecto

```
3d-game-project
├── assets
│   └── rooms
│       └── room1.obj
├── src
│   ├── game.py
│   ├── graphics.py
│   ├── input.py
│   └── utils.py
├── requirements.txt
└── README.md
```

## Archivos Principales

- **assets/rooms/room1.obj**: Representación 3D de la habitación en formato OBJ.
- **src/game.py**: Punto de entrada del juego que inicializa el entorno 3D y gestiona el bucle principal.
- **src/graphics.py**: Maneja la renderización de gráficos en 3D.
- **src/input.py**: Gestiona la entrada del usuario.
- **src/utils.py**: Contiene funciones utilitarias para el proyecto.

## Requisitos

Para instalar las dependencias necesarias, asegúrate de tener `pip` instalado y ejecuta:

```
pip install -r requirements.txt
```

## Ejecución del Juego

Para ejecutar el juego, utiliza el siguiente comando:

```
python src/game.py
```

## Contribuciones

Las contribuciones son bienvenidas. Si deseas contribuir, por favor abre un issue o envía un pull request.