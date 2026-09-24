from datetime import UTC, datetime

from sqlmodel import Session, SQLModel, create_engine, select

from app.models import (
    Albergue,
    AlbergueDetallePublic,
    AlbergueUsuario,
    AreaFuncional,
    EstadoEstancia,
    EstadoOperativoAlbergue,
    GrupoFamiliar,
    InventarioInfraestructura,
    InventarioRecursoHumano,
    InventarioSuministro,
    InventarioSuministroUpdate,
    PersonaRefugiada,
    RegistroSalidaRefugiado,
    RolOperativo,
    User,
)


def test_creacion_albergue_e_inventarios():
    """Valida la creacion de un albergue con sus tres inventarios y relaciones 1:1."""
    motor_bd = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(motor_bd)

    with Session(motor_bd) as sesion:
        # 1. Crear usuario responsable
        coordinador = User(
            email="coordinador.pc@oaxaca.gob.mx",
            hashed_password="hash_seguro_de_prueba",
            full_name="Coordinador de Proteccion Civil",
            is_superuser=False,
        )
        sesion.add(coordinador)
        sesion.commit()
        sesion.refresh(coordinador)

        # 2. Crear Albergue
        albergue = Albergue(
            folio_identificador="ALB-OAX-2026-001",
            nombre="Albergue Temporal Deportivo Hermanos Flores Magon",
            direccion="Calzada Madero 450, Centro",
            municipio="Oaxaca de Juarez",
            estado_republica="Oaxaca",
            latitud=17.0654,
            longitud=-96.7236,
            telefono_contacto="9515012345",
            estado_operativo=EstadoOperativoAlbergue.ACTIVADO,
            responsable_id=coordinador.id,
        )
        sesion.add(albergue)
        sesion.commit()
        sesion.refresh(albergue)

        # 3. Crear Inventario de Suministros (18 campos)
        suministros = InventarioSuministro(
            albergue_id=albergue.id,
            agua_potable=3500.0,
            alimentos_no_perecederos=1200,
            formula_infantil=80,
            medicamentos_basicos=150,
            material_curacion=200,
            cobijas=500,
            colchonetas=400,
            ropa=650,
            kits_higiene=300,
            panales=120,
            cubrebocas=1000,
            productos_limpieza=90,
            bolsas_residuos=150,
            linternas=45,
            pilas=180,
            extintores=12,
            herramientas=8,
            material_oficina=25,
        )

        # 4. Crear Inventario de Infraestructura (14 campos)
        infraestructura = InventarioInfraestructura(
            albergue_id=albergue.id,
            capacidad_maxima=450,
            dormitorios=8,
            banos=16,
            regaderas=12,
            cocina=2,
            comedor=1,
            consultorio=2,
            bodega=2,
            salidas_emergencia=6,
            extintores=14,
            accesos_silla_ruedas=True,
            planta_electrica=True,
            sistema_agua="Cisterna y Red Municipal",
            estado_inmueble="Operativo Seguro",
        )

        # 5. Crear Inventario de Recursos Humanos (12 campos)
        recursos_humanos = InventarioRecursoHumano(
            albergue_id=albergue.id,
            administrador=3,
            medicos=4,
            enfermeria=8,
            psicologia=3,
            cocineros=6,
            personal_limpieza=8,
            seguridad=6,
            trabajadores_sociales=4,
            traductores=2,
            voluntarios=35,
            conductores=4,
            responsables_bodega=2,
        )

        sesion.add_all([suministros, infraestructura, recursos_humanos])
        sesion.commit()

        # 6. Consultar y verificar la integridad de las relaciones
        consulta = select(Albergue).where(
            Albergue.folio_identificador == "ALB-OAX-2026-001"
        )
        albergue_recuperado = sesion.exec(consulta).first()

        assert albergue_recuperado is not None
        assert (
            albergue_recuperado.nombre
            == "Albergue Temporal Deportivo Hermanos Flores Magon"
        )
        assert albergue_recuperado.responsable is not None
        assert albergue_recuperado.responsable.email == "coordinador.pc@oaxaca.gob.mx"

        # Validacion de suministros
        inv_sum = albergue_recuperado.inventario_suministros
        assert inv_sum is not None
        assert inv_sum.agua_potable == 3500.0
        assert inv_sum.cobijas == 500
        assert inv_sum.cubrebocas == 1000

        # Validacion de infraestructura
        inv_inf = albergue_recuperado.inventario_infraestructura
        assert inv_inf is not None
        assert inv_inf.capacidad_maxima == 450
        assert inv_inf.planta_electrica is True
        assert inv_inf.accesos_silla_ruedas is True

        # Validacion de recursos humanos
        inv_rh = albergue_recuperado.inventario_recursos_humanos
        assert inv_rh is not None
        assert inv_rh.medicos == 4
        assert inv_rh.voluntarios == 35
        assert inv_rh.traductores == 2

        # 7. Validacion de esquema consolidado DTO
        detalle_publico = AlbergueDetallePublic.model_validate(albergue_recuperado)
        assert detalle_publico.folio_identificador == "ALB-OAX-2026-001"
        assert detalle_publico.inventario_suministros is not None
        assert detalle_publico.inventario_suministros.agua_potable == 3500.0
        assert detalle_publico.inventario_infraestructura is not None
        assert detalle_publico.inventario_infraestructura.capacidad_maxima == 450
        assert detalle_publico.inventario_recursos_humanos is not None
        assert detalle_publico.inventario_recursos_humanos.voluntarios == 35


