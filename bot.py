# ici tu met les dépendence que ta besoin pour ton projet (ex: dotenv pour charger les variables d'environnement)
from dotenv import load_dotenv
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import aiohttp

load_dotenv()

# ici t'appelle ton token qui es dans le .env
api_telegram = os.getenv("KEY_API_TELEGRAM")
key_odds = os.getenv('KEY_ODDS')

# sa c'est le code pour verifier si ton token existe
# if api_telegram:
#     print("le token existe", api_telegram)
# else:
#     print("sa marche pas")    

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("contactez support@test.com en cas de probleme")

async def parionsSport(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Je récupère les cotes...")

    url = (
        "https://api.the-odds-api.com/v4/sports/soccer_france_ligue_one/odds"
        f"?regions=eu&markets=h2h&oddsFormat=decimal&apiKey={key_odds}"
    )

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                return await update.message.reply_text(
                    f"❌ Erreur : impossible de récupérer les cotes (code {resp.status})"
                )
            data = await resp.json()

    if not data:
        return await update.message.reply_text("⚠️ Aucun match disponible pour le moment.")

    messages = []
    for match in data:
        home = match["home_team"]
        away = match["away_team"]
        bookmakers = match["bookmakers"]

        if not bookmakers:
            continue

        bookmaker = bookmakers[0]  # premier bookmaker dispo
        odds = bookmaker["markets"][0]["outcomes"]

        home_odd = None
        away_odd = None
        draw_odd = None

        # Récupération des cotes
        for o in odds:
            if o["name"] == home:
                home_odd = o["price"]
            elif o["name"] == away:
                away_odd = o["price"]
            elif o["name"].lower() in ["draw", "nul", "tie"]:
                draw_odd = o["price"]

        # Création message stylé
        text = (
            f"⚽ *{home} vs {away}*\n"
            f"📅 Bookmaker : _{bookmaker['title']}_\n\n"
            f"🏠 Victoire *{home}* : `{home_odd}`\n"
            f"🆚 Match nul : `{draw_odd if draw_odd else '—'}`\n"
            f"🚀 Victoire *{away}* : `{away_odd}`\n"
            f"──────────────────────\n"
        )
        messages.append(text)

    final_message = "📊 *Cotes Ligue 1 – ParionsSport*\n\n" + "".join(messages)
    await update.message.reply_text(final_message, parse_mode="Markdown")


async def Menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    menu_text = (
        "🌟 *Bienvenue dans le menu du bot !*\n\n"
        "Voici ce que je peux faire pour toi :\n\n"
        "⚽ *Cotes Sportives* : /cotes\n"
        "    Obtiens les dernières cotes pour la Ligue 1.\n\n"
        "ℹ️ *Aide* : /start\n"
        "    Instructions et informations sur le bot.\n\n"
        "💡 *Conseil* : Utilise les commandes ci-dessus pour interagir avec moi.\n\n"
        "─────────────────────────────\n"
        "🔗 *Restez connecté pour les mises à jour !*"
    )
    await update.message.reply_text(menu_text, parse_mode="Markdown")


def main():
    application = Application.builder().token(api_telegram).build()

    # On ajoute les handlers directement à l'application
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("cotes", parionsSport))
    application.add_handler(CommandHandler("menu", Menu))

    application.run_polling()


if __name__ == '__main__':
    main()
