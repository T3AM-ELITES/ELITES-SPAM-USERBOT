import os
import datetime

from PIL import Image
from telegraph import Telegraph, exceptions, upload_file

from . import *


DEADLY_NAME = str(ALIVE_NAME) if ALIVE_NAME else "Deadly User"

opsameer = str(ALIVE_NAME) if ALIVE_NAME else "Deadly Bot"

telegraph = Telegraph()
r = telegraph.create_account(short_name=Config.TELEGRAPH_SHORT_NAME)
auth_url = r["auth_url"]


@bot.on(admin_cmd(pattern=f"t(m|t) ?(.*)", outgoing=True))
@bot.on(sudo_cmd(pattern=f"t(m|t) ?(.*)", allow_sudo=True))
async def _(event):
    if event.fwd_from:
        return
    if Config.PLUGIN_CHANNEL is None:
        await eod(event, "You need to setup `PLUGIN_CHANNEL` to use telegraph...", 7)
        return
    if not os.path.isdir(Config.TMP_DOWNLOAD_DIRECTORY):
        os.makedirs(Config.TMP_DOWNLOAD_DIRECTORY)
    optional_title = event.pattern_match.group(2)
    if event.reply_to_msg_id:
        start = datetime.datetime.now()
        r_message = await event.get_reply_message()
        input_str = event.pattern_match.group(1)
        if input_str == "m":
            downloaded_file_name = await bot.download_media(
                r_message, Config.TMP_DOWNLOAD_DIRECTORY
            )
            end = datetime.datetime.now()
            ms = (end - start).seconds
            await edit_or_reply(event, 
                "Downloaded to  `{}`  in  `{}`  seconds. \nMaking Telegraph Link.....".format(downloaded_file_name, ms)
            )
            if downloaded_file_name.endswith((".webp")):
                resize_image(downloaded_file_name)
            try:
                start = datetime.datetime.now()
                media_urls = upload_file(downloaded_file_name)
            except exceptions.TelegraphException as exc:
                await eod(event, "ERROR: " + str(exc), 8)
                os.remove(downloaded_file_name)
            else:
                end = datetime.datetime.now()
                ms_two = (end - start).seconds
                os.remove(downloaded_file_name)
                await edit_or_reply(event, 
                   "✓ **File uploaded to [telegraph](https://telegra.ph{})** \n✓ **Time Taken :-** `{}` secs \n✓ **By :- {}**".format(
                        media_urls[0], (ms + ms_two), DEADLY_NAME, opsameer
                    ),
                    link_preview=True,
                )
        elif input_str == "t":
            user_object = await borg.get_entity(r_message.sender_id)
            title_of_page = user_object.first_name  # + " " + user_object.last_name
            # apparently, all Users do not have last_name field
            if optional_title:
                title_of_page = optional_title
            page_content = r_message.message
            if r_message.media:
                if page_content != "":
                    title_of_page = page_content
                downloaded_file_name = await borg.download_media(
                    r_message, Config.TMP_DOWNLOAD_DIRECTORY
                )
                m_list = None
                with open(downloaded_file_name, "rb") as fd:
                    m_list = fd.readlines()
                for m in m_list:
                    page_content += m.decode("UTF-8") + "\n"
                os.remove(downloaded_file_name)
            page_content = page_content.replace("\n", "<br>")
            response = telegraph.create_page(title_of_page, html_content=page_content)
            end = datetime.datetime.now()
            ms = (end - start).seconds
            hellboy = f"https://telegra.ph/{response['path']}"
            await edit_or_reply(event, 
                  f"✓ **Pasted to** [telegraph]({opsameer}) \n✓ **Time Taken :-** `{ms}` secs\n✓** By :**  {DEADLY_NAME}", link_preview=True)
    else:
        await eod(event, 
            "Reply to a message to get a permanent telegra.ph link."
        )


def resize_image(image):
    im = Image.open(image)
    im.save(image, "PNG")


CmdHelp("telegraph").add_command(
  "tt", "<reply to text message>", "Uploads the replied text message to telegraph making a short telegraph link"
).add_command(
  "tm", "<reply to media>", "Uploads the replied media (sticker/ gif/ video/ image) to telegraph and gives a short telegraph link"
).add_info(
  "Make Telegraph Links."
).add_warning(
  "✅ Harmless Module."
).add()
