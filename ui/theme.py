"""
DevDeck Theme — Qt stylesheet generation for light and dark mode.

Why this file was rewritten
---------------------------
The previous stylesheet was hand-written and, in many places, invalid Qt QSS:
declarations such as ``color: #a159ff.`` (missing semicolon) and unterminated
rule blocks. Qt's QSS parser drops the remainder of a rule as soon as it hits a
malformed declaration, so large parts of the UI rendered unstyled, and dark
mode (which relied on ``[theme="dark"]`` property selectors) failed almost
entirely.

The sheet is now generated from two token dicts, so light and dark can never
drift apart and every emitted declaration is valid.
"""

# ── Design tokens ────────────────────────────────────────────────────────────
LIGHT = {
    # Cool, quiet neutrals with one consistent blue accent.
    "bg_app": "#F4F6F8", "bg_panel": "#FFFFFF", "bg_sidebar": "#EEF2F6",
    "bg_inset": "#F1F4F7", "bg_hover": "#E8EDF3", "bg_active": "#E4EDF7",
    "bg_running": "#EAF5EE", "border": "#DFE5EC", "border_strong": "#C8D2DE",
    "primary": "#356B9A", "primary_hover": "#28577F", "primary_soft": "#E7F0F8",
    "on_primary": "#FFFFFF", "text": "#1D2935", "text_dim": "#536273",
    "text_faint": "#7D8996", "green": "#278456", "green_soft": "#E6F3EB",
    "red": "#B94F52", "red_soft": "#F9E9E9", "amber": "#966B27",
    "amber_soft": "#F7F0E2", "star": "#A87928", "log_bg": "#111820",
    "log_border": "#2C3945", "log_text": "#E7EDF3", "log_muted": "#A6B2BE",
}

DARK = {
    # The same hue relationships as light mode, tuned for dark surfaces.
    "bg_app": "#151A20", "bg_panel": "#1D252E", "bg_sidebar": "#19212A",
    "bg_inset": "#232D37", "bg_hover": "#2A3642", "bg_active": "#263B4D",
    "bg_running": "#20382C", "border": "#2C3945", "border_strong": "#405160",
    "primary": "#83B5DE", "primary_hover": "#A0C9E9", "primary_soft": "#263B4D",
    "on_primary": "#101820", "text": "#EAF0F5", "text_dim": "#BCC8D3",
    "text_faint": "#8795A3", "green": "#78C99A", "green_soft": "#203B2D",
    "red": "#E18D8F", "red_soft": "#432B2D", "amber": "#E0BC78",
    "amber_soft": "#403723", "star": "#E4C47C", "log_bg": "#0F151B",
    "log_border": "#2A3540", "log_text": "#E7EDF3", "log_muted": "#A6B2BE",
}


def _rule(selector, **decls) -> str:
    body = "\n".join(f"    {k.replace('_', '-')}: {v};" for k, v in decls.items())
    return f"{selector} {{\n{body}\n}}"


