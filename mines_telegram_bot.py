import time
import telebot
import random
import datetime
import validators
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID
from mines import get_mines_data
from telebot import types

class TelegramBot:
    def __init__(self):
        self.bot = telebot.TeleBot(token=TELEGRAM_BOT_TOKEN)
        self.bot_interval = None
        self.is_running = False
        self.message_text = None
        self.final_message_text = None
        self.link = None
        self.message_link = None
        self.message_link_final = None
        self.pausar = False
        self.change = False
        self.ok = False
        self.COMMANDS=['/start','/pause','/restart','/mudar_sinal','/mudar_finalizacao','/mudar_texto_link','mudar_link']

    def send_signals_to_telegram_channel(self, signals: dict):
        safe_positions = signals['safe_positions']
        selected_safe_positions = random.sample(safe_positions, 5)
        safe_positions_str = ""

        for row in range(5):
            for col in range(5):
                if (row, col) in selected_safe_positions:
                    safe_positions_str += "⭐️"
                else:
                    safe_positions_str += "🟦"
                if col == 4:
                    safe_positions_str += "\n"

        message = f"{self.message_text}\n\n{safe_positions_str}\n\n{self.message_link_final}"
        self.bot.send_message(chat_id=TELEGRAM_CHANNEL_ID, disable_web_page_preview=True, text=message, parse_mode='MarkdownV2')

        time.sleep(2 * 60) # Tempo ativo

        now = datetime.datetime.now()
        final_message_time = now.strftime("%H:%M")
        final_message = f"{self.final_message_text} {final_message_time}"
        
        self.bot.send_message(chat_id=TELEGRAM_CHANNEL_ID, text=final_message, parse_mode='MarkdownV2')

    def run_bot_every_interval(self):
        while self.is_running:
            signals = get_mines_data()
            self.send_signals_to_telegram_channel(signals)
            if self.pausar:
                self.bot.reply_to(self.msg_pause, 'O Bot Foi Pausado.')
                self.is_running = False
            time.sleep(3 * 60)

    def start(self, message):
        if not self.is_running:
            self.bot.reply_to(message, 'Por favor, digite a mensagem do sinal:')
            self.bot.register_next_step_handler(message, self.set_message)
        else:
            self.bot.reply_to(message, 'O bot já está em execução.')

    def set_message(self, message):
        self.message_text = message.text
        if self.message_text in self.COMMANDS:
            self.bot.reply_to(message, 'Esse texto não é permitido, digite novamente:')
            self.bot.register_next_step_handler(message, self.set_message)
        else:
            self.bot.reply_to(message, 'Por favor, digite a mensagem de finalização\n- Lembre-se de que o horário sempre aparecerá por último\n- EX:✅ Pago, finalizado as 02:15')
            self.bot.register_next_step_handler(message, self.set_final_message)

    def set_final_message(self, message):
        self.final_message_text = message.text
        if self.final_message_text in self.COMMANDS:
            self.bot.reply_to(message, 'Esse texto não é permitido, digite novamente:')
            self.bot.register_next_step_handler(message, self.set_final_message)
        else:
            self.bot.reply_to(message, 'Por favor, digite a mensagem que irá conter um link:')
            self.bot.register_next_step_handler(message, self.set_message_link)

    def set_message_link(self, message):
        self.message_link = message.text
        if self.message_link in self.COMMANDS:
            self.bot.reply_to(message, 'Esse texto não é permitido, digite novamente:')
            self.bot.register_next_step_handler(message, self.set_message_link)
        else:
            self.bot.reply_to(message, 'Por favor, digite o link no formato correto\nEX: https://google.com\nLinks com formato incorreto não serão aceitos')
            self.bot.register_next_step_handler(message, self.set_link)



    def set_link(self, message):
        self.link = message.text
        link = validators.url(self.link)
        if not link:
            self.bot.reply_to(message, 'Formato de link incorreto. Por favor, digite o link novamente:')
            self.bot.register_next_step_handler(message, self.set_link)
        else:
            self.message_link_final = f"[{self.message_link}]({self.link})"
            self.bot.reply_to(message, 'Link definido com sucesso!')

            if not self.is_running:
                self.bot.reply_to(message, 'Bot iniciado!')
                self.is_running = True
                self.ok = True
                self.run_bot_every_interval()
            else:
                self.bot.reply_to(message, 'Bot já está em execução!')

    def pause(self, message):
        if self.is_running and not self.pausar:
            self.pausar = True
            self.is_running = False
            self.bot.reply_to(message, 'Bot irá ser pausado após o término do sinal !')
            self.msg_pause= message
        else:
            self.bot.reply_to(message, 'O bot não está em execução ou já clicou para pausar.')


    def restart(self,message):
        if not self.is_running and self.ok and not self.pausar:
            self.pausar = False
            self.is_running = True
            self.run_bot_every_interval()
            self.bot.reply_to(message, 'Bot reinciado !')
        else:
            self.bot.reply_to(message, 'Bot em execução ou nao foi iniciado !')


    def change_message(self, message):
        if self.is_running:
            self.bot.reply_to(message, 'Não é possível alterar a mensagem enquanto o bot estiver em execução. Por favor, pause o bot primeiro.')
        else:
            self.change = True
            self.bot.reply_to(message, 'Por favor, digite a nova mensagem do sinal:')
            self.bot.register_next_step_handler(message, self.mudar_texto)

    def change_final_message(self, message):
        if self.is_running:
            self.bot.reply_to(message, 'Não é possível alterar a mensagem final enquanto o bot estiver em execução. Por favor, pause o bot primeiro.')
        else:
            self.change = True
            self.bot.reply_to(message, 'Por favor, digite a nova mensagem de finalização:')
            self.bot.register_next_step_handler(message, self.mudar_final)

    def change_message_link(self, message):
        if self.is_running:
            self.bot.reply_to(message, 'Não é possível alterar a mensagem do link enquanto o bot estiver em execução. Por favor, pause o bot primeiro.')
        else:
            self.change = True
            self.bot.reply_to(message, 'Por favor, digite o novo texto do link:')
            self.bot.register_next_step_handler(message, self.mudar_texto_link)

    def change_link(self, message):
        if self.is_running:
            self.bot.reply_to(message, 'Não é possível alterar o link enquanto o bot estiver em execução. Por favor, pause o bot primeiro.')
        else:
            self.change = True
            self.bot.reply_to(message, 'Por favor, digite o novo link:')
            self.bot.register_next_step_handler(message, self.mudar_link)

    def mudar_texto(self,message):
        self.message_text = message.text

        if '/' in self.message_text:
            self.bot.reply_to(message, 'Formato de texto incorreto !')
            self.change_message(message)
        else:
            self.bot.reply_to(message, 'Texto Alterado com sucesso, aperta /restart para reiniciar')

    def mudar_final(self,message):
        self.final_message_text = message.text = message.text

        if '/' in self.final_message_text:
            self.bot.reply_to(message, 'Formato de texto incorreto !')
            self.change_final_message(message)
        else:
            self.bot.reply_to(message, 'Texto Alterado com sucesso, aperta /restart para reiniciar')

    def mudar_texto_link(self,message):
        self.message_link = message.text
        if '/' in self.final_message_text:
            self.bot.reply_to(message, 'Formato de texto incorreto !')
            self.change_message_link(message)
        else:
            self.message_link_final = f"[{self.message_link}]({self.link})"
            self.bot.reply_to(message, 'Texto do Link Alterado com sucesso, aperta /restart para reiniciar')

    def mudar_link(self,message):
        self.link = message.text 
       
        if '.com' in self.link:
            self.message_link_final = f"[{self.message_link}]({self.link})"
            self.bot.reply_to(message, 'Link alterado com sucesso, aperta /restart para reiniciar')
        else:
            self.bot.reply_to(message, 'Formato de link incorreto !')
            self.change_link(message)

    def handle_user_input(self, message):
        if message.content_type == 'text' and message.text.startswith('/'):
            available_commands = ['/start', '/pause', '/mudar_sinal', '/mudar_finalizacao', '/mudar_texto_link', '/mudar_link']

            keyboard_markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
            keyboard_markup.add(*available_commands)

    def handle_unknown_commands(self, message):
        self.bot.reply_to(message, '\n/start para iniciar o bot\n/pause para pausá-lo\n/restart para reinciar o bot\n/mudar_sinal para alterar a mensagem do sinal\n/mudar_finalizacao para alterar a mensagem final\n/mudar_texto_link para alterar o texto do link\n/mudar_link para alterar o link.')
        
    def run(self):
        @self.bot.message_handler(commands=['start'])
        def start_command(message):
            self.start(message)

        @self.bot.message_handler(commands=['pause'])
        def pause_command(message):
            self.pause(message)
        @self.bot.message_handler(commands=['restart'])
        def restart_command(message):
            self.restart(message)

        @self.bot.message_handler(commands=['mudar_sinal'])
        def change_command(message):
            self.change_message(message)

        @self.bot.message_handler(commands=['mudar_finalizacao'])
        def change_final_command(message):
            self.change_final_message(message)

        @self.bot.message_handler(commands=['mudar_texto_link'])
        def change_text_link_command(message):
            self.change_message_link(message)

        @self.bot.message_handler(commands=['mudar_link'])
        def change_link_command(message):
            self.change_link(message)

        @self.bot.message_handler(func=lambda message: True)
        def unknown_command(message):
            self.handle_unknown_commands(message)

        @self.bot.message_handler(func=lambda message: True)
        def unknow_command(message):
            self.handle_user_input(message)


        self.bot.polling()


if __name__ == "__main__":
    bot = TelegramBot()
    bot.run()
