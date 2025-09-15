# Proyecto Flask + MySQL

Este proyecto es un ejemplo de cómo conectar una aplicación **Flask** con **MySQL**, cumpliendo los requisitos de la tarea de desarrollo web.

---

## 🚀 Instalación y configuración

### 1. Clonar el repositorio
```bash
git clone https://github.com/david/tu-proyecto-flask.git
cd tu-proyecto-flask
```

### 2. Crear entorno virtual e instalar dependencias
```bash
python -m venv venv
venv\Scripts\activate   # en Windows
source venv/bin/activate   # en Linux/Mac
pip install -r requirements.txt
```

### 3. Configurar conexión en `conexion.py`
- Usuario: `root`
- Contraseña: tu contraseña de MySQL
- Base de datos: `desarrollo_web`

### 4. Crear la base de datos y tabla en MySQL
```sql
CREATE DATABASE IF NOT EXISTS desarrollo_web;
USE desarrollo_web;

CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100),
    mail VARCHAR(100)
);
```

### 5. Ejecutar Flask
```bash
python app.py
```

---

## 📌 Rutas disponibles

- `http://localhost:5000/` → Prueba Flask  
- `http://localhost:5000/test_db` → Verifica conexión con MySQL  
- `http://localhost:5000/add_usuario` → Inserta usuario (POST con JSON)  
  Ejemplo:
  ```json
  {
    "nombre": "Juan",
    "mail": "juan@mail.com"
  }
  ```
- `http://localhost:5000/usuarios` → Lista usuarios registrados  

---

## 📂 Estructura del proyecto

```
tu-proyecto-flask/
│── app.py
│── conexion.py
│── requirements.txt
│── README.md
```

---

## ✅ Autor
Proyecto desarrollado por **David**  
Repositorio en GitHub: [https://github.com/david/tu-proyecto-flask](https://github.com/david/tu-proyecto-flask)
