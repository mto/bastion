__author__ = 'hoang281283@gmail.com'


class Picker(object):
    def __init__(self, viewport_height=0):
        self.total = 0
        self.selected_index = 0
        self.items = []
        self.loaded_items = []
        self.total_loaded = 0
        self.multi_selected_idxs = []
        self.viewport_height = viewport_height
        self.viewport_min_idx = 0
        self.viewport_max_idx = 0
        self.multi_selected_mode = False

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
        self.loaded_items = list() + items
        self.total_loaded = len(self.items)

        self.items = items
        self.total = len(self.items)
        self.selected_index = selected_idx
        self.viewport_max_idx = min(self.viewport_height, self.total)
        self.viewport_min_idx = 0

    def reset(self):
        self.items = self.loaded_items
        self.total = self.total_loaded
        self.selected_index = 0
        self.viewport_min_idx = 0
        self.viewport_max_idx = min(self.total_loaded, self.viewport_height)

    def search(self, exp):
        ret = list()
        for item in self.loaded_items:
            if item.contain(exp):
                ret.append(item)

        return ret

    def multi_select_add(self, idx):
        if self.multi_selected_mode and idx not in self.multi_selected_idxs:
            self.multi_selected_idxs.append(idx)

    def enter_multi_select(self):
        self.multi_selected_mode = True
        self.multi_selected_idxs = [self.selected_index]

    def exit_multi_select(self):
        self.multi_selected_mode = False
        self.multi_selected_idxs = []

    def ms_idxs(self):
        if self.multi_selected_mode:
            return sorted(self.multi_selected_idxs)
        else:
            return list()

    def ms_items(self):
        ret = list()
        for i in self.ms_idxs():
            if i < self.total:
                ret.append(self.items[i])

        return ret
