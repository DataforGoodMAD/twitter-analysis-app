import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from datetime import datetime

from twitter_analysis_app.app import TwitterAnalysisFeatures
from twitter_analysis_app.local_config import config_check, verify_config, save_config


class TwitterAnalysisApp(toga.App):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = TwitterAnalysisFeatures()

        icon = "resources/logo_dfg.png"

        self.command_update_config = toga.Command(
            action=self.action_update_config,
            label="Actualizar Configuración",
            tooltip="Actualizar Configuración",
            icon=icon,
        )

        self.command_update_data = toga.Command(
            action=self.action_update_data,
            label="Actualizar Datos",
            tooltip="Actualiza Tweets, Seguidores y Amigos del usuario principal",
            icon=icon,
        )

        self.command_find_similar_users = toga.Command(
            action=self.action_find_similar_users,
            label="Encontrar Usuarios Afines",
            tooltip="""
                Actualiza Tweets, Seguidores y Amigos del usuario principal
            """,
            icon=icon,
        )

        self.command_show_sim_users_window = toga.Command(
            action=self.action_show_users_window,
            label="Usuarios Afines",
            tooltip="Actualiza Tweets, Seguidores y Amigos del usuario principal",
            icon=icon,
        )

        self.command_show_hidden_users = toga.Command(
            action=self.action_show_hidden_users,
            label="Usuarios Ocultos",
            tooltip="Actualiza Tweets, Seguidores y Amigos del usuario principal",
            icon=icon,
        )

    @property
    def db(self):
        return self.app.db

    @property
    def processor(self):
        return self.app.processor

    @property
    def miner(self):
        return self.app.miner

    ##########
    # Utils  #
    ##########

    def open_user_in_webview(self, table, row):
        base_url = "https://twitter.com/"
        self.webview.url = base_url + row.usuario

    def open_user_dialog(self, table, row):
        user_info_box = toga.Box(
            style=Pack(
                direction=ROW,
                padding=5,
            ),
        )
        user_label = toga.Label(
            row.usuario,
            style=Pack(
                padding=(5, 5),
            ),
        )

        user_info_box.add(
            user_label,
        )

        follow_button = toga.Button(
            label="Seguir",
            on_press=self.follow_user,
        )
        hide_button = toga.Button(
            label="Ocultar",
            on_press=self.hide_user,
        )
        user_buttons_box = toga.Box(
            style=Pack(
                direction=ROW,
                padding=5,
            ),
        )
        user_buttons_box.add(
            follow_button,
            hide_button,
        )

        user_dialog_box = toga.Box(style=Pack(direction=COLUMN))
        user_dialog_box.add(user_info_box, user_buttons_box)

        self.user_window = toga.Window(title="Configuración Inicial")
        self.user_window.content = user_dialog_box

        self.user_window.show()

        ###########
        # Actions #
        ###########

    def action_show_users_window(self, widget):
        self.users_main_box = self._build_users_layout()
        self.users_window = self._build_users_window()
        self.users_window.content = self.users_main_box
        self.users_window.show()

    def action_show_hidden_users(self, widget):
        if not self.users_window:
            return False
        hidden_users_data = self.db.get_similar_users(hidden=True)
        self.hidden_users_table = self._build_users_table(hidden_users_data)
        self.users_main_box.content[0] = self.hidden_users_table

    def action_update_data(self, widget):
        self.app.update_timeline()
        self.app.update_tokens_count()
        self.app.update_followers(self.app.miner.username)
        self.app.update_friends(self.app.miner.username)

    def action_find_similar_users(self, widget):
        return self.app.second_grade_search()

    def action_update_config(self, widget):
        return self.startup_config()

    ##########
    # Builds #
    ##########

    def _build_users_table(self, data):
        similar_users_table = toga.Table(
            headings=[
                "Usuario",
                "Seguidores",
                "Tweets",
                "Último Tweet",
                "Afinidad"
            ],
            data=data,
            on_select=self.open_user_in_webview,
            on_double_click=self.open_user_dialog,
        )

        similar_users_container = toga.Box(
            style=Pack(
                direction=ROW,
            ),
        )

        similar_users_container.add(similar_users_table)
        return similar_users_container

    def _build_webview(self):
        webview = toga.WebView(
            style=Pack(
                direction=ROW,
            ),
            url="https://twitter.com/home",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)\
            AppleWebKit/537.36 (KHTML, like Gecko)\
            Chrome/70.0.3538.77 Safari/537.36",
        )
        return webview

    def _build_users_layout(self):
        similar_users_data = self.db.get_similar_users()
        follow_button = toga.Button(
            label="Seguir",
            on_press=self.follow_user,
        )
        similar_users_data = [
            row + [follow_button] for row in similar_users_data
        ]
        self.users_table = self._build_users_table(similar_users_data)
        self.webview = self._build_webview()
        sim_users_main_box = toga.SplitContainer(
            direction=toga.SplitContainer.VERTICAL,
            style=Pack(
                direction=ROW,
                flex=1,
            ),
        )

        sim_users_main_box.content = [
            (self.users_table, 1),
            (self.webview, 9),
        ]
        return sim_users_main_box

    def follow_user(self, widget):
        self.user_window.close()

    def hide_user(self, widget):
        user_id = widget
        self.db.hide_user(user_id)
        self.user_window.close()

    def _build_users_window(self):
        similar_users_window = toga.Window("Usuarios Afines")
        similar_users_window.toolbar.add(
            self.command_update_data,
            self.command_find_similar_users,
            self.command_show_hidden_users,
        )
        return similar_users_window

    def _build_main_window_layout(self):
        main_window = toga.MainWindow(
            title=self.formal_name,
        )
        main_window.toolbar.add(
            self.command_show_sim_users_window,
            self.command_update_config,
            self.command_update_data,
        )
        return main_window

    def _build_dashboard_layout(self):
        dashboard_main_box = toga.ScrollContainer()
        return dashboard_main_box

    ##########
    # Config #
    ##########

    def startup_config(self):
        config_loaded = config_check()
        if not config_loaded:

            input_params_box = toga.Box(
                style=Pack(
                    direction=ROW,
                    padding=5,
                ),
            )
            twitter_consumer_key_label = toga.Label(
                "Twitter Consumer Key: ",
                style=Pack(
                    padding=(5, 5),
                ),
            )
            self.twitter_consumer_key = toga.TextInput(
                style=Pack(
                    flex=1,
                ),
            )
            twitter_consumer_secret_key_label = toga.Label(
                "Twitter Consumer Secret Key: ",
                style=Pack(
                    padding=(5, 5),
                ),
            )
            self.twitter_consumer_secret_key = toga.TextInput(
                style=Pack(
                    flex=1,
                ),
            )
            user_screen_name_label = toga.Label(
                "Twitter Username: ", style=Pack(
                    padding=(5, 5),
                ),
            )
            self.user_screen_name = toga.TextInput(
                style=Pack(
                    flex=1,
                ),
            )

            input_params_box.add(
                twitter_consumer_key_label,
                self.twitter_consumer_key,
                twitter_consumer_secret_key_label,
                self.twitter_consumer_secret_key,
                user_screen_name_label,
                self.user_screen_name,
            )

            confirmation_button_box = toga.Box(
                style=Pack(
                    direction=ROW,
                    padding=5,
                ),
            )
            confirmation_button = toga.Button(
                "Confirmar",
                on_press=self.confirm_config_params,
                style=Pack(padding=50)
            )
            confirmation_button_box.add(confirmation_button)

            config_box = toga.Box(style=Pack(direction=COLUMN))
            config_box.add(input_params_box, confirmation_button_box)

            self.config_window = toga.Window(title="Configuración Inicial")
            self.config_window.content = config_box

            self.config_window.show()

    def confirm_config_params(self, widget):
        user = verify_config(
            self.twitter_consumer_key.value,
            self.twitter_consumer_secret_key.value,
            self.user_screen_name.value,
        )
        if isinstance(user, Exception):
            pass
        else:
            config_ok = self.config_window.confirm_dialog(
                title="Confirmar Datos de Configuración",
                message=f"Es este tú usuario?\n"
                f"Username: {user['user']}\n"
                f"Description: {user['description']}",
            )
            if config_ok:
                save_config(
                    self.twitter_consumer_key.value,
                    self.twitter_consumer_secret_key.value,
                    self.user_screen_name.value,
                )
                self.config_window.close()
            else:
                self.config_window.close()
                self.startup_config()

    ###########
    # Startup #
    ###########

    def startup(self):
        self.dashboard_main_box = self._build_dashboard_layout()
        self.main_window = self._build_main_window_layout()
        self.main_window.content = self.dashboard_main_box
        self.main_window.show()
        self.startup_config()


def main():
    return TwitterAnalysisApp()