def test_actualizaciones_parciales_inventarios():
    """Valida actualizaciones parciales en suministros, infraestructura y recursos humanos."""
    motor_bd = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(motor_bd)

    with Session(motor_bd) as sesion:
        albergue = Albergue(
            folio_identificador="ALB-PUE-002",
            nombre="Albergue Gimnasio Zaragoza",
            direccion="Diagonal Defensores 200",
            municipio="Puebla",
        )
        sesion.add(albergue)
        sesion.commit()
        sesion.refresh(albergue)

        suministros = InventarioSuministro(albergue_id=albergue.id, agua_potable=500.0)
        sesion.add(suministros)
        sesion.commit()

        # Actualizar con DTO parcial
        actualizacion = InventarioSuministroUpdate(agua_potable=1200.0, cobijas=150)
        suministros.sqlmodel_update(actualizacion.model_dump(exclude_unset=True))
        sesion.add(suministros)
        sesion.commit()
        sesion.refresh(suministros)

        assert suministros.agua_potable == 1200.0
        assert suministros.cobijas == 150
        assert suministros.alimentos_no_perecederos == 0


def test_eliminacion_en_cascada_albergue():
    """Verifica que al eliminar un albergue, se eliminen en cascada sus inventarios y datos satelites."""
    motor_bd = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(motor_bd)

    with Session(motor_bd) as sesion:
        albergue = Albergue(
            folio_identificador="ALB-VER-003",
            nombre="Albergue Puerto Seco",
            direccion="Av. Independencia 10",
            municipio="Veracruz",
        )
        sesion.add(albergue)
        sesion.commit()
        sesion.refresh(albergue)

        id_albergue = albergue.id
        suministros = InventarioSuministro(albergue_id=id_albergue, agua_potable=100.0)
        infra = InventarioInfraestructura(albergue_id=id_albergue, capacidad_maxima=50)
        rh = InventarioRecursoHumano(albergue_id=id_albergue, voluntarios=10)
        sesion.add_all([suministros, infra, rh])
        sesion.commit()

        # Eliminar albergue
        sesion.delete(albergue)
        sesion.commit()

        # Comprobar que no queden inventarios huerfanos
        sum_restante = sesion.exec(
            select(InventarioSuministro).where(
                InventarioSuministro.albergue_id == id_albergue
            )
        ).first()
        inf_restante = sesion.exec(
            select(InventarioInfraestructura).where(
                InventarioInfraestructura.albergue_id == id_albergue
            )
        ).first()
        rh_restante = sesion.exec(
            select(InventarioRecursoHumano).where(
                InventarioRecursoHumano.albergue_id == id_albergue
            )
        ).first()

        assert sum_restante is None
        assert inf_restante is None
        assert rh_restante is None


