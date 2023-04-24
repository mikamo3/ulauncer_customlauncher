import subprocess
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
        subprocess.run(['code', arg])


class KeywordQueryEventListener(EventListener):
    def on_event(self, event: KeywordQueryEvent, extension: VSCodeExtension):
        if event.get_argument() == None:
            extension.repositories = getRepositoryList()
        items = []
        filterd = []
        if event.get_argument() == None:
            filterd = [r["title"] for r in extension.repositories]
        else:
            filterd = filter(extension.repositories, event.get_argument())

        for i in extension.repositories:
            if i["title"] in filterd:
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
        output.append({"abs": r, "title": r.split(
            '/')[-1], "rel": re.sub(f"^{root}/", "", r)})
    return output


def filter(repositories, query):
    namelist = [r["title"] for r in repositories]
    cmd = 'echo -e "{}"| fzf --filter "{}"'.format('\n'.join(namelist), query)
    return subprocess.run(cmd, stdout=subprocess.PIPE,
                          shell=True).stdout.decode('utf-8').splitlines()


if __name__ == '__main__':
    VSCodeExtension().run()
