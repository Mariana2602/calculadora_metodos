import sys
import copy

import customtkinter as ctk

from aplicacion.metodos.costo_minimo import CostoMinimo
from aplicacion.metodos.esquina_noroeste import EsquinaNoroeste
from aplicacion.metodos.aproximacion_vogel import AproximacionVogel

ctk.set_appearance_mode("Light")

APP_BG = "#F4F7FB"
CARD_BG = "#FFFFFF"
CARD_ALT_BG = "#F8FAFC"
BORDER_COLOR = "#D8E1EA"
TEXT_PRIMARY = "#102033"
TEXT_SECONDARY = "#5A6675"
TEXT_MUTED = "#7A8796"
PRIMARY_COLOR = "#2563EB"
PRIMARY_HOVER = "#1D4ED8"
SUCCESS_COLOR = "#059669"
SUCCESS_HOVER = "#047857"
SOFT_BLUE_BG = "#EEF4FF"
SOFT_GREEN_BG = "#ECFDF5"
SOFT_ROSE_BG = "#FFF1F2"
SOFT_AMBER_BG = "#FFFBEB"
INPUT_BG = "#F8FAFC"
CONSOLE_BG = "#F8FAFC"
CONSOLE_TEXT = "#1F2937"
FONT_TITLE = ("DejaVu Sans", 26, "bold")
FONT_SUBTITLE = ("DejaVu Sans", 16, "bold")
FONT_BODY = ("DejaVu Sans", 14)
FONT_SMALL = ("DejaVu Sans", 12)
FONT_CONSOLE = ("DejaVu Sans Mono", 13)

