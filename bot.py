import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import os 
import asyncio
from typing import Optional

# --- 1. CONFIGURAÇÃO (LÊ VARIÁVEIS DE AMBIENTE) ---

# O código lê o token e o chat ID de variáveis de ambiente. 
# VOCÊ NÃO PRECISA ALTERAR NADA AQUI.
TOKEN: Optional[str] = os.environ.get('BOT_TOKEN') 
# O ADMIN_CHAT_ID é lido como string do ambiente e convertido para int.
ADMIN_CHAT_ID: Optional[int] = None
admin_chat_id_str = os.environ.get('ADMIN_CHAT_ID')
if admin_chat_id_str:
    try:
        ADMIN_CHAT_ID = int(admin_chat_id_str)
    except ValueError:
        pass # Se a conversão falhar, será tratado como erro abaixo

# Configuração de log
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- 2. FUNÇÃO DE TRATAMENTO DE NOVO MEMBRO ---

async def novo_membro_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Trata o evento de novos membros entrando no grupo e notifica os administradores.
    """
    
    # Verifica se há novos membros na mensagem de serviço
    if update.message and update.message.new_chat_members and ADMIN_CHAT_ID:
        
        # Pega as informações do grupo onde o novo membro entrou
        group_name = update.message.chat.title
        group_id = update.message.chat_id

        for user in update.message.new_chat_members:
            # Ignora o próprio bot se ele for adicionado ao grupo (muito comum)
            if user.id == context.bot.id:
                logger.info(f"O próprio bot foi adicionado ao grupo {group_name}.")
                continue

            # Pega as informações do novo membro
            user_id = user.id
            # Escapa o '@' para o MarkdownV2
            username = f"\\@{user.username}" if user.username else "\*Sem Username\*" 
            first_name = user.first_name if user.first_name else ""
            last_name = user.last_name if user.last_name else ""
            full_name = f"{first_name} {last_name}".strip()
            
            # Formatação da Mensagem (usando MarkdownV2 para negrito e links)
            # Caracteres especiais como ., -, (, ) devem ser escapados com \
            
            mensagem_notificacao = f"""
🚨 \*\*NOVO MEMBRO REGISTRADO\!\*\* 🚨

👥 \*\*Grupo:\*\* `{group_name}` \(`{group_id}`\)

👤 \*\*Detalhes do Usuário:\*\*
  • \*\*ID:\*\* `{user_id}`
  • \*\*Nome Completo:\*\* `{full_name}`
  • \*\*Username:\*\* {username}
  • \*\*Link:\*\* [Ver Perfil](tg://user?id={user_id})
  
\-\-\-
✅ \*\*Ação:\*\* Notificação de entrada enviada\.
"""
            
            # Envia a mensagem de notificação para o chat privado dos administradores
            try:
                await context.bot.send_message(
                    chat_id=ADMIN_CHAT_ID,
                    text=mensagem_notificacao,
                    parse_mode='MarkdownV2' 
                )
                logger.info(f"Notificação de novo membro ({user_id}) enviada com sucesso para o ADMIN_CHAT_ID.")
            except Exception as e:
                logger.error(f"Erro ao enviar notificação para o Admin Chat ID: {e}")
                
            # Adicione um pequeno delay para evitar flood (opcional)
            await asyncio.sleep(0.5)


# --- 3. EXECUÇÃO PRINCIPAL DO BOT ---

def main():
    """Inicia o bot."""
    if not TOKEN:
        logger.error("ERRO: A variável de ambiente BOT_TOKEN não está configurada.")
        return
    if not ADMIN_CHAT_ID:
        logger.error("ERRO: A variável de ambiente ADMIN_CHAT_ID não está configurada ou é inválida.")
        return

    # Cria o Application e passa o token
    application = Application.builder().token(TOKEN).build()

    # Adiciona o 'handler' que escuta o evento de 'new_chat_members'
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, novo_membro_handler))

    # Inicia o bot (polling)
    print("🤖 Bot iniciado e escutando novos membros...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
          
