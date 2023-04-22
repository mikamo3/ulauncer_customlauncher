import subprocess
import logging
import re
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import ItemEnterEvent, KeywordQueryEvent, PreferencesEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction


class VSCodeExtension(Extension):

    def __init__(self):
        super().__init__()
        self.subscribe(PreferencesEvent, OnLoad())
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())
        self.repositories = []


class ItemEnterEventListener(EventListener):
    def on_event(self, event: ItemEnterEvent, extension: VSCodeExtension):
        arg = event.get_data()
        logging.info(arg)
        subprocess.run(['code', arg])


class KeywordQueryEventListener(EventListener):
    def on_event(self, event: KeywordQueryEvent, extension: VSCodeExtension):
        if event.get_argument() == None:
            extension.repositories = getRepositoryList()
        items = []
        logging.info(extension.repositories)
        for i in extension.repositories:
            if event.get_argument() == None or (event.get_argument().lower() in i["rel"].lower()):
                items.append(ExtensionResultItem(icon='/usr/share/icons/visual-studio-code.png',
                                                 name=i["title"],
                                                 description=i["rel"],
                                                 on_enter=ExtensionCustomAction(
                                                     data=i["abs"], keep_app_open=False),
                                                 )
                             )

        return RenderResultListAction(items)


class OnLoad(EventListener):
    def on_event(self, event, extension: VSCodeExtension):
        extension.repositories = getRepositoryList()
        return super().on_event(event, extension)


def getRepositoryList():
    root = subprocess.run(
        ['ghq', 'root'], stdout=subprocess.PIPE).stdout.decode('utf-8').splitlines()[0]
    result = subprocess.run(
        ['ghq', 'list', '-p'], stdout=subprocess.PIPE).stdout.decode('utf-8').splitlines()
    output = []
    for r in result:
        logging.info(root)
        logging.info(r)
        logging.info(re.sub(f"^{root}/", "", r))
        output.append({"abs": r, "title": r.split(
            '/')[-1], "rel": re.sub(f"^{root}/", "", r)})
    return output


if __name__ == '__main__':
    VSCodeExtension().run()