class RedirectText:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, string):
        self.text_widget.configure(state="normal")
        self.text_widget.insert("end", string)
        self.text_widget.see("end")
        self.text_widget.configure(state="disabled")

    def flush(self):
        pass


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Calculadora de Problemas de Transporte")
        width = self.winfo_screenwidth()
        height = self.winfo_screenheight()
        vent_width = 1200
        vent_height = 920
        x = (width // 2) - (vent_width // 2)
        y = (height // 2) - (vent_height // 2)
        self.geometry(f"{vent_width}x{vent_height}+{x}+{y}")

        self.configure(fg_color=APP_BG)

        self.matrix_entries = []
        self.offer_entries = []
        self.demand_entries = []
        self.validate = (self.register(self.validate_digit), "%P")
        self.validateFloat = (self.register(self.validate_float), "%P")

        self.check_var = ctk.IntVar(value=False)

        self.setup_ui()

    def validate_digit(self, text: str):
        if text.isdigit() or text == "":
            return True
        return False
    
    def validate_float(self, text: str):
        if text == "":
            return True
        try:
            float(text)
            return True
        except ValueError:
            return False
    
    def setup_ui(self):
        self.main_container = ctk.CTkScrollableFrame(
            self,
            fg_color=APP_BG,
            corner_radius=0,
            border_width=0,
        )
        self.main_container.pack(fill="both", expand=True, padx=14, pady=14)

        self.header_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.header_frame.pack(fill="x", pady=(0, 18))
        self._build_header(self.header_frame)

        self.setup_row = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.setup_row.pack(fill="x", pady=(0, 18))
        self.setup_row.grid_columnconfigure(0, weight=1)
        self.setup_row.grid_columnconfigure(1, weight=1)

        self.config_card = self._make_card(self.setup_row)
        self.config_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        self.action_card = self._make_card(self.setup_row)
        self.action_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        self._build_configuration_card(self.config_card)
        self._build_actions_card(self.action_card)

        self.matrix_card = self._make_card(self.main_container)
        self.matrix_card.pack(fill="both", expand=True, pady=(0, 18))
        self._build_matrix_card(self.matrix_card)

        self.console_card = self._make_card(self.main_container)
        self.console_card.pack(fill="both", expand=True)
        self._build_console_card(self.console_card)

        sys.stdout = RedirectText(self.console_text)
        sys.stderr = RedirectText(self.console_text)

        print("Configuración lista. Define las dimensiones y genera la matriz.")

    def _make_card(self, parent):
        return ctk.CTkFrame(
            parent,
            fg_color=CARD_BG,
            corner_radius=20,
            border_width=1,
            border_color=BORDER_COLOR,
        )

    def _build_header(self, parent):
        title_row = ctk.CTkFrame(parent, fg_color="transparent")
        title_row.pack(fill="x")

        left_block = ctk.CTkFrame(title_row, fg_color="transparent")
        left_block.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            left_block,
            text="Calculadora de Problemas de Transporte",
            font=FONT_TITLE,
            text_color=TEXT_PRIMARY,
        ).pack(anchor="w")

        badge = ctk.CTkFrame(
            title_row,
            fg_color=SOFT_BLUE_BG,
            corner_radius=999,
            border_width=1,
            border_color="#C9DAFF",
        )

    def _build_configuration_card(self, parent):
        ctk.CTkLabel(
            parent,
            text="1. Configuración inicial",
            font=FONT_SUBTITLE,
            text_color=TEXT_PRIMARY,
        ).pack(anchor="w", padx=20, pady=(18, 2))

        ctk.CTkLabel(
            parent,
            text="Define cuántos orígenes y destinos vas a evaluar. El límite de 8x8 evita saturar la pantalla.",
            font=FONT_BODY,
            text_color=TEXT_SECONDARY,
            wraplength=500,
            justify="left",
        ).pack(anchor="w", padx=20, pady=(0, 16))

        form = ctk.CTkFrame(parent, fg_color=CARD_ALT_BG, corner_radius=16, border_width=1, border_color="#E5ECF3")
        form.pack(fill="x", padx=20, pady=(0, 20))
        form.grid_columnconfigure((1, 3), weight=1)

        ctk.CTkLabel(form, text="Orígenes", font=FONT_BODY, text_color=TEXT_PRIMARY).grid(row=0, column=0, sticky="w", padx=(16, 10), pady=(16, 10))
        self.rows_entry = ctk.CTkEntry(
            form,
            width=90,
            fg_color=INPUT_BG,
            text_color=TEXT_PRIMARY,
            border_color=BORDER_COLOR,
            border_width=1,
            font=FONT_BODY,
            validate='key',
            validatecommand=self.validate,
        )
        self.rows_entry.grid(row=0, column=1, sticky="ew", padx=(0, 16), pady=(16, 10))

        ctk.CTkLabel(form, text="Destinos", font=FONT_BODY, text_color=TEXT_PRIMARY).grid(row=1, column=0, sticky="w", padx=(16, 10), pady=(0, 16))
        self.cols_entry = ctk.CTkEntry(
            form,
            width=90,
            fg_color=INPUT_BG,
            text_color=TEXT_PRIMARY,
            border_color=BORDER_COLOR,
            border_width=1,
            font=FONT_BODY,
            validate='key',
            validatecommand=self.validate,
        )
        self.cols_entry.grid(row=1, column=1, sticky="ew", padx=(0, 16), pady=(0, 16))

        helper = ctk.CTkFrame(form, fg_color=SOFT_AMBER_BG, corner_radius=12, border_width=1, border_color="#F3D98C")
        helper.grid(row=0, column=2, rowspan=2, sticky="nsew", padx=(0, 16), pady=16)
        helper.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(helper, text="Consejo", font=FONT_BODY, text_color="#7C5C00").pack(anchor="w", padx=14, pady=(12, 4))
        ctk.CTkLabel(
            helper,
            text="Usa enteros positivos para filas y columnas. Luego genera la matriz y completa costos, oferta y demanda.",
            font=FONT_SMALL,
            text_color="#8A6B11",
            wraplength=220,
            justify="left",
        ).pack(anchor="w", padx=14, pady=(0, 12))

        self.btn_generate = ctk.CTkButton(
            form,
            text="Generar matriz",
            font=FONT_BODY,
            fg_color=PRIMARY_COLOR,
            hover_color=PRIMARY_HOVER,
            corner_radius=12,
            height=40,
            command=self.generate_matrix,
        )
        self.btn_generate.grid(row=2, column=0, columnspan=3, sticky="ew", padx=16, pady=(0, 16))

    def _build_actions_card(self, parent):
        ctk.CTkLabel(
            parent,
            text="2. Resolución",
            font=FONT_SUBTITLE,
            text_color=TEXT_PRIMARY,
        ).pack(anchor="w", padx=20, pady=(18, 2))

        ctk.CTkLabel(
            parent,
            text="Selecciona el método que prefieras y, si quieres, activa la conclusión automática con Groq.",
            font=FONT_BODY,
            text_color=TEXT_SECONDARY,
            wraplength=500,
            justify="left",
        ).pack(anchor="w", padx=20, pady=(0, 16))

        options = ctk.CTkFrame(parent, fg_color=CARD_ALT_BG, corner_radius=16, border_width=1, border_color="#E5ECF3")
        options.pack(fill="x", padx=20, pady=(0, 16))
        options.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(options, text="Método", font=FONT_BODY, text_color=TEXT_PRIMARY).grid(row=0, column=0, sticky="w", padx=(16, 10), pady=(16, 10))

        self.method_var = ctk.StringVar(value="Costo Mínimo")
        self.method_dropdown = ctk.CTkComboBox(
            options,
            variable=self.method_var,
            values=["Costo Mínimo", "Esquina Noroeste", "Aproximación de Vogel"],
            state="readonly",
            width=260,
            font=FONT_BODY,
            dropdown_font=FONT_BODY,
            fg_color=INPUT_BG,
            text_color=TEXT_PRIMARY,
            button_color=PRIMARY_COLOR,
            button_hover_color=PRIMARY_HOVER,
            border_color=BORDER_COLOR,
            border_width=1,
        )
        self.method_dropdown.grid(row=0, column=1, sticky="ew", padx=(0, 16), pady=(16, 10))

        self.checkbox_row = ctk.CTkFrame(options, fg_color="transparent")
        self.checkbox_row.grid(row=1, column=0, columnspan=2, sticky="ew", padx=16, pady=(0, 16))
        self.checkbox_row.grid_columnconfigure(1, weight=1)

        self.checkbox = ctk.CTkCheckBox(
            self.checkbox_row,
            text="Crear conclusión con Groq",
            variable=self.check_var,
            onvalue=True,
            offvalue=False,
            text_color=TEXT_PRIMARY,
            checkbox_width=20,
            checkbox_height=20,
            border_width=2,
            border_color=BORDER_COLOR,
            fg_color=PRIMARY_COLOR,
            hover_color=PRIMARY_HOVER,
        )
        self.checkbox.grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            self.checkbox_row,
            text="La salida se escribirá en la consola y, si activas esta opción, también se generará la conclusión.",
            font=FONT_SMALL,
            text_color=TEXT_MUTED,
            wraplength=320,
            justify="left",
        ).grid(row=0, column=1, sticky="w", padx=(12, 0))

        self.btn_calculate = ctk.CTkButton(
            parent,
            text="Calcular resultado",
            font=("DejaVu Sans", 14, "bold"),
            fg_color=SUCCESS_COLOR,
            hover_color=SUCCESS_HOVER,
            corner_radius=12,
            height=42,
            command=self.calculate,
        )
        self.btn_calculate.pack(fill="x", padx=20, pady=(0, 20))

    def _build_matrix_card(self, parent):
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(18, 10))

        ctk.CTkLabel(
            header,
            text="3. Matriz de costos",
            font=FONT_SUBTITLE,
            text_color=TEXT_PRIMARY,
        ).pack(anchor="w")

        ctk.CTkLabel(
            header,
            text="Completa la tabla de costos, oferta y demanda.",
            font=FONT_BODY,
            text_color=TEXT_SECONDARY,
            wraplength=1080,
            justify="left",
        ).pack(anchor="w", pady=(6, 0))

        self.matrix_frame = ctk.CTkScrollableFrame(
            parent,
            fg_color=CARD_ALT_BG,
            corner_radius=16,
            border_width=1,
            border_color="#E5ECF3",
        )
        self.matrix_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def _build_console_card(self, parent):
        ctk.CTkLabel(
            parent,
            text="4. Consola de salida",
            font=FONT_SUBTITLE,
            text_color=TEXT_PRIMARY,
        ).pack(anchor="w", padx=20, pady=(18, 2))

        ctk.CTkLabel(
            parent,
            text="Validaciones, desarrollo del método y cualquier error o resultado generado.",
            font=FONT_BODY,
            text_color=TEXT_SECONDARY,
            wraplength=1080,
            justify="left",
        ).pack(anchor="w", padx=20, pady=(0, 10))

        self.console_text = ctk.CTkTextbox(
            parent,
            state="disabled",
            font=FONT_CONSOLE,
            fg_color=CONSOLE_BG,
            text_color=CONSOLE_TEXT,
            corner_radius=16,
            border_width=1,
            border_color=BORDER_COLOR,
            height=260,
        )
        self.console_text.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def generate_matrix(self):
        try:
            rows = int(self.rows_entry.get())
            cols = int(self.cols_entry.get())
            if rows <= 0 or cols <= 0:
                raise ValueError("Por favor ingresa números enteros mayores a 0 para filas y columnas.")
            if rows >= 9 or cols >= 9:
                raise ValueError("No genere matrices de un tamaño mayor a 8x8")
        except ValueError as ve:
            print(ve)
            return

        for widget in self.matrix_frame.winfo_children():
            widget.destroy()

        self.matrix_entries = []
        self.offer_entries = []
        self.demand_entries = []

        for j in range(cols):
            ctk.CTkLabel(
                self.matrix_frame,
                text=f"D{j+1}",
                font=("DejaVu Sans", 13, "bold"),
                text_color=TEXT_MUTED,
            ).grid(row=0, column=j+1, padx=8, pady=(14, 8))
        
        ctk.CTkLabel(
            self.matrix_frame,
            text="OFERTA",
            font=("DejaVu Sans", 13, "bold"),
            text_color="#0F766E",
        ).grid(row=0, column=cols+1, padx=15, pady=(14, 8))
        for i in range(rows):
            ctk.CTkLabel(
                self.matrix_frame,
                text=f"O{i+1}",
                font=("DejaVu Sans", 13, "bold"),
                text_color=TEXT_MUTED,
            ).grid(row=i+1, column=0, padx=8, pady=8)
            
            row_entries = []
            for j in range(cols):
                entry = ctk.CTkEntry(
                    self.matrix_frame,
                    width=70,
                    height=36,
                    justify="center",
                    font=FONT_BODY,
                    fg_color=INPUT_BG,
                    text_color=TEXT_PRIMARY,
                    border_color=BORDER_COLOR,
                    border_width=1,
                    validate='key',
                    validatecommand=self.validateFloat,
                )
                entry.grid(row=i+1, column=j+1, padx=4, pady=4)
                row_entries.append(entry)
            self.matrix_entries.append(row_entries)

            offer_entry = ctk.CTkEntry(
                self.matrix_frame,
                width=70,
                height=36,
                justify="center",
                font=FONT_BODY,
                fg_color=SOFT_BLUE_BG,
                text_color=TEXT_PRIMARY,
                border_color="#A7C0FF",
                border_width=1,
                validate='key',
                validatecommand=self.validateFloat,
            )
            offer_entry.grid(row=i+1, column=cols+1, padx=15, pady=4)
            self.offer_entries.append(offer_entry)

        ctk.CTkLabel(
            self.matrix_frame,
            text="DEMANDA",
            font=("DejaVu Sans", 13, "bold"),
            text_color="#B91C1C",
        ).grid(row=rows+1, column=0, padx=8, pady=(15, 18))
        for j in range(cols):
            demand_entry = ctk.CTkEntry(
                self.matrix_frame,
                width=70,
                height=36,
                justify="center",
                font=FONT_BODY,
                fg_color=SOFT_ROSE_BG,
                text_color=TEXT_PRIMARY,
                border_color="#F4A5B6",
                border_width=1,
                validate='key',
                validatecommand=self.validateFloat,
            )
            demand_entry.grid(row=rows+1, column=j+1, padx=4, pady=15)
            self.demand_entries.append(demand_entry)

        print(f"Matriz generada exitosamente: {rows} orígenes x {cols} destinos.")

    def calculate(self):
        self.console_text.configure(state="normal")
        self.console_text.delete("1.0", "end")
        self.console_text.configure(state="disabled")

        try:
            matriz = []
            for row_entries in self.matrix_entries:
                row_values = [float(entry.get()) for entry in row_entries]
                matriz.append(row_values)

            offers = [float(entry.get()) for entry in self.offer_entries]
            demands = [float(entry.get()) for entry in self.demand_entries]
        except ValueError:
            print("[Error]: Por favor llena todos los campos generados con números válidos.")
            return

        method = self.method_var.get()
        print(f"--- EJECUTANDO MÉTODO: {method.upper()} ---\n")

        try:
            match method:
                case "Costo Mínimo":
                    t = CostoMinimo(copy.deepcopy(matriz), offers[:], demands[:])
                    t.resolve_costo_minimo()
                    conclusion = t.groq_prompt() if self.check_var.get() else ""
                    t.save_result_to_txt("Costo_Minimo", conclusion)

                case "Esquina Noroeste":
                    t = EsquinaNoroeste(copy.deepcopy(matriz), offers[:], demands[:])
                    t.resolve_esquina_noroeste()
                    conclusion = t.groq_prompt() if self.check_var.get() else ""
                    t.save_result_to_txt("Esquina_Noroeste", conclusion)

                case "Aproximación de Vogel":
                    t = AproximacionVogel(copy.deepcopy(matriz), offers[:], demands[:])
                    t.resolve_aproximacion_vogel()
                    conclusion = t.groq_prompt() if self.check_var.get() else ""
                    t.save_result_to_txt("Aproximacion_de_Vogel", conclusion)

        except ValueError as ve:
            print(f"[Error de validación]: {ve}")
        except Exception as e:
            print(f"[Error inesperado]: {e}")
