import sublime
import sublime_plugin
# import json
import re

class Settings:
  settings = sublime.load_settings('tailwind_reorder.sublime-settings')

  @staticmethod
  def init():
    Settings.settings.add_on_change('tailwind_reorder' + '-reload', Settings.setup)
    Settings.setup()

  @staticmethod
  def setup():
    Settings.filter_by = Settings.settings.get('filter_by', 0)
    Settings.classNames = Settings.settings.get('classNames', 0)
    Settings.scopes = Settings.settings.get('scopes', 0)
    Settings.data = Settings.settings.get('data', 0)

def plugin_loaded():
    Settings.init()
    print(Settings.scopes)

class TailwindOrderCommand(sublime_plugin.TextCommand):

    def getRegexClassNames(self):
        classNames = Settings.classNames
        # classNames = self.settings.get('classNames')
        regex = "(?:"
        for item in classNames:
            regex += '(?<=' + item + '=")|'
        regex += '(?<=class="))(.*?)(?=")'
        # '(?:(?<=class=")|(?<=className="))(.*?)(?=")'
        return regex

    # def checkScope1(self):
    #     # scopes = self.settings.get('scopes')
    #     cursor = self.view.sel()[0].begin()
    #     curr_scope = view.scope_name(cursor)

    #     return (curr_scope in scopes)

    def checkScope(self):
        scopes = Settings.scopes
        # scopes = self.settings.get('scopes')
        # matchHTMLString = view.match_selector(locations[0], "text.html string.quoted")
        match = next(filter(lambda scope: self.view.find_by_selector(scope), scopes), None)
        return match

    def create_filters(self, list):
        filter_by = {}
        for item in list:
            filter_by[item] = []
        return filter_by

    def run(self, edit):
        # if not hasattr(self, "settings"):
        #     self.settings = sublime.load_settings("tailwind-order.sublime-settings")
        if not self.checkScope():
            return 0
        regex = self.getRegexClassNames()
        filter_by = Settings.filter_by
        # filter_by = self.settings.get('filter_by')
        file = Settings.data
        # file = self.settings.get('data')

        # file = sublime.load_resource(sublime.find_resources('data.json')[0])
        # file = json.loads(file)
        dif = 0
        classes = self.view.find_all(regex)
        # classes = self.view.find_all('(?<=class=")(.*?)(?=")')

        for item in classes:
            if not dif == 0:
                item.a += dif
                item.b += dif
            # region = item
            originStr = self.view.substr(item)
            temp_str = originStr.strip()
            if not temp_str:
                continue
            temp_classes = re.sub(' +', ' ', temp_str)
            temp_classes = temp_classes.split(' ')

            if len(temp_classes) < 2:
                if not originStr == temp_str:
                    self.view.replace(edit, item, temp_str)
                    dif += len(temp_str) - len(originStr)
                continue
            filters = self.create_filters(filter_by)

            other_classes = temp_classes[:]
            sorted_class = ""

            for temp_class in temp_classes:
                for tw_class in file:
                    if temp_class.startswith(tw_class['name']):
                        if tw_class['kind'] in filters.keys() and temp_class not in filters[tw_class['kind']]:
                            filters[tw_class['kind']].append(temp_class)
                            if temp_class in other_classes:
                                other_classes.remove(temp_class)
                        break # because flex-wrap will have flex and flex-
            for kind in filter_by:
            # for kind in filters.keys():
                if not filters[kind]:
                    continue
                filters[kind] = sorted(filters[kind])
                sorted_class += ' '.join(filters[kind]) + ' '
                # if filters[kind]:
                    # sorted_class += ' '
            if other_classes:
                # ' '.join will add empty string when join because classes now arr and sorted return arr
                if sorted_class:
                    sorted_class = ' '.join(sorted(other_classes)) + ' ' + sorted_class[:-1]
                else:
                    sorted_class = ' '.join(sorted(other_classes))
                # sorted_class += ' '.join(sorted(other_classes))
            self.view.replace(edit, item, sorted_class)
            dif += len(sorted_class) - len(originStr)
            # dif += len(sorted_class) - len(str(self.view.substr(item)))
