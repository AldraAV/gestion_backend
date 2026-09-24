import uuid
from datetime import datetime

from pydantic import BaseModel


class PersonaAlbergadaItemDashboard(BaseModel):
    id: uuid.UUID
    folio_identificacion: str
    nombre_completo: str
    genero: str | None = None
    dormitorio_asignado: str | None = None
    numero_cama_colchoneta: str | None = None
    estado_estancia: str
    fecha_ingreso: datetime
    # Campos medicos y sensibles (solo para admin o salud)
    condicion_medica: str | None = None
    discapacidad: bool | None = None
    necesidad_especial: str | None = None


class ResumenInfraestructuraDashboard(BaseModel):
    capacidad_maxima: int
    ocupacion_actual: int
    cupo_disponible: int
    porcentaje_ocupacion: float
    semaforo: str  # verde, ambar, rojo, inactivo
    dormitorios: int
    banos: int
    regaderas: int
    cocina: int
    comedor: int
    consultorio: int
    bodega: int
    salidas_emergencia: int
    extintores_instalados: int
    accesos_silla_ruedas: bool
    planta_electrica: bool
    sistema_agua: str
    estado_inmueble: str


class ResumenRecursoHumanoDashboard(BaseModel):
    personal_administracion: int
    personal_medicos: int
    personal_enfermeria: int
    personal_psicologia: int
    personal_cocineros: int
    personal_limpieza: int
    personal_seguridad: int
    personal_voluntarios: int
    total_personal_salud: int


class ResumenSuministrosDashboard(BaseModel):
    agua_potable_litros: float
    agua_litros_por_persona: float
    alerta_agua_critica: bool
    raciones_alimentos: int
    raciones_por_persona: float
    alerta_alimentos_critica: bool
    colchonetas_disponibles: int
    alerta_colchonetas_deficit: bool
    cobijas_disponibles: int
    kits_higiene_disponibles: int
    medicamentos_cajas: int
    material_curacion_paquetes: int
    extintores_reserva: int


class AdministradorACargo(BaseModel):
    id: uuid.UUID
    nombre: str
    email: str
    rol: str


class DashboardAlbergueRespuesta(BaseModel):
    albergue_id: uuid.UUID
    folio_identificador: str
    nombre: str
    municipio: str
    localidad: str | None = None
    direccion: str
    estado_operativo: str
    semaforo: str
    fecha_ultimo_corte: datetime | None = None
    administrador_a_cargo: AdministradorACargo | None = None
    infraestructura: ResumenInfraestructuraDashboard
    recurso_humano: ResumenRecursoHumanoDashboard
    suministros: ResumenSuministrosDashboard
    personas_albergadas: list[PersonaAlbergadaItemDashboard]
    total_personas_registradas: int
