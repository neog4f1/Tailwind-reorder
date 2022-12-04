import sublime
import sublime_plugin
# import json
import re


class TailwindOrderCommand(sublime_plugin.TextCommand):
    
    def getRegexClassNames(self, settings):
        classNames = settings.get('classNames')
        regex = "(?:"
        for item in classNames:
            regex += '(?<=' + item + '=")|'
        regex += '(?<=class="))(.*?)(?=")'
        # '(?:(?<=class=")|(?<=className="))(.*?)(?=")'
        return regex
    
    def checkScope1(self, settings):
        scopes = settings.get('scopes')
        cursor = self.view.sel()[0].begin()
        curr_scope = view.scope_name(cursor)

        return (curr_scope in scopes)
    
    def checkScope(self, settings):
        scopes = settings.get('scopes')
        # matchHTMLString = view.match_selector(locations[0], "text.html string.quoted")
        match = next(filter(lambda scope: self.view.find_by_selector(scope), scopes), None)
        return match

    def create_filters(self, list):
        filter_by = {}
        for item in list:
            filter_by[item] = []
        return filter_by

    def run(self, edit):
        settings = sublime.load_settings('tailwind-order.sublime-settings')
        if not self.checkScope(settings):
            return 0
        regex = self.getRegexClassNames(settings)
        list = settings.get('filter_by')
        file = settings.get('data')
        
        # file = sublime.load_resource(sublime.find_resources('data.json')[0])
        # file = json.loads(file)
        dif = 0
        classes = self.view.find_all(regex)
        # classes = self.view.find_all('(?<=class=")(.*?)(?=")')
        
        for item in classes:
            item.a += dif
            item.b += dif
            region = item
            temp_classes = self.view.substr(item)
            temp_classes = re.sub(' +', ' ', temp_classes)
            temp_classes = temp_classes.split(' ')

            if len(temp_classes) == 1:
                continue
            filters = self.create_filters(list)
            
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
            for kind in list:
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
            self.view.replace(edit, region, sorted_class)
            dif += len(sorted_class) - len(str(self.view.substr(item)))
