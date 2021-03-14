import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from .db_queries import DBQueries
from twitter_analysis_app.local_config import config_check, verify_config, save_config
from .db_models import AccountTimeline, TokensCount, Tweet, User


class TwitterAnalysisApp(toga.App):
    def __init__(self, db, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = db

    def action_update_data(self, widget):
        pass

    def action_find_similar_users(self, widget):
        pass

    def action_update_config(self, widget):
        return self.startup_config()

    def _get_similar_users(self):
        with self.db.get_session() as session:
           sim_users = session.query(User).filter(User.similarity_score >= 0.75).all()
        base_url = "https://twitter.com/"
        data = [
            (user.screen_name, user.similarity_score)
            for user in sim_users
        ]
        return data



    def main_box_layout(self):

        self.main_box = toga.SplitContainer()

        self.left_container = toga.Box(
            style=Pack(direction=COLUMN),
        )

        self.right_container = toga.ScrollContainer()

        similar_users = self._get_similar_users()

        self.right_container = toga.Table(
            headings=["User", "Similarity Score"],
            data=similar_users,
        )

        webview_container = toga.WebView(style=Pack(flex=1))
        self.left_container.add(webview_container)

        self.main_box.content = [self.right_container, self.left_container]

        return self.main_box

    def main_window_layout(self):
        actions = toga.Group("Actions")

        icon = "resources/logo_dfg.png"

        self.command_update_config = toga.Command(
            action=self.action_update_config,
            label="Actualizar Configuración",
            tooltip="Actualizar Configuración",
            group=actions,
            # shortcut=toga.Key.MOD_1 + "k",
            icon=icon,
        )

        self.command_update_data = toga.Command(
            action=self.action_update_data,
            label="Actualizar Datos",
            tooltip="Actualiza Tweets, Seguidores y Amigos del usuario principal",
            # shortcut=toga.Key.MOD_1 + "k",
            icon=icon,
            group=actions,
        )

        self.command_find_similar_users = toga.Command(
            action=self.action_find_similar_users,
            label="Encontrar Usuarios Afines",
            tooltip="Actualiza Tweets, Seguidores y Amigos del usuario principal",
            # shortcut=toga.Key.MOD_1 + "k",
            icon=icon,
            group=actions,
        )

        self.dashboard_window = toga.Command(
            action=self.action_find_similar_users,
            label="Ver Dashboard",
            tooltip="Actualiza Tweets, Seguidores y Amigos del usuario principal",
            # shortcut=toga.Key.MOD_1 + "k",
            icon=icon,
            group=actions,
        )

        self.commands.add(
            self.command_update_config,
            self.command_update_data,
            self.command_find_similar_users,
            self.dashboard_window,
        )

        self.main_window = toga.MainWindow(
            title=self.formal_name,
        )

        self.main_window.toolbar.add(
            self.command_update_config,
            self.command_update_data,
            self.command_find_similar_users,
        )
        return self.main_window

    ##########
    # Config #
    ##########
    def startup_config(self):
        config_loaded = config_check()
        if not config_loaded:

            input_params_box = toga.Box(style=Pack(direction=ROW, padding=5))
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
        self.main_box_layout()
        self.main_window_layout()
        self.main_window.content = self.main_box
        self.main_window.show()
        self.startup_config()


def main():
    db = DBQueries()
    return TwitterAnalysisApp(db)
