"""
Tarjeta visual para destacar métricas clave (KPIs) en las vistas de resultados.
Universidad José Antonio Páez - Métodos Cuantitativos
"""

import customtkinter as ctk
from ..theme import Theme


class MetricCard(ctk.CTkFrame):
    """
    Widget tipo tarjeta para mostrar una métrica calculada con título,
    valor en texto grande y subtítulo/unidad explicativa.
    """

    def __init__(
        self,
        master,
        titulo: str,
        valor_inicial: str = "-",
        subtitulo: str = "",
        color_borde: str = Theme.BORDER_COLOR,
        color_acento: str = Theme.PRIMARY,
        **kwargs
    ):
        super().__init__(
            master,
            fg_color=Theme.BG_INPUT,
            corner_radius=8,
            border_width=1,
            border_color=color_borde,
            **kwargs
        )
        self.color_acento = color_acento

        # Título
        self.lbl_titulo = ctk.CTkLabel(
            self,
            text=titulo,
            font=Theme.font_small(),
            text_color=Theme.TEXT_MUTED,
            anchor="w"
        )
        self.lbl_titulo.pack(fill="x", padx=12, pady=(10, 2))

        # Valor
        self.lbl_valor = ctk.CTkLabel(
            self,
            text=valor_inicial,
            font=Theme.font_metric(),
            text_color=self.color_acento,
            anchor="w"
        )
        self.lbl_valor.pack(fill="x", padx=12, pady=2)

        # Subtítulo / Unidad
        self.lbl_subtitulo = ctk.CTkLabel(
            self,
            text=subtitulo,
            font=Theme.font_small(),
            text_color=Theme.TEXT_SUBTLE,
            anchor="w"
        )
        self.lbl_subtitulo.pack(fill="x", padx=12, pady=(2, 10))

    def actualizar(self, valor: str, subtitulo: str = None):
        """Actualiza el texto del valor y opcionalmente el subtítulo."""
        self.lbl_valor.configure(text=valor)
        if subtitulo is not None:
            self.lbl_subtitulo.configure(text=subtitulo)
