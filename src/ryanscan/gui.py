# coding: utf-8

from __future__ import unicode_literals

from collections import namedtuple

try:
    import tkinter as tk
except ImportError:
    import Tkinter as tk


Model = namedtuple('Model', ['filter', 'min_between_flights'])


class View(object):

    def __init__(self, on_filter_change):
        self.root = r = tk.Tk()
        r.title('Ryanscanner')
        r.geometry('600x300+200+200')
        # r.deiconify()

        self.on_filter_change = on_filter_change

    def render(self, model):
        self._render_input_block(model)

    def _render_input_block(self, model):
        inp_fr = tk.Frame(self.root)
        inp_fr.grid(row=0, column=0)

        tk.Label(inp_fr, text='Filter').grid(row=0, column=0)

        filter = tk.Entry(inp_fr)
        filter.insert(0, model.filter)
        filter.bind('<Button>', self.on_filter_change)
        filter.grid(row=0, column=1)

        cb = tk.Checkbutton(inp_fr, state=tk.NORMAL, text='Return')
        cb.grid(row=0, column=2)

        tk.Label(inp_fr, text='Min. between flights').grid(row=0, column=3)
        min_between = tk.Entry(inp_fr)
        min_between.insert(0, model.min_between_flights)
        filter.grid(row=0, column=5)

    def start(self):
        self.root.mainloop()


class Controller(object):

    def __init__(self, model, **handlers):
        self.model = model

        self.view = View(
            **{k: self.idontknowhowtocallthis(v) for k, v in handlers.items()}
        )

    def idontknowhowtocallthis(self, handler):
        def wrapper(event):
            new_state = handler(self.model, event)
            self.view.render(new_state)

            self.model = new_state

        return wrapper

    def start(self):
        self.view.render(self.model)
        self.view.start()


def big_bang(model):
    Controller(
        model=model,
        on_filter_change=on_filter_change,
    ).start()


def on_filter_change(model, event):
    print(model, event)
    return model


if __name__ == '__main__':
    mod = Model(
        filter='lol',
        min_between_flights=2,
    )
    big_bang(mod)
