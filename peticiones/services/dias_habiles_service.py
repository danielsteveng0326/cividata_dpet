# services/dias_habiles_service.py
"""
Servicio para calcular días hábiles considerando:
- Sábados y domingos (NO son días hábiles)
- Festivos nacionales de Colombia
- Días no hábiles personalizados configurados por el administrador
"""
from datetime import date, timedelta
from ..models import DiaNoHabil


class DiasHabilesService:
    """
    Servicio para gestionar cálculos de días hábiles
    """
    
    # Festivos fijos de Colombia
    FESTIVOS_FIJOS = {
        (1, 1): "Año Nuevo",
        (5, 1): "Día del Trabajo",
        (7, 20): "Día de la Independencia",
        (8, 7): "Batalla de Boyacá",
        (12, 8): "Día de la Inmaculada Concepción",
        (12, 25): "Navidad"
    }
    
    @staticmethod
    def es_fin_de_semana(fecha):
        """Verifica si una fecha es sábado o domingo"""
        return fecha.weekday() in [5, 6]  # 5=sábado, 6=domingo
    
    @staticmethod
    def es_festivo_fijo(fecha):
        """Verifica si una fecha es un festivo fijo de Colombia"""
        return (fecha.month, fecha.day) in DiasHabilesService.FESTIVOS_FIJOS
    
    @staticmethod
    def calcular_lunes_festivo(fecha_base, mes, dia):
        """
        Calcula el lunes festivo más cercano para festivos que se trasladan
        según la Ley Emiliani en Colombia
        """
        fecha = date(fecha_base.year, mes, dia)
        dias_hasta_lunes = (7 - fecha.weekday()) % 7
        if dias_hasta_lunes == 0:
            return fecha
        return fecha + timedelta(days=dias_hasta_lunes)
    
    @staticmethod
    def obtener_festivos_movibles(año):
        """
        Retorna los festivos que se trasladan al lunes siguiente
        según la Ley Emiliani (Ley 51 de 1983)
        """
        festivos_movibles = []
        
        # Festivos que se trasladan al lunes siguiente
        festivos_a_trasladar = [
            (1, 6, "Día de los Reyes Magos"),
            (3, 19, "Día de San José"),
            (6, 29, "San Pedro y San Pablo"),
            (8, 15, "Asunción de la Virgen"),
            (10, 12, "Día de la Raza"),
            (11, 1, "Día de Todos los Santos"),
            (11, 11, "Independencia de Cartagena"),
        ]
        
        fecha_base = date(año, 1, 1)
        for mes, dia, nombre in festivos_a_trasladar:
            fecha_festivo = DiasHabilesService.calcular_lunes_festivo(fecha_base, mes, dia)
            festivos_movibles.append(fecha_festivo)
        
        return festivos_movibles
    
    @staticmethod
    def es_festivo_movible(fecha):
        """Verifica si una fecha es un festivo movible"""
        festivos_movibles = DiasHabilesService.obtener_festivos_movibles(fecha.year)
        return fecha in festivos_movibles
    
    @staticmethod
    def calcular_semana_santa(año):
        """
        Calcula las fechas de Jueves y Viernes Santo
        Usando el algoritmo de Butcher para calcular la Pascua
        """
        # Algoritmo de Butcher para calcular la Pascua
        a = año % 19
        b = año // 100
        c = año % 100
        d = b // 4
        e = b % 4
        f = (b + 8) // 25
        g = (b - f + 1) // 3
        h = (19 * a + b - d - g + 15) % 30
        i = c // 4
        k = c % 4
        l = (32 + 2 * e + 2 * i - h - k) % 7
        m = (a + 11 * h + 22 * l) // 451
        mes = (h + l - 7 * m + 114) // 31
        dia = ((h + l - 7 * m + 114) % 31) + 1
        
        # Fecha de Pascua (Domingo de Resurrección)
        pascua = date(año, mes, dia)
        
        # Jueves Santo (3 días antes de Pascua)
        jueves_santo = pascua - timedelta(days=3)
        # Viernes Santo (2 días antes de Pascua)
        viernes_santo = pascua - timedelta(days=2)
        
        return [jueves_santo, viernes_santo]
    
    @staticmethod
    def es_semana_santa(fecha):
        """Verifica si una fecha es Jueves o Viernes Santo"""
        fechas_semana_santa = DiasHabilesService.calcular_semana_santa(fecha.year)
        return fecha in fechas_semana_santa
    
    @staticmethod
    def es_dia_no_habil_personalizado(fecha):
        """Verifica si una fecha está marcada como día no hábil personalizado"""
        return DiaNoHabil.objects.filter(fecha=fecha, activo=True).exists()
    
    @staticmethod
    def es_dia_habil(fecha):
        """
        Verifica si una fecha es un día hábil
        Un día NO es hábil si:
        - Es fin de semana (sábado o domingo)
        - Es festivo fijo
        - Es festivo movible (Ley Emiliani)
        - Es Semana Santa (Jueves o Viernes Santo)
        - Está marcado como día no hábil personalizado
        """
        if DiasHabilesService.es_fin_de_semana(fecha):
            return False
        
        if DiasHabilesService.es_festivo_fijo(fecha):
            return False
        
        if DiasHabilesService.es_festivo_movible(fecha):
            return False
        
        if DiasHabilesService.es_semana_santa(fecha):
            return False
        
        if DiasHabilesService.es_dia_no_habil_personalizado(fecha):
            return False
        
        return True
    
    @staticmethod
    def calcular_fecha_vencimiento(fecha_inicio, dias_habiles=15):
        """
        Calcula la fecha de vencimiento sumando días hábiles a partir de una fecha
        
        Args:
            fecha_inicio: Fecha de inicio (puede ser datetime o date)
            dias_habiles: Cantidad de días hábiles a sumar (por defecto 15)
        
        Returns:
            date: Fecha de vencimiento
        """
        # Si es datetime, convertir a date
        if hasattr(fecha_inicio, 'date'):
            fecha_actual = fecha_inicio.date()
        else:
            fecha_actual = fecha_inicio
        
        dias_sumados = 0
        
        while dias_sumados < dias_habiles:
            fecha_actual += timedelta(days=1)
            
            if DiasHabilesService.es_dia_habil(fecha_actual):
                dias_sumados += 1
        
        return fecha_actual
    
    @staticmethod
    def contar_dias_habiles_entre_fechas(fecha_inicio, fecha_fin):
        """
        Cuenta los días hábiles entre dos fechas (sin incluir fecha_inicio)
        
        Args:
            fecha_inicio: Fecha de inicio
            fecha_fin: Fecha de fin
        
        Returns:
            int: Cantidad de días hábiles
        """
        # Si son datetime, convertir a date
        if hasattr(fecha_inicio, 'date'):
            fecha_inicio = fecha_inicio.date()
        if hasattr(fecha_fin, 'date'):
            fecha_fin = fecha_fin.date()
        
        dias_habiles = 0
        fecha_actual = fecha_inicio + timedelta(days=1)
        
        while fecha_actual <= fecha_fin:
            if DiasHabilesService.es_dia_habil(fecha_actual):
                dias_habiles += 1
            fecha_actual += timedelta(days=1)
        
        return dias_habiles
    
    @staticmethod
    def obtener_descripcion_dia_no_habil(fecha):
        """
        Obtiene la descripción de por qué un día no es hábil
        
        Returns:
            str: Descripción del motivo
        """
        if DiasHabilesService.es_fin_de_semana(fecha):
            dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
            return f"{dias[fecha.weekday()]} (Fin de semana)"
        
        if DiasHabilesService.es_festivo_fijo(fecha):
            return DiasHabilesService.FESTIVOS_FIJOS.get((fecha.month, fecha.day))
        
        if DiasHabilesService.es_semana_santa(fecha):
            fechas_semana_santa = DiasHabilesService.calcular_semana_santa(fecha.year)
            if fecha == fechas_semana_santa[0]:
                return "Jueves Santo"
            return "Viernes Santo"
        
        if DiasHabilesService.es_festivo_movible(fecha):
            return "Festivo (Ley Emiliani)"
        
        # Buscar en días no hábiles personalizados
        dia_no_habil = DiaNoHabil.objects.filter(fecha=fecha, activo=True).first()
        if dia_no_habil:
            return dia_no_habil.descripcion
        
        return "Día hábil"
