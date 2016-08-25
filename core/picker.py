__author__ = 'hoang281283@gmail.com'


class Picker(object):
    def __init__(self, viewport_height=0):
        self.total = 0
        self.selected_index = 0
        self.items = []
        self.loaded_items = []
        self.total_loaded = 0
        self.multi_selected_items = []
        self.viewport_height = viewport_height
        self.viewport_min_idx = 0
        self.viewport_max_idx = 0

    def initialize(self, items):
        self.loaded_items = list() + items
        self.total_loaded = len(items)
        self.items = list() + items
        self.total = len(items)
        self.viewport_min_idx = 0
        self.viewport_max_idx = min(self.viewport_height, self.total)

    def all_items(self):
        return self.items

    def viewport_items(self):
        return [self.items[i] for i in range(self.viewport_min_idx, self.viewport_max_idx)]

    def current(self):
        if len(self.items) > self.selected_index:
            return self.items[self.selected_index]
        else:
            return None

    def move_down(self):
        tmp_idx = self.selected_index + 1
        if tmp_idx < self.total:
            self.selected_index = tmp_idx
            if tmp_idx >= self.viewport_max_idx:
                if (self.viewport_max_idx - self.viewport_min_idx) >= self.viewport_height:
                    self.viewport_min_idx += 1
                    self.viewport_max_idx += 1
                else:
                    self.viewport_max_idx += 1

    def move_up(self):
        tmp_idx = self.selected_index - 1
        if tmp_idx >= 0:
            self.selected_index = tmp_idx
            if tmp_idx < self.viewport_min_idx:
                if (self.viewport_max_idx - self.viewport_min_idx) >= self.viewport_height:
                    self.viewport_max_idx -= 1
                    self.viewport_min_idx -= 1
                else:
                    self.viewport_min_idx -= 1

    def update(self, items, selected_idx):
        self.items = items
        self.total = len(self.items)
        self.selected_index = selected_idx
        self.viewport_max_idx = min(self.viewport_height, self.total)
        self.viewport_min_idx = 0

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

