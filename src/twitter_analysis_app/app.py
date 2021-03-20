import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

from twitter_analysis_app.features import (
    build_db_queries,
    build_twitter_miner,
    build_twitter_processor,
    update_followers,
    update_friends,
    update_timeline,
    update_tokens_count,
)
from .db_queries import DBQueries
from twitter_analysis_app.local_config import config_check, verify_config, save_config
from twitter_analysis_app.db_models import AccountTimeline, TokensCount, Tweet, User


class TwitterAnalysisApp(toga.App):
    def __init__(self, db, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.twitter_consumer_key = (False,)
        self.twitter_consumer_secret_key = (False,)
        self.user_screen_name = (False,)
        self.db = build_db_queries()
        self.miner = build_twitter_miner()
        self.processor = build_twitter_processor()

    ##########
    # Utils  #
    ##########

    def _open_user_in_webview(self, table, row):
        base_url = "https://twitter.com/"
        self.webview.url = base_url + row.user

    def _get_similar_users(self):
        with self.db.get_session() as session:
            sim_users = (
                session.query(User)
                .filter(User.similarity_score >= 0.75)
                .order_by(User.similarity_score)
                .all()
            )
        data = [(user.screen_name, user.similarity_score) for user in sim_users]
        return data

    ###########
    # Actions #
    ###########

    def action_show_sim_users_window(self, widget):
        self.similar_users_main_box = self._build_similar_users_layout()
        self.sim_users_window = self._build_similar_users_window()
        self.sim_users_window.content = self.similar_users_main_box
        self.sim_users_window.show()

    def action_update_data(self, widget):
        #TODO: Refactorizar
        p = self.processor
        m = self.miner
        d = self.db
        update_timeline(p, d, m)
        update_tokens_count(p, d)
        update_followers(d, m, self.user_screen_name)
        update_friends(p, d, m)

    def action_find_similar_users(self, widget):
        pass

    def action_update_config(self, widget):
        return self.startup_config()

    ##########
    # Builds #
    ##########

    def _build_similar_users_table(self):

        similar_users_data = self._get_similar_users()

        sim_users_table = toga.Table(
            headings=["User", "Similarity Score"],
            data=similar_users_data,
            on_select=self._open_user_in_webview,
        )

        sim_users_container = toga.Box(
            style=Pack(direction=ROW),
        )

        sim_users_container.add(sim_users_table)
        return sim_users_container

    def _build_webview(self):
        webview = toga.WebView(
            style=Pack(
                flex=1,
                direction=COLUMN,
            ),
            url="https://twitter.com/home",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)\
            AppleWebKit/537.36 (KHTML, like Gecko)\
            Chrome/70.0.3538.77 Safari/537.36",
        )
        return webview

    def _build_similar_users_layout(self):
        self.similar_users_container = self._build_similar_users_table()
        self.webview = self._build_webview()
        sim_users_main_box = toga.SplitContainer(direction=toga.SplitContainer.VERTICAL)
        sim_users_main_box.content = [self.similar_users_container, self.webview]
        return sim_users_main_box

    def _build_similar_users_window(self):
        similar_users_window = toga.Window("Usuarios Afines")
        similar_users_window.toolbar.add(
            self.command_update_data,
            self.command_find_similar_users,
        )
        return similar_users_window

    def _build_dashboard_layout(self):
        dashboard_main_box = toga.ScrollContainer()
        return dashboard_main_box

    def _build_main_window_layout(self):
        actions = toga.Group("Actions")

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
            tooltip="Actualiza Tweets, Seguidores y Amigos del usuario principal",
            icon=icon,
        )

        self.command_show_sim_users_window = toga.Command(
            action=self.action_show_sim_users_window,
            label="Usuarios Afines",
            tooltip="Actualiza Tweets, Seguidores y Amigos del usuario principal",
            icon=icon,
        )

        main_window = toga.MainWindow(
            title=self.formal_name,
        )

        main_window.toolbar.add(
            self.command_show_sim_users_window,
            self.command_update_config,
            self.command_update_data,
            self.command_find_similar_users,
        )
        return main_window

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
    db = DBQueries()
    return TwitterAnalysisApp(db)