def test_roles_delegados_y_personas_refugiadas():
    """Valida los tres niveles de privilegios y el control de ingreso/egreso de personas refugiadas."""
    motor_bd = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(motor_bd)

    with Session(motor_bd) as sesion:
        # 1. Crear usuarios para los 3 roles
        admin_refugio = User(email="admin.refugio@pc.gob.mx", hashed_password="hash1")
        resp_recepcion = User(email="recepcion.jefe@pc.gob.mx", hashed_password="hash2")
        operativo_campo = User(
            email="voluntario.registro@pc.gob.mx", hashed_password="hash3"
        )
        sesion.add_all([admin_refugio, resp_recepcion, operativo_campo])
        sesion.commit()

        # 2. Crear Albergue
        albergue = Albergue(
            folio_identificador="ALB-TAB-004",
            nombre="Albergue Villahermosa Central",
            direccion="Av. Paseo Tabasco 500",
            municipio="Centro",
            estado_republica="Tabasco",
            estado_operativo=EstadoOperativoAlbergue.ACTIVADO,
        )
        sesion.add(albergue)
        sesion.commit()
        sesion.refresh(albergue)

        # 3. Asignar los 3 roles operativos con su area funcional
        asig_admin = AlbergueUsuario(
            albergue_id=albergue.id,
            usuario_id=admin_refugio.id,
            rol=RolOperativo.ADMINISTRADOR_ALBERGUE,
            area=AreaFuncional.GENERAL,
        )
        asig_resp = AlbergueUsuario(
            albergue_id=albergue.id,
            usuario_id=resp_recepcion.id,
            rol=RolOperativo.RESPONSABLE_AREA,
            area=AreaFuncional.RECEPCION_REGISTRO,
        )
        asig_operativo = AlbergueUsuario(
            albergue_id=albergue.id,
            usuario_id=operativo_campo.id,
            rol=RolOperativo.PERSONAL_OPERATIVO,
            area=AreaFuncional.RECEPCION_REGISTRO,
        )
        sesion.add_all([asig_admin, asig_resp, asig_operativo])
        sesion.commit()

        # 4. Crear Grupo Familiar
        familia = GrupoFamiliar(
            albergue_id=albergue.id,
            codigo_familia="FAM-TAB-001",
            nombre_referente="Hernandez Perez",
            total_integrantes=3,
            comunidad_origen="Gaviotas Sur",
            necesidades_especiales="Adulto mayor requiere insulina",
        )
        sesion.add(familia)
        sesion.commit()
        sesion.refresh(familia)

        # 5. Registro de Ingreso (Check-in) realizado por Personal Operativo
        refugiado = PersonaRefugiada(
            albergue_id=albergue.id,
            grupo_familiar_id=familia.id,
            folio_identificacion="REF-TAB-2026-001",
            nombre="Maria",
            apellido_paterno="Hernandez",
            apellido_materno="Perez",
            curp="HEPM800101MTBXXX01",
            genero="Femenino",
            municipio_origen="Centro",
            localidad_origen="Gaviotas Sur",
            adulto_mayor=False,
            embarazo=False,
            discapacidad=False,
            menor_de_edad=False,
            dormitorio_asignado="Dormitorio B",
            numero_cama_colchoneta="Cama 14",
            estado_estancia=EstadoEstancia.ALBERGADO,
            registrado_por_id=operativo_campo.id,
        )
        sesion.add(refugiado)
        sesion.commit()
        sesion.refresh(refugiado)

        # Comprobar relacion y estado activo
        assert refugiado.estado_estancia == EstadoEstancia.ALBERGADO
        assert refugiado.registrado_por is not None
        assert refugiado.registrado_por.email == "voluntario.registro@pc.gob.mx"
        assert refugiado.grupo_familiar.codigo_familia == "FAM-TAB-001"

        # 6. Registro de Egreso (Check-out) administrativo por Responsable de Area
        salida_dto = RegistroSalidaRefugiado(
            fecha_salida=datetime.now(UTC),
            motivo_salida="Reubicacion a casa de familiares",
            destino_salida="Calle Juarez 80, Comalcalco",
            observaciones="Se le entregaron 2 kits de higiene y provision de alimentos para 48h.",
            estado_estancia=EstadoEstancia.EGRESO_DEFINITIVO,
        )
        refugiado.sqlmodel_update(salida_dto.model_dump(exclude_unset=True))
        refugiado.egreso_por_id = resp_recepcion.id
        sesion.add(refugiado)
        sesion.commit()
        sesion.refresh(refugiado)

        assert refugiado.estado_estancia == EstadoEstancia.EGRESO_DEFINITIVO
        assert refugiado.egreso_por is not None
        assert refugiado.egreso_por.email == "recepcion.jefe@pc.gob.mx"
        assert refugiado.motivo_salida == "Reubicacion a casa de familiares"
        assert refugiado.fecha_salida is not None
