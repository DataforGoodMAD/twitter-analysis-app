import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

from twitter_analysis_app.local_config import config_check, verify_config, save_config


class TwitterAnalysisApp(toga.App):
    def action_update_data(self):
        pass

    def action_find_similar_users(self):
        pass

    def action_update_config(self, widget):
        return self.startup_config()


    def main_window_layout(self):
        self.command_update_config = toga.Command(
            action=self.action_update_config,
            label="Actualizar Configuración",
            tooltip="Actualizar Configuración",
            # shortcut=toga.Key.MOD_1 + "k",
            # icon=cricket_icon,
        )

        self.command_update_data = toga.Command(
            action=self.action_update_data,
            label="Actualizar Datos",
            tooltip="Actualiza Tweets, Seguidores y Amigos del usuario principal",
            # shortcut=toga.Key.MOD_1 + "k",
            # icon=cricket_icon,
        )

        self.command_find_similar_users = toga.Command(
            action=self.action_find_similar_users,
            label="Encontrar Usuarios Afines",
            tooltip="Actualiza Tweets, Seguidores y Amigos del usuario principal",
            # shortcut=toga.Key.MOD_1 + "k",
            # icon=cricket_icon,
        )
        self.commands.add(self.command_update_data, self.command_find_similar_users)

        self.main_window = toga.MainWindow(
            title=self.formal_name,
            toolbar=[
                self.command_update_data, 
                self.command_find_similar_users,
            ]
        )

    ##########
    # Config #
    ##########
    def startup_config(self):
        config_loaded = config_check()
        if not config_loaded:

            input_params_box = toga.Box(style=Pack(direction=COLUMN, padding=5))
            twitter_consumer_key_label = toga.Label(
                "Twitter Consumer Key: ", style=Pack(padding=(5, 5))
            )
            self.twitter_consumer_key = toga.TextInput(style=Pack(flex=1))
            twitter_consumer_secret_key_label = toga.Label(
                "Twitter Consumer Secret Key: ", style=Pack(padding=(5, 5))
            )
            self.twitter_consumer_secret_key = toga.TextInput(style=Pack(flex=1))
            user_screen_name_label = toga.Label(
                "Twitter Username: ", style=Pack(padding=(5, 5))
            )
            self.user_screen_name = toga.TextInput(style=Pack(flex=1))

            input_params_box.add(
                twitter_consumer_key_label,
                self.twitter_consumer_key,
                twitter_consumer_secret_key_label,
                self.twitter_consumer_secret_key,
                user_screen_name_label,
                self.user_screen_name,
            )

            confirmation_button_box = toga.Box(style=Pack(direction=ROW, padding=5))
            confirmation_button = toga.Button(
                "Confirmar", on_press=self.confirm_config_params, style=Pack(padding=50)
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

    def startup(self):
        self.main_window_layout()
        self.main_box = toga.Box(style=Pack(direction=COLUMN))

        self.main_window.content = self.main_box
        self.main_window.show()
        self.startup_config()


def main():
    return TwitterAnalysisApp()
