__author__ = 'hoang281283@gmail.com'


class Picker(object):
    def __init__(self):
        self.total = 0
        self.selected_index = 0
        self.items = []
        self.loaded_items = []
        self.total_loaded = 0
        self.multi_selected_items = []

    def initialize(self, items):
        self.loaded_items = list() + items
        self.total_loaded = len(items)
        self.items = list() + items
        self.total = len(items)

    def all_items(self):
        return self.items

    def current(self):
        if len(self.items) > self.selected_index:
            return self.items[self.selected_index]
        else:
            return None

    def move_down(self):
        self.selected_index = (self.selected_index + 1) % self.total

    def move_up(self):
        self.selected_index = (self.selected_index - 1) % self.total

    def update(self, hosts, selected_idx):
        self.items = hosts
        self.total = len(self.items)
        self.selected_index = selected_idx

    def reset(self):
        self.items = self.loaded_items
        self.total = self.total_loaded
        self.selected_index = 0

    def search(self, exp):
        ret = list()
        for item in self.loaded_items:
            if item.contain(exp):
                ret.append(item)

        return ret

    def multi_select_add(self, item):
        self.multi_selected_items.append(item)

    def enter_multi_select(self):
        self.multi_selected_items = []
        item = self.current()
        if item is not None:
            self.multi_selected_items.append(item)

    def exit_multi_select(self):
        self.multi_selected_items = []

    def ms_items(self):
        ret = list() + self.multi_selected_items
        return ret

