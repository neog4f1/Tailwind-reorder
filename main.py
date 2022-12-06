import sublime
import sublime_plugin
# import json
import re

class Settings:
  @staticmethod
  def init():
    Settings.settings = sublime.load_settings('tailwind_reorder.sublime-settings')
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

class TailwindOrderCommand(sublime_plugin.TextCommand):

    # def getRegexClassNames(self):
        # classNames = Settings.classNames
        # # classNames = self.settings.get('classNames')
        # regex = "(?:"
        # for item in classNames:
            # regex += '(?<=' + item + '=")|'
        # regex = regex[:-1] + ')(.*?)(?=")'
        # # '(?:(?<=class=")|(?<=className="))(.*?)(?=")'
        # return regex

    def getClassNames(self):
        classNames = Settings.classNames
        regex = r'('
        for i in classNames:
            regex += i + '|'
        regex = regex[:-1] + ')\s*=[^\"\']*[\"|\'](?P<str>[^\"\']*)[\"|\']'
        classes = []
        target_string = self.view.substr(sublime.Region(0, self.view.size()))
        pattern = re.compile(regex)
        # pattern = re.compile("(className|class|ClassName)\s*=[^\"\']*[\"|\'](?P<str>[^\"\']*)[\"|\']")
        n = pattern.finditer(target_string)
        # Extract matching values of all groups
        for match in n:
            # extract words
            classes.append({ 'data': match.group('str'), 'region': sublime.Region(match.start('str'), match.end('str')) })
            # classes.append(match.group('str'))

        return classes

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
 
    def replace(self, edit, region, str, originStr, dif):
        self.view.replace(edit, region, str)
        dif += len(str) - len(originStr)
        return dif

    def run(self, edit):
        # if not hasattr(self, "settings"):
        #     self.settings = sublime.load_settings("tailwind-order.sublime-settings")
        if not self.checkScope():
            return 0

        filter_by = Settings.filter_by
        # filter_by = self.settings.get('filter_by')
        file = Settings.data
        # file = self.settings.get('data')

        # file = sublime.load_resource(sublime.find_resources('data.json')[0])
        # file = json.loads(file)
        dif = 0

        classes = self.getClassNames()
        # regex = self.getRegexClassNames()
        # classes = self.view.find_all(regex)
        # classes = self.view.find_all('(?<=class=")(.*?)(?=")')
        
        if len(classes) < 1:
            return 0

        for item in classes:
        # for item in classes:
            if not dif == 0:
                item['region'].a += dif
                item['region'].b += dif
            # dont strip here, need origin string for calculate position
            originStr = item['data']
            # originStr = self.view.substr(item)
            temp_str = originStr.strip()
            if not temp_str:
                continue
            # remove duplicate space
            temp_classes = re.sub(' +', ' ', temp_str)
            temp_classes = temp_classes.split(' ')

            if len(temp_classes) < 2:
                if not originStr == temp_str:
                    dif = self.replace(edit, item['region'], temp_str, originStr, dif)
                    # self.view.replace(edit, item['region'], temp_str)
                    # dif += len(temp_str) - len(originStr)
                continue
            filters = self.create_filters(filter_by)

            # clone list
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
                # ' '.join will add empty string when join because classes now arr and sorted return arr
                filters[kind] = sorted(filters[kind])
                sorted_class += ' '.join(filters[kind]) + ' '
            if sorted_class:
                sorted_class = sorted_class[:-1]
                if other_classes:
                    sorted_class = ' '.join(sorted(other_classes)) + ' ' + sorted_class
            else:
                sorted_class = ' '.join(sorted(other_classes))

            dif = self.replace(edit, item['region'], sorted_class, originStr, dif)
            # self.view.replace(edit, item['region'], sorted_class)
            # dif += len(sorted_class) - len(originStr)
            # dif += len(sorted_class) - len(str(self.view.substr(item)))
