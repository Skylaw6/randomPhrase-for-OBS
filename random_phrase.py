__author__ = "Skylaw6"
__version__ = "1.1.0"
__contact__ = "skylaw6@hotmail.com"

import obspython as obs
import datetime
import random
import os

# Variables globales
interval = 30
source_name = ""
file_path = ""
ultima_frase = None

# ------------------------------------------------------------
# Función principal: actualiza el texto en la fuente seleccionada
# ------------------------------------------------------------
def update_text():
    global interval, source_name, file_path, ultima_frase

    if not source_name:
        obs.script_log(obs.LOG_WARNING, "No se ha seleccionado una fuente de texto.")
        return

    source = obs.obs_get_source_by_name(source_name)
    if source is None:
        obs.script_log(obs.LOG_WARNING, f"No se encontró la fuente: {source_name}")
        return

    # Si no hay archivo, mostrar advertencia
    if not file_path or not os.path.isfile(file_path):
        text = "Archivo de frases no encontrado."
        obs.script_log(obs.LOG_WARNING, f"Archivo no válido: {file_path}")
    else:
        try:
            # Leer frases del archivo
            with open(file_path, "r", encoding="utf-8") as f:
                frases = [line.strip() for line in f if line.strip()]

            if not frases:
                text = "El archivo de frases está vacío."
                obs.script_log(obs.LOG_WARNING, "El archivo de frases no contiene texto.")
            else:
                # Evitar repetir la última frase
                nueva_frase = ultima_frase
                while nueva_frase == ultima_frase and len(frases) > 1:
                    nueva_frase = random.choice(frases)
                ultima_frase = nueva_frase
                text = nueva_frase
                obs.script_log(obs.LOG_INFO, f"Frase mostrada: {text}")

        except Exception as e:
            text = f"Error leyendo archivo: {e}"
            obs.script_log(obs.LOG_ERROR, text)

    # Actualizar texto en OBS
    settings = obs.obs_data_create()
    obs.obs_data_set_string(settings, "text", text)
    obs.obs_source_update(source, settings)

    # Liberar memoria
    obs.obs_data_release(settings)
    obs.obs_source_release(source)


# ------------------------------------------------------------
# Botón manual para refrescar la frase
# ------------------------------------------------------------
def refresh_pressed(props, prop):
    update_text()


# ------------------------------------------------------------
# Descripción visible en el panel de scripts de OBS
# ------------------------------------------------------------
def script_description():
    return (
        "Muestra una frase aleatoria desde un archivo de texto.\n\n"
        "• Selecciona un archivo con frases (una por línea).\n"
        "• Asigna una fuente de texto.\n"
        "• Cambia el intervalo si quieres actualización automática.\n"
        "\nPor Skylaw6"
    )


# ------------------------------------------------------------
# Se ejecuta cuando el usuario cambia las propiedades del script
# ------------------------------------------------------------
def script_update(settings):
    global interval, source_name, file_path

    interval = obs.obs_data_get_int(settings, "interval")
    source_name = obs.obs_data_get_string(settings, "source")
    file_path = obs.obs_data_get_string(settings, "file")

    # Reiniciar el temporizador
    obs.timer_remove(update_text)
    if file_path and source_name:
        obs.timer_add(update_text, interval * 1000)
        obs.script_log(obs.LOG_INFO, f"Script iniciado: actualizando cada {interval} segundos.")


# ------------------------------------------------------------
# Valores por defecto de las propiedades
# ------------------------------------------------------------
def script_defaults(settings):
    obs.obs_data_set_default_int(settings, "interval", 10)


# ------------------------------------------------------------
# Propiedades visibles en el panel de OBS
# ------------------------------------------------------------
def script_properties():
    props = obs.obs_properties_create()

    obs.obs_properties_add_path(props, "file", "Archivo de frases", obs.OBS_PATH_FILE, "*.txt", "")
    obs.obs_properties_add_int(props, "interval", "Intervalo de actualización (segundos)", 5, 3600, 1)

    # Lista de fuentes de texto
    p = obs.obs_properties_add_list(
        props, "source", "Fuente de texto",
        obs.OBS_COMBO_TYPE_EDITABLE, obs.OBS_COMBO_FORMAT_STRING
    )

    sources = obs.obs_enum_sources()
    if sources is not None:
        for source in sources:
            source_id = obs.obs_source_get_unversioned_id(source)
            if source_id in ("text_gdiplus", "text_ft2_source"):
                name = obs.obs_source_get_name(source)
                obs.obs_property_list_add_string(p, name, name)
        obs.source_list_release(sources)

    # Botón para actualizar manualmente
    obs.obs_properties_add_button(props, "button", "Refrescar frase", refresh_pressed)

    return props