def _build(t: dict) -> str:
    out = []
    a = out.append

    # ── Base ────────────────────────────────────────────────────────────────
    a(_rule("QWidget",
            background_color=t["bg_app"],
            color=t["text"],
            font_family='"Inter", "Segoe UI", Roboto, "Helvetica Neue", Ubuntu, sans-serif',
            font_size="13px"))
    a("QLabel { background: transparent; }")
    a(_rule("QToolTip",
            background_color=t["bg_panel"],
            color=t["text"],
            border=f"1px solid {t['border_strong']}",
            border_radius="6px",
            padding="5px 8px"))
    a(_rule("QWidget:disabled", color=t["text_faint"]))

    # ── Shell & containers ─────────────────────────────────────────────────
    a(_rule("QMainWindow", background_color=t["bg_app"]))
    a(_rule("QWidget#CentralRoot", background_color=t["bg_app"]))
    a(_rule("QFrame#HeroPanel",
            background_color=t["bg_sidebar"],
            border="none",
            border_radius="14px"))
    a(_rule("QWidget#RightContainer", background="transparent"))
    a(_rule("QWidget#NavContainer", background="transparent"))
    a(_rule("QWidget#EmptyBtns", background="transparent"))
    a(_rule("QScrollArea#NavScroll", background="transparent", border="none"))
    a(_rule("QScrollArea#CardsScroll", background="transparent", border="none"))
    a(_rule("QWidget#CardsContainer", background="transparent"))

    a(_rule("QFrame#WorkspaceHeader", background="transparent", border="none"))
    a(_rule("QLabel#PageTitle", font_size="25px", font_weight="750", color=t["text"]))
    a(_rule("QLabel#PageSubtitle", font_size="12px", color=t["text_faint"]))
    a(_rule("QPushButton#SecondaryBtn",
            background_color=t["bg_panel"], color=t["text_dim"],
            border=f"1px solid {t['border']}", border_radius="8px",
            padding="8px 13px", font_size="12px", font_weight="600"))
    a(_rule("QPushButton#SecondaryBtn:hover",
            background_color=t["bg_hover"], border_color=t["border_strong"], color=t["text"]))
    a(_rule("QPushButton#UtilityBtn",
            background_color="transparent", color=t["text_dim"],
            border=f"1px solid {t['border']}", border_radius="8px",
            padding="6px 8px", font_size="11px", font_weight="600"))
    a(_rule("QPushButton#UtilityBtn:hover",
            background_color=t["bg_hover"], color=t["text"], border_color=t["border_strong"]))

    # ── Brand ──────────────────────────────────────────────────────────────
    a(_rule("QLabel#HeroTitle", font_size="19px", font_weight="800", color=t["primary"]))
    a(_rule("QLabel#HeroSubtitle", font_size="11px", font_weight="500", color=t["text_faint"]))

    # ── Stats card ─────────────────────────────────────────────────────────
    a(_rule("QFrame#StatsCard",
            background_color=t["bg_inset"],
            border="none",
            border_radius="10px"))
    a(_rule("QFrame#StatBadge", background="transparent", border="none"))
    a(_rule("QLabel#StatValue", font_size="18px", font_weight="800", color=t["text"]))
    a(_rule("QLabel#StatLabel", font_size="9px", font_weight="700", color=t["text_faint"]))
    a('QLabel#StatValue[statKind="TOTAL"] { color: %s; }' % t["text"])
    a('QLabel#StatValue[statKind="ACTIVE"] { color: %s; }' % t["green"])
    a('QLabel#StatValue[statKind="PORTS"] { color: %s; }' % t["primary"])
    a(_rule("QFrame#VDivider",
            background_color=t["border"],
            max_width="1px", min_width="1px"))

    # ── Search ─────────────────────────────────────────────────────────────
    a(_rule("QFrame#FilterBar", background="transparent", border="none"))
    a(_rule("QLineEdit#SearchBar",
            background_color=t["bg_panel"],
            border=f"1px solid {t['border_strong']}",
            border_radius="9px",
            padding="8px 12px",
            color=t["text"],
            font_size="12px",
            font_weight="500",
            selection_background_color=t["primary"],
            selection_color=t["on_primary"]))
    a("QLineEdit#SearchBar:focus { border: 1px solid %s; }" % t["primary"])
    a("QLineEdit#SearchBar::placeholder { color: %s; }" % t["text_faint"])
    a(_rule("QLabel#SearchIcon",
            font_size="12px", color=t["text_faint"], background="transparent"))
    a(_rule("QLabel#ShortcutPill",
            background_color=t["bg_inset"],
            border=f"1px solid {t['border']}",
            border_radius="5px",
            padding="1px 6px",
            font_size="9px",
            font_weight="700",
            color=t["text_dim"]))

    # ── Sidebar navigation ─────────────────────────────────────────────────
    a(_rule("QLabel#SectionHeader",
            background="transparent",
            color=t["text_faint"],
            font_size="10px",
            font_weight="800",
            padding="4px 8px"))
    a(_rule("QPushButton#NavItem",
            background_color="transparent",
            border="1px solid transparent",
            border_radius="8px",
            padding="8px 12px",
            color=t["text_dim"],
            font_weight="600",
            font_size="12px",
            text_align="left"))
    a(_rule("QPushButton#NavItem:hover",
            background_color=t["bg_hover"],
            color=t["text"],
            border_color=t["border"]))
    a(_rule('QPushButton#NavItem[checked="true"]',
            background_color=t["primary_soft"],
            border=f"1px solid {t['primary_soft']}",
            border_left=f"3px solid {t['primary']}",
            color=t["primary"],
            font_weight="700"))
    a(_rule("QLabel#NavIcon", font_size="13px", color=t["text_faint"]))
    a(_rule('QLabel#NavIcon[compact="true"]',
            background_color=t["bg_inset"],
            border=f"1px solid {t['border_strong']}",
            border_radius="7px",
            color=t["text_dim"],
            font_size="10px",
            font_weight="800",
            padding="0px"))
    a(_rule("QLabel#NavTitle", font_size="12px", color=t["text_dim"]))
    a(_rule('QPushButton#NavItem[checked="true"] QLabel#NavTitle',
            color=t["primary"], font_weight="700"))
    a(_rule('QPushButton#NavItem[checked="true"] QLabel#NavIcon', color=t["primary"]))
    a(_rule("QLabel#NavBadge",
            background_color=t["bg_inset"],
            border=f"1px solid {t['border']}",
            border_radius="7px",
            padding="0 6px",
            min_width="18px",
            font_size="10px",
            font_weight="700",
            color=t["text_faint"]))
    a(_rule('QPushButton#NavItem[checked="true"] QLabel#NavBadge',
            background_color=t["bg_panel"], border_color=t["primary"], color=t["primary"]))

    # ── Buttons ────────────────────────────────────────────────────────────
    a(_rule("QPushButton",
            background_color=t["bg_panel"],
            border=f"1px solid {t['border_strong']}",
            border_radius="9px",
            padding="7px 13px",
            color=t["text"],
            font_weight="600",
            font_size="12px"))
    a(_rule("QPushButton:hover",
            background_color=t["bg_hover"], border_color=t["primary"], color=t["text"]))
    a(_rule("QPushButton:pressed", background_color=t["bg_active"]))
    a(_rule("QPushButton:disabled",
            background_color=t["bg_inset"], border_color=t["border"], color=t["text_faint"]))

    a(_rule("QPushButton#PrimaryBtn",
            background_color=t["primary"],
            border=f"1px solid {t['primary']}",
            color=t["on_primary"],
            font_weight="700"))
    a(_rule("QPushButton#PrimaryBtn:hover",
            background_color=t["primary_hover"], border_color=t["primary_hover"]))
    a(_rule("QPushButton#PrimaryBtn:disabled",
            background_color=t["bg_inset"], border_color=t["border"], color=t["text_faint"]))

    a(_rule("QPushButton#StartBtn",
            background_color=t["green_soft"],
            border=f"1px solid {t['green']}",
            color=t["green"],
            font_weight="700"))
    a(_rule("QPushButton#StartBtn:hover", background_color=t["green"], color=t["on_primary"]))
    a(_rule("QPushButton#StartBtn:disabled",
            background_color=t["bg_inset"],
            border_color=t["border"],
            color=t["text_faint"]))

    a(_rule("QPushButton#StopBtn",
            background_color=t["red_soft"],
            border=f"1px solid {t['red']}",
            color=t["red"],
            font_weight="700"))
    a(_rule("QPushButton#StopBtn:hover",
            background_color=t["red"], color=t["on_primary"]))
    # The objectName rules are more specific than the generic disabled rule,
    # so the muted state has to be restated per-button.
    a(_rule("QPushButton#StopBtn:disabled",
            background_color=t["bg_inset"],
            border_color=t["border"],
            color=t["text_faint"]))

    a(_rule("QPushButton#BrowserBtn",
            background_color=t["bg_inset"],
            border=f"1px solid {t['border_strong']}",
            color=t["text_dim"],
            font_weight="600"))
    a(_rule("QPushButton#BrowserBtn:hover",
            background_color=t["bg_hover"], border_color=t["primary"], color=t["primary"]))
    a(_rule("QPushButton#BrowserBtn:disabled",
            background_color=t["bg_inset"], border_color=t["border"], color=t["text_faint"]))

    a(_rule("QPushButton#IconBtn",
            background_color=t["bg_panel"],
            border=f"1px solid {t['border']}",
            border_radius="8px",
            padding="6px 10px",
            color=t["text_dim"],
            font_size="11px",
            font_weight="600"))
    a(_rule("QPushButton#IconBtn:hover",
            background_color=t["bg_hover"],
            border_color=t["border_strong"],
            color=t["text"]))
    a(_rule("QPushButton#IconBtn:disabled",
            background="transparent", border="none", color=t["text_faint"]))
    a(_rule('QPushButton#IconBtn[fav="on"]', color=t["star"]))

    # The port is a number, so it gets plain monospace text rather than a
    # button that implies an action it is not.
    a(_rule("QPushButton#PortTag",
            background_color="transparent",
            border="none",
            border_radius="5px",
            padding="2px 6px",
            color=t["text_faint"],
            font_size="10px",
            font_weight="700",
            font_family='"JetBrains Mono", "DejaVu Sans Mono", monospace'))
    a(_rule("QPushButton#PortTag:hover",
            background_color=t["bg_hover"], color=t["primary"]))

    a(_rule("QPushButton#ThemeToggle",
            background_color="transparent",
            border=f"1px solid {t['border']}",
            border_radius="9px",
            padding="7px 10px",
            color=t["text_dim"],
            font_size="12px",
            font_weight="600"))
    a(_rule("QPushButton#ThemeToggle:hover",
            background_color=t["bg_hover"], border_color=t["primary"], color=t["primary"]))

    # ── Content section headers ────────────────────────────────────────────
    a(_rule("QLabel#CardSectionTitle",
            background="transparent", color=t["text"], font_size="13px", font_weight="700"))
    a(_rule("QLabel#CardSectionCount",
            background_color=t["bg_inset"],
            border=f"1px solid {t['border']}",
            border_radius="6px",
            padding="1px 7px",
            color=t["text_dim"],
            font_size="10px",
            font_weight="700"))

    # ── Empty state ────────────────────────────────────────────────────────
    a(_rule("QFrame#EmptyStateFrame",
            background_color=t["bg_panel"],
            border="none",
            border_radius="14px"))
    a(_rule("QLabel#EmptyIcon", font_size="34px", background="transparent"))
    a(_rule("QLabel#EmptyTitle", font_size="16px", font_weight="700", color=t["text"]))
    a(_rule("QLabel#EmptySubtitle", font_size="12px", font_weight="500", color=t["text_faint"]))

    # ── Cards ──────────────────────────────────────────────────────────────
    for card in ("QFrame#ProjectCard", "QFrame#StackCard"):
        a(_rule(card,
                background_color=t["bg_panel"],
                border=f"1px solid {t['border']}",
                border_radius="13px"))
        a(_rule(f"{card}:hover", border_color=t["border_strong"]))
        a(_rule(f'{card}[running="true"]',
                border=f"1px solid {t['green']}", background_color=t["bg_running"]))

    a(_rule("QLabel#CardTitle", font_size="14px", font_weight="700", color=t["text"]))
    a(_rule("QLabel#CardPath", font_size="11px", font_weight="500", color=t["text_faint"]))
    a(_rule("QLabel#CardCmd",
            font_size="11px",
            color=t["text_dim"],
            background_color=t["bg_inset"],
            border="none",
            border_radius="6px",
            padding="3px 7px",
            font_family='"JetBrains Mono", "DejaVu Sans Mono", monospace'))
    a(_rule("QLabel#StackBadge",
            background_color=t["primary_soft"],
            border="none",
            border_radius="6px",
            padding="2px 7px",
            font_size="10px",
            font_weight="700",
            color=t["primary"]))
    a(_rule("QLabel#MetricsLabel",
            font_size="10px",
            color=t["text_faint"],
            font_family='"JetBrains Mono", "DejaVu Sans Mono", monospace'))
    a(_rule("QLabel#ElidedLabel", font_size="14px", font_weight="700", color=t["text"]))
    a(_rule("QLabel#ElidedTitleLabel", font_size="14px", font_weight="700", color=t["text"]))

    a(_rule("QFrame#IconSquircle",
            background_color=t["primary_soft"],
            border="none",
            border_radius="9px",
            min_width="34px", max_width="34px",
            min_height="34px", max_height="34px"))
    a(_rule("QLabel#SquircleIcon", font_size="16px", background="transparent"))
    a(_rule("QFrame#StackCardIconBox",
            background_color=t["primary_soft"],
            border="none",
            border_radius="8px",
            min_width="32px", max_width="32px",
            min_height="32px", max_height="32px"))
    a(_rule("QLabel#StackCardIcon", font_size="16px", color=t["primary"]))

    a(_rule("QLabel#StatusBadge",
            border_radius="7px", padding="3px 8px",
            font_size="10px", font_weight="700", border="1px solid transparent"))
    a(_rule('QLabel#StatusBadge[status="running"]',
            background_color=t["green_soft"], color=t["green"], border_color=t["green"]))
    a(_rule('QLabel#StatusBadge[status="starting"]',
            background_color=t["amber_soft"], color=t["amber"], border_color=t["amber"]))
    a(_rule('QLabel#StatusBadge[status="stopped"]',
            background_color=t["bg_inset"], color=t["text_faint"], border_color=t["border"]))
    a(_rule('QLabel#StatusBadge[status="error"]',
            background_color=t["red_soft"], color=t["red"], border_color=t["red"]))

    # ── Stack card internals ───────────────────────────────────────────────
    # Density note: service rows carry no border. They are nested inside a
    # card that already has one, so a second outline reads as noise. The
    # subtle background tint plus row spacing does the separating instead.
    a(_rule("QLabel#StackCardTitle", font_size="14px", font_weight="700", color=t["text"]))
    a(_rule("QLabel#StackCardSub", font_size="10px", font_weight="600", color=t["text_faint"]))
    a(_rule("QFrame#ServiceMiniRow",
            background_color=t["bg_inset"],
            border="none",
            border_radius="8px"))
    a(_rule("QFrame#ServiceMiniRow:hover", background_color=t["bg_hover"]))
    a(_rule("QLabel#ServiceIcon", font_size="12px", color=t["text_faint"]))
    a(_rule("QLabel#ServiceName", font_size="12px", font_weight="600", color=t["text"]))
    a(_rule("QLabel#ServiceCmd",
            font_size="10px",
            color=t["text_faint"],
            font_family='"JetBrains Mono", "DejaVu Sans Mono", monospace'))

    # ── Dialogs ────────────────────────────────────────────────────────────
    a(_rule("QDialog", background_color=t["bg_app"]))
    for dlg in ("QDialog#StackDialog", "QDialog#ProjectDialog"):
        a(_rule(dlg, background_color=t["bg_app"], border=f"1px solid {t['border_strong']}"))
    a(_rule("QLabel#DialogTitle", font_size="18px", font_weight="800", color=t["text"]))
    a(_rule("QLabel#DialogSubtitle", font_size="11px", font_weight="500", color=t["text_faint"]))
    a(_rule("QLabel#DialogFieldLabel", font_size="11px", font_weight="700", color=t["text_dim"]))
    a(_rule("QLabel#FieldHint", font_size="10px", font_weight="500", color=t["text_faint"]))
    a(_rule("QScrollArea#StackDialogScroll", background="transparent", border="none"))
    a(_rule("QWidget#StackDialogContainer", background="transparent"))
    a(_rule("QFrame#ServiceRow",
            background_color=t["bg_inset"],
            border="none",
            border_radius="8px"))
    a(_rule("QFrame#ServiceRow:hover", background_color=t["bg_hover"]))
    a(_rule("QLabel#ServiceRowBadge",
            background_color=t["bg_panel"],
            border=f"1px solid {t['border_strong']}",
            border_radius="6px",
            padding="2px 7px",
            font_size="10px",
            font_weight="700",
            color=t["text_dim"]))

    # ── Inputs ─────────────────────────────────────────────────────────────
    a(_rule("QLineEdit",
            background_color=t["bg_panel"],
            border=f"1px solid {t['border_strong']}",
            border_radius="8px",
            padding="8px 11px",
            color=t["text"],
            font_size="12px",
            font_weight="500",
            selection_background_color=t["primary"],
            selection_color=t["on_primary"]))
    a("QLineEdit:focus { border: 1px solid %s; }" % t["primary"])
    a("QLineEdit::placeholder { color: %s; }" % t["text_faint"])
    a(_rule("QLineEdit:disabled",
            background_color=t["bg_inset"], color=t["text_faint"], border_color=t["border"]))

    a(_rule("QComboBox",
            background_color=t["bg_panel"],
            border=f"1px solid {t['border_strong']}",
            border_radius="8px",
            padding="7px 11px",
            color=t["text"], font_size="12px", font_weight="500"))
    a("QComboBox:focus { border: 1px solid %s; }" % t["primary"])
    a(_rule("QComboBox:disabled",
            background_color=t["bg_inset"], color=t["text_faint"], border_color=t["border"]))
    a(_rule("QComboBox::drop-down",
            border="none", width="22px",
            subcontrol_origin="padding", subcontrol_position="center right"))
    a(_rule("QComboBox::down-arrow",
            image="none",
            border_left="4px solid transparent",
            border_right="4px solid transparent",
            border_top=f"5px solid {t['text_dim']}",
            margin_right="8px"))
    a(_rule("QComboBox QAbstractItemView",
            background_color=t["bg_panel"],
            color=t["text"],
            border=f"1px solid {t['border_strong']}",
            border_radius="8px",
            selection_background_color=t["bg_active"],
            selection_color=t["primary"],
            outline="none"))

    a(_rule("QSpinBox",
            background_color=t["bg_panel"],
            border=f"1px solid {t['border_strong']}",
            border_radius="8px",
            padding="7px 11px",
            color=t["text"], font_size="12px"))
    a(_rule("QSpinBox:focus", border=f"1px solid {t['primary']}"))

    a(_rule("QCheckBox", color=t["text_dim"], font_size="12px", spacing="8px"))
    a(_rule("QCheckBox::indicator",
            width="15px", height="15px",
            border=f"1px solid {t['border_strong']}",
            border_radius="4px",
            background_color=t["bg_panel"]))
    a(_rule("QCheckBox::indicator:checked",
            background_color=t["primary"], border_color=t["primary"]))

    # ── Log drawer ─────────────────────────────────────────────────────────
    a(_rule("QFrame#LogDrawer",
            background_color=t["log_bg"],
            border=f"1px solid {t['log_border']}",
            border_radius="12px"))
    a(_rule("QTextEdit#LogViewer",
            background_color=t["log_bg"],
            border="none",
            color=t["log_text"],
            font_family='"JetBrains Mono", "DejaVu Sans Mono", monospace',
            font_size="12px",
            padding="8px 10px",
            selection_background_color=t["primary"],
            selection_color=t["on_primary"]))
    a(_rule("QLabel#LogTitle", font_size="12px", font_weight="700", color=t["log_text"]))
    a(_rule("QLabel#LogMeta", font_size="10px", font_weight="600", color=t["log_muted"]))
    a(_rule("QLineEdit#LogSearch",
            background_color=t["log_bg"],
            border=f"1px solid {t['log_border']}",
            border_radius="7px",
            padding="5px 9px",
            color=t["log_text"], font_size="11px",
            selection_background_color=t["primary"]))
    a("QLineEdit#LogSearch:focus { border: 1px solid %s; }" % t["primary"])
    a(_rule("QCheckBox#LogAutoScroll", color=t["log_muted"], font_size="11px", spacing="6px"))
    a(_rule("QCheckBox#LogAutoScroll::indicator",
            width="14px", height="14px",
            border=f"1px solid {t['log_border']}",
            border_radius="4px",
            background_color=t["log_bg"]))
    a(_rule("QCheckBox#LogAutoScroll::indicator:checked",
            background_color=t["primary"], border_color=t["primary"]))
    a(_rule("QPushButton#LogBtn",
            background_color="transparent",
            border=f"1px solid {t['log_border']}",
            border_radius="7px",
            padding="4px 10px",
            color=t["log_muted"], font_size="11px", font_weight="600"))
    a(_rule("QPushButton#LogBtn:hover",
            background_color=t["bg_hover"], border_color=t["primary"], color=t["primary"]))
    a(_rule("QPushButton#LogBtn:pressed", background_color=t["bg_active"]))
    a(_rule("QPushButton#LogBtn:disabled", color=t["log_muted"]))

    # ── Splitter ───────────────────────────────────────────────────────────
    a(_rule("QSplitter::handle", background_color="transparent"))
    a(_rule("QSplitter::handle:vertical", background_color="transparent", height="6px"))
    a(_rule("QSplitter::handle:hover", background_color=t["border_strong"]))

    # ── Scrollbars ─────────────────────────────────────────────────────────
    a(_rule("QScrollBar:vertical",
            background="transparent", width="10px", border="none", margin="2px"))
    a(_rule("QScrollBar::handle:vertical",
            background=t["border_strong"], min_height="30px", border_radius="4px"))
    a("QScrollBar::handle:vertical:hover { background: %s; }" % t["text_faint"])
    a(_rule("QScrollBar:horizontal",
            background="transparent", height="10px", border="none", margin="2px"))
    a(_rule("QScrollBar::handle:horizontal",
            background=t["border_strong"], min_width="30px", border_radius="4px"))
    a("QScrollBar::handle:horizontal:hover { background: %s; }" % t["text_faint"])
    a(_rule("QScrollBar::add-line, QScrollBar::sub-line", height="0px", width="0px"))
    a(_rule("QScrollBar::add-page, QScrollBar::sub-page", background="transparent"))

    # ── Menus & message boxes ──────────────────────────────────────────────
    a(_rule("QMenu",
            background_color=t["bg_panel"],
            border=f"1px solid {t['border_strong']}",
            border_radius="9px",
            padding="5px"))
    a(_rule("QMenu::item",
            padding="6px 24px 6px 12px", border_radius="6px",
            color=t["text"], font_size="12px"))
    a(_rule("QMenu::item:selected", background_color=t["bg_active"], color=t["primary"]))
    a(_rule("QMenu::separator", height="1px", background=t["border"], margin="4px 8px"))
    a(_rule("QMessageBox", background_color=t["bg_app"]))
    a(_rule("QMessageBox QLabel", color=t["text"], font_size="12px"))

    return "\n".join(out)


LIGHT_QSS = _build(LIGHT)
DARK_QSS = _build(DARK)

# Backwards-compatible export used elsewhere.
FIGMA_THEME_QSS = LIGHT_QSS

THEMES = {"light": LIGHT_QSS, "dark": DARK_QSS}


def stylesheet_for(theme: str) -> str:
    """Return the stylesheet for ``'light'`` or ``'dark'``."""
    return THEMES.get(theme, LIGHT_QSS)


def apply_theme(app, theme: str) -> None:
    """Apply a theme to a QApplication instance."""
    if app is not None:
        app.setStyleSheet(stylesheet_for(theme))


def get_color(key: str, theme: str = "light") -> str:
    """Look up a palette token by name (kept for API compatibility)."""
    tokens = DARK if theme == "dark" else LIGHT
    return tokens.get(key, tokens["primary"])